""""""
import base64
import io

# import matplotlib
# # 强制无头模式
# matplotlib.use('Agg')
# import matplotlib.pyplot as plt
from contextlib import redirect_stderr, redirect_stdout
from dataclasses import dataclass

from IPython.core.interactiveshell import InteractiveShell

from .database.duckdb_database import DuckBarsDatabase


@dataclass
class ExecutionBlock:
    """定义 Engine 返回的数据块"""
    msg_type: str  # stdout, error, display_data, execute_result
    mime_type: str # text/plain, image/png, text/html
    content: str = ""
    binary_data: bytes | None = None

class IPythonEngine:
    def __init__(self):
        self.shell = InteractiveShell()
        self.shell.user_ns["database"] = DuckBarsDatabase()
        # 拦截 IPython 的富媒体发布系统
        self.shell.display_pub.publish = self._on_display_publish
        self._collected_data: list[ExecutionBlock] = []

    def _on_display_publish(self, data, metadata=None, **kwargs):
        """当代码调用 plt.show() 或 display() 时触发"""
        if 'image/png' in data:
            raw = data['image/png']
            # 处理可能是 base64 字符串的情况
            binary = base64.b64decode(raw) if isinstance(raw, str) else raw
            self._collected_data.append(ExecutionBlock(
                msg_type="display_data", mime_type="image/png", binary_data=binary
            ))
        elif 'text/html' in data:
            self._collected_data.append(ExecutionBlock(
                msg_type="display_data", mime_type="text/html", content=data['text/html']
            ))

    def run(self, code: str) -> list[ExecutionBlock]:
        """执行代码并收集所有输出块"""
        self._collected_data = []
        stdout_io = io.StringIO()
        stderr_io = io.StringIO()

        with redirect_stdout(stdout_io), redirect_stderr(stderr_io):
            result = self.shell.run_cell(code)

        # 1. 收集标准输出
        if stdout_io.getvalue():
            self._collected_data.append(ExecutionBlock(
                msg_type="stdout", mime_type="text/plain", content=stdout_io.getvalue()
            ))

        # 2. 收集错误信息
        if result.error_in_exec:
            self._collected_data.append(ExecutionBlock(
                msg_type="error", mime_type="text/plain", content=str(result.error_in_exec)
            ))

        # 3. 收集 Out[x] 表达式结果
        if result.result is not None:
            self._collected_data.append(ExecutionBlock(
                msg_type="execute_result", mime_type="text/plain", content=repr(result.result)
            ))

        # 4. 清理当前未关闭的图表，防止状态污染
        # plt.close('all')
        print(self._collected_data)

        return self._collected_data
