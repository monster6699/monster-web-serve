from flask import Blueprint
from flask_restful import Api

from . import user
from utils.output import output_json

admin_bp = Blueprint('admin', __name__)
admin_api = Api(admin_bp, catch_all_404s=True)
admin_api.representation('application/json')(output_json)

admin_api.add_resource(user.AdminUserListResource, '/admin/user/list', endpoint='AdminUserListResource')
admin_api.add_resource(user.AdminUserInfoResource, '/admin/user/info/<int(min=1):user_id>',
                       endpoint='AdminUserInfoResource')

admin_api.add_resource(user.AdminUserUpdateResource, '/admin/user/update',
                       endpoint='AdminUserUpdateResource')

admin_api.add_resource(user.AdminMenuInfoResource, '/admin/menu/list',
                       endpoint='AdminMenuInfoResource')

admin_api.add_resource(user.AdminRolesResource, '/admin/role/list',
                       endpoint='AdminRolesResource')

admin_api.add_resource(user.AdminGetRoleInfoResource, '/admin/user/role/<int(min=1):user_id>',
                       endpoint='AdminGetRoleInfoResource')

admin_api.add_resource(user.AdminRoleUpdateResource, '/admin/user/role',
                       endpoint='AdminRoleUpdateResource')

admin_api.add_resource(user.AdminRestPasswordResource, '/admin/user/password/reset',
                       endpoint='AdminRestPasswordResource')

admin_api.add_resource(user.AdminLogOutResource, '/user/logout',
                       endpoint='AdminLogOutResource')

admin_api.add_resource(user.AdminGetParentMenuResource, '/admin/menu/parentMenuList',
                       endpoint='AdminGetParentMenuResource')

admin_api.add_resource(user.AdminCreateMenuResourece, '/admin/menu/create',
                       endpoint='AdminCreateMenuResourece')

admin_api.add_resource(user.AdminGetSingleMenuResource, '/admin/menu/info',
                       endpoint='AdminGetSingleMenuResource')

admin_api.add_resource(user.AdmminUpdateMenyResource, '/admin/menu/update',
                       endpoint='AdmminUpdateMenyResource')

admin_api.add_resource(user.AdmminGetSingleRoleResource, '/admin/role/info',
                       endpoint='AdmminGetSingleRoleResource')

admin_api.add_resource(user.AdmminUpdateSingleRoleResource, '/admin/role/update',
                       endpoint='AdmminUpdateSingleRoleResource')

admin_api.add_resource(user.AdminGetMenuInfoResource, '/admin/role/menu',
                       endpoint='AdminGetMenuInfoResource')

admin_api.add_resource(user.AdminUpdateRoleMenuInfoResource, '/admin/role/menu',
                       endpoint='AdminUpdateRoleMenuInfoResource')