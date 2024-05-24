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

from flask_restx import Resource, Api,Namespace
import large_image
from flask import jsonify, send_file
import io
from flask_cors import CORS, cross_origin

api_ns_image = Namespace('image', description='Image related operations')


@api_ns_image.route('/tile/<int:z>/<int:x>/<int:y>', endpoint='tile')
class Tile(Resource):
    def get(self, z, x, y):
        # path = '/home/jackson/research/data/tortuosity_study/tortuosity_training_set/_1687394.svs'
        path = '/mnt/nas/emory_datasets/pathomics_data/gu/kidney/umich/neptune/Neptune_Master_WSI/FSGS/13_266069_040_003 L02 PAS.ndpi'
        source = large_image.open(path)
        img = source.getTile(x, y, z, pilImageAllowed=True)
        img_bytes = io.BytesIO()
        img.save(img_bytes, 'PNG')
        img_bytes.seek(0)
        return send_file(img_bytes, mimetype='image/png')


@api_ns_image.route('/tile/info', endpoint='tile_info')
class TileInfo(Resource):
    def get(self):
        path = '/mnt/nas/emory_datasets/pathomics_data/gu/kidney/umich/neptune/Neptune_Master_WSI/FSGS/13_266069_040_003 L02 PAS.ndpi'
        source = large_image.open(path)
        out_dict = {
            'sizeX': source.sizeX,
            'sizeY': source.sizeY,
            'tileWidth': source.tileWidth,
            'tileHeight': source.tileHeight
        }
        return out_dict


# FLASK ANNOTATION SERVER ENDPOINTS
Base = declarative_base()


class Annotation(Base):
    __tablename__ = 'annotations'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    color = Column(ARRAY(Integer))
    coordinates = Column(Geometry('POLYGON'))


# Create a connection to CockroachDB
engine = create_engine('cockroachdb://root@localhost:26257/test1')

# http://localhost:5005/image/annotations?minx=39040&miny=28743&maxx=39042&maxy=28745
@api_ns_image.route('/annotations', endpoint='annotations')
class Annotations(Resource):
    def get(self):
        try:
            minx = float(request.args.get('minx'))
            miny = float(request.args.get('miny'))
            maxx = float(request.args.get('maxx'))
            maxy = float(request.args.get('maxy'))

            centroid_only = bool(request.args.get('centroid'))
            bounding_box = ST_MakeEnvelope(minx, miny, maxx, maxy)

            Session = sessionmaker(bind=engine)
            session = Session()
            annotations = session.query(Annotation).filter(ST_Intersects(Annotation.coordinates, bounding_box)).all()

            if centroid_only:
                results = [
                    geojson.Feature(geometry=mapping(wkb.loads(str(ann.coordinates)).centroid),
                                    properties={"color": ann.color, "name": ann.name})
                    for ann in annotations
                ]
            else:
                results = [
                    geojson.Feature(geometry=mapping(wkb.loads(str(ann.coordinates))),
                                    properties={"color": ann.color, "name": ann.name})
                    for ann in annotations
                ]

            output = {
                "type": "FeatureCollection",
                "features": results
            }
            return output, 200

        except Exception as e:
            return jsonify({'error': str(e)}), 400