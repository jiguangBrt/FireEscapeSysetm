from PyQt5.QtWidgets import QWidget, QStackedWidget
from main_menu_ui import MainMenuUI
from floor_plan_editor_ui import FloorPlanEditorUI
from fire_simulation_ui import FireSimulationUI

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

        # 存储棋盘数据
        self.board_data = None
        self.board_size = 32

        # 存储模拟数据
        self.simulation_data = None

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

        # 火灾模拟界面
        self.interfaces['fire_simulation'] = FireSimulationUI(self)
        self.stacked_widget.addWidget(self.interfaces['fire_simulation'])

        # 默认显示主菜单
        # self.show_main_menu()

    def show_main_menu(self):
        """显示主菜单"""
        # 在切换到主菜单前，保存编辑器中的数据
        # if 'floor_plan_editor' in self.interfaces:
        #     self.save_board_data()
        self._switch_interface('main_menu')

        # 更新主菜单中的棋盘显示
        if self.board_data:
            self.interfaces['main_menu'].update_board_display(self.board_data)

        # # 更新主菜单中的模拟显示
        # if self.simulation_data:
        #     self.interfaces['main_menu'].update_simulation_display(self.simulation_data)

    def show_floor_plan_editor_ui(self):
        """显示地图编辑界面"""
        self._switch_interface('floor_plan_editor')

        # 恢复之前保存的数据
        if self.board_data:
            self.interfaces['floor_plan_editor'].load_board_data(self.board_data)

    def show_fire_simulation_ui(self):
        """显示火灾模拟界面"""
        self._switch_interface('fire_simulation')

        # 恢复之前保存的数据
        if self.board_data:
            self.interfaces['fire_simulation'].load_board_data(self.board_data)

        # 恢复之前的模拟数据
        if self.simulation_data:
            self.interfaces['fire_simulation'].load_simulation_data(self.simulation_data)

    def _switch_interface(self, interface_name):
        """切换界面"""
        if interface_name in self.interfaces:
            interface_widget = self.interfaces[interface_name]
            self.stacked_widget.setCurrentWidget(interface_widget)
            self.current_interface = interface_widget

    def save_board_data(self):
        """保存棋盘数据"""
        if 'floor_plan_editor' in self.interfaces:
            editor = self.interfaces['floor_plan_editor']
            if hasattr(editor, 'chessboard'):
                self.board_data = editor.chessboard.get_state_matrix()

    def get_board_data(self):
        """获取棋盘数据"""
        return self.board_data

    def set_board_data(self, data):
        """设置棋盘数据"""
        self.board_data = data

    def set_simulation_data(self, data):
        """设置模拟数据"""
        self.simulation_data = data

    def get_simulation_data(self):
        """获取模拟数据"""
        return self.simulation_data