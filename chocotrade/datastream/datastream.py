""""""
import polars as pl

from ..core.constant import Exchange, Interval
from ..core.datatype import BarData


class DataStream:
    """"""
    def __init__(self, df: pl.DataFrame):
        # 1. 提取 NumPy 视图 (零拷贝)
        self.dt_view = df["timestamp"].to_list()
        self.o_view = df["open"].to_numpy()
        self.h_view = df["high"].to_numpy()
        self.l_view = df["low"].to_numpy()
        self.c_view = df["close"].to_numpy()
        self.v_view = df["volume"].to_numpy()
        # self.t_view = df["turnover"].to_numpy()
        # self.oi_view = df["open_interest"].to_numpy()

        self.length = len(df)
        self._cursor = 0

        # 2. 预初始化唯一的 BarData 对象 (只创建一次)
        # 假设这些是不变的基础信息，从第一行提取或由构造函数传入
        self._bar = BarData(
            symbol=df["symbol"][0],
            # exchange=df["exchange"][0],
            exchange=Exchange.GLOBAL,
            # interval=df["interval"][0],
            interval=Interval.DAILY,
            datetime=df["timestamp"][0], # 初始占位
            open_price=df["open"][0],
            high_price=df["high"][0],
            low_price=df["low"][0],
            close_price=df["close"][0],
            volume=df["volume"][0],
            # turnover=df["turnover"][0],
            # open_interest=df["open_interest"][0]
            gateway_name="okx"
        )

    def __iter__(self):
        self._cursor = 0
        return self

    def __next__(self) -> BarData:
        if self._cursor < self.length:
            i = self._cursor
            bar = self._bar

            # 3. 高性能属性更新 (核心：复用同一个内存地址)
            # 注意：从 Polars/NumPy 转换 datetime 对象是 Python 层面的性能瓶颈
            # 如果追求极致速度，建议在策略里直接用时间戳数字
            bar.datetime = self.dt_view[i]
            bar.open_price = self.o_view[i]
            bar.high_price = self.h_view[i]
            bar.low_price = self.l_view[i]
            bar.close_price = self.c_view[i]
            bar.volume = self.v_view[i]
            # bar.turnover = self.t_view[i]
            # bar.open_interest = self.oi_view[i]

            self._cursor += 1
            return bar
        else:
            raise StopIteration
