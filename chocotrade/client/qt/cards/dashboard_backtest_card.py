from PySide6.QtCore import QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QProgressBar, QVBoxLayout, QWidget

from ....utilities import load_source

# =================================================================
# 样式定义 (QSS)
# =================================================================
BACKTEST_ENGINE_STYLESHEET = """
/* --- 主容器卡片 --- */
#BacktestModule {
    background-color: #251e1c;
    border-radius: 12px;
    border: 1px solid rgba(79, 69, 63, 0.1);
}

/* --- 头部标题和状态 --- */
#ModuleTitle {
    color: #e9c349;
    font-weight: bold;
    font-size: 16px;
}

#JobStatus {
    font-size: 10px;
    font-weight: bold;
    color: #d2c4bc;
    letter-spacing: 1px;
}

/* --- 任务项文字 (BacktestItem) --- */
.ItemName {
    font-weight: bold;
    font-size: 12px;
    color: #ede0dc;
}

.ItemPercent {
    font-size: 11px;
    color: #d2c4bc;
}

/* --- 进度条全局样式 --- */
QProgressBar {
    background-color: #3b3331; /* surface-container-highest */
    border-radius: 4px;
    border: none;
}

QProgressBar::chunk {
    background-color: #e9c349; /* primary gold */
    border-radius: 4px;
}
"""

# =================================================================
# 组件实现
# =================================================================

class BacktestItem(QWidget):
    def __init__(self, name, progress_val):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # 上方文字行
        text_row = QHBoxLayout()

        name_lbl = QLabel(name)
        name_lbl.setProperty("class", "ItemName") # 关联样式

        percent_lbl = QLabel(f"{progress_val}%")
        percent_lbl.setProperty("class", "ItemPercent") # 关联样式

        text_row.addWidget(name_lbl)
        text_row.addStretch()
        text_row.addWidget(percent_lbl)
        layout.addLayout(text_row)

        # 下方进度条
        self.bar = QProgressBar()
        self.bar.setRange(0, 100)
        self.bar.setValue(progress_val)
        self.bar.setTextVisible(False)
        self.bar.setFixedHeight(8)

        layout.addWidget(self.bar)


class BacktestEngineCard(QFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName("BacktestModule")
        # 将样式表应用到主容器
        self.setStyleSheet(BACKTEST_ENGINE_STYLESHEET)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(24)

        # 1. 头部标题栏
        header_layout = QHBoxLayout()

        # 左侧标题
        title_container = QHBoxLayout()
        title_container.setSpacing(10)

        icon_lbl = QLabel()
        icon_lbl.setPixmap(
            QIcon(str(load_source("src", "icons", "science2.svg"))).pixmap(QSize(20, 20))
        )

        title_lbl = QLabel("Backtest Engine")
        title_lbl.setObjectName("ModuleTitle") # 关联样式

        title_container.addWidget(icon_lbl)
        title_container.addWidget(title_lbl)

        # 右侧状态标签
        status_lbl = QLabel("2 ACTIVE JOBS")
        status_lbl.setObjectName("JobStatus") # 关联样式

        header_layout.addLayout(title_container)
        header_layout.addStretch()
        header_layout.addWidget(status_lbl)

        layout.addLayout(header_layout)

        # 2. 进度条列表
        list_layout = QVBoxLayout()
        list_layout.setSpacing(24)

        # 模拟数据填充
        list_layout.addWidget(BacktestItem("Deep Liquidity V3 (BTC/USD)", 82))
        list_layout.addWidget(BacktestItem("Trend Following Stress Test", 34))

        layout.addLayout(list_layout)

        # 填充底部空间
        layout.addStretch()
