import json
import random

from flask import current_app
from flask_restful import Resource
from flask_restful.reqparse import RequestParser
from sqlalchemy import func
import time

from utils.decorators import login_required, set_db_to_read, set_db_to_write
from models import db
from models.administor import Administrator, AdministratorMenu, AdministratorRole, \
    AdministratorUserRole, AdministratorRoleMenu


class AdminUserListResource(Resource):
    """
    获取管理员信息
    """
    method_decorators = [set_db_to_read, login_required]

    def get(self):
        """
        获取管理员信息
        """
        json_parser = RequestParser()
        json_parser.add_argument('page', type=int, required=True, location='args')
        json_parser.add_argument('per_page', type=int, required=True, location='args')
        json_parser.add_argument('sort', type=str, required=False, location='args')
        args = json_parser.parse_args()
        offset = (args.page - 1) * args.per_page
        # total = Administrator.query.count()
        # 优化
        total = Administrator.query.with_entities(func.count(Administrator.id)).scalar()
        admin_user_list = Administrator.query.filter_by().offset(offset).limit(args.per_page).all()
        data = []
        for admin_user in admin_user_list:
            result = {
                "id": admin_user.id,
                "username": admin_user.username,
                "name": admin_user.name,
                "email": admin_user.email,
                "mobile": admin_user.mobile,
                "remark": admin_user.remark,
                "status": admin_user.status
            }
            data.append(result)
        data = {
            "total": total,
            "current_page": args.page,
            "per_page": args.per_page,
            "data": data
        }
        return data


class AdminUserInfoResource(Resource):
    """
    获取单个管理员信息
    """
    method_decorators = [set_db_to_read, login_required]

    def get(self, user_id):
        admin_user_info = Administrator.query.filter_by(id=user_id).first()
        result = {
            "id": admin_user_info.id,
            "username": admin_user_info.username,
            "name": admin_user_info.name,
            "email": admin_user_info.email,
            "mobile": admin_user_info.mobile,
            "remark": admin_user_info.remark,
            "status": admin_user_info.status
        }
        return result


class AdminUserUpdateResource(Resource):
    """
    修改用户信息
    """
    method_decorators = [set_db_to_write, login_required]

    @staticmethod
    def post():
        json_parser = RequestParser()
        json_parser.add_argument('id', type=int, required=True, location='json')
        json_parser.add_argument('name', type=str, required=True, location='json')
        json_parser.add_argument('email', type=str, required=True, location='json')
        json_parser.add_argument('mobile', type=str, required=True, location='json')
        json_parser.add_argument('remark', type=str, required=False, location='json')
        json_parser.add_argument('status', type=str, required=False, location='json')
        args = json_parser.parse_args()
        admin_user_info = Administrator.query.filter_by(id=args.id).first()
        admin_user_info.name = args.name
        admin_user_info.email = args.email
        admin_user_info.mobile = args.mobile
        admin_user_info.remark = args.remark
        admin_user_info.status = args.status
        db.session.add(admin_user_info)
        db.session.commit()
        return "ok"


