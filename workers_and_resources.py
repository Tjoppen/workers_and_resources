#!/usr/bin/env python3
import os
import struct

'''
.bbox format

u32 numshapes;
{
  //540 B per shape
  char shapename[512]; //at least 29 (pasted__polySurfaceShape1430), lots of strcpy()-ish garbage and uninited memory
  u32 index;           //appears to increase by 1 per shape, starting from 0
  float xmin;
  float ymin;
  float zmin;
  float xmax;
  float ymax;
  float zmax;
}
'''

d = 'media_soviet/buildings_types'
goods = set()
#COST_WORK_BUILDING_NODE = set()
COST_RESOURCE_AUTO = set()
COST_RESOURCE_AUTO2 = {}
COST_RESOURCE_AUTO3 = {}
n = 0

# hard mode, 1960
autos = ['tech_steel', 'wall_steel', 'electro_steel', 'steel', 'techelectro_steel', 'ground', 'wall_panels', 'wall_bricks', 'wall_wood', 'roof_woodbrick', 'roof_asphalt', 'wall_concrete', 'wall_brick', 'roof_woodsteel', 'roof_steel', 'ground_asphalt']

# These are ordered in complexity. Each row has at most row# number of non-zeroes
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

'''
airplaneparking_30.ini
eletric_switch_low.ini
road_pumping_station_v2.ini
powerplant_wind2.ini
heating_endstation_small.ini
pedestrian_tunel_entry.ini
trolleybus_depo.ini
raildepobig.ini
playground_tenis2.ini
fountain3.ini
co_art_gallery.ini
warehouse_covered_combined.ini
production_airplane.ini
hotel_horsky.ini
rail_gas_station.ini
co_beach.ini
'''

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

skipem = ['ground_asphalt', 'electro_steel', 'tech_steel', 'techelectro_steel', 'wall_brick', 'ground',
'roof_steel','roof_woodsteel','steel','wall_concrete','roof_asphalt','roof_woodbrick','wall_panels',
#'wall_bricks','wall_steel','wall_wood',
]

outstats = [()]*16

