from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox, QSlider
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QBrush, QColor
from chessboard import InteractiveChessboard
from typing import List, Tuple, Optional
import copy
import numpy as np


class FireSimulationUI(QtWidgets.QWidget):
    """火灾仿真界面"""

    def __init__(self, interface_manager):
        super().__init__()
        self.interface_manager = interface_manager
        self.simulation_data = None # 存储模拟数据
        self.current_mode = "none"  # "start_point", "none"
        self.start_point = None  # 逃生起点 (row, col)
        self.risk_data = None  # 三维风险数据 [time][x][y]
        self.escape_routes = []  # 逃生路线数据 [算法1, 算法2, 算法3]
        self.current_time_step = 0
        self.max_time_steps = 0
        self.auto_play_timer = QTimer()
        self.auto_play_timer.timeout.connect(self.auto_play_step)
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
        # 设置为仿真专用棋盘
        self.chessboard.set_interactive(False)
        self.chessboard.set_drag_enabled(False)

        # 创建提示框
        self.lb_tips = QtWidgets.QLabel(self)
        self.lb_tips.setGeometry(QtCore.QRect(610, 200, 280, 60))
        self.lb_tips.setStyleSheet("""
            QLabel {
                background-color: rgba(0, 255, 255, 64);
                border: 1px solid rgba(0, 255, 255, 64);
                border-radius: 12px;
                color: white;
                padding: 10px;
                font-size: 12px;
                font-weight: bold;
            }
        """)
        self.lb_tips.setText("选择起点后进行风险和路线计算")
        self.lb_tips.setWordWrap(True)
        self.lb_tips.setAlignment(QtCore.Qt.AlignCenter)

        # 时间控制滑块
        self.setup_time_slider()

        # 按钮设置
        self.setup_buttons()

        # 设置层级
        self.lb_background.raise_()
        self.graphics_view.raise_()
        self.lb_title.raise_()
        self.lb_tips.raise_()
        self.time_slider.raise_()
        self.lb_time_display.raise_()
        self.btn_set_start.raise_()
        self.btn_calc_risk.raise_()
        self.btn_calc_route.raise_()
        self.btn_back.raise_()

        # 连接信号
        self.btn_set_start.clicked.connect(self.on_set_start_clicked)
        self.btn_calc_risk.clicked.connect(self.on_calc_risk_clicked)
        self.btn_calc_route.clicked.connect(self.on_calc_route_clicked)
        self.btn_back.clicked.connect(self.on_back_clicked)

    def setup_time_slider(self):
        """设置时间滑块"""
        # 时间滑块
        self.time_slider = QSlider(Qt.Horizontal, self)
        self.time_slider.setGeometry(QtCore.QRect(610, 280, 280, 30))
        self.time_slider.setMinimum(0)
        self.time_slider.setMaximum(0)  # 初始为0，计算后更新
        self.time_slider.setValue(0)
        self.time_slider.setEnabled(False)
        self.time_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #bbb;
                background: white;
                height: 10px;
                border-radius: 4px;
            }
            QSlider::sub-page:horizontal {
                background: qlineargradient(x1: 0, y1: 0,    x2: 0, y2: 1,
                    stop: 0 #66e, stop: 1 #bbf);
                background: qlineargradient(x1: 0, y1: 0.2, x2: 1, y2: 1,
                    stop: 0 #bbf, stop: 1 #55f);
                border: 1px solid #777;
                height: 10px;
                border-radius: 4px;
            }
            QSlider::add-page:horizontal {
                background: #fff;
                border: 1px solid #777;
                height: 10px;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #eee, stop:1 #ccc);
                border: 1px solid #777;
                width: 18px;
                margin-top: -2px;
                margin-bottom: -2px;
                border-radius: 3px;
            }
            QSlider::handle:horizontal:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #fff, stop:1 #ddd);
                border: 1px solid #444;
                border-radius: 3px;
            }
        """)

        # 时间显示标签
        self.lb_time_display = QtWidgets.QLabel(self)
        self.lb_time_display.setGeometry(QtCore.QRect(610, 320, 280, 30))
        self.lb_time_display.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 14px;
                font-weight: bold;
                text-align: center;
            }
        """)
        self.lb_time_display.setText("时间: 0 / 0")
        self.lb_time_display.setAlignment(QtCore.Qt.AlignCenter)

        # 连接滑块信号
        self.time_slider.valueChanged.connect(self.on_time_changed)

    def setup_buttons(self):
        """设置按钮"""
        # 修改起点按钮 - 粉色
        self.btn_set_start = QtWidgets.QPushButton(self)
        self.btn_set_start.setGeometry(QtCore.QRect(610, 380, 280, 60))
        self.btn_set_start.setText("修改起点")
        self.btn_set_start.setCheckable(True)
        self.btn_set_start.setStyleSheet("""
            QPushButton {
                font: 75 18pt "Arial";
                background-color: rgba(255, 20, 147, 180);
                border: 1px solid rgba(255, 20, 147, 180);
                border-radius: 12px;
                color: white;
                padding: 8px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255, 20, 147, 220);
            }
            QPushButton:checked {
                background-color: rgba(199, 21, 133, 255);
                border: 2px solid white;
            }
        """)

        # 风险计算按钮 - 橙色
        self.btn_calc_risk = QtWidgets.QPushButton(self)
        self.btn_calc_risk.setGeometry(QtCore.QRect(610, 460, 280, 60))
        self.btn_calc_risk.setText("风险计算")
        self.btn_calc_risk.setStyleSheet("""
            QPushButton {
                font: 75 18pt "Arial";
                background-color: rgba(255, 140, 0, 180);
                border: 1px solid rgba(255, 140, 0, 180);
                border-radius: 12px;
                color: white;
                padding: 8px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255, 140, 0, 220);
            }
            QPushButton:pressed {
                background-color: rgba(204, 112, 0, 255);
            }
        """)

        # 路线计算按钮 - 蓝色
        self.btn_calc_route = QtWidgets.QPushButton(self)
        self.btn_calc_route.setGeometry(QtCore.QRect(610, 540, 280, 60))
        self.btn_calc_route.setText("路线计算")
        self.btn_calc_route.setStyleSheet("""
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
            QPushButton:pressed {
                background-color: rgba(0, 86, 179, 255);
            }
        """)

        # 返回按钮 - 红色
        self.btn_back = QtWidgets.QPushButton(self)
        self.btn_back.setGeometry(QtCore.QRect(610, 620, 280, 60))
        self.btn_back.setText("返回")
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

    def on_set_start_clicked(self):
        """修改起点模式"""
        if self.btn_set_start.isChecked():
            self.current_mode = "start_point"
            self.chessboard.set_interactive(True)
            self.chessboard.set_edit_mode("start")
            # 重写鼠标事件处理
            self._setup_start_point_mode()
            print("进入起点设置模式")
        else:
            self.current_mode = "none"
            self.chessboard.set_interactive(False)
            print("退出起点设置模式")

    def _setup_start_point_mode(self):
        """设置起点选择模式"""
        # 为棋盘的每个方块添加起点设置的鼠标事件
        for row in range(self.chessboard.size):
            for col in range(self.chessboard.size):
                square = self.chessboard.squares[row][col]
                # 重写鼠标点击事件
                original_mouse_press = square.mousePressEvent

                def make_start_point_handler(r, c, original_handler):
                    def start_point_handler(event):
                        if self.current_mode == "start_point" and event.button() == Qt.LeftButton:
                            self._set_start_point(r, c)
                        else:
                            original_handler(event)

                    return start_point_handler

                square.mousePressEvent = make_start_point_handler(row, col, original_mouse_press)

    def _set_start_point(self, row, col):
        """设置起点"""
        # 检查是否点击在墙体上
        if self.chessboard.state_matrix[row][col] == 1:
            QMessageBox.warning(self, '无效位置', '不能在墙体上设置起点！')
            return

        # 清除之前的起点
        if self.start_point:
            old_row, old_col = self.start_point
            if (0 <= old_row < self.chessboard.size and
                    0 <= old_col < self.chessboard.size and
                    self.chessboard.state_matrix[old_row][old_col] == 3):
                self.chessboard.squares[old_row][old_col].set_state(0)

        # 设置新起点
        self.start_point = (row, col)
        self.chessboard.squares[row][col].set_state(3)  # 3代表起点

        # 检查是否有逃生路线
        if self._check_escape_route_exists(row, col):
            print(f"起点设置成功: ({row}, {col})")
            QMessageBox.information(self, '起点设置', f'起点已设置在位置 ({row}, {col})')
        else:
            # 没有逃生路线，取消起点设置
            self.chessboard.squares[row][col].set_state(0)
            self.start_point = None
            QMessageBox.warning(self, '无逃生路线', '该位置没有可用的逃生路线，请选择其他位置！')

        # 退出起点设置模式
        self.btn_set_start.setChecked(False)
        self.current_mode = "none"
        self.chessboard.set_interactive(False)

    def _check_escape_route_exists(self, start_row, start_col):
        """检查是否存在逃生路线（简单的BFS检查）"""
        from collections import deque

        matrix = self.chessboard.get_state_matrix()
        rows, cols = len(matrix), len(matrix[0])

        # BFS寻找到出口的路径
        queue = deque([(start_row, start_col)])
        visited = set()
        visited.add((start_row, start_col))

        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]

        while queue:
            row, col = queue.popleft()

            # 检查是否到达出口
            if matrix[row][col] == 2:
                return True

            # 探索四个方向
            for dr, dc in directions:
                new_row, new_col = row + dr, col + dc

                if (0 <= new_row < rows and 0 <= new_col < cols and
                        (new_row, new_col) not in visited and
                        matrix[new_row][new_col] != 1):  # 不是墙体

                    visited.add((new_row, new_col))
                    queue.append((new_row, new_col))

        return False

    def on_calc_risk_clicked(self):
        """风险计算"""
        if not self.start_point:
            QMessageBox.warning(self, '未设置起点', '请先设置逃生起点！')
            return

        try:
            # 这里调用外部py文件的风险计算函数
            # 假设函数名为 calculate_fire_risk(matrix, start_point)
            # 返回三维数组 [time_steps][x][y] 表示每个时间步的风险值

            # 示例实现（实际使用时替换为真实的函数调用）
            matrix = self.chessboard.get_state_matrix()
            self.risk_data = self._mock_calculate_fire_risk(matrix, self.start_point)

            if self.risk_data is not None:
                self.max_time_steps = len(self.risk_data)
                self.time_slider.setMaximum(self.max_time_steps - 1)
                self.time_slider.setEnabled(True)
                self.time_slider.setValue(0)
                self.current_time_step = 0

                # 更新显示
                self._update_risk_display(0)
                self._update_time_display()

                QMessageBox.information(self, '计算完成', f'风险计算完成！共 {self.max_time_steps} 个时间步。')
                print(f"风险计算完成，时间步数: {self.max_time_steps}")
            else:
                QMessageBox.warning(self, '计算失败', '风险计算失败，请检查地图设置！')

        except Exception as e:
            QMessageBox.critical(self, '错误', f'风险计算时发生错误: {str(e)}')
            print(f"风险计算错误: {e}")

    def _mock_calculate_fire_risk(self, matrix: List[List[int]], start_point: Tuple[int, int]) -> List[List[List[float]]]:
        """模拟风险计算函数（实际使用时替换为真实函数）"""
        rows, cols = len(matrix), len(matrix[0])
        time_steps = 50  # 假设20个时间步

        risk_data = []
        start_row, start_col = start_point

        for t in range(time_steps):
            time_risk = np.zeros((rows, cols))

            # 模拟火灾从起点扩散
            for i in range(rows):
                for j in range(cols):
                    if matrix[i][j] == 1:  # 墙体
                        continue

                    # 计算距离起点的距离
                    distance = abs(i - start_row) + abs(j - start_col)

                    # 随时间扩散的风险值
                    if distance <= t * 0.5:
                        time_risk[i][j] = max(0, min(0.9, (t * 0.1 - distance * 0.05)))

            risk_data.append(time_risk.tolist())

        return risk_data

    def on_calc_route_clicked(self):
        """路线计算"""
        if not self.start_point:
            QMessageBox.warning(self, '未设置起点', '请先设置逃生起点！')
            return

        try:
            # 调用三个不同的搜索算法
            matrix = self.chessboard.get_state_matrix()

            # 这里应该调用外部py文件的三个函数
            # 假设函数名为：
            # - algorithm1_pathfinding(matrix, start_point)
            # - algorithm2_pathfinding(matrix, start_point)
            # - algorithm3_pathfinding(matrix, start_point)
            # 每个都返回 [(x1,y1), (x2,y2), ...] 格式的路径

            # 示例实现（实际使用时替换为真实的函数调用）
            route1 = self._mock_algorithm1_pathfinding(matrix, self.start_point)
            route2 = self._mock_algorithm2_pathfinding(matrix, self.start_point)
            route3 = self._mock_algorithm3_pathfinding(matrix, self.start_point)

            self.escape_routes = [route1, route2, route3]

            if any(route for route in self.escape_routes):
                QMessageBox.information(self, '计算完成',
                                        f'路线计算完成！\n'
                                        f'算法1路径长度: {len(route1) if route1 else 0}\n'
                                        f'算法2路径长度: {len(route2) if route2 else 0}\n'
                                        f'算法3路径长度: {len(route3) if route3 else 0}')

                # 自动播放一次时间流逝
                self._start_auto_play()
                print("路线计算完成，开始自动播放")
            else:
                QMessageBox.warning(self, '无路径', '未找到有效的逃生路径！')

        except Exception as e:
            QMessageBox.critical(self, '错误', f'路线计算时发生错误: {str(e)}')
            print(f"路线计算错误: {e}")

    def _mock_algorithm1_pathfinding(self, matrix: List[List[int]], start_point: Tuple[int, int]) -> List[Tuple[int, int]]:
        """模拟算法1（A*搜索）"""
        return self._simple_pathfinding(matrix, start_point)

    def _mock_algorithm2_pathfinding(self, matrix: List[List[int]], start_point: Tuple[int, int]) -> List[Tuple[int, int]]:
        """模拟算法2（Dijkstra）"""
        return self._simple_pathfinding(matrix, start_point)

    def _mock_algorithm3_pathfinding(self, matrix: List[List[int]], start_point: Tuple[int, int]) -> List[Tuple[int, int]]:
        """模拟算法3（BFS）"""
        return self._simple_pathfinding(matrix, start_point)

    def _simple_pathfinding(self, matrix: List[List[int]], start_point: Tuple[int, int]) -> List[Tuple[int, int]]:
        """简单的路径查找算法（用于演示）"""
        from collections import deque

        rows, cols = len(matrix), len(matrix[0])
        start_row, start_col = start_point

        queue = deque([(start_row, start_col, [(start_row, start_col)])])
        visited = set()
        visited.add((start_row, start_col))

        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]

        while queue:
            row, col, path = queue.popleft()

            # 检查是否到达出口
            if matrix[row][col] == 2:
                return path

            # 探索四个方向
            for dr, dc in directions:
                new_row, new_col = row + dr, col + dc

                if (0 <= new_row < rows and 0 <= new_col < cols and
                        (new_row, new_col) not in visited and
                        matrix[new_row][new_col] != 1):  # 不是墙体

                    visited.add((new_row, new_col))
                    new_path = path + [(new_row, new_col)]
                    queue.append((new_row, new_col, new_path))

        return []  # 未找到路径

    def _start_auto_play(self):
        """开始自动播放"""
        if self.max_time_steps > 0:
            self.current_time_step = 0
            self.time_slider.setValue(0)
            self.auto_play_timer.start(100)  # 每200ms更新一次

    def auto_play_step(self):
        """自动播放的每一步"""
        if self.current_time_step < self.max_time_steps - 1:
            self.current_time_step += 1
            self.time_slider.setValue(self.current_time_step)
        else:
            self.auto_play_timer.stop()
            print("自动播放完成")

    def on_time_changed(self, value):
        """时间滑块值改变"""
        self.current_time_step = value
        self._update_time_display()

        # 更新风险显示
        if self.risk_data:
            self._update_risk_display(value)

        # 更新路线显示
        if self.escape_routes:
            self._update_route_display(value)

    def _update_time_display(self):
        """更新时间显示"""
        self.lb_time_display.setText(f"时间: {self.current_time_step+1} / {self.max_time_steps}")

    def _update_risk_display(self, time_step):
        """更新风险显示"""
        if not self.risk_data or time_step >= len(self.risk_data):
            return

        current_risk = self.risk_data[time_step]

        # 更新每个方块的颜色
        for row in range(self.chessboard.size):
            for col in range(self.chessboard.size):
                if row < len(current_risk) and col < len(current_risk[row]):
                    risk_value = current_risk[row][col]
                    square = self.chessboard.squares[row][col]

                    # 根据状态设置颜色
                    if self.chessboard.state_matrix[row][col] == 1:  # 墙体
                        continue
                    elif self.chessboard.state_matrix[row][col] == 2:  # 出口
                        square.setBrush(QBrush(QColor(0, 255, 0)))  # 保持绿色
                    elif self.chessboard.state_matrix[row][col] == 3:  # 起点
                        square.setBrush(QBrush(QColor(255, 0, 255)))  # 保持粉色
                    else:
                        # 根据风险值设置颜色（绿到红）
                        self._set_risk_color(square, risk_value)

    def _set_risk_color(self, square, risk_value):
        """根据风险值设置颜色"""
        if risk_value <= 0:
            # 安全 - 白色
            square.setBrush(QBrush(QColor(255, 255, 255)))
        else:
            # 风险值0-0.9映射到绿色(0,255,0)到红色(255,0,0)
            risk_value = min(0.9, max(0, risk_value))

            # 线性插值
            red = int(risk_value * 255 / 0.9)
            green = int((0.9 - risk_value) * 255 / 0.9)
            blue = 0

            square.setBrush(QBrush(QColor(red, green, blue)))

    def _update_route_display(self, time_step):
        """更新路线显示"""
        if self.escape_routes and len(self.escape_routes) > 0:
            route = self.escape_routes[0]
            if route:
                # 如果时间步超过路线长度，显示完整路径
                # 否则按时间步显示路径
                max_display_step = min(time_step + 1, len(route))
                if time_step >= len(route) - 1:
                    max_display_step = len(route)

                for i in range(max_display_step):
                    row, col = route[i]
                    if (0 <= row < self.chessboard.size and
                            0 <= col < self.chessboard.size and
                            self.chessboard.state_matrix[row][col] not in [1, 2, 3]):  # 不覆盖墙体、出口、起点
                        square = self.chessboard.squares[row][col]
                        square.setBrush(QBrush(QColor(0, 0, 255)))  # 蓝色路径

    def on_back_clicked(self):
        """返回主菜单"""
        # 保存当前状态（包含风险显示和路线）
        current_matrix = self.chessboard.get_state_matrix()

        # 保存风险和路线数据到interface_manager
        simulation_data = {
            'risk_data': self.risk_data,
            'escape_routes': self.escape_routes,
            'current_time_step': self.current_time_step,
            'max_time_steps': self.max_time_steps
        }
        self.interface_manager.set_simulation_data(simulation_data)

        self.interface_manager.set_board_data(copy.deepcopy(current_matrix))

        # 停止自动播放
        if self.auto_play_timer.isActive():
            self.auto_play_timer.stop()

        self.interface_manager.show_main_menu()

    def load_board_data(self, matrix):
        """加载棋盘数据"""
        if matrix and self.chessboard:
            self.chessboard.set_board_from_matrix(matrix)
            print("仿真界面棋盘数据已加载")