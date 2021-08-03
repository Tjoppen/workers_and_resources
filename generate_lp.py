#!/usr/bin/env python3
from workers_and_resources import get_costs
import json

building_fields, buildings = get_costs()

b2 = {}
for k,v in buildings.items():
  if 'powerplant' in k:
    b2[k] = v

buildings = b2

#buildings = {'powerplantcoal': buildings['powerplantcoal']}
#print(json.dumps(buildings, indent=4))
#exit(0)

goods = set(building_fields)
goods.add('workers')
goods.add('rubles')
goods.add('dollars')

for k,v in buildings.items():
  for q in ['consumption', 'consumption_per_second', 'production']:
    for g in v[q].keys():
      goods.add(g)

#  print(','.join([str(vv) for vv in v['costs']]))
goods = sorted(goods)
#print(goods)
#exit(0)

tmax = 10
x0 = {
  'rubles': 1000000,
  'dollars': 1000000,
  'workers': 100,
  'powerplantcoal': 1,
  'coal': 10000,
  'concrete': 100000,
  'gravel': 100000,
  'asphalt': 10000,
  'steel': 10000,
  'mcomponents': 300,
  'ecomponents': 300,
  'nuclearfuel': 10,
  'vehicles': 100, # nuclear plants need this for some reason
}

# minimize number of workers in powerplantcoal
#print('min: workers_powerplantcoal_%i;' % tmax)

#print(f'min: ' + ' + '.join([f'workers_powerplantcoal_{t} + workers_powerplantcoalv2_{t} + building_powerplantsolar_{t}' for t in range(tmax)]) + ';')
print(f'max: coal_{tmax};')
#print(f'max: workers_powerplantcoal_{tmax};')
#print(f'max: eletric_{tmax};')
#print(f'max: ' + ' + '.join([f'powerplantcoal_{t}' for t in range(tmax+1)]) + ';')
#print(f'max: ' + ' + '.join([f'invested_workers_powerplantcoal_{t}' for t in range(tmax+1)]) + ';')

for k,v in x0.items():
  if k in buildings:
    print(f'building_{k}_0 = {x0[k]};')
  else:
    print(f'{k}_0 = {x0[k]};')
  # set up investments for initial buildings
  if k in buildings.keys():
    for g,amount in buildings[k]['costs'].items():
      print(f'invested_{g}_{k}_0 = {amount*x0[k]};')

for g in goods:
  if g not in x0:
    print(f'{g}_0 = 0;')

for b,d in buildings.items():
  if b not in x0:
    print(f'building_{b}_0 = 0;')
    for g,amount in d['costs'].items():
      print(f'invested_{g}_{b}_0 = 0;')

ints = []
for t in range(tmax+1):
  ws = []
  prods = {}
  cons = {}
  
  if t > tmax/2:
    print(f'eletric_{t} >= {6000*t};')
  
  for b,d in buildings.items():
    max_workers = d["workers"]
    if max_workers is not None:
      # can't employ more workers than the current number of buildings allows
      w = f'workers_{b}_{t}'
      ws.append(w)
      print(f'{w} <= {max_workers} building_{b}_{t};')
      # production is given by number of workers employed
      for g,amount in d['production'].items():
        print(f'prod_{b}_{g}_{t} = {amount} {w};')
        if g not in prods:
          prods[g] = set()
        prods[g].add(b)
      for g,amount in d['consumption'].items():
        print(f'con_{b}_{g}_{t} = {amount} {w};')
        if g not in cons:
          cons[g] = set()
        cons[g].add(b)

    if t > 0:
      # number of buildings never decreases
      print(f'building_{b}_{t} >= building_{b}_{t-1};')

    # number of buildings can't exceed the amount of resources invested so far
    if t > 0:
      for g,a in d['costs'].items():
        print(f'invested_{g}_{b}_{t} >= {a} building_{b}_{t};')
        #print(f'invested_{g}_{b}_{t} >= invested_{g}_{b}_{t-1};')

    # these have to be at the end of the program for some reason
    ints.append(f'int building_{b}_{t};')

  for g,bs in prods.items():
    prodstr = ' + '.join([f'prod_{b}_{g}_{t}' for b in bs])
    print(f'prod_{g}_{t} = {prodstr};')

  for g,bs in cons.items():
    constr = ' + '.join([f'con_{b}_{g}_{t}' for b in bs])
    print(f'con_{g}_{t} = {constr};')

  for g in goods:
    if g not in prods:
      print(f'prod_{g}_{t} = 0;')
    if g not in cons:
      print(f'con_{g}_{t} = 0;')

  if t > 0:
    for g in goods:
      if g == 'workers':
        print(f'{g}_{t} = {g}_{t-1} + prod_{g}_{t-1};')
        ws.append(f'invested_workers_{b}_{t} - invested_workers_{b}_{t-1}')
      else:
        prod = []
        invs = []
        for b,d in buildings.items():
          if g in d['costs']:
            # subtract difference in investment
            invs.append(f' + invested_{g}_{b}_{t-1} - invested_{g}_{b}_{t}')

        invs = ''.join(invs)
        #print(f'{g}_{t} = {g}_{t-1} + prod_{g}_{t-1} - con_{g}_{t-1} {invs};')
        print(f'{g}_{t} = {g}_{t-1} + prod_{g}_{t-1} - con_{g}_{t-1} {invs};')

  ws = ' + '.join(ws)
  print(f'{ws} <= workers_{t};')


for i in ints:
  print(i)

#for k, v in buildings.items():
#    print('%33s %s' % (k, ' '.join(['%7.1f' % (round(vv*10)*0.1) for vv in v])))
#print(len(buildings))
#print(buildings)
#print(json.dumps(buildings, indent=4))
#print(len(goods))
#for k in buildings.keys():
#  if 'coal' in k:
#    print(k)

