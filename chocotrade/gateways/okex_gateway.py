""""""
import base64
import hashlib
import hmac
import json
import logging
import time
from datetime import datetime

from pydantic_settings import BaseSettings, SettingsConfigDict

from ..base.gateway import BaseGateway
from ..base.restapi import BaseRestClient
from ..base.websocket import BaseWebSocketClient
from ..core.constant import Direction, Exchange, OrderType
from ..core.datatype import CancelRequest, OrderData, OrderRequest, SubscribeRequest

PUBLIC_HOST: str = "wss://ws.okx.com:8443/ws/v5/public"

HOSTS = {
    "real": {
        "REAL_REST_HOST": "https://www.okx.com",
        "REAL_PUBLIC_HOST": "wss://ws.okx.com:8443/ws/v5/public",
        "REAL_PRIVATE_HOST": "wss://ws.okx.com:8443/ws/v5/private",
        "REAL_BUSINESS_HOST": "wss://ws.okx.com:8443/ws/v5/business"
    },
    "demo": {
        "DEMO_REST_HOST": "https://www.okx.com",
        "DEMO_PUBLIC_HOST": "wss://wspap.okx.com:8443/ws/v5/public",
        "DEMO_PRIVATE_HOST": "wss://wspap.okx.com:8443/ws/v5/private",
        "DEMO_BUSINESS_HOST": "wss://wspap.okx.com:8443/ws/v5/business"
    }
}


logger = logging.getLogger("Backend")


class Settings(BaseSettings):
    api_key: str
    secret_key: str
    passphrase: str

    model_config = SettingsConfigDict(env_file="~/.chocotrade/.env")


settings = Settings()


class OkexGateway(BaseGateway):
    """"""
    default_name = "okex"

    def __init__(self, event_engine, gateway_name: str):
        """"""
        super().__init__(event_engine, self.default_name)
        self.public_ws = PublicWebsocket(self)
        self.private_ws = PrivateWebsocket(self)

    def connect(self, setting: dict) -> None:
        """"""
        self.api_key = settings.api_key
        self.secret_key = settings.secret_key
        self.passphrase = settings.passphrase

        self.public_ws.connect()
        self.private_ws.connect(
            self.api_key,
            self.secret_key,
            self.passphrase
        )
        self.public_ws.wait_until_connected()
        self.private_ws.wait_until_connected()

        self.private_ws.login()

        self.start_timer(20)
        self.subscribe("")

    def close(self) -> None:
        """"""
        pass

    def subscribe(self, req: SubscribeRequest) -> None:
        """"""
        self.public_ws.subscribe()

    def query_account(self) -> None:
        """"""
        pass

    def query_position(self) -> None:
        """"""
        pass

    def send_order(self, req: OrderRequest) -> str:
        """"""
        self.private_ws.send_order2(req)

    def cancel_order(self, req: CancelRequest) -> None:
        """"""
        pass

    def on_schedule_triggered(self):
        """"""
        self.public_ws.ping()
        self.private_ws.ping()


class OkexRestClient(BaseRestClient):
    """"""
    pass


class OkexWebSocketClient(BaseWebSocketClient):
    """"""
    def __init__(self, gateway: OkexGateway) -> None:
        """"""
        super().__init__()
        self.gateway = gateway
        self.rest_host: str = None
        self.public_wss: str = None
        self.private_wss: str = None
        self.business_wss: str = None

    def connect(self):
        """"""
        (
            self.rest_host,
            self.public_wss,
            self.private_wss,
            self.business_wss
        ) = HOSTS["demo"].values()

    def on_connect(self):
        """"""
        logger.info("[okex] 连接成功")

    def on_disconnect(self):
        """"""
        logger.info("[okex] 连接已关闭")

    def ping(self):
        """"""
        logger.info("okex网关：send ping")
        self.send_text("ping")

    def on_message(self, msg):
        """"""
        pass


class PublicWebsocket(OkexWebSocketClient):
    """"""
    def __init__(self, gateway: OkexGateway):
        """"""
        super().__init__(gateway)

    def connect(self):
        """"""
        super().connect()
        self.init(self.public_wss)
        self.start()

    def subscribe(self):
        """"""
        symbol: str = "BTC-USDT"

        packet: dict = {
            "op": "subscribe",
            "args":[
                {
                    "channel":"books5",
                    "instId": symbol
                }
            ]
        }
        self.send_json(packet)

    def on_message(self, msg):
        """"""
        # logger.info(f"okex网关：{msg}")
        self.gateway.on_tick(msg)