for e in os.listdir(d):
  if '.ini' in e:
    shapes = {}
    with open(d+'/'+e.replace('.ini','.bbox'), 'rb') as f:
      numshapes = struct.unpack('I', f.read(4))[0]
      COST_RESOURCE_AUTO2[e] = set()
      auto_mask = '0'*len(autos)

      #print(e)
      #print(numshapes)
      atot = 0
      wtot = 0
      vtot = 0
      ctot = 0
      xminmin = None
      yminmin = None
      zminmin = None
      xmaxmax = None
      ymaxmax = None
      zmaxmax = None
      for i in range(numshapes):
        name, index, xmin, ymin, zmin, xmax, ymax, zmax = struct.unpack('512sIffffff', f.read(540))
        name = name[0:name.find(b'\0')].decode('ascii')

        if xminmin is None:
          xminmin = xmin
          yminmin = ymin
          zminmin = zmin
          xmaxmax = xmax
          ymaxmax = ymax
          zmaxmax = zmax

        xminmin = min(xminmin, xmin)
        yminmin = min(yminmin, ymin)
        zminmin = min(zminmin, zmin)
        xmaxmax = max(xmaxmax, xmax)
        ymaxmax = max(ymaxmax, ymax)
        zmaxmax = max(zmaxmax, zmax)

        xs = xmax - xmin
        ys = ymax - ymin
        zs = zmax - zmin

        v = xs*ys*zs # volume
        a = xs*zs # area
        c = 2*xs + 2*zs # circumference
        w = c*ys # wall area

        vtot += v
        atot += a
        ctot += c
        wtot += w

        # stuff som troligtvis är relevant:
        # golvyta på alla bboxes (v)
        # omkrets på alla bboxes (c)
        # väggyta på alla bboxes (w)
        # golvyta som omringar alla bboxes (betonggrund)
        # volym av alla bboxes (v)
        # volym som omringar alla bboxes (osäker om användbart)


        if 'cement_plant' in e and 'ground' in name:
          print("   %30s %f" % (name, v))
        shapes[name] = (xs, ys, zs)

        # ys == 0 happens for flat planes (y = vertical)
        if (min(xs, zs) <= 0 or ys < 0)and len(name) > 0:
          print('bork')
          exit(1)
      
      try:
        #print(RE)
        i = RE.index(e)
        de här summorna måste göras baserat på vad varje auto specar för bboxar
        outstats[i] = (
          atot,
          ctot,
          vtot,
          wtot,
          (xmaxmax-xminmin)*(zmaxmax-zminmin), # floor area
          2*(xmaxmax-xminmin)+2*(zmaxmax-zminmin), # circumference
          (xmaxmax-xminmin)*(ymaxmax-yminmin)*(zmaxmax-zminmin), # bounding volume
          (2*(xmaxmax-xminmin)+2*(zmaxmax-zminmin))*(ymaxmax-yminmin), # bounding wall
        )
        print(i)
      except Exception:
        pass
        #stats[

    with open(d+'/'+e, 'r') as f:
      n += 1

      WORKERS_NEEDED = None
      PRODUCTION = []
      CONSUMPTION = []
      CONSUMPTION_PER_SECOND = []
      
      # building phase stuff
      COST_WORK_BUILDING_NODE = [] # taken from bboxes
      COST_WORK_VEHICLE_STATION_ACCORDING_NODE = [] # taken from bboxes
      COST_WORK_VEHICLE_STATION = [] # defined explicitly in file

      for line in f.readlines():
        p = line.split()

        # ignore empty lines
        if len(p) == 0:
          continue

        # other crap to ignore
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
          '$COST_WORK_BUILDING_ALL',
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
          # $COST_WORK SOVIET_CONSTRUCTION_SKELETON_CASTING		1.0
          COST_WORK_BUILDING_NODE = []
          COST_WORK_VEHICLE_STATION_ACCORDING_NODE = []
          COST_WORK_VEHICLE_STATION = []
        elif p[0] == '$COST_RESOURCE_AUTO':
          # $COST_RESOURCE_AUTO ground_asphalt 	1.0
          # $COST_RESOURCE_AUTO wall_steel 1.0
          # $COST_RESOURCE_AUTO tech_steel 0.8
          if p[1] not in skipem and 'residental' not in e and 'panel' not in e:
            ps = p[1].split('_')
            pos = autos.index(p[1])
            auto_mask = auto_mask[:pos] + '1' + auto_mask[pos+1:]
            COST_RESOURCE_AUTO.add(p[1])
            COST_RESOURCE_AUTO2[e].add(p[1])
        elif p[0] == '$COST_RESOURCE':
          #print(p)
          pass
        elif p[0] == '$COST_WORK_BUILDING_NODE':
          # $COST_WORK_BUILDING_NODE concreteShape7
          pass
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
          pass
        else:
          # print stuff we missed
          print(e, p)

      #if WORKERS_NEEDED and PRODUCTION:
      #  print(e, WORKERS_NEEDED, str(CONSUMPTION), '->', PRODUCTION)
      COST_RESOURCE_AUTO3[str(len(COST_RESOURCE_AUTO2[e]))+','.join(sorted(list(COST_RESOURCE_AUTO2[e])))] = e
      #COST_RESOURCE_AUTO3[str(len(COST_RESOURCE_AUTO2[e]))+auto_mask] = e
      COST_RESOURCE_AUTO2[e] = list(COST_RESOURCE_AUTO2[e])
      #print(auto_mask)

#for g in goods:
#  print(g)
#print(COST_WORK_BUILDING_NODE)
#print(n, len(COST_WORK_BUILDING_NODE), len(goods))
#print(COST_RESOURCE_AUTO)
#print(len(COST_RESOURCE_AUTO))
import json
#print(json.dumps(sorted(COST_RESOURCE_AUTO2.items(), key= lambda x:-len(x[1])), indent=4))
#print(COST_RESOURCE_AUTO3)
from collections import OrderedDict
#print(json.dumps(OrderedDict(sorted(COST_RESOURCE_AUTO3.items())), indent=4))
#print(len(COST_RESOURCE_AUTO3))
for k,v in sorted(COST_RESOURCE_AUTO3.items()):
  print("# %s -> %s" % (v, k[1:]))
print(len(skipem))
print(json.dumps(outstats[RE.index('playground_tenis2.ini')], indent=4))
