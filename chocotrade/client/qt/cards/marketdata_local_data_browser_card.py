
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QCursor, QIcon
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
)

from ....utilities import _, load_source

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


class MarketDataBrowserCard(BentoBox):
    """"""
    def __init__(self):
        super().__init__()
        self.tmp_rows = []

        header = QHBoxLayout()
        v_box = QVBoxLayout()
        title = QLabel(_("Local Market Data Browser"))
        title.setProperty("class", "card-title")
        sub = QLabel(_("Manage and inspect historical data assets stored in the local vault."))
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
        self.layout.addLayout(header)

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
        self.create_browser_row(rows)

        self.layout.addLayout(self.table_container)

        load_btn = QPushButton("LOAD MORE ARCHIVED FILES")
        load_btn.setProperty("class", "btn-outline")
        load_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.layout.addWidget(load_btn)

    def create_browser_row(self, data):
        for item in self.tmp_rows:
            self.table_container.removeWidget(item)
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
            inspect_btn = QPushButton(_("INSPECT"))
            inspect_btn.setProperty("class", "btn-action-small")
            inspect_btn.setCursor(QCursor(Qt.PointingHandCursor))
            c3_layout.addStretch()
            c3_layout.addWidget(inspect_btn, alignment=Qt.AlignVCenter)

            row_layout.addLayout(c0_layout, stretch=3)
            row_layout.addLayout(c1_layout, stretch=2)
            row_layout.addLayout(c2_layout, stretch=3)
            row_layout.addLayout(c3_layout, stretch=2)

            self.table_container.addWidget(row_frame)
            self.tmp_rows.append(row_frame)
