import sys

from PySide6.QtCore import QDateTime, QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QCalendarWidget,
    QComboBox,
    QDateTimeEdit,
    QDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListView,
    QProxyStyle,
    QPushButton,
    QStyle,
    QStyledItemDelegate,
    QVBoxLayout,
)

from ....utilities import load_source

QSS = """
QDialog {
    background-color: #181210;
    color: #ede0dc;
    font-family: 'Inter', sans-serif;
}

QLabel#mainTitle {
    color: #e9c349; font-size: 24px; font-weight: bold; font-family: 'Manrope', sans-serif;
}
QLabel#subTitle { color: #d5c5a8; font-size: 13px; font-weight: 500; }
QLabel#fieldLabel { color: #9b8e87; font-size: 11px; font-weight: bold; letter-spacing: 1px; }

/* 强制所有输入框组件统一高度和内边距，实现完美对称 */
QLineEdit, QComboBox, QDateTimeEdit {
    background-color: #3b3331;
    color: #ede0dc;
    border: 1px solid transparent;
    border-radius: 8px;
    padding: 12px 16px;
    font-size: 13px;
    min-height: 20px;
}
QLineEdit:focus, QComboBox:focus, QDateTimeEdit:focus {
    border: 1px solid rgba(233, 195, 73, 0.6);
}
QComboBox::drop-down, QDateTimeEdit::drop-down { border: none; width: 24px; }
QComboBox::down-arrow, QDateTimeEdit::down-arrow { image: none; }

QComboBox QFrame {
    background-color: #251e1c;
    border: 1px solid #4f453f;
    border-radius: 6px;
    padding: 0px;
    margin: 0px;
}
#comboView { background-color: #251e1c; border: none; outline: none; padding: 4px; }
#comboView::item {
    color: #ede0dc; min-height: 35px; padding-left: 10px; border: none; border-radius: 4px;
}
#comboView::item:selected { background-color: #3b3331; color: #e9c349; }

QFrame#segmentFrame { background-color: #3b3331; border-radius: 8px; }

/* 调整频率按钮容器，使其高度和输入框完全一致 */
QFrame#freqFrame {
    background-color: #3b3331;
    border-radius: 8px;
    padding: 2px;
    min-height: 40px;
}

QPushButton#modeButton {
    background-color: transparent; color: #9b8e87; border: none; padding: 10px 0;
    font-weight: bold; font-size: 13px; border-radius: 6px;
}
QPushButton#modeButton:checked { background-color: #2f2826; color: #e9c349; }
QPushButton#modeButton:hover:!checked { color: #ede0dc; }

QPushButton#freqButton {
    background-color: transparent; color: #9b8e87; border: none; padding: 8px 0;
    font-weight: bold; font-size: 11px; border-radius: 6px;
}
QPushButton#freqButton:checked { background-color: #181210; color: #e9c349; }
QPushButton#freqButton:hover:!checked { color: #ede0dc; }

QPushButton#startButton {
    background-color: #e9c349; color: #241a00; border: none; border-radius: 8px;
    font-weight: bold; font-size: 15px; font-family: 'Manrope', sans-serif; padding: 16px;
}
QPushButton#startButton:hover { background-color: #ffe088; }
QPushButton#startButton:pressed { background-color: #b59319; }

QPushButton#cancelButton {
    background-color: transparent; color: #9b8e87; border: none;
    font-weight: bold; font-size: 12px; padding: 8px;
}
QPushButton#cancelButton:hover { color: #ede0dc; }

QCalendarWidget QWidget { background-color: #3b3331; color: #ede0dc; }
QCalendarWidget QAbstractItemView {
    background-color: #181210; selection-background-color: #e9c349; selection-color: #241a00;
}
"""


# --- 核心黑科技：强制消除原生边框的代理样式 ---
class DarkComboStyle(QProxyStyle):
    def styleHint(self, hint, option=None, widget=None, returnData=None):
        if hint == QStyle.SH_ComboBox_Popup:
            return 0
        return super().styleHint(hint, option, widget, returnData)


class DataAcquisitionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Data Acquisition")
        self.setMinimumWidth(680) # 稍微加宽一点，让左右两列更有呼吸感
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        self.setup_ui()
        self.apply_stylesheet()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(36, 32, 36, 32)
        main_layout.setSpacing(24)

        # ---------------- 1. 头部 & 模式切换 ----------------
        header_layout = QVBoxLayout()
        header_layout.setAlignment(Qt.AlignCenter)
        header_layout.setSpacing(8)

        title_label = QLabel("Market Data Recorder")
        title_label.setObjectName("mainTitle")
        title_label.setAlignment(Qt.AlignCenter)

        subtitle_label = QLabel("Configure your vault acquisition parameters")
        subtitle_label.setObjectName("subTitle")
        subtitle_label.setAlignment(Qt.AlignCenter)

        # 模式切换 (Segmented Control)
        mode_frame = QFrame()
        mode_frame.setObjectName("segmentFrame")
        mode_frame.setFixedWidth(420)
        mode_layout = QHBoxLayout(mode_frame)
        mode_layout.setContentsMargins(4, 4, 4, 4)
        mode_layout.setSpacing(0)

        self.mode_group = QButtonGroup(self)
        for i, text in enumerate(["Download Historical Data", "Record Live Data"]):
            btn = QPushButton(text)
            btn.setCheckable(True)
            btn.setObjectName("modeButton")
            if i == 0:
                btn.setChecked(True)
            self.mode_group.addButton(btn, i)
            mode_layout.addWidget(btn)

        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        header_layout.addSpacing(16)
        header_layout.addWidget(mode_frame, alignment=Qt.AlignCenter)

        main_layout.addLayout(header_layout)
        main_layout.addSpacing(10)

        # ---------------- 2. 表单配置区 (完美的 6 宫格对称布局) ----------------
        form_grid = QGridLayout()
        form_grid.setHorizontalSpacing(24) # 左右列的间距
        form_grid.setVerticalSpacing(20)   # 上下行的间距

        # 强制强制两列宽度绝对一致 (1:1 比例)
        form_grid.setColumnStretch(0, 1)
        form_grid.setColumnStretch(1, 1)

        # [第 1 行，第 1 列] Data Interface
        interface_box = QVBoxLayout()
        interface_box.setSpacing(8)
        interface_box.addWidget(self.create_label("DATA INTERFACE"))
        self.combo_interface = QComboBox()
        self.combo_interface.addItems(
            ["Binance Professional", "Interactive Brokers TWS",
             "OKX Exchange API", "Coinbase Prime"]
        )
        self.apply_dark_combo_style(self.combo_interface)
        interface_box.addWidget(self.combo_interface)
        form_grid.addLayout(interface_box, 0, 0)

        # [第 1 行，第 2 列] Contract Code / Symbol
        symbol_box = QVBoxLayout()
        symbol_box.setSpacing(8)
        symbol_box.addWidget(self.create_label("CONTRACT CODE / SYMBOL"))
        self.input_symbol = QLineEdit()
        self.input_symbol.setPlaceholderText("e.g. BTC/USDT")
        symbol_box.addWidget(self.input_symbol)
        form_grid.addLayout(symbol_box, 0, 1)

        # [第 2 行，第 1 列] Start Time
        start_time_box = QVBoxLayout()
        start_time_box.setSpacing(8)
        start_time_box.addWidget(self.create_label("START TIME (UTC)"))
        self.dt_start = self.create_datetime_edit()
        start_time_box.addWidget(self.dt_start)
        form_grid.addLayout(start_time_box, 1, 0)

        # [第 2 行，第 2 列] End Time
        end_time_box = QVBoxLayout()
        end_time_box.setSpacing(8)
        end_time_box.addWidget(self.create_label("END TIME (UTC)"))
        self.dt_end = self.create_datetime_edit()
        end_time_box.addWidget(self.dt_end)
        form_grid.addLayout(end_time_box, 1, 1)

        #[第 3 行，第 1 列] Data Granularity
        freq_box = QVBoxLayout()
        freq_box.setSpacing(8)
        freq_box.addWidget(self.create_label("DATA GRANULARITY"))

        freq_frame = QFrame()
        freq_frame.setObjectName("freqFrame") # 独立名字以便精确控制高度
        freq_layout = QHBoxLayout(freq_frame)
        freq_layout.setContentsMargins(4, 4, 4, 4)
        freq_layout.setSpacing(2)

        self.freq_group = QButtonGroup(self)
        for i, text in enumerate(["TICK", "1M", "5M", "1H", "1D"]):
            btn = QPushButton(text)
            btn.setCheckable(True)
            btn.setObjectName("freqButton")
            if text == "TICK":
                btn.setChecked(True)
            self.freq_group.addButton(btn, i)
            freq_layout.addWidget(btn)
        freq_box.addWidget(freq_frame)
        form_grid.addLayout(freq_box, 2, 0)

        #[第 3 行，第 2 列] Save To Vault
        storage_box = QVBoxLayout()
        storage_box.setSpacing(8)
        storage_box.addWidget(self.create_label("SAVE TO VAULT"))
        self.combo_storage = QComboBox()
        self.combo_storage.addItems(
            ["QuestDB Cluster (High-Perf)", "PostgreSQL Timescale",
             "Local NVMe RAID-0", "S3 Cold Storage"]
        )
        self.apply_dark_combo_style(self.combo_storage)
        storage_box.addWidget(self.combo_storage)
        form_grid.addLayout(storage_box, 2, 1)

        # 将配置网格加入主布局
        main_layout.addLayout(form_grid)
        main_layout.addStretch()

        # ---------------- 3. 底部操作区 ----------------
        footer_layout = QVBoxLayout()
        footer_layout.setSpacing(12)

        start_btn = QPushButton("Start Download")
        start_btn.setIcon(
            QIcon(str(load_source("src", "icons", "download_dark.svg"))).pixmap(QSize(30, 30))
        )
        start_btn.setObjectName("startButton")
        start_btn.clicked.connect(self.accept)

        cancel_btn = QPushButton("Cancel Acquisition")
        cancel_btn.setObjectName("cancelButton")
        cancel_btn.clicked.connect(self.reject)

        footer_layout.addWidget(start_btn)
        footer_layout.addWidget(cancel_btn)

        main_layout.addLayout(footer_layout)

    def create_label(self, text):
        label = QLabel(text)
        label.setObjectName("fieldLabel")
        return label

    def create_datetime_edit(self):
        dt_edit = QDateTimeEdit()
        dt_edit.setCalendarPopup(True)
        dt_edit.setDateTime(QDateTime.currentDateTime())
        dt_edit.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        calendar = QCalendarWidget()
        calendar.setGridVisible(True)
        dt_edit.setCalendarWidget(calendar)
        return dt_edit

    def apply_dark_combo_style(self, combo_box: QComboBox):
        combo_box.setStyle(DarkComboStyle())
        view = QListView()
        view.setObjectName("comboView")
        combo_box.setView(view)
        combo_box.setItemDelegate(QStyledItemDelegate(combo_box))

        container = combo_box.view().window()
        container.setAttribute(Qt.WA_StyledBackground)
        container.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint)

    def get_configuration(self):
        mode_btn = self.mode_group.checkedButton()
        freq_btn = self.freq_group.checkedButton()
        return {
            "mode": mode_btn.text() if mode_btn else "Unknown",
            "interface": self.combo_interface.currentText(),
            "symbol": self.input_symbol.text(),
            "start_time": self.dt_start.dateTime().toPython(),
            "end_time": self.dt_end.dateTime().toPython(),
            "granularity": freq_btn.text() if freq_btn else "Unknown",
            "storage": self.combo_storage.currentText()
        }

    def apply_stylesheet(self):
        self.setStyleSheet(QSS)

if __name__ == "__main__":
    sys.argv +=['-style', 'Fusion']
    app = QApplication(sys.argv)

    dialog = DataAcquisitionDialog()
    if dialog.exec():
        print("====== 接收到下载指令 ======")
        config = dialog.get_configuration()
        for k, v in config.items():
            print(f"{k:>15}: {v}")
    else:
        print("已取消操作")
