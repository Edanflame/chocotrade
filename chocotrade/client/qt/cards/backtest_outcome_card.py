from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from ....utilities import _
from ..dialogs.backtest_report_dialog import BacktestDetailDialog
from ..dialogs.backtest_start_dialog import BacktestConfigDialog

CARDS_STYLESHEET = """
/* ---------------- MiniBarChart ---------------- */
.MiniBar {
    border-top-left-radius: 2px;
    border-top-right-radius: 2px;
    border: none;
    opacity: 0.2;
}

/* ---------------- BacktestCard ---------------- */
#Card {
    background-color: #251e1c;
    border: 1px solid rgba(79, 69, 63, 0.2);
    border-radius: 12px;
}
#Card:hover {
    background-color: #2f2826;
    border: 1px solid rgba(233, 195, 73, 0.3);
}

.CategoryLabel {
    color: #d5c5a8;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 2px;
}

.NameLabel {
    color: #ede0dc;
    font-size: 18px;
    font-weight: bold;
}

#StatusBadge {
    background-color: #3b3331;
    font-size: 10px;
    font-weight: 800;
    text-transform: uppercase;
    border: 1px solid transparent;
    border-radius: 10px;
    padding: 2px 10px;
}

/* 状态标签颜色动态切换 */
#StatusBadge[status="Optimized"] { color: #4ade80; }
#StatusBadge[status="Legacy"] { color: #d2c4bc; }
#StatusBadge[status="In-Progress"] { color: #e9c349; }

.ChartContainer {
    background-color: #181210;
    border-radius: 8px;
}

.ProcessingLabel {
    color: #d5c5a8;
    font-style: italic;
    font-size: 11px;
}

.GridHeaderLabel {
    color: #d2c4bc;
    font-size: 10px;
    font-weight: bold;
}

.GridValueLabel {
    font-size: 16px;
    font-weight: bold;
}

.DetailButton {
    background-color: #3b3331;
    border: none;
    border-radius: 6px;
    padding: 12px;
    font-weight: bold;
    font-size: 12px;
}
.DetailButton:hover { background-color: #3f3835; }

/* ---------------- NewTestCard ---------------- */
#NewTestCard {
    background-color: #181210;
    border: 2px dashed rgba(79, 69, 63, 0.3);
    border-radius: 12px;
}
#NewTestCard:hover {
    border: 2px dashed #e9c349;
    background-color: #1c1614;
}

.IconCircle {
    background-color: #3b3331;
    border-radius: 32px;
}

.PlusIcon {
    color: #e9c349;
    font-size: 28px;
    font-weight: bold;
    background: transparent;
}

.NewTestTitle {
    color: #ede0dc;
    font-size: 20px;
    font-weight: 800;
    background: transparent;
}

.NewTestDesc {
    color: #d2c4bc;
    font-size: 13px;
    background: transparent;
}

.ConfigButton {
    background-color: #e9c349;
    color: #3c2f00;
    font-weight: bold;
    border-radius: 6px;
    font-size: 12px;
    text-transform: uppercase;
}
.ConfigButton:hover { background-color: #f2e0c3; }
.ConfigButton:pressed {
    background-color: #d4ae3d;
    padding-left: 5px;
    padding-top: 5px;
}
"""


class MiniBarChart(QWidget):
    def __init__(self, values, color="#e9c349"):
        super().__init__()
        self.setStyleSheet(CARDS_STYLESHEET)
        self.setFixedHeight(100)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        layout.setAlignment(Qt.AlignBottom)

        for val in values:
            bar = QFrame()
            bar.setProperty("class", "MiniBar")
            bar.setStyleSheet(f"background-color: {color};")
            bar.setFixedHeight(int(60 * val))
            layout.addWidget(bar, 1, Qt.AlignBottom)


