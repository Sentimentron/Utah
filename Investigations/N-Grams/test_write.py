#!/bin/env python

import pickle
import postgresql
import logging
import time
import numpy
import random

if __name__ == "__main__":
    db = postgresql.open("pq://worker:worker@localhost/keywords")

    logging.info("Dropping database tables...")
    db.query("drop owned by current_user");

    logging.info("Opening dump file")
    with open("words.pkl", "rb") as f:
        words = pickle.load(f)

    logging.info("Creating database tables...")
    db.query(r"""CREATE TABLE keywords (id SERIAL, word TEXT UNIQUE NOT NULL)""")

    logging.info("Picking some random words...")
    # Pick about 10000 words for a sample read test
    sample = list(words)
    random.shuffle(sample)
    sample = sample[:10000]

    logging.info("Starting insertions")
    stmt = db.prepare(r"""INSERT INTO keywords (word) VALUES ($1) ON CONFLICT DO
    NOTHING""")

    check = db.prepare("SELECT id FROM keywords WHERE word = $1")

    results = []
    for i, word in enumerate(words):
        start = time.clock()
        stmt(word)
        end = time.clock()
        results.append(end-start)

        if i % 10000 == 0:
            print("Written %.2f of all words" % (i*100.0/len(words)),)
            avg_writes = numpy.mean(results)
            print("Average words/second: %.2f" % (1/avg_writes,))
            results = []

            start = time.clock()
            for s in sample:
                for row in check(s):
                    pass
            end = time.clock()
            print("Read test took %.4f seconds" % (end-start))




