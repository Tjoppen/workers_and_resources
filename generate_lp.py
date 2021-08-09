#!/usr/bin/env python3
from workers_and_resources import get_costs
import json

# eletric = MWh  (24 t coal -> 1400 MWh)
# wires = MW
# STORAGE_LIVING_AUTO -> housing capacity

# https://steamcommunity.com/app/784150/discussions/0/1642042464758987302/
# workday = 8h when building
# power plants = 24h "workday" (3 shifts)

# https://steamcommunity.com/app/784150/discussions/0/2966141980983025345/
# power = 60h days?

building_fields, buildings = get_costs()

# same order as building_fields
# computed from statistics from the game
# within +-3% of actual values
prices = [
      8.6008,
     30.9588,
     38.6777,
     46.7298,
     51.0958,
     42.0923,
    443.5262,
    753.6935,
   1304.4270,
     46.4380,
]

# strip 'vehicles' from all buildings
dels = []
for k in buildings.keys():
  if 'vehicles' in buildings[k]['consumption']:
    del buildings[k]['consumption']['vehicles']
  if 'vehicles' in buildings[k]['production']:
    del buildings[k]['production']['vehicles']

  if len(buildings[k]['consumption']) == 0 and \
      len(buildings[k]['consumption_per_second']) == 0 and \
      len(buildings[k]['production']) == 0:    
    dels.append(k)

for d in dels:
  del buildings[d]

'''b2 = {}
for k,v in buildings.items():
  if 'powerplant' in k:
    b2[k] = v

buildings = b2'''

#print(json.dumps(buildings, indent=4))
#print(len(buildings))
#exit(0)

goods = set(building_fields)
goods.add('workers')
#goods.add('rubles')
#goods.add('dollars')

for k,v in buildings.items():
  for q in ['consumption', 'consumption_per_second', 'production']:
    for g in v[q].keys():
      goods.add(g)

#  print(','.join([str(vv) for vv in v['costs']]))
goods = sorted(goods)
#print(goods)
#exit(0)

tmax = 8
dT = 100    # time between t's in days
shifts = 3  # number of shifts in buildings
x0 = {
  #'rubles': 1000000,
  #'dollars': 1000000,
  'workers': 1000,
  #'powerplantcoal': 1,
  #'cement': 1000,

  # gravelmine, gravelprocessing, concreteplant
  # cementplant, coalmine, coalprocessing, woodcuttingpost
  # sawmill
  'concrete': 2 + 110 + 25 + 739, # + 250 + 361 + 9 + 28,
  'gravel': 2 + 13 + 19 + 70, # + 10 + 66 + 7 + 22,
  'asphalt': 1 + 11 + 15 + 56 + 8 + 53 + 6 + 17,
  'boards': 21 + 75 + 11 + 26,
  'steel': 43 + 30 + 255 + 75 + 201 + 2 + 12,
  'mcomponents': 3, # 3 is enough for one mechanicalcomponentsfactory #4 + 3 + 6 + 4 + 5,
  #'ecomponents': 1000,
  'bricks': 113 + 61, # + 47, # bricks are needed to make bricks
  #'oil': 1000, # oilmine.workers = null
  #'plants': 1000, # farm.workers = null
}

# minimize number of workers in powerplantcoal
#print('min: workers_powerplantcoal_%i;' % tmax)

#print(f'min: ' + ' + '.join([f'workers_powerplantcoal_{t:03d} + workers_powerplantcoalv2_{t:03d} + building_powerplantsolar_{t:03d}' for t in range(tmax)]) + ';')
#print(f'max: coal_{tmax:03d};')
#print(f'max: workers_powerplantcoal_{tmax:03d};')
#print(f'max: eletric_{tmax:03d};')

# Value of objective function: 2449.17581189
#print(f'max: ' + ' + '.join([f'building_powerplantnuclearsingle_{t:03d} + workers_powerplantnuclearsingle_{t:03d}' for t in range(tmax+1)]) + ';')

