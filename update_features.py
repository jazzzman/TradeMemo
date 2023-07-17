import sys
import json
import argparse
import pandas as pd

from pages.config import FEATURENAME, DBNAME

ap = argparse.ArgumentParser(
        prog = "update_features.py", 
        description="App add new feature or remove feature at particular index in features.json"
                    "and update database with a new column")

ap.add_argument('-f','--feature', help='New feature. Consists of two parts'
                                       'separated semicolon: Tablename:code. '
                                       'Exp: OB:order_block, Треугольник:triangle...', 
                type=str)
ap.add_argument("-i",'--index', help="Specified index of new feature or feature to be removed. Last index is prohibited.",type=int, default=-1)
ap.add_argument("-p",'--preview', help="Preview features.json with indexes", action='store_true')
ap.add_argument("-r",'--remove', help="Remove feature at particular index setted by --index parameter.", action='store_true')


args = ap.parse_args()

feature, index, preview, remove = args.feature, args.index, args.preview, args.remove


with open(FEATURENAME,'r') as f:
    features = json.load(f)

if len([p for p in [remove, preview, feature] if p])>1:
    print('Too much modificators. Only one should be choosen:\n'
          '--feature\n--remove\n--preview')
    sys.exit()

if preview:
    for i,f in enumerate(features):
        print(f'{i} {f}')
    sys.exit()
elif feature:
    feature = feature.split(':')
    if len(feature)!=2 or any([f=='' for f in feature]):
        print("Wrong feature. See help...")
        sys.exit()

    if any([feature[0] == f[0] for f in features]) or \
            any([feature[1] == f[1] for f in features]):
        print('This feature is already in features')
        sys.exit()

    if index<0: 
        index = len(features)+index
    if index >= len(features):
        print("Last index is prohibited. Read help.")
        sys.exit()

    features.insert(index,feature)
    for i,f in enumerate(features):
        print(f'{i} {f}')
    resp = input("New features list. Is it ok? ")
    if not resp.strip().lower().startswith('y'):
        sys.exit()

    print(f'Writing {FEATURENAME}')
    with open('features.json','w',encoding='utf-8') as f:
        json.dump(features,f,ensure_ascii=False)
    
    print(f'Writing {DBNAME}')
    db = pd.read_csv(DBNAME)
    # index + 1 because first column in db is ticker name
    db.insert(index+1,feature[0],pd.Series([None]*db.shape[0]))
    db.to_csv(DBNAME, index=False)
elif remove:
    if index<0: 
        index = len(features)+index
    if index >= len(features):
        print("Last index is prohibited. Read help.")
        sys.exit()

    del features[index]
    for i,f in enumerate(features):
        print(f'{i} {f}')
    resp = input("New features list. Is it ok? ")
    if not resp.strip().lower().startswith('y'):
        sys.exit()

    print(f'Writing {FEATURENAME}')
    with open('features.json','w',encoding='utf-8') as f:
        json.dump(features,f,ensure_ascii=False)
    
    print(f'Writing {DBNAME}')
    db = pd.read_csv(DBNAME)
    # index + 1 because first column in db is ticker name
    db.drop(db.columns[index+1],axis=1,inplace=True)
    db.to_csv(DBNAME, index=False)
    pass 
