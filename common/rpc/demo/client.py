import grpc
import demo_pb2_grpc
import demo_pb2


def run():
    with grpc.insecure_channel('127.0.0.1:8888') as channel:
        stub = demo_pb2_grpc.DemoStub(channel)

        work = demo_pb2.Work()
        work.num1 = 100
        work.num2 = 60
        work.op = demo_pb2.Work.ADD

        ret = stub.Calculate(work)
        # ret -> Result
        print(ret.val)


if __name__ == '__main__':
    run()