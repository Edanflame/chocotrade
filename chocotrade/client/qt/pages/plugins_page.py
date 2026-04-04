import sys

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from ....utilities import load_source
from ...client import save_config
from ..dialogs.plugin_config_dialog import PluginConfigDialog

# ==========================================
# 提取自 Tailwind Config 的全局颜色方案
# ==========================================
COLORS = {
    "background": "#181210",
    "surface": "#181210",
    "surface_container": "#251e1c",
    "surface_container_low": "#201a18",
    "surface_container_highest": "#3b3331",
    "primary": "#e9c349",
    "on_primary": "#3c2f00",
    "primary_container": "#3b2d00",
    "on_primary_container": "#b59319",
    "secondary": "#f9ba82",
    "tertiary": "#d5c5a8",
    "on_surface": "#ede0dc",
    "on_surface_variant": "#d2c4bc",
    "outline_variant": "#4f453f",
    "error": "#ffb4ab",
    "success": "#4ade80"
}

SCROLLBAR_STYLE = f"""
    QScrollBar:vertical {{
        border: none; background: {COLORS['background']}; width: 8px; margin: 0px;
    }}
    QScrollBar::handle:vertical {{
        background: {COLORS['surface_container_highest']}; border-radius: 4px;
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        border: none; background: none;
    }}
"""

PLUGINS = {
    "Tushare Interface": {
        "name": "tushare",
        "desc": "Professional data gateway for Chinese A-shares, funds, and derivatives markets.",
        "category": "database",
        "star": "5",
        "download": "100",
        "is_new": False,
        "auth_fields": ["api_token"]
    },
    "Okx Execution Gateway": {
        "name": "okx",
        "desc": "Direct market access through proprietary low-latency\
            WebSocket and REST interfaces.",
        "category": "hub",
        "star": "5",
        "download": "100",
        "is_new": False,
        "auth_fields": []
    },
    "Standard LLM Interface": {
        "name": "standard-llm",
        "desc": "Universal LLM connector compatible with OpenAI-style APIs,\
            supporting custom endpoints and model selection.",
        "category": "robot",
        "star": "5",
        "download": "500",
        "is_new": True,
        "auth_fields": ["base_url", "model_name", "api_key"]
    },
    "TimescaleDB Interface": {
        "name": "timescaledb",
        "desc": "High-performance time-series database optimization for\
            tick-level data storage and retrieval.",
        "category": "database",
        "star": "5",
        "download": "100",
        "is_new": False,
        "auth_fields": []
    },
    "Redis Latency Buffer": {
        "name": "redis",
        "desc": "In-memory data structure store for rapid order execution feedback loops.",
        "category": "memory",
        "star": "4.9",
        "download": "1.2k",
        "is_new": True,
        "auth_fields": []
    },
    "AWS S3 Cold Storage": {
        "name": "aws_s3",
        "desc": "Automated archiving of historical trading data and\
            backtest results to the cloud.",
        "category": "cloud_upload",
        "star": "4.7",
        "download": "842",
        "is_new": False,
        "auth_fields": []
    },
    "Vault Sentinel Bot": {
        "name": "sentinel_bot",
        "desc": "Receive real-time alerts and manage active positions\
            via Telegram's secure interface.",
        "category": "send",
        "star": "5.0",
        "download": "2.1k",
        "is_new": False,
        "auth_fields": []
    },
    "Polygon.io Stream": {
        "name": "polygon",
        "desc": "Institutional-grade market data feed for equities, forex, and crypto markets.",
        "category": "timeline",
        "star": "4.8",
        "download": "1.5k",
        "is_new": False,
        "auth_fields": []
    }
}


