from flask_restx import Resource, Api,Namespace
import large_image
from flask import jsonify, send_file
import io

api_ns_image = Namespace('image', description='Image related operations')


@api_ns_image.route('/tile/<int:z>/<int:x>/<int:y>', endpoint='tile')
class Tile(Resource):
    def get(self, z, x, y):
        path = '/home/jackson/research/data/tortuosity_study/tortuosity_training_set/_1687394.svs'
        source = large_image.open(path)
        img = source.getTile(x, y, z, pilImageAllowed=True)
        img_bytes = io.BytesIO()
        img.save(img_bytes, 'PNG')
        img_bytes.seek(0)
        return send_file(img_bytes, mimetype='image/png')

@api_ns_image.route('/tile/info', endpoint='tile_info')
class TileInfo(Resource):
    def get(self):
        path = '/home/jackson/research/data/tortuosity_study/tortuosity_training_set/_1687394.svs'
        source = large_image.open(path)
        out_dict = {
            'sizeX': source.sizeX,
            'sizeY': source.sizeY,
            'tileWidth': source.tileWidth,
            'tileHeight': source.tileHeight
        }
        return out_dict
