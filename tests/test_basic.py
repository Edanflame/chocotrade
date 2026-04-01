"""
基础测试函数
"""


def fib(n):
    """演示测试函数"""
    if n in (0, 1):
        return 1
    return fib(n - 1) + fib(n - 2)


def test_fib():
    """演示测试"""
    fib(5)
