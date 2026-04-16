""""""
from threading import Lock

from ..backtest import BacktestEngine
from ..base.gateway import BaseGateway
from ..data_record.data_record import RecorderEngine
from ..database.duckdb_database import DuckBarsDatabase
from .datatype import Exchange, SubscribeRequest
from .event import Event, EventEngine, EventType, Handler
from .plugin_manager import PluginManager


class MainEngine:
    """Main engine"""
    _instance = None
    _lock = Lock()

    _event_engine = None
    _aux_event_engine = None
    _gms_engine = None
    _oms_engine = None
    _ems_engine = None
    _dms_engine = None
    _cms_engine = None

    def __init__(self) -> None:
        """"""
        self.plugin_manager = PluginManager()
        self.backtest_engine = BacktestEngine()
        self.database = DuckBarsDatabase()

    def __new__(cls):
        """Singleton Pattern"""
        with cls._lock:
            if cls._instance is None:
                instance = super().__new__(cls)
                instance._event_engine = EventEngine()
                instance._aux_event_engine = EventEngine()
                instance._gms_engine = GmsEngine(main_controller=instance)
                instance._oms_engine = OmsEngine(main_controller=instance)
                instance._ems_engine = EmsEngine(main_controller=instance)
                instance._dms_engine = DmsEngine(main_controller=instance)
                instance._cms_engine = CmsEngine(main_controller=instance)

                cls._instance = instance
        return cls._instance

    def init(self) -> None:
        """"""
        self._event_engine.start()
        self._aux_event_engine.start()  # Auxiliary Event Engine

    def start(self) -> None:
        """"""
        self.init()

    def add_gateway(
        self,
        gateway_class: BaseGateway,
        gateway_name: str = ""
    ) -> BaseGateway:
        """添加交易网关"""
        gateway = self._gms_engine.add_gateway(gateway_class, gateway_name)
        self._oms_engine.add_gateway(gateway)
        self._ems_engine.add_gateway(gateway)
        return gateway

    def get_gateway(self):
        """"""
        return self._gms_engine.get_gateway()

    def subscribe(
        self,
        gateway_id,
        symbol
    ) -> None:
        """"""
        self._gms_engine.subscribe(gateway_id, symbol)

    def get_database(self):
        """"""
        return self.database

    def add_plugin(self, plugin_name, plugin):
        """"""
        self._cms_engine.add_plugin(plugin_name, plugin)

    def save_config(self, category, name, config: dict) -> None:
        """"""
        self._cms_engine.save_config(
            category, name, config
        )

    def load_config(self, category, name) -> dict:
        """"""
        return self._cms_engine.load_config(
            category, name
        )

    def send_order(
        self,
        gateway_id: str,
        req
    ) -> str:
        """"""
        return self._gms_engine.send_order(gateway_id, req)

    def register_handle(self, event_type: str, handler: Handler) -> None:
        """"""
        self._event_engine.register_handle(event_type, handler)

    def unregister_handle(self, event_type: str, handler: Handler) -> None:
        """"""
        self._event_engine.unregister_handle(event_type, handler)

    def register_client(self, handler: Handler):
        """"""
        self.register_handle(EventType.EVENT_ALL, handler)

    def unregister_client(self, handler: Handler):
        """"""
        self.unregister_handle(EventType.EVENT_ALL, handler)

    def add_event(self, event: Event) -> None:
        """"""
        self._event_engine.put(event)

    def stop(self) -> None:
        """"""
        self._ems_engine.stop()
        self._oms_engine.stop()
        self._event_engine.stop()
        self._aux_event_engine.stop()


class GmsEngine:
    """
    Gateway Manager System Engine
    """
    def __init__(self, main_controller, engine_name: str = "gms") -> None:
        """"""
        self.main = main_controller
        self._gateways: dict[str, BaseGateway] = {}

    def add_gateway(
        self,
        gateway_class: BaseGateway,
        gateway_name: str = ""
    ) -> str:
        """添加交易网关"""
        gateway = gateway_class(self.main._event_engine, gateway_name)
        self._gateways[gateway.gateway_id] = gateway
        return gateway.gateway_id

    def get_gateway(self):
        """"""
        for key, _ in self._gateways.items():
            return key

    def subscribe(
        self,
        gateway_id,
        symbol
    ) -> None:
        """"""
        gateway: BaseGateway | None = self._gateways.get(gateway_id, None)
        if gateway:
            gateway.connect({})
            sub_request = SubscribeRequest(
                symbol=symbol,
                exchange=Exchange.GLOBAL
            )
            return gateway.subscribe(sub_request)
        else:
            return ""

    def send_order(
        self,
        gateway_id: str,
        req
    ) -> str:
        """委托下单"""
        gateway: BaseGateway | None = self._gateways.get(gateway_id, None)
        if gateway:
            return gateway.send_order(req)
        else:
            return ""


class OmsEngine:
    """
    Order Management System Engine
    """
    def __init__(self, main_controller, engine_name: str = "oms") -> None:
        """"""
        self.main = main_controller
        self.gateways: dict[str, str] = {}

    def add_gateway(self, gateway: str) -> None:
        """添加交易网关"""
        self.gateways[gateway] = gateway

    def stop(self):
        """"""
        pass


class EmsEngine:
    """
    Execution Management System Engine
    """
    def __init__(self, main_controller, engine_name: str = "ems") -> None:
        """"""
        self.main = main_controller
        self.gateways: dict[str, str] = {}

    def add_gateway(self, gateway: str) -> None:
        """添加交易网关"""
        self.gateways[gateway] = gateway

    def stop(self):
        """"""
        pass


class DmsEngine:
    """
    Data Management System Engine
    """
    def __init__(self, main_controller, engine_name: str = "dms") -> None:
        """"""
        self.main = main_controller
        self.recorder = RecorderEngine(self.main)

    def start_record(self):
        """"""
        self.recorder.start()

    def stop_record(self):
        """"""
        self.recorder.stop()

    def add_record_symbol(self, symbol):
        """"""
        gateway_id = self.main.get_gateway()
        self.main.subscribe(gateway_id, symbol)
        self.recorder.add_record_symbol(symbol)

    def get_record_streams(self):
        """"""
        return self.recorder.get_record_streams()


class CmsEngine:
    """
    Configure Management System Engine
    """
    def __init__(self, main_controller, engine_name: str = "cms") -> None:
        """"""
        self.main = main_controller
        self.configs: dict[str, dict] = {}

    def save_config(self, category, name, config: dict) -> None:
        """"""
        self.main.plugin_manager.save_config(name, config)

    def load_config(self, category, name) -> dict:
        """"""
        return self.main.plugin_manager.load_config(name)
