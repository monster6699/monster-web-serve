from flask_restful import Resource
from flask_limiter.util import get_remote_address
from flask import request, current_app, g
from flask_restful.reqparse import RequestParser
import random
from datetime import datetime, timedelta
from redis.exceptions import ConnectionError

from celery_tasks.sms.tasks import send_verification_code
from . import constants
from utils import parser
from models import db
from models.administor import Administrator
from models.toutiao_user import User, UserProfile
from utils.jwt_util import generate_jwt
from cache import user as cache_user
from utils.limiter import limiter as lmt
from utils.decorators import set_db_to_read, set_db_to_write


class SMSVerificationCodeResource(Resource):
    """
    短信验证码
    """
    error_message = 'Too many requests.'

    decorators = [
        lmt.limit(constants.LIMIT_SMS_VERIFICATION_CODE_BY_MOBILE,
                  key_func=lambda: request.view_args['mobile'],
                  error_message=error_message),
        lmt.limit(constants.LIMIT_SMS_VERIFICATION_CODE_BY_IP,
                  key_func=get_remote_address,
                  error_message=error_message)
    ]

    def get(self, mobile):
        code = '{:0>6d}'.format(random.randint(0, 999999))
        current_app.redis_master.setex('app:code:{}'.format(mobile), constants.SMS_VERIFICATION_CODE_EXPIRES, code)
        send_verification_code.delay(mobile, code)
        return {'mobile': mobile}


class AuthorizationResource(Resource):
    """
    认证
    """
    method_decorators = {
        'post': [set_db_to_write],
    }

    @staticmethod
    def _generate_tokens(user_id, with_refresh_token=True):
        """
        生成token 和refresh_token
        :param user_id: 用户id
        :return: token, refresh_token
        """
        # 颁发JWT
        now = datetime.utcnow()
        expiry = now + timedelta(hours=current_app.config['JWT_EXPIRY_HOURS'])
        # expiry = now + timedelta(minutes=current_app.config['JWT_EXPIRY_HOURS'])
        token = generate_jwt({'user_id': user_id, 'refresh': False}, expiry)
        refresh_token = None
        if with_refresh_token:
            refresh_expiry = now + timedelta(days=current_app.config['JWT_REFRESH_DAYS'])
            refresh_token = generate_jwt({'user_id': user_id, 'refresh': True}, refresh_expiry)
        return token, refresh_token

    def post(self):
        """
        登录创建token
        """
        json_parser = RequestParser()
        json_parser.add_argument('username', type=str, required=True, location='form')
        json_parser.add_argument('password', type=str, required=True, location='form')
        args = json_parser.parse_args()
        username = args.username
        password = args.password

        # # 查询或保存用户
        user = Administrator.query.filter_by(username=username).first()

        if user.check_password(password) is False:
            return {"message": "error"}, 500
        token, refresh_token = self._generate_tokens(user.id)
        return {"access_token": token, "refresh_token": refresh_token}, 200

    def put(self):
        """
        刷新token
        """
        user_id = g.user_id
        if user_id and g.is_refresh_token:

            # 判断用户状态
            user_enable = cache_user.UserStatusCache(g.user_id).get()
            if not user_enable:
                return {'message': 'User denied.'}, 403

            token, refresh_token = self._generate_tokens(user_id, with_refresh_token=False)

            return {'token': token}, 201

        else:

            return {'message': 'Wrong refresh token.'}, 403
