from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QColor, QIcon, QPainter
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from ....utilities import load_source

# =================================================================
# 颜色与样式定义
# =================================================================
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

INFRA_STYLESHEET = f"""
/* ---------------- StatusItem ---------------- */
#ItemContainer {{
    background-color: {COLORS['surface_high']};
    border-radius: 8px;
    border: 1px solid transparent;
}}
#ItemContainer:hover {{
    background-color: #3f3835;
    border: 1px solid {COLORS['primary']};
}}
#ItemContainer[isError="true"]:hover {{
    border: 1px solid {COLORS['error']};
}}

#IconBg {{
    background-color: {COLORS['surface_highest']};
    border-radius: 4px;
}}
#IconBg[isError="true"] {{
    background-color: rgba(147, 0, 10, 0.2);
}}

.ItemName {{
    font-weight: bold;
    font-size: 11px;
    color: #ede0dc;
}}

.ItemDesc {{
    font-size: 9px;
    color: {COLORS['on_surface_variant']};
    text-transform: uppercase;
}}
.ItemDesc[isError="true"] {{
    color: {COLORS['error']};
}}

.LatencyText {{
    font-size: 9px;
    color: {COLORS['on_surface_variant']};
}}
.LatencyText[isError="true"] {{
    color: {COLORS['error']};
}}

#StatusDot {{
    border-radius: 4px;
}}

/* ---------------- Sparkline ---------------- */
.SparkBar {{
    border-top-left-radius: 2px;
    border-top-right-radius: 2px;
    border: none;
}}

#SparklineTitle {{
    font-size: 10px;
    letter-spacing: 2px;
    font-weight: bold;
    color: {COLORS['on_surface_variant']};
}}

/* ---------------- InfraCard ---------------- */
#infra_card {{
    background-color: {COLORS['surface']};
    border-radius: 12px;
}}

#CardHeader {{
    background-color: rgba(32, 26, 24, 0.5);
    border-bottom: 1px solid rgba(79, 69, 63, 0.1);
    border-top-left-radius: 12px;
    border-top-right-radius: 12px;
}}

#CardTitle {{
    color: {COLORS['primary']};
    font-weight: bold;
    font-size: 16px;
}}

.HeaderInfoText {{
    font-size: 10px;
    color: rgba(210, 196, 188, 0.6);
    letter-spacing: 1px;
}}

QScrollArea {{
    border: none;
    background: transparent; /* 让QScrollArea的背景透明 */
    background-color: rgba(32, 26, 24, 0.5);
}}


QScrollBar:vertical {{
    background: transparent;
    width: 4px;
}}

QScrollBar::handle:vertical {{
    background: #4f453f;
    border-radius: 2px;
}}

QScrollBar:horizontal {{
    background: transparent;
    height: 4px; /* 横向滚动条是高度，竖向是宽度 */
}}

QScrollBar::handle:horizontal {{
    background: #4f453f; /* 滚动条手柄颜色 */
    border-radius: 2px;
}}

"""


# =================================================================
# 组件实现
# =================================================================

class StatusItem(QFrame):
    def __init__(self, icon_name, name, desc, latency, is_error=False):
        super().__init__()
        self.setMinimumHeight(60)
        self.STYLE = f"""
            #ItemContainer {{
                background-color: {COLORS['surface_high']};
                border-radius: 8px;
                border: 1px solid transparent;
            }}
            #ItemContainer:hover {{
                background-color: #3f3835;
                border: 1px solid {COLORS['error'] if is_error else COLORS['primary']};
            }}
        """
        self.setObjectName("ItemContainer")
        self.setStyleSheet(self.STYLE)
        self.setProperty("isError", is_error)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(10)

        # 图标容器
        icon_bg = QFrame()
        icon_bg.setObjectName("IconBg")
        icon_bg.setProperty("isError", is_error)
        icon_bg.setFixedSize(32, 32)
        bg_color = "rgba(147, 0, 10, 0.2)" if is_error else COLORS['surface_highest']
        icon_bg.setStyleSheet(f"background-color: {bg_color}; border-radius: 4px;")

        icon_label = QLabel(icon_bg)
        pixmap = QIcon(str(load_source("src", "icons", f"{icon_name}.svg"))).pixmap(QSize(18, 18))
        # 动态给图标上色
        painter = QPainter(pixmap)
        painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
        painter.fillRect(
            pixmap.rect(),
            QColor(COLORS['primary'] if not is_error else COLORS['error'])
        )
        painter.end()
        icon_label.setPixmap(pixmap)
        icon_label.setAlignment(Qt.AlignCenter)

        v = QVBoxLayout(icon_bg)
        v.setContentsMargins(0, 0, 0, 0)
        v.addWidget(icon_label)

        # 文字信息
        info_layout = QVBoxLayout()
        info_layout.setSpacing(0)

        name_lbl = QLabel(name)
        name_lbl.setProperty("class", "ItemName")

        desc_lbl = QLabel(desc)
        desc_lbl.setProperty("class", "ItemDesc")
        desc_lbl.setProperty("isError", is_error)

        info_layout.addWidget(name_lbl)
        info_layout.addWidget(desc_lbl)

        # 右侧状态
        status_layout = QHBoxLayout()
        status_layout.setSpacing(6)

        lat_lbl = QLabel(latency)
        lat_lbl.setProperty("class", "LatencyText")
        lat_lbl.setProperty("isError", is_error)

        dot = QFrame()
        dot.setObjectName("StatusDot")
        dot.setFixedSize(8, 8)
        dot.setStyleSheet(f"""
            background-color: {COLORS['error'] if is_error else COLORS['success']};
        """)

        status_layout.addWidget(lat_lbl)
        status_layout.addWidget(dot)

        layout.addWidget(icon_bg)
        layout.addLayout(info_layout)
        layout.addStretch()
        layout.addLayout(status_layout)