class BacktestCard(QFrame):
    def __init__(
        self,
        category,
        name,
        status,
        stats,
        chart_data,
        backtest_result,
        is_processing=False
    ):
        super().__init__()
        self.setStyleSheet(CARDS_STYLESHEET)
        self.setObjectName("Card")
        self.setMinimumWidth(300)

        self.backtest_result = backtest_result

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        # 1. 顶部
        header = QHBoxLayout()
        title_vbox = QVBoxLayout()

        cat_lbl = QLabel(category.upper())
        cat_lbl.setProperty("class", "CategoryLabel")

        name_lbl = QLabel(name)
        name_lbl.setProperty("class", "NameLabel")

        title_vbox.addWidget(cat_lbl)
        title_vbox.addWidget(name_lbl)

        self.status_badge = QLabel(f" ●  {status}")
        self.status_badge.setObjectName("StatusBadge")
        self.status_badge.setProperty("status", status if not is_processing else "In-Progress")
        self.status_badge.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.status_badge.setAlignment(Qt.AlignCenter)

        header.addLayout(title_vbox)
        header.addStretch()
        header.addWidget(self.status_badge)
        layout.addLayout(header)

        # 2. 中间图表
        chart_container = QFrame()
        chart_container.setObjectName("ChartContainer")
        chart_container.setProperty("class", "ChartContainer")
        chart_container.setFixedHeight(100)
        chart_layout = QVBoxLayout(chart_container)

        if is_processing:
            proc_lbl = QLabel(_("Crunching historical tick data..."))
            proc_lbl.setProperty("class", "ProcessingLabel")
            proc_lbl.setAlignment(Qt.AlignCenter)
            chart_layout.addWidget(proc_lbl)
        else:
            chart = MiniBarChart(chart_data, color="rgba(233, 195, 73, 0.6)")
            chart_layout.addWidget(chart)

        layout.addWidget(chart_container)

        # 3. 数据网格
        self.stats_grid = QGridLayout()
        self.stats_grid.setSpacing(10)
        layout.addLayout(self.stats_grid)
        self.update_overview_metric(stats, is_processing)

        # 4. 底部按钮
        btn_text = _("View Detailed Report") if not is_processing else _("Processing Results")
        self.footer_btn = QPushButton(btn_text)
        self.footer_btn.setProperty("class", "DetailButton")
        # 按钮文字颜色随状态标签变化
        badge_color = "#e9c349" if is_processing else \
            ("#4ade80" if status == "Optimized" else "#d2c4bc")
        self.footer_btn.setStyleSheet(f"color: {badge_color};")

        self.footer_btn.clicked.connect(self.open_report)
        self.footer_btn.setCursor(Qt.PointingHandCursor)
        self.footer_btn.setEnabled(not is_processing)

        layout.addWidget(self.footer_btn)

    def update_overview_metric(self, stats, is_processing):
        """更新数据网格"""
        labels = [_("Return"), _("Sharpe"), _("Drawdown")]
        for i, stat in enumerate(stats):
            l_lbl = QLabel(labels[i].upper())
            l_lbl.setProperty("class", "GridHeaderLabel")

            v_val = stat
            # 颜色逻辑保持在代码中，因为它是基于数据的逻辑
            v_color = "#ede0dc"
            if not is_processing:
                if "-" in v_val:
                    v_color = "#ffb4ab"
                elif "+" in v_val:
                    v_color = "#4ade80"
            else:
                v_color = "rgba(210,196,188,0.3)"

            v_lbl = QLabel(v_val)
            v_lbl.setProperty("class", "GridValueLabel")
            v_lbl.setStyleSheet(f"color: {v_color};")

            self.stats_grid.addWidget(l_lbl, 0, i)
            self.stats_grid.addWidget(v_lbl, 1, i)

    def update_overview_chart(self):
        """"""
        pass

    def update_overview(self):
        """"""
        pass

    def update_backtest_result(self, data):
        """"""
        self.backtest_result = data["backtest_result"]

        self.update_overview_metric(
            ["+" + str(data["backtest_result"]["totalNetPnl"] / 1000) + "%",
             str(data["backtest_result"]["sharpeRatio"]),
             "-12%"],
            False
        )

        status = _("finish")
        self.status_badge.setText(f" ●  {status}")
        self.footer_btn.setText(_("View Detailed Report"))
        self.footer_btn.setEnabled(True)

    def open_report(self):
        dialog = BacktestDetailDialog(self, self.backtest_result)
        dialog.exec()


class NewTestCard(QFrame):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent

        self.setStyleSheet(CARDS_STYLESHEET)
        self.setObjectName("NewTestCard")
        self.setMinimumHeight(300)
        self.setMinimumWidth(300)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(15)
        layout.setAlignment(Qt.AlignCenter)

        icon_circle = QFrame()
        icon_circle.setFixedSize(64, 64)
        icon_circle.setProperty("class", "IconCircle")
        icon_layout = QVBoxLayout(icon_circle)

        plus_icon = QLabel("＋")
        plus_icon.setProperty("class", "PlusIcon")
        plus_icon.setAlignment(Qt.AlignCenter)
        icon_layout.addWidget(plus_icon)

        title = QLabel(_("Execute New Test"))
        title.setProperty("class", "NewTestTitle")

        desc = QLabel(_("Simulate your strategy against\nhistorical volatility pools."))
        desc.setProperty("class", "NewTestDesc")
        desc.setAlignment(Qt.AlignCenter)

        config_btn = QPushButton(_("Configure Engine"))
        config_btn.setProperty("class", "ConfigButton")
        config_btn.setCursor(Qt.PointingHandCursor)
        config_btn.setFixedSize(160, 40)
        # config_btn.clicked.connect(self.parent.add_new_card)
        config_btn.clicked.connect(self.open_report)

        layout.addStretch()
        layout.addWidget(icon_circle, 0, Qt.AlignCenter)
        layout.addWidget(title, 0, Qt.AlignCenter)
        layout.addWidget(desc, 0, Qt.AlignCenter)
        layout.addSpacing(10)
        layout.addWidget(config_btn, 0, Qt.AlignCenter)
        layout.addStretch()

    def open_report(self):
        dialog = BacktestConfigDialog(self)
        if dialog.exec():
            config_data = dialog.get_results()
            self.parent.start_new_backtest(config_data)
        else:
            pass
