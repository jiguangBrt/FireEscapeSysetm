from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QBrush, QColor
from chessboard import InteractiveChessboard

class MainMenuUI(QtWidgets.QWidget):
    """主菜单界面"""

    def __init__(self, interface_manager):
        super().__init__()
        self.interface_manager = interface_manager
        self.setup_ui()

    def setup_ui(self):
        """设置UI界面"""
        # 背景标签
        self.lb_background = QtWidgets.QLabel(self)
        self.lb_background.setGeometry(QtCore.QRect(0, 0, 1000, 750))
        self.lb_background.setText("")
        self.lb_background.setPixmap(QtGui.QPixmap("../resources/背景图.png"))
        self.lb_background.setScaledContents(True)

        # 标题
        self.lb_title = QtWidgets.QLabel(self)
        self.lb_title.setGeometry(QtCore.QRect(280, 50, 431, 71))
        self.lb_title.setStyleSheet("""
            QLabel {
                background-color: #8B4513;
                color: white;
                font-size: 20px;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 10px;
            }
        """)
        self.lb_title.setText("Fire escape route prediction system")

        # 网格视图（仅显示，不可交互）
        self.graphics_view = QtWidgets.QGraphicsView(self)
        self.graphics_view.setGeometry(QtCore.QRect(40, 140, 500, 500))

        # 创建静态网格显示
        self.chessboard = InteractiveChessboard(self.graphics_view, size=32)
        # 禁用交互
        self.chessboard.set_interactive(False)

        # 绘制地图按钮
        self.btn_draw_floor_plan = QtWidgets.QPushButton(self)
        self.btn_draw_floor_plan.setGeometry(QtCore.QRect(610, 240, 291, 91))
        self.btn_draw_floor_plan.setStyleSheet("""
            QPushButton {
                font: 75 25pt "Arial";
                background-color: rgba(0, 255, 255, 64);
                border: 1px solid rgba(0, 255, 255, 64);
                border-radius: 12px;
                color: white;
                padding: 8px 20px;
                font-weight: bold;
                font-size: 30px;
                backdrop-filter: blur(4px);
            }
            QPushButton:hover {
                background-color:rgba(0, 255, 255, 64);
            }
            QPushButton:pressed {
                background-color: rgba(0, 238, 255, 64);
            }
        """)
        self.btn_draw_floor_plan.setText("Draw a floor plan")

        # 开始仿真按钮
        self.btn_start_sim = QtWidgets.QPushButton(self)
        self.btn_start_sim.setGeometry(QtCore.QRect(610, 380, 281, 81))
        self.btn_start_sim.setStyleSheet("""
            QPushButton {
                font: 75 25pt "Arial";
                background-color: rgba(0, 255, 42, 64);
                border: 1px solid rgba(0, 255, 42, 64);
                border-radius: 12px;
                color: white;
                padding: 8px 20px;
                font-weight: bold;
                font-size: 30px;
                backdrop-filter: blur(4px);
            }
            QPushButton:hover {
                background-color:rgba(0, 255, 127, 64);
            }
            QPushButton:pressed {
                background-color: rgba(0, 255, 42, 64);
            }
        """)
        self.btn_start_sim.setText("Start simulation")

        # 设置层级
        self.lb_background.raise_()
        self.graphics_view.raise_()
        self.lb_title.raise_()
        self.btn_draw_floor_plan.raise_()
        self.btn_start_sim.raise_()

        # 连接信号
        self.btn_draw_floor_plan.clicked.connect(self.on_draw_floor_plan_clicked)
        self.btn_start_sim.clicked.connect(self.on_start_simulation_clicked)

    def on_draw_floor_plan_clicked(self):
        """点击绘制地图按钮"""
        self.interface_manager.show_floor_plan_editor_ui()

    def on_start_simulation_clicked(self):
        """点击开始仿真按钮"""
        self.interface_manager.show_fire_simulation_ui()

    def update_board_display(self, matrix):
        """更新棋盘显示"""
        if matrix and self.chessboard:
            self.chessboard.set_board_from_matrix(matrix)
            print("主菜单棋盘显示已更新")
