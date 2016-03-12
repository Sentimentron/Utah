#!/bin/env python3

import pickle
import postgresql
import logging
import time
import numpy
from collections import defaultdict

if __name__ == "__main__":

    db = postgresql.open("pq://worker:worker@localhost/keywords")
    db.query("drop owned by current_user")

    logging.info("Creating database tables...")
    db.query(r"""CREATE TABLE inverted (packid serial, keyword integer, words integer[])""")

    db.query(r"""CREATE INDEX keyword_index ON inverted USING BTREE
    (keyword)""")

    # Keep a count of how many things we've inserted
    counts = {(i+1) : 0 for i in range(10)}
    def total_count():
        return sum([counts[i] for i in counts])

    append = db.prepare(r"""INSERT INTO inverted (keyword, words) VALUES ($1,
    $2)""")

    # Insert until further notice
    while total_count() < 10E6:
        # Generate a random number between 1 and 10
        keys = numpy.random.randint(1, 11, 10000)
        values = numpy.random.randint(1, None, 10000)
        insert_plan = defaultdict(list)
        for k, v in zip(keys, values):
            insert_plan[k].append(v)
        # Measure the start time
        start = time.time()
        for k in insert_plan:
            append(k, insert_plan[k])
        end = time.time()
        for k, v in zip(keys, values):
            counts[k] = counts[k] + 1
        print("Time to insert %d entries was %.4f seconds (%.4f values per \
        second, %.2f %% done" % (len(keys), end-start, len(keys)/(end-start),
        total_count() / 10E6 * 100))


