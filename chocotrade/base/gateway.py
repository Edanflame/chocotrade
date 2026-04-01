"""
交易网关
"""

from abc import ABC, abstractmethod
from typing import Any

from ..core.constant import Exchange
from ..core.datatype import (
    AccountData,
    BarData,
    CancelRequest,
    ContractData,
    HistoryRequest,
    LogData,
    OrderData,
    OrderRequest,
    PositionData,
    SubscribeRequest,
    TickData,
    TradeData,
)
from ..core.event import Event, EventEngine, EventType


class BaseGateway(ABC):
    """"""
    default_name: str = ""
    default_setting: dict[str, Any] = {}
    exchanges: list[Exchange] = []

    def __init__(self, event_engine: EventEngine, gateway_name: str) -> None:
        """"""
        self.event_engine = event_engine
        self.gateway_name = gateway_name
        self.gateway_id = str(id(self))

    def on_event(self, event_type: str, data: Any = None) -> None:
        """"""
        event: Event = Event(event_type, data)
        self.event_engine.put(event)

    def on_tick(self, tick: TickData) -> None:
        """"""
        self.on_event(EventType.EVENT_TICK, tick)

    def on_bar(self, bar: BarData) -> None:
        """"""
        self.on_event(EventType.EVENT_BAR, bar)

    def on_account(self, account: AccountData) -> None:
        """"""
        self.on_event(EventType.EVENT_ACCOUNT, account)

    def on_position(self, position: PositionData) -> None:
        """"""
        self.on_event(EventType.EVENT_POSITION, position)

    def on_contract(self, contract: ContractData) -> None:
        """"""
        self.on_event(EventType.EVENT_CONTRACT, contract)

    def on_order(self, order: OrderData) -> None:
        """"""
        self.on_event(EventType.EVENT_ORDER, order)

    def on_trade(self, trade: TradeData) -> None:
        """"""
        self.on_event(EventType.EVENT_TRADE, trade)

    def on_log(self, log: LogData) -> None:
        """"""
        self.on_event(EventType.EVENT_LOG, log)

    def write_log(self, msg: str) -> None:
        """"""
        log: LogData = LogData(msg=msg, gateway_name=self.gateway_name)
        self.on_log(log)

    def get_default_setting(self) -> dict[str, Any]:
        """"""
        return self.default_setting

    def start_timer(self, interval: int) -> None:
        """"""
        self._interval = interval
        self.event_engine.register_handle(EventType.EVENT_TIMER, self.process_timer_event)

    def process_timer_event(self, event) -> None:
        """"""
        if event.event_data % self._interval == 0:
            self.on_schedule_triggered()

    def on_schedule_triggered(self):    # noqa: B027
        """"""
        pass

    @abstractmethod
    def connect(self, setting: dict) -> None:
        """"""
        pass

    @abstractmethod
    def close(self) -> None:
        """"""
        pass

    @abstractmethod
    def subscribe(self, req: SubscribeRequest) -> None:
        """"""
        pass

    @abstractmethod
    def query_account(self) -> None:
        """"""
        pass

    @abstractmethod
    def query_position(self) -> None:
        """"""
        pass

    def query_history(self, req: HistoryRequest) -> list[BarData]:  # noqa: B027
        """"""
        pass

    @abstractmethod
    def send_order(self, req: OrderRequest) -> str:
        """"""
        pass

    @abstractmethod
    def cancel_order(self, req: CancelRequest) -> None:
        """"""
        pass