# 已激活插件卡片组件
class ActivePluginCard(QFrame):
    # def __init__(self, config, title, desc, icon_name, is_active=True, parent=None):
    def __init__(self, title, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.title = title
        desc = config["desc"]
        icon_name = config["category"]
        is_active = True

        self.setObjectName("ActiveCard")
        self.setStyleSheet(f"""
            /* 外层卡片本身的样式 (使用 # 限定) */
            QFrame#ActiveCard {{
                background-color: {COLORS['surface_container']};
                border-radius: 12px;
                border: 1px solid transparent;
            }}
            QFrame#ActiveCard:hover {{
                border: 1px solid rgba(233, 195, 73, 0.2);
            }}

            /* icon_frame 的样式 (使用 class 属性限定) */
            QFrame[class="IconFrameClass"] {{
                background-color: rgba(104, 61, 15, 0.3);
                border-radius: 10px;
            }}
        """)
        self.setFixedHeight(230)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)

        # 头部：图标 + 状态
        header = QHBoxLayout()

        # 使用真实的 SVG 图标
        icon_frame = QFrame()
        icon_frame.setFixedSize(48, 48)
        icon_frame.setStyleSheet("background: rgba(104, 61, 15, 0.3); border-radius: 10px;")
        icon_layout = QVBoxLayout(icon_frame)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_lbl = QLabel()
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_lbl.setPixmap(
            QIcon(str(load_source("src", "icons", f"{icon_name}.svg"))).pixmap(24, 24)
        )
        icon_layout.addWidget(icon_lbl)

        status_text = "CONNECTED" if is_active else "ACTIVE"
        status_lbl = QLabel(f"● {status_text}")
        status_lbl.setStyleSheet(f"""
            color: {COLORS['success']};
            font-size: 10px; font-weight: bold;
            background: {COLORS['surface_container_highest']};
            padding: 6px 12px; border-radius: 12px; letter-spacing: 1px;
        """)

        header.addWidget(icon_frame)
        header.addStretch()
        header.addWidget(status_lbl, alignment=Qt.AlignTop)

        # 文本
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(f"""
            font-size: 18px; font-weight: bold; color: {COLORS['on_surface']};
            font-family: 'Manrope', sans-serif; margin-top: 10px;
            background-color: {COLORS['surface_container']}
        """)

        desc_lbl = QLabel(desc)
        desc_lbl.setWordWrap(True)
        desc_lbl.setStyleSheet(f"""
            color: {COLORS['on_surface_variant']}; font-size: 13px;
            line-height: 1.5; background-color: {COLORS['surface_container']}
        """)

        # 按钮
        btn_layout = QHBoxLayout()
        self.btn_config = QPushButton("Configure")
        self.btn_config.setCursor(Qt.PointingHandCursor)
        self.btn_config.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS['surface_container_highest']};
                color: {COLORS['primary']}; font-weight: bold;
                border-radius: 6px; padding: 10px; font-size: 13px;
            }}
            QPushButton:hover {{ background: {COLORS['primary']}; color: {COLORS['on_primary']}; }}
        """)
        self.btn_config.clicked.connect(self.open_config)

        btn_power = QPushButton()
        btn_power.setIcon(QIcon(str(load_source("src", "icons", "power_settings_new.svg"))))
        btn_power.setIconSize(QSize(20, 20))
        btn_power.setFixedSize(40, 40)
        btn_power.setCursor(Qt.PointingHandCursor)
        btn_power.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS['surface_container_highest']}; border-radius: 6px;
            }}
            QPushButton:hover {{ background: {COLORS['error']}; }}
        """)

        btn_layout.addWidget(self.btn_config)
        btn_layout.addWidget(btn_power)

        layout.addLayout(header)
        layout.addWidget(title_lbl)
        layout.addWidget(desc_lbl)
        layout.addStretch()
        layout.addLayout(btn_layout)

    def open_config(self):
        dialog = PluginConfigDialog(self.title, self.config, self)
        if dialog.exec():
            configuration = dialog.get_configuration()
            print(configuration)
            save_config(category="robot", name="standard-llm", config=configuration)
        else:
            pass


