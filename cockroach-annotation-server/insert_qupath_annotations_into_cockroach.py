# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.16.1
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# +
#https://www.cockroachlabs.com/docs/stable/start-a-local-cluster-in-docker-linux.html#step-7-stop-the-cluster
# -

import json

from sqlalchemy import create_engine, Column, String, Integer, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import sessionmaker
from geoalchemy2 import Geometry 
from tqdm import tqdm

# %%time
with open('../data/13_266069_040_003 L02 PAS.json', 'r') as file:
    # Load the JSON data into a Python dictionary
    data = json.load(file)

import shapely
from shapely.geometry import shape


# +
# Define the base class for ORM
Base = declarative_base()

# Define the Annotation class
class Annotation(Base):
    __tablename__ = 'annotations'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    color = Column(ARRAY(Integer))
    coordinates = Column(Geometry('POLYGON'))


# -

# Create a connection to CockroachDB
#engine = create_engine('cockroachdb://root@170.140.138.73:26257/test1',echo=True)
engine = create_engine('cockroachdb://root@localhost:26257/test1')#,echo=True)

# +
from sqlalchemy_utils import database_exists, create_database

if not database_exists(engine.url):
    print("creating")
    create_database(engine.url)

print(database_exists(engine.url))
# -

# Create the table if it doesn't exist
Base.metadata.create_all(engine)

# +
# %%time
#--- reasonable
# Create a session
Session = sessionmaker(bind=engine)
session = Session()

for i,d in enumerate(tqdm(data)):
    shapely_geometry = shape(d['geometry'])
    new_annotation = Annotation(name=d['properties']['classification']['name'],
                                color=d['properties']['classification']['color'], 
                                coordinates=shapely_geometry.wkt)


    session.add(new_annotation)
    if i % 1_000 ==0:
        print("doing commit")
        session.commit()
        continue
        
    # if i % 100_000 == 0:
    #     break
session.commit()


# Close the session
session.close()
# -







# +
# %%time
# Create a session
Session = sessionmaker(bind=engine)
session = Session()


all_annos=[]
for d in tqdm(data):
    shapely_geometry = shape(d['geometry'])
    new_annotation = Annotation(name=d['properties']['classification']['name'],
                                color=d['properties']['classification']['color'], 
                                coordinates=shapely_geometry.wkt)

    all_annos.append(new_annotation)
    if(len(all_annos))==10:
        break

# +
# %%time    
session.add_all(all_annos)
session.commit()


# Close the session
session.close()

# +
# %%time
# Create a session
Session = sessionmaker(bind=engine)
session = Session()


all_annos=[]
for d in tqdm(data):
    shapely_geometry = shape(d['geometry'])
    new_annotation = Annotation(name=d['properties']['classification']['name'],
                                color=d['properties']['classification']['color'], 
                                coordinates=shapely_geometry.wkt)

    all_annos.append(new_annotation)

# +
# %%time
# Create a session
Session = sessionmaker(bind=engine)
session = Session()

for i,d in enumerate(tqdm(data)):
    shapely_geometry = shape(d['geometry'])
    new_annotation = Annotation(name=d['properties']['classification']['name'],
                                color=d['properties']['classification']['color'], 
                                coordinates=shapely_geometry.wkt)


    session.add(new_annotation)
    if i % 1000 ==0:
        print("doing commit")
        session.commit()
        continue
        
    if i % 100_000 == 0:
        break
session.commit()


# Close the session
session.close()

# +
#---------- below is scratch code for testing query
# -





from shapely.geometry import Point
from geoalchemy2.functions import ST_Contains, ST_Intersects, ST_AsBinary, ST_AsText
from geoalchemy2 import WKTElement

import numpy as np



query_geom = shape(data[0]['geometry'])
#query_geom = shape(np.random.choice(data)['geometry'])

Session = sessionmaker(bind=engine)
session = Session()


# +
# #%%timeit

query_geom = shape(np.random.choice(data)['geometry'])
results = session.query(Annotation).filter(ST_Contains(Annotation.coordinates, query_geom.centroid.wkt)).all()
# -

# Print the results
from shapely import wkt, wkb
for i,annotation in enumerate(results):
    print(i,annotation.name)
    shapely_obj=wkb.loads(str(annotation.coordinates))
    print(shapely_obj.centroid)

shapely_obj

# +

shapely_obj.centroid.y

# +
#--- below is scratch code for testing converting
# -

from shapely.geometry import mapping

geo=mapping(shapely_obj)

import geojson

# +

props={"color":[1,2,3],"name":"tubule"}
# -

props

feature = geojson.Feature(geometry=geo, properties=props)


geojson.dumps(feature)


