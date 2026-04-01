""""""
import asyncio
import threading
from collections.abc import Coroutine
from concurrent.futures import Future
from threading import Thread
from typing import Any

import httpx


class BaseRestClient:
    """"""
    def __init__(self, base_url: str) -> None:
        """"""
        self.base_url = base_url
        self.client = None
        self._loop = None
        self._thread: Thread | None = None

    async def _init_client(self) -> None:
        """初始化异步客户端，开启 HTTP/2"""
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            http2=True,
            headers={"X-API-KEY": ""},
            timeout=httpx.Timeout(5.0)
            )

    async def _close_client(self) -> None:
        """"""
        if self.client:
            await self.client.aclose()

    def call(self, coro: Coroutine) -> Any:
        """"""
        if not self._loop or not self._loop.is_running():
            raise RuntimeError("后台线程未运行")

        future: Future = asyncio.run_coroutine_threadsafe(coro, self._loop)

        return future.result()

    async def request(self, method: str, endpoint: str, **kwargs):
        """"""
        resp = await self.client.request(method, endpoint, **kwargs)
        return resp.text
        # return resp.json()

    async def get_price_async(self):
        """"""
        return await self.request("GET", "/", params={"wd": "qwen"})

    def _thread_worker(self):
        """"""
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)

        # 初始化 client
        self._loop.run_until_complete(self._init_client())

        # 保持 loop 运行，直到调用 stop()
        try:
            self._loop.run_forever()
        finally:
            self._loop.run_until_complete(self._close_client())
            self._loop.close()

    def run_in_thread(self):
        """"""
        self._thread = threading.Thread(target=self._thread_worker, daemon=True)
        self._thread.start()

    def stop(self):
        """"""
        if self._loop:
            self._loop.call_soon_threadsafe(self._loop.stop)

