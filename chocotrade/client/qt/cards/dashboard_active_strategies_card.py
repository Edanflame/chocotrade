from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from ....utilities import load_source

# =================================================================
# 样式定义 (QSS)
# =================================================================
ACTIVE_STRATEGIES_STYLESHEET = """
/* --- 主容器卡片 --- */
#ModuleContainer {
    background-color: #201a18;
    border-radius: 12px;
}

#ModuleTitle {
    font-size: 18px;
    font-weight: bold;
    color: #d5c5a8;
}

/* --- 策略单项 (StrategyItem) --- */
#StrategyItem {
    background-color: #251e1c;
    border-radius: 8px;
    border-left: 4px solid #3b3331; /* 默认 IDLE 颜色 */
}

/* 动态边框颜色映射 */
#StrategyItem[status="LIVE"] { border-left: 4px solid #e9c349; }
#StrategyItem[status="IDLE"] { border-left: 4px solid rgba(79, 69, 63, 0.3); }
#StrategyItem[status="HALTED"] { border-left: 4px solid #ffb4ab; }

.NameLabel {
    font-weight: bold;
    font-size: 13px;
    color: #ede0dc;
}

.MetricLabel {
    color: #d2c4bc;
    font-size: 12px;
}

/* --- 状态徽章 (StatusBadge) --- */
.StatusBadge {
    font-size: 10px;
    font-weight: bold;
    padding: 2px 8px;
    border-radius: 4px;
}

.StatusBadge[status="LIVE"] {
    background-color: #3b2d00;
    color: #e9c349;
}
.StatusBadge[status="IDLE"] {
    background-color: #3b3331;
    color: #d2c4bc;
}
.StatusBadge[status="HALTED"] {
    background-color: #93000a;
    color: #ffb4ab;
}

/* --- 数值标签 (ValueLabel) --- */
.ValueLabel {
    font-weight: bold;
    font-size: 14px;
    color: #ede0dc;
}
.ValueLabel[status="LIVE"] {
    font-size: 18px;
}

/* --- 底部按钮 --- */
#ViewManagerBtn {
    background-color: transparent;
    color: #e9c349;
    border: 1px solid rgba(233, 195, 73, 0.2);
    border-radius: 4px;
    padding: 10px;
    font-weight: bold;
    font-size: 11px;
}

#ViewManagerBtn:hover {
    background-color: rgba(233, 195, 73, 0.05);
}
"""

# =================================================================
# 组件实现
# =================================================================

class StrategyItem(QFrame):
    def __init__(self, name, status_text, status_type, label, value, value_color=None):
        super().__init__()
        self.setObjectName("StrategyItem")
        # 通过属性控制 QSS 中的边框颜色
        self.setProperty("status", status_type)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)

        # 第一行：名称 + 状态标签
        top_row = QHBoxLayout()
        name_lbl = QLabel(name)
        name_lbl.setProperty("class", "NameLabel")

        status_badge = QLabel(status_text)
        status_badge.setProperty("class", "StatusBadge")
        status_badge.setProperty("status", status_type) # 控制徽章背景和文字颜色

        top_row.addWidget(name_lbl)
        top_row.addStretch()
        top_row.addWidget(status_badge)

        # 第二行：指标标签 + 指标值
        bottom_row = QHBoxLayout()
        bottom_row.setAlignment(Qt.AlignBottom)

        label_lbl = QLabel(label)
        label_lbl.setProperty("class", "MetricLabel")

        value_lbl = QLabel(value)
        value_lbl.setProperty("class", "ValueLabel")
        value_lbl.setProperty("status", status_type) # 控制 LIVE 时的字体加大

        # 只有在传入了特定的 value_color (如绿色 +1.42%) 时才覆盖样式
        if value_color:
            value_lbl.setStyleSheet(f"color: {value_color};")

        bottom_row.addWidget(label_lbl)
        bottom_row.addStretch()
        bottom_row.addWidget(value_lbl)

        layout.addLayout(top_row)
        layout.addLayout(bottom_row)


class ActiveStrategiesCard(QFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName("ModuleContainer")
        # 应用提取出的样式表
        self.setStyleSheet(ACTIVE_STRATEGIES_STYLESHEET)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        # 1. 头部标题
        header_layout = QHBoxLayout()
        header_icon = QLabel()
        header_icon.setPixmap(
            QIcon(str(load_source("src", "icons", "bolt.svg"))).pixmap(QSize(20, 20))
        )

        title = QLabel("Active Strategies")
        title.setObjectName("ModuleTitle")

        header_layout.addWidget(header_icon)
        header_layout.addWidget(title)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # 2. 策略列表容器
        list_container = QVBoxLayout()
        list_container.setSpacing(16)

        # 填充数据
        list_container.addWidget(StrategyItem(
            "Golden Cross HFT", "LIVE", "LIVE",
            "Daily PnL", "+1.42%", value_color="#4ade80"
        ))

        list_container.addWidget(StrategyItem(
            "Mean Reversion Alpha", "IDLE", "IDLE",
            "Last Run", "3h ago"
        ))

        list_container.addWidget(StrategyItem(
            "Volatility Arbitrage", "HALTED", "HALTED",
            "Reason", "LATENCY SPIKE", value_color="#ffb4ab"
        ))

        layout.addLayout(list_container)
        layout.addStretch()

        # 3. 底部按钮
        footer_btn = QPushButton("VIEW STRATEGY MANAGER")
        footer_btn.setObjectName("ViewManagerBtn")
        footer_btn.setCursor(Qt.PointingHandCursor)
        layout.addWidget(footer_btn)
