import demo_pb2_grpc
import demo_pb2
import grpc
from concurrent import futures
import time


class DemoServicer(demo_pb2_grpc.DemoServicer):

    def Calculate(self, request, context):
        """unary rpc
        """
        # request -> Work
        if request.op == demo_pb2.Work.ADD:
            ret = request.num1 + request.num2
            # result = Result(val=ret)
            result = demo_pb2.Result()
            result.val = ret
            return result

        elif request.op == demo_pb2.Work.SUBTRACT:
            result = request.num1 - request.num2
            return demo_pb2.Result(val=result)

        elif request.op == demo_pb2.Work.MULTIPLY:
            result = request.num1 * request.num2
            return demo_pb2.Result(val=result)

        elif request.op == demo_pb2.Work.DIVIDE:
            # 通过context设置异常的响应
            if request.num2 == 0:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details('cannot divide by 0')
                return demo_pb2.Result()

            result = request.num1 // request.num2
            return demo_pb2.Result(val=result)
        else:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('invalid operation')
            return demo_pb2.Result()


def serve():
    # 多线程服务器
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    # 注册本地服务
    demo_pb2_grpc.add_DemoServicer_to_server(DemoServicer(), server)
    # 监听端口
    server.add_insecure_port('127.0.0.1:8888')
    # 开始接收请求进行服务
    server.start()
    # 使用 ctrl+c 可以退出服务
    try:
        time.sleep(1000)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    serve()