class AdminMenuInfoResource(Resource):
    """
    获取菜单
    """
    method_decorators = [set_db_to_read, login_required]

    def get(self):
        """
        获取所有的菜单数据
        """
        menu_list = AdministratorMenu.query.all()
        resualt = []
        for menu in menu_list:
            menu_dict = {
                "id": menu.id,
                "name": menu.name,
                "path": menu.path,
                "parent_id": menu.parent_id,
                "meta": json.loads(menu.meta),
                "fullPath": menu.full_path,
                "menuOrder": menu.menu_order,
                "remark": menu.remark,
                "redirect": menu.redirect,
                "hidden": menu.hidden,
                "status": menu.status
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


class AdminRolesResource(Resource):
    """
    获取所有角色信息
    """
    method_decorators = [set_db_to_read, login_required]

    def get(self):
        """
        获取角色信息
        """
        json_parser = RequestParser()
        json_parser.add_argument('page', type=int, required=True, location='args')
        json_parser.add_argument('per_page', type=int, required=True, location='args')
        json_parser.add_argument('sort', type=str, required=False, location='args')
        args = json_parser.parse_args()
        offset = (args.page - 1) * args.per_page
        # total = AdministratorRole.query.count()
        # 优化
        total = AdministratorRole.query.with_entities(func.count(AdministratorRole.id)).scalar()
        admin_user_list = AdministratorRole.query.filter_by().offset(offset).limit(args.per_page).all()
        data = []
        for admin_user in admin_user_list:
            result = {
                "id": admin_user.id,
                "name": admin_user.name,
                "remark": admin_user.remark,
                "status": admin_user.status
            }
            data.append(result)
        data = {
            "total": total,
            "current_page": args.page,
            "per_page": args.per_page,
            "data": data
        }
        return data


class AdminRoleUpdateResource(Resource):
    """
    设置用户角色
    """
    method_decorators = [set_db_to_write, login_required]

    @staticmethod
    def post():
        json_parser = RequestParser()
        json_parser.add_argument('data', action='append', type=str, required=True, location='json')
        args = json_parser.parse_args()
        for item in args.data:
            item = dict(eval(item))
            role_list = AdministratorUserRole.query.filter_by(user_id=int(item['userId']),
                                                              role_id=int(item['roleId'])).all()
            if len(role_list) > 0:
                for role in role_list:
                    role.status = item['status']
                    role.utime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                    db.session.add(role)
                db.session.commit()
            else:
                au = AdministratorUserRole(user_id=int(item['userId']), role_id=int(item['roleId']),
                                           status=int(item['status']))
                db.session.add(au)
                db.session.commit()
        return "ok"


class AdminGetRoleInfoResource(Resource):
    """
    获取用户角色
    """
    method_decorators = [set_db_to_read, login_required]

    @staticmethod
    def get(user_id):
        role_list = AdministratorUserRole.query.filter_by(user_id=user_id, status=1).all()
        role_id_list = []
        for role in role_list:
            role_id_list.append(role.role_id)
        role_in_info = AdministratorRole.query.filter(AdministratorRole.id.in_(role_id_list),
                                                      AdministratorRole.status == 1).all()
        role_not_info = AdministratorRole.query.filter(AdministratorRole.id.notin_(role_id_list),
                                                       AdministratorRole.status == 1).all()
        data = []
        for role in role_in_info:
            result = {
                "id": role.id,
                "name": role.name,
                "remark": role.remark,
                "status": 1
            }
            data.append(result)
        for role in role_not_info:
            result = {
                "id": role.id,
                "name": role.name,
                "remark": role.remark,
                "status": 0
            }
            data.append(result)
        return data


class AdminRestPasswordResource(Resource):
    """
    重置密码
    """
    method_decorators = [set_db_to_read, login_required]

    def post(self):
        json_parser = RequestParser()
        json_parser.add_argument('id', type=str, required=True, location='json')
        args = json_parser.parse_args()
        user = Administrator.query.filter_by(id=args.id).first()
        new_password = self._generate_code()
        user.password = new_password
        db.session.add(user)
        db.session.commit()
        return {"password": new_password}

    @staticmethod
    def _generate_code(code_len=6):
        all_char = '0123456789qazwsxedcrfvtgbyhnujmikolpQAZWSXEDCRFVTGBYHNUJIKOLP'
        index = len(all_char)
        code = ''
        for _ in range(code_len):
            num = random.randint(0, index)
            code += all_char[num]
        return code


class AdminLogOutResource(Resource):
    """
    退出登录, 目前清除token后端无法实现
    """
    method_decorators = [set_db_to_read, login_required]

    @staticmethod
    def post():
        return "ok"


class AdminGetParentMenuResource(Resource):
    """
    获取一级菜单
    """
    method_decorators = [set_db_to_read, login_required]

    @staticmethod
    def get():
        menu_list = AdministratorMenu.query.filter_by(parent_id=0).all()
        data = []
        for menu in menu_list:
            data.append({
                "id": menu.id,
                "name": menu.name
            })
        return data


class AdminCreateMenuResourece(Resource):
    """
    创建菜单
    """
    method_decorators = [set_db_to_read, login_required]

    @staticmethod
    def post():
        json_parser = RequestParser()
        json_parser.add_argument('meta', type=str, required=True, location='json')
        json_parser.add_argument('fullPath', type=str, required=True, location='json')
        json_parser.add_argument('name', type=str, required=True, location='json')
        json_parser.add_argument('order', type=str, required=True, location='json')
        json_parser.add_argument('parentId', type=str, required=True, location='json')
        json_parser.add_argument('path', type=str, required=True, location='json')
        json_parser.add_argument('redirect', type=str, required=False, location='json')
        json_parser.add_argument('remark', type=str, required=False, location='json')
        json_parser.add_argument('status', type=int, required=True, location='json')
        args = json_parser.parse_args()
        try:
            menu = AdministratorMenu(meta=json.dumps(dict(eval(args.meta)), ensure_ascii=False),
                                     full_path=args.fullPath, name=args.name,
                                     menu_order=args.order,
                                     parent_id=args.parentId, path=args.path, redirect=args.redirect,
                                     remark=args.remark,
                                     status=args.status)
            db.session.add(menu)
            db.session.commit()
            menu_id = AdministratorMenu.query.filter_by(path=args.path).first()
            save_menu = AdministratorRoleMenu(role_id=1, menu_id=menu_id.id, status=1)
            db.session.add(save_menu)
            db.session.commit()
        except Exception as e:
            print(e)
            db.session.rollback()
            db.session.commit()
            return {"message": 'add error'}, 405
        return "ok"


class AdminGetSingleMenuResource(Resource):
    """
    get single menu
    """
    method_decorators = [set_db_to_read, login_required]

    @staticmethod
    def get():
        json_parser = RequestParser()
        json_parser.add_argument('menuId', type=str, required=True, location='args')
        args = json_parser.parse_args()
        menu = AdministratorMenu.query.filter_by(id=args.menuId).first()
        data = {
            "id": menu.id,
            "name": menu.name,
            "path": menu.path,
            "fullPath": menu.full_path,
            "order": menu.menu_order,
            "remark": menu.remark,
            "redirect": menu.redirect,
            "meta": json.loads(menu.meta),
            "status": menu.status,
        }
        return data


class AdmminUpdateMenyResource(Resource):
    """
        update single menu
        """
    method_decorators = [set_db_to_read, login_required]

    @staticmethod
    def post():
        json_parser = RequestParser()
        json_parser.add_argument('id', type=int, required=True, location='json')
        json_parser.add_argument('meta', type=str, required=True, location='json')
        json_parser.add_argument('fullPath', type=str, required=True, location='json')
        json_parser.add_argument('name', type=str, required=True, location='json')
        json_parser.add_argument('order', type=str, required=True, location='json')
        json_parser.add_argument('path', type=str, required=True, location='json')
        json_parser.add_argument('redirect', type=str, required=False, location='json')
        json_parser.add_argument('remark', type=str, required=False, location='json')
        json_parser.add_argument('status', type=int, required=True, location='json')
        args = json_parser.parse_args()
        menu = AdministratorMenu.query.filter_by(id=args.id).first()
        menu.meta = json.dumps(dict(eval(args.meta)), ensure_ascii=False)
        menu.full_path = args.fullPath
        menu.name = args.name
        menu.menu_order = args.order
        menu.path = args.path
        menu.redirect = args.redirect
        menu.redirect = args.remark
        menu.status = args.status
        db.session.add(menu)
        db.session.commit()
        return "ok"


class AdmminGetSingleRoleResource(Resource):
    """
        get single role
        """
    method_decorators = [set_db_to_read, login_required]

    @staticmethod
    def get():
        json_parser = RequestParser()
        json_parser.add_argument('roleId', type=int, required=True, location='args')
        args = json_parser.parse_args()
        role = AdministratorRole.query.filter_by(id=args.roleId).first()
        data = {
            "id": role.id,
            "name": role.name,
            "status": role.status,
            "remark": role.remark,
        }
        return data


class AdmminUpdateSingleRoleResource(Resource):
    """
        Update single role
        """
    method_decorators = [set_db_to_read, login_required]

    @staticmethod
    def post():
        json_parser = RequestParser()
        json_parser.add_argument('id', type=int, required=True, location='json')
        json_parser.add_argument('name', type=str, required=True, location='json')
        json_parser.add_argument('status', type=str, required=True, location='json')
        json_parser.add_argument('remark', type=str, required=True, location='json')
        args = json_parser.parse_args()
        role = AdministratorRole.query.filter_by(id=args.id).first()
        role.name = args.name
        role.status = args.status
        role.remark = args.remark
        db.session.add(role)
        db.session.commit()
        return "ok"


class AdminGetMenuInfoResource(Resource):
    """
    获取角色菜单
    """
    method_decorators = [set_db_to_read, login_required]

    def get(self):
        json_parser = RequestParser()
        json_parser.add_argument('roleId', type=int, required=True, location='args')
        args = json_parser.parse_args()
        menu_list = AdministratorRoleMenu.query.filter_by(role_id=args.roleId, status=1).all()
        menu_id_list = []
        for menu in menu_list:
            menu_id_list.append(menu.menu_id)
        menu_in_info = AdministratorMenu.query.filter(AdministratorMenu.status == 1).all()
        resualt = []
        for menu in menu_in_info:
            menu_dict = {
                "id": menu.id,
                "name": menu.name,
                "path": menu.path,
                "parentId": menu.parent_id,
                "meta": json.loads(menu.meta),
                "fullPath": menu.full_path,
                "menuOrder": menu.menu_order,
                "remark": menu.remark,
                "redirect": menu.redirect,
                "hidden": menu.hidden,
                "status": 1 if menu.id in menu_id_list else 0
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
            if node['parentId'] == parent_id:
                parent_list.append(node)
        return parent_list

    @staticmethod
    def _find_children_node(node_list, parent_id):
        children_list = []
        for node in node_list:
            if node['parentId'] == parent_id:
                children_list.append(node)
        return children_list


class AdminUpdateRoleMenuInfoResource(Resource):
    """
    设置角色菜单
    """
    method_decorators = [set_db_to_write, login_required]

    @staticmethod
    def post():
        json_parser = RequestParser()
        json_parser.add_argument('data', action='append', type=str, required=True, location='json')
        args = json_parser.parse_args()
        menu_parent_list = AdministratorMenu.query.filter_by(parent_id=0).all()
        patent_list = []
        for menu_parent in menu_parent_list:
            patent_list.append(menu_parent.id)
        for item in args.data:
            item = dict(eval(item))
            menu_list = AdministratorRoleMenu.query.filter(AdministratorRoleMenu.menu_id == int(item['menuId']),
                                                           AdministratorRoleMenu.role_id == int(item['roleId'])
                                                           ).all()
            if len(menu_list) > 0:
                for menu in menu_list:
                    menu.status = 1 if menu.menu_id in patent_list else item['status']
                    menu.utime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                    db.session.add(menu)
                db.session.commit()
            else:
                au = AdministratorRoleMenu(role_id=int(item['roleId']), menu_id=int(item['menuId']),
                                           status=int(item['status']))
                db.session.add(au)
                db.session.commit()
        return "ok"
