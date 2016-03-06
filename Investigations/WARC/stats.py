#!/usr/bin/env python3

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
  f = warc.open(f)
  content_lengths = []
  lengths = []
  num_words = []
  distinct_words = []
  for record in f:
    if record['Content-Type'] != 'application/http; msgtype=response':
        print "Skipped", record['Content-Type']
        continue
    if 'WARC-Target-URI' in record:
      lengths.append(len(record['WARC-Target-URI']))
      content = record.payload.read()
      
      src = FakeSocket(content)
      response = HTTPResponse(src)
      response.begin()
      
      content_type = response.getheader('Content-Type')
      if content_type is not None and "text/html" not in content_type:
          print "Skipped content", response.getheader('Content-Type')
          continue
      
      #content_lengths.append(len(content))
      try:
          content = response.read()
          content_lengths.append(len(content))
          h = BeautifulSoup(content, "lxml")
      except IncompleteRead:
          continue
      for title in h.findAll('title'):
          print "TITLE", title.text.encode('utf-8')
            
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
          num_words.append(len(text))
          distinct_words.append(len(set(text)))
          
    
  stats(lengths)
  print >> open("lengths.txt","w"), "\n".join([str(s) for s in lengths])
  stats(content_lengths)
  print >> open("content_lengths.txt","w") , "\n".join([str(s) for s in content_lengths])
  stats(num_words)
  print >> open("num_words.txt", "w"), "\n".join([str(s) for s in num_words])
  stats(distinct_words)
  print >> open("distinct_words.txt", "w"), "\n".join([str(s) for s in distinct_words])