# 可用插件卡片组件
class AvailablePluginCard(QFrame):
    def __init__(self, title, desc, icon_name, rating, downloads, is_new=False, parent=None):
        super().__init__(parent)
        self.setObjectName("ActiveCard")
        self.setStyleSheet(f"""
            /* 外层卡片本身的样式 (使用 # 限定) */
            QFrame#ActiveCard {{
                background-color: {COLORS['surface_container']};
                border-radius: 12px;
                border: 1px solid transparent;
            }}
            QFrame#ActiveCard:hover {{
                border: 1px solid rgba(233, 195, 73, 0.2);
            }}

            /* icon_frame 的样式 (使用 class 属性限定) */
            QFrame[class="IconFrameClass"] {{
                background-color: rgba(104, 61, 15, 0.3);
                border-radius: 10px;
            }}
        """)
        self.setFixedHeight(140)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        # 左侧图标
        icon_frame = QFrame()
        icon_frame.setFixedSize(80, 80)
        icon_frame.setStyleSheet(f"""
            background: {COLORS['surface_container_highest']}; border-radius: 12px;
        """)
        icon_layout = QVBoxLayout(icon_frame)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_lbl = QLabel()
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_lbl.setPixmap(
            QIcon(str(load_source("src", "icons", f"{icon_name}.svg"))).pixmap(32, 32)
        )
        icon_layout.addWidget(icon_lbl)

        # 右侧内容
        right_layout = QVBoxLayout()
        right_layout.setSpacing(4)

        title_row = QHBoxLayout()
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(f"""
            font-size: 17px; font-weight: bold;
            font-family: 'Manrope', sans-serif;
            background-color: {COLORS['surface_container']};
        """)
        title_row.addWidget(title_lbl)

        title_row.addStretch()

        if is_new:
            badge = QLabel("NEW")
            badge.setStyleSheet(f"""
                background: {COLORS['primary_container']};
                color: {COLORS['on_primary_container']};
                font-size: 10px; font-weight: bold; padding: 2px 6px;
                border-radius: 4px; letter-spacing: 1px;
            """)
            title_row.addWidget(badge)
            title_row.addWidget(badge, alignment=Qt.AlignTop)

        desc_lbl = QLabel(desc)
        desc_lbl.setWordWrap(True)
        desc_lbl.setStyleSheet(f"""
            color: {COLORS['on_surface_variant']};
            font-size: 13px;
            background-color: {COLORS['surface_container']};
        """)

        # 底部数据与按钮
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(12)

        # Rating 区域 (星型图标 + 文本)
        stat_rating = QHBoxLayout()
        star_icon = QLabel()
        star_icon.setPixmap(QIcon(str(load_source("src", "icons", "star.svg"))).pixmap(12, 12))
        star_icon.setStyleSheet(f"background-color: {COLORS['surface_container']};")
        lbl_rating = QLabel(rating)
        lbl_rating.setStyleSheet(f"""
            color: {COLORS['tertiary']}; font-size: 12px;
            background-color: {COLORS['surface_container']};
        """)
        stat_rating.addWidget(star_icon)
        stat_rating.addWidget(lbl_rating)

        # Download 区域 (下载图标 + 文本)
        stat_download = QHBoxLayout()
        dl_icon = QLabel()
        dl_icon.setPixmap(QIcon(str(load_source("src", "icons", "download.svg"))).pixmap(12, 12))
        dl_icon.setStyleSheet(f"background-color: {COLORS['surface_container']};")
        lbl_dl = QLabel(downloads)
        lbl_dl.setStyleSheet(f"""
            color: {COLORS['tertiary']}; font-size: 12px;
            background-color: {COLORS['surface_container']};
        """)
        stat_download.addWidget(dl_icon)
        stat_download.addWidget(lbl_dl)

        btn_add = QPushButton(" Add to Vault")
        btn_add.setIcon(QIcon(str(load_source("src", "icons", "add_circle.svg"))))
        btn_add.setCursor(Qt.PointingHandCursor)
        btn_add.setStyleSheet(f"""
            color: {COLORS['primary']}; font-weight: bold;
            border: none; background: transparent; font-size: 13px;
        """)

        bottom_layout.addLayout(stat_rating)
        bottom_layout.addLayout(stat_download)
        bottom_layout.addStretch()
        bottom_layout.addWidget(btn_add)

        right_layout.addLayout(title_row)
        right_layout.addWidget(desc_lbl)
        right_layout.addStretch()
        right_layout.addLayout(bottom_layout)

        layout.addWidget(icon_frame)
        layout.addLayout(right_layout)


