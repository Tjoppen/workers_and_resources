#!/usr/bin/env python3
import sys
#names = [];
last_v = None
values = [0]

buildings = [];
workers = []; # employment
news = [];
other = [];
tmax = 0

def values_not_all_same():
  #return not all([abs(value - values[0]) < 1e-4 for value in values])
  return any(values)

def print_values():
  global tmax
  tmax = len(values)-1
  outvalues = ','.join([str(value) for value in values])
  print(f'{last_v} = [{outvalues}];')
  if last_v[:8] == 'building':
    buildings.append(last_v)
  elif last_v[:7] == 'workers':
    workers.append(last_v)
  elif last_v[:4] == 'new_':
    news.append(last_v)
  else:
    other.append(last_v)

for line in sys.stdin.readlines():
  p = line.split()
  #v = p[0]
  #if v != last_v:

  q = p[0].split('_')
  v = '_'.join(q[:-1])
  
  if v != last_v:
    if values_not_all_same():
      if last_v:
        print_values()
    last_v = v
    values = []
  values.append(float(p[1]))
    

if values_not_all_same():
  print_values()

print(f"t = 0:{tmax};")
for matrixname,columns,title,strip,i in zip(['B','W','N','R'], [buildings, workers, news, other], ['Buildings','Employment','New buildings','Resources'], [9,8,0,0], [1,2,3,4]):
  if len(columns):
    labels = [col[strip:] for col in columns]
    cols = ';\n'.join(columns)
    print(f"{matrixname} = [{cols}]';")
    underscore = '\\_'
    colnames = ';'.join([f"'{n.replace('_',underscore)}'" for n in labels])
    print(f"colnames{matrixname} = [{colnames}];")
    print(f"figure({i}); plot(t(1:size({matrixname},1)), {matrixname},'x-'); legend(colnames{matrixname}, 'location', 'northwest'); title('{title}');")
    print(f"print('{title}.png');")

