""""""
from ..base.strategy import BaseStrategy


class CtaStrategy(BaseStrategy):
    """"""
    def __init__(self):
        """"""
        super().__init__()

    @BaseStrategy.auto_update
    def on_bar(self, bar):
        """"""
        if self.last_price is None:
            self.last_price = bar
            return

        if self.cache.mean(10) > self.cache.mean(5):
            self.buy(bar, 1)
        else:
            self.sell(bar, 1)


