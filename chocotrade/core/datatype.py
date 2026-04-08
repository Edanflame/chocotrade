"""
数据类型
"""
from dataclasses import dataclass, field
from datetime import datetime
from logging import INFO

from .constant import Direction, Exchange, Interval, Offset, OptionType, OrderType, Product, Status


@dataclass(slots=True)
class BaseData:
    """
    数据类型基类
    """

    gateway_name: str

    extra: dict = field(init=False, default_factory=dict)


# 行情相关
@dataclass(slots=True)
class TickData(BaseData):
    """
    tick数据类型
    """

    symbol: str
    exchange: Exchange
    timestamp: datetime

    name: str = ""
    volume: float = 0
    turnover: float = 0
    open_interest: float = 0
    last_price: float = 0
    last_volume: float = 0
    limit_up: float = 0
    limit_down: float = 0

    open_price: float = 0
    high_price: float = 0
    low_price: float = 0
    pre_close: float = 0

    bid_price_1: float = 0
    bid_price_2: float = 0
    bid_price_3: float = 0
    bid_price_4: float = 0
    bid_price_5: float = 0

    ask_price_1: float = 0
    ask_price_2: float = 0
    ask_price_3: float = 0
    ask_price_4: float = 0
    ask_price_5: float = 0

    bid_volume_1: float = 0
    bid_volume_2: float = 0
    bid_volume_3: float = 0
    bid_volume_4: float = 0
    bid_volume_5: float = 0

    ask_volume_1: float = 0
    ask_volume_2: float = 0
    ask_volume_3: float = 0
    ask_volume_4: float = 0
    ask_volume_5: float = 0

    ct_symbol: str = ""

    def __post_init__(self) -> None:
        """"""
        self.ct_symbol: str = f"{self.symbol}.{self.exchange.value}"

    def to_dict(self):
        """"""
        return {
            "symbol": self.symbol,
            "exchange": self.exchange.value,
            "timestamp": self.timestamp.strftime("%d/%m/%Y, %H:%M:%S"),
            "name": self.name,
            "volume": self.volume,
            "turnover": self.turnover,
            "open_interest": self.open_interest,
            "last_price": self.last_price,
            "last_volume": self.last_volume,
            "limit_up": self.limit_up,
            "limit_down": self.limit_down,
            "open_price": self.open_price,
            "high_price": self.high_price,
            "low_price": self.low_price,
            "pre_close": self.pre_close,
            "bid_price_1": self.bid_price_1,
            "bid_price_2": self.bid_price_2,
            "bid_price_3": self.bid_price_3,
            "bid_price_4": self.bid_price_4,
            "bid_price_5": self.bid_price_5,
            "ask_price_1": self.ask_price_1,
            "ask_price_2": self.ask_price_2,
            "ask_price_3": self.ask_price_3,
            "ask_price_4": self.ask_price_4,
            "ask_price_5": self.ask_price_5,
            "bid_volume_1": self.bid_volume_1,
            "bid_volume_2": self.bid_volume_2,
            "bid_volume_3": self.bid_volume_3,
            "bid_volume_4": self.bid_volume_4,
            "bid_volume_5": self.bid_volume_5,
            "ask_volume_1": self.ask_volume_1,
            "ask_volume_2": self.ask_volume_2,
            "ask_volume_3": self.ask_volume_3,
            "ask_volume_4": self.ask_volume_4,
            "ask_volume_5": self.ask_volume_5,
            "ct_symbol": self.ct_symbol,
            "gateway_name": self.gateway_name
        }


@dataclass(slots=True)
class BarData(BaseData):
    """
    bar数据类型
    """

    symbol: str
    exchange: Exchange
    interval: Interval
    datetime: datetime

    volume: float = 0
    turnover: float = 0
    open_interest: float = 0
    open_price: float = 0
    high_price: float = 0
    low_price: float = 0
    close_price: float = 0

    ct_symbol: str = ""

    def __post_init__(self) -> None:
        """"""
        self.ct_symbol: str = f"{self.symbol}.{self.exchange.value}"


@dataclass(slots=True)
class NewsData(BaseData):
    """
    news数据类型
    """

    headline: str
    content: str
    datetime: datetime


# 查询相关
@dataclass(slots=True)
class AccountData(BaseData):
    """"""
    accountid: str

    balance: float = 0
    frozen: float = 0
    available: float = 0
    ct_accountid: str = ""

    def __post_init__(self) -> None:
        """"""
        self.available: float = self.balance - self.frozen
        self.ct_accountid: str = f"{self.gateway_name}.{self.accountid}"


@dataclass(slots=True)
class PositionData(BaseData):
    """"""

    symbol: str
    exchange: Exchange
    direction: Direction

    volume: float = 0
    frozen: float = 0
    price: float = 0
    pnl: float = 0
    yd_volume: float = 0

    ct_symbol: str = ""
    ct_positionid: str = ""

    def __post_init__(self) -> None:
        """"""
        self.ct_symbol: str = f"{self.symbol}.{self.exchange.value}"
        self.ct_positionid: str = f"{self.vt_symbol}.{self.direction.value}"


