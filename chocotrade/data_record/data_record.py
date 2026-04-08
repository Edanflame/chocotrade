import threading
import time
from datetime import datetime

import numpy as np
import polars as pl

from ..core.event import EventType
from ..database.duckdb_database import DuckBarsDatabase


class TickBuffer:
    """单个列式缓冲区"""
    def __init__(self, capacity):
        self.capacity = capacity

        self.timestamp = np.zeros(capacity, dtype='datetime64[us]')

        self.volume = np.zeros(capacity, dtype='i8')
        self.turnover = np.zeros(capacity, dtype='f8')
        self.open_interest = np.zeros(capacity, dtype='f8')
        self.last_price = np.zeros(capacity, dtype='f8')
        self.last_volume = np.zeros(capacity, dtype='f8')
        self.limit_up = np.zeros(capacity, dtype='f8')
        self.limit_down = np.zeros(capacity, dtype='f8')
        self.open_price = np.zeros(capacity, dtype='f8')
        self.high_price = np.zeros(capacity, dtype='f8')
        self.low_price = np.zeros(capacity, dtype='f8')
        self.pre_close = np.zeros(capacity, dtype='f8')
        self.bid_price_1 = np.zeros(capacity, dtype='f8')
        self.bid_price_2 = np.zeros(capacity, dtype='f8')
        self.bid_price_3 = np.zeros(capacity, dtype='f8')
        self.bid_price_4 = np.zeros(capacity, dtype='f8')
        self.bid_price_5 = np.zeros(capacity, dtype='f8')
        self.ask_price_1 = np.zeros(capacity, dtype='f8')
        self.ask_price_2 = np.zeros(capacity, dtype='f8')
        self.ask_price_3 = np.zeros(capacity, dtype='f8')
        self.ask_price_4 = np.zeros(capacity, dtype='f8')
        self.ask_price_5 = np.zeros(capacity, dtype='f8')
        self.bid_volume_1 = np.zeros(capacity, dtype='f8')
        self.bid_volume_2 = np.zeros(capacity, dtype='f8')
        self.bid_volume_3 = np.zeros(capacity, dtype='f8')
        self.bid_volume_4 = np.zeros(capacity, dtype='f8')
        self.bid_volume_5 = np.zeros(capacity, dtype='f8')
        self.ask_volume_1 = np.zeros(capacity, dtype='f8')
        self.ask_volume_2 = np.zeros(capacity, dtype='f8')
        self.ask_volume_3 = np.zeros(capacity, dtype='f8')
        self.ask_volume_4 = np.zeros(capacity, dtype='f8')
        self.ask_volume_5 = np.zeros(capacity, dtype='f8')

        self.exchange = [None] * capacity
        self.symbol = [None] * capacity
        self.name = [None] * capacity
        self.ptr = 0

    def is_full(self):
        return self.ptr >= self.capacity

    def add(self, tick):
        idx = self.ptr
        self.symbol[idx] = tick.symbol
        self.exchange[idx] = tick.exchange
        self.name[idx] = tick.name

        self.timestamp[idx] = tick.timestamp
        self.volume[idx] = tick.volume
        self.turnover[idx] = tick.turnover
        self.open_interest[idx] = tick.open_interest
        self.last_price[idx] = tick.last_price
        self.last_volume[idx] = tick.last_volume
        self.limit_up[idx] = tick.limit_up
        self.limit_down[idx] = tick.limit_down
        self.open_price[idx] = tick.open_price
        self.high_price[idx] = tick.high_price
        self.low_price[idx] = tick.low_price
        self.pre_close[idx] = tick.pre_close
        self.bid_price_1[idx] = tick.bid_price_1
        self.bid_price_2[idx] = tick.bid_price_2
        self.bid_price_3[idx] = tick.bid_price_3
        self.bid_price_4[idx] = tick.bid_price_4
        self.bid_price_5[idx] = tick.bid_price_5
        self.ask_price_1[idx] = tick.ask_price_1
        self.ask_price_2[idx] = tick.ask_price_2
        self.ask_price_3[idx] = tick.ask_price_3
        self.ask_price_4[idx] = tick.ask_price_4
        self.ask_price_5[idx] = tick.ask_price_5
        self.bid_volume_1[idx] = tick.bid_volume_1
        self.bid_volume_2[idx] = tick.bid_volume_2
        self.bid_volume_3[idx] = tick.bid_volume_3
        self.bid_volume_4[idx] = tick.bid_volume_4
        self.bid_volume_5[idx] = tick.bid_volume_5
        self.ask_volume_1[idx] = tick.ask_volume_1
        self.ask_volume_2[idx] = tick.ask_volume_2
        self.ask_volume_3[idx] = tick.ask_volume_3
        self.ask_volume_4[idx] = tick.ask_volume_4
        self.ask_volume_5[idx] = tick.ask_volume_5

        self.ptr += 1

    def clear(self):
        self.ptr = 0

    def get_view(self):
        """获取当前已填充部分的视图，用于存入数据库"""
        data = {
            "symbol": self.symbol[:self.ptr],
            "exchange": self.exchange[:self.ptr],
            "name": self.name[:self.ptr],
            "timestamp": self.timestamp[:self.ptr],
            "volume": self.volume[:self.ptr],
            "turnover": self.turnover[:self.ptr],
            "open_interest": self.open_interest[:self.ptr],
            "last_price": self.last_price[:self.ptr],
            "last_volume": self.last_volume[:self.ptr],
            "limit_up": self.limit_up[:self.ptr],
            "limit_down": self.limit_down[:self.ptr],
            "open_price": self.open_price[:self.ptr],
            "high_price": self.high_price[:self.ptr],
            "low_price": self.low_price[:self.ptr],
            "pre_close": self.pre_close[:self.ptr],
            "bid_price_1": self.bid_price_1[:self.ptr],
            "bid_price_2": self.bid_price_2[:self.ptr],
            "bid_price_3": self.bid_price_3[:self.ptr],
            "bid_price_4": self.bid_price_4[:self.ptr],
            "bid_price_5": self.bid_price_5[:self.ptr],
            "ask_price_1": self.ask_price_1[:self.ptr],
            "ask_price_2": self.ask_price_2[:self.ptr],
            "ask_price_3": self.ask_price_3[:self.ptr],
            "ask_price_4": self.ask_price_4[:self.ptr],
            "ask_price_5": self.ask_price_5[:self.ptr],
            "bid_volume_1": self.bid_volume_1[:self.ptr],
            "bid_volume_2": self.bid_volume_2[:self.ptr],
            "bid_volume_3": self.bid_volume_3[:self.ptr],
            "bid_volume_4": self.bid_volume_4[:self.ptr],
            "bid_volume_5": self.bid_volume_5[:self.ptr],
            "ask_volume_1": self.ask_volume_1[:self.ptr],
            "ask_volume_2": self.ask_volume_2[:self.ptr],
            "ask_volume_3": self.ask_volume_3[:self.ptr],
            "ask_volume_4": self.ask_volume_4[:self.ptr],
            "ask_volume_5": self.ask_volume_5[:self.ptr]
        }

        df_to_insert = pl.from_dict(data)
        return df_to_insert