# Value of objective function: 29.87302305
#print(f'max: ' + ' + '.join([f'building_powerplantnuclearsingle_{t:03d}' for t in range(tmax+1)]) + ';')
#print(f'max: building_powerplantnuclearsingle_{tmax:03d};')
#print(f'max: ' + ' + '.join([f'invested_workers_powerplantcoal_{t:03d}' for t in range(tmax+1)]) + ';')
print(f'max: gravel_{tmax:03d};')

for k,v in x0.items():
  if k in buildings:
    print(f'building_{k}_000 = {x0[k]};')
  else:
    print(f'{k}_000 = {x0[k]};')
  # set up investments for initial buildings
  if k in buildings.keys():
    for g,amount in buildings[k]['costs'].items():
      print(f'invested_{g}_{k}_000 = {amount*x0[k]};')

for g in goods:
  if g not in x0:
    print(f'{g}_000 = 0;')

for b,d in buildings.items():
  if b not in x0:
    print(f'building_{b}_000 = 0;')
    for g,amount in d['costs'].items():
      print(f'invested_{g}_{b}_000 = 0;')

ints = []
for t in range(tmax+1):
  ws = []
  prods = {}
  cons = {}

  #print(f'building_powerplantnuclearsingle_{t:03d} <= 1;')

  #if t > tmax/2:
  #  print(f'eletric_{t:03d} >= {6000*t};')

  for b,d in buildings.items():
    max_workers = d["workers"]
    if max_workers is not None:
      # can't employ more workers than the current number of buildings allows
      w = f'workers_{b}_{t:03d}'
      ws.append(w)
      print(f'{w} <= {shifts*max_workers} building_{b}_{t:03d};')
      # production is given by number of workers employed, and the number of days (dT)
      for g,amount in d['production'].items():
        print(f'prod_{b}_{g}_{t:03d} = {dT*amount/shifts} {w};')
        if g not in prods:
          prods[g] = set()
        prods[g].add(b)
      for g,amount in d['consumption'].items():
        print(f'con_{b}_{g}_{t:03d} = {dT*amount/shifts} {w};')
        if g not in cons:
          cons[g] = set()
        cons[g].add(b)

    if t > 0:
      # number of buildings never decreases
      print(f'building_{b}_{t:03d} >= building_{b}_{t-1:03d};')

    # number of buildings can't exceed the amount of resources invested so far
    if t > 0:
      for g,a in d['costs'].items():
        print(f'invested_{g}_{b}_{t:03d} >= {a} building_{b}_{t:03d};')
        #print(f'invested_{g}_{b}_{t:03d} >= invested_{g}_{b}_{t-1:03d};')

    # these have to be at the end of the program for some reason
    ints.append(f'int building_{b}_{t:03d};')

  for g,bs in prods.items():
    prodstr = ' + '.join([f'prod_{b}_{g}_{t:03d}' for b in bs])
    print(f'prod_{g}_{t:03d} = {prodstr};')

  for g,bs in cons.items():
    constr = ' + '.join([f'con_{b}_{g}_{t:03d}' for b in bs])
    print(f'con_{g}_{t:03d} = {constr};')

  for g in goods:
    if g not in prods:
      print(f'prod_{g}_{t:03d} = 0;')
    if g not in cons:
      print(f'con_{g}_{t:03d} = 0;')

  if t > 0:
    for g in goods:
      if g == 'workers':
        print(f'workers_{t:03d} = workers_{t-1:03d} + prod_workers_{t-1:03d};')
        ws.append(f'{dT} invested_workers_{b}_{t:03d} - {dT} invested_workers_{b}_{t-1:03d}')
      else:
        prod = []
        invs = []
        for b,d in buildings.items():
          if g in d['costs']:
            # subtract difference in investment
            invs.append(f' + invested_{g}_{b}_{t-1:03d} - invested_{g}_{b}_{t:03d}')

        invs = ''.join(invs)
        print(f'{g}_{t:03d} = {g}_{t-1:03d} + prod_{g}_{t-1:03d} - con_{g}_{t-1:03d} {invs};')

  ws = ' + '.join(ws)
  print(f'{ws} <= workers_{t:03d};')


for i in ints:
  print(i)

