"""回测"""
import logging
from dataclasses import asdict, dataclass, field, fields
from datetime import datetime

import numpy as np
import polars as pl

from .core.constant import Direction, Exchange, Offset, OrderType, Status
from .core.datatype import OrderData, TradeData
from .datastream import DataStream
from .strategies import CtaStrategy

logger = logging.getLogger("Backtest")

@dataclass
class DailyResult:
    """"""
    date: datetime = datetime.now()
    close_price: float = 0.0
    pre_close: float = 0.0

    trades: list = field(default_factory=list)
    trade_count: int = 0

    start_pos: float = 0
    end_pos: float = 0

    turnover: float = 0
    commission: float = 0
    slippage: float = 0

    trading_pnl: float = 0
    holding_pnl: float = 0
    total_pnl: float = 0
    net_pnl: float = 0

    def add_trade(self, trade: TradeData) -> None:
        """"""
        self.trades.append(trade)

    def calculate_pnl(
        self,
        pre_close: float,
        start_pos: float,
        size: float,
        rate: float,
        slippage: float
    ) -> None:
        """"""
        # If no pre_close provided on the first day,
        # use value 1 to avoid zero division error
        if pre_close:
            self.pre_close = pre_close
        else:
            self.pre_close = 1

        # Holding pnl is the pnl from holding position at day start
        self.start_pos = start_pos
        self.end_pos = start_pos

        self.holding_pnl = self.start_pos * (self.close_price - self.pre_close) * size

        # Trading pnl is the pnl from new trade during the day
        self.trade_count = len(self.trades)

        for trade in self.trades:
            if trade.direction == Direction.LONG:
                pos_change = trade.volume
            else:
                pos_change = -trade.volume

            self.end_pos += pos_change

            turnover: float = trade.volume * size * trade.price
            self.trading_pnl += pos_change * \
                (self.close_price - trade.price) * size
            self.slippage += trade.volume * size * slippage

            self.turnover += turnover
            self.commission += turnover * rate

        # Net pnl takes account of commission and slippage cost
        self.total_pnl = self.trading_pnl + self.holding_pnl
        self.net_pnl = self.total_pnl - self.commission - self.slippage


@dataclass
class BacktestResult:
    # --- 时间信息 ---
    start_date: str = ""
    end_date: str = ""
    total_days: int = 0

    # --- 盈亏分布 ---
    profit_days: int = 0
    loss_days: int = 0
    total_net_pnl: float = 0.0
    daily_net_pnl: float = 0.0

    # --- 成本相关 ---
    total_commission: float = 0.0
    daily_commission: float = 0.0
    total_slippage: float = 0.0
    daily_slippage: float = 0.0
    total_turnover: float = 0.0
    daily_turnover: float = 0.0

    # --- 交易统计 ---
    total_trade_count: int = 0
    daily_trade_count: float = 0.0

    # --- 收益率与风险指标 ---
    end_balance: float = 0.0
    total_return: float = 0.0
    annual_return: float = 0.0
    daily_return: float = 0.0
    return_std: float = 0.0

    # --- 风险评价 ---
    max_drawdown: float = 0.0
    max_ddpercent: float = 0.0
    max_drawdown_duration: int = 0
    sharpe_ratio: float = 0.0
    ewm_sharpe: float = 0.0
    return_drawdown_ratio: float = 0.0  # 也叫卡玛比率 Calmar Ratio
    rgr_ratio: float = 0.0             # 回归增长比等

    def to_dict(self):
        """方便转换为字典，用于保存 JSON 或存库"""
        return asdict(self)