class DoubleBufferRecorder:
    def __init__(self, database, capacity=5000):
        self.database = database

        # 初始化两个缓冲区
        self.buffer_a = TickBuffer(capacity)
        self.buffer_b = TickBuffer(capacity)

        self.active_buffer = self.buffer_a
        self.lock = threading.Lock()
        self.executor_thread = None

        self.total_rows_saved = 0
        self.last_write_speed = 0  # rows/sec
        self.last_write_duration = 0 # ms
        self.size = 0
        self.size_str = None

    def on_tick(self, tick):
        # 1. 快速写入活跃缓冲区
        self.active_buffer.add(tick)

        # 2. 如果缓冲区满了，且当前没有后台任务在写，则交换
        if self.active_buffer.is_full():
            self.switch_and_flush()

    def switch_and_flush(self):
        with self.lock:
            # 检查后台线程是否还在忙（防止数据积压）
            if self.executor_thread and self.executor_thread.is_alive():
                print("警告：磁盘写入过慢，缓冲区溢出！")
                return

            # 交换 A/B 缓冲
            writing_buffer = self.active_buffer
            self.active_buffer = \
                self.buffer_b if self.active_buffer is self.buffer_a else self.buffer_a

            # 开启后台线程落库
            self.executor_thread = threading.Thread(
                target=self._async_save,
                args=(writing_buffer.get_view(), writing_buffer)
            )
            self.executor_thread.start()

    def _async_save(self, data_view, buffer_to_clear):
        """在后台线程运行"""
        try:
            row_count = len(data_view)
            start_time = time.perf_counter() # 精准计时开始
            self.database.update_tickdata(data_view)
            end_time = time.perf_counter() # 精准计时结束

            # 计算性能指标
            duration = end_time - start_time
            speed = row_count / duration if duration > 0 else 0
            self.size += row_count * 352   # (3 * 32 + 32 * 8)

            # 更新状态
            self.last_write_speed = speed
            self.last_write_duration = duration * 1000 # 转为毫秒
            self.total_rows_saved += row_count
            if self.size < 1024 * 1024:
                self.size_str = f"{self.size / 1024:.1f} KB"
            else:
                self.size_str = f"{self.size / (1024 * 1024):.2f} MB"

            # 清空旧缓冲区供下次使用
            buffer_to_clear.clear()
        except Exception as e:
            print(f"落库失败: {e}")

    def close(self):
        """退出前确保最后一批数据存入"""
        if self.active_buffer.ptr > 0:
            view = self.active_buffer.get_view()
            self.database.update_tickdata(view)


