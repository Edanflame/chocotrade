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
</p>

## ✨ Highlights
- ***Modern & Aesthetic Interface.***
Unlike traditional quantitative tools that often feel cluttered and outdated, ChocoTrade features a "Premium Artisanal" design language. Built with a sophisticated dark-and-gold aesthetic, it provides a high-contrast, intuitive, and visually stunning user experience that aligns with modern high-end application standards.

- ***Decoupled Architecture & Headless Operation.***
The system features a strict separation between frontend and backend. The core engine can operate in "headless mode," allowing you to close the GUI during routine operations to ensure maximum performance and stability for long-running trading tasks.

- ***Terminal User Interface (TUI) for Remote Servers.***
Beyond the Desktop GUI, ChocoTrade provides a sophisticated terminal interface powered by Textual. This is a game-changer for users deploying on headless Linux servers, enabling quick health checks and status monitoring directly via SSH.

- ***Distributed Computing via gRPC.***
By utilizing high-performance gRPC for communication, ChocoTrade supports distributed deployments. You can run heavy computational backtesting or live trading on a powerful dedicated server while monitoring the real-time dashboard on a completely different machine within your local network.

- ***OpenClaw Integration & AI-Ready Skills.***
Designed for the era of AI Agents, we provide comprehensive API interfaces and dedicated "Skills" for OpenClaw. This enables seamless interaction between AI agents and the trading engine for automated analysis and intelligent execution.

## 🏗️ Architecture
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

## 🛠 Installation

### 1. Installation via Homebrew (Recommended)
The easiest way to get ChocoTrade on macOS or Linux is via our official ***Homebrew*** Tap:

```Bash
# Add the official tap repository
brew tap edanflame/tap
# Install chocotrade
brew install chocotrade

# By using brew services, you can run backend as a system daemon. This ensures your trading logic
# executes 24/7 in the background, persistent and unaffected by UI terminal closures.
# Start the backend engine (set to run automatically on system boot)
brew services start chocotrade
# Stop the backend engine
brew services stop chocotrade
```

### 2. Standard Installation (Recommended)
The easiest way to get ChocoTrade is via ***pip***:

```Bash
pip install chocotrade
```

### 3. Local/Development Installation
If you want to install from source (e.g., for local modifications), clone the repository and run:

```Bash
# Navigate to the project root directory
cd chocotrade

# Install in editable mode or standard mode
pip install .
```

### 4. Global Tool for uv
If you want to use chocotrade as a standalone command across your entire system, use uv:

```Bash
# Install from local source as a global tool
uv tool install .
```

***Important Notes***

Path Conflict Warning

Python's module resolution may prioritize the local chocotrade/ folder over the installed package, leading to import conflicts or "Module Not Found" errors.

Best Practices:

Use pip for global or virtual environment installations.

Avoid running chocotrade commands while your current working directory is the root of the source code, unless you are using an editable install (pip install -e .).

## 🚀 Getting Started

Chocotrade offers three ways to interact with the trading engine. You can run it as a unified app or in a distributed client-server architecture.

### 1. Distributed Mode (Recommended for Servers)
Use this mode if you want to run the heavy calculation engine on one machine and monitor it from another.

***Step 1: Start the Core Engine (Backend)***

```Bash
chocotrade server
```

***Step 2: Choose your Interface***

Desktop GUI (PySide6):
```Bash
chocotrade gui --connect localhost:50051
```

Terminal UI (Textual):
```Bash
chocotrade tui --connect localhost:50051
```

### 2. Standalone Mode (Local All-in-one)
Start the interface and the engine in a single process for local development or simple backtesting.

Launch Desktop App: 
```
chocotrade gui
```

Launch Terminal App:
```
chocotrade tui
```

### 3. macOS Menu Bar Mode (Monitoring)
A lightweight background application that lives in your macOS tray, powered by rumps. Perfect for quick status checks without opening a full window.

```Bash
chocotrade tray
```

## 🛠 Development Workflow
We recommend using uv for lightning-fast dependency management and project isolation.

### 📦 Dependency Management
ChocoTrade uses pyproject.toml to manage dependencies. Please avoid using standard pip directly to keep the environment consistent.

#### 1. Environment Setup
Before running any development tools (like Ruff or Pytest), you need to synchronize your environment with the development dependency group:

```Bash
# Install all production and development dependencies
uv sync --group dev
```

#### 2. Managing Packages
To add or remove dependencies, use the following commands:

```Bash
uv add <package_name>     # Add a production dependency
uv remove <package_name>  # Remove a dependency
```

#### 3. Synchronizing Requirements Files

If you make changes to dependencies, please update the static requirements.txt files for backward compatibility:

```Bash
# Generate production requirements
uv pip compile pyproject.toml -o requirements.txt

# Generate development requirements (including linters and testers)
uv pip compile pyproject.toml --group dev -o requirements-dev.txt
```

### 🧹 Code Quality (Linting & Formatting)
We use Ruff to maintain a clean and consistent codebase. Please run these checks before submitting any pull requests.

#### 1. Code Linting
Check for logical errors and style violations:

```Bash
uv run ruff check .
```

#### 2. Auto-Fixing Issues
Automatically fix most linting errors:

```Bash
uv run ruff check . --fix
```

#### 3. Code Formatting
Automatically reformat the code to match the project style:

```Bash
uv run ruff format .
```

## 🤝 Acknowledgments

ChocoTrade is built upon or inspired by the excellent open-source project [vn.py](https://github.com/vnpy/vnpy). 

We would like to express our sincere gratitude to **Mr. Chen Xiaoyou**, the creator of vn.py, for his outstanding contribution to the quantitative trading community in China. This project incorporates certain architectural concepts or components from vn.py under the terms of the MIT License.