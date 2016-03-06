import pandas
import numpy
from collections import defaultdict

df = pandas.DataFrame.from_csv("write_load.txt", sep=",")

print(df.columns.values)
print(df.describe())

#print(df.groupby("file").median())

distinct = defaultdict(list)

with open("write_load.txt", "r") as fp:
    for lineno, line in enumerate(fp):
        if lineno == 0:
            continue

        f, d = line.split(",")
        f = int(f)
        d = int(d)
        distinct[f].append(d)
        print(d)

for k in sorted(distinct):
    arr = numpy.asarray(distinct[k], dtype='int_')
    a = numpy.percentile(arr, 1)
    b = numpy.percentile(arr, 5)
    c = numpy.percentile(arr, 50)
    d = numpy.percentile(arr, 95)
    e = numpy.percentile(arr, 99)

    print((k, a, b, c, d, e))