class StrategyContext:
    """"""
    def __init__(self):
        """"""
        self.account = 10000
        self.pos = 0
        self.cache = RollingWindow(100)
        self.orderid = 0
        self.limit_orders: dict = {}
        self.tradeid = 0
        self.trades: dict = {}
        self.daily_results: dict = {}
        self.result = {
            "return": 0,
            "sharp": 0,
            "drawdown": 0
        }

    def init(self):
        """"""
        pass

    def load_strategy(self, strategy):
        """"""
        self.strategy = strategy
        strategy.add_context(self)

    def on_bar(self, data):
        """"""
        self.strategy.on_bar(data)

    def send_order(
        self,
        direction: Direction,
        offset: Offset,
        price: float,
        volume: float
    ) -> list:
        """"""
        order = OrderData(
            symbol="btc-usdt",
            exchange=Exchange.GLOBAL,
            orderid=str(self._create_orderid()),
            datetime=datetime.now(),
            type=OrderType.LIMIT,
            direction=direction,
            offset=offset,
            price=price,
            volume=volume,
            gateway_name="okx"
        )

        self.limit_orders[order.ct_orderid] = order
        return order.ct_orderid

    def buy(self, price, volume):
        """"""
        self.send_order(
            direction=Direction.LONG,
            offset=Offset.OPEN,
            price=price,
            volume=volume
        )
        self.account -= price

    def sell(self, price, volume):
        """"""
        self.send_order(
            direction=Direction.SHORT,
            offset=Offset.CLOSE,
            price=price,
            volume=volume
        )
        self.account += price

    def cross_order(self, bar):
        """"""
        long_cross_price = bar.low_price
        short_cross_price = bar.high_price
        long_best_price = bar.open_price
        short_best_price = bar.open_price

        for order in list(self.limit_orders.values()):
            if order.status == Status.SUBMITTING:
                order.status = Status.NOTTRADED
                self.strategy.on_order(order)

            long_cross: bool = (
                order.direction == Direction.LONG
                and order.price >= long_cross_price
                and long_cross_price > 0
            )

            short_cross: bool = (
                order.direction == Direction.SHORT
                and order.price <= short_cross_price
                and short_cross_price > 0
            )

            if not long_cross and not short_cross:
                continue

            order.traded = order.volume
            order.status = Status.ALLTRADED
            self.strategy.on_order(order)

            if order.ct_orderid in self.limit_orders:
                self.limit_orders.pop(order.ct_orderid)

            if long_cross:
                trade_price = min(order.price, long_best_price)
                pos_change = order.volume
            else:
                trade_price = max(order.price, short_best_price)
                pos_change = -order.volume

            trade: TradeData = TradeData(
                symbol=order.symbol,
                exchange=order.exchange,
                orderid=order.orderid,
                tradeid=str(self._create_tradeid()),
                direction=order.direction,
                offset=order.offset,
                price=trade_price,
                volume=order.volume,
                datetime=bar.datetime,
                gateway_name=bar.gateway_name,
            )

            self.pos += pos_change
            self.strategy.on_trade(trade)

            self.trades[trade.ct_tradeid] = trade

    def create_daily_result(self, bar):
        """"""
        d = bar.datetime.date()

        daily_result: DailyResult | None = self.daily_results.get(d, None)
        if daily_result:
            daily_result.close_price = bar.close_price
        else:
            self.daily_results[d] = DailyResult(d, bar.close_price)

    def _create_orderid(self) -> int:
        """"""
        self.orderid += 1
        return self.orderid

    def _create_tradeid(self) -> int:
        """"""
        self.tradeid += 1
        return self.tradeid

    def update(self, price):
        """"""
        self.cache.add(price)


