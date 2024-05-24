from flask import Flask
from api import api_blueprint
from flask_cors import CORS, cross_origin


def run_app():
    app = Flask(__name__)
    app.debug = True
    app.config['CORS_HEADERS'] = 'Content-Type'

    app.register_blueprint(api_blueprint)
    CORS(app)
    app.logger.info(f'Flask server starting...')
    app.run(host='localhost', port=5005, debug=True, threaded=True)




if __name__ == '__main__':
    run_app()