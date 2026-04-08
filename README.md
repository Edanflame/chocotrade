# ChocoTrader

<p align="center">
  <img src="assets/logo.png" width="200" alt="Chocotrade Logo">
</p>

<p align="center">
  <!-- 1. Build 状态  -->
  <a href="https://github.com/Edanflame/chocotrade/actions">
    <img src="https://github.com/Edanflame/chocotrade/workflows/build/badge.svg" alt="build">
  </a>

  <!-- 静态 License -->
  <a href="https://www.python.org/">
    <img src="https://img.shields.io/badge/python-3.13+-blue?logo=python&style=flat-square" alt="Python Version">
  </a>

  <!-- 静态 Python 版本 -->
  <a href="https://github.com/Edanflame/chocotrade/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/License-Apache%202.0-blue.svg?style=flat-square" alt="License">
  </a>

  <img src ="https://img.shields.io/badge/platform-macos-green.svg"/>
</p>

💬 Want to read this in **English** ? Go [**here**](README_ENG.md)

## ✨ 项目亮点
- **现代感审美设计。**
区别于传统量化工具杂乱、陈旧的界面，ChocoTrade 采用了“精品手工（Premium Artisanal）”设计语言。基于高级的黑金配色方案，提供高对比度、直观且极具视觉冲击力的用户体验，符合现代高端应用的设计标准。

- **前后端分离与无界面运行。**
系统采用严格的前后端分离架构。核心引擎支持“无界面（Headless）模式”，在常态化运行时可以关闭 GUI 界面，以确保长期交易任务的最佳性能与稳定性。

- **专为服务器设计的终端界面 (TUI)。**
除了桌面 GUI，ChocoTrade 还提供由 Textual 驱动的高级终端界面。这对于部署在 Linux 服务器上的用户来说是革命性的，支持直接通过 SSH 进行快速健康检查和状态监控。

- **基于 gRPC 的分布式计算。**
利用高性能 gRPC 进行通讯，ChocoTrade 支持分布式部署。您可以将高负载的计算任务（如回测或实盘）运行在强大的专用服务器上，而在本地局域网内的另一台机器上通过实时仪表盘进行监控。

- **OpenClaw 集成与 AI 技能库。**
专为 AI Agent 时代设计。我们为 OpenClaw 提供了完整的 API 接口和专属“技能（Skills）”，实现 AI 智能体与交易引擎的无缝交互，支持自动化分析与智能执行。

<p align="center">
  <img src="assets/show.gif" width="800" alt="Chocotrade Show">
</p>

## 🏗️ 架构
```text
      ┌───────────────────────────────────────────────────────────────────────────────┐
      │                            PROJECT ARCHITECTURE                               │
      └───────────────────────────────────────────────────────────────────────────────┘

        [ FRONTEND / UI ]              [ BRIDGE ]                 [ BACKEND ]
      ┌────────────────────┐        ┌──────────────┐      ┌───────────────────────────┐
      │                    │        │              │      │       Main Engine         │
      │  - PySide6 GUI     │ <────> │     gRPC     │ <──> │  ┌─────────────────────┐  │
      │                    │        │              │      │  │    Event Engine     │  │
      │  - Textual TUI     │        └──────────────┘      │  └──────────┬──────────┘  │
      │                    │                              │  ┌──────────┴──────────┐  │
      │  - CLI Tool        │                              │  │ BT  │  LIVE  │ DB   │  │
      │                    │                              │  └─────────────────────┘  │
      └────────────────────┘                              └───────────────────────────┘
```

## 🛠 安装指南

### 1. 使用 Homebrew 进行安装（推荐）
获取 ChocoTrade 最简单的方式是通过 **brew**:

```Bash
# 添加仓库 tap
brew tap edanflame/tap
# 安装 chocotrade
brew install chocotrade

# 通过 brew services，您可以将后端作为系统守护进程运行，
# 确保交易逻辑在后台 24/7 稳定执行，不受 UI 界面关闭的影响。
# 启动后台交易引擎 (自动随系统启动)
brew services start chocotrade
# 停止后台引擎
brew services stop chocotrade
```