class BacktestEngine:
    """"""
    def __init__(self):
        """"""
        self.strategy_contexts: dict = {}
        self.backtest_results: dict = {}
        self.raw_data: pl.DataFrame = None
        self.db = None

    def init(self):
        """"""
        pass

    def add_strategy(self):
        """"""
        strategy = CtaStrategy()
        context = StrategyContext()
        context.load_strategy(strategy)

        self.strategy_contexts[id(context)] = context
        return id(context)

    def add_database(self, db):
        """"""
        self.db = db

    def load_data(self, symbol):
        """"""
        try:
            data = self.db.query_bardata(symbol)
        except Exception as e:
            raise e

        self.raw_data = data

    def list_contexts(self):
        """"""
        return list(self.strategy_contexts.keys())

    def list_backtest_results(self):
        """"""
        return list(self.backtest_results.values())

    def start(self, context_id):
        """"""
        context = self.strategy_contexts[context_id]
        self.run_backtest(context)

    def run_backtest(self, context):
        """"""
        self._run_simulation(context)
        df = self._calculate_daily_pnl(context)
        result = self._calculate_statistics(context, df)
        self.backtest_results[id(context)] = result.copy()

    def get_backtest_result(self, context_id):
        """"""
        if not context_id:
            return {}
        return self.backtest_results[context_id]

    def get_empty_result(self):
        """"""
        result = BacktestResult()
        return result.to_dict()

    def _run_simulation(self, context):
        """"""
        for bar in DataStream(self.raw_data):
            context.cross_order(bar)
            context.on_bar(bar.open_price)
            context.create_daily_result(bar)

    def _calculate_daily_pnl(self, context):
        """"""
        if not context.trades:
            return pl.DataFrame()

        for trade in context.trades.values():
            if not trade.datetime:
                continue

            d = trade.datetime.date()
            daily_result: DailyResult = context.daily_results[d]
            daily_result.add_trade(trade)

        pre_close: float = 0
        start_pos: float = 0

        for daily_result in context.daily_results.values():
            daily_result.calculate_pnl(
                pre_close,
                start_pos,
                # self.size,
                # self.rate,
                # self.slippage
                1, 0, 0
            )

            pre_close = daily_result.close_price
            start_pos = daily_result.end_pos

        colnames = [f.name for f in fields(DailyResult)]
        data = {
            name: [getattr(obj, name) for obj in context.daily_results.values()]
            for name in colnames
        }

        return pl.DataFrame(data, strict=False)

    def _calculate_statistics(self, context, df):
        """"""
        self.annual_days = 255
        self.risk_free = 0.02
        self.half_life = 20
        self.capital = 100000

        result = BacktestResult()
        result.capital = self.capital

        if df.is_empty():
            return result.to_dict()

        df = df.drop("trades")
        df.write_parquet("~/data.parquet")

        # 计算是否出现资产低于0
        df = df.lazy()
        df = df.with_columns((pl.col("net_pnl").cum_sum() + self.capital).alias("balance"))
        df = df.with_columns([
            pl.when(
                (pl.col("balance") / pl.col("balance").shift(1).fill_null(self.capital)) > 0
            )
            .then(
                (pl.col("balance") / pl.col("balance").shift(1).fill_null(self.capital)).log()
            )
            .otherwise(0.0)
            .fill_null(0.0)
            .alias("return")
        ])
        df = df.collect()
        is_all_positive = df.select((pl.col("balance") > 0).all()).item()

        if not is_all_positive:
            return result.to_dict()

        # 计算统计指标
        df = df.with_columns(
            pl.col("balance").cum_max().alias("highlevel")
        ).with_columns(
            (pl.col("balance") - pl.col("highlevel")).alias("drawdown")
        ).with_columns(
            (pl.col("drawdown") / pl.col("highlevel")).alias("ddpercent")
        )


        result.start_date = df["date"][0].strftime("%Y-%m-%d")
        result.end_date = df["date"][-1].strftime("%Y-%m-%d")
        result.total_days = df.select(
            pl.len()
        ).item()
        result.profit_days = df.select(
            (pl.col("net_pnl") > 0).sum()
        ).item()
        result.loss_days = df.select(
            (pl.col("net_pnl") < 0).sum()
        ).item()
        result.end_balance = df["balance"][-1]
        result.max_drawdown = df.select(
            pl.col("drawdown").min()
        ).item()
        result.max_ddpercent = df.select(
            pl.col("ddpercent").min()
        ).item()
        result.max_ddpercent = df.select(
            pl.col("ddpercent").min()
        ).item()

        max_drawdown_end_idx = df.select(pl.col("drawdown").arg_min()).item()
        if max_drawdown_end_idx is not None:
            max_drawdown_end = df["date"][max_drawdown_end_idx]

            max_drawdown_start_idx = df["balance"][:max_drawdown_end_idx + 1].arg_max()
            max_drawdown_start = df["date"][max_drawdown_start_idx]

            delta = max_drawdown_end - max_drawdown_start
            result.max_drawdown_duration = delta.days
        else:
            result.max_drawdown_duration = 0

        result.total_net_pnl = df.select(
            pl.col("net_pnl").sum()
        ).item()
        result.daily_net_pnl = df.select(
            pl.col("net_pnl").mean()
        ).item()
        result.total_commission = df.select(
            pl.col("commission").sum()
        ).item()
        result.daily_commission = df.select(
            pl.col("commission").mean()
        ).item()
        result.total_slippage = df.select(
            pl.col("slippage").sum()
        ).item()
        result.daily_slippage = df.select(
            pl.col("slippage").mean()
        ).item()
        result.total_turnover = df.select(
            pl.col("turnover").sum()
        ).item()
        result.daily_turnover = df.select(
            pl.col("turnover").mean()
        ).item()
        result.total_trade_count = df.select(
            pl.col("trade_count").sum()
        ).item()
        result.daily_trade_count = df.select(
            pl.col("trade_count").mean()
        ).item()
        result.total_return = (df["balance"][-1] / self.capital -1)
        result.annual_return = result.total_return * self.annual_days / result.total_days
        result.daily_return = df.select(
            pl.col("return").mean()
        ).item()
        result.return_std = df.select(
            pl.col("return").std()
        ).item()

        daily_risk_free: float = self.risk_free / np.sqrt(self.annual_days)
        result.sharpe_ratio = (result.daily_return - daily_risk_free) / result.return_std /\
            np.sqrt(self.annual_days)

        df = df.with_columns([
            (pl.col("return").ewm_mean(half_life=self.half_life, adjust=True) * 100)
            .alias("ewm_mean"),
            (pl.col("return").ewm_std(half_life=self.half_life, adjust=True) * 100)
            .alias("ewm_std")
        ]).with_columns(
            ((pl.col("ewm_mean") - daily_risk_free) / pl.col("ewm_std") /\
             pl.lit(self.annual_days).sqrt()).alias("ewm_sharpe")
        )

        result.ewm_sharpe = df["ewm_sharpe"][-1]

        return result.to_dict()

    def _has_negative_equity(self, df):
        """"""
        self.capital = 100000
        df = df.drop("trades")
        df = df.lazy()
        df = df.with_columns((pl.col("net_pnl").cum_sum() + self.capital).alias("balance"))
        df = df.with_columns([
            pl.when(pl.col("balance") > 0)
            .then((pl.col("balance") / pl.col("balance").shift(1).fill_null(self.capital)).log())
            .otherwise(0)
            .alias("return")
        ])
        df = df.with_columns(pl.col("balance").cum_max().alias("highlevel"))
        df = df.with_columns([
            (pl.col("balance") - pl.col("highlevel")).alias("drawdown"),
            ((pl.col("balance") - pl.col("highlevel")) / pl.col("highlevel") * 100)
            .alias("ddpercent")
        ])
        df = df.collect()

        is_all_positive = df.select((pl.col("balance") > 0).all()).item()

        return is_all_positive


class RollingWindow:
    """Double Buffer"""
    def __init__(self, size, dtype=np.float64):
        """"""
        self.size = size
        self.buffer = np.zeros(2 * size, dtype=dtype)
        self.cursor = 0
        self.is_full = False

    def add(self, value):
        """"""
        self.buffer[self.cursor] = value
        self.buffer[self.cursor + self.size] = value

        # 2. 更新指针
        self.cursor += 1
        if self.cursor >= self.size:
            self.is_full = True
            self.cursor = 0

    def get_window(self):
        """"""
        if not self.is_full and self.cursor > 0:
            return self.buffer[:self.cursor]

        return self.buffer[self.cursor : self.cursor + self.size]

    def get_stats(self):
        window = self.get_window()
        return {
            "mean": np.mean(window),
            "std": np.std(window),
            "sum": np.sum(window)
        }

    def mean(self, window: int = 0):
        """The  property."""
        window = self.get_window()[-window:]
        return np.mean(window)
