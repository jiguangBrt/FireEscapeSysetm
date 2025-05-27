from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox
from chessboard import InteractiveChessboard
import numpy as np
from scipy import ndimage
import copy


class FloorPlanEditorUI(QtWidgets.QWidget):
    """地图编辑界面"""

    def __init__(self, interface_manager):
        super().__init__()
        self.interface_manager = interface_manager
        self.current_mode = "none"  # "wall", "output", "none"
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

        # 网格视图
        self.graphics_view = QtWidgets.QGraphicsView(self)
        self.graphics_view.setGeometry(QtCore.QRect(40, 140, 500, 500))

        # 创建交互式棋盘
        self.chessboard = InteractiveChessboard(self.graphics_view, size=32)
        # 初始状态下禁用交互，等待用户选择模式
        self.chessboard.set_interactive(False)

        # 按钮样式
        button_style_base = """
            QPushButton {{
                font: 75 18pt "Arial";
                border-radius: 12px;
                color: white;
                padding: 8px 20px;
                font-weight: bold;
            }}
            QPushButton:pressed {{
                background-color: {pressed_color};
            }}
        """

        # Edit Wall 按钮
        self.btn_edit_wall = QtWidgets.QPushButton(self)
        self.btn_edit_wall.setGeometry(QtCore.QRect(610, 180, 280, 60))
        self.btn_edit_wall.setText("Edit Wall")
        self.btn_edit_wall.setCheckable(True)

        # Edit Output 按钮
        self.btn_edit_output = QtWidgets.QPushButton(self)
        self.btn_edit_output.setGeometry(QtCore.QRect(610, 260, 280, 60))
        self.btn_edit_output.setText("Edit Output")
        self.btn_edit_output.setCheckable(True)

        # Check and Store 按钮
        self.btn_check_store = QtWidgets.QPushButton(self)
        self.btn_check_store.setGeometry(QtCore.QRect(610, 340, 280, 60))
        self.btn_check_store.setText("Check and Store")

        # Back 按钮
        self.btn_back = QtWidgets.QPushButton(self)
        self.btn_back.setGeometry(QtCore.QRect(610, 420, 280, 60))
        self.btn_back.setText("Back")

        # 设置按钮样式
        self._setup_button_styles()

        # 设置层级
        self.lb_background.raise_()
        self.graphics_view.raise_()
        self.lb_title.raise_()
        self.btn_edit_wall.raise_()
        self.btn_edit_output.raise_()
        self.btn_check_store.raise_()
        self.btn_back.raise_()

        # 连接信号
        self.btn_edit_wall.clicked.connect(self.on_edit_wall_clicked)
        self.btn_edit_output.clicked.connect(self.on_edit_output_clicked)
        self.btn_check_store.clicked.connect(self.on_check_store_clicked)
        self.btn_back.clicked.connect(self.on_back_clicked)

    def _setup_button_styles(self):
        """设置按钮样式"""
        # Edit Wall - 蓝色
        self.btn_edit_wall.setStyleSheet("""
            QPushButton {
                font: 75 18pt "Arial";
                background-color: rgba(0, 123, 255, 180);
                border: 1px solid rgba(0, 123, 255, 180);
                border-radius: 12px;
                color: white;
                padding: 8px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(0, 123, 255, 220);
            }
            QPushButton:checked {
                background-color: rgba(0, 86, 179, 255);
                border: 2px solid white;
            }
        """)

        # Edit Output - 绿色
        self.btn_edit_output.setStyleSheet("""
            QPushButton {
                font: 75 18pt "Arial";
                background-color: rgba(40, 167, 69, 180);
                border: 1px solid rgba(40, 167, 69, 180);
                border-radius: 12px;
                color: white;
                padding: 8px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(40, 167, 69, 220);
            }
            QPushButton:checked {
                background-color: rgba(28, 117, 48, 255);
                border: 2px solid white;
            }
        """)

        # Check and Store - 橙色
        self.btn_check_store.setStyleSheet("""
            QPushButton {
                font: 75 18pt "Arial";
                background-color: rgba(255, 149, 0, 180);
                border: 1px solid rgba(255, 149, 0, 180);
                border-radius: 12px;
                color: white;
                padding: 8px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255, 149, 0, 220);
            }
            QPushButton:pressed {
                background-color: rgba(204, 119, 0, 255);
            }
        """)

        # Back - 红色
        self.btn_back.setStyleSheet("""
            QPushButton {
                font: 75 18pt "Arial";
                background-color: rgba(220, 53, 69, 180);
                border: 1px solid rgba(220, 53, 69, 180);
                border-radius: 12px;
                color: white;
                padding: 8px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(220, 53, 69, 220);
            }
            QPushButton:pressed {
                background-color: rgba(176, 42, 55, 255);
            }
        """)

    def on_edit_wall_clicked(self):
        """编辑墙体模式"""
        if self.btn_edit_wall.isChecked():
            self.current_mode = "wall"
            self.btn_edit_output.setChecked(False)
            self.chessboard.set_interactive(True)
            self.chessboard.set_edit_mode("wall")  # 黑白切换
            print("进入墙体编辑模式")
        else:
            self.current_mode = "none"
            self.chessboard.set_interactive(False)
            print("退出墙体编辑模式")

    def on_edit_output_clicked(self):
        """编辑出口模式"""
        if self.btn_edit_output.isChecked():
            self.current_mode = "output"
            self.btn_edit_wall.setChecked(False)
            self.chessboard.set_interactive(True)
            self.chessboard.set_edit_mode("output")  # 绿白切换
            print("进入出口编辑模式")
        else:
            self.current_mode = "none"
            self.chessboard.set_interactive(False)
            print("退出出口编辑模式")

    def on_check_store_clicked(self):
        """检查并存储地图"""
        matrix = self.chessboard.get_state_matrix()

        # 检查封闭区域
        if self._check_enclosed_areas(matrix):
            reply = QMessageBox.question(
                self,
                '检测到封闭区域',
                '地图中存在封闭区域，这可能影响逃生路径。是否继续保存？',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.No:
                return

        # 存储数据到interface_manager
        self.interface_manager.set_board_data(copy.deepcopy(matrix))
        self._save_floor_plan_data(matrix)

        QMessageBox.information(self, '保存成功', '地图数据已成功保存！')
        print("地图检查完成并已保存")

    def on_back_clicked(self):
        """返回主菜单"""
        # 保存当前状态到interface_manager
        current_matrix = self.chessboard.get_state_matrix()
        self.interface_manager.set_board_data(copy.deepcopy(current_matrix))

        self.interface_manager.show_main_menu()

    def load_board_data(self, matrix):
        """加载棋盘数据"""
        if matrix and self.chessboard:
            self.chessboard.set_board_from_matrix(matrix)
            print("棋盘数据已加载")

    def _check_enclosed_areas(self, matrix):
        """检查是否存在封闭区域"""
        try:
            # 将矩阵转换为numpy数组
            arr = np.array(matrix)

            # 创建边界（假设边界都是墙）
            padded = np.pad(arr, 1, constant_values=1)

            # 使用flood fill从边界开始填充
            # 0表示空地，1表示墙
            open_area = np.zeros_like(padded)

            # 从所有边界的空地开始flood fill
            for i in range(padded.shape[0]):
                for j in range(padded.shape[1]):
                    if (i == 0 or i == padded.shape[0] - 1 or
                        j == 0 or j == padded.shape[1] - 1) and padded[i, j] == 0:
                        self._flood_fill(padded, open_area, i, j)

            # 检查原始区域中是否有空地没有被标记为开放区域
            original_open = padded[1:-1, 1:-1]
            marked_open = open_area[1:-1, 1:-1]

            enclosed_exists = np.any((original_open == 0) & (marked_open == 0))
            return enclosed_exists

        except Exception as e:
            print(f"检查封闭区域时出错: {e}")
            return False

    def _flood_fill(self, matrix, visited, x, y):
        """递归flood fill算法"""
        if (x < 0 or x >= matrix.shape[0] or y < 0 or y >= matrix.shape[1] or
                visited[x, y] == 1 or matrix[x, y] == 1):
            return

        visited[x, y] = 1

        # 递归填充四个方向
        self._flood_fill(matrix, visited, x + 1, y)
        self._flood_fill(matrix, visited, x - 1, y)
        self._flood_fill(matrix, visited, x, y + 1)
        self._flood_fill(matrix, visited, x, y - 1)

    def _save_floor_plan_data(self, matrix):
        """保存地图数据"""
        # 这里可以实现具体的保存逻辑
        # 例如保存到文件、数据库等
        print("保存地图数据:")
        print(f"地图大小: {len(matrix)}x{len(matrix[0])}")

        # 统计墙体和出口数量
        wall_count = sum(row.count(1) for row in matrix)
        output_count = sum(row.count(2) for row in matrix)

        print(f"墙体方块数: {wall_count}")
        print(f"出口方块数: {output_count}")
