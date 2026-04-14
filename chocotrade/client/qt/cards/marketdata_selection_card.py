
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QCursor, QIcon
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
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


class MarketDataSelectionCard(BentoBox):
    """"""
    def __init__(self):
        super().__init__(style_class="bento-box-low")

        header = QHBoxLayout()
        title = QLabel(_("Target Market Selection"))
        title.setProperty("class", "card-title")
        header.addWidget(title)
        header.addStretch()

        tag1 = QLabel(_("EXCHANGE: COINBASE_PRO"))
        tag1.setProperty("class", "tag-tertiary")
        tag2 = QLabel(_("TYPE: SPOT"))
        tag2.setProperty("class", "tag-tertiary")
        header.addWidget(tag1)
        header.addWidget(tag2)
        self.layout.addLayout(header)

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
        self.layout.addLayout(grid)
