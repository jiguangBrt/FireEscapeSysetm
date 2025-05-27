import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from interface_manager import InterfaceManager


def main():
    """主程序入口"""
    app = QApplication(sys.argv)

    # 创建主窗口和界面管理器
    main_window = QMainWindow()
    interface_manager = InterfaceManager(main_window)

    # 显示主菜单
    interface_manager.show_main_menu()
    main_window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()