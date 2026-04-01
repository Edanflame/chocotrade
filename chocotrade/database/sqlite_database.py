""""""
import sqlite3

from ..base.database import BoxDatabase
from ..config import settings


class SqliteBoxDatabase(BoxDatabase):
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
        """延迟初始化连接 (Lazy Initialization)"""
        if self._con is None:
            db_path = settings.box_database_path
            self._con = sqlite3.connect(db_path)
            self._con.row_factory = sqlite3.Row

        if not self._initialized_db:
            self._create_db_if_not_exist()
            self._initialized_db = True
        return self._con

    def save(self, category: str, name: str, key: str, value: str):
        """将字典存入数据库"""
        with self.con:
            self.con.execute("""
                INSERT OR REPLACE INTO service_configs (category, name, config_key, config_value)
                VALUES (?, ?, ?, ?)
            """, (category, name, key, value))

    def load(self, category: str, name: str) -> dict:
        """从数据库读取字典"""
        cur = self.con.cursor()
        cur.execute(
            "SELECT config_key, config_value  FROM service_configs WHERE category=? AND name=?",
            (category, name)
        )
        rows = cur.fetchall()
        return {row["config_key"]: row["config_value"] for row in rows}

    def delete(self, category: str, name: str):
        """从数据库删除记录"""
        with self.con:
            self.con.execute(
                "DELETE FROM service_configs WHERE category=? AND name=?",
                (category, name)
            )

    def _create_db_if_not_exist(self):
        """"""
        with self._con:
            self._con.execute("""
                CREATE TABLE IF NOT EXISTS service_configs (
                    category TEXT NOT NULL,      -- 分类：如 'data_source', 'exchange', 'database'
                    name TEXT NOT NULL,          -- 名称：如 'tushare', 'binance', 'influxdb'
                    config_key TEXT NOT NULL,    -- 键名：如 'api_token', 'api_key', 'secret_key'
                    config_value TEXT NOT NULL,  -- 键值：存储加密后的密文或明文
                    is_encrypted INTEGER DEFAULT 0,  -- 是否加密：0-明文, 1-加密
                    description TEXT DEFAULT '',                -- 备注
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (category, name, config_key)
                )
            """)
