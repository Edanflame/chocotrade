from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

# --- 颜色配置 ---
COLORS = {
    "background": "#181210",
    "surface": "#251e1c",
    "surface_high": "#2f2826",
    "surface_highest": "#3b3331",
    "primary": "#e9c349",
    "on_primary": "#3c2f00",
    "on_surface": "#ede0dc",
    "on_surface_variant": "#d2c4bc",
    "outline": "#4f453f",
    "error": "#ffb4ab",
    "success": "#4ade80",
    "tertiary": "#d5c5a8"
}

# =================================================================
# 样式定义 (QSS)
# =================================================================
REPORT_DIALOG_STYLESHEET = f"""
/* ---------------- 基础设置 ---------------- */
QDialog {{
    background-color: {COLORS['background']};
}}

QLabel {{
    color: {COLORS['on_surface']};
}}

/* ---------------- 滚动条样式 ---------------- */
QScrollArea {{
    background: transparent;
    border: none;
}}

QScrollBar:vertical {{
    background: transparent;
    width: 6px;
}}

QScrollBar::handle:vertical {{
    background: {COLORS['outline']};
    border-radius: 3px;
    min-height: 20px;
}}

/* ---------------- KPI 行组件 ---------------- */
#KPIRow {{
    background-color: {COLORS['surface']};
    border-radius: 8px;
    border: 1px solid transparent;
}}

#KPIRow:hover {{
    background-color: {COLORS['surface_high']};
    border: 1px solid rgba(233, 195, 73, 0.1);
}}

.KPILabel {{
    color: {COLORS['on_surface_variant']};
    font-size: 10px;
    font-weight: bold;
    letter-spacing: 1.5px;
}}

.KPIValue {{
    font-size: 28px;
    font-weight: 800;
}}

.KPISubtitle {{
    color: {COLORS['primary']};
    font-size: 10px;
    font-weight: bold;
}}

/* ---------------- Header 元素 ---------------- */
#ValidatedTag {{
    background: rgba(233, 195, 73, 0.1);
    color: {COLORS['primary']};
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 10px;
    font-weight: bold;
}}

#MainTitle {{
    font-size: 36px;
    font-weight: 800;
}}

#SubTitle {{
    color: {COLORS['tertiary']};
    font-size: 14px;
}}

/* ---------------- 按钮样式 ---------------- */
.PrimaryBtn {{
    background-color: {COLORS['primary']};
    color: {COLORS['on_primary']};
    padding: 10px 20px;
    border-radius: 6px;
    font-weight: bold;
}}

.SecondaryBtn {{
    background-color: {COLORS['surface_high']};
    color: white;
    padding: 10px 20px;
    border-radius: 6px;
    font-weight: bold;
}}

#DismissBtn {{
    color: {COLORS['on_surface_variant']};
    border: none;
    font-weight: bold;
    background: transparent;
}}

#DismissBtn:hover {{
    color: {COLORS['primary']};
}}

/* ---------------- 进度条 ---------------- */
QProgressBar {{
    background: {COLORS['surface_highest']};
    border-radius: 4px;
    border: none;
    text-align: center;
}}

QProgressBar::chunk {{
    background: {COLORS['primary']};
    border-radius: 4px;
}}

/* ---------------- 参数优化区块 ---------------- */
#OptBox {{
    background-color: {COLORS['surface_high']};
    border-radius: 12px;
    border: 1px solid rgba(79, 69, 63, 0.2);
}}

#OptTitle {{
    font-size: 20px;
    font-weight: bold;
}}

QLineEdit {{
    background: {COLORS['surface_highest']};
    border: 1px solid transparent;
    border-radius: 6px;
    padding: 10px;
    color: {COLORS['primary']};
    font-size: 16px;
    font-weight: bold;
}}

QLineEdit:focus {{
    border: 1px solid {COLORS['primary']};
}}

/* ---------------- 页脚 ---------------- */
#FooterInfo {{
    color: {COLORS['on_surface_variant']};
    font-size: 9px;
    letter-spacing: 2px;
}}
"""

# =================================================================
# 组件实现
# =================================================================

class KPIRow(QFrame):
    def __init__(self, label, value, value_color=COLORS['on_surface']):
        super().__init__()
        self.setObjectName("KPIRow")
        self.setFixedHeight(90)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)

        # 1. 标签和数值
        val_box = QVBoxLayout()
        l_lbl = QLabel(label.upper())
        l_lbl.setProperty("class", "KPILabel")

        v_lbl = QLabel(value)
        v_lbl.setProperty("class", "KPIValue")
        v_lbl.setStyleSheet(f"color: {value_color};") # 特殊数值颜色保持内联

        val_box.addWidget(l_lbl)
        val_box.addWidget(v_lbl)
        layout.addLayout(val_box, 1)

        # 2. 中间可视化占位
        self.viz_container = QWidget()
        self.viz_layout = QHBoxLayout(self.viz_container)
        self.viz_layout.setContentsMargins(40, 0, 40, 0)
        layout.addWidget(self.viz_container, 2)

        # 3. 右侧说明
        self.info_box = QVBoxLayout()
        self.info_box.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layout.addLayout(self.info_box, 1)

    def add_viz(self, widget):
        self.viz_layout.addWidget(widget)


