from server import sio
import time
from werkzeug.wrappers import Request
from utils.jwt_util import verify_jwt


JWT_SECRET = 'TPmi4aLWRbyVq8zu9v82dWYW17/z+UvRnYTt4P6fAXA'


@sio.on('connect')
def on_connect(sid, environ):
    """
    当客户端连接时做的事情
    如果方法返回False，表示服务器拒绝客户端的socketio连接，
    :param environ: dict
    :return:
    """
    # print('sid={}'.format(sid))
    # print('environ={}'.format(environ))

    timestamp = time.time()
    sio.emit('notify', {'msg': 'Hello, this is notify event', 'timestamp': timestamp})
    # send -> event 'message'
    sio.send({'msg': 'Hello, this is message event', 'timestamp': timestamp})

    # 解析environ字典，取出查询字符串中传递的token
    request = Request(environ)
    token = request.args.get('token')

    # print('token=>{}'.format(token))

    # 验证token，获取用户身份
    if token:
        payload = verify_jwt(token, JWT_SECRET)
        # print('payload->{}'.format(payload))
        if payload is not None:
            user_id = payload['user_id']

            # 将用户添加到专属房间，房间编号为用户id，方便flask web那边的业务可以直接给user_id对应的房间发送消息
            sio.enter_room(sid, str(user_id))
            return
    return False


@sio.on('disconnect')
def on_disconnect(sid):
    """
    与客户端的连接断开之后执行的方法
    :param sid:
    :return:
    """
    # 将断开连接的客户端从他专属的房间中剔除

    # 获取一个socketio 用户的所有房间
    rooms = sio.rooms(sid)
    for room in rooms:
        sio.leave_room(sid, room)


@sio.on('notify')
def on_notify(sid, data):
    """
    收到客户端notify事件消息的时候执行
    :param sid:
    :param data:
    :return:
    """
    print('data->{}'.format(data))
    timestamp = time.time()
    sio.emit('notify', {'msg': 'I have received your msg: {}'.format(data), 'timestamp': timestamp})
