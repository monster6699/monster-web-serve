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
