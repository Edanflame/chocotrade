
from PySide6.QtWidgets import (
    QGridLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from ....utilities import _
from ...qt.cards import (
    ActiveStrategiesCard,
    BacktestEngineCard,
    ExecutionLogModule,
    InfraCard,
    PortfolioCard,
)

COLORS = {
    "background": "#181210",
    "surface": "#251e1c",
    "surface_low": "#201a18",
    "surface_high": "#2f2826",
    "surface_highest": "#3b3331",
    "surface_lowest": "#130d0b",
    "primary": "#e9c349",
    "on_primary": "#3c2f00",
    "on_surface": "#ede0dc",
    "on_surface_variant": "#d2c4bc",
    "outline": "#4f453f",
    "error": "#ffb4ab",
    "success": "#4ade80",
    "tertiary": "#d5c5a8"
}

class DashboardPage(QWidget):
    """右侧内容：首页仪表盘"""
    def __init__(self):
        super().__init__()
        # 总布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(25)

        # 总标题
        h_title = QLabel(_("System Overview"))
        h_title.setStyleSheet("font-size: 32px; font-weight: 800;")
        h_sub = QLabel(_("Real-time health and operational status."))
        h_sub.setStyleSheet(f"color: {COLORS['on_surface_variant']};")
        layout.addWidget(h_title)
        layout.addWidget(h_sub)

        # 栅格布局
        grid = QGridLayout()
        grid.setSpacing(20)

        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(2, 1)
        grid.setColumnStretch(3, 1)
        grid.setColumnStretch(4, 1)
        grid.setColumnStretch(5, 1)

        # 1. 基础设施卡片
        infra_card = InfraCard()
        grid.addWidget(infra_card, 0, 0, 1, 4)

        active_strategies_card = ActiveStrategiesCard()
        grid.addWidget(active_strategies_card, 0, 4, 1, 2)

        backtest_engine_card = BacktestEngineCard()
        grid.addWidget(backtest_engine_card, 1, 0, 1, 3)

        portfolio_card = PortfolioCard()
        grid.addWidget(portfolio_card, 1, 3, 1, 3)

        live_log_card = ExecutionLogModule()
        grid.addWidget(live_log_card, 2, 0, 1, 6)

        layout.addLayout(grid)
        layout.addStretch()
