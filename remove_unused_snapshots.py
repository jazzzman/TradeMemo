import os
import sys
import re


FOLDER = 'assets\snapshots'
DB = 'db_levels.csv'

regex = re.compile(r"'(.*?)'")
files = []
with open(DB,'r') as db:
    for line in db.readlines():
        m = regex.findall(line)
        if m:
            files += m

print(f'{len(files)=}')
print(*files[:5],sep='\n')
print()

pngs = [p for p in os.listdir(FOLDER) if p.endswith('png')]
print(f'{len(pngs)=}')
print(*pngs[:5],sep='\n')
print()

to_del = set(pngs)-set(files)
print(f'{len(to_del)=}')
print('Files are about to delete:',*to_del,sep='\n')
if to_del and input('Are you ready to remove? ') in 'Yy':
    for f in to_del:
        os.remove(os.path.join(FOLDER,f))
    print('Done')