### 2. 标准安装（推荐）
如果您本地有安装有python，获取 ChocoTrade 可以通过 **pip**:

```Bash
pip install chocotrade
```

### 3. 本地/开发安装
如果您希望从源码安装（例如为了进行本地修改），请克隆仓库并运行：

```Bash
# 进入项目根目录
cd chocotrade

# 以标准模式或可编辑模式安装
pip install .
```

### 4. 使用 uv 安装全局工具
如果您希望在整个系统中将 chocotrade 作为一个独立的命令使用，请使用 uv:

```Bash
# 从本地源码安装为全局工具
uv tool install .
```

⚠️ 重要提示：路径冲突风险

Python 的模块解析机制可能会优先识别本地的 chocotrade/ 文件夹，而非已安装的包。这可能导致导入冲突或 "Module Not Found" 错误。

最佳实践：

建议使用 pip 进行全局安装或在虚拟环境中安装。

除非您使用的是可编辑安装（pip install -e .），否则请勿在源码根目录下直接运行 chocotrade 相关命令。

## 🚀 快速上手
Chocotrade 提供三种交互方式。您可以将其作为单体应用运行，也可以采用分布式的客户端-服务器架构。

### 1. 分布式模式（推荐服务器用户使用）
如果您希望在一台机器上运行重型计算引擎，而在另一台机器上进行监控，请使用此模式。

**第一步：启动核心引擎（后端）**

```Bash
chocotrade server
```

**第二步：选择您的交互界面**

桌面 GUI (PySide6):

```Bash
chocotrade gui
```

终端 UI (Textual):

```Bash
chocotrade tui
```

### 2. 单机模式（本地一体化）
在单个进程中同时启动界面和引擎，适合本地开发或简单的策略回测。

启动桌面应用:

```Bash
chocotrade gui
```

启动终端应用:

```Bash
chocotrade tui
```

### 3. macOS 菜单栏模式（状态监控）
这是一个常驻于 macOS 系统托盘（菜单栏）的轻量化后台应用，由 rumps 驱动。非常适合在不打开主窗口的情况下快速查看运行状态。

```Bash
chocotrade tray
```

## 🛠 开发工作流
我们建议使用 uv 进行极速的依赖管理和项目隔离。

### 📦 依赖管理
ChocoTrade 使用 pyproject.toml 管理依赖。请避免直接使用标准的 pip，以保持环境的一致性。

#### 1. 环境初始化
在运行任何开发工具（如 Ruff 或 Pytest）之前，您需要同步开发依赖组：

```
Bash
# 安装所有生产和开发依赖
uv sync --group dev
```

#### 2. 管理依赖包
使用以下命令添加或删除依赖：

```Bash
uv add <package_name>     # 添加生产环境依赖
uv remove <package_name>  # 删除依赖
```

#### 3. 同步 Requirements 文件
如果您更改了依赖项，请更新静态的 requirements.txt 文件以确保向后兼容性：

```Bash
# 生成生产环境 requirements
uv pip compile pyproject.toml -o requirements.txt

# 生成开发环境 requirements（包含 linter 和测试工具）
uv pip compile pyproject.toml --group dev -o requirements-dev.txt
```

### 🧹 代码质量（检查与格式化）
我们使用 Ruff 来保持代码库的整洁与一致。请在提交任何 Pull Request 之前运行以下检查。

#### 1. 代码检查 (Linting)
检查逻辑错误和代码风格问题：

```Bash
uv run ruff check .
```

#### 2. 自动修复
自动修复大部分可识别的 Lint 错误：

```Bash
uv run ruff check . --fix
```

#### 3. 代码格式化 (Formatting)
自动按照项目标准重排代码格式：

```Bash
uv run ruff format .
```

## 🤝 鸣谢
本项目的开发受到了优秀开源项目 [vn.py](https://github.com/vnpy/vnpy) 的启发或使用了其相关组件。

在此特别感谢 **陈晓优** 先生及其团队。vn.py 为国内量化交易社区做出了卓越贡献，其开放的精神和优秀的架构为本项目提供了宝贵的参考。