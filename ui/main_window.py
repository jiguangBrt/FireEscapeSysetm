from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QBrush, QPen, QColor
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsRectItem


class ChessboardSquare(QGraphicsRectItem):
    """单个棋盘方块类"""

    def __init__(self, x, y, size, row, col, parent_board):
        super().__init__(x, y, size, size)
        self.row = row
        self.col = col
        self.parent_board = parent_board
        self.is_black = False

        # 设置清晰的网格样式
        self.setPen(QPen(QColor(0, 0, 0), 1))  # 黑色边框，1像素宽
        self.setBrush(QBrush(QColor(255, 255, 255)))  # 白色填充

        # 启用鼠标事件
        self.setAcceptHoverEvents(True)

    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.LeftButton:
            self.toggle_color()
            self.parent_board.is_dragging = True
            # 记录拖拽开始时的目标状态（与当前状态相反）
            self.parent_board.last_drag_state = self.is_black

    def hoverEnterEvent(self, event):
        """鼠标进入事件 - 用于拖拽绘制"""
        if self.parent_board.is_dragging:
            # 拖拽模式下，将方块设置为目标状态
            target_state = self.parent_board.last_drag_state
            if self.is_black != target_state:
                self.toggle_color()

    def toggle_color(self):
        """切换方块颜色"""
        self.is_black = not self.is_black
        if self.is_black:
            self.setBrush(QBrush(QColor(0, 0, 0)))  # 黑色填充
        else:
            self.setBrush(QBrush(QColor(255, 255, 255)))  # 白色填充

        # 保持黑色边框以显示网格
        self.setPen(QPen(QColor(0, 0, 0), 1))

        # 更新父棋盘的状态矩阵
        self.parent_board.update_state_matrix(self.row, self.col, 1 if self.is_black else 0)


class InteractiveChessboard(QtCore.QObject):
    """交互式棋盘类"""

    def __init__(self, graphics_view, size=50):
        super().__init__()
        self.graphics_view = graphics_view
        self.size = size
        # 计算方块大小：500px视图 / 50格子 = 10px每格
        view_size = 500  # graphicsView的尺寸
        self.square_size = view_size // size  # 10px每个方块
        self.is_dragging = False
        self.last_drag_state = False

        # 初始化状态矩阵 (0表示白色，1表示黑色)
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

        print(f"Creating {self.size}x{self.size} chessboard with {self.square_size}px squares")

        for row in range(self.size):
            square_row = []
            for col in range(self.size):
                x = col * self.square_size
                y = row * self.square_size

                square = ChessboardSquare(x, y, self.square_size, row, col, self)
                self.scene.addItem(square)
                square_row.append(square)

            self.squares.append(square_row)

        # 设置场景大小为精确的棋盘大小
        board_size = self.size * self.square_size
        self.scene.setSceneRect(0, 0, board_size, board_size)

        # 设置视图属性
        self.graphics_view.setRenderHint(QtGui.QPainter.Antialiasing, False)  # 关闭抗锯齿以保持网格清晰
        self.graphics_view.setDragMode(QtWidgets.QGraphicsView.NoDrag)
        self.graphics_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.graphics_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # 不使用fitInView，而是直接设置缩放以铺满视图
        self.graphics_view.resetTransform()
        self.graphics_view.scale(1.0, 1.0)  # 1:1缩放

        print(f"Scene rect: {self.scene.sceneRect()}")
        print(f"Created {len(self.scene.items())} items")

    def setup_mouse_events(self):
        """设置鼠标事件"""
        # 安装事件过滤器来捕获鼠标释放事件
        self.graphics_view.installEventFilter(self)
        self.graphics_view.viewport().installEventFilter(self)

    def eventFilter(self, obj, event):
        """事件过滤器 - 捕获鼠标释放事件结束拖拽"""
        if event.type() == QtCore.QEvent.MouseButtonRelease:
            if event.button() == Qt.LeftButton:
                self.is_dragging = False
                return True
        elif event.type() == QtCore.QEvent.MouseMove and self.is_dragging:
            # 处理鼠标移动事件来实现拖拽绘制
            pos = self.graphics_view.mapToScene(event.pos())
            item = self.scene.itemAt(pos, self.graphics_view.transform())
            if isinstance(item, ChessboardSquare):
                target_state = self.last_drag_state
                if item.is_black != target_state:
                    item.toggle_color()
            return True
        return super().eventFilter(obj, event)

    def update_state_matrix(self, row, col, state):
        """更新状态矩阵"""
        if 0 <= row < self.size and 0 <= col < self.size:
            self.state_matrix[row][col] = state

    def get_state_matrix(self):
        """获取当前状态矩阵"""
        return self.state_matrix

    def clear_board(self):
        """清空棋盘"""
        for row in range(self.size):
            for col in range(self.size):
                square = self.squares[row][col]
                if square.is_black:
                    square.toggle_color()

    def set_board_from_matrix(self, matrix):
        """从矩阵设置棋盘状态"""
        if len(matrix) != self.size or len(matrix[0]) != self.size:
            print("矩阵大小不匹配")
            return

        for row in range(self.size):
            for col in range(self.size):
                square = self.squares[row][col]
                target_state = matrix[row][col] == 1

                if square.is_black != target_state:
                    square.toggle_color()


