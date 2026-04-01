import logging
import uuid

from PySide6.QtCore import QObject, Qt, QThread, Signal, Slot
from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QScrollArea, QVBoxLayout, QWidget

from ...client import get_all_backtest_results, run_backtest
from ..cards import BacktestCard, NewTestCard

BACKTEST_PAGE_STYLE = """
/* 页面标题 */
#BacktestTitle {
    color: #e9c349;
    font-size: 36px;
    font-weight: 800;
}

/* 页面描述 */
#BacktestDesc {
    color: #d2c4bc;
    font-size: 14px;
}

/* 滚动区域基础样式 */
QScrollArea {
    background-color: transparent;
    border: none;
}

/* 垂直滚动条 */
QScrollBar:vertical {
    background: transparent;
    width: 8px;
    margin: 0px;
}

/* 滚动条滑块 */
QScrollBar::handle:vertical {
    background: #3b3331; /* surface-highest */
    min-height: 30px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background: #4f453f; /* 悬停颜色 */
}

/* 隐藏滚动条上下箭头 */
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* 加载状态文字 */
#LoadingLabel {
    color: #d2c4bc;
    font-style: italic;
}
"""


logger = logging.getLogger("Frontend")

class BacktestPage(QWidget):
    def __init__(self):
        super().__init__()
        self._is_loaded = False
        self.results = []
        self.new_test_card = None

        # 应用样式
        self.setStyleSheet(BACKTEST_PAGE_STYLE)

        # 总布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(25)

        # 1. 标题头
        header = QVBoxLayout()
        title = QLabel("Backtest Outcomes")
        title.setObjectName("BacktestTitle")

        desc = QLabel(
            "Performance archives from the Velvet Vault engine. Compare historical yields."
        )
        desc.setObjectName("BacktestDesc")

        header.addWidget(title)
        header.addWidget(desc)
        layout.addLayout(header)

        # 2. 滚动区域设置
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # 3. 内部网格容器
        self.scroll_content = QWidget()
        self.scroll_content.setStyleSheet("background-color: transparent;")
        self.grid = QGridLayout(self.scroll_content)
        self.grid.setSpacing(25)
        self.grid.setColumnStretch(0, 1)
        self.grid.setColumnStretch(1, 1)
        self.grid.setColumnStretch(2, 1)

        # 加载初始模拟数据
        self.cards_data = [
            ("Momentum Alpha", "Gold-Runner V4", "Optimized", ["+24.8%", "2.14", "-4.2%"],
                [0.3, 0.5, 0.4, 0.8, 0.4, 0.7, 0.9], {}),
            ("Mean Reversion", "Cocoa Arbitrage", "Legacy", ["+12.4%", "1.65", "-8.1%"],
                [0.6, 0.5, 0.4, 0.5, 0.6, 0.5, 0.4], {}),
            ("Sentiment Engine", "The Velvet Trend", "In-Progress", ["--", "--", "--"],
                [], {}, True),
            ("High Frequency", "Silver-Spike HFT", "Optimized", ["+31.2%", "3.42", "-2.1%"],
                [0.5, 0.6, 0.8, 0.7, 0.9, 1.0, 0.9], {}),
            ("Neutral Grid", "Steady Cream", "Legacy", ["+6.2%", "0.92", "-0.5%"],
                [0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3], {}),
        ]

        self.refresh_grid_layout()

        self.scroll.setWidget(self.scroll_content)
        layout.addWidget(self.scroll)

        # 数据加载线程
        self.loader = DataLoaderThread()
        self.loader.data_loaded.connect(self.populate_cards)

        # 运行回测线程
        self.backtest_manager = BacktestManager()

    def refresh_grid_layout(self):
        """刷新网格中的所有卡片"""
        # 1. 渲染模拟数据或已有数据
        for i, data in enumerate(self.cards_data):
            row, col = divmod(i, 3)
            card = BacktestCard(
                data[0], data[1], data[2], data[3], data[4], data[5] if len(data) > 5 else False
            )
            self.grid.addWidget(card, row, col)

        # 2. 渲染新加载的数据（如果有）
        if self.results:
            start_offset = len(self.cards_data)
            for i, data in enumerate(self.results):
                row, col = divmod(i + start_offset, 3)
                card = BacktestCard(*data)
                self.grid.addWidget(card, row, col)

        # 3. 始终在最后放一个 NewTestCard
        self.add_new_test_card()

    def showEvent(self, event):
        super().showEvent(event)
        if not self._is_loaded:
            self.load_data()

    def load_data(self):
        self.loading_label = QLabel("Loading historical results...")
        self.loading_label.setObjectName("LoadingLabel")
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.grid.addWidget(self.loading_label, 0, 0, 1, 3)
        self.loader.start()

    def add_new_card(self, strategy_name="Sentiment Engine"):
        """"""
        data = (strategy_name, "The Velvet Trend", "In-Progress", ["--", "--", "--"],
                [], {}, True)

        total_items = len(self.cards_data) + (len(self.results) if self.results else 0)
        row, col = divmod(total_items, 3)
        card = BacktestCard(*data)
        self.grid.addWidget(card, row, col)

        self.results.append(data)
        self.add_new_test_card()

        return card

    def add_new_test_card(self):
        """"""
        total_items = len(self.cards_data) + (len(self.results) if self.results else 0)
        row, col = divmod(total_items, 3)
        if self.new_test_card:
            self.grid.removeWidget(self.new_test_card)
        else:
            self.new_test_card = NewTestCard(self)
        self.grid.addWidget(self.new_test_card, row, col)

    def populate_cards(self, results):
        if hasattr(self, 'loading_label'):
            self.loading_label.deleteLater()

        self.results = results
        # 重新刷新布局（包含新数据）
        self.refresh_grid_layout()
        self._is_loaded = True

    def start_new_backtest(self, config_data: dict):
        """"""
        card = self.add_new_card(config_data["strategy_name"])
        self.backtest_manager.start_backtest(config_data, card)


