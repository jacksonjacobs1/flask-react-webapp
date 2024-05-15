from flask import render_template, Blueprint, request, current_app, send_file
from flask_restx import Api
from api_image import api_ns_image

api_blueprint = Blueprint('image', __name__, template_folder='templates')

api = Api(
    api_blueprint,
    title='QA API',
    version='1.0',
    description='A description',
    # All API metadatas
)

api.add_namespace(api_ns_image)