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

import ray

ray.init()

from glob import glob
import shapely
from shapely.geometry import shape

# Define the base class for ORM
Base = declarative_base()
def getAnnotationClass(tablename):# Define the Annotation class
    class Annotation(Base):
        __tablename__ = tablename
    
        id = Column(Integer, primary_key=True)
        name = Column(String)
        color = Column(ARRAY(Integer))
        coordinates = Column(Geometry('POLYGON'))
    return Annotation


@ray.remote
def commit(tablename,annos):
    from sqlalchemy import create_engine, Column, String, Integer, func
    from sqlalchemy import create_engine, Column, String, Integer, func
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.dialects.postgresql import ARRAY
    from sqlalchemy.orm import sessionmaker
    from geoalchemy2 import Geometry 
    from tqdm import tqdm
    import numpy as np

    Base = declarative_base()

    def getAnnotationClass(tablename):# Define the Annotation class
        class Annotation(Base):
            __tablename__ = tablename
        
            id = Column(Integer, primary_key=True)
            name = Column(String)
            color = Column(ARRAY(Integer))
            coordinates = Column(Geometry('POLYGON'))
        return Annotation
    Annotation=getAnnotationClass(tablename);
    
    db_url=np.random.choice(['cockroachdb://root@170.140.138.87:26257/test1',
                             'cockroachdb://root@170.140.138.63:26257/test1',
                             'cockroachdb://root@170.140.138.73:26257/test1'])

    engine = create_engine(db_url)#,echo=True)
    # Create a session
    Session = sessionmaker(bind=engine)
    session = Session()
    for a in annos:
        session.add(Annotation(name=a[0], color=a[1], coordinates=a[2].wkt))
    
    session.commit()
    session.close()


engine = create_engine('cockroachdb://root@170.140.138.87:26257/test1')#,echo=True)

from sqlalchemy_utils import database_exists, create_database
create_database(engine.url)    

wsifnames=glob('*.ndpi')
for i,wsifname in enumerate(wsifnames):
    jsonfname=wsifname.replace("ndpi","json")
    with open(jsonfname, 'r') as file:
        data = json.load(file)

    tablename=f'a_{i}'
    Annotation=getAnnotationClass(tablename)
    
    Base.metadata.create_all(engine)

    tasks = []
    all_anno=[]
    for i,d in enumerate(tqdm(data)):
        shapely_geometry = shape(d['geometry'])
        name = d['properties']['classification']['name']
        color = d['properties']['classification']['color']
        geom = shapely_geometry
        
        all_anno.append([name,color,geom])
        if len(all_anno)==1_000:
            task= commit.remote(tablename,all_anno)
            tasks.append(task)
            all_anno=[]
            
        
    
    print("waiting")
    vals=ray.get(tasks)
    print(len(vals))


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

shapely_obj.bounds

import openslide

i

Annotation.__tablename__

osh=openslide.open_slide(wsifnames[1])

osh.level_dimensions

coords=[int(a) for a in shapely_obj.bounds[0:2]]

xwidth=int(shapely_obj.bounds[2]-shapely_obj.bounds[0])
ywidth=int(shapely_obj.bounds[3]-shapely_obj.bounds[1])

i=np.asarray(osh.read_region(coords,0,(xwidth,ywidth)))

import matplotlib.pyplot as plt

plt.imshow(i)

shapely_obj

# +
import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import Polygon
from matplotlib.patches import Polygon as PolygonPatch
from skimage.draw import polygon


def generate_binary_mask(shape_obj):
    # Get the bounds of the shape object
    min_x, min_y, max_x, max_y = shape_obj.bounds

    # Extract coordinates of the shape object
    coords = np.array(shape_obj.exterior.coords.xy).T

    # Shift the coordinates to fit within the bounding box
    shifted_coords = coords - np.array([min_x, min_y])

    # Calculate the dimensions of the binary mask
    width, height = int(max_x - min_x), int(max_y - min_y)

    # Create a blank mask
    mask = np.zeros((height, width), dtype=np.uint8)

    # Fill the mask with the shape object
    # Fill the mask with the shape object
    rr, cc = polygon(shifted_coords[:, 1], shifted_coords[:, 0], shape=mask.shape)
    mask[rr, cc] = 1


    return mask
# -

mask=generate_binary_mask(shapely_obj)

plt.imshow(mask)

# +
masked_image = np.copy(i)
masked_image[mask == 1] = masked_image[mask == 1]*.5

# Plot the overlay
plt.imshow(masked_image)
plt.show()
# -



















mask.shape

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