class DataLoaderThread(QThread):
    data_loaded = Signal(list)

    def run(self):
        try:
            results = get_all_backtest_results()
            formatted_results = []
            for r in results:
                formatted_results.append(
                    ("Momentum", "Gold-Runner V4", "Optimized",
                    ["+24.8%", "2.14", "-4.2%"], [0.3, 0.5, 0.8], r)
                )
            self.data_loaded.emit(formatted_results)
        except Exception as e:
            logger.error(f"Failed to load backtest results: {e}")


# 1. 定义工人类：处理耗时的回测逻辑
class BacktestWorker(QObject):
    # 信号定义：(任务ID, 结果数据字典)
    finished = Signal(str, dict)
    error = Signal(str, str)

    def __init__(self, task_id, params):
        super().__init__()
        self.task_id = task_id
        self.params = params

    @Slot()
    def run(self):
        try:
            result = run_backtest()

            # 发送信号，必须带上 task_id，这样主线程才知道是谁的结果
            self.finished.emit(self.task_id, result)

        except Exception as e:
            self.error.emit(self.task_id, str(e))


# 2. 在你的主逻辑中管理多线程
class BacktestManager(QObject):
    def __init__(self):
        super().__init__()
        self.active_tasks = {}

    def start_backtest(self, params, target_object):
        """
        params: 回测参数
        target_object: 你想绑定的对象（比如 UI 里的一个 Card 或 TableItem）
        """
        # 生成唯一标识符
        task_id = str(uuid.uuid4())

        # 创建线程和工人
        thread = QThread()
        worker = BacktestWorker(task_id, params)
        worker.moveToThread(thread)

        # 记录任务关系
        self.active_tasks[task_id] = {
            "thread": thread,
            "worker": worker,
            "target": target_object  # 👈 关键：在这里绑定你的对象
        }

        # 信号连接
        thread.started.connect(worker.run)
        worker.finished.connect(self.handle_result)
        worker.error.connect(self.handle_error)

        # 线程清理（防止内存泄漏）
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        thread.finished.connect(lambda: self.cleanup_task(task_id))

        thread.start()
        logger.debug(f"已发起回测，任务ID: {task_id}")

    @Slot(str, dict)
    def handle_result(self, task_id, result):
        # 通过 task_id 找到对应的对象
        task_info = self.active_tasks.get(task_id)
        if task_info:
            target = task_info["target"]
            # 👈 现在你可以把结果直接赋给原来的对象了
            logger.debug(f"任务 {task_id} 完成，正在更新对象: {target}")
            self.update_ui_object(target, result)

    def update_ui_object(self, target, backtest_result):
        card_status = ""
        data = {
            "card_status": card_status,
            "backtest_result": backtest_result
        }
        logger.info(backtest_result)
        target.update_backtest_result(data)

    def cleanup_task(self, task_id):
        # 任务结束后从字典移除，释放内存
        if task_id in self.active_tasks:
            del self.active_tasks[task_id]
            logger.debug(f"任务 {task_id} 已清理释放")

    def handle_error(self, task_id, err_msg):
        logger.debug(f"任务 {task_id} 出错: {err_msg}")


