""""""
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """"""
    base_dir: Path = Path.home() / ".chocotrade"
    default_box_database: str = "box.sqlite"
    default_bars_database: str = "bars.duckdb"

    def __init__(self):
        """"""
        super().__init__()

    @field_validator("base_dir")
    @classmethod
    def ensure_dir_exists(cls, v: Path) -> Path:
        """"""
        if not v.exists():
            v.mkdir(parents=True, exist_ok=True)

        plugins_dir = v / "plugins"
        if not plugins_dir.exists():
            plugins_dir.mkdir(parents=True, exist_ok=True)

        return v

    @property
    def box_database_path(self) -> str:
        """"""
        return str(self.base_dir / self.default_box_database)

    @property
    def bars_database_path(self) -> str:
        """"""
        return str(self.base_dir / self.default_bars_database)

    @property
    def env_path(self) -> str:
        """"""
        return str(self.base_dir / ".env")


settings = Settings()