# 修改后的主窗口类
class Ui_FireEscapeSystem(object):
    def setupUi(self, FireEscapeSystem):
        FireEscapeSystem.setObjectName("FireEscapeSystem")
        FireEscapeSystem.resize(1000, 734)
        self.centralwidget = QtWidgets.QWidget(FireEscapeSystem)
        self.centralwidget.setObjectName("centralwidget")

        # 原有的graphicsView
        self.graphicsView = QtWidgets.QGraphicsView(self.centralwidget)
        self.graphicsView.setGeometry(QtCore.QRect(40, 140, 500, 500))
        self.graphicsView.setObjectName("graphicsView")

        # 初始化交互式棋盘
        self.chessboard = InteractiveChessboard(self.graphicsView)

        # 原有的其他控件
        self.lbTitle = QtWidgets.QLabel(self.centralwidget)
        self.lbTitle.setGeometry(QtCore.QRect(280, 50, 431, 71))
        self.lbTitle.setStyleSheet("QLabel {\n"
                                   "    background-color: #8B4513;  /* SaddleBrown 褐色 */\n"
                                   "    color: white;\n"
                                   "    font-size: 20px;\n"
                                   "    font-weight: bold;\n"
                                   "    padding: 10px 20px;\n"
                                   "    border-radius: 10px;\n"
                                   "}\n"
                                   "")
        self.lbTitle.setObjectName("lbTitle")

        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(610, 240, 291, 91))
        self.pushButton.setStyleSheet("QPushButton {\n"
                                      "    font: 75 25pt \"Arial\";\n"
                                      "    background-color: rgba(0, 255, 255, 64);\n"
                                      "    border: 1px solid rgba(0, 255, 255, 64);\n"
                                      "    border-radius: 12px;\n"
                                      "    color: white;\n"
                                      "    padding: 8px 20px;\n"
                                      "    font-weight: bold;\n"
                                      "    font-size: 30px;\n"
                                      "    backdrop-filter: blur(4px);\n"
                                      "}\n"
                                      "QPushButton:hover {\n"
                                      "    background-color:rgba(0, 255, 255, 64);\n"
                                      "}\n"
                                      "QPushButton:pressed {\n"
                                      "    background-color: rgba(0, 238, 255, 64);\n"
                                      "}")
        self.pushButton.setIconSize(QtCore.QSize(19, 19))
        self.pushButton.setObjectName("pushButton")

        self.btnStartSim = QtWidgets.QPushButton(self.centralwidget)
        self.btnStartSim.setGeometry(QtCore.QRect(610, 380, 281, 81))
        self.btnStartSim.setStyleSheet("QPushButton {\n"
                                       "    font: 75 25pt \"Arial\";\n"
                                       "    background-color: rgba(0, 255, 42, 64);\n"
                                       "    border: 1px solid rgba(0, 255, 42, 64);\n"
                                       "    border-radius: 12px;\n"
                                       "    color: white;\n"
                                       "    padding: 8px 20px;\n"
                                       "    font-weight: bold;\n"
                                       "    font-size: 30px;\n"
                                       "    backdrop-filter: blur(4px);\n"
                                       "}\n"
                                       "QPushButton:hover {\n"
                                       "    background-color:rgba(0, 255, 127, 64);\n"
                                       "}\n"
                                       "QPushButton:pressed {\n"
                                       "    background-color: rgba(0, 255, 42, 64);\n"
                                       "}")
        self.btnStartSim.setObjectName("btnStartSim")

        # 添加清空按钮
        self.btnClear = QtWidgets.QPushButton(self.centralwidget)
        self.btnClear.setGeometry(QtCore.QRect(610, 520, 281, 61))
        self.btnClear.setStyleSheet("QPushButton {\n"
                                    "    font: 75 18pt \"Arial\";\n"
                                    "    background-color: rgba(255, 0, 0, 64);\n"
                                    "    border: 1px solid rgba(255, 0, 0, 64);\n"
                                    "    border-radius: 12px;\n"
                                    "    color: white;\n"
                                    "    padding: 8px 20px;\n"
                                    "    font-weight: bold;\n"
                                    "}\n"
                                    "QPushButton:hover {\n"
                                    "    background-color:rgba(255, 64, 64, 64);\n"
                                    "}\n"
                                    "QPushButton:pressed {\n"
                                    "    background-color: rgba(255, 0, 0, 64);\n"
                                    "}")
        self.btnClear.setObjectName("btnClear")

        # 背景标签
        self.lbBackground = QtWidgets.QLabel(self.centralwidget)
        self.lbBackground.setGeometry(QtCore.QRect(0, 0, 1000, 750))
        self.lbBackground.setText("")
        self.lbBackground.setPixmap(QtGui.QPixmap("../resources/背景图.png"))
        self.lbBackground.setScaledContents(True)
        self.lbBackground.setObjectName("lbBackground")

        # 设置层级
        self.lbBackground.raise_()
        self.graphicsView.raise_()
        self.lbTitle.raise_()
        self.pushButton.raise_()
        self.btnStartSim.raise_()
        self.btnClear.raise_()

        FireEscapeSystem.setCentralWidget(self.centralwidget)

        # 连接信号
        self.btnClear.clicked.connect(self.clear_chessboard)

        self.retranslateUi(FireEscapeSystem)
        QtCore.QMetaObject.connectSlotsByName(FireEscapeSystem)

    def retranslateUi(self, FireEscapeSystem):
        _translate = QtCore.QCoreApplication.translate
        FireEscapeSystem.setWindowTitle(_translate("FireEscapeSystem", "MainWindow"))
        self.lbTitle.setText(_translate("FireEscapeSystem", "Fire escape route prediction system"))
        self.pushButton.setText(_translate("FireEscapeSystem", "Draw a floor plan"))
        self.btnStartSim.setText(_translate("FireEscapeSystem", "Start simulation"))
        self.btnClear.setText(_translate("FireEscapeSystem", "Clear Board"))

    def clear_chessboard(self):
        """清空棋盘"""
        self.chessboard.clear_board()

    def get_floor_plan_matrix(self):
        """获取当前地图矩阵"""
        return self.chessboard.get_state_matrix()


# 使用示例
if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    FireEscapeSystem = QtWidgets.QMainWindow()
    ui = Ui_FireEscapeSystem()
    ui.setupUi(FireEscapeSystem)

    FireEscapeSystem.show()


    # 演示如何获取矩阵状态
    def print_matrix():
        matrix = ui.get_floor_plan_matrix()
        print("当前地图状态:")
        for row in matrix:
            print(''.join(['1' if cell else '0' for cell in row]))


    # 可以连接到按钮来查看状态
    ui.btnStartSim.clicked.connect(print_matrix)

    sys.exit(app.exec_())