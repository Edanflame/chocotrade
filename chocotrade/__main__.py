"""
程序主入口
"""

# Licensed under the Apache License: http://www.apache.org/licenses/LICENSE-2.0

import logging
import signal
import socket
import subprocess
import sys
import threading
import time

import typer

from chocotrade.config import settings

PORT = "50051"
LOG_FILE = settings.base_dir / ".myapp_service.log" # 后台日志路径


logger = logging.getLogger(__name__)


app = typer.Typer(help="My gRPC Service with Auto-Wake")

# --- 服务端 ---
def run_server(stop_event: threading.Event):
    """"""
    from chocotrade.server import get_server, stop_engine
    server = get_server(PORT)
    server.start()

    try:
        while not stop_event.is_set():
            # wait(timeout) 让出控制权，确保 Python 解释器能处理信号
            if stop_event.wait(timeout=1.0):
                break
    except (KeyboardInterrupt, SystemExit):
        typer.echo("Interrupted by user/system.")
    finally:
        typer.echo("Shutting down server...")
        stop_engine() # 引擎清理逻辑
        server.stop(grace=2).wait()
        typer.echo("Server stopped.")


# --- 自动启动 ---
def is_service_running():
    """检查 gRPC 服务是否存活"""
    try:
        # 探测 ::1 (IPv6 localhost)
        with socket.create_connection(("::1", PORT), timeout=0.5):
            return True
    except (OSError, ConnectionRefusedError):
        try:
            # 备选：探测 127.0.0.1 (IPv4 localhost)
            with socket.create_connection(("127.0.0.1", PORT), timeout=0.5):
                return True
        except (OSError, ConnectionRefusedError):
            return False

def start_service_background():
    """以后台进程形式启动服务端"""
    logger.info("未发现后台服务，正在尝试自动启动...")
    typer.echo("未发现后台服务，正在尝试自动启动...")

    # 获取当前执行文件的路径 (myapp)
    # 我们调用自身的 'serve' 子命令
    executable = sys.executable
    args = [sys.argv[0], "server", "--slave"]

    # 在 macOS/Unix 上创建守护进程
    with open(LOG_FILE, "a") as log:
        subprocess.Popen(
            [executable] + args,
            stdout=log,
            stderr=log,
            stdin=subprocess.PIPE,
            # preexec_fn=os.setpgrp, # 脱离当前终端会话
            # start_new_session=True # 开启新会话，确保终端关闭后服务不挂
        )

    # 等待服务就绪
    for _ in range(5):
        time.sleep(1)
        if is_service_running():
            logger.info("服务启动成功！")
            typer.echo("服务启动成功！")
            return

    logger.info("服务启动超时，请检查日志。")
    typer.echo("服务启动超时，请检查日志。")
    sys.exit(1)


# --- CLI ---
@app.command()
def server(
    slave: bool = typer.Option(False, "--slave", help="随父进程关闭而关闭 (内部调用)")
):
    """启动 gRPC 后端服务"""
    stop_event = threading.Event()

    def signal_handler(sig, frame):
        stop_event.set()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # 2. 如果是 Slave 模式，增加 Stdin 监听
    if slave:
        def watch_stdin():
            try:
                # 当父进程关闭时，stdin.read() 会返回 EOF (空字符串)
                sys.stdin.read()
            except Exception:
                pass
            finally:
                typer.echo("Parent process connection lost. Stopping...")
                stop_event.set()

        # 必须设为 daemon，确保它不会阻止进程退出
        threading.Thread(target=watch_stdin, daemon=True).start()

    typer.echo(f"Server starting (Slave Mode: {slave})...")
    run_server(stop_event)


@app.command(name="tray", help="Start macOS Menu Bar app (rumps)")
def menu_bar():
    """"""
    from chocotrade.server import MyServiceApp

    MyServiceApp().run()


@app.command(name="tui", help="Start Textual Terminal Interface")
def terminal_client():
    """"""
    from chocotrade.client.textual_client import TextualClient

    if not is_service_running():
        start_service_background()

    app = TextualClient()
    app.run()


@app.command(name="gui", help="Start PySide6 Desktop Interface")
def qt_client():
    """"""
    from chocotrade.client.qt_client import create_qt_client

    if not is_service_running():
        start_service_background()

    create_qt_client()


def main():
    app()


if __name__ == "__main__":
    main()
