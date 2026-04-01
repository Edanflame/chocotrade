import logging

from PySide6.QtCore import QSize, Qt, QThread, Signal
from PySide6.QtGui import QColor, QCursor, QIcon
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,  # <--- 新增
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from ....utilities import load_source
from ...client import get_overview, sync_data
from ..dialogs.marketdata_download_dialog import DataAcquisitionDialog

logger = logging.getLogger("Frontend")

# =================================================================
# 1. 颜色与主题配置
# =================================================================
T = {
    "bg": "#181210",
    "surface": "#251e1c",
    "surface_low": "#201a18",
    "surface_high": "#2f2826",
    "surface_highest": "#3b3331",
    "surface_bright": "#3f3835",
    "primary": "#e9c349",
    "on_primary": "#241a00",
    "primary_bg": "rgba(233, 195, 73, 0.1)",
    "secondary": "#f9ba82",
    "secondary_container": "#683d0f",
    "on_secondary_container": "#e6a872",
    "text": "#ede0dc",
    "text_dim": "#d2c4bc",
    "outline": "#4f453f",
    "emerald": "#4ade80",
    "error": "#ffb4ab",
    "tertiary": "#d5c5a8"
}

# =================================================================
# 2. 全局 QSS 样式表
# =================================================================
GLOBAL_QSS = f"""
QWidget#MainContainer {{ background-color: {T['bg']}; border: none; }}
QScrollArea {{ background-color: transparent; border: none; }}
QWidget#ScrollContent {{ background-color: transparent; }}

QLabel[class="page-title"] {{
    font-size: 40px; font-weight: 800; font-family: 'Manrope'; color: {T['text']};
}}
QLabel[class="page-subtitle"] {{ color: {T['text_dim']}; font-size: 16px; font-family: 'Inter'; }}

QFrame[class="status-badge-container"] {{
    background-color: {T['surface_low']}; border-radius: 8px; padding: 6px;
}}
QLabel[class="status-badge"] {{
    background-color: {T['surface_highest']}; color: {T['emerald']};
    font-weight: bold; font-size: 11px; padding: 6px 12px; border-radius: 12px;
}}

QFrame[class="bento-box"] {{
    background-color: {T['surface']}; border-radius: 12px; border: 1px solid {T['outline']}33;
}}
QFrame[class="bento-box-low"] {{
    background-color: {T['surface_low']}; border-radius: 12px; border: 1px solid {T['outline']}33;
}}
QFrame[class="bento-box-active"] {{
    background-color: {T['surface']}; border-radius: 12px;
    border: 1px solid {T['outline']}33; border-left: 4px solid {T['primary']};
}}

QLabel {{ background: transparent; border: none; color: {T['text']}; font-family: 'Inter'; }}
QLabel[class="card-title"] {{ font-size: 20px; font-weight: bold; font-family: 'Manrope'; }}
QLabel[class="stat-label"] {{
    color: {T['outline']};
    font-size: 10px; font-weight: bold;
    text-transform: uppercase; letter-spacing: 1px;
}}
QLabel[class="stat-value"] {{ font-size: 28px; font-weight: bold; font-family: 'Manrope'; }}
QLabel[class="stat-value-primary"] {{
    font-size: 28px; font-weight: bold; color: {T['primary']}; font-family: 'Manrope';
}}

QProgressBar {{ background-color: {T['surface_highest']}; border-radius: 3px; border: none; }}
QProgressBar::chunk {{ border-radius: 3px; }}
QProgressBar[class="prog-primary"]::chunk {{ background-color: {T['primary']}; }}
QProgressBar[class="prog-error"]::chunk {{ background-color: {T['error']}; }}

QPushButton {{ font-weight: bold; border-radius: 6px; font-family: 'Inter'; }}
QPushButton[class="btn-primary"] {{
    background-color: {T['primary']}; color: {T['on_primary']}; padding: 12px 24px; border: none;
}}
QPushButton[class="btn-primary"]:hover {{ background-color: #ffdf7a; }}
QPushButton[class="btn-secondary"] {{
    background-color: {T['secondary_container']};
    color: {T['on_secondary_container']}; padding: 12px 24px; border: none;
}}
QPushButton[class="btn-secondary"]:hover {{ background-color: #7d4a13; }}
QPushButton[class="btn-ghost"] {{
    color: {T['text_dim']}; padding: 12px 16px; border: none; background: transparent;
}}
QPushButton[class="btn-ghost"]:hover {{ color: {T['text']}; background: {T['surface_highest']}; }}
QPushButton[class="btn-outline"] {{
    color: {T['outline']};
    border: 1px solid {T['outline']}44;
    padding: 10px;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 1px;
}}
QPushButton[class="btn-outline"]:hover {{
    color: {T['primary']}; border: 1px solid {T['primary']}66;
}}
QPushButton[class="btn-icon"] {{
    background-color: transparent; color: {T['text_dim']};
    border: none; padding: 6px; border-radius: 4px;
}}
QPushButton[class="btn-icon"]:hover {{ background-color: {T['surface_highest']}; }}
QPushButton[class="btn-action-small"] {{
    background-color: {T['surface_highest']};
    color: {T['text']}; padding: 6px 12px; font-size: 11px; border: none;
}}
QPushButton[class="btn-action-small"]:hover {{
    background-color: {T['primary']}; color: {T['on_primary']};
}}
QPushButton[class="btn-text-primary"] {{
    color: {T['primary']}; font-weight: bold; border: none;
    background: transparent; font-size: 12px;
}}
QPushButton[class="btn-text-primary"]:hover {{ text-decoration: underline; }}

/* 市场与图标容器 */
QFrame[class="market-item"] {{
    background-color: {T['surface_high']}; border-radius: 8px; border: 1px solid transparent;
}}
QFrame[class="market-item"]:hover {{
    background-color: {T['surface_bright']}; border: 1px solid {T['primary']}33;
}}
QFrame[class="icon-circle"] {{ background-color: {T['surface_highest']}; border-radius: 20px; }}
QFrame[class="icon-circle-small"] {{
    background-color: {T['surface_highest']}; border-radius: 16px;
}}

/* 标签 Tags */
QLabel[class="tag-tertiary"] {{
    background-color: {T['surface_highest']};
    color: {T['tertiary']};
    font-size: 10px;
    font-weight: bold;
    padding: 4px 8px;
    border-radius: 4px;
}}
QLabel[class="tag-hollow-secondary"] {{
    color: {T['secondary']};
    background-color: rgba(249, 186, 130, 0.1);
    border: 1px solid rgba(249, 186, 130, 0.2);
    font-size: 9px;
    font-weight: bold;
    padding: 4px 8px;
    border-radius: 4px;
}}
QLabel[class="tag-hollow-primary"] {{
    color: {T['primary']};
    background-color: rgba(233, 195, 73, 0.1);
    border: 1px solid rgba(233, 195, 73, 0.2);
    font-size: 9px;
    font-weight: bold;
    padding: 4px 8px;
    border-radius: 4px;
}}

/* 警告框 */
QFrame[class="warning-box"] {{ background-color: {T['surface_highest']}; border-radius: 8px; }}

/* 自定义表格行样式 */
QFrame[class="custom-table-header"] {{ border-bottom: 1px solid {T['outline']}33; }}
QFrame[class="custom-table-row"] {{
    border-bottom: 1px solid {T['outline']}11; background-color: transparent; border-radius: 6px;
}}
QFrame[class="custom-table-row"]:hover {{ background-color: {T['surface_highest']}; }}

QLabel[class="table-header-text"] {{
    color: {T['outline']};
    font-weight: bold;
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 1px;
}}

QLabel[class="log-time"] {{ color: #9b8e87; font-family: 'Consolas', monospace; font-size: 10px; }}
QLabel[class="log-text"] {{ font-family: 'Consolas', monospace; font-size: 10px; }}
/* 必须写 border: none; 才能让单侧边框生效 */
QFrame[class="log-row-primary"] {{
    border: none;
    border-left: 2px solid #e9c349;
    background-color: transparent;
}}
QFrame[class="log-row-dim"] {{
    border: none;
    border-left: 2px solid rgba(233, 195, 73, 0.2);
    background-color: transparent;
}}
/* 悬浮提示框 (Tooltip) 完美还原网页中的提示 */
QToolTip {{
    background-color: #3f3835;
    color: #ede0dc;
    border: 1px solid #4f453f;
    border-radius: 4px;
    padding: 6px 12px;
    font-size: 12px;
    font-weight: bold;
    font-family: 'Inter';
}}
"""

