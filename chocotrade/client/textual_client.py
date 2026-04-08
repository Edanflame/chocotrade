import logging
from functools import partial

from rich.table import Table
from rich.text import Text
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import (
    Button,
    Footer,
    Header,
    Input,
    Label,
    LoadingIndicator,
    RichLog,
    Static,
    TabbedContent,
    TabPane,
)
from textual.worker import Worker, WorkerState

from .client import add_gateway, get_backtest_result, listen_to_backend, run_backtest, send_order
from .texutal.widgets import BackendEventMessage

logger = logging.getLogger("Client")


# 模拟行情数据
MOCK_DATA = {
    "symbol": "700.HK",
    "last_price": 350.40,
    "asks": [(350.80, 120), (350.70, 80), (350.60, 210), (350.50, 45), (350.45, 12)],  # 卖盘
    "bids": [(350.35, 90), (350.30, 150), (350.25, 40), (350.20, 200), (350.10, 60)]   # 买盘
}


class StockDepth(Static):
    """显示5档行情的组件"""

    def on_mount(self) -> None:
        # 初次加载显示
        self.render_table()

    def render_table(self) -> None:
        # 使用 Rich 的 Table 构造 5 档界面
        table = Table(show_header=False, expand=True, box=None, padding=(0, 1))
        table.add_column("level", style="cyan")
        table.add_column("price", justify="right")
        table.add_column("volume", justify="right")

        # 1. 渲染卖盘 (从 卖5 到 卖1)
        for i, (p, v) in enumerate(reversed(MOCK_DATA["asks"])):
            table.add_row(f"卖{5-i}", Text(f"{p:.2f}", style="red"), str(v))

        # 2. 渲染最新价
        table.add_row("-" * 5, "-" * 10, "-" * 5)
        table.add_row("最新", Text(f"{MOCK_DATA['last_price']:.2f}", style="bold yellow"), "")
        table.add_row("-" * 5, "-" * 10, "-" * 5)

        # 3. 渲染买盘 (从 买1 到 买5)
        for i, (p, v) in enumerate(MOCK_DATA["bids"]):
            table.add_row(f"买{i+1}", Text(f"{p:.2f}", style="green"), str(v))

        self.update(table)


class TextualHandler(logging.Handler):
    def __init__(self, rich_log: RichLog):
        super().__init__()
        self.rich_log = rich_log

    def emit(self, record):
        log_entry = self.format(record)
        # 使用 call_after_refresh 确保线程安全
        self.rich_log.write(log_entry)


