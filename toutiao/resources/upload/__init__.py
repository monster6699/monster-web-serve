from flask import Blueprint
from flask_restful import Api

from . import images
from utils.output import output_json

upload_bp = Blueprint('upload', __name__)
upload_api = Api(upload_bp, catch_all_404s=True)
upload_api.representation('application/json')(output_json)

upload_api.add_resource(images.UploadImageResource, '/upload/images', endpoint='UploadImageResource')