class PrivateWebsocket(OkexWebSocketClient):
    """"""
    def __init__(self, gateway: OkexGateway):
        """"""
        super().__init__(gateway)
        self.order_count = 0
        self.reqid = 0

    def connect(
        self,
        api_key,
        secret_key,
        passphrase
    ):
        """"""
        super().connect()

        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase

        self.init(self.private_wss)
        self.start()

    def login(self):
        """"""
        timestamp: str = str(time.time())
        msg: str = timestamp + "GET" + "/users/self/verify"
        signature: bytes = generate_signature(msg, self.secret_key)

        packet: dict = {
            "op": "login",
            "args":
            [
                {
                    "apiKey": self.api_key,
                    "passphrase": self.passphrase,
                    "timestamp": timestamp,
                    "sign": signature.decode("utf-8")
                }
            ]
        }

        self.send_json(packet)

    def subscribe_topic(self) -> None:
        """"""
        packet: dict = {
            "op": "subscribe",
            "args": [
                {
                    "channel": "orders",
                    "instType": "ANY"
                },
                {
                    "channel": "account"
                },
                {
                    "channel": "positions",
                    "instType": "ANY"
                },
            ]
        }
        self.send_json(packet)

    def send_order(self, req: OrderRequest) -> str:
        """"""
        self.order_count += 1
        self.connect_time = int(datetime.now().strftime("%y%m%d%H%M%S"))
        count_str = str(self.order_count).rjust(6, "0")
        orderid = f"{self.connect_time}{count_str}"
        self.orderid = orderid
        arg: dict = {
            # "instIdCode": contract.extra["instIdCode"],     # type: ignore
            "instIdCode": req.symbol,     # type: ignore
            "clOrdId": orderid,
            # "side": DIRECTION_VT2OKX[req.direction],
            "side": "buy",
            # "ordType": ORDERTYPE_VT2OKX[req.type],
            "ordType": "limit",
            "px": str(req.price),
            "sz": str(req.volume),
            "tdMode": "cross"       # Only support cross margin mode
        }

        # Add extra field for portfolio margin
        # if self.margin_currency:
        #     arg["ccy"] = self.margin_currency

        # Add extra field for spot
        # if "SPOT" in req.symbol:
        #     quote_ccy_list: list[str] = contract.extra["tradeQuoteCcyList"]     # type: ignore
        #     arg["tradeQuoteCcy"] = quote_ccy_list[0]

        # Create websocket request with unique request ID
        self.reqid += 1
        packet: dict = {
            "id": str(self.reqid),
            "op": "order",
            "args": [arg]
        }
        self.send_json(packet)

        # Create order data object and push to gateway
        order: OrderData = req.create_order_data(orderid, self.gateway.gateway_name)
        self.gateway.on_order(order)

        # Return VeighNa order ID (gateway_name.orderid)
        return str(order.ct_orderid)

    def cancel_order(self, req: CancelRequest):
        """"""
        """
        contract: ContractData | None = self.gateway.get_contract_by_symbol(req.symbol)
        if not contract:
            self.gateway.write_log(f"Cancel order failed, symbol not found: {req.symbol}")
            return
        """
        # Initialize cancel parameters
        # arg: dict = {"instIdCode": contract.extra["instIdCode"]}     # type: ignore
        arg: dict = {"instIdCode": "BTC-USDT"}     # type: ignore
        arg["clOrdId"] = self.orderid
        """
        # Determine the type of order ID to use for cancellation
        # OKX supports both client order ID and exchange order ID for cancellation
        if req.orderid in self.local_orderids:
            # Use client order ID if it was created by this gateway instance
            arg["clOrdId"] = req.orderid
        else:
            # Use exchange order ID if it came from another source
            arg["ordId"] = req.orderid
        """
        # Create websocket request with unique request ID
        self.reqid += 1
        packet: dict = {
            "id": str(self.reqid),
            "op": "cancel-order",
            "args": [arg]
        }

        # Send the cancellation request
        self.send_json(packet)

    def on_connect(self):
        """"""
        logger.info("okex private 登录成功")

    def on_login(self, data):
        """"""
        pass

    def send_order2(self, req=""):
        order = OrderRequest(
            symbol = "BTC-USDT",
            exchange = Exchange.GLOBAL,
            direction = Direction.LONG,
            type = OrderType.LIMIT,
            volume = 0.01,
            price = 70000
        )
        self.send_order(order)

    def on_order(self):
        """"""
        # self.cancel_order("")
        pass

    def on_message(self, msg):
        """"""
        if msg == "pong":
            return

        data = json.loads(msg)
        if data.get("event", "") == "login":
            self.on_login(data)
        elif data.get("op", "") == "order":
            self.on_order()

        logger.info(f"okex private网关登录：{msg}")


def generate_signature(msg: str, secret_key: str) -> bytes:
    """"""
    return base64.b64encode(
        hmac.new(secret_key.encode(), msg.encode(), hashlib.sha256).digest()
    )



