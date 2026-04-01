""""""
import asyncio
import json
import logging
import threading

import websockets
from websockets import State

logger = logging.getLogger("Websocket")


class BaseWebSocketClient:
    def __init__(self):
        """"""
        self.uri = None
        self.loop = None
        self.ws = None
        self._running = False  # 控制重连循环的开关
        self.connected_event = threading.Event()

    def init(self, url):
        """"""
        self.uri = url

    def _loop_runner(self):
        """"""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.create_task(self._connect_and_listen())
        try:
            self.loop.run_forever()
        finally:
            # 确保循环关闭时清理资源
            self.loop.close()

    async def _connect_and_listen(self):
        """"""
        self._running = True  # 初始设为开启

        while self._running:  # 检查开关状态
            try:
                async with websockets.connect(self.uri, ping_interval=20) as websocket:
                    self.ws = websocket
                    self.on_connect()
                    self.connected_event.set()
                    async for message in websocket:
                        self.on_message(message)

                self.on_disconnect()

            except Exception as e:
                if not self._running:
                    logger.info("[后台] 检测到手动关闭，停止重连")
                    break

                logger.info(f"[后台] 异常断开: {e}，5秒后重连...")
                await asyncio.sleep(5)

            self.ws = None

    def start(self):
        """"""
        t = threading.Thread(target=self._loop_runner, daemon=True)
        t.start()

    def send_text(self, message):
        """"""
        if self.ws and self.ws.state == State.OPEN:
            asyncio.run_coroutine_threadsafe(self.ws.send(message), self.loop)
        else:
            logger.info("[主线程] 无法发送：连接未建立")

    def send_json(self, message):
        """"""
        if self.ws and self.ws.state == State.OPEN:
            asyncio.run_coroutine_threadsafe(self.ws.send(json.dumps(message)), self.loop)
        else:
            logger.info("[主线程] 无法发送：连接未建立")

    async def _async_stop(self):
        """内部异步关闭逻辑"""
        logger.info("[后台] 正在执行手动关闭步骤...")
        self._running = False  # 1. 关掉重连开关
        if self.ws:
            await self.ws.close()  # 2. 关闭当前 Socket

        self.loop.stop()

    def wait_until_connected(self, timeout=10):
        """"""
        return self.connected_event.wait(timeout=timeout)

    def stop(self):
        """主线程调用的同步关闭接口"""
        if self.loop.is_running():
            asyncio.run_coroutine_threadsafe(self._async_stop(), self.loop)
            logger.info("[主线程] 已发起关闭指令")

    def on_message(self, msg):
        """"""
        logger.info(f"\n[后台] 收到消息: {msg}")

    def on_connect(self):
        """"""
        logger.info("[后台] 连接成功")

    def on_disconnect(self):
        """"""
        logger.info("[后台] 连接已关闭")


