#!/usr/bin/env python3

import pandas
import numpy as np
import sys


import dateutil.parser

from datetime import timedelta

histprice = pandas.DataFrame.from_csv("spot-instance-history.tsv", sep='\t', parse_dates=5, infer_datetime_format=True)

histprice['DATE'] = pandas.to_datetime(histprice['DATE'])

histprice['exceeds_bid'] = histprice['PRICE'] >= 0.026

az_groups = histprice[['AZ', 'exceeds_bid']].groupby('AZ').aggregate(np.sum)

# Select only the zone which closely matches my bid
histprice = histprice[histprice['AZ']=='us-east-1e']

# Get the top-level stats
print(histprice.describe())

# Time between updates
histprice['DATE_DELTA'] = histprice['DATE'].shift()-histprice['DATE']

# The maximum date that price applies
histprice['MAX_DATE'] = histprice['DATE'] + histprice['DATE_DELTA']

print(histprice)

prices = []
with open('spot-instance-history.tsv') as fp:
   for no, line in enumerate(fp):
      if no == 0:
          continue
      #print(line.split())
      _, az, _, _, price, date = line.split('\t')
      date = dateutil.parser.parse(date)
      price = float(price)
      if az == 'us-east-1e':
          prices.append((price, date))

current_span = []
all_spans = []
for price, date in prices:
    if price <= 0.026:
        # Meets the bid 
        current_span.append(date)
    elif len(current_span) > 0:
        all_spans.append((min(current_span), max(current_span)))
       #  print(all_spans[-1])
        current_span = []

for min_time, max_time in all_spans:
    print((max_time - min_time))
    
# OK: now print the actual time we would have been charged for and simulate when the instance would have stopped
min_time = min(x[1] for x in prices) # Time the spot instance got placed
max_time = max(x[1] for x in prices) # Simulated time
delta = max_time - min_time
delta_hours = delta.total_seconds() / 60 / 60

print(delta_hours)

prices_dict = {d : p for p, d in prices}

# Between our min and max time, calculate what the cost would have been per hour
hour_prices = {}
run_status = {}
total_hours = 0
partial_hours = 0
max_bid = float(sys.argv[1])
for i in range(int(delta_hours)):
    
    # Retrieve a list of dates that are in between this 
    # and the next hour
    i = timedelta(hours=i) + min_time
    max_hour_time = i + timedelta(hours=1)
    quoted_times = [j for j in prices_dict if j < max_hour_time and j >= i]
    
    print((i, len(quoted_times)))
    
    # Find the date that's closest to this time, but is before to set
    # the "price per hour"
    possible_times = [j for j in prices_dict if j < i]
    if len(possible_times) == 0:
        continue
    possible_time = max(possible_times)
    hour_prices[i] = prices_dict[possible_time]
    run_status[i] = timedelta(hours=1)
    total_hours += 1
    
    
    # If the price of one of those times is greater than our bid...
    for q in sorted(quoted_times):
        if prices_dict[q] >= max_bid:
            hour_prices[i] = 0.0 # Not charged for a partial hour
            run_status[i] = q-i
            partial_hours += 1
            total_hours -= 1
            break
            
    
    
# Work out the total cost
s = 0
h = timedelta()
for j in sorted(hour_prices):
    print((j, hour_prices[j], run_status[j]))
    s += hour_prices[j]
    h += run_status[j]

print(s)
print(h.total_seconds()/60/60)
print((total_hours, partial_hours))
print(("Effective full hourly rate:", s / total_hours))
print(("Hourly rate (assuming no penalty for partial hours)", s / (h.total_seconds()/60/60)))


# Aggregate
#print(histprice.groupby('exceeds_bid').agg({'DATE': [np.min, np.max]}))

#print(histprice.groupby('exceeds_bid').aggregate(np.average))


#print(histprice.describe())


#print((histprice[histprice['exceeds_bid']]).count())
#print((histprice[histprice['exceeds_bid']])

#print(histprice)
