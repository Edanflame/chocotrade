""""""
import threading
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from threading import Thread
from time import sleep
from typing import Any

from .data_structures import Empty, Queue


@dataclass(slots=True)
class Event:
    """"""
    event_type: str
    event_data: Any


class EventType(Enum):
    """"""
    EVENT_ALL = "event_all"
    EVENT_TIMER = "event_timer"
    EVENT_DEFAULT = "event_default"

    EVENT_TICK = "event_tick."
    EVENT_BAR = "event_bar."
    EVENT_NEWS = "event_news."

    EVENT_CONTRACT = "event_contract."
    EVENT_POSITION = "event_position."
    EVENT_ACCOUNT = "event_account."

    EVENT_TRADE = "event_trade."
    EVENT_ORDER = "event_order."

    EVENT_LOG = "eLog"


class Handler(Callable):
    """"""
    def __init__(self):
        super().__init__()


class EventEngine:
    """
    Event engine of the Uquant
    """
    def __init__(self, engine_name: str = "event_engine") -> None:
        """初始化引擎"""
        self._engine_name: str = engine_name
        self._interval: int = 1
        self._timer: int = 0
        self._active: threading.Event = threading.Event()
        self._queue: Queue = Queue()
        self._handles: defaultdict = defaultdict(list)

        self._worker: Thread = Thread(target=self._work)
        self._timer_worker: Thread = Thread(target=self._timer_work)

    def start(self) -> None:
        """启动引擎"""
        self._active.clear()
        self._worker.start()
        self._timer_worker.start()

    def stop(self) -> None:
        """停止引擎"""
        self._active.set()
        if self._timer_worker.is_alive():
            self._timer_worker.join()

        if self._worker.is_alive():
            self._worker.join()

    def register_handle(self, event_type: str, handler: Handler) -> None:
        """注册事件处理函数"""
        event_handlers: list[Handler] = self._handles[event_type]
        if handler not in event_handlers:
            event_handlers.append(handler)

    def unregister_handle(self, event_type: str, handler: Handler) -> None:
        """"""
        event_handlers: list[Handler] = self._handles[event_type]
        if handler in event_handlers:
            event_handlers.remove(handler)

    def _work(self) -> None:
        """事件引擎运行"""
        while not self._active.is_set():
            try:
                event: Event = self.get()
                self._process(event)
            except Empty:
                pass

    def _timer_work(self) -> None:
        """定时器引擎定时放置事件"""
        while not self._active.is_set():
            sleep(self._interval)
            self._timer += 1
            self._timer % 60
            event: Event = Event(EventType.EVENT_TIMER, self._timer)
            self.put(event)

    def put(self, event) -> None:
        """把事件放入事件引擎"""
        self._queue.put(event)

    def get(self) -> Event:
        """从事件引擎中取出事件"""
        event = self._queue.get(block=True, timeout=1)
        return event

    def _process(self, event: Event) -> None:
        """事件处理"""
        if event.event_type in self._handles:
            [handle(event) for handle in self._handles[event.event_type]]

        if event.event_type != EventType.EVENT_TIMER:
            [handle(event) for handle in self._handles[EventType.EVENT_ALL]]

