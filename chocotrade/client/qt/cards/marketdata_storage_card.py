
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QCursor, QIcon
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
)

from ....utilities import load_source

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


class MarketDataStorageCard(BentoBox):
    """"""
    def __init__(self):
        super().__init__(title="Storage Vault", style_class="bento-box-low")

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

        self.layout.addWidget(content)
        self.layout.addStretch()
