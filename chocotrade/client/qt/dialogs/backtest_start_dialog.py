import sys

from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QCalendarWidget,
    QComboBox,
    QDateEdit,
    QDialog,
    QDoubleSpinBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListView,
    QProxyStyle,
    QPushButton,
    QSpinBox,
    QStyle,
    QStyledItemDelegate,
    QVBoxLayout,
)


# --- 核心黑科技：强制消除原生边框的代理样式 ---
class DarkComboStyle(QProxyStyle):
    def styleHint(self, hint, option=None, widget=None, returnData=None):
        # 强制禁用弹出菜单的阴影和系统原生边框，防止白边溢出
        if hint == QStyle.SH_ComboBox_Popup:
            return 0
        return super().styleHint(hint, option, widget, returnData)


class BacktestConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configure Backtest Engine")
        self.setMinimumWidth(600)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        self.setup_ui()
        self.apply_stylesheet()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ---------------- 头部 (Header) ----------------
        header_frame = QFrame()
        header_frame.setObjectName("headerFrame")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(30, 20, 30, 20)

        title_layout = QVBoxLayout()
        title_label = QLabel("Configure Backtest Engine")
        title_label.setObjectName("mainTitle")
        subtitle_label = QLabel("Initialize high-frequency simulation environment")
        subtitle_label.setObjectName("subTitle")
        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle_label)

        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        main_layout.addWidget(header_frame)

        # ---------------- 内容区 (Content) ----------------
        content_frame = QFrame()
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(30, 25, 30, 25)
        content_layout.setSpacing(25)

        grid_layout = QGridLayout()
        grid_layout.setSpacing(15)

        # 策略名称
        grid_layout.addWidget(self.create_label("STRATEGY NAME"), 0, 0, 1, 2)
        self.strategy_input = QLineEdit("Momentum_Arbitrage_v4")
        grid_layout.addWidget(self.strategy_input, 1, 0, 1, 2)

        # 数据源 (完美暗黑下拉框 - 绝杀方案)
        grid_layout.addWidget(self.create_label("DATABASE SOURCE"), 2, 0)
        self.db_combo = QComboBox()

        # 1. 应用自定义代理样式 (干掉系统默认弹出框行为)
        self.db_combo.setStyle(DarkComboStyle())

        # 2. 使用独立的 QListView 并设置属性
        view = QListView()
        view.setObjectName("comboView")
        self.db_combo.setView(view)

        # 3. 剥夺系统原生绘制，防止重叠
        self.db_combo.setItemDelegate(QStyledItemDelegate(self.db_combo))

        # 4. 强制底层属性，确保 QSS 能够完整覆盖到边缘
        container = self.db_combo.view().window()
        container.setAttribute(Qt.WA_StyledBackground)
        container.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint)

        self.db_combo.addItems(
            ["PostgreSQL Cluster", "TimeScaleDB", "InfluxDB Core", "Local CSV Cache"]
        )
        grid_layout.addWidget(self.db_combo, 3, 0)

        # 频率选择
        grid_layout.addWidget(self.create_label("FREQUENCY"), 2, 1)
        freq_frame = QFrame()
        freq_frame.setObjectName("freqFrame")
        freq_layout = QHBoxLayout(freq_frame)
        freq_layout.setContentsMargins(2, 2, 2, 2)
        freq_layout.setSpacing(2)

        self.freq_group = QButtonGroup(self)
        for i, text in enumerate(["1m", "5m", "15m", "1h"]):
            btn = QPushButton(text)
            btn.setCheckable(True)
            btn.setObjectName("freqButton")
            if text == "5m":
                btn.setChecked(True)
            self.freq_group.addButton(btn, i)
            freq_layout.addWidget(btn)
        grid_layout.addWidget(freq_frame, 3, 1)

        # 开始日期 & 结束日期
        grid_layout.addWidget(self.create_label("START DATE"), 4, 0)
        self.start_date = self.create_date_edit(2023, 1, 1)
        grid_layout.addWidget(self.start_date, 5, 0)

        grid_layout.addWidget(self.create_label("END DATE"), 4, 1)
        self.end_date = self.create_date_edit(2023, 12, 31)
        grid_layout.addWidget(self.end_date, 5, 1)

        content_layout.addLayout(grid_layout)

        # --- 优化参数区 ---
        opt_frame = QFrame()
        opt_frame.setObjectName("optFrame")
        opt_layout = QVBoxLayout(opt_frame)
        opt_layout.setContentsMargins(20, 20, 20, 20)

        opt_title = QLabel("⚙  Optimization Parameters")
        opt_title.setObjectName("sectionTitle")
        opt_layout.addWidget(opt_title)
        opt_layout.addSpacing(10)

        opt_grid = QGridLayout()
        opt_grid.setColumnStretch(0, 1)
        opt_grid.setColumnStretch(2, 1)

        opt_grid.addWidget(QLabel("Fast EMA Period"), 0, 0)
        self.fast_ema = QSpinBox()
        self.fast_ema.setValue(12)
        opt_grid.addWidget(self.fast_ema, 0, 1)

        opt_grid.addWidget(QLabel("Slow EMA Period"), 1, 0)
        self.slow_ema = QSpinBox()
        self.slow_ema.setValue(26)
        opt_grid.addWidget(self.slow_ema, 1, 1)

        opt_grid.addWidget(QLabel("RSI Threshold"), 0, 2)
        self.rsi_thresh = QSpinBox()
        self.rsi_thresh.setValue(30)
        opt_grid.addWidget(self.rsi_thresh, 0, 3)

        opt_grid.addWidget(QLabel("Trailing Stop %"), 1, 2)
        self.trail_stop = QDoubleSpinBox()
        self.trail_stop.setValue(1.5)
        self.trail_stop.setSingleStep(0.1)
        opt_grid.addWidget(self.trail_stop, 1, 3)

        opt_layout.addLayout(opt_grid)
        content_layout.addWidget(opt_frame)

        main_layout.addWidget(content_frame)

        # ---------------- 底部操作区 (Footer) ----------------
        footer_frame = QFrame()
        footer_frame.setObjectName("footerFrame")
        footer_layout = QHBoxLayout(footer_frame)
        footer_layout.setContentsMargins(30, 15, 30, 15)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("cancelButton")
        cancel_btn.clicked.connect(self.reject)

        start_btn = QPushButton("▶  Start Backtest")
        start_btn.setObjectName("startButton")
        start_btn.clicked.connect(self.accept)

        footer_layout.addStretch()
        footer_layout.addWidget(cancel_btn)
        footer_layout.addWidget(start_btn)

        main_layout.addWidget(footer_frame)

    def create_label(self, text):
        label = QLabel(text)
        label.setObjectName("fieldLabel")
        return label

    def create_date_edit(self, year, month, day):
        date_edit = QDateEdit()
        date_edit.setCalendarPopup(True)
        date_edit.setDate(QDate(year, month, day))
        date_edit.setDisplayFormat("yyyy-MM-dd")
        calendar = QCalendarWidget()
        calendar.setGridVisible(True)
        date_edit.setCalendarWidget(calendar)
        return date_edit

    def get_results(self):
        """打包所有配置数据"""
        return {
            "strategy_name": self.strategy_input.text(),
            "database": self.db_combo.currentText(),
            "frequency": self.freq_group.checkedButton().text(), # 获取选中的按钮文字
            "start_date": self.start_date.date().toPython(),    # 转为 Python datetime.date
            "end_date": self.end_date.date().toPython(),
            "fast_ema": self.fast_ema.value(),
            "slow_ema": self.slow_ema.value(),
            "rsi_threshold": self.rsi_thresh.value(),
            "trailing_stop": self.trail_stop.value()
        }

    def apply_stylesheet(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #181210;
                color: #ede0dc;
                font-family: 'Inter', sans-serif;
            }
            QFrame#headerFrame {
                background-color: #251e1c; border-bottom: 1px solid rgba(79, 69, 63, 0.4);
            }
            QFrame#footerFrame {
                background-color: #201a18; border-top: 1px solid rgba(79, 69, 63, 0.4);
            }
            QFrame#optFrame {
                background-color: rgba(32, 26, 24, 0.8);
                border: 1px solid rgba(79, 69, 63, 0.4); border-radius: 8px;
            }

            QLabel#mainTitle { color: #e9c349; font-size: 20px; font-weight: bold; }
            QLabel#subTitle { color: #9b8e87; font-size: 11px; }
            QLabel#fieldLabel { color: #d5c5a8; font-size: 10px; font-weight: bold; }
            QLabel { color: #d2c4bc; font-size: 13px; }

            QLineEdit, QComboBox, QDateEdit, QSpinBox, QDoubleSpinBox {
                background-color: #3b3331;
                color: #ede0dc;
                border: 1px solid transparent;
                border-radius: 6px;
                padding: 8px 12px;
            }
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus {
                border: 1px solid rgba(233, 195, 73, 0.6);
            }

            /* --- 终极下拉框 QSS：核心是针对容器和 View 进行彻底覆盖 --- */

            /* 1. 这是弹窗的最底层容器，设置它来消除任何漏出的白边 */
            QComboBox QFrame {
                background-color: #251e1c;
                border: 1px solid #4f453f;
                border-radius: 4px;
                padding: 0px;
                margin: 0px;
            }

            /* 2. 这是内部的列表视图，确保它完全填满容器且无额外边距 */
            #comboView {
                background-color: #251e1c;
                border: none;
                outline: none;
                padding: 2px;
            }

            #comboView::item {
                color: #ede0dc;
                min-height: 35px;
                padding-left: 10px;
                border: none;
                border-radius: 3px;
            }

            #comboView::item:selected {
                background-color: #3b3331;
                color: #e9c349;
            }

            /* 频率切换按钮样式 */
            QFrame#freqFrame { background-color: #3b3331; border-radius: 6px; }
            QPushButton#freqButton {
                background-color: transparent;
                color: #9b8e87; border: none; padding: 6px 0; font-weight: bold;
            }
            QPushButton#freqButton:checked { background-color: #4f453f; color: #e9c349; }

            /* 底部按钮样式 */
            QPushButton#cancelButton { color: #9b8e87; border: none; font-weight: bold; }
            QPushButton#startButton {
                background-color: #e9c349; color: #241a00; border: none; border-radius: 6px;
                font-weight: bold; padding: 10px 24px;
            }

            QScrollBar:vertical { background: #181210; width: 8px; }
            QScrollBar::handle:vertical { background: #4f453f; border-radius: 4px; }

            /* 日历样式微调 */
            QCalendarWidget QWidget { background-color: #3b3331; color: #ede0dc; }
            QCalendarWidget QAbstractItemView {
                background-color: #181210; selection-background-color: #e9c349;
            }
        """)

if __name__ == "__main__":
    # 使用 Fusion 风格作为底座
    sys.argv += ['-style', 'Fusion']
    app = QApplication(sys.argv)

    dialog = BacktestConfigDialog()
    if dialog.exec():
        print("Done")
