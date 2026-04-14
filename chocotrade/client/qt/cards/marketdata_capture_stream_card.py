
from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from ....utilities import _

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


class MarketDataCaptreStreamCard(BentoBox):
    """"""
    def __init__(self):
        super().__init__(title=_("Capture Stream"), style_class="bento-box-low")
        self.tmp_rows = []

        self.log_area = QVBoxLayout()
        # 修复点 1：增大行与行之间的间距 (对应 Tailwind 的 space-y-4)
        self.log_area.setSpacing(16)

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
        self.create_stream_row(logs)

        self.layout.addLayout(self.log_area)

        view_btn = QPushButton(_("VIEW FULL LOG CLOUD"))
        view_btn.setProperty("class", "btn-action-small")
        view_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.layout.addWidget(view_btn)

        self.layout.addStretch()

    def create_stream_row(self, logs):
        """"""
        for item in self.tmp_rows:
            self.log_area.removeWidget(item)
            item.hide()
            item.deleteLater()

        self.tmp_rows = []

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

            self.log_area.addWidget(row_frame)
            self.tmp_rows.append(row_frame)
