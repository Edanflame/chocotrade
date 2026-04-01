""""""
import logging
import time

from chocotrade.base.restapi import BaseRestClient

logger = logging.getLogger(__name__)


def test_get_url_content_success():
    """"""
    url = "https://postman-echo.com/get?test=123"
    client = BaseRestClient(url)
    client.run_in_thread()

    time.sleep(0.1)

    price_data = client.call(client.get_price_async())
    logger.info(f"[主线程] 收到后台返回的结果: {str(price_data)}")

    client.stop()


def test_post_url_content_success():
    """"""
    url = "https://postman-echo.com/post"
    client = BaseRestClient(url)
    client.run_in_thread()

    time.sleep(0.1)

    price_data = client.call(client.get_price_async())
    logger.info(f"[主线程] 收到后台返回的结果: {price_data}")

    client.stop()

