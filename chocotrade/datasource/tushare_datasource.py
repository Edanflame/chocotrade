""""""
import polars as pl
import tushare as ts

from ..database.sqlite_database import SqliteBoxDatabase


class TushareDataSource:
    """"""
    _instance = None
    _pro = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """"""
        super().__init__()
        self.init()

    @property
    def pro(self):
        if self._pro is None:
            ts.set_token(self.api_token)
            self._pro = ts.pro_api()
        return self._pro

    def init(self):
        """"""
        sqlitebox = SqliteBoxDatabase()
        self.api_token = sqlitebox.load("data_source", "tushare").get("api_token", None)

    def test(self, symbol):
        print(self.pro)
        print(self.api_token)
        data = ts.pro_bar(
            ts_code= symbol, adj='qfq', start_date='20180101', end_date='20261011'
        )
        df = pl.from_pandas(data)
        df = df.select([
            pl.col("ts_code").alias("symbol"),
            pl.col("trade_date").str.to_datetime("%Y%m%d").alias("timestamp"),
            pl.col("open"),
            pl.col("high"),
            pl.col("low"),
            pl.col("close"),
            pl.col("vol").cast(pl.Float64).alias("volume") # 确保是 DOUBLE
        ])
        ts_exchange = symbol.split(".")[1]
        if ts_exchange == "SZ":
            exchange = "SZSE"
        elif ts_exchange == "SH":
            exchange = "SSE"
        elif ts_exchange == "BJ":
            exchange = "BSE"

        df_to_save = df.with_columns(
            pl.lit(exchange).alias("exchange")
        )

        return df_to_save


if __name__ == "__main__":
    td = TushareDataSource()

    td.test()
