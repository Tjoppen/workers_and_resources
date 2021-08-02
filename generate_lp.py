#!/usr/bin/env python3
from workers_and_resources import get_costs

costs_dict = get_costs()
for k, v in costs_dict.items():
    print('%33s %s' % (k, ' '.join(['%7.1f' % (round(vv*10)*0.1) for vv in v])))
print(len(costs_dict))
