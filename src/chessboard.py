from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QBrush, QPen, QColor
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsRectItem
import copy


class ChessboardSquare(QGraphicsRectItem):
    """单个棋盘方块类"""

    def __init__(self, x, y, size, row, col, parent_board):
        super().__init__(x, y, size, size)
        self.row = row
        self.col = col
        self.parent_board = parent_board
        self.state = 0  # 0=白色空地, 1=黑色墙体, 2=绿色出口, 3=逃生起始点

        # 设置清晰的网格样式
        self.setPen(QPen(QColor(0, 0, 0), 1))  # 黑色边框，1像素宽
        self.setBrush(QBrush(QColor(255, 255, 255)))  # 白色填充

        # 启用鼠标事件
        self.setAcceptHoverEvents(True)

    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if self.parent_board.is_interactive:
            if event.button() == Qt.LeftButton:
                # 左键：添加当前编辑模式的元素
                self.add_element()
                if self.parent_board.drag_enabled:
                    self.parent_board.is_dragging = True
                    self.parent_board.drag_mode = "add"
            elif event.button() == Qt.RightButton:
                # 右键：删除元素（设为空地）
                self.remove_element()
                if self.parent_board.drag_enabled:
                    self.parent_board.is_dragging = True
                    self.parent_board.drag_mode = "remove"

    def hoverEnterEvent(self, event):
        """鼠标进入事件 - 用于拖拽编辑"""
        if (self.parent_board.is_dragging and
                self.parent_board.is_interactive and
                self.parent_board.drag_enabled):
            if self.parent_board.drag_mode == "add":
                self.add_element()
            elif self.parent_board.drag_mode == "remove":
                self.remove_element()

    def add_element(self):
        """添加当前编辑模式的元素"""
        if self.parent_board.edit_mode == "wall":
            if self.state != 1:  # 如果不是墙体，则设为墙体
                self.set_state(1)
        elif self.parent_board.edit_mode == "output":
            if self.state != 2:  # 如果不是出口，则设为出口
                self.set_state(2)

    def remove_element(self):
        """删除元素（设为空地）"""
        if self.state != 0:  # 如果不是空地，则设为空地
            self.set_state(0)

    def change_state(self):
        """切换方块状态"""
        if self.parent_board.edit_mode == "wall":
            # 墙体编辑模式：在白色(0)和黑色(1)之间切换
            self.state = 1 if self.state == 0 else 0
        elif self.parent_board.edit_mode == "output":
            # 出口编辑模式：在白色(0)和绿色(2)之间切换
            self.state = 2 if self.state == 0 else 0
        elif self.parent_board.edit_mode == "start":
            # 逃生起点编辑模式：在白色(0)和粉色(3)之间切换
            self.state = 3 if self.state == 0 else 0

        self.update_appearance()
        self.parent_board.update_state_matrix(self.row, self.col, self.state)

    def set_state(self, state):
        """设置方块状态"""
        self.state = state
        self.update_appearance()
        self.parent_board.update_state_matrix(self.row, self.col, self.state)

    def update_appearance(self):
        """更新方块外观"""
        if self.state == 0:
            # 白色空地
            self.setBrush(QBrush(QColor(255, 255, 255)))
        elif self.state == 1:
            # 黑色墙体
            self.setBrush(QBrush(QColor(0, 0, 0)))
        elif self.state == 2:
            # 绿色出口
            self.setBrush(QBrush(QColor(0, 255, 0)))
        elif self.state == 3:
            # 粉色逃生起始点
            self.setBrush(QBrush(QColor(255, 0, 255)))

        # 保持黑色边框以显示网格
        self.setPen(QPen(QColor(0, 0, 0), 1))


