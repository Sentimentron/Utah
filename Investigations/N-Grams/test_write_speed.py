#!/bin/env python3

import postgresql
import sys
import os
import gzip
import pickle

if __name__ == "__main__":
    db = postgresql.open("pq://worker:worker@localhost/keywords")

    # Open all of the files
    cur_files = [f for f in os.listdir('.') if os.path.isfile(f)]
    cur_files = [f for f in cur_files if os.path.splitext(f)[1] == '.gz']

    words = set([])

    for f in cur_files:
        print("Reading {}...".format(f))
        g = gzip.GzipFile(f)
        for line in g:
            line = line.decode('utf8')
            word, _, _ = line.partition('\t')
            word, _, _ = word.partition('_')
            words.add(word)

    with open('words.pkl', 'wb') as f:
        print("Writing dump...")
        pickle.dump(words, f)
