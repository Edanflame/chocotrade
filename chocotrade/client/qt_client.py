import sys

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from ..utilities import load_source
from .qt.pages.backtest_page import BacktestPage
from .qt.pages.dashboard_page import DashboardPage
from .qt.pages.marketdata_page import MarketDataPage
from .qt.pages.plugins_page import PluginManagementWidget as PluginsPage

# --- 1. 配置与常量 ---
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

# =================================================================
# 统一样式定义 (QSS)
# =================================================================
STYLESHEET = f"""
QMainWindow {{
    background-color: {COLORS['background']};
}}

QWidget {{
    color: {COLORS['on_surface']};
    font-family: '.AppleSystemUIFont', 'Helvetica Neue', 'Arial', sans-serif;
}}

/* ---------------- 顶栏样式 ---------------- */
#TopBar {{
    background-color: #120d0c;
    border-bottom: 1px solid {COLORS['outline']};
}}

#Logo {{
    color: {COLORS['primary']};
    font-weight: bold;
    font-size: 18px;
}}

#PageTitle {{
    color: {COLORS['primary']};
    font-weight: 800;
    font-size: 15px;
    text-transform: uppercase;
    letter-spacing: 1px;
}}

#TopSearch {{
    background: {COLORS['surface_high']};
    border: 1px solid {COLORS['outline']};
    border-radius: 6px;
    padding: 5px 15px;
    color: white;
}}

.TopIconButton {{
    background: transparent;
    color: {COLORS['tertiary']};
    font-weight: 600;
    border: none;
}}
.TopIconButton:hover {{
    background-color: {COLORS['surface']};
    border-radius: 4px;
}}

#Avatar {{
    background: {COLORS['primary']};
    border-radius: 16px;
}}

/* ---------------- 侧边栏样式 ---------------- */
#SideBar {{
    background-color: {COLORS['background']};
    border-right: 1px solid {COLORS['outline']};
    min-width: 240px;
}}

#SideBar QPushButton {{
    background-color: transparent;
    border: none;
    color: {COLORS['tertiary']};
    text-align: left;
    padding: 12px 20px;
    border-radius: 4px;
    font-weight: bold;
    font-size: 13px;
    spacing: 10px;
}}

#SideBar QPushButton:hover {{
    background-color: {COLORS['surface']};
    color: {COLORS['primary']};
}}

#SideBar QPushButton[active="true"] {{
    background-color: {COLORS['primary']};
    color: {COLORS['on_primary']};
}}

#SideBar #NewStrategyBtn {{
    background-color: {COLORS['primary']};
    color: {COLORS['on_primary']};
    font-weight: bold;
    padding: 12px;
    border-radius: 4px;
    text-align: center;
}}
#NewStrategyBtn:hover {{
    background-color: #f2e0c3;
}}

/* 底部功能按钮 */
QPushButton.BottomLinkBtn {{
    background-color: transparent;
    color: {COLORS['tertiary']};
    text-align: left;
    padding: 8px 12px;
    border: none;
    font-size: 13px;
}}
QPushButton.BottomLinkBtn:hover {{
    color: {COLORS['primary']};
    background-color: {COLORS['surface_low']};
}}

/* ---------------- 进度条 ---------------- */
QProgressBar {{
    border: none;
    background-color: {COLORS['surface_high']};
    height: 6px;
    border-radius: 3px;
    text-align: center;
    color: transparent;
}}
QProgressBar::chunk {{
    background-color: {COLORS['primary']};
    border-radius: 3px;
}}
"""

# =================================================================
# 布局模块实现
# =================================================================

class TopBar(QFrame):
    """上方导航栏模块"""
    def __init__(self):
        super().__init__()
        self.setObjectName("TopBar")
        self.setFixedHeight(64)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 0, 20, 0)

        # Logo
        logo = QLabel("Chocotrade")
        logo.setObjectName("Logo")
        layout.addWidget(logo)

        # 中间当前页面标题
        layout.addSpacing(40)
        self.page_title_label_texts = [
            "Dashboard", "Plugins", "Strategies", "Backtest", "Market Data"
        ]
        self.page_title_label = QLabel("Dashboard")
        self.page_title_label.setObjectName("PageTitle")
        layout.addWidget(self.page_title_label)

        layout.addStretch()

        # 搜索框
        search = QLineEdit()
        search.setObjectName("TopSearch")
        search.setPlaceholderText("Search parameters...")
        layout.addWidget(search)

        # 功能图标按钮
        for icon in ["notifications", "settings"]:
            btn = QPushButton("")
            btn.setProperty("class", "TopIconButton")
            btn.setIcon(QIcon(str(load_source("src", "icons", f"{icon}2.svg"))))
            btn.setIconSize(QSize(20, 20))
            layout.addWidget(btn)

        # 头像占位
        avatar = QFrame()
        avatar.setObjectName("Avatar")
        avatar.setFixedSize(32, 32)
        layout.addWidget(avatar)

    def update_title(self, index):
        """同步更新页面标题文字"""
        if 0 <= index < len(self.page_title_label_texts):
            self.page_title_label.setText(self.page_title_label_texts[index])