class BacktestDetailDialog(QDialog):
    def __init__(self, parent=None, backtest_result=None):
        super().__init__(parent)
        self.setStyleSheet(REPORT_DIALOG_STYLESHEET)
        self.setWindowTitle("Backtest Report")
        self.setFixedSize(900, 850)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(40, 40, 40, 40)
        content_layout.setSpacing(30)

        # 1. Header 部分
        header_layout = QHBoxLayout()
        title_vbox = QVBoxLayout()

        tag = QLabel("VALIDATED RUN")
        tag.setObjectName("ValidatedTag")
        tag.setFixedWidth(100)

        title_lbl = QLabel("Golden Croissant Arbitrage")
        title_lbl.setObjectName("MainTitle")

        start_time = self.display_date(backtest_result["start_date"])
        end_time = self.display_date(backtest_result["end_date"])
        sub_lbl = QLabel(f"Execution Period: {start_time} — {end_time} • Intraday 15m")
        sub_lbl.setObjectName("SubTitle")

        title_vbox.addWidget(tag)
        title_vbox.addWidget(title_lbl)
        title_vbox.addWidget(sub_lbl)

        btn_layout = QHBoxLayout()
        export_btn = QPushButton(" Export PDF")
        export_btn.setProperty("class", "SecondaryBtn")
        deploy_btn = QPushButton(" Deploy Strategy")
        deploy_btn.setProperty("class", "PrimaryBtn")

        btn_layout.addWidget(export_btn)
        btn_layout.addWidget(deploy_btn)

        header_layout.addLayout(title_vbox)
        header_layout.addStretch()
        header_layout.addLayout(btn_layout)
        content_layout.addLayout(header_layout)

        # 2. KPI 列表
        # Total Return
        total_return = backtest_result["total_return"]
        total_return_str = f"{total_return:.2f}%"
        if total_return > 0:
            total_return_str = "+" + total_return_str
        row_return = KPIRow("Total Return", total_return_str, COLORS['primary'])
        chart_mock = QFrame()
        chart_mock.setFixedHeight(40)
        chart_mock.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #130d0b, stop:1 #e9c349);
            border-radius: 4px; opacity: 0.5;
        """)
        row_return.add_viz(chart_mock)
        alpha_lbl = QLabel("+201.7% ALPHA")
        alpha_lbl.setProperty("class", "KPISubtitle")
        row_return.info_box.addWidget(alpha_lbl)
        content_layout.addWidget(row_return)

        # Sharpe Ratio
        sharpe_ratio = backtest_result["sharpe_ratio"]
        row_sharpe = KPIRow("Sharpe Ratio", f"{sharpe_ratio:.2f}")
        bar = QProgressBar()
        bar.setRange(-3, 5)
        bar.setValue(sharpe_ratio)
        bar.setTextVisible(False)
        bar.setFixedHeight(8)
        row_sharpe.add_viz(bar)
        tier_tag = QLabel("TIER 1 RISK-ADJUSTED")
        tier_tag.setProperty("class", "KPISubtitle")
        row_sharpe.info_box.addWidget(tier_tag)
        content_layout.addWidget(row_sharpe)

        # Max Drawdown
        row_dd = KPIRow("Max Drawdown", "-8.12%", COLORS['error'])
        row_dd.info_box.addWidget(QLabel("⚠️ VOLATILITY SPIKE"))
        content_layout.addWidget(row_dd)

        # 动态加载结果
        if backtest_result:
            for key, value in backtest_result.items():
                if key not in ["start_date", "end_date", "total_return", "sharpe_ratio"]:
                    row_t = KPIRow(f"{key}", f"{value}")
                    content_layout.addWidget(row_t)

        # 3. Parameter Optimization
        opt_box = QFrame()
        opt_box.setObjectName("OptBox")
        opt_layout = QVBoxLayout(opt_box)
        opt_layout.setContentsMargins(30, 30, 30, 30)

        opt_title = QLabel("🛠️ Parameter Optimization")
        opt_title.setObjectName("OptTitle")
        opt_layout.addWidget(opt_title)

        grid = QGridLayout()
        inputs = [("Lookback Period", "20"), ("Stop Loss %", "1.5"), ("Profit Target", "4.5")]
        for i, (lab, val) in enumerate(inputs):
            vbox = QVBoxLayout()
            label = QLabel(lab.upper())
            label.setProperty("class", "KPILabel")
            edit = QLineEdit(val)
            edit.setFixedHeight(45)
            vbox.addWidget(label)
            vbox.addWidget(edit)
            grid.addLayout(vbox, 0, i)

        exec_btn = QPushButton("⚡ Execute Optimization")
        exec_btn.setProperty("class", "PrimaryBtn")
        exec_btn.setFixedHeight(56)
        grid.addWidget(exec_btn, 0, 3)

        opt_layout.addLayout(grid)
        content_layout.addWidget(opt_box)

        # Footer
        footer_info = QLabel("The Artisanal Exchange • Quantitative Intelligence Engine v2.4.1")
        footer_info.setObjectName("FooterInfo")
        footer_info.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(footer_info)

        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)

        # 底部操作栏
        close_bar = QHBoxLayout()
        close_bar.setContentsMargins(20, 10, 20, 10)
        close_btn = QPushButton("Dismiss Report")
        close_btn.setObjectName("DismissBtn")
        close_btn.clicked.connect(self.close)
        close_bar.addStretch()
        close_bar.addWidget(close_btn)
        main_layout.addLayout(close_bar)

    def display_date(self, str_date: str):
        """"""
        month_map = {
            "01": "Jan", "02": "Feb", "03": "Mar", "04": "Apr", "05": "May", "06": "Jun",
            "07": "Jul", "08": "Aug", "09": "Sep", "10": "Oct", "11": "Nov", "12": "Dec"
        }

        year, month, day = str_date.split("-")
        return f"{month_map[month]} {day}, {year}"

