#!/usr/bin/env python3

import pandas
import numpy as np
import sys

"""
aws ec2 describe-spot-price-history --instance-types   c4.large --output text --start-time 2016-02-04 --end-time 2016-03-05 --product-descriptions 'Linux/UNIX (Amazon VPC)' > spot-instance-history.tsv

"""



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
      prices.append((price, date, az))
    
# OK: now print the actual time we would have been charged for and simulate when the instance would have stopped
min_time = min(x[1] for x in prices) # Time the spot instance got placed
max_time = max(x[1] for x in prices) # Simulated time
delta = max_time - min_time
delta_hours = delta.total_seconds() / 60 / 60

print(delta_hours)

prices_dict_withaz = {(d, a) : p for p, d, a in prices}

# Between our min and max time, calculate what the cost would have been per hour
hour_prices = {}
run_status = {}
total_hours = 0
partial_hours = 0
max_bid = float(sys.argv[1])
current_az = None
for i in range(int(delta_hours)):
    
    i = timedelta(hours=i) + min_time
    
    # If we were running before, we have to stay in the same AZ
    if current_az != None:
        print(("Retaining", current_az))
        prices_dict = {d : p for p, d, a in prices if a == current_az}
    else:
        # Otherwise, we can price the AZ with the cheapest price at
        # this point
        possible_azs = set([d for j, d in prices_dict_withaz])
        cheapest_az, cheapest_price = None, 100000
        for az in possible_azs:
            prices_dict = {d : p for p, d, a in prices if a == az}
            possible_times = [j for j in prices_dict if j < i]
            if len(possible_times) == 0:
                continue
            possible_time = max(possible_times)
            price = prices_dict[possible_time]
            if price < cheapest_price:
                cheapest_az = az
                cheapest_price = price 
                print(("Cheapest AZ is now", cheapest_az))
         
        current_az = cheapest_az
        prices_dict = {d : p for p, d, a in prices if a == current_az}        
    
    # Retrieve a list of dates that are in between this 
    # and the next hour
    max_hour_time = i + timedelta(hours=1)
    quoted_times = [j for j in prices_dict if j < max_hour_time and j >= i]
        
    # Find the date that's closest to this time, but is before to set
    # the "price per hour"
    possible_times = [j for j in prices_dict if j < i]
    if len(possible_times) == 0:
        continue
    possible_time = max(possible_times)
    hour_prices[i] = prices_dict[possible_time]
    print((i, len(quoted_times)), str(possible_time), prices_dict[possible_time])
    run_status[i] = timedelta(hours=1)
    total_hours += 1
    
    
    # If the price of one of those times is greater than our bid...
    for q in sorted(quoted_times):
        if prices_dict[q] > max_bid:
            hour_prices[i] = 0.0 # Not charged for a partial hour
            run_status[i] = q-i
            partial_hours += 1
            total_hours -= 1
            current_az = None
            print(("Able to run for", str(q - i)))
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
