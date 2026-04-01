""""""
from threading import Lock

from ..base.gateway import BaseGateway
from ..database.sqlite_database import SqliteBoxDatabase
from .event import Event, EventEngine, EventType, Handler


class MainEngine:
    """Main engine"""
    _instance = None
    _lock = Lock()

    _event_engine = None
    _aux_event_engine = None
    _gms_engine = None
    _oms_engine = None
    _ems_engine = None
    _cms_engine = None

    def __init__(self) -> None:
        """"""
        pass

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
        gateway.connect({})
        self._gateways[gateway.gateway_id] = gateway
        return gateway.gateway_id

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


class CmsEngine:
    """
    Configure Management System Engine
    """
    def __init__(self, main_controller, engine_name: str = "cms") -> None:
        """"""
        self.main = main_controller
        self.configs: dict[str, dict] = {}
        self.config_database = SqliteBoxDatabase()

    def save_config(self, category, name, config: dict) -> None:
        """"""
        for key, value in config.items():
            self.config_database.save(category, name, key, value)

    def load_config(self, category, name) -> dict:
        """"""
        config = self.config_database.load(category, name)
        return config