class SideBar(QFrame):
    """左侧侧边栏模块"""
    menu_clicked = Signal(int)

    def __init__(self):
        super().__init__()
        self.setObjectName("SideBar")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 20, 10, 20)

        # 导航组
        self.nav_btns = []
        self.menus = [
            ("dashboard", "Dashboard", 0),
            ("extension", "Plugins", 1),
            ("query_stats", "Strategies", 2),
            ("history_toggle_off", "Backtests", 3),
            ("database", "Market Data", 4),
        ]

        for icon, text, index in self.menus:
            btn = QPushButton(f"    {text}")
            if index == 0:
                btn.setIcon(QIcon(str(load_source("src", "icons", f"{icon}_dark.svg"))))
            else:
                btn.setIcon(QIcon(str(load_source("src", "icons", f"{icon}.svg"))))
            btn.setIconSize(QSize(20, 20))
            # 修改 lambda 确保 index 正确传递，并调用 handle_click 刷新样式
            btn.clicked.connect(lambda checked=False, i=index: self.handle_click(i))

            # 默认第0个激活
            btn.setProperty("active", index == 0)
            layout.addWidget(btn)
            self.nav_btns.append(btn)

        layout.addStretch()

        # 下方工具按钮
        new_btn = QPushButton("NEW STRATEGY")
        new_btn.setObjectName("NewStrategyBtn")
        layout.addWidget(new_btn)

        # 底部链接
        status_btn = QPushButton(" System Status")
        status_btn.setProperty("class", "BottomLinkBtn")
        status_btn.setIcon(QIcon(str(load_source("src", "icons", "sensors2.svg"))))
        layout.addWidget(status_btn)

        logout_btn = QPushButton(" Logout")
        logout_btn.setProperty("class", "BottomLinkBtn")
        logout_btn.setIcon(QIcon(str(load_source("src", "icons", "logout2.svg"))))
        layout.addWidget(logout_btn)

    def handle_click(self, index):
        """处理点击逻辑：更新按钮状态并发送信号"""
        for i, btn in enumerate(self.nav_btns):
            icon_name = self.menus[i][0]
            # 更新 active 属性
            btn.setProperty("active", i == index)

            if i == index:
                btn.setProperty("active", True)
                # 切换为深色图标（例如：dashboard_dark.svg）
                btn.setIcon(QIcon(str(load_source("src", "icons", f"{icon_name}_dark.svg"))))
            else:
                btn.setProperty("active", False)
                # 切换回金色图标
                btn.setIcon(QIcon(str(load_source("src", "icons", f"{icon_name}.svg"))))

            # 强制刷新样式表渲染
            btn.style().unpolish(btn)
            btn.style().polish(btn)

        # 发送切换页面信号
        self.menu_clicked.emit(index)


class StrategiesPage(QWidget):
    def __init__(self):
        super().__init__()
        # 总布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(25)

        h_title = QLabel("StrategiesPage")
        h_title.setStyleSheet("font-size: 32px; font-weight: 800;")
        layout.addWidget(h_title)


# --- 4. 主窗口组装 ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chocotrade v0.1.0")
        self.resize(1280, 850)

        # 核心框架布局
        self.central = QWidget()
        self.setCentralWidget(self.central)
        self.root_layout = QVBoxLayout(self.central)
        self.root_layout.setContentsMargins(0, 0, 0, 0)
        self.root_layout.setSpacing(0)

        # A. 上：顶栏
        self.top_bar = TopBar()
        self.root_layout.addWidget(self.top_bar)

        # 下方区域：左侧栏 + 右侧内容
        self.main_body = QHBoxLayout()
        self.main_body.setSpacing(0)

        # B. 左：侧边栏
        self.side_bar = SideBar()
        self.side_bar.menu_clicked.connect(self.switch_page) # 绑定切换事件
        self.main_body.addWidget(self.side_bar)

        # C. 右：可替换的内容区
        self.content_stack = QStackedWidget()
        self.page_dashboard = DashboardPage()
        self.page_plugins = PluginsPage()
        self.page_strategies = QLabel("<h2>Strategies Page</h2><p>Content to be implemented...</p>")
        self.page_strategies.setAlignment(Qt.AlignCenter)
        self.page_backtest = BacktestPage()
        self.page_marketdata = MarketDataPage()

        self.content_stack.addWidget(self.page_dashboard)
        self.content_stack.addWidget(self.page_plugins)
        self.content_stack.addWidget(self.page_strategies)
        self.content_stack.addWidget(self.page_backtest)
        self.content_stack.addWidget(self.page_marketdata)

        self.main_body.addWidget(self.content_stack)

        self.root_layout.addLayout(self.main_body)

    def switch_page(self, index):
        """切换右侧 StackWidget 的显示内容"""
        if index < self.content_stack.count():
            self.content_stack.setCurrentIndex(index)

            # 更新按钮激活状态
            for i, btn in enumerate(self.side_bar.nav_btns):
                btn.setProperty("active", i == index)

            self.side_bar.style().unpolish(self.side_bar)
            self.side_bar.style().polish(self.side_bar)

        self.top_bar.update_title(index)


def create_qt_client():
    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_DontCreateNativeWidgetSiblings)
    app.setStyleSheet(STYLESHEET)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    create_qt_client()
