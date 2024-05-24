from flask import Flask, request, jsonify

from sqlalchemy import create_engine, Column, String, Integer, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import ARRAY
from geoalchemy2 import Geometry
from geoalchemy2.functions import ST_Intersects, ST_MakeEnvelope
from sqlalchemy.orm import sessionmaker
from shapely.geometry import mapping
from shapely import wkt, wkb
import geojson

Base = declarative_base()

class Annotation(Base):
    __tablename__ = 'annotations'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    color = Column(ARRAY(Integer))
    coordinates = Column(Geometry('POLYGON'))

# Create a connection to CockroachDB
engine = create_engine('cockroachdb://root@localhost:26257/test1')

app = Flask(__name__)

@app.route('/annotations', methods=['GET'])
def get_annotations():
    try:
        # Parse bounding box coordinates from query parameters
        minx = float(request.args.get('minx'))
        miny = float(request.args.get('miny'))
        maxx = float(request.args.get('maxx'))
        maxy = float(request.args.get('maxy'))

        centroid_only = bool(request.args.get('centroid'))
        # Create bounding box envelope
        bounding_box = ST_MakeEnvelope(minx, miny, maxx, maxy)

        Session = sessionmaker(bind=engine)
        session = Session()
        # Query for annotations that intersect with the bounding box
        annotations = session.query(Annotation).filter(ST_Intersects(Annotation.coordinates, bounding_box)).all()

        # Convert results to a list of geojson with the correct properties
        # results = []
        # for ann in annotations:
        #     shapely_obj = wkb.loads(str(ann.coordinates))
        #     geo = mapping(shapely_obj)
        #     props = {"color": ann.color, "name": ann.name}
        #     geoann = geojson.Feature(geometry=geo, properties=props)
        #     results.append(geoann)

        if (centroid_only):
            results = [
                geojson.Feature(geometry=mapping(wkb.loads(str(ann.coordinates)).centroid),
                    properties={"color": ann.color, "name": ann.name }
                )
                for ann in annotations
            ]

        else:
            results = [
                geojson.Feature(geometry=mapping(wkb.loads(str(ann.coordinates))),
                    properties={"color": ann.color, "name": ann.name }
                )
                for ann in annotations
            ]

        return geojson.dumps(results), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 400


if __name__ == '__main__':
    app.run(debug=True)