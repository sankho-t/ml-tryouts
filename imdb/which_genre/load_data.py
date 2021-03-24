import pprint
from functools import partial
import subprocess

import numpy as np
import tensorflow as tf
from tensorflow.keras.utils import to_categorical

from .params import fname, categories, fname_wordlist, batch_size

header = open(fname).readline().strip().split('\t')
inp_col, target_col = header.index('primaryTitle'), header.index('genres')

cat_keyval = tf.lookup.KeyValueTensorInitializer(keys=categories, values=np.r_[range(len(categories))])
cat_table = tf.lookup.StaticVocabularyTable(cat_keyval, num_oov_buckets=1)
cat_enc = partial(to_categorical, num_classes=len(categories))

all_words = tf.expand_dims(tf.constant(list(map(lambda x: x.strip(), open(fname_wordlist).readlines()))), axis=0)

sample_count_ = subprocess.run(['wc', '-l', fname], capture_output=True).stdout
sample_count = int(sample_count_.decode().strip().split(' ')[0])

@tf.function
def record_line(ln):
    ln_ = tf.strings.lower(tf.strings.split(ln, sep='\t'))
    inp = ln_[inp_col]
    genre0 = tf.strings.split(ln_[target_col], sep=',')
    genre0_ = cat_table.lookup(genre0)
    genre0__ = tf.one_hot(genre0_, depth=len(categories), on_value=True, off_value=False)
    genre0___ = tf.math.reduce_any(genre0__, axis=0)
    return inp, genre0___

@tf.function
def any_en(text):
    words = tf.strings.split(text, sep=' ')
    words_ = tf.expand_dims(words, axis=0)
    common = tf.sets.intersection(words_, all_words)
    return tf.reduce_prod(tf.shape(common.indices)) > 0

data = tf.data.TextLineDataset(fname)\
    .map(record_line)\
    .skip(1)\
    .filter(lambda x,_: any_en(x))\
    .batch(batch_size)\

def view_top_batch():
    for inp, target in data.take(1):
        pprint.pprint(inp)
        pprint.pprint(target)
        break