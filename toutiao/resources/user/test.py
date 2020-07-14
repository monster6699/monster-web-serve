from flask_restful import Resource
from flask import g, current_app
from flask_restful.reqparse import RequestParser
from flask_restful import inputs
from sqlalchemy.exc import IntegrityError

from utils.decorators import login_required
from cache import user as cache_user
from models.toutiao_user import User, UserProfile
from utils import parser
from models import db
from utils.storage import upload_image
from utils.decorators import set_db_to_write, set_db_to_read
from models.administor import Administrator, AdministratorMenu

class UserResource(Resource):
    """
    用户数据资源
    """

    method_decorators = {
        'get': [set_db_to_read],
    }

    def get(self):
        """
        获取target用户的数据
        :param target: 目标用户id
        """
        data = AdministratorMenu(id=2)

        print(data)
        return "ok"
