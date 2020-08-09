from flask import Blueprint
from flask_restful import Api

from . import upload
from utils.output import output_json

actilce_bp = Blueprint('admin', __name__)
acticle_api = Api(actilce_bp, catch_all_404s=True)
acticle_api.representation('application/json')(output_json)

acticle_api.add_resource(user.AdminUserListResource, '/admin/user/list', endpoint='AdminUserListResource')