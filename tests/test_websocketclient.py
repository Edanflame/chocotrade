""""""
import time

from chocotrade.base.websocket import BaseWebSocketClient


def test_websocket():
    """"""
    ws = BaseWebSocketClient()
    ws.init("wss://ws.postman-echo.com/raw")

    ws.start()
    ws.wait_until_connected()

    ws.send_text("Hello")
    time.sleep(1)

    ws.stop()

