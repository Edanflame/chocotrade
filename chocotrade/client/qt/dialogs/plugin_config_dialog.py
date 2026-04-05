from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)

from ....utilities import load_source

COLORS = {
    "background": "#181210",
    "surface": "#181210",
    "surface_container": "#251e1c",
    "surface_container_low": "#201a18",
    "surface_container_highest": "#3b3331",
    "primary": "#e9c349",
    "on_primary": "#3c2f00",
    "primary_container": "#3b2d00",
    "on_primary_container": "#b59319",
    "secondary": "#f9ba82",
    "tertiary": "#d5c5a8",
    "on_surface": "#ede0dc",
    "on_surface_variant": "#d2c4bc",
    "outline_variant": "#4f453f",
    "error": "#ffb4ab",
    "success": "#4ade80"
}


# ==========================================
# 1. 独立弹窗：Plugin Configuration Dialog
# ==========================================
class PluginConfigDialog(QDialog):
    def __init__(self, plugin_name, config, current_config, parent=None):
        super().__init__(parent)
        self.config = config
        self.current_config = current_config

        self.setWindowTitle("Plugin Configuration")
        self.setFixedSize(760, 480)

        self.setStyleSheet(f"""
            * {{ outline: none; }}
            QDialog {{
                background-color: {COLORS['surface_container']};
            }}
            QLabel {{
                color: {COLORS['on_surface']};
                font-family: 'Inter', sans-serif;
            }}
            QLineEdit {{
                background-color: {COLORS['surface_container_highest']};
                border: none;
                border-radius: 8px;
                padding: 12px;
                color: {COLORS['on_surface']};
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border: none;
            }}
            QPushButton#btnSave {{
                background-color: {COLORS['primary']};
                color: {COLORS['on_primary']};
                font-weight: bold;
                border-radius: 8px;
                padding: 12px;
            }}
            QPushButton#btnSave:hover {{
                background-color: #fce47c;
            }}
            QPushButton#btnTest {{
                background-color: {COLORS['surface_container_highest']};
                color: {COLORS['on_surface']};
                font-weight: bold;
                border-radius: 8px;
                padding: 12px;
            }}
            QPushButton#btnTest:hover {{
                background-color: #4a403d;
            }}
            QPushButton.IconBtn {{
                background: transparent;
                border: none;
                border-radius: 4px;
                padding: 4px;
            }}
            QPushButton.IconBtn:hover {{
                background: {COLORS['surface_container_highest']};
            }}
            QFrame#StatusFrame {{
                background-color: {COLORS['surface_container_low']};
                border-radius: 12px;
                border: 1px solid rgba(79, 69, 63, 0.3);
            }}
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(35, 35, 35, 35)
        main_layout.setSpacing(30)

        # --- 以下代码保持完全不变 ---
        # --- 头部 ---
        header_hlayout = QHBoxLayout()
        header_text_vbox = QVBoxLayout()
        header_text_vbox.setSpacing(4)
        title = QLabel("Plugin Configuration")
        title.setStyleSheet(f"""
            font-size: 24px; font-weight: bold; font-family: 'Manrope', sans-serif;
            background-color: {COLORS['surface_container']};
        """)
        subtitle = QLabel(f"Advanced settings for {plugin_name}")
        subtitle.setStyleSheet(f"""
            color: {COLORS['on_surface_variant']}; font-size: 13px;
            background-color: {COLORS['surface_container']};
        """)
        header_text_vbox.addWidget(title)
        header_text_vbox.addWidget(subtitle)

        # 头部右上角 Icon 按钮
        btn_help = QPushButton()
        btn_help.setProperty("class", "IconBtn")
        btn_help.setIcon(QIcon(str(load_source("src", "icons", "help.svg"))))
        btn_help.setCursor(Qt.PointingHandCursor)

        btn_close = QPushButton()
        btn_close.setProperty("class", "IconBtn")
        btn_close.setIcon(QIcon(str(load_source("src", "icons", "close.svg"))))
        btn_close.setCursor(Qt.PointingHandCursor)
        btn_close.clicked.connect(self.reject)

        header_hlayout.addLayout(header_text_vbox)
        header_hlayout.addStretch()
        header_hlayout.addWidget(btn_help, alignment=Qt.AlignTop)
        header_hlayout.addWidget(btn_close, alignment=Qt.AlignTop)

        main_layout.addLayout(header_hlayout)

        # --- 表单区 (左右两列) ---
        form_layout = QHBoxLayout()
        form_layout.setSpacing(48)

        # 左列：输入框
        left_col = QVBoxLayout()
        left_col.setSpacing(16)

        def create_input_group(label_text, widget):
            vbox = QVBoxLayout()
            vbox.setSpacing(8)
            lbl = QLabel(label_text)
            lbl.setStyleSheet(f"""
                color: {COLORS['tertiary']}; font-weight: bold; font-size: 11px;
                letter-spacing: 1px; background-color: {COLORS['surface_container']};
            """)
            vbox.addWidget(lbl)
            vbox.addWidget(widget)
            return vbox

        for field in self.config["auth_fields"]:
            # 1. 初始化 QLineEdit，建议不要放 "***"，而是设置模式
            tmp = QLineEdit()
            tmp.setEchoMode(QLineEdit.Password) # 默认为隐藏模式
            # 如果有旧值，可以填入实际值而非星号
            tmp.setText(self.current_config.get(field, ""))

            # 2. 添加 Action 并获取引用 (保存为 action 变量)
            # 初始图标建议显示“不可见”状态
            action = tmp.addAction(
                QIcon(str(load_source("src", "icons", "visibility_off.svg"))),
                QLineEdit.TrailingPosition
            )

            # 3. 核心：使用 lambda 锁定当前的 tmp 和 action
            # 注意：t=tmp, a=action 是为了在循环中捕捉当前迭代的对象
            action.triggered.connect(
                lambda checked=False, t=tmp, a=action: self.toggle_password_view(t, a)
            )

            # 4. 绑定到 self 并添加到布局
            setattr(self, field, tmp)
            left_col.addLayout(create_input_group(field.upper(), getattr(self, field)))

        # self.inp_endpoint = QLineEdit("wss://stream.binance.com:9443/ws")
        # self.inp_key = QLineEdit("AKIA****************")
        # self.inp_key.setEchoMode(QLineEdit.Password)

        # # 在输入框右侧添加 visibility 图标
        # self.inp_key.addAction(
        #     QIcon(str(load_source("src", "icons", "visibility.svg"))), QLineEdit.TrailingPosition
        # )

        # left_col.addLayout(create_input_group("API ENDPOINT", self.inp_endpoint))
        # left_col.addLayout(create_input_group("ACCESS KEY ID", self.inp_key))

        # # 滑动条
        # slider_vbox = QVBoxLayout()
        # slider_vbox.setSpacing(8)
        # lbl_rate = QLabel("RATE LIMIT (REQ/SEC)")
        # lbl_rate.setStyleSheet(f"""
        #     color: {COLORS['tertiary']}; font-weight: bold; font-size: 11px;
        #     letter-spacing: 1px; background-color: {COLORS['surface_container']};
        # """)

        # slider_hbox = QHBoxLayout()
        # self.slider = QSlider(Qt.Horizontal)
        # self.slider.setRange(100, 1000)
        # self.slider.setValue(500)
        # self.slider.setStyleSheet(f"background-color: {COLORS['surface_container']};")
        # self.lbl_slider_val = QLabel("500")
        # self.lbl_slider_val.setStyleSheet(f"""
        #     color: {COLORS['primary']}; font-weight: bold;
        #     font-size: 14px; background-color: {COLORS['surface_container']};
        # """)
        # self.slider.valueChanged.connect(lambda v: self.lbl_slider_val.setText(str(v)))

        # slider_hbox.addWidget(self.slider)
        # slider_hbox.addWidget(self.lbl_slider_val)
        # slider_vbox.addWidget(lbl_rate)
        # slider_vbox.addLayout(slider_hbox)
        # left_col.addLayout(slider_vbox)
        left_col.addStretch()

        # 右列：状态与按钮
        right_col = QVBoxLayout()
        right_col.setSpacing(24)

        status_frame = QFrame()
        status_frame.setObjectName("StatusFrame")
        status_layout = QVBoxLayout(status_frame)
        status_layout.setContentsMargins(20, 20, 20, 20)
        status_layout.setSpacing(12)

        health_title = QLabel("INSTANCE HEALTH")
        health_title.setStyleSheet(f"""
            color: {COLORS['tertiary']}; font-weight: bold; font-size: 11px;
            letter-spacing: 1px; background-color: {COLORS['surface_container_low']};
        """)
        status_layout.addWidget(health_title)

        def add_stat_row(name, val, val_color=COLORS['on_surface']):
            row = QHBoxLayout()
            lbl_name = QLabel(name)
            lbl_name.setStyleSheet(f"""
                color: {COLORS['on_surface_variant']}; font-size: 13px;
                background-color: {COLORS['surface_container_low']};
            """)
            lbl_val = QLabel(val)
            lbl_val.setStyleSheet(f"""
                color: {val_color}; font-weight: bold; font-size: 13px;
                background-color: {COLORS['surface_container_low']};
            """)
            row.addWidget(lbl_name)
            row.addStretch()
            row.addWidget(lbl_val)
            status_layout.addLayout(row)

        add_stat_row("Uptime", "99.98%")
        add_stat_row("Latent Median", "14ms")
        add_stat_row("Queue Depth", "Optimal", COLORS['success'])
        right_col.addWidget(status_frame)
        right_col.addStretch()

        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        btn_save = QPushButton("Save Changes")
        btn_save.setObjectName("btnSave")
        btn_save.setCursor(Qt.PointingHandCursor)
        btn_save.clicked.connect(self.accept)

        btn_test = QPushButton("Test Connection")
        btn_test.setObjectName("btnTest")
        btn_test.setCursor(Qt.PointingHandCursor)

        btn_layout.addWidget(btn_save)
        btn_layout.addWidget(btn_test)
        right_col.addLayout(btn_layout)

        form_layout.addLayout(left_col, 1)
        form_layout.addLayout(right_col, 1)

        main_layout.addLayout(form_layout)

    def toggle_password_view(self, line_edit, action):
        # 检查当前的模式
        if line_edit.echoMode() == QLineEdit.Password:
            # 切换到普通文本模式
            line_edit.setEchoMode(QLineEdit.Normal)
            # 切换图标为“可见”
            action.setIcon(QIcon(str(load_source("src", "icons", "visibility.svg"))))
        else:
            # 切换回密码模式
            line_edit.setEchoMode(QLineEdit.Password)
            # 切换图标为“不可见”
            action.setIcon(QIcon(str(load_source("src", "icons", "visibility_off.svg"))))

    def get_configuration(self):
        return {
            field: getattr(self, field).text() for field in self.config["auth_fields"]
        }
