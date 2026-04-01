""""""
import asyncio
import json
import logging

import grpc
from google.protobuf.json_format import MessageToDict

from ..config import settings
from ..protos_generated import service_pb2, service_pb2_grpc
from .texutal.widgets import BackendEventMessage

logging.basicConfig(
    level=logging.INFO,
    filename=str(settings.base_dir / "debug_client.log"),
    filemode="w", # 每次启动重新创建文件
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger("Client")


def run_client_logic(name="Pythoner", port="50051"):
    with grpc.insecure_channel(f'localhost:{port}') as channel:
        stub = service_pb2_grpc.GreeterStub(channel)
        response = stub.SayHello(service_pb2.HelloRequest(name=name))
        logger.info(f"[前端] 收到后端回复: {response.message}")
        return response.message


def run_backtest(name="Pythoner", port="50051"):
    with grpc.insecure_channel(f'localhost:{port}') as channel:
        stub = service_pb2_grpc.BacktesterStub(channel)
        response = stub.StartBacktest(service_pb2.BacktestRequest(name=name))
        result = MessageToDict(response)
        logger.info("回测完成")
        return result


def get_backtest_result(name="Pythoner", port="50051"):
    with grpc.insecure_channel(f'localhost:{port}') as channel:
        stub = service_pb2_grpc.BacktesterStub(channel)
        response = stub.GetTargetBacktestResult(service_pb2.BacktestRequest(name=name))
        result = MessageToDict(response)
        logger.info("回测结果查询完成")
        return result


def get_all_backtest_results(name="Pythoner", port="50051"):
    with grpc.insecure_channel(f'localhost:{port}') as channel:
        stub = service_pb2_grpc.BacktesterStub(channel)
        response = stub.GetAllBacktestResults(service_pb2.BacktestRequest(name=name))
        dicts = [MessageToDict(r, preserving_proto_field_name=True) for r in response.results]
        logger.info("所有回测结果查询完成")
        return dicts


def add_gateway(gateway_name="Pythoner", port="50051"):
    with grpc.insecure_channel(f'localhost:{port}') as channel:
        stub = service_pb2_grpc.GatewayManagerStub(channel)
        response = stub.AddGateway(service_pb2.GatewayRequest(gateway_name=gateway_name))
        logger.info(f"[前端] 收到后端回复: {response.message}")
        return response.message


def send_order(gateway_name="Pythoner", port="50051"):
    with grpc.insecure_channel(f'localhost:{port}') as channel:
        stub = service_pb2_grpc.GatewayManagerStub(channel)
        response = stub.SendOrder(service_pb2.SendOrderRequest(gateway_name=gateway_name))
        logger.info(f"[前端] 收到后端回复: {response.order_id}")
        return response.order_id

def sync_data(gateway_name="Pythoner", port="50051", symbol=""):
    with grpc.insecure_channel(f'localhost:{port}') as channel:
        stub = service_pb2_grpc.DataManagerStub(channel)
        response = stub.SyncData(service_pb2.SyncDataRequest(symbol=symbol))
        # logger.info(f"[前端] 收到后端回复: {response.order_id}")
        return response.data_id

def get_overview(gateway_name="Pythoner", port="50051"):
    with grpc.insecure_channel(f'localhost:{port}') as channel:
        stub = service_pb2_grpc.DataManagerStub(channel)
        response = stub.GetOverview(service_pb2.GetOverviewRequest(data_id=""))
        dicts = [MessageToDict(r, preserving_proto_field_name=True) for r in response.results]
        return dicts


async def listen_to_backend(callbacks, port="50051"):
    """"""
    async with grpc.aio.insecure_channel(f'localhost:{port}') as channel:
        stub = service_pb2_grpc.EventEngineStub(channel)

        try:
            # 开启 gRPC 异步流
            stream = stub.SubscribeEvents(service_pb2.Empty())
            async for event in stream:
                # 收到后端事件，直接转换并“发给”自己（Textual 引擎）
                message = BackendEventMessage(event.name, event.data)
                callbacks[0](f"{message.event_type} 和 {message.event_data}")
                if message.event_type == "event_tick." and message.event_data != "pong":
                    data = json.loads(message.event_data).get("data", None)
                    if data:
                        callbacks[1](data)
        except grpc.aio.AioRpcError as e:
            # 处理连接断开的情况
            callbacks[0](f"连接异常: {e.details()}")
            logger.warning("前端回调异常")
        except asyncio.CancelledError:
            logger.info("回调断开")
        finally:
            logger.info("回调结束")

