import  json


DBNAME='db_levels.csv'
FEATURENAME='features.json'

tooltip_delay = {
    'show':500,
    'hide':10
}

with open(FEATURENAME,'r') as f:
    features = json.load(f)
