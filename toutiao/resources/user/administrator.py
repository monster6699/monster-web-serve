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
            "username": user_info.username,
            "name": user_info.name,
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
        role = AdministratorUserRole.query.filter_by(user_id=g.user_id, status=1).first()
        user_menu = AdministratorRoleMenu.query.filter_by(role_id=role.role_id, status=1).all()
        menu_list = []
        for menu in user_menu:
            menu_list.append(menu.menu_id)
        role_menu = AdministratorMenu.query.filter(AdministratorMenu.id.in_(menu_list),
                                                   AdministratorMenu.status == 1).all()
        resualt = []
        for menu in role_menu:
            menu_dict = {
                "id": menu.id,
                "name": menu.name,
                "path": menu.path,
                "parent_id": menu.parent_id,
                "meta": json.loads(menu.meta),
                "fullPath": menu.full_path,
                "redirect": menu.redirect,
                "hidden": menu.hidden
            }
            resualt.append(menu_dict)
        parent_list = self._find_parent_node(resualt)
        res = self.fomate_menu(resualt, parent_list)
        return res

    def fomate_menu(self, resualt, parent_list):
        if len(parent_list) == 0:
            return []
        for parent in parent_list:
            parent['children'] = self._find_children_node(resualt, parent['id'])
            self.fomate_menu(resualt, parent['children'])
        return parent_list

    @staticmethod
    def _find_parent_node(node_list, parent_id=0):
        parent_list = []
        for node in node_list:
            if node['parent_id'] == parent_id:
                parent_list.append(node)
        return parent_list

    @staticmethod
    def _find_children_node(node_list, parent_id):
        children_list = []
        for node in node_list:
            if node['parent_id'] == parent_id:
                children_list.append(node)
        return children_list
