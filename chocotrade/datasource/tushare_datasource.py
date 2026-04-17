""""""
import logging

import polars as pl
import tushare as ts
from pydantic_settings import SettingsConfigDict

from ..base.plugin import CHOCO_ENV_FILE, BasePlugin, BaseSettings

logger = logging.getLogger("tushare")


EXCHANGE_MAP = {
    "SZ": "SZSE",
    "SH": "SSE",
    "BJ": "BSE"
}


class TushareConfig(BaseSettings):
    token: str = ""

    model_config = SettingsConfigDict(
        env_file=CHOCO_ENV_FILE,
        env_prefix="TUSHARE_",
        extra="ignore"
    )


class TushareDataSource(BasePlugin[TushareConfig]):
    """"""
    config_class = TushareConfig

    _instance = None
    _pro = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """"""
        super().__init__()
        self.start()

    @property
    def pro(self):
        if self._pro is None:
            ts.set_token(self.token)
            self._pro = ts.pro_api()
        return self._pro

    def start(self):
        """"""
        self.token = self.config.token

    def update_auth(self):
        """"""
        ts.set_token(self.token)

    def query_bar_history(
        self,
        symbol,
        start_time: str,
        end_time: str,
        granularity
    ):
        if not self.pro:
            return

        self.update_auth()

        start_date = start_time.split(" ")[0].replace("-", "")
        end_date = end_time.split(" ")[0].replace("-", "")

        try:
            data = ts.pro_bar(
                ts_code=symbol, adj="qfq", start_date=start_date, end_date=end_date
            )
        except OSError as e:
            logger.info(e)
            return

        df = pl.from_pandas(data)
        df = df.select([
            pl.col("ts_code").alias("symbol"),
            pl.col("trade_date").str.to_datetime("%Y%m%d").alias("timestamp"),
            pl.col("open"),
            pl.col("high"),
            pl.col("low"),
            pl.col("close"),
            pl.col("vol").cast(pl.Float64).alias("volume")
        ])
        ts_exchange = symbol.split(".")[1]
        exchange = EXCHANGE_MAP.get(ts_exchange, "")

        df_to_save = df.with_columns(
            pl.lit(exchange).alias("exchange")
        )

        return df_to_save


if __name__ == "__main__":
    td = TushareDataSource()

    td.test()
