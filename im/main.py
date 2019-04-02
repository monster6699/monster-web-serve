import eventlet
eventlet.monkey_patch()

import eventlet.wsgi
from server import app
import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, 'common'))


# 读取启动命令 python main.py [port] 通过启动命令传递端口号
# sys.argv保存启动参数的，列表  argv -> ['main.py', port]
if len(sys.argv) < 2:
    print('Usage: python main.py [port].')
    exit(1)  # 退出程序

import notify

port = int(sys.argv[1])
server_address = ('', port)
sock = eventlet.listen(server_address)
eventlet.wsgi.server(sock, app)