class SparklineBar(QFrame):
    def __init__(self, height_percent, color):
        super().__init__()
        self.setFixedHeight(int(64 * height_percent))
        self.setProperty("class", "SparkBar")
        self.setStyleSheet(f"background-color: {color};")


class SparklineView(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedHeight(70)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        title = QLabel("NETWORK LATENCY (LAST 60M)")
        title.setObjectName("SparklineTitle")
        layout.addWidget(title)

        bars_layout = QHBoxLayout()
        bars_layout.setSpacing(4)
        bars_layout.setContentsMargins(0, 0, 0, 0)
        bars_layout.setAlignment(Qt.AlignBottom)

        data = [0.5, 0.75, 0.6, 0.5, 1.0, 0.6, 0.8, 0.5, 0.3,
                0.6, 0.8, 0.5, 0.3, 0.7, 0.5, 0.3, 0.6, 0.8]
        for i, val in enumerate(data):
            color = "rgba(255, 180, 171, 0.6)" if i == 4 else "rgba(233, 195, 73, 0.3)"
            bar = SparklineBar(val, color)
            bars_layout.addWidget(bar, 1, Qt.AlignBottom)

        layout.addLayout(bars_layout)
        layout.addStretch(1)


class InfraCard(QFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName("infra_card")
        self.setStyleSheet(INFRA_STYLESHEET)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. 标题栏
        header = QFrame()
        header.setObjectName("CardHeader")
        header.setFixedHeight(56)
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(24, 0, 24, 0)

        infra_icon = QLabel()
        infra_icon.setPixmap(QIcon(str(load_source("src", "icons", "hub.svg")))
            .pixmap(QSize(20, 20)))

        title_lbl = QLabel("Infrastructure Health")
        title_lbl.setObjectName("CardTitle")

        info_box = QHBoxLayout()
        for txt in ["INSTANCES: 12 ACTIVE", "LAST POLL: 14:02:45 GMT"]:
            lbl = QLabel(txt)
            lbl.setProperty("class", "HeaderInfoText")
            info_box.addWidget(lbl)
            info_box.addSpacing(15)

        h_layout.addWidget(infra_icon)
        h_layout.addWidget(title_lbl)
        h_layout.addStretch()
        h_layout.addLayout(info_box)
        main_layout.addWidget(header)

        # 2. 滚动网格
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        grid_container = QWidget()
        grid_layout = QGridLayout(grid_container)
        grid_layout.setContentsMargins(24, 24, 24, 24)
        grid_layout.setSpacing(12)
        grid_container.setAttribute(Qt.WA_StyledBackground, True)
        grid_container.setStyleSheet("background-color: transparent;")

        monitors = [
            ("api", "Coinbase Pro API", "ORDER GATEWAY", "12ms"),
            ("storage", "PostgreSQL 01", "PRIMARY ARCHIVE", "0.4ms"),
            ("cloud_off", "Binance WS", "RECONNECTING", "TIMEOUT", True),
            ("memory", "Redis Cache", "HOT MEMORY", "0.1ms"),
            ("key", "Vault KMS", "ENCRYPTION SERVICE", "42ms"),
            ("cloud", "AWS S3 Gateway", "SNAPSHOT SYNC", "85ms"),
            ("api", "Kraken REST", "SECONDARY EXEC", "156ms"),
            ("dns", "PG Replica 02", "READ-ONLY POOL", "2ms"),
            ("notification_important", "Discord Webhook", "ALERT SYSTEM", "210ms"),
            ("swap_calls", "Deribit WS", "OPTIONS FLOW", "18ms"),
            ("lan", "Proxy Node 04", "OFFLINE", "DOWN", True),
            ("precision_manufacturing", "Exec Cluster A", "COMPUTE NODE", "5ms"),
        ]

        for i, m in enumerate(monitors):
            row, col = divmod(i, 3)
            grid_layout.addWidget(StatusItem(*m), row, col)

        scroll.setWidget(grid_container)
        main_layout.addWidget(scroll)

        # 3. 底部图表
        chart_container = QFrame()
        chart_layout = QVBoxLayout(chart_container)
        chart_layout.setContentsMargins(24, 10, 24, 24)
        chart_layout.addWidget(SparklineView())
        main_layout.addWidget(chart_container)
