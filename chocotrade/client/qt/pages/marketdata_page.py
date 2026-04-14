import logging

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QColor, QCursor
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from ....utilities import _
from ...client import add_record_symbol, get_overview, get_streaming_record, sync_data
from ..cards.marketdata_active_recoding_card import MarketDataActivateCard
from ..cards.marketdata_capture_stream_card import MarketDataCaptreStreamCard
from ..cards.marketdata_local_data_browser_card import MarketDataBrowserCard
from ..cards.marketdata_selection_card import MarketDataSelectionCard
from ..cards.marketdata_storage_card import MarketDataStorageCard
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


class MarketDataPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setObjectName("MainContainer")
        self.setStyleSheet(GLOBAL_QSS)
        self.setup_ui()

        # 数据加载线程
        self.loader = DataLoaderThread()
        self.loader.data_loaded.connect(self.update_browser)
        self.loader.stream_log_loaded.connect(self.update_stream_log)

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
        left_col.addWidget(MarketDataActivateCard())
        left_col.addWidget(MarketDataSelectionCard())
        self.browser_card = MarketDataBrowserCard()
        left_col.addWidget(self.browser_card)
        left_col.addStretch()

        right_col = QVBoxLayout()
        right_col.setSpacing(24)
        right_col.addWidget(MarketDataStorageCard())
        self.stream_log = MarketDataCaptreStreamCard()
        right_col.addWidget(self.stream_log)
        right_col.addStretch()

        split_layout.addLayout(left_col, stretch=2)
        split_layout.addLayout(right_col, stretch=1)

        self.content_layout.addLayout(split_layout)
        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)

        self.create_fab()

    def create_header(self):
        header = QHBoxLayout()
        v_box = QVBoxLayout()

        title = QLabel(_("Market Data Recorder"))
        title.setProperty("class", "page-title")
        sub = QLabel(_("Capture high-fidelity order book updates and trade \
                     streams into the encrypted vault for post-trade analysis."))
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

        status = QLabel(_("●  RECORDER ENGINE ONLINE"))
        status.setProperty("class", "status-badge")
        b_layout.addWidget(status)

        header.addWidget(badge_container, alignment=Qt.AlignBottom)
        self.content_layout.addLayout(header)

    def create_fab(self):
        """"""
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

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # 计算坐标：窗口总宽/高 减去 按钮宽/高 再减去 48px 的边距 (bottom-12 right-12)
        fab_x = self.width() - self.fab_btn.width() - 48
        fab_y = self.height() - self.fab_btn.height() - 48
        # 将按钮移动到计算好的位置
        self.fab_btn.move(fab_x, fab_y)

    def update_browser(self, data):
        """"""
        self.browser_card.create_browser_row(data)

    def update_stream_log(self, data):
        self.stream_log.create_stream_row(data)

    def showEvent(self, event):
        super().showEvent(event)
        self.loader.start()

    def open_download_dialog(self):
        dialog = DataAcquisitionDialog(self)
        if dialog.exec():
            configuration = dialog.get_configuration()
            print(configuration)
            if "Historical" in configuration["mode"]:
                sync_data(
                    interface=configuration["interface"],
                    symbol=configuration["symbol"],
                    start_time=configuration["start_time"].strftime("%Y-%m-%d %H:%M:%S"),
                    end_time=configuration["end_time"].strftime("%Y-%m-%d %H:%M:%S"),
                    granularity=configuration["granularity"],
                    storage=configuration["storage"]
                )
            elif "Record" in configuration["mode"]:
                add_record_symbol(
                    interface=configuration["interface"],
                    symbol=configuration["symbol"],
                    is_day_record=configuration["is_day_record"],
                    day_record_start_time=configuration["day_record_start_time"].strftime("%H:%M:%S"),
                    day_record_end_time=configuration["day_record_end_time"].strftime("%H:%M:%S"),
                    is_night_record=configuration["is_night_record"],
                    night_record_start_time=configuration["night_record_start_time"].strftime("%H:%M:%S"),
                    night_record_end_time=configuration["night_record_end_time"].strftime("%H:%M:%S"),
                    storage=configuration["storage"]
                )
        else:
            pass


class DataLoaderThread(QThread):
    data_loaded = Signal(list)
    stream_log_loaded = Signal(list)

    def run(self):
        try:
            results = get_overview()
            formatted_results = []
            for r in results:
                if r["type"] == "bar":
                    exchange_type = "Bar 1min"
                elif r["type"] == "tick":
                    exchange_type = "  TICK  "
                else:
                    exchange_type = "        "

                formatted_results.append([
                    r["symbol"], f"{r["exchange"]} / EQUITY", exchange_type,
                    "tag-hollow-secondary", r["start_dt_str"],
                    r["end_dt_str"]
                ])
            self.data_loaded.emit(formatted_results)

            stream_log = get_streaming_record()
            self.stream_log_loaded.emit(stream_log)

        except Exception as e:
            logger.error(f"Failed to load database overview: {e}")
