import socketio


RABBITMQ = 'amqp://python:rabbitmqpwd@localhost:5672/toutiao'

# 创建一个从rabbitmq队列中取出需要推送消息的辅助工具
mgr = socketio.KombuManager(RABBITMQ)

# 像创建flask程序对象一样，创建socketio对象
sio = socketio.Server(async_mode='eventlet', client_manager=mgr)
app = socketio.Middleware(sio)
