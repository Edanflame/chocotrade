
from textual.message import Message


class BackendEventMessage(Message):
    """自定义一个 Textual 消息，用于承载后端事件"""
    def __init__(self, event_type: str, event_data: any) -> None:
        """"""
        super().__init__()
        self.event_type = event_type
        self.event_data = event_data

