#!/usr/bin/env python3

# Estimate the number of documents inside a typical crawl archive

import warc
import numpy

from bs4 import BeautifulSoup
from bs4.element import NavigableString, Comment, Tag

from httplib import HTTPResponse, IncompleteRead
from StringIO import StringIO

import string
import re
import itertools
import unicodedata

def stats(lengths):
  lengths = numpy.asarray(lengths)
  print numpy.mean(lengths), numpy.std(lengths), numpy.min(lengths), numpy.max(lengths), lengths.size
  print numpy.percentile(lengths, 5), numpy.percentile(lengths, 50), numpy.percentile(lengths, 95)
  print

class FakeSocket():
    def __init__(self, response_str):
        self._file = StringIO(response_str)
    def makefile(self, *args, **kwargs):
        return self._file

if __name__ == "__main__":
  f = "CC-MAIN-20150226074101-00072-ip-10-28-5-156.ec2.internal.warc.gz"
  f = "CC-MAIN-20150226074102-00290-ip-10-28-5-156.ec2.internal.warc.gz"
  f = "CC-MAIN-20150226074102-00290-ip-10-28-5-156.ec2.internal.warc.gz"

  files = [
    "CC-MAIN-20150226074102-00290-ip-10-28-5-156.ec2.internal.warc.gz",
    "CC-MAIN-20150226074102-00293-ip-10-28-5-156.ec2.internal.warc.gz",
    "CC-MAIN-20150226074103-00011-ip-10-28-5-156.ec2.internal.warc.gz",
    "CC-MAIN-20150226074103-00204-ip-10-28-5-156.ec2.internal.warc.gz",
    "CC-MAIN-20150226074105-00000-ip-10-28-5-156.ec2.internal.warc.gz",
    "CC-MAIN-20150226074103-00063-ip-10-28-5-156.ec2.internal.warc.gz",
    "CC-MAIN-20150226074102-00107-ip-10-28-5-156.ec2.internal.warc.gz",
    "CC-MAIN-20150226074103-00029-ip-10-28-5-156.ec2.internal.warc.gz",
    "CC-MAIN-20150226074101-00055-ip-10-28-5-156.ec2.internal.warc.gz",
    "CC-MAIN-20150226074103-00159-ip-10-28-5-156.ec2.internal.warc.gz",
    "CC-MAIN-20150226074104-00089-ip-10-28-5-156.ec2.internal.warc.gz",
    "CC-MAIN-20150226074102-00322-ip-10-28-5-156.ec2.internal.warc.gz",
    "CC-MAIN-20150226074103-00113-ip-10-28-5-156.ec2.internal.warc.gz",
    "CC-MAIN-20150226074104-00071-ip-10-28-5-156.ec2.internal.warc.gz"
  ]

  o = open("write_load.txt", "w")
  all_words = set([])

  for fileno, f in enumerate(files):
    f = warc.open(f)
    record_count = 0
    for record in f:
        if record['Content-Type'] != 'application/http; msgtype=response':
            continue
        if 'WARC-Target-URI' in record:
            content = record.payload.read()

            src = FakeSocket(content)
            response = HTTPResponse(src)
            response.begin()

            content_type = response.getheader('Content-Type')
            if content_type is not None and "text/html" not in content_type and "xml" not in content_type and "text" not in content_type:
                if "image" not in content_type:
                  print content_type
                  continue

            try:
                content = response.read()
                h = BeautifulSoup(content, "lxml")
            except IncompleteRead:
                continue

            for body in h.findAll("body"):
                #text = [i for i in body.recursiveChildGenerator() if type(i) == NavigableString]

                #text = [t.split() for t in text if len(t) > 0]
                #print(text)

                [s.extract() for s in body('script')]
                [s.extract() for s in body('style')]
                #print(body)
                text = [i for i in body.recursiveChildGenerator() if type(i) == NavigableString if len(i) > 0]

                text = [unicodedata.normalize("NFKD", t) for t in text]

                regex = re.compile(r'[%s\s]+' % re.escape(string.punctuation))
                text = [regex.split(i) for i in text]


                text = list(itertools.chain.from_iterable(text))

                text = [t for t in text if len(t) > 0]
                #print(text)

                if len(text) == 0:
                    continue
                record_count += 1
                new_words = set([s for s in text if s not in all_words])
                print >> o, fileno, len(new_words)
                for n in new_words:
                  all_words.add(n)

    print record_count
