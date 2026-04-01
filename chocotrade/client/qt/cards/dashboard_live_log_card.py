import logging
from datetime import datetime

from PySide6.QtCore import QObject, Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QScrollArea, QVBoxLayout, QWidget

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

# LogLine 相关的样式
LOGLINE_STYLES = {
    "mono_font": "font-family: 'Menlo', 'Monaco'; font-size: 11px;",
    "time_lbl": f"color: {COLORS['on_surface_variant']};",
    "level_colors": {
        "INFO": "#4ade80",
        "WARN": "#e9c349",
        "CRIT": "#ffb4ab",
        "ERROR": "#ffb4ab"
    }
}

# ExecutionLogModule 相关的样式
EXECUTION_LOG_MODULE_STYLESHEET = f"""
    #LogModule {{
        background-color: {COLORS['surface_lowest']}; /* surface-container-lowest */
        border: 1px solid rgba(79, 69, 63, 0.2);
        border-radius: 8px;
    }}

    #LogModuleHeader {{
        background-color: {COLORS['surface_high']}; /* surface-container-high */
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
        border-bottom: 1px solid rgba(79, 69, 63, 0.1);
    }}

    #LogModuleHeaderDot {{
        background-color: {COLORS['primary']};
        border-radius: 3px;
    }}

    #LogModuleTitle {{
        color: {COLORS['on_surface']};
        font-size: 10px;
        font-weight: bold;
        letter-spacing: 1px;
    }}

    #LogModuleHint {{
        color: {COLORS['on_surface_variant']};
        font-size: 10px;
    }}
    #LogModuleHint kbd {{
        background-color: {COLORS['background']};
        border: 1px solid {COLORS['outline']};
        border-radius: 3px;
        padding: 1px 4px;
        font-family: 'Menlo', 'Monaco'; /* 保持等宽字体 */
        font-size: 10px; /* 与父级保持一致 */
    }}

    QScrollArea {{ background: transparent; }}
    QScrollBar:vertical {{
        background: transparent;
        width: 5px;
        margin: 0px;
    }}
    QScrollBar::handle:vertical {{
        background: {COLORS['surface_highest']}; /* 滚动条手柄颜色 */
        border-radius: 2px;
        min-height: 20px;
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}

    #LogContentWidget {{ /* content_widget 的 ID */
        background: transparent;
    }}
"""

# =================================================================
# 组件实现
# =================================================================

class LogLine(QWidget):
    def __init__(self, timestamp, level, message):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 2, 0, 2)
        layout.setSpacing(15)

        # 时间戳 [14:05:01]
        time_lbl = QLabel(f"[{timestamp}]")
        time_lbl.setStyleSheet(f"{LOGLINE_STYLES['mono_font']} {LOGLINE_STYLES['time_lbl']}")
        time_lbl.setFixedWidth(70)

        # 级别 [INFO]
        level_color = LOGLINE_STYLES['level_colors'].get(level, COLORS['on_surface'])
        level_lbl = QLabel(f"[{level}]")
        level_lbl.setStyleSheet(f"""
            {LOGLINE_STYLES['mono_font']} color: {level_color};
            font-weight: bold;
        """)
        level_lbl.setFixedWidth(50)

        # 消息正文
        msg_content_color = LOGLINE_STYLES['level_colors'].get(level)\
            if level == "CRIT" else COLORS['on_surface']
        msg_lbl = QLabel(message)
        msg_lbl.setStyleSheet(f"{LOGLINE_STYLES['mono_font']} color: {msg_content_color};")
        msg_lbl.setMinimumWidth(600)
        msg_lbl.setWordWrap(True)

        layout.addWidget(time_lbl)
        layout.addWidget(level_lbl)
        layout.addWidget(msg_lbl)
        layout.addStretch()


