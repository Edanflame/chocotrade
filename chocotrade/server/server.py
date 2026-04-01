import logging
from concurrent import futures
from queue import Empty, Queue

import grpc
from google.protobuf.json_format import ParseDict

from ..backtest import BacktestEngine
from ..config import settings
from ..core.engine import MainEngine
from ..core.event import Event
from ..database.duckdb_database import DuckBarsDatabase
from ..datasource.tushare_datasource import TushareDataSource
from ..protos_generated import service_pb2, service_pb2_grpc
from ..utilities import safe_import_module

# 配置日志，写入到 debug.log 文件
logging.basicConfig(
    level=logging.INFO,
    filename=str(settings.base_dir / "debug_serve.log"),
    filemode="w", # 每次启动重新创建文件
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("Backend")


main_engine = MainEngine()
backtest_engine = BacktestEngine()


class GreeterServicer(service_pb2_grpc.GreeterServicer):
    def SayHello(self, request, context):
        # 假设你在这里调用了你的 C++ 模块
        # from . import my_module1
        # result = my_module1.add(1, 2)
        return service_pb2.HelloReply(message=f"后端收到: {request.name}")


class BacktesterServicer(service_pb2_grpc.BacktesterServicer):
    """"""
    def __init__(self, backtest_engine=backtest_engine):
        """"""
        super().__init__()
        self.backtest_engine = backtest_engine
        self.backtest_engine.init()

    def StartBacktest(self, request, context):
        """"""
        context_id = self.backtest_engine.add_strategy()
        self.backtest_engine.load_data()

        self.backtest_engine.start(context_id)
        result = self.backtest_engine.get_backtest_result(context_id)
        return service_pb2.BacktestResultReply(**result)

    def GetAllBacktestResults(self, request, context):
        """"""
        backtest_results = self.backtest_engine.list_backtest_results()

        data = {
            "results": backtest_results,
            "total_count": len(backtest_results)
        }

        reply = service_pb2.BacktestListReply()
        ParseDict(data, reply)
        return reply

    def GetTargetBacktestResult(self, request, context):
        """"""
        tmp = self.backtest_engine.list_contexts()
        if len(tmp) == 0:
            result = {}
        else:
            context_id = self.backtest_engine.list_contexts()[0]
            result = self.backtest_engine.get_backtest_result(context_id)
        return service_pb2.BacktestResultReply(**result)

    def StartTest(self, request, context):
        from ..backtest import run_test
        result = run_test()
        return service_pb2.BacktestResultReply(**result)


class GatewayManagerServicer(service_pb2_grpc.GatewayManagerServicer):
    """"""
    def __init__(self, engine=main_engine):
        """"""
        super().__init__()
        self._engine = engine
        self._gateway_id = ""

    def AddGateway(self, request, context):
        """"""
        gateway_name = "okex_gateway"
        my_module = safe_import_module(gateway_name)
        self._gateway_id = self._engine.add_gateway(my_module.OkexGateway, gateway_name)
        # return service_pb2.GatewayReply(message=f"成功加载模块{gateway_name}")
        return service_pb2.GatewayReply(message=self._gateway_id)

    def SendOrder(self, request, context):
        """"""
        gateway_id = self._gateway_id
        req = ""
        self._engine.send_order(gateway_id, req)
        return service_pb2.SendOrderReply(order_id="")


class DataManagerServicer(service_pb2_grpc.DataManagerServicer):
    """"""
    def __init__(self):
        """"""
        super().__init__()

    def add_database(self):
        """"""
        pass

    def add_datasource(self):
        """"""
        pass

    def FetchData(self, symbol):
        """"""
        data = TushareDataSource().test(symbol)
        return data

    def SaveData(self, data):
        """"""
        if data is None:
            return

        database = DuckBarsDatabase()
        database.update_bardata(data)

    def SyncData(self, request, context):
        """"""
        data = self.FetchData(request.symbol)
        self.SaveData(data)
        return service_pb2.SyncDataReply(data_id="")

    def GetOverview(self, request, context):
        """"""
        database = DuckBarsDatabase()
        overview = database.query_bar_overview_dict()
        data = {
            "results": overview,
            "total_count": len(overview)
        }
        reply = service_pb2.GetOverviewListReply()
        ParseDict(data, reply)
        return reply


class DatafeedManager:
    """"""
    def __init__(self):
        """"""
        pass

    def add_datafeed(self):
        """"""
        pass


class ConfigureManagerServicer(service_pb2_grpc.ConfigureManagerServicer):
    """"""
    def __init__(self, engine=main_engine):
        super().__init__()
        self._engine = engine

    def SaveConfig(self, request, context) -> None:
        """"""
        category = request.category
        name = request.name

        config_dict = {}
        for field in request.fields:
            config_dict[field.key] = field.value

        self._engine.save_config(
            category, name, config_dict
        )

        return service_pb2.SaveConfigReply(request_id="")

    def LoadConfig(self, request, context) -> dict:
        """"""
        config_dict = self._engine.load_config(
            request.category, request.name
        )
        field_list = []
        for k, v in config_dict.items():
            # 创建单个字段消息对象
            field_msg = service_pb2.ConfigFieldMsg(key=str(k), value=str(v))
            field_list.append(field_msg)

        return service_pb2.LoadConfigReply(
            fields=field_list,
            field_count=len(field_list)
        )


class EventEngineServicer(service_pb2_grpc.EventEngineServicer):
    """gRPC 接口层"""
    def __init__(self, engine=main_engine):
        """"""
        self._engine = engine

    def SubscribeEvents(self, request, context):
        """"""
        # 1. 确实是私有队列，放在函数内部
        _queue = Queue()

        # 2. 定义一个桥接函数（把 Engine 的数据推入当前 Queue）
        # 这个函数会被 Engine 线程调用
        def bridge_callback(e: Event):
            try:
                event = service_pb2.EventReply(
                    name=e.event_type.value,
                    data=str(e.event_data))
                # 跨线程安全地推入队列
                _queue.put(event)
            except Exception as e:
                logger.info(e)

        # 3. 将这个桥接函数注册到 Engine
        self._engine.register_client(bridge_callback)
        logger.info("新连接：已注册监听回调")

        try:
            while True:
                # 只有当前客户端会从这个 queue 里拿数据
                if not context.is_active():
                    break

                try:
                    # 从队列获取数据，设置 timeout 允许循环检查 context.is_active()
                    # 这是为了防止在没有数据时，程序一直卡在 get() 无法响应关闭信号
                    event = _queue.get(timeout=1.0)
                    yield event  # 普通的 yield，返回给客户端
                except Empty:
                    # 只是 1 秒内没数据，继续循环
                    continue
        except Exception as e:
            logger.info(f"流处理发生错误: {e}")
        finally:
            # 4. 断开连接时，务必移除回调
            self._engine.unregister_client(bridge_callback)
            logger.info("连接断开：已移除监听回调")


def get_server(port="50051"):
    """"""
    main_engine.start()

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    service_pb2_grpc.add_GreeterServicer_to_server(GreeterServicer(), server)
    service_pb2_grpc.add_BacktesterServicer_to_server(BacktesterServicer(), server)
    service_pb2_grpc.add_GatewayManagerServicer_to_server(GatewayManagerServicer(), server)
    service_pb2_grpc.add_DataManagerServicer_to_server(DataManagerServicer(), server)
    service_pb2_grpc.add_ConfigureManagerServicer_to_server(ConfigureManagerServicer(), server)
    service_pb2_grpc.add_EventEngineServicer_to_server(EventEngineServicer(), server)
    server.add_insecure_port(f'[::]:{port}')
    return server


def stop_engine():
    """"""
    main_engine.stop()