class RecorderEngine:
    def __init__(self, main_engine):
        self.main_engine = main_engine
        self.event_engine = main_engine._event_engine

        self.database = DuckBarsDatabase()
        self.recorder = DoubleBufferRecorder(self.database)

        # 2. 状态变量
        self.active = False
        self._timer = None

        self.record_stream = {}

        # # 3. 注册事件监听（对接你的事件驱动系统）
        # self.register_event()
        # self.start()

    def register_event(self):
        """订阅事件引擎的行情推送"""
        self.event_engine.register_handle(EventType.EVENT_TICK, self.process_tick_event)

    def process_tick_event(self, event):
        """事件回调处理逻辑"""
        if not self.active:
            return
        tick = event.event_data
        # 喂给底层的缓冲区
        self.recorder.on_tick(tick)

    def add_record_symbol(self, symbol):
        """"""
        now = datetime.now()
        now_str = now.strftime("%H:%M:%S")
        self.record_stream[symbol] =\
            f"{now_str},BOOK {symbol} L2_UPDATE,L5,log-row-dim,#d5c5a8,#d2c4bc"

        self.register_event()

    def get_record_streams(self):
        """"""
        data = []
        for _, value in self.record_stream.items():
            data.append({"detail": value})
        return data

    def start(self):
        """启动记录引擎"""
        self.active = True
        # 开启定时强制落库线程（例如每秒一次）
        # self._start_timer()
        print("行情记录引擎已启动")

    def pause(self):
        self.active = False

    def stop(self):
        """安全关闭（非常关键！）"""
        self.active = False
        # if self._timer:
        #     self._timer.cancel()

        # 核心逻辑：关闭前强制把 Buffer A 和 B 里的残余数据全部写入磁盘
        print("正在进行最后的数据落库...")
        self.recorder.close()
        print("记录引擎已安全关闭")

    def get_performance_metrics(self):
        """为 UI 提供的监控接口"""
        return {
            "speed": self.recorder.last_write_speed,
            "total": self.recorder.total_rows_saved,
            "latency": self.recorder.last_write_duration,
            "size_label": self.recorder.size_str
        }
