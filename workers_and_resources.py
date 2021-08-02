#!/usr/bin/env python3
import os
import struct
import json
from collections import OrderedDict

def get_costs():
  d = 'media_soviet/buildings_types'
  goods = set()

  # crap to ignore
  ignore = [
    '$CONNECTION',
    '0',
    '1',
    '2',
    '3',
    '4',
    '5',
    '6',
    '7',
    '8',
    '9',
    'end',
    '-',
    '$NAME',
    '$HARBOR',
    '$HEATING_DISABLE',
    '$ATTRACTIVE',
    '$STORAGE',
    '$TYPE',
    '$SEASONAL',
    '$ELETRIC_WITHOUT',
    '$SUBTYPE_TELEVISION',
    '$PROFESORS_NEEDED',
    '$TEXT_CAPTION',
    '$VEHICLE_STATION',
    '$RESOURCE_VISUALIZATION',
    'position',
    'rotation',
    'scale',
    'numstepx',
    'numstept',
    '$RESOURCE_INCREASE_POINT',
    '$VEHICLE_UNLOADING_FACTOR',
    '$ELETRIC_CONSUMPTION_LOADING_FIXED',
    '$ELETRIC_CONSUMPTION_UNLOADING_FIXED',
    '$STATION_NOT_BLOCK',
    '$QUALITY_OF_LIVING',
    '$WORKING_VEHICLES_NEEDED',
    '$VEHICLE_PARKING',
    '$PARTICLE',
    '$VEHICLE_CANNOTSELECT_INSIDE',
    '$LONG_TRAINS',
    'positon',
    '$HELIPORT_STATION',
    '$WORKER_RENDERING_AREA',
    '$SUBTYPE_TROLLEYBUS',
    '$ROADVEHICLE_ELETRIC',
    '$VEHICLE_PARKING_PERSONAL',
    '$SUBTYPE_AIRPLANE',
    '$HEATING_ENABLE',
    '$SUBTYPE_AIR',
    '$SUBTYPE_AIRCUSTOM',
    '$CIVIL_BUILDING',
    '$ROADVEHICLE_NOTFLIP',
    '$ELETRIC_CONSUMPTION_LIVING_WORKER_FACTOR',
    '$ELETRIC_CONSUMPTION_LIGHTING_WORKER_FACTOR',
    '$OFFSET',
    '$RESOURCE',
    '//',
    '$WORKING_SFX',
    '$PRODUCTION_CONNECT_TO_SUN',
    '$HELIPORT_AREA',
    '$ELETRIC_CONSUMPTION_HEATING_WORKER_FACTOR',
    '$VEHICLE_LOADING_FACTOR',
    '$POLLUTION_SMALL',
    '$SUBTYPE_CABLEWAY',
    '$ENGINE_SPEED',
    '$POLLUTION_MEDIUM',
    '$SUBTYPE_CABLEWAY',
    '$CABLEWAY_LIGHT',
    'buildings',
    '$VEHICLE_PASSANGER_ONLY',
    '$SUBTYPE_SHIP',
    '$SHIP_STATION',
    '$SUBTYPE_RADIO',
    '$UNDERGROUND_MESH',
    '$MONUMENT_ENABLE_TRESPASSING',
    '$SUBTYPE_TECHNICAL',
    '$ANIMATION_MESH',
    'editor',
    '$SUBTYPE_HOSTEL',
    '$HEATING_WITHOUT_WORKING_FACTOR',
    '$CABLEWAY_HEAVY',
    '$SUBTYPE_SOVIET',
    '$SUBTYPE_ROAD',
    '$PRODUCTION_CONNECT_TO_WIND',
    '$ANIMATION_SPEED_FPS',
    '$SUBTYPE_MEDICAL',
    '$FIRESTATION',
    '$SUBTYPE_RESTAURANT',
    'televizia',
    '$SUBTYPE_RAIL',
    '$SUBTYPE_SPACE_FOR_VEHICLES',
  ]

  # hard mode, 1960
  autos = ['tech_steel', 'wall_steel', 'electro_steel', 'steel', 'techelectro_steel', 'ground', 'wall_panels', 'wall_bricks', 'wall_wood', 'roof_woodbrick', 'roof_asphalt', 'wall_concrete', 'wall_brick', 'roof_woodsteel', 'roof_steel', 'ground_asphalt']

  # order of fields in auto_dict, after ground, walls and volume
  fields = ['workers', 'concrete', 'gravel', 'asphalt', 'bricks', 'boards', 'steel', 'mcomponents', 'ecomponents', 'prefabpanels']

  auto_dict = {
    # Auto: (Ground, Walls, Volume, Workdays, Concrete, Gravel, Asphalt, Bricks, Boards, Steel, Mech C, Elec C, Prefab)
    'ground':           (1,0,0.08,    150,13,10,0,0,0,0,0,0,0),
    'ground_asphalt':   (1,0,0.08,    150,13,10,8,0,0,0,0,0,0),
    'wall_concrete':    (0,1,0.3,     100,22,0,0,0,0,5,0,0,0),
    'wall_panels':      (0,1,0.3,     65,0,0,0,0,0,1,0,0,10),
    'wall_brick':       (0,1,0.3,     140,0,0,0,12,4,1.5,0,0,0),
    'wall_steel':       (0,1,0.3,     90,0,0,0,0,0,8,0,0,0),
    'wall_wood':        (0,1,0.3,     90,0,0,0,0,10,0,0,0,0),
    'tech_steel':       (0,0.25,0.8,  170,0,0,0,0,0,6,1.25,0,0),
    'techelectro_steel':(0,0.25,0.8,  190,0,0,0,0,0,5,0.85,0.55,0),
    'electro_steel':    (0,0.25,0.8,  170,0,0,0,0,0,6,0,1.25,0),
    'roof_woodbrick':   (1,0,0.05,    87,0,0,0,2,10,0,0,0,0),
    'roof_steel':       (1,0,0.05,    95,0,0,0,0,0,7,0,0,0),
    'roof_woodsteel':   (1,0,0.05,    85,0,0,0,0,5,3,0,0,0),
  }

  # These are ordered by complexity. Each row has at most row# number of non-zeroes
  # airplaneparking_30.ini -> ground_asphalt
  # eletric_switch_low.ini -> electro_steel
  # road_pumping_station_v2.ini -> tech_steel
  # powerplant_wind2.ini -> techelectro_steel
  # heating_endstation_small.ini -> wall_brick
  # pedestrian_tunel_entry.ini -> ground
  # trolleybus_depo.ini -> roof_steel
  # raildepobig.ini -> roof_woodsteel
  # playground_tenis2.ini -> steel
  # fountain3.ini -> wall_concrete
  # co_art_gallery.ini -> roof_asphalt
  # warehouse_covered_combined.ini -> roof_woodbrick
  # production_airplane.ini -> wall_panels
  # hotel_horsky.ini -> wall_bricks
  # rail_gas_station.ini -> wall_steel
  # co_beach.ini -> wall_wood

  RE = [
  'airplaneparking_30.ini',
  'eletric_switch_low.ini',
  'road_pumping_station_v2.ini',
  'powerplant_wind2.ini',
  'heating_endstation_small.ini',
  'pedestrian_tunel_entry.ini',
  'trolleybus_depo.ini',
  'raildepobig.ini',
  'playground_tenis2.ini',
  'fountain3.ini',
  'co_art_gallery.ini',
  'warehouse_covered_combined.ini',
  'production_airplane.ini',
  'hotel_horsky.ini',
  'rail_gas_station.ini',
  'co_beach.ini',
  ]

  costs_dict = {}

  for e in os.listdir(d):
  #for e in ['coal_mine.ini']:
  #for e in RE:
    # crop fields have zero cost, don't bother with them
    if e[:6] == 'field_':
      continue

    if '.ini' in e:
      shapes = {}
      costs = [0]*10

      # parse .bbox into shapes
      with open(d+'/'+e.replace('.ini','.bbox'), 'rb') as f:
        numshapes = struct.unpack('I', f.read(4))[0]
        for i in range(numshapes):
          name, index, xmin, ymin, zmin, xmax, ymax, zmax = struct.unpack('512sIffffff', f.read(540))
          name = name[0:name.find(b'\0')].decode('ascii')
          xs = xmax - xmin
          ys = ymax - ymin
          zs = zmax - zmin

          shapes[name] = (xs, ys, zs)

          # ys == 0 happens for flat planes (y = vertical)
          if (min(xs, zs) <= 0 or ys < 0)and len(name) > 0:
            print('bork')
            exit(1)

      with open(d+'/'+e, 'r') as f:
        WORKERS_NEEDED = None
        PRODUCTION = []
        CONSUMPTION = []
        CONSUMPTION_PER_SECOND = []

        # building phase stuff
        autos = {}
        nodes = set()

        def handle_autos():
          #print('handle_autos: ' + str(autos) + ' ' + str(nodes))
          for auto, weight in autos.items():
            mul = weight*0.5
            v = 0
            g = 0
            w = 0

            for n in nodes:
              if n in shapes:
                xs, ys, zs = shapes[n]
                v += xs*ys*zs
                g += xs*zs
                w += 2.0*(xs+zs)*ys
              else:
                #print(n + ' not found in shapes')
                pass

            g /= 300.0
            w /= 300.0
            v /= 3000.0

            # there are typos
            if auto in auto_dict:
              a = auto_dict[auto]
              # Ground, Walls, Volume
              factor = g*a[0] + w*a[1] + v*a[2]
              for i in range(len(costs)):
                costs[i] += mul*factor*a[i+3]

        for line in f.readlines():
          p = line.split()

          # ignore empty lines
          if len(p) == 0:
            continue
          
          if any([i for i in ignore if i in p[0]]):
            continue

          if p[0] == '$WORKERS_NEEDED':
            # $WORKERS_NEEDED 15
            WORKERS_NEEDED = int(p[1])
          elif p[0] == '$PRODUCTION':
            # $PRODUCTION gravel 5.5
            PRODUCTION.append((p[1], float(p[2])))
            goods.add(p[1])
          elif p[0] == '$CONSUMPTION':
            if len(p) >= 3:
              # $CONSUMPTION rawgravel 8.0
              CONSUMPTION.append((p[1], float(p[2])))
              goods.add(p[1])
            else:
              # $CONSUMPTION 1
              pass
          elif p[0] == '$CONSUMPTION_PER_SECOND':
            # $CONSUMPTION_PER_SECOND eletric 0.4
            CONSUMPTION_PER_SECOND.append((p[1], float(p[2])))
            goods.add(p[1])
          elif p[0] == '$CITIZEN_ABLE_SERVE':
            # $CITIZEN_ABLE_SERVE 7
            pass
          elif p[0] == '$COST_WORK':
            # new building phase
            # $COST_WORK SOVIET_CONSTRUCTION_GROUNDWORKS 0.0
            # $COST_WORK SOVIET_CONSTRUCTION_SKELETON_CASTING,0,1.0
            handle_autos()
            autos = {}
            nodes = set()
          elif p[0] == '$COST_RESOURCE_AUTO':
            # $COST_RESOURCE_AUTO ground_asphalt ,1.0
            # $COST_RESOURCE_AUTO wall_steel 1.0
            # $COST_RESOURCE_AUTO tech_steel 0.8
            autos[p[1]] = float(p[2])
          elif p[0] == '$COST_RESOURCE':
            # $COST_RESOURCE workers 3000
            costs[fields.index(p[1])] += float(p[2])
          elif p[0] == '$COST_WORK_BUILDING_NODE':
            # $COST_WORK_BUILDING_NODE concreteShape7
            nodes.add(p[1])
          elif p[0] == '$COST_WORK_VEHICLE_STATION_ACCORDING_NODE':
            # $COST_WORK_VEHICLE_STATION_ACCORDING_NODE polySurfaceShape278
            pass
          elif p[0] == '$COST_WORK_VEHICLE_STATION':
            # $COST_WORK_VEHICLE_STATION -33.5602 0 -7.5026 -27.4859 0 -1.8503
            pass
          elif p[0] == '$COST_WORK_BUILDING_KEYWORD':
            # $COST_WORK_BUILDING_KEYWORD $concrete
            # $COST_WORK_BUILDING_KEYWORD $steel
            # $COST_WORK_BUILDING_KEYWORD $tech
            # this just matches on the start of the node names, unless the keyword is $all
            keyword = p[1][1:]
            if keyword == 'all':
              for k in shapes.keys():
                nodes.add(k)
            else:
              n = len(keyword)
              for k in shapes.keys():
                if k[:n] == keyword:
                  nodes.add(k)
          elif p[0] == '$COST_WORK_BUILDING_ALL':
            # same as $all
            for k in shapes.keys():
              nodes.add(k)
          else:
            # print stuff we missed
            print(e, p)

        handle_autos()
        costs_dict[e[:-4]] = costs

  return costs_dict

#costs_dict = get_costs()
#for k, v in costs_dict.items():
#    print('%37s %s' % (k, ' '.join(['%7.1f' % (round(vv*10)*0.1) for vv in v])))
#print(len(costs_dict))
