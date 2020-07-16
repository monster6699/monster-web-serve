from flask import request, g

from .jwt_util import verify_jwt


def jwt_authentication():
    """
    根据jwt验证用户身份
    """
    g.user_id = None
    g.use_token = False
    g.anonymous_id = None
    g.is_verified = False
    authorization = request.headers.get('Authorization')
    if authorization and authorization.startswith('bearer '):
        g.use_token = True
        token = authorization.strip()[7:]
        payload = verify_jwt(token)
        if payload:
            g.user_id = payload.get('user_id')
            g.is_refresh_token = payload.get('refresh')
            g.is_verified = payload.get('verified', False)
    elif authorization and authorization.startswith('Anony '):
        g.anonymous_id = authorization.strip()[6:]


