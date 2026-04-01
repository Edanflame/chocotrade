""""""
import functools


class BaseStrategy:
    """"""
    def __init__(self):
        """"""
        self.context = None
        self.cache = None
        self.last_price: float = None

    def init(self):
        """"""
        self.cache = self.context.cache

    def add_context(self, context):
        """"""
        self.context = context
        self.init()

    def auto_update(func):
        """自动更新缓存"""
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            self.update(args[0])
            func(self, *args, **kwargs)
            self.last_price = args[0]
        return wrapper

    @auto_update
    def on_bar(self, bar):
        """"""
        if self.last_price is None:
            self.last_price = bar
            return

        if bar > self.cache.mean():
            self.buy(bar, 1)
        else:
            self.sell(bar, 1)

    def on_trade(self, trade) -> None:
        """"""
        pass

    def on_order(self, order) -> None:
        """"""
        pass

    def buy(self, price, volume):
        """"""
        self.context.buy(price, volume)

    def sell(self, price, volume):
        """"""
        self.context.sell(price, volume)

    def update(self, price):
        """"""
        self.context.update(price)