@dataclass(slots=True)
class ContractData(BaseData):
    """"""

    symbol: str
    exchange: Exchange
    name: str
    product: Product
    size: float
    pricetick: float

    min_volume: float = 1           # minimum trading volume of the contract
    stop_supported: bool = False    # whether server supports stop order
    net_position: bool = False      # whether gateway uses net position volume
    history_data: bool = False      # whether gateway provides bar history data

    option_strike: float = 0
    option_underlying: str = ""     # vt_symbol of underlying contract
    option_type: OptionType = None
    option_listed: datetime = None
    option_expiry: datetime = None
    option_portfolio: str = ""
    option_index: str = ""          # for identifying options with same strike price

    ct_symbol: str = ""

    def __post_init__(self) -> None:
        """"""
        self.ct_symbol: str = f"{self.symbol}.{self.exchange.value}"


# 交易相关
@dataclass(slots=True)
class OrderData(BaseData):
    """"""

    symbol: str
    exchange: Exchange
    orderid: str
    datetime: datetime

    type: OrderType = OrderType.LIMIT
    direction: Direction = None
    offset: Offset = Offset.NONE
    price: float = 0
    volume: float = 0
    traded: float = 0
    status: Status = Status.SUBMITTING
    reference: str = ""

    ct_symbol: str = ""
    ct_orderid: str = ""

    def __post_init__(self) -> None:
        """"""
        self.ct_symbol: str = f"{self.symbol}.{self.exchange.value}"
        self.ct_orderid: str = f"{self.gateway_name}.{self.orderid}"

    def is_active(self) -> bool:
        """"""
        return self.status in set([Status.SUBMITTING, Status.NOTTRADED, Status.PARTTRADED])

    def create_cancel_request(self) -> "CancelRequest":
        """"""
        req: CancelRequest = CancelRequest(
            orderid=self.orderid, symbol=self.symbol, exchange=self.exchange
        )
        return req


@dataclass(slots=True)
class TradeData(BaseData):
    """"""

    symbol: str
    exchange: Exchange
    orderid: str
    tradeid: str
    datetime: datetime

    direction: Direction = None
    offset: Offset = Offset.NONE
    price: float = 0
    volume: float = 0

    ct_symbol: str = ""
    ct_orderid: str = ""
    ct_tradeid: str = ""

    def __post_init__(self) -> None:
        """"""
        self.ct_symbol: str = f"{self.symbol}.{self.exchange.value}"
        self.ct_orderid: str = f"{self.gateway_name}.{self.orderid}"
        self.ct_tradeid: str = f"{self.gateway_name}.{self.tradeid}"


@dataclass(slots=True)
class SubscribeRequest:
    """"""

    symbol: str
    exchange: Exchange

    ct_symbol: str = ""

    def __post_init__(self) -> None:
        """"""
        self.ct_symbol: str = f"{self.symbol}.{self.exchange.value}"


@dataclass(slots=True)
class HistoryRequest:
    """"""

    symbol: str
    exchange: Exchange
    start: datetime
    end: datetime = None
    interval: Interval = None

    ct_symbol: str = ""

    def __post_init__(self) -> None:
        """"""
        self.ct_symbol: str = f"{self.symbol}.{self.exchange.value}"


@dataclass(slots=True)
class OrderRequest:
    """"""

    symbol: str
    exchange: Exchange
    direction: Direction
    type: OrderType
    volume: float
    price: float = 0
    offset: Offset = Offset.NONE
    reference: str = ""

    ct_symbol: str = ""

    def __post_init__(self) -> None:
        """"""
        self.ct_symbol: str = f"{self.symbol}.{self.exchange.value}"

    def create_order_data(self, orderid: str, gateway_name: str) -> OrderData:
        """"""
        order: OrderData = OrderData(
            symbol=self.symbol,
            exchange=self.exchange,
            orderid=orderid,
            type=self.type,
            direction=self.direction,
            offset=self.offset,
            price=self.price,
            volume=self.volume,
            reference=self.reference,
            datetime=None,
            gateway_name=gateway_name,
        )
        return order


@dataclass(slots=True)
class CancelRequest:
    """"""

    orderid: str
    symbol: str
    exchange: Exchange

    ct_symbol: str = ""

    def __post_init__(self) -> None:
        """"""
        self.ct_symbol: str = f"{self.symbol}.{self.exchange.value}"


# 其他
@dataclass(slots=True)
class LogData(BaseData):
    """"""

    msg: str
    level: int = INFO

    time: datetime = None

    def __post_init__(self) -> None:
        """"""
        self.time: datetime = datetime.now()


# 函数
def create_tickdata(
    symbol: str,
    exchange: str,
    datetime: datetime,
    gateway_name: str
) -> TickData:
    """创建单一tick数据"""
    tick: TickData = TickData(
        symbol=symbol,
        exchange=exchange,
        datetime=datetime,
        gateway_name=gateway_name,
    )
    return tick


def create_bardata(
    symbol: str,
    exchange: str,
    interval: str,
    datetime: datetime,
    gateway_name: str
) -> BarData:
    """创建单一bar数据"""
    bar: BarData = BarData(
        symbol=symbol,
        exchange=exchange,
        interval=interval,
        datetime=datetime,
        gateway_name=gateway_name,
    )
    return bar


def create_newsdata(
    headline: str,
    content: str,
    datetime: datetime,
    gateway_name: str
) -> NewsData:
    """创建单一news数据"""
    news: NewsData = NewsData(
        headline=headline,
        content=content,
        datetime=datetime,
        gateway_name=gateway_name,
    )
    return news