class InteractiveChessboard(QtCore.QObject):
    """交互式棋盘类"""

    def __init__(self, graphics_view, size=32):
        super().__init__()
        self.graphics_view = graphics_view
        self.size = size
        view_size = 500
        self.square_size = view_size // size

        # 交互控制
        self.is_interactive = True
        self.drag_enabled = True
        self.is_dragging = False
        self.drag_mode = "add"  # "add" 或 "remove"
        self.edit_mode = "wall"  # "wall" 或 "output"


        # 初始化状态矩阵 (0=空地, 1=墙体, 2=出口, 3=逃生起始点)
        self.state_matrix = [[0 for _ in range(size)] for _ in range(size)]

        # 创建场景
        self.scene = QGraphicsScene()
        self.graphics_view.setScene(self.scene)

        # 存储所有方块
        self.squares = []

        self.create_chessboard()
        self.setup_mouse_events()

    def create_chessboard(self):
        """创建棋盘"""
        self.squares = []

        for row in range(self.size):
            square_row = []
            for col in range(self.size):
                x = col * self.square_size
                y = row * self.square_size

                square = ChessboardSquare(x, y, self.square_size, row, col, self)
                self.scene.addItem(square)
                square_row.append(square)

            self.squares.append(square_row)

        # 设置场景大小
        board_size = self.size * self.square_size
        self.scene.setSceneRect(0, 0, board_size, board_size)

        # 设置视图属性
        self.graphics_view.setRenderHint(QtGui.QPainter.Antialiasing, False)
        self.graphics_view.setDragMode(QtWidgets.QGraphicsView.NoDrag)
        self.graphics_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.graphics_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.graphics_view.resetTransform()
        self.graphics_view.scale(1.0, 1.0)

    def setup_mouse_events(self):
        """设置鼠标事件"""
        self.graphics_view.installEventFilter(self)
        self.graphics_view.viewport().installEventFilter(self)

    def eventFilter(self, obj, event):
        """事件过滤器"""
        if not self.is_interactive or not self.drag_enabled:
            return super().eventFilter(obj, event)

        if event.type() == QtCore.QEvent.MouseButtonRelease:
            if event.button() in [Qt.LeftButton, Qt.RightButton]:
                self.is_dragging = False
                return True
        elif event.type() == QtCore.QEvent.MouseMove and self.is_dragging:
            pos = self.graphics_view.mapToScene(event.pos())
            item = self.scene.itemAt(pos, self.graphics_view.transform())
            if isinstance(item, ChessboardSquare):
                if self.drag_mode == "add":
                    item.add_element()
                elif self.drag_mode == "remove":
                    item.remove_element()
            return True
        return super().eventFilter(obj, event)

    def set_interactive(self, interactive):
        """设置是否允许交互"""
        self.is_interactive = interactive

    def set_edit_mode(self, mode):
        """设置编辑模式"""
        self.edit_mode = mode

    def set_drag_enabled(self, enabled):
        """设置是否启用拖拽"""
        self.drag_enabled = enabled

    def update_state_matrix(self, row, col, state):
        """更新状态矩阵"""
        if 0 <= row < self.size and 0 <= col < self.size:
            self.state_matrix[row][col] = state

    def get_state_matrix(self):
        """获取当前状态矩阵"""
        return copy.deepcopy(self.state_matrix)

    def clear_board(self):
        """清空棋盘"""
        for row in range(self.size):
            for col in range(self.size):
                square = self.squares[row][col]
                square.set_state(0)

        # 重置状态矩阵
        self.state_matrix = [[0 for _ in range(self.size)] for _ in range(self.size)]

    def set_board_from_matrix(self, matrix):
        """从矩阵设置棋盘状态"""
        if not matrix or len(matrix) != self.size:
            print(f"矩阵大小不匹配: 期望 {self.size}x{self.size}")
            return

        try:
            # 更新内部状态矩阵
            self.state_matrix = copy.deepcopy(matrix)

            # 更新每个方块的显示状态
            for row in range(self.size):
                if len(matrix[row]) != self.size:
                    print(f"矩阵行 {row} 大小不匹配: 期望 {self.size}")
                    continue

                for col in range(self.size):
                    state = matrix[row][col]
                    # 验证状态值有效性
                    if state not in [0, 1, 2, 3]:
                        print(f"无效状态值 {state} 在位置 ({row}, {col})")
                        state = 0  # 默认为空地

                    # 更新方块状态
                    if row < len(self.squares) and col < len(self.squares[row]):
                        self.squares[row][col].set_state(state)

            print("棋盘状态已从矩阵更新")

        except Exception as e:
            print(f"设置棋盘状态时出错: {e}")

    def get_board_statistics(self):
        """获取棋盘统计信息"""
        wall_count = 0
        output_count = 0
        empty_count = 0

        for row in self.state_matrix:
            for cell in row:
                if cell == 0:
                    empty_count += 1
                elif cell == 1:
                    wall_count += 1
                elif cell == 2:
                    output_count += 1

        return {
            'empty': empty_count,
            'wall': wall_count,
            'output': output_count,
            'total': self.size * self.size
        }