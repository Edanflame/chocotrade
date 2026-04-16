""""""
import duckdb
import polars as pl

from ..base.database import BarsDatabase, DatabaseReadError
from ..config import settings


class DuckBarsDatabase(BarsDatabase):
    """"""
    _instance = None
    _con = None
    _initialized_db = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @property
    def con(self):
        # 只有在代码中第一次执行 db.con.execute(...) 时，才会真正去拿 DuckDB 的锁
        if self._con is None:
            db_path = settings.bars_database_path
            self._con = duckdb.connect(db_path)

        if not self._initialized_db:
            self._create_db_if_not_exist()
            self._initialized_db = True
        return self._con

    def query_bar_overview(self):
        """"""
        with self.con.cursor() as cur:
            data = cur.execute("""
                SELECT
                    exchange,
                    symbol,
                    COUNT(*) as total,
                    MIN(timestamp) as start_dt,
                    MAX(timestamp) as end_dt,
                    MAX(updated_at) as last_sync_at
                FROM bars
                GROUP BY exchange, symbol
                ORDER BY last_sync_at DESC
            """).pl()
            return data

    def query_bar_overview_dict(self):
        """"""
        df = self.query_bar_overview()
        processed_df = (
            df.with_columns([
                # 先利用 last_updated 生成你想要的格式（比如字符串）
                pl.col("start_dt").dt.strftime("%Y-%m-%d %H:%M").alias("start_dt_str"),
                pl.col("end_dt").dt.strftime("%Y-%m-%d %H:%M").alias("end_dt_str")
            ])
            .drop("last_sync_at")
            .drop("start_dt")
            .drop("end_dt")
        )

        return processed_df.to_dicts()

    def query_tick_overview(self):
        """"""
        with self.con.cursor() as cur:
            data = cur.execute("""
                SELECT
                    exchange,
                    symbol,
                    COUNT(*) as total,
                    MIN(timestamp) as start_dt,
                    MAX(timestamp) as end_dt,
                    MAX(updated_at) as last_sync_at
                FROM ticks
                GROUP BY exchange, symbol
                ORDER BY last_sync_at DESC
            """).pl()
            return data

    def query_tick_overview_dict(self):
        """"""
        df = self.query_tick_overview()
        processed_df = (
            df.with_columns([
                # 先利用 last_updated 生成你想要的格式（比如字符串）
                pl.col("start_dt").dt.strftime("%Y-%m-%d %H:%M").alias("start_dt_str"),
                pl.col("end_dt").dt.strftime("%Y-%m-%d %H:%M").alias("end_dt_str")
            ])
            .drop("last_sync_at")
            .drop("start_dt")
            .drop("end_dt")
        )

        return processed_df.to_dicts()

    def query_bardata(self, symbol):
        """"""
        with self.con.cursor() as cur:
            data = cur.sql(
                f"""
                SELECT exchange, symbol, timestamp, open, high, low, close, volume FROM bars
                WHERE symbol='{symbol}'
                ORDER BY timestamp ASC
                """
            ).pl()

            if len(data) == 0:
                raise DatabaseReadError(f"查询结束，但未能从 DuckDB 提取到 '{symbol}' 的任何数据。")

            return data

    def query_tickdata(self):
        """"""
        pass

    def update_bardata(self, data: pl.DataFrame):
        """"""
        self.con.execute("""
            INSERT OR IGNORE INTO bars BY NAME
            SELECT * FROM data
        """)

    def update_tickdata(self, data):
        """"""
        self.con.execute("""
            INSERT OR IGNORE INTO ticks BY NAME
            SELECT * FROM data
        """)

    def delete_bardata(self):
        """"""
        pass

    def delete_tickdata(self):
        """"""
        pass

    def query_symbol_metadata(self):
        """"""
        pass

    def _create_db_if_not_exist(self):
        """"""
        with self._con.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS bars (
                    exchange  VARCHAR,
                    symbol    VARCHAR,
                    timestamp TIMESTAMP,
                    open      DOUBLE,
                    high      DOUBLE,
                    low       DOUBLE,
                    close     DOUBLE,
                    volume    DOUBLE,
                    updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (symbol, exchange, timestamp)
                )
                """
            )

            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS ticks (
                    exchange       VARCHAR,
                    symbol         VARCHAR,
                    timestamp      TIMESTAMP,
                    name           VARCHAR,
                    volume         DOUBLE,
                    turnover       DOUBLE,
                    open_interest  DOUBLE,
                    last_price     DOUBLE,
                    last_volume    DOUBLE,
                    limit_up       DOUBLE,
                    limit_down     DOUBLE,

                    open_price     DOUBLE,
                    high_price     DOUBLE,
                    low_price      DOUBLE,
                    pre_close      DOUBLE,

                    bid_price_1    DOUBLE,
                    bid_price_2    DOUBLE,
                    bid_price_3    DOUBLE,
                    bid_price_4    DOUBLE,
                    bid_price_5    DOUBLE,

                    ask_price_1    DOUBLE,
                    ask_price_2    DOUBLE,
                    ask_price_3    DOUBLE,
                    ask_price_4    DOUBLE,
                    ask_price_5    DOUBLE,

                    bid_volume_1   DOUBLE,
                    bid_volume_2   DOUBLE,
                    bid_volume_3   DOUBLE,
                    bid_volume_4   DOUBLE,
                    bid_volume_5   DOUBLE,

                    ask_volume_1   DOUBLE,
                    ask_volume_2   DOUBLE,
                    ask_volume_3   DOUBLE,
                    ask_volume_4   DOUBLE,
                    ask_volume_5   DOUBLE,
                    updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (symbol, exchange, timestamp)
                )
                """
            )

