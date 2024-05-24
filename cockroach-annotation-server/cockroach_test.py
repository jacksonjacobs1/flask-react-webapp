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

import json

with open('15_26609_024_045 L03 PAS.json', 'r') as file:
    # Load the JSON data into a Python dictionary
    data = json.load(file)

data

len(data)

set([d['type'] for d in data])

# data[].keys()

data[0]['properties']

data[0]['geometry'].keys()

from geoalchemy2 import Geometry 

from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, Column, String, Integer, func


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
engine = create_engine('cockroachdb://root@localhost:26257/file1_test')

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
# Create a session
Session = sessionmaker(bind=engine)
session = Session()

# Create an instance of Annotation and insert it into the database
#new_annotation = Annotation(name="Example", color=[255, 0, 0], coordinates=[(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)])
coordinates = [(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)]
polygon_wkt = "POLYGON((" + ", ".join([f"{x} {y}" for x, y in coordinates]) + "))"

new_annotation = Annotation(name="Example1", color=[255, 0, 0], coordinates=polygon_wkt)

session.add(new_annotation)
session.commit()

# Close the session
session.close()

# +
from shapely.geometry import Point
from geoalchemy2.functions import ST_Contains
from geoalchemy2 import WKTElement

point = Point(0.5, 0.5)

# Query annotations containing the point
results = session.query(Annotation).filter(ST_Contains(Annotation.coordinates, point.wkb)).all()

# -

# Print the results
for annotation in results:
    print(annotation.name)
