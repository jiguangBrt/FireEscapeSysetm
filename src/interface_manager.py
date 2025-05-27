from PyQt5.QtWidgets import QWidget, QStackedWidget
from main_menu import MainMenuUI
from floor_plan_editor import FloorPlanEditorUI

class InterfaceManager:
    """界面管理器 - 控制不同界面之间的切换"""

    def __init__(self, main_window):
        self.main_window = main_window
        self.main_window.resize(1000, 750)
        self.main_window.setWindowTitle("Fire Escape System")

        # 使用QStackedWidget管理界面切换
        self.stacked_widget = QStackedWidget()
        self.main_window.setCentralWidget(self.stacked_widget)

        # 存储不同界面的实例
        self.interfaces = {}
        self.current_interface = None

        # 初始化界面
        self._setup_interfaces()

    def _setup_interfaces(self):
        """初始化所有界面"""
        # 主菜单界面
        self.interfaces['main_menu'] = MainMenuUI(self)
        self.stacked_widget.addWidget(self.interfaces['main_menu'])

        # 地图编辑界面
        self.interfaces['floor_plan_editor'] = FloorPlanEditorUI(self)
        self.stacked_widget.addWidget(self.interfaces['floor_plan_editor'])

        # 默认显示主菜单
        self.show_main_menu()

    def show_main_menu(self):
        """显示主菜单"""
        self._switch_interface('main_menu')

    def show_floor_plan_editor(self):
        """显示地图编辑界面"""
        self._switch_interface('floor_plan_editor')

    def _switch_interface(self, interface_name):
        """切换界面"""
        if interface_name in self.interfaces:
            interface_widget = self.interfaces[interface_name]
            self.stacked_widget.setCurrentWidget(interface_widget)
            self.current_interface = interface_widget