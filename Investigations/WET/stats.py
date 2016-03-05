#!/usr/bin/env python3

import warc
import numpy

def stats(lengths):
  lengths = numpy.asarray(lengths)
  print numpy.mean(lengths), numpy.std(lengths), numpy.min(lengths), numpy.max(lengths), lengths.size
  print numpy.percentile(lengths, 5), numpy.percentile(lengths, 50), numpy.percentile(lengths, 95)
  print

if __name__ == "__main__":
  f = warc.open("CC-MAIN-20151124205404-00053-ip-10-71-132-137.ec2.internal.warc.wet.gz")
  content_lengths = []
  lengths = []
  num_words = []
  distinct_words = []
  for record in f:
    if 'WARC-Target-URI' in record:
      lengths.append(len(record['WARC-Target-URI']))
      content = record.payload.read().decode('utf-8')
      content_lengths.append(len(content))
      words = content.split()
      num_words.append(len(words))
      distinct_words.append(len(set(words)))
  
  stats(lengths)
  print >> open("lengths.txt","w"), "\n".join([str(s) for s in lengths])
  stats(content_lengths)
  print >> open("content_lengths.txt","w") , "\n".join([str(s) for s in content_lengths])
  stats(num_words)
  print >> open("num_words.txt", "w"), "\n".join([str(s) for s in num_words])
  stats(distinct_words)
  print >> open("distinct_words.txt", "w"), "\n".join([str(s) for s in distinct_words])