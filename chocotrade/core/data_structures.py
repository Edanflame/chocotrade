"""
抽象数据结构
"""
from queue import Empty as Empty
from queue import Queue as Queue


class CtQueue:
    """"""
    MAX_SIZE = 10

    def __init__(self, _max_size: int = MAX_SIZE):
        """"""
        self._max_size = _max_size
        self._count = 0
        self.front = None
        self.rear = None

    class Node:
        """"""
        def __init__(self, item: int):
            """"""
            self.item = item
            self.next = None

    def count(self):
        """"""
        return self._count

    def is_empty(self) -> bool:
        """"""
        return self._count == 0

    def is_full(self) -> bool:
        """"""
        return self._count == self.max_size

    def enqueue(self, x: int) -> bool:
        """"""
        if self.is_full():
            return False

        add = self.Node(x)
        if self.front is None:
            self.front = add
        else:
            self.rear.next = add

        self.rear = add
        return True

    def deqeueue(self) -> tuple[bool, int]:
        """"""
        if self.is_empty():
            return (False, None)

        temp = self.front.item
        self.front = self.front.next

        if self.front is None:
            self.rear = None

        return (True, temp)
