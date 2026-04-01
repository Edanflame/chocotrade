""""""
from importlib import resources
from pathlib import Path

import rumps


class MyServiceApp(rumps.App):
    def __init__(self):
        super().__init__("🚀")
        '''
        self.stop_event = threading.Event()

        # 在子线程启动 gRPC
        self.server_thread = threading.Thread(
            target=start_grpc_logic,
            args=(self.stop_event,),
            daemon=True
        )
        self.server_thread.start()
        '''
        self.menu = [
            rumps.MenuItem("服务状态: 正在检测...", callback=None),
            None, # 分隔线
            "启动服务",
            "启动客户端",
            "打开主界面",
            None,
            "退出"
        ]

        icon_resource = resources.files("chocotrade").joinpath("src", "nav_icon.png")
        self.icon = str(icon_resource)

    @rumps.clicked("启动服务")
    def start_server(self, _):
        """"""
        pass

    @rumps.clicked("启动客户端")
    def start_client(self, _):
        """"""
        pass

    @rumps.clicked("打开主界面")
    def open_gui(self, _):
        import subprocess
        import sys
        executable = sys.executable
        args = ["-m", "chocotrade", "gui"]

        log_file = Path.home() / ".myapp_service.log" # 后台日志路径

        log_file = open(log_file, "a")
        # 在 macOS/Unix 上创建守护进程
        subprocess.Popen(
            [executable] + args,
            stdout=log_file,
            stderr=log_file,
            stdin=subprocess.PIPE,
            # preexec_fn=os.setpgrp, # 脱离当前终端会话
            start_new_session=True # 开启新会话，确保终端关闭后服务不挂
        )


    @rumps.clicked("退出")
    def quit_app(self, _):
        # self.stop_event.set() # 通知 gRPC 停止
        rumps.quit_application()

if __name__ == "__main__":
    MyServiceApp().run()
