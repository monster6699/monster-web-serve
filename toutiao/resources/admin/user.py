from flask_restful import Resource
from flask_restful.reqparse import RequestParser
from flask import g, current_app
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
import time

from utils.decorators import login_required, set_db_to_read
from utils import parser
from models import db
from models.administor import Administrator
from models.news import Attitude, ArticleStatistic, CommentLiking, Comment
from cache import statistic as cache_statistic


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
                "status": admin_user.mobile
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
        print(admin_user_info)
        result = {
            "id": admin_user_info.id,
            "username": admin_user_info.username,
            "name": admin_user_info.name,
            "email": admin_user_info.email,
            "mobile": admin_user_info.mobile,
            "remark": admin_user_info.remark,
            "status": admin_user_info.mobile
        }
        return result
