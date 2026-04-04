import datetime
import io
from contextlib import redirect_stderr, redirect_stdout

from PySide6.QtCore import Qt, QThread, QTimer, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSplitter,
    QVBoxLayout,
    QWidget,
)
from qtconsole.inprocess import QtInProcessKernelManager

from ....llm.llm import LLMCore

COLORS = {
    "bg": "#181210",
    "surface": "#251e1c",
    "surface_low": "#201a18",
    "surface_highest": "#3b3331",
    "primary": "#e9c349",
    "on_primary": "#181210",
    "secondary": "#f9ba82",
    "tertiary": "#d5c5a8",
    "on_surface": "#ede0dc",
    "on_surface_variant": "#d2c4bc",
    "outline": "#4f453f",
    "error": "#ffb4ab",
    "success": "#4ade80",
    "primary_container": "#3b2d00"
}

GLOBAL_STYLES = f"""
QWidget#MainWorkspace {{ background-color: {COLORS['bg']}; }}
QSplitter#MainSplitter::handle {{ background-color: #332b29; }}
QSplitter#MainSplitter::handle:hover {{ background-color: {COLORS['primary']}; }}
QWidget#ChatPanel {{
    background-color: {COLORS['bg']}; border-left: 1px solid {COLORS['outline']}4D;
}}

QFrame#NotebookCellFrame {{ background: transparent; border: none; }}
QLabel[class="CellInLabel"] {{
    color: {COLORS['on_surface_variant']};
    font-family: 'Consolas';
    font-size: 11px;
    opacity: 0.5;
}}
QPlainTextEdit[class="CellEditor"] {{
    background-color: {COLORS['surface']};
    color: #f2e0c3;
    border: none;
    border-left: 4px solid {COLORS['primary']};
    border-radius: 4px;
    padding: 10px;
    font-family: 'Consolas';
    font-size: 13px;
}}
QPlainTextEdit[class="CellEditor"]:read-only {{
    border-left: 4px solid {COLORS['outline']};
    color: {COLORS['on_surface_variant']};
}}
QLabel[class="CellOutput"] {{
    background-color: #130d0b;
    color: #d2c4bc;
    border: 1px solid #4f453f33;
    border-radius: 6px;
    padding: 12px;
    font-family: 'Consolas';
    font-size: 12px;
    qproperty-alignment: 'AlignLeft | AlignTop';
}}

QFrame#FloatingBar {{
    background-color: {COLORS['surface']};
    border: 1px solid {COLORS['outline']}4D;
    border-radius: 16px;
}}
QPlainTextEdit[class="FloatingInput"] {{
    background: transparent;
    border: none;
    color: white;
    padding: 10px;
    font-size: 14px;
    font-family: 'Inter';
}}
QPushButton[class="FloatingConfirmBtn"] {{
    background-color: {COLORS['primary']};
    color: {COLORS['on_primary']};
    font-weight: 800;
    border-radius: 8px;
}}
QPushButton[class="FloatingConfirmBtn"]:hover {{ background-color: #fce47c; }}

QLabel[class="UserBubble"] {{
    background-color: {COLORS['primary_container']};
    color: {COLORS['primary']};
    border: 1px solid {COLORS['primary']}33;
    border-radius: 12px;
    border-top-right-radius: 0px;
    padding: 10px;
    font-size: 13px;
}}
QLabel[class="AiBubble"] {{
    background-color: {COLORS['surface']};
    color: {COLORS['on_surface']};
    border: 1px solid {COLORS['outline']}1A;
    border-radius: 12px;
    border-top-left-radius: 0px;
    padding: 10px;
    font-size: 13px;
}}
QLabel[class="BubbleMeta"] {{
    font-size: 9px;
    font-weight: bold;
    color: gray;
    opacity: 0.5;
}}

/* 确保滚动区域背景透明，不遮挡主背景 */
QScrollArea {{
    background: transparent;
    border: none;
}}

/* 关键：设置滚动区域内部的视口背景为透明 */
QScrollArea > QWidget > QWidget {{
    background: transparent;
}}

/* 显式给左侧容器设置背景色 */
QWidget#NotebookContainer {{
    background-color: #181210;
}}
"""


