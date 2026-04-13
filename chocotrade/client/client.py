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


def sync_data(
        gateway_name="Pythoner",
        port="50051",
        interface="",
        symbol="",
        start_time="",
        end_time="",
        granularity="",
        storage=""
    ):
    with grpc.insecure_channel(f'localhost:{port}') as channel:
        stub = service_pb2_grpc.DataManagerStub(channel)
        response = stub.SyncData(service_pb2.SyncDataRequest(
            interface=interface,
            symbol=symbol,
            start_time=start_time,
            end_time=end_time,
            granularity=granularity,
            storage=storage
        ))
        # logger.info(f"[前端] 收到后端回复: {response.order_id}")
        return response.data_id

def start_record(gateway_name="Pythoner", port="50051"):
    """"""
    with grpc.insecure_channel(f'localhost:{port}') as channel:
        stub = service_pb2_grpc.DataManagerStub(channel)
        stub.StartRecord(service_pb2.Empty())


def stop_record(gateway_name="Pythoner", port="50051"):
    """"""
    with grpc.insecure_channel(f'localhost:{port}') as channel:
        stub = service_pb2_grpc.DataManagerStub(channel)
        stub.StopRecord(service_pb2.Empty())


def add_record_symbol(
        gateway_name="Pythoner",
        port="50051",
        interface="",
        symbol="",
        is_day_record="",
        day_record_start_time="",
        day_record_end_time="",
        is_night_record="",
        night_record_start_time="",
        night_record_end_time="",
        storage=""
    ):
    with grpc.insecure_channel(f'localhost:{port}') as channel:
        stub = service_pb2_grpc.DataManagerStub(channel)
        stub.AddRecordSymbol(service_pb2.AddRecordSymbolRequest(symbol=symbol))


def get_streaming_record(gateway_name="Pythoner", port="50051"):
    """"""
    with grpc.insecure_channel(f'localhost:{port}') as channel:
        stub = service_pb2_grpc.DataManagerStub(channel)
        response = stub.GetRecordStreams(service_pb2.Empty())
        dicts = [MessageToDict(r, preserving_proto_field_name=True) for r in response.streams]
        return [stream["detail"].split(",") for stream in dicts]


def get_overview(gateway_name="Pythoner", port="50051"):
    """"""
    with grpc.insecure_channel(f'localhost:{port}') as channel:
        stub = service_pb2_grpc.DataManagerStub(channel)
        response = stub.GetOverview(service_pb2.GetOverviewRequest(data_id=""))
        dicts = [MessageToDict(r, preserving_proto_field_name=True) for r in response.results]
        return dicts


def save_config(gateway_name="Pythoner", port="50051", category="", name="", config=None):
    if config is None:
        config = {}

    with grpc.insecure_channel(f'localhost:{port}') as channel:
        stub = service_pb2_grpc.ConfigureManagerStub(channel)
        field_list = []
        for k, v in config.items():
            # 创建单个字段消息对象
            field_msg = service_pb2.ConfigFieldMsg(key=str(k), value=str(v))
            field_list.append(field_msg)

        response = stub.SaveConfig(
            service_pb2.SaveConfigListRequest(
                category=category,
                name=name,
                fields=field_list,
                field_count=len(field_list)
            )
        )
        return response.request_id


def load_config(gateway_name="Pythoner", port="50051", category="", name=""):
    with grpc.insecure_channel(f'localhost:{port}') as channel:
        stub = service_pb2_grpc.ConfigureManagerStub(channel)
        response = stub.LoadConfig(service_pb2.LoadConfigRequest(category=category, name=name))
        dicts = [MessageToDict(r, preserving_proto_field_name=True) for r in response.fields]
        return dicts


def run_code(code, gateway_name="Pythoner", port="50051"):
    with grpc.insecure_channel(f'localhost:{port}') as channel:
        stub = service_pb2_grpc.IpythonKernelManagerStub(channel)
        responses = stub.ExecuteCode(service_pb2.ExecuteRequest(code=code))
        for r in responses:
            if r.mime_type == "text/plain":
                yield {"mime_type": r.mime_type,
                       "msg_type": r.msg_type,
                       "text_output": r.text_output
                      }
            elif r.mime_type == "image/png":
                yield {"mime_type": r.mime_type,
                       "msg_type": r.msg_type,
                       "binary_data": r.data_content
                      }
            elif r.mime_type == "text/html":
                yield {"mime_type": r.mime_type,
                       "msg_type": r.msg_type,
                       "data_content": r.data_content
                      }


def ask_stream(msg, gateway_name="Pythoner", port="50051"):
    with grpc.insecure_channel(f'localhost:{port}') as channel:
        stub = service_pb2_grpc.LLMManagerStub(channel)
        responses = stub.AskStream(service_pb2.LLMRequest(msg=msg))
        for r in responses:
            yield r.msg


def extract_code(msg, gateway_name="Pythoner", port="50051"):
    with grpc.insecure_channel(f'localhost:{port}') as channel:
        stub = service_pb2_grpc.LLMManagerStub(channel)
        response = stub.ExtractCode(service_pb2.LLMRequest(msg=msg))
        return response.msg


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
                    data = json.loads(message.event_data)
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

