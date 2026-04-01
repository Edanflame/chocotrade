from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout

# =================================================================
# 颜色与样式定义
# =================================================================
COLORS = {
    "background": "#181210",
    "surface": "#251e1c",
    "surface_low": "#201a18",
    "surface_high": "#2f2826",
    "surface_highest": "#3b3331",
    "surface_lowest": "#130d0b",
    "primary": "#e9c349", # 金色
    "on_primary": "#3c2f00",
    "on_surface": "#ede0dc", # 亮白色
    "on_surface_variant": "#d2c4bc", # 柔和白
    "outline": "#4f453f",
    "error": "#ffb4ab",
    "success": "#4ade80", # 绿色
    "tertiary": "#d5c5a8" # 文艺金色
}

# PortfolioCard 整体样式
PORTFOLIO_CARD_STYLESHEET = f"""
    #PortfolioCard {{
        background-color: qlineargradient(
            x1: 0, y1: 0, x2: 1, y2: 1,
            stop: 0 {COLORS['background']}, /* #181210 */
            stop: 0.5 {COLORS['surface']},    /* #251e1c */
            stop: 1 #3b2d00     /* #3b2d00 (primary 颜色加透明度，模拟右上角微弱金光) */
        );
        border: 1px solid rgba(233, 195, 73, 0.15); /* primary 颜色加透明度 */
        border-radius: 12px;
    }}

    #PortfolioCardTitle {{
        color: {COLORS['primary']}; /* primary 颜色加透明度 */
        font-size: 11px;
        font-weight: bold;
        letter-spacing: 2px;
    }}

    #PortfolioCardMainPrice {{
        color: {COLORS['on_surface']};
        font-size: 44px;
        font-weight: 800; /* extabold 对应 800 */
        letter-spacing: -1px;
    }}

    #PortfolioCardChange {{
        color: {COLORS['success']};
        font-size: 14px;
        font-weight: bold;
        margin-bottom: 8px; /* 模拟 HTML 元素对齐时的微调 */
    }}

    .PortfolioStatLabel {{
        color: {COLORS['on_surface_variant']};
        font-size: 10px;
        font-weight: bold;
        letter-spacing: 1px;
    }}

    .PortfolioStatValue {{
        color: {COLORS['tertiary']}; /* 文艺金色 */
        font-size: 20px;
        font-weight: bold;
    }}

    .VerticalDivider {{
        background-color: {COLORS['outline']}; /* outline 颜色加透明度 */
        margin: 5px 0px;
    }}
"""

# =================================================================
# 组件实现
# =================================================================

class PortfolioCard(QFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName("PortfolioCard")
        self.setStyleSheet(PORTFOLIO_CARD_STYLESHEET)

        # 主布局 (对应 HTML 的 p-8)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(32, 32, 32, 32) # p-8 对应 32px
        main_layout.setSpacing(0)

        # --- 上半部分：总价值展示 ---
        top_container = QVBoxLayout()
        top_container.setSpacing(4) # space-y-1 对应 4px

        title_lbl = QLabel("TOTAL PORTFOLIO VALUE")
        title_lbl.setObjectName("PortfolioCardTitle") # 应用样式表中的对象名选择器

        value_layout = QHBoxLayout()
        value_layout.setSpacing(12) # space-x-3 对应 12px
        value_layout.setAlignment(Qt.AlignBottom | Qt.AlignLeft)

        main_price = QLabel("$1,248,390.15")
        main_price.setObjectName("PortfolioCardMainPrice") # 应用样式表中的对象名选择器

        change_lbl = QLabel("+2.4%")
        change_lbl.setObjectName("PortfolioCardChange") # 应用样式表中的对象名选择器

        value_layout.addWidget(main_price)
        value_layout.addWidget(change_lbl)

        top_container.addWidget(title_lbl)
        top_container.addLayout(value_layout)
        main_layout.addLayout(top_container)

        # 增加间距 (mt-8 对应 32px)
        main_layout.addSpacing(32)

        # --- 下半部分：三个统计指标 (带分隔线) ---
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(0) # space-x-0

        # 指标 1: Max Drawdown
        stats_layout.addLayout(self._create_stat_item("MAX DRAWDOWN", "4.12%"))

        # 分隔线 1
        stats_layout.addWidget(self._create_vline())

        # 指标 2: Sharpe Ratio
        stats_layout.addLayout(self._create_stat_item("SHARPE RATIO", "2.84"))

        # 分隔线 2
        stats_layout.addWidget(self._create_vline())

        # 指标 3: Win Rate
        stats_layout.addLayout(self._create_stat_item("WIN RATE", "68%"))

        main_layout.addLayout(stats_layout)

    def _create_stat_item(self, label, value):
        """创建单个指标垂直布局"""
        layout = QVBoxLayout()
        layout.setSpacing(4) # space-y-1 对应 4px
        # 左右留白模拟比例分布，在 QHBoxLayout 中，通常通过 addStretch() 或 setStretch() 来分配空间
        # 但这里为了保持每个 item 内部的 padding，可以设置 contentsMargins。
        # 如果需要均匀分布，QGridLayout 或 QHBoxLayout 的 addWidget(widget, stretch) 更合适。
        # 这里为了简单起见，暂用 contentsMargins 模拟一些横向间距。
        layout.setContentsMargins(10, 0, 10, 0) # 模拟 p-x

        l_lbl = QLabel(label)
        l_lbl.setProperty("class", "PortfolioStatLabel") # 应用样式表中的类选择器

        v_lbl = QLabel(value)
        v_lbl.setProperty("class", "PortfolioStatValue") # 应用样式表中的类选择器

        layout.addWidget(l_lbl, alignment=Qt.AlignHCenter) # 居中对齐
        layout.addWidget(v_lbl, alignment=Qt.AlignHCenter) # 居中对齐
        return layout

    def _create_vline(self):
        """创建垂直分隔线 (对应 HTML 的 border-l border-outline-variant/30)"""
        line = QFrame()
        line.setFixedWidth(1)
        line.setProperty("class", "VerticalDivider") # 应用样式表中的类选择器
        return line