class NotebookCell(QFrame):
    def __init__(self, execution_count, code=None, parent=None):
        super().__init__(parent)
        self.setObjectName("NotebookCellFrame")

        layout = QVBoxLayout(self)
        layout.setSizeConstraint(QVBoxLayout.SetFixedSize) # 关键：高度随内部紧缩
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # In [x] + Code Area
        input_layout = QHBoxLayout()
        in_label = QLabel(f"In [{execution_count}]:")
        in_label.setProperty("class", "CellInLabel")
        in_label.setFixedWidth(50)
        in_label.setAlignment(Qt.AlignRight | Qt.AlignTop)

        self.code_box = QPlainTextEdit()
        self.code_box.setProperty("class", "CellEditor")
        self.code_box.setPlaceholderText("... waiting for input")
        self.code_box.setFixedHeight(100) # 固定高度
        if code is not None:
            self.code_box.setPlainText(code)

        input_layout.addWidget(in_label)
        input_layout.addWidget(self.code_box)
        layout.addLayout(input_layout)

        # Output Area
        self.output_frame = QFrame()
        self.output_frame.hide()
        out_layout = QHBoxLayout(self.output_frame)
        out_layout.setContentsMargins(0, 0, 0, 0)

        empty_spacer = QWidget()
        empty_spacer.setFixedWidth(50)

        self.out_content = QLabel()
        self.out_content.setProperty("class", "CellOutput")
        self.out_content.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.out_content.setWordWrap(True)

        out_layout.addWidget(empty_spacer)
        out_layout.addWidget(self.out_content)
        layout.addWidget(self.output_frame)

    def set_readonly(self, status):
        self.code_box.setReadOnly(status)
        self.code_box.style().unpolish(self.code_box) # 刷新样式
        self.code_box.style().polish(self.code_box)

    def set_codebox(self, code):
        """"""
        self.code_box.setPlainText(code)

    def set_output(self, text):
        if text.strip():
            # 使用 white-space: pre 保证 ASCII 表格不换行，并设置 Out 标签
            self.out_content.setText(
                f"<div style='color: {COLORS['primary']};\
                    font-weight: bold; margin-bottom: 4px;'>Out:</div>"
                f"<div style='white-space: pre;'>{text}</div>"
            )
            self.output_frame.show()
            QTimer.singleShot(0, self.adjustSize)


class FloatingCommandBar(QFrame):
    submitted = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("FloatingBar")
        self.setFixedWidth(800)
        self.setFixedHeight(120)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(40)
        shadow.setColor(QColor(0, 0, 0, 200))
        shadow.setOffset(0, 10)
        self.setGraphicsEffect(shadow)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)

        self.input = QPlainTextEdit()
        self.input.setProperty("class", "FloatingInput")
        self.input.setPlaceholderText("Enter multi-line code or strategy thoughts...")

        btn_container = QVBoxLayout()
        self.btn = QPushButton("CONFIRM")
        self.btn.setProperty("class", "FloatingConfirmBtn")
        self.btn.setCursor(Qt.PointingHandCursor)
        self.btn.setFixedSize(100, 40)

        btn_container.addStretch()
        btn_container.addWidget(self.btn)

        layout.addWidget(self.input)
        layout.addLayout(btn_container)

        self.btn.clicked.connect(self.send)

    def send(self):
        text = self.input.toPlainText().strip()
        self.submitted.emit(text)
        self.input.clear()


class ChatBubble(QWidget):
    def __init__(self, text, is_user=True):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        self.bubble = QLabel(text)
        self.bubble.setProperty("class", "UserBubble" if is_user else "AiBubble")
        self.bubble.setWordWrap(True)
        self.bubble.setMaximumWidth(300)

        time_str = datetime.datetime.now().strftime("%H:%M")
        meta_label = QLabel(f"{'YOU' if is_user else 'AI'} · {time_str}")
        meta_label.setProperty("class", "BubbleMeta")
        meta_label.setAlignment(Qt.AlignRight if is_user else Qt.AlignLeft)

        v_layout = QVBoxLayout()
        v_layout.setSpacing(2)
        v_layout.addWidget(self.bubble)
        v_layout.addWidget(meta_label)

        if is_user:
            layout.addStretch()
            layout.addLayout(v_layout)
        else:
            layout.addLayout(v_layout)
            layout.addStretch()


class ResearchPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("MainWorkspace")
        self.resize(1300, 900)
        self.execution_count = 1

        self.kernel_manager = QtInProcessKernelManager()
        self.kernel_manager.start_kernel()
        self.kernel = self.kernel_manager.kernel

        self.llm_core = LLMCore()
        self.llm_core.init()
        # self.llm_core.init(
        #     base_url="http://localhost:11434/v1",
        #     model="qwen3:4b-instruct-2507-q4_K_M",
        #     api_key="YOUR_API_KEY"
        # )

        self.init_ui()
        self.create_new_cell()

        self.worker = None

    def init_ui(self):
        self.setStyleSheet(GLOBAL_STYLES)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setObjectName("MainSplitter")
        self.splitter.setHandleWidth(6)

        # 左侧 Notebook
        self.notebook_scroll = QScrollArea()
        self.notebook_scroll.setWidgetResizable(True)
        self.notebook_scroll.setFrameShape(QFrame.NoFrame)

        self.notebook_container = QWidget()
        self.notebook_container.setObjectName("NotebookContainer")
        self.notebook_container.setAttribute(Qt.WA_StyledBackground)
        self.notebook_layout = QVBoxLayout(self.notebook_container)
        self.notebook_layout.setAlignment(Qt.AlignTop)
        self.notebook_layout.setContentsMargins(30, 30, 30, 150)
        self.notebook_layout.addStretch(1) # 关键弹簧：让内容靠顶

        self.notebook_scroll.setWidget(self.notebook_container)

        # 右侧 Chat
        self.chat_panel = QWidget()
        self.chat_panel.setObjectName("ChatPanel")
        self.chat_panel.setAttribute(Qt.WA_StyledBackground)
        self.chat_panel.setMinimumWidth(300)

        chat_vbox = QVBoxLayout(self.chat_panel)
        chat_vbox.setContentsMargins(0, 0, 0, 0)

        chat_header = QLabel("  QUANT AI ASSISTANT")
        chat_header.setFixedHeight(50)
        chat_header.setStyleSheet(f"""
            font-weight: bold; color: {COLORS['primary']};
            border-bottom: 1px solid {COLORS['outline']}33;
        """
        )

        self.chat_scroll = QScrollArea()
        self.chat_scroll.setWidgetResizable(True)
        self.chat_scroll.setFrameShape(QFrame.NoFrame)
        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.setAlignment(Qt.AlignTop)
        self.chat_scroll.setWidget(self.chat_container)

        chat_vbox.addWidget(chat_header)
        chat_vbox.addWidget(self.chat_scroll)

        self.splitter.addWidget(self.notebook_scroll)
        self.splitter.addWidget(self.chat_panel)
        self.splitter.setSizes([1000, 300])

        main_layout.addWidget(self.splitter)

        # 悬浮条
        self.floating_bar = FloatingCommandBar(self)
        self.floating_bar.submitted.connect(self.handle_execution)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        bar_x = (self.width() - self.floating_bar.width()) // 2
        bar_y = self.height() - 140
        self.floating_bar.move(bar_x, bar_y)
        self.floating_bar.raise_()

    def create_new_cell(self, code=None):
        self.active_cell = NotebookCell(self.execution_count, code)
        # 插入到弹簧上方
        self.notebook_layout.insertWidget(self.notebook_layout.count() - 1, self.active_cell)
        self.execution_count += 1

    def handle_execution(self, text):
        """"""
        if text:
            # 如有聊天框有内容，就在右边创建聊天气泡并显示
            self.chat_layout.addWidget(ChatBubble(text, is_user=True))

        code = self.active_cell.code_box.toPlainText()
        if code or text:
            self.worker = WorkflowThread(self.llm_core, code, text, self.execute_python)
            self.worker.step_started.connect(lambda c: print(c))
            self.worker.initial_executed.connect(self.show_code_output)
            self.worker.chunk_received.connect(lambda c: print(c, end="", flush=True))
            self.worker.chunk_finished.connect(self.show_llm_chat)
            self.worker.ai_code_analysised.connect(self.add_llm_code)
            self.worker.finished.connect(lambda c: print(c))
            self.worker.start()

    def show_code_output(self, text):
        self.active_cell.set_output(text)
        self.active_cell.set_readonly(True)
        self.create_new_cell()

    def show_llm_chat(self, text):
        """对话框生成辅助对话"""
        self.chat_layout.addWidget(
            ChatBubble(
                f"[{self.execution_count-1}]:{"\n"}{text}.",
                is_user=False
            )
        )

    def add_llm_code(self, text):
        """左侧添加有内容的代码框"""
        if self.active_cell.code_box.toPlainText():
            self.create_new_cell(text)

            # 自动滚动
            QTimer.singleShot(50, lambda: self.notebook_scroll.verticalScrollBar().setValue(
                self.notebook_scroll.verticalScrollBar().maximum()
            ))
        else:
            self.active_cell.set_codebox(text)

    def execute_python(self, code):
        f = io.StringIO()
        with redirect_stdout(f), redirect_stderr(f):
            try:
                res = self.kernel.shell.run_cell(code)
                if res.result is not None:
                    print(res.result)
            except Exception as e:
                print(f"Error: {e}")
        return f.getvalue()


class WorkflowThread(QThread):
    """"""
    step_started = Signal(str)
    initial_executed = Signal(str)
    chunk_received = Signal(str)
    chunk_finished = Signal(str)
    ai_code_analysised = Signal(str)
    finished = Signal(str)

    def __init__(self, core: LLMCore, initial_script, initial_prompt, execute_code):
        super().__init__()
        self.core = core
        self.initial_script = initial_script
        self.initial_prompt = initial_prompt
        self.execute_code = execute_code

    def run(self):
        if self.initial_script:
            # check if input code
            self.step_started.emit("running initial script...")
            initial_output = self.execute_code(self.initial_script)
            self.initial_executed.emit(initial_output)
        else:
            initial_output= ""

        if self.initial_prompt:
            # check if input prompt
            self.step_started.emit("request llm analysis...")
            prompt = f"""
                我新运行的函数是{self.initial_script}
                运行的结果是{initial_output}
                我新的需求是{self.initial_prompt}
            """

            full_llm_response = ""
            for chunk in self.core.ask_stream(prompt):
                full_llm_response += chunk
                self.chunk_received.emit(chunk) # 实时推送到 UI 气泡

            self.step_started.emit("llm analysis finished")
            self.chunk_finished.emit(full_llm_response)

            self.step_started.emit("extracting code...")
            ai_code = self.core.extract_code(full_llm_response)

            if ai_code:
                self.step_started.emit("code extracted")
                self.ai_code_analysised.emit(ai_code)
                self.finished.emit("llm code generation finished")
            else:
                self.finished.emit("no llm code generated")
