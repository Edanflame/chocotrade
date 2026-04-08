
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QCursor, QIcon
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
)

from ....utilities import load_source
from ...client import start_record, stop_record

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


class MarketDataActivateCard(BentoBox):
    """"""
    def __init__(self):
        super().__init__(title="Active Recording Session", style_class="bento-box-active")
        self.is_paused = True
        self.is_terminated = True

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
        self.layout.addLayout(stats_layout)

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
        self.layout.addLayout(prog_box)

        btn_layout = QHBoxLayout()
        self.stop_btn = QPushButton("Activate Session")
        self.stop_btn.setIcon(
            QIcon(str(load_source("src", "icons", "play_dark.svg"))).pixmap(QSize(30, 30))
        )
        self.stop_btn.setProperty("class", "btn-primary")
        self.stop_btn.setFixedWidth(200)
        self.stop_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.stop_btn.clicked.connect(self.toggle_stop)

        self.pause_btn = QPushButton("Resume Stream")
        self.pause_btn.setIcon(
            QIcon(str(load_source("src", "icons", "play.svg"))).pixmap(QSize(30, 30))
        )
        self.pause_btn.setProperty("class", "btn-secondary")
        self.pause_btn.setFixedWidth(180)
        self.pause_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.pause_btn.clicked.connect(self.toggle_pause)

        export_btn = QPushButton("Export Partial")
        export_btn.setIcon(
            QIcon(str(load_source("src", "icons", "download.svg"))).pixmap(QSize(30, 30))
        )
        export_btn.setProperty("class", "btn-ghost")
        export_btn.setCursor(QCursor(Qt.PointingHandCursor))

        btn_layout.addWidget(self.stop_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self.pause_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(export_btn)

        self.layout.addLayout(btn_layout)

    def toggle_pause(self):
        if self.is_terminated:
            return

        self.is_paused = not self.is_paused
        if self.is_paused:
            self.pause_btn.setText("Resume Stream")
            self.pause_btn.setIcon(
                QIcon(str(load_source("src", "icons", "play.svg"))).pixmap(QSize(30, 30))
            )
        else:
            self.pause_btn.setText("Pause Stream")
            self.pause_btn.setIcon(
                QIcon(str(load_source("src", "icons", "pause.svg"))).pixmap(QSize(30, 30))
            )

    def toggle_stop(self):
        self.is_terminated = not self.is_terminated
        if self.is_terminated:
            self.stop_btn.setText("Activate  Session")
            self.stop_btn.setIcon(
                QIcon(str(load_source("src", "icons", "play_dark.svg"))).pixmap(QSize(30, 30))
            )
            stop_record()

            self.is_paused = True
            self.pause_btn.setText("Resume Stream")
            self.pause_btn.setIcon(
                QIcon(str(load_source("src", "icons", "play.svg"))).pixmap(QSize(30, 30))
            )
        else:
            self.stop_btn.setText("Terminate Session")
            self.stop_btn.setIcon(
                QIcon(str(load_source("src", "icons", "stop_dark.svg"))).pixmap(QSize(30, 30))
            )
            start_record()

            self.is_paused = False
            self.pause_btn.setText("Pause Stream")
            self.pause_btn.setIcon(
                QIcon(str(load_source("src", "icons", "pause.svg"))).pixmap(QSize(30, 30))
            )
