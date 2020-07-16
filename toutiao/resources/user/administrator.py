import json

from flask_restful import Resource
from flask import g, current_app
from flask_restful.reqparse import RequestParser
from flask_restful import inputs
from sqlalchemy.exc import IntegrityError
from models.administor import AdministratorUserRole, AdministratorMenu, AdministratorRoleMenu, db
from utils.decorators import login_required
from cache import user as cache_user
from models.toutiao_user import User, UserProfile
from utils import parser
from models import db
from utils.storage import upload_image
from utils.decorators import set_db_to_write, set_db_to_read


class CurrentUserResource(Resource):
    """
    用户自己的数据
    """
    method_decorators = [set_db_to_read, login_required]

    @staticmethod
    def get():
        """
        获取当前用户自己的数据
        """
        user_data = AdministratorUserRole.query.filter_by(user_id=g.user_id).first()
        user_info = user_data.user
        result = {
            "id": user_info.id,
            "name": user_info.username,
            "mobile": user_info.mobile,
            "email": user_info.email,
            "roles": [user_data.role.name]
        }
        return result


class CurrentUserMenu(Resource):
    """
    获取用户菜单
    """
    method_decorators = [set_db_to_read, login_required]

    def get(self):
        """
        获取当前用户自己的菜单数据
        """
        role_id = AdministratorUserRole.query.filter_by(user_id=g.user_id).first()
        user_menu = AdministratorRoleMenu.query.filter(role_id == role_id).all()
        menu_list = []
        for menu_id in user_menu:
            menu_list.append(menu_id.id)
        role_menu = AdministratorMenu.query.filter(AdministratorMenu.id.in_(menu_list)).all()
        self.hanleFormateTree(role_menu)
        return "ok"

    def hanleFormateTree(self, menu_obj):
        resualt = []
        for menu in menu_obj:
            menu_dict = {
                "id": menu.id,
                "name": menu.name,
                "path": menu.path,
                "meta": json.loads(menu.meta),
                "children":
            }
            if menu.parent_id == 0:
                pass
        pass