# =================================================================
# 3. 核心组件与布局
# =================================================================

class BentoBox(QFrame):
    def __init__(self, title=None, style_class="bento-box", parent=None):
        super().__init__(parent)
        self.setProperty("class", style_class)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(28, 28, 28, 28)
        self.layout.setSpacing(20)

        if title:
            t_label = QLabel(title)
            t_label.setProperty("class", "card-title")
            self.layout.addWidget(t_label)

class MarketDataPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tmp_rows = []
        self.setObjectName("MainContainer")
        self.setStyleSheet(GLOBAL_QSS)
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        content_widget = QWidget()
        content_widget.setObjectName("ScrollContent")
        self.content_layout = QVBoxLayout(content_widget)
        self.content_layout.setContentsMargins(32, 40, 32, 40)
        self.content_layout.setSpacing(28)

        self.create_header()

        split_layout = QHBoxLayout()
        split_layout.setSpacing(24)

        left_col = QVBoxLayout()
        left_col.setSpacing(24)
        left_col.addWidget(self.create_session_card())
        left_col.addWidget(self.create_market_selection_card())
        left_col.addWidget(self.create_browser_card())
        left_col.addStretch()

        right_col = QVBoxLayout()
        right_col.setSpacing(24)
        right_col.addWidget(self.create_storage_card())
        right_col.addWidget(self.create_capture_stream_card())
        right_col.addStretch()

        split_layout.addLayout(left_col, stretch=2)
        split_layout.addLayout(right_col, stretch=1)

        self.content_layout.addLayout(split_layout)
        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)

        # =======================================================
        # 新增：创建右下角悬浮按钮 (Contextual FAB)
        # =======================================================
        # 注意：把 self 作为父类传进去，不加入任何 layout
        self.fab_btn = QPushButton("+", self)
        self.fab_btn.setFixedSize(56, 56) # 对应 w-14 h-14
        self.fab_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.fab_btn.setToolTip("New Recording Task") # 悬浮文字
        self.fab_btn.clicked.connect(self.open_download_dialog)

        # 按钮样式 (完美的圆形和居中十字)
        self.fab_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {T['primary']};
                color: {T['on_primary']};
                border-radius: 28px;
                font-size: 32px;
                font-weight: 300;
                padding-bottom: 4px; /* 微调十字居中 */
                border: none;
            }}
            QPushButton:hover {{
                background-color: #ffdf7a;
            }}
            QPushButton:pressed {{
                background-color: #d4ae36;
            }}
        """)

        # 还原网页中的 shadow-2xl 阴影效果
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(25)
        shadow.setColor(QColor(0, 0, 0, 180)) # 纯黑带透明度的浓重阴影
        shadow.setOffset(0, 8) # 阴影垂直向下偏 8px
        self.fab_btn.setGraphicsEffect(shadow)

        # 数据加载线程
        self.loader = DataLoaderThread()
        self.loader.data_loaded.connect(self.update_browser)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # 计算坐标：窗口总宽/高 减去 按钮宽/高 再减去 48px 的边距 (bottom-12 right-12)
        fab_x = self.width() - self.fab_btn.width() - 48
        fab_y = self.height() - self.fab_btn.height() - 48
        # 将按钮移动到计算好的位置
        self.fab_btn.move(fab_x, fab_y)

    def create_header(self):
        header = QHBoxLayout()
        v_box = QVBoxLayout()

        title = QLabel("Market Data Recorder")
        title.setProperty("class", "page-title")
        sub = QLabel("Capture high-fidelity order book updates and trade \
                     streams into the encrypted vault for post-trade analysis.")
        sub.setProperty("class", "page-subtitle")
        sub.setWordWrap(True)

        v_box.addWidget(title)
        v_box.addWidget(sub)
        header.addLayout(v_box)
        header.addStretch()

        badge_container = QFrame()
        badge_container.setProperty("class", "status-badge-container")
        b_layout = QHBoxLayout(badge_container)
        b_layout.setContentsMargins(2, 2, 2, 2)

        status = QLabel("●  RECORDER ENGINE ONLINE")
        status.setProperty("class", "status-badge")
        b_layout.addWidget(status)

        header.addWidget(badge_container, alignment=Qt.AlignBottom)
        self.content_layout.addLayout(header)

    def create_session_card(self):
        card = BentoBox("Active Recording Session", style_class="bento-box-active")

        stats_layout = QHBoxLayout()
        stats_data =[("Duration", "02:44:12", True), ("Data Captured", "14.82 GB", False),
                     ("Write Speed", "124 MB/s", False)]

        for label_text, val, is_primary in stats_data:
            box = QVBoxLayout()
            box.setSpacing(4)
            label = QLabel(label_text)
            label.setProperty("class", "stat-label")
            v = QLabel(val)
            v.setProperty("class", "stat-value-primary" if is_primary else "stat-value")
            box.addWidget(label)
            box.addWidget(v)
            stats_layout.addLayout(box)
        card.layout.addLayout(stats_layout)

        prog_box = QVBoxLayout()
        prog_box.setSpacing(8)
        p_head = QHBoxLayout()
        cap_l = QLabel("Buffer Capacity")
        cap_l.setStyleSheet(f"color: {T['text_dim']}; font-size: 11px;")
        occ_l = QLabel("14% Occupied")
        occ_l.setStyleSheet(f"color: {T['text_dim']}; font-size: 11px;")
        p_head.addWidget(cap_l)
        p_head.addStretch()
        p_head.addWidget(occ_l)

        pbar = QProgressBar()
        pbar.setProperty("class", "prog-primary")
        pbar.setValue(14)
        pbar.setTextVisible(False)
        pbar.setFixedHeight(10)

        prog_box.addLayout(p_head)
        prog_box.addWidget(pbar)
        card.layout.addLayout(prog_box)

        btn_layout = QHBoxLayout()
        stop_btn = QPushButton("⏹ Terminate Session")
        stop_btn.setProperty("class", "btn-primary")
        stop_btn.setCursor(QCursor(Qt.PointingHandCursor))

        pause_btn = QPushButton("⏸ Pause Stream")
        pause_btn.setProperty("class", "btn-secondary")
        pause_btn.setCursor(QCursor(Qt.PointingHandCursor))

        export_btn = QPushButton("Export Partial")
        export_btn.setIcon(QIcon(str(load_source("src", "icons", "download.svg"))))
        export_btn.setProperty("class", "btn-ghost")
        export_btn.setCursor(QCursor(Qt.PointingHandCursor))

        btn_layout.addWidget(stop_btn)
        btn_layout.addWidget(pause_btn)
        btn_layout.addWidget(export_btn)
        btn_layout.addStretch()
        card.layout.addLayout(btn_layout)

        return card

    def create_market_selection_card(self):
        card = BentoBox(style_class="bento-box-low")

        header = QHBoxLayout()
        title = QLabel("Target Market Selection")
        title.setProperty("class", "card-title")
        header.addWidget(title)
        header.addStretch()

        tag1 = QLabel("EXCHANGE: COINBASE_PRO")
        tag1.setProperty("class", "tag-tertiary")
        tag2 = QLabel("TYPE: SPOT")
        tag2.setProperty("class", "tag-tertiary")
        header.addWidget(tag1)
        header.addWidget(tag2)
        card.layout.addLayout(header)

        grid = QGridLayout()
        grid.setSpacing(16)

        # Item 1 (BTC/USD)
        item1 = QFrame()
        item1.setProperty("class", "market-item")
        item1.setCursor(QCursor(Qt.PointingHandCursor))
        i1_layout = QHBoxLayout(item1)
        i1_layout.setContentsMargins(16, 16, 16, 16)

        i1_icon_frame = QFrame()
        i1_icon_frame.setFixedSize(40, 40)
        i1_icon_frame.setProperty("class", "icon-circle")
        i1_icon_layout = QVBoxLayout(i1_icon_frame)
        i1_icon_layout.setContentsMargins(0, 0, 0, 0)
        i1_icon_lbl = QLabel()
        i1_icon_lbl.setPixmap(
            QIcon(str(load_source("src", "icons", "data_usage.svg"))).pixmap(QSize(24, 24))
        )
        i1_icon_lbl.setAlignment(Qt.AlignCenter)
        i1_icon_layout.addWidget(i1_icon_lbl)

        i1_left = QVBoxLayout()
        lbl1 = QLabel("BTC / USD")
        lbl1.setStyleSheet("font-weight: bold; font-size: 14px;")
        lbl2 = QLabel("Perpetual Futures")
        lbl2.setStyleSheet(f"color: {T['outline']}; font-size: 11px;")
        i1_left.addWidget(lbl1)
        i1_left.addWidget(lbl2)

        i1_right = QVBoxLayout()
        i1_right.setAlignment(Qt.AlignRight)
        act_lbl = QLabel("ACTIVE")
        act_lbl.setStyleSheet(f"color: {T['emerald']}; font-size: 12px; font-weight: bold;")
        rec_lbl = QLabel("REC-ID: 4492")
        rec_lbl.setStyleSheet(f"color: {T['outline']}; font-size: 10px;")
        i1_right.addWidget(act_lbl, alignment=Qt.AlignRight)
        i1_right.addWidget(rec_lbl, alignment=Qt.AlignRight)

        i1_layout.addWidget(i1_icon_frame)
        i1_layout.addSpacing(8)
        i1_layout.addLayout(i1_left)
        i1_layout.addStretch()
        i1_layout.addLayout(i1_right)

        # Item 2 (ETH/USD)
        item2 = QFrame()
        item2.setProperty("class", "market-item")
        item2.setCursor(QCursor(Qt.PointingHandCursor))
        i2_layout = QHBoxLayout(item2)
        i2_layout.setContentsMargins(16, 16, 16, 16)

        i2_icon_frame = QFrame()
        i2_icon_frame.setFixedSize(40, 40)
        i2_icon_frame.setProperty("class", "icon-circle")
        i2_icon_layout = QVBoxLayout(i2_icon_frame)
        i2_icon_layout.setContentsMargins(0, 0, 0, 0)
        i2_icon_lbl = QLabel()
        i2_icon_lbl.setPixmap(
            QIcon(str(load_source("src", "icons", "data_usage.svg"))).pixmap(QSize(24, 24))
        )
        i2_icon_lbl.setAlignment(Qt.AlignCenter)
        i2_icon_layout.addWidget(i2_icon_lbl)

        i2_left = QVBoxLayout()
        lbl3 = QLabel("ETH / USD")
        lbl3.setStyleSheet("font-weight: bold; font-size: 14px;")
        lbl4 = QLabel("Spot Market")
        lbl4.setStyleSheet(f"color: {T['outline']}; font-size: 11px;")
        i2_left.addWidget(lbl3)
        i2_left.addWidget(lbl4)

        add_btn = QPushButton("ADD SYMBOL")
        add_btn.setProperty("class", "btn-text-primary")
        add_btn.setCursor(QCursor(Qt.PointingHandCursor))

        i2_layout.addWidget(i2_icon_frame)
        i2_layout.addSpacing(8)
        i2_layout.addLayout(i2_left)
        i2_layout.addStretch()
        i2_layout.addWidget(add_btn, alignment=Qt.AlignRight)

        grid.addWidget(item1, 0, 0)
        grid.addWidget(item2, 0, 1)
        card.layout.addLayout(grid)

        return card

    def create_browser_card(self):
        card = BentoBox()

        header = QHBoxLayout()
        v_box = QVBoxLayout()
        title = QLabel("Local Market Data Browser")
        title.setProperty("class", "card-title")
        sub = QLabel("Manage and inspect historical data assets stored in the local vault.")
        sub.setStyleSheet(f"color: {T['outline']}; font-size: 12px;")
        v_box.addWidget(title)
        v_box.addWidget(sub)

        header.addLayout(v_box)
        header.addStretch()

        btn_search = QPushButton("")
        icon_path = str(load_source("src", "icons", "search.svg"))
        btn_search.setProperty("class", "btn-icon")
        btn_search.setIcon(QIcon(icon_path))
        btn_search.setIconSize(QSize(20, 20))
        btn_search.setCursor(Qt.PointingHandCursor)
        btn_filter = QPushButton("")
        btn_filter.setProperty("class", "btn-icon")
        icon_path = str(load_source("src", "icons", "filter_list.svg"))
        btn_filter.setIcon(QIcon(icon_path))
        btn_filter.setIconSize(QSize(20, 20))
        btn_filter.setCursor(Qt.PointingHandCursor)
        header.addWidget(btn_search)
        header.addWidget(btn_filter)
        card.layout.addLayout(header)

        # 伪装的流式表格容器
        self.table_container = QVBoxLayout()
        self.table_container.setSpacing(0)

        t_header = QFrame()
        t_header.setProperty("class", "custom-table-header")
        t_header_layout = QHBoxLayout(t_header)
        t_header_layout.setContentsMargins(16, 12, 16, 12)

        def make_h_lbl(text):
            lbl = QLabel(text)
            lbl.setProperty("class", "table-header-text")
            return lbl

        h1, h2, h3, h4 = make_h_lbl("Ticker / Asset"), make_h_lbl("Data Type"),\
            make_h_lbl("Time Range"), make_h_lbl("Actions")
        h4.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        t_header_layout.addWidget(h1, stretch=3)
        t_header_layout.addWidget(h2, stretch=2)
        t_header_layout.addWidget(h3, stretch=3)
        t_header_layout.addWidget(h4, stretch=2)
        self.table_container.addWidget(t_header)

        rows =[
            ("AAPL", "NASDAQ / EQUITY", "L2 QUOTES", "tag-hollow-secondary",
             "2023-11-20 09:30:00", "2023-11-20 16:00:00"),
            ("TSLA", "NASDAQ / EQUITY", "TRADES", "tag-hollow-primary",
             "2023-11-20 09:30:00", "2023-11-20 16:00:00"),
            ("NVDA", "NASDAQ / EQUITY", "L2 QUOTES", "tag-hollow-secondary",
             "2023-11-19 14:00:00", "2023-11-19 16:00:00"),
        ]

        """000001.SZ	SZSE / EQUITY	深圳交易所 A 股
        600519.SH	SSE / EQUITY	上海交易所 A 股
        830832.BJ	BSE / EQUITY	北京交易所 A 股
        0700.HK	HKEX / EQUITY	香港交易所 港股
        """
        self.create_browser_row(self.table_container, rows)

        card.layout.addLayout(self.table_container)

        load_btn = QPushButton("LOAD MORE ARCHIVED FILES")
        load_btn.setProperty("class", "btn-outline")
        load_btn.setCursor(QCursor(Qt.PointingHandCursor))
        card.layout.addWidget(load_btn)

        return card

    def create_browser_row(self, container, data):
        for item in self.tmp_rows:
            container.removeWidget(item)
            item.hide()
            item.deleteLater()

        self.tmp_rows = []

        for d in data:
            ticker, asset_class, dtype, tag_cls, t_start, t_end = d

            row_frame = QFrame()
            row_frame.setProperty("class", "custom-table-row")
            row_frame.setFixedHeight(72)
            row_layout = QHBoxLayout(row_frame)
            row_layout.setContentsMargins(16, 8, 16, 8)

            # 1. Ticker / Asset
            c0_layout = QHBoxLayout()
            c0_layout.setSpacing(12)
            icon_frame = QFrame()
            icon_frame.setFixedSize(32, 32)
            icon_frame.setProperty("class", "icon-circle-small")
            icon_layout = QVBoxLayout(icon_frame)
            icon_layout.setContentsMargins(0, 0, 0, 0)
            icon_lbl = QLabel()
            icon_lbl.setPixmap(
                QIcon(str(load_source("src", "icons", "show_chart.svg"))).pixmap(QSize(18, 18))
            )
            icon_lbl.setAlignment(Qt.AlignCenter)
            icon_layout.addWidget(icon_lbl)

            text_layout = QVBoxLayout()
            text_layout.setSpacing(2)
            text_layout.setAlignment(Qt.AlignVCenter)
            lbl_ticker = QLabel(ticker)
            lbl_ticker.setStyleSheet(f"font-weight: bold; font-size: 14px; color: {T['text']};")
            lbl_asset = QLabel(asset_class)
            lbl_asset.setStyleSheet(f"font-size: 10px; color: {T['outline']}; font-weight: bold;")
            text_layout.addWidget(lbl_ticker)
            text_layout.addWidget(lbl_asset)

            c0_layout.addWidget(icon_frame)
            c0_layout.addLayout(text_layout)
            c0_layout.addStretch()

            # 2. Data Type
            c1_layout = QHBoxLayout()
            tag_label = QLabel(dtype)
            tag_label.setProperty("class", tag_cls)
            tag_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            c1_layout.addWidget(tag_label, alignment=Qt.AlignLeft | Qt.AlignVCenter)

            # 3. Time Range
            c2_layout = QVBoxLayout()
            c2_layout.setSpacing(2)
            c2_layout.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
            lbl_start = QLabel(t_start)
            lbl_start.setStyleSheet(f"""
                font-family: 'Consolas', monospace; font-size: 11px; color: {T['text_dim']};
            """)
            lbl_end = QLabel(t_end)
            lbl_end.setStyleSheet(f"""
                font-family: 'Consolas', monospace; font-size: 11px; color: {T['outline']};
            """)
            c2_layout.addWidget(lbl_start)
            c2_layout.addWidget(lbl_end)

            # 4. Actions
            c3_layout = QHBoxLayout()
            inspect_btn = QPushButton("INSPECT")
            inspect_btn.setProperty("class", "btn-action-small")
            inspect_btn.setCursor(QCursor(Qt.PointingHandCursor))
            c3_layout.addStretch()
            c3_layout.addWidget(inspect_btn, alignment=Qt.AlignVCenter)

            row_layout.addLayout(c0_layout, stretch=3)
            row_layout.addLayout(c1_layout, stretch=2)
            row_layout.addLayout(c2_layout, stretch=3)
            row_layout.addLayout(c3_layout, stretch=2)

            container.addWidget(row_frame)
            self.tmp_rows.append(row_frame)

    def create_storage_card(self):
        card = BentoBox("Storage Vault", style_class="bento-box-low")

        content = QFrame()
        c_layout = QVBoxLayout(content)
        c_layout.setContentsMargins(0, 0, 0, 0)
        c_layout.setSpacing(24)

        # 1. 标题与图标行
        info = QHBoxLayout()
        info.setSpacing(12)

        nvme_icon = QLabel()
        nvme_icon.setFixedSize(20, 20) # 修复点：锁死图标尺寸，防止平分空间
        nvme_icon.setPixmap(
            QIcon(str(load_source("src", "icons", "hard_drive.svg"))).pixmap(QSize(20, 20))
        )

        l_name = QLabel("Primary NVMe")
        l_name.setStyleSheet(f"color: {T['text_dim']}; font-size: 14px;")

        l_perc = QLabel("84.2% Full")
        l_perc.setStyleSheet(f"color: {T['text']}; font-weight: bold; font-size: 14px;")

        info.addWidget(nvme_icon)
        info.addWidget(l_name)
        info.addStretch()
        info.addWidget(l_perc)

        # 2. 进度条
        pbar = QProgressBar()
        pbar.setProperty("class", "prog-error")
        pbar.setValue(84)
        pbar.setTextVisible(False)
        pbar.setFixedHeight(6)

        # 3. 警告框区域
        warn_container = QFrame()
        warn_container.setProperty("class", "warning-box")
        w_layout = QVBoxLayout(warn_container)
        w_layout.setContentsMargins(16, 16, 16, 16)
        w_layout.setSpacing(12)

        # ⚠️ 修复布局平均分配问题
        warn_row = QHBoxLayout()
        warn_row.setSpacing(12)

        warn_icon = QLabel()
        warn_icon.setFixedSize(16, 16) # 修复点：锁死图标最大尺寸
        warn_icon.setPixmap(
            QIcon(str(load_source("src", "icons", "warning.svg"))).pixmap(QSize(16, 16))
        )

        warn_text = QLabel(f"""
            Space is critical. Auto-archiving to AWS S3 Glacier will trigger in \
            <span style='color: {T['error']}; font-weight: bold;'>12.4 GB</span>.
        """)
        warn_text.setStyleSheet(f"color: {T['text_dim']}; font-size: 11px; line-height: 1.5;")
        warn_text.setWordWrap(True)
        warn_text.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Preferred
        ) # 修复点：允许文本区域扩充

        # 修复点：通过 stretch 参数告诉 Qt：图标占 0，文字占 1（即文字占满剩余所有宽度）
        warn_row.addWidget(warn_icon, stretch=0, alignment=Qt.AlignTop)
        warn_row.addWidget(warn_text, stretch=1, alignment=Qt.AlignTop)

        purge_btn = QPushButton("PURGE OLDER LOGS")
        purge_btn.setStyleSheet(f"""
            QPushButton {{
                color: {T['primary']};
                background: {T['primary_bg']};
                border: 1px solid {T['primary']}33;
                padding: 10px;
                font-size: 12px;
                font-weight: bold;
                border-radius: 6px;
            }}
            QPushButton:hover {{
                background: {T['primary']}33;
            }}
        """)
        purge_btn.setCursor(QCursor(Qt.PointingHandCursor))

        w_layout.addLayout(warn_row)
        w_layout.addWidget(purge_btn)

        c_layout.addLayout(info)
        c_layout.addWidget(pbar)
        c_layout.addWidget(warn_container)

        card.layout.addWidget(content)
        card.layout.addStretch()
        return card

    def create_capture_stream_card(self):
        card = BentoBox("Capture Stream", style_class="bento-box-low")

        log_area = QVBoxLayout()
        # 修复点 1：增大行与行之间的间距 (对应 Tailwind 的 space-y-4)
        log_area.setSpacing(16)

        # 修复点 3：增加第五行数据（复制第四行）
        logs =[
            ("14:02:11.233", "TICK BTC/USD 64,221.40", "+0.4", "log-row-primary",
             T['primary'], T['emerald']),
            ("14:02:11.198", "BOOK BTC/USD L2_UPDATE", "42_MS", "log-row-dim",
             T['tertiary'], T['text_dim']),
            ("14:02:11.102", "BOOK BTC/USD L2_UPDATE", "11_MS", "log-row-dim",
             T['tertiary'], T['text_dim']),
            ("14:02:10.982", "TICK BTC/USD 64,221.00", "-1.2", "log-row-dim",
             T['primary'], T['error']),
            ("14:02:10.982", "TICK BTC/USD 64,221.00", "-1.2", "log-row-dim",
             T['primary'], T['error'])
        ]

        for ts, msg, val, row_cls, msg_color, val_color in logs:
            row_frame = QFrame()
            # 强化：强制启用 StyledPanel，确保 QSS 的左边框完美渲染
            row_frame.setFrameShape(QFrame.StyledPanel)
            row_frame.setProperty("class", row_cls)

            row = QHBoxLayout(row_frame)
            # 修复点 2：左侧留出 12px 内边距 (对应 pl-3)，上下留出 4px (对应 py-1)
            row.setContentsMargins(12, 4, 0, 4)

            t_lbl = QLabel(ts)
            t_lbl.setProperty("class", "log-time")

            m_lbl = QLabel(msg)
            m_lbl.setProperty("class", "log-text")
            m_lbl.setStyleSheet(f"color: {msg_color};")

            v_lbl = QLabel(val)
            v_lbl.setProperty("class", "log-text")
            v_lbl.setStyleSheet(f"color: {val_color};")

            # 完美模拟 justify-between，将三个元素等距排开
            row.addWidget(t_lbl)
            row.addStretch(1)
            row.addWidget(m_lbl, alignment=Qt.AlignCenter)
            row.addStretch(1)
            row.addWidget(v_lbl, alignment=Qt.AlignRight)

            log_area.addWidget(row_frame)

        card.layout.addLayout(log_area)

        view_btn = QPushButton("VIEW FULL LOG CLOUD")
        view_btn.setProperty("class", "btn-action-small")
        view_btn.setCursor(QCursor(Qt.PointingHandCursor))
        card.layout.addWidget(view_btn)

        card.layout.addStretch()
        return card

    def update_browser(self, data):
        """"""
        self.create_browser_row(self.table_container, data)

    def showEvent(self, event):
        super().showEvent(event)
        self.loader.start()

    def open_download_dialog(self):
        dialog = DataAcquisitionDialog(self)
        if dialog.exec():
            configuration = dialog.get_configuration()
            sync_data(symbol=configuration["symbol"])
        else:
            pass


class DataLoaderThread(QThread):
    data_loaded = Signal(list)

    def run(self):
        try:
            results = get_overview()
            formatted_results = []
            for r in results:
                formatted_results.append([
                    r["symbol"], f"{r["exchange"]} / EQUITY", "Bar 1min",
                    "tag-hollow-secondary", r["start_dt_str"],
                    r["end_dt_str"]
                ])
            self.data_loaded.emit(formatted_results)
        except Exception as e:
            logger.error(f"Failed to load database overview: {e}")