# ==========================================
# 4. 主区域 Widget
# ==========================================
class PluginManagementWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['background']};
                color: {COLORS['on_surface']}; font-family: 'Inter', sans-serif;
            }}
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 核心滚动区
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setStyleSheet(SCROLLBAR_STYLE)

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(35, 35, 35, 35)
        content_layout.setSpacing(24)

        # --- 页面 Header ---
        header_layout = QHBoxLayout()

        header_text_vbox = QVBoxLayout()
        title_lbl = QLabel("Plugin Management")
        title_lbl.setStyleSheet("""
            font-size: 36px; font-weight: 800; font-family: 'Manrope', sans-serif;
            margin-bottom: 8px; letter-spacing: -0.5px;
        """)
        desc_lbl = QLabel("Extend the vault's capabilities. Connect to secure data interfaces,\
            scale with enterprise databases, and bridge execution through global gateways.")
        desc_lbl.setStyleSheet(f"""
            color: {COLORS['on_surface_variant']}; font-size: 15px; max-width: 600px;
        """)
        desc_lbl.setWordWrap(True)

        header_text_vbox.addWidget(title_lbl)
        header_text_vbox.addWidget(desc_lbl)

        btn_upload = QPushButton(" Upload Plugin")
        btn_upload.setIcon(QIcon(str(load_source("src", "icons", "upload_file.svg"))))
        btn_upload.setCursor(Qt.PointingHandCursor)
        btn_upload.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['surface_container_highest']};
                color: {COLORS['tertiary']}; padding: 10px 20px;
                border-radius: 8px; font-weight: bold; font-size: 13px;
            }}
            QPushButton:hover {{ background-color: #4a403d; }}
        """)

        header_layout.addLayout(header_text_vbox)
        header_layout.addStretch()
        header_layout.addWidget(btn_upload, alignment=Qt.AlignBottom)

        content_layout.addLayout(header_layout)
        content_layout.addSpacing(10)

        # --- Active Vault Integrations ---
        sec_active = QLabel("Active Vault Integrations")
        sec_active.setStyleSheet(f"""
            color: {COLORS['primary']}; font-size: 20px;
            font-weight: bold; font-family: 'Manrope', sans-serif;
        """)
        content_layout.addWidget(sec_active)

        horizontal_scrollbar_style = f"""
            QScrollBar:horizontal {{
                border: none; background: {COLORS['background']}; height: 8px; margin: 0px;
            }}
            QScrollBar::handle:horizontal {{
                background: {COLORS['surface_container_highest']};
                border-radius: 4px; min-width: 20px;
            }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                border: none; background: none;
            }}
        """
        # 1. 创建滚动区域
        active_scroll = QScrollArea()
        active_scroll.setWidgetResizable(True)
        active_scroll.setFrameShape(QFrame.NoFrame)
        active_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)    # 禁用纵向
        active_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded) # 按需横向
        active_scroll.setStyleSheet(horizontal_scrollbar_style)
        active_scroll.setFixedHeight(300) # 高度略高于卡片高度(230)，给滚动条留位置

        # 2. 创建容器 Widget
        active_container = QWidget()
        active_container.setStyleSheet("background: transparent;")
        active_hbox = QHBoxLayout(active_container)
        active_hbox.setContentsMargins(0, 0, 0, 10) # 底部留一点空间给滚动条
        active_hbox.setSpacing(24)

        # 3. 创建并添加卡片
        # 注意：在横向滚动区域，卡片需要设置固定宽度，否则会被压缩
        def create_scroll_card(title):
            plugin = PLUGINS[title]
            # card = ActivePluginCard(title, plugin["desc"], plugin["category"])
            card = ActivePluginCard(title, plugin)
            card.setFixedWidth(400)  # 设置一个合适的固定宽度
            return card

        active_hbox.addWidget(create_scroll_card("Tushare Interface"))
        active_hbox.addWidget(create_scroll_card("Okx Execution Gateway"))
        active_hbox.addWidget(create_scroll_card("Standard LLM Interface"))
        active_hbox.addWidget(create_scroll_card("TimescaleDB Interface"))

        # 4. 添加弹簧，防止卡片数量少时散开
        active_hbox.addStretch()

        # 5. 装载容器并加入主布局
        active_scroll.setWidget(active_container)
        content_layout.addWidget(active_scroll)

        content_layout.addSpacing(20)

        # --- Available Plugins ---
        sec_avail = QLabel("Available Plugins")
        sec_avail.setStyleSheet(f"""
            color: {COLORS['on_surface']}; font-size: 20px;
            font-weight: bold; font-family: 'Manrope', sans-serif;
        """)
        content_layout.addWidget(sec_avail)

        avail_grid = QGridLayout()
        avail_grid.setSpacing(24)

        # 传入的第三个参数对应 src/icons/xxx.svg 的文件名
        avail_plugins = [
            "Redis Latency Buffer",
            "AWS S3 Cold Storage",
            "Vault Sentinel Bot",
            "Polygon.io Stream"
        ]

        for i, title in enumerate(avail_plugins):
            desc = PLUGINS[title]["desc"]
            category = PLUGINS[title]["category"]
            star = PLUGINS[title]["star"]
            download = PLUGINS[title]["download"]
            is_new = PLUGINS[title]["is_new"]
            avail_grid.addWidget(
                AvailablePluginCard(title, desc, category, star, download, is_new), i // 2, i % 2
            )

        # for i, (t, d, ic, r, dl, is_new) in enumerate(avail_plugins):
        #     avail_grid.addWidget(AvailablePluginCard(t, d, ic, r, dl, is_new), i // 2, i % 2)

        content_layout.addLayout(avail_grid)

        # --- Footer ---
        footer_vbox = QVBoxLayout()
        footer_vbox.setContentsMargins(0, 40, 0, 20)
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("""
            border: none; background-color: rgba(79, 69, 63, 0.2); max-height: 1px;
        """)

        footer_lbl = QLabel("CRAFTED WITH PRECISION IN THE ARTISANAL VAULT")
        footer_lbl.setAlignment(Qt.AlignCenter)
        footer_lbl.setStyleSheet("""
            color: rgba(210, 196, 188, 0.4);
            font-size: 10px; letter-spacing: 4px;
            font-family: 'Manrope', sans-serif; margin-top: 15px;
        """)

        footer_vbox.addWidget(line)
        footer_vbox.addWidget(footer_lbl)

        content_layout.addStretch()
        content_layout.addLayout(footer_vbox)

        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PluginManagementWidget()
    window.setWindowTitle("Plugin Management (Standalone Widget Test)")
    window.resize(1000, 800)
    window.show()
    sys.exit(app.exec())