class TextualClient(App):
    """"""
    CSS = """
    Screen {
        align: center middle;
    }

    #main {
        width: 100%;
        height: 100%;
    }

    #main-layout {
        /* layout: horizontal; */
        width: 100%;
        height: 1fr;
        /* align: center middle; */
        padding: 1;
    }

    #left-pane {
        width: 65%;   /* 占据 65% 的宽度 */
        height: 100%;
        border: solid green;
        padding: 1;
        margin-right: 1;
        align: center top;
    }

    #display {
        height: 2;
    }

    #button-wrapper {
        width: 100%;
        height: auto;
        /* 核心：让这个容器里的按钮居中 */
        align: center top;
    }

    #button-wrapper Button {
        width: 30%;
        margin-top: 1; /* 按钮之间的间距 */
    }

    #loader-container {
        height: 3;           /* 占据 3 行高度 */
    }

    #right-pane {
        width: 35%;   /* 占据剩余 35% 的宽度 */
        height: 100%;
        border: solid yellow;
        padding: 1;
    }

    #metrics-list {
        /* 如果指标太多，允许纵向滚动 */
        overflow-y: auto;
    }

    Label {
        width: 100%;
        content-align: center middle;
        text-style: bold;
        color: cyan;
        margin-bottom: 1;
        background: $boost;
    }

    .metric {
        background: $surface;
        margin-bottom: 1;
        padding: 0 1;
        border-left: solid cyan;
        height: 3; /* 固定高度让列表整齐 */
        content-align: left middle;
    }
    StockDepth {
        width: 30;
        height: 15;
        border: solid gray;
        margin: 1 2;
        background: $surface;
    }
    """


    def compose(self) -> ComposeResult:
        """"""
        yield Header(show_clock=True)  # 显示带时钟的页眉

        with TabbedContent(id="main"):
            with TabPane("首页", id="home"):
                yield Static("[red]●[/red] 连接失败", id="status_text1")
                yield Static("[green]●[/green] 系统正常", id="status_text2")
                yield Static("[yellow]●[/yellow] 系统未初始化", id="status_text3")

            with TabPane("操作", id="mani"):
                with Horizontal(id="main-layout"):
                    # 左侧
                    with Vertical(id="left-pane"):
                        yield Label("你好！请在下方输入：")
                        yield Input(placeholder="在此输入一些文字...")
                        yield Static(id="display")    # 用来显示结果的区域

                        with Horizontal(id="center"):
                            yield StockDepth(id="my_depth_widget")
                            with Vertical(id="button-wrapper"):
                                yield Button("添加网关", id="add_gateway_btn")
                                # yield Button("委托下单", id="send_order_btn")
                                yield Button("开始回测", id="calc_btn")
                                yield Button("回测结果", id="query_calc_btn")
                                yield Button("关闭页面", id="quit")

                        with Container(id="loader-container"):
                            loading = LoadingIndicator(id="loading")
                            loading.display = False
                            yield loading

                        yield RichLog(id="log_view", auto_scroll=True)

                    # 右侧
                    with Vertical(id="right-pane"):
                        yield Label("实时指标监控")
                        # 模拟不定数量的指标（可以动态 yield 或 query 后更新）
                        with Vertical(id="metrics-list"):
                            yield Static("指标 1: 运行中", classes="metric")
                            yield Static("指标 2: 240ms", classes="metric")
                            yield Static("指标 3: 85% CPU", classes="metric")

            with TabPane("网关", id="gateways"):
                yield Static("这是网关")
                yield Static("[green]●[/green] 系统正常", id="status_text")

            with TabPane("回测", id="backtest"):
                yield Static("这是回测")
                yield Static("[red]●[/red] 连接失败", id="status_text")

            with TabPane("策略", id="strategy"):
                yield Static("这是策略")

            with TabPane("录制", id="record"):
                yield Static("这是录制")
        yield Footer()                 # 显示快捷键的页眉

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """"""
        if event.button.id == "calc_btn":
            self.query_one("#loading").display = True
            event.button.disabled = True
            logger.info("开始计算")
            run_backtest_func = partial(run_backtest, name="User_B", port=50051)
            self.run_worker(run_backtest_func, thread=True, exclusive=False, name="run_backtest")
        elif event.button.id == "add_gateway_btn":
            logger.info("添加网关")
            add_gateway_func = partial(add_gateway, gateway_name="User_B", port=50051)
            self.run_worker(add_gateway_func, thread=True, exclusive=False, name="add_gateway")
        elif event.button.id == "send_order_btn":
            logger.info("发送委托")
            send_order_func = partial(send_order, gateway_name="User_B", port=50051)
            self.run_worker(send_order_func, thread=True, exclusive=False, name="send_order")
        elif event.button.id == "query_calc_btn":
            logger.info("查询回测结果")
            get_backtest_result_func = partial(get_backtest_result, name="User_B", port=50051)
            self.run_worker(
                get_backtest_result_func,
                thread=True,
                exclusive=False,
                name="query_backtest"
            )
        elif event.button.id == "quit":
            self.exit()

    def on_input_changed(self, event: Input.Changed) -> None:
        """"""
        display = self.query_one("#display", Static)
        if event.value:
            display.update(f"你正在输入: [yellow]{event.value}[/yellow]")
        else:
            display.update("")

    async def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        """监听所有 Worker 状态"""
        worker = event.worker

        # 根据名字和状态精准拦截
        if worker.name == "run_backtest" and event.state == WorkerState.SUCCESS:
            # 获取结果并处理
            result = worker.result
            logger.info("success")
            self.query_one("#loading").display = False
            self.query_one("#calc_btn").disabled = False

            container = self.query_one("#metrics-list")
            for key, value in result.items():
                new_item = Static(f"指标 {key}: {value}", classes="metric")

                # 限制数量：如果超过5个，删除第一个
                existing_metrics = container.query(".metric")
                if len(existing_metrics) >= 20:
                    await existing_metrics.first().remove()

                # 挂载新组件
                await container.mount(new_item)
        elif worker.name == "query_backtest" and event.state == WorkerState.SUCCESS:
            result = worker.result
            for key, value in result.items():
                logger.info(f"{key}: {value}")

        elif worker.name == "add_gateway" and event.state == WorkerState.SUCCESS:
            result = worker.result
            display = self.query_one("#display", Static)
            display.update(result)

    def on_backend_event_message(self, message: BackendEventMessage) -> None:
        """"""
        if message.event_type == "USER_LOGIN":
            self.write(f"用户登录: {message.data['user']}")
        elif message.event_type == "SERVER_ALERT":
            self.write(f"警告: {message.data['info']}")

    async def on_mount(self) -> None:
        """"""
        log_view = self.query_one("#log_view", RichLog)
        handler = TextualHandler(log_view)

        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

        self.run_worker(
            listen_to_backend([logger.info, self.refresh_data]),
            thread=False,
            name="bgtask"
        )

    def refresh_data(self, data) -> None:
        # 这里写从 API 获取数据的逻辑
        MOCK_DATA["asks"] = [
            (float(data["ask_price_1"]), float(data["ask_volume_1"])),
            (float(data["ask_price_2"]), float(data["ask_volume_2"])),
            (float(data["ask_price_3"]), float(data["ask_volume_3"])),
            (float(data["ask_price_4"]), float(data["ask_volume_4"])),
            (float(data["ask_price_5"]), float(data["ask_volume_5"]))
        ]
        MOCK_DATA["bids"] = [
            (float(data["bid_price_1"]), float(data["bid_volume_1"])),
            (float(data["bid_price_2"]), float(data["bid_volume_2"])),
            (float(data["bid_price_3"]), float(data["bid_volume_3"])),
            (float(data["bid_price_4"]), float(data["bid_volume_4"])),
            (float(data["bid_price_5"]), float(data["bid_volume_5"]))
        ]
        MOCK_DATA["last_price"] = (MOCK_DATA["asks"][0][0] + MOCK_DATA["bids"][0][0]) / 2
        depth_widget = self.query_one("#my_depth_widget", StockDepth)
        depth_widget.render_table()


if __name__ == "__main__":
    app = TextualClient()
    app.run()