class ExecutionLogModule(QFrame):
    def __init__(self):
        super().__init__()
        # 1. 整体容器样式
        self.setObjectName("LogModule")
        self.setStyleSheet(EXECUTION_LOG_MODULE_STYLESHEET) # 应用统一的样式表

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- A. 顶部状态栏 ---
        header = QFrame()
        header.setObjectName("LogModuleHeader") # 设置对象名以便样式表识别
        header.setFixedHeight(32)
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(15, 0, 15, 0)

        # 左侧标题
        title_box = QHBoxLayout()
        title_box.setSpacing(8)

        dot = QFrame()
        dot.setObjectName("LogModuleHeaderDot") # 设置对象名
        dot.setFixedSize(6, 6)

        title_lbl = QLabel("LIVE EXECUTION LOGS")
        title_lbl.setObjectName("LogModuleTitle") # 设置对象名

        title_box.addWidget(dot)
        title_box.addWidget(title_lbl)

        # 右侧快捷键提示 (模拟 <kbd> 标签)
        # 注意：Qt 的 QLabel 不直接支持 HTML <kbd> 标签样式，
        # 需要通过更复杂的 QSS 选择器或分割 QLabel 来模拟
        # 这里的 QSS 对 span 标签的样式处理是在 QLabel 内部进行的。
        hint_lbl = QLabel(f"""
            Press <span style='background:{COLORS['background']};\
            border:1px solid {COLORS['outline']};\
            border-radius:3px; padding:1px 4px; font-family: "Menlo", "Monaco";\
            font-size: 10px;'>ESC</span> to toggle full console
        """)
        hint_lbl.setObjectName("LogModuleHint") # 设置对象名

        h_layout.addLayout(title_box)
        h_layout.addStretch()
        h_layout.addWidget(hint_lbl)
        main_layout.addWidget(header)

        # --- B. 滚动日志区域 ---
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)

        self.content_widget = QWidget()
        self.content_widget.setObjectName("LogContentWidget") # 设置对象名

        self.log_layout = QVBoxLayout(self.content_widget)
        self.log_layout.setContentsMargins(20, 15, 20, 15)
        self.log_layout.setSpacing(4)
        self.log_layout.setAlignment(Qt.AlignTop)

        # 填充初始模拟数据
        self.add_mock_logs()

        self.scroll.setWidget(self.content_widget)
        main_layout.addWidget(self.scroll)

        # 1. 初始化自定义 Handler
        self.log_handler = QtLogHandler()

        # 2. 只有当信号触发时，才调用 add_log 更新 UI
        # 这样可以确保即使日志是在后台线程产生的，UI 也会在主线程安全刷新
        self.log_handler.new_log_signal.connect(self.add_log)

        # 3. 将此 Handler 添加到 logging 系统
        # 你可以绑定到特定的 logger（如 'Frontend'），也可以绑定到 root
        logging.getLogger().addHandler(self.log_handler)
        logging.getLogger().setLevel(logging.INFO) # 设置显示等级

    def add_log(self, timestamp, level, message):
        """动态添加日志的方法"""
        # line = LogLine(timestamp, level, message)
        # self.log_layout.addWidget(line)
        # # 自动滚动到底部
        # self.scroll.verticalScrollBar().setValue(self.scroll.verticalScrollBar().maximum())
        if self.log_layout.count() > 100:
            item = self.log_layout.takeAt(0) # 取出最旧的一条
            if item.widget():
                item.widget().deleteLater()

        line = LogLine(timestamp, level, message)
        self.log_layout.addWidget(line)

        # 自动滚动到底部
        # 使用 QTimer.singleShot 是为了等布局刷新后再执行滚动，定位更准
        from PySide6.QtCore import QTimer
        QTimer.singleShot(50, lambda: self.scroll.verticalScrollBar().setValue(
            self.scroll.verticalScrollBar().maximum()
        ))

    def add_mock_logs(self):
        logs = [
            ("14:05:01", "INFO",
                "Order #882194 executed successfully: BUY 0.25 BTC @ $64,212.00"),
            ("14:04:58", "WARN",
                "Latency spike detected in Gateway-West: 48ms"),
            ("14:04:45", "INFO",
                "Strategy 'Golden Cross HFT' signaled entry on ETH/USDT"),
            ("14:04:12", "CRIT",
                "WebSocket connection lost: Binance-Feed-01. Attempting reconnect (1/5)..."),
            ("14:03:55", "INFO",
                "Backtest job 'Trend Stress Test' initialized on engine-cluster-alpha")
        ]
        for log in logs:
            self.add_log(*log)


class QtLogHandler(logging.Handler, QObject):
    """自定义日志处理器，将日志转发为 Qt 信号"""
    # 信号参数：(时间戳字符串, 日志等级字符串, 消息内容字符串)
    new_log_signal = Signal(str, str, str)

    def __init__(self):
        logging.Handler.__init__(self)
        QObject.__init__(self)

    def emit(self, record):
        # 1. 格式化消息内容
        msg = self.format(record)
        # 2. 提取时间（也可以直接用 record.created）
        timestamp = datetime.fromtimestamp(record.created).strftime("%H:%M:%S")
        # 3. 提取等级 (INFO, WARN, etc.)
        level = record.levelname
        if level == "CRITICAL":
            level = "CRIT" # 对齐你的 LogLine 逻辑
        if level == "WARNING":
            level = "WARN"

        # 4. 发送信号到主线程
        self.new_log_signal.emit(timestamp, level, msg)
