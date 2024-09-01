import sys
import os
import time
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QPushButton,
                               QVBoxLayout, QHBoxLayout, QListWidget, QLabel,
                               QRubberBand, QDialog, QDialogButtonBox, QListWidgetItem,
                               QScrollArea, QMessageBox, QGridLayout, QToolTip, QStyle, QGraphicsDropShadowEffect)
from PySide6.QtGui import (QPixmap, QScreen, QPainter, QColor, QIcon, QGuiApplication,
                           QImage, QTransform, QCursor, QPainterPath, QRegion, QPalette, QPen)
from PySide6.QtCore import (Qt, QRect, QPoint, Signal, QSize, QPropertyAnimation,
                            QEasingCurve, Property, QEvent, QThread, QTimer, QThreadPool, QRunnable, QObject)

import traceback

from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QWidget, QRubberBand, QApplication, QLabel
from PySide6.QtCore import Qt, QRect, QPoint, Signal, QTimer
from PySide6.QtGui import QPixmap, QGuiApplication

import sys
import os
import tempfile


# import win32pipe, win32file, pywintypes
# def is_already_running():
#     try:
#         pipe_name = r'\\.\pipe\ScreenshotToolSingleInstance'
#         handle = win32file.CreateFile(
#             pipe_name,
#             win32file.GENERIC_READ | win32file.GENERIC_WRITE,
#             0,
#             None,
#             win32file.OPEN_EXISTING,
#             0,
#             None
#         )
#         # 如果能打开管道，说明已经有一个实例在运行
#         win32file.CloseHandle(handle)
#         return True
#     except pywintypes.error:
#         # 如果管道不存在，说明这是第一个实例
#         return False
#
# def create_single_instance_pipe():
#     pipe_name = r'\\.\pipe\ScreenshotToolSingleInstance'
#     pipe_handle = win32pipe.CreateNamedPipe(
#         pipe_name,
#         win32pipe.PIPE_ACCESS_DUPLEX,
#         win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_READMODE_MESSAGE | win32pipe.PIPE_WAIT,
#         1, 65536, 65536,
#         0,
#         None
#     )
#     return pipe_handle
def global_exception_handler(exctype, value, traceback):
    print("Unhandled exception:", exctype, value)
    print("Traceback:")
    import traceback as tb
    tb.print_tb(traceback)


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class SplashScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        layout = QVBoxLayout(self)
        self.label = QLabel(self)
        pixmap = QPixmap(resource_path("icons/logo_big.png"))  # 替换为您的启动画面图片路径
        self.label.setPixmap(pixmap)
        layout.addWidget(self.label)

        self.setFixedSize(pixmap.width() + 120, pixmap.height() + 140)
        self.center()

    def center(self):
        qr = self.frameGeometry()
        cp = QGuiApplication.primaryScreen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


class ScreenshotItem(QWidget):
    def __init__(self, pixmap, filename, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.filename = filename

        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 创建一个容器来包含图片和删除按钮
        container = QWidget()
        container.setStyleSheet("background-color: transparent;")
        container_layout = QGridLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        # 图片标签
        self.image_label = QLabel()
        self.image_label.setFixedSize(300, 150)  # 设置固定大小
        self.image_label.setScaledContents(True)  # 允许内容缩放
        self.image_label.setAlignment(Qt.AlignCenter)

        # 缩放并裁剪图片
        scaled_pixmap = self.scale_and_crop_pixmap(pixmap, 300, 150)
        self.image_label.setPixmap(scaled_pixmap)

        # 删除按钮
        self.delete_button = QPushButton()
        delete_icon = QIcon(resource_path("icons/remove_icon.png"))
        self.delete_button.setIcon(delete_icon)
        self.delete_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
            }
            QPushButton:hover {
                background-color: rgba(255, 0, 0, 50);
            }
        """)
        self.delete_button.setFixedSize(24, 24)
        self.delete_button.setIconSize(self.delete_button.size())
        self.delete_button.hide()

        # 将图片和删除按钮添加到容器布局
        container_layout.addWidget(self.image_label, 0, 0)
        container_layout.addWidget(self.delete_button, 0, 0, Qt.AlignTop | Qt.AlignRight)

        # 将容器添加到主布局
        main_layout.addWidget(container)

    def scale_and_crop_pixmap(self, pixmap, target_width, target_height):
        # 计算缩放比例
        width_ratio = target_width / pixmap.width()
        height_ratio = target_height / pixmap.height()
        scale_ratio = max(width_ratio, height_ratio)

        # 缩放图片
        scaled_pixmap = pixmap.scaled(
            pixmap.width() * scale_ratio,
            pixmap.height() * scale_ratio,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        # 裁剪图片
        x = (scaled_pixmap.width() - target_width) // 2
        y = (scaled_pixmap.height() - target_height) // 2
        cropped_pixmap = scaled_pixmap.copy(
            x, y, target_width, target_height
        )

        return cropped_pixmap

    def enterEvent(self, event):
        self.delete_button.show()

    def leaveEvent(self, event):
        self.delete_button.hide()

    def sizeHint(self):
        return QSize(150, 150)



class Separator(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(4)
        self.setAutoFillBackground(True)  # 确保背景被填充
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("#FFA500"))  # 设置背景色
        self.setPalette(palette)


class ScreenshotTool(QMainWindow):
    def __init__(self):
        super().__init__()

        # 设置窗口无边框
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # 创建阴影效果
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(20)
        self.shadow.setColor(QColor(0, 0, 0, 80))
        self.shadow.setOffset(0, 0)

        # 创建一个中央窗口部件并应用阴影效果
        self.central_widget = QWidget()
        self.central_widget.setGraphicsEffect(self.shadow)
        self.setCentralWidget(self.central_widget)

        # 主布局
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(10, 10, 10, 10)  # 为阴影留出空间

        self.setWindowTitle("截图工具")
        self.setGeometry(100, 100, 300, 500)  # 增加宽度到 400

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # Top area: buttons with purple background
        top_widget = QWidget()
        top_widget.setStyleSheet("background-color: #651FFF;")
        top_layout = QVBoxLayout(top_widget)
        top_layout.setContentsMargins(10, 10, 10, 10)
        top_layout.setSpacing(10)

        # Logo icon
        icon_container = QWidget()
        icon_layout = QHBoxLayout(icon_container)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_layout.setSpacing(0)

        # Logo
        icon_label = QLabel()
        icon_pixmap = QPixmap(resource_path("icons/logo_small.png"))
        icon_label.setPixmap(icon_pixmap.scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        icon_layout.addWidget(icon_label)

        icon_layout.addStretch(1)  # 添加伸缩项，使logo靠左，关闭按钮靠右

        # Close button
        self.close_button = QPushButton()
        close_icon = QIcon(resource_path("icons/close.png"))  # 请确保您有一个合适的关闭图标
        self.close_button.setIcon(close_icon)
        self.close_button.setIconSize(QSize(24, 24))
        self.close_button.setStyleSheet("""
                    QPushButton {
                        background-color: transparent;
                        border: none;
                    }
                    # QPushButton:hover {
                    #     background-color: rgba(255, 255, 255, 0.2);
                    # }
                    QPushButton:pressed {
                        background-color: rgba(255, 255, 255, 0.1);
                    }
                """)
        self.close_button.setFixedSize(48, 48)  # 设置固定大小，与logo大小一致
        # self.close_button.clicked.connect(self.close)  # 连接到关闭功能
        self.close_button.clicked.connect(self.close_application)  # 修改这里
        icon_layout.addWidget(self.close_button)

        top_layout.addWidget(icon_container)

        # Buttons container
        buttons_widget = QWidget()
        buttons_layout = QHBoxLayout(buttons_widget)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(10)

        # 创建截图按钮
        self.capture_button = QPushButton("截图")
        self.capture_button.setStyleSheet("""
            QPushButton {
                background-color: #651FFF;
                color: black;
                border: none;
                padding: 5px 10px;
                font-size: 16px;
                font-weight: bold;
                text-align: left;  /* 文字左对齐 */
            }
            QPushButton:hover {
                background-color: #651FFF;
            }
            QPushButton:pressed {
                background-color: #2758b3;
            }
        """)

        # 设置图标
        icon = QIcon(resource_path("icons/cut_icon.png"))  # 确保路径正确
        self.capture_button.setIcon(icon)
        self.capture_button.setIconSize(QSize(24, 24))
        self.capture_button.clicked.connect(self.start_capture)

        # 标题标签
        self.title_label = QLabel("截图板")
        self.title_label.setStyleSheet("""
                    color: white;
                    font-size: 20px;
                    font-weight: bold;
                """)
        self.title_label.setAlignment(Qt.AlignCenter)

        # 全部清空按钮
        self.delete_all_button = QPushButton("全部清空")
        self.delete_all_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;  /* 透明背景 */
                color: black;
                border: none;  /* 无边框 */
                padding: 5px 10px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(50, 104, 199, 0.1);  /* 半透明的悬停效果 */
            }
            QPushButton:pressed {
                background-color: rgba(39, 88, 179, 0.2);  /* 半透明的按下效果 */
            }
        """)

        self.delete_all_button.clicked.connect(self.delete_all_screenshots)

        buttons_layout.addWidget(self.capture_button)
        buttons_layout.addStretch(1)
        buttons_layout.addWidget(self.title_label)
        buttons_layout.addStretch(1)
        buttons_layout.addWidget(self.delete_all_button)

        top_layout.addWidget(buttons_widget)
        self.layout.addWidget(top_widget)

        # 添加橙黄色分隔条
        # separator = Separator()
        # self.layout.addWidget(separator)
        # # self.layout.setContentsMargins(0, 5, 0, 5)  # 在分隔条上下添加 5 像素的间距

        # 添加分割线
        self.separator = Separator()
        self.layout.addWidget(self.separator)

        # # 确保分割线周围有一些空间
        # self.layout.addSpacing(5)  # 在分割线上方添加空间
        # self.layout.addWidget(self.separator)
        # self.layout.addSpacing(5)  # 在分割线下方添加空间

        # Bottom area: content with light background
        bottom_widget = QWidget()
        bottom_widget.setStyleSheet("background-color: #EFEFEF;")
        bottom_layout = QVBoxLayout(bottom_widget)

        # Screenshot list
        self.screenshot_list = QListWidget()
        self.screenshot_list.setIconSize(QSize(100, 100))
        self.screenshot_list.setResizeMode(QListWidget.Adjust)
        self.screenshot_list.setSpacing(10)
        self.screenshot_list.itemDoubleClicked.connect(self.show_full_screenshot)
        self.screenshot_list.setStyleSheet("""
                    QListWidget {
                        border: none;
                        background-color: #f0f0f0;
                    }
                    QListWidget::item {
                        border-bottom: 1px solid #e0e0e0;
                        padding: 5px;
                    }
                    QListWidget::item:selected {
                        background-color: transparent;
                        border: 3px solid #E2974B;
                        padding: 2px;
                    }
                    QScrollBar:vertical {
                        border: none;
                        background: #f0f0f0;
                        width: 10px;
                        margin: 0px 0px 0px 0px;
                    }
                    QScrollBar::handle:vertical {
                        background: #c0c0c0;
                        min-height: 30px;
                        border-radius: 5px;
                    }
                    QScrollBar::handle:vertical:hover {
                        background: #a0a0a0;
                    }
                    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                        height: 0px;
                    }
                    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                        background: none;
                    }
                """)

        bottom_layout.addWidget(self.screenshot_list)

        self.layout.addWidget(bottom_widget)

        self.load_saved_screenshots()

        self.expanded_height = 500
        self.collapsed_height = 20  # 减小收缩高度
        self.setFixedWidth(400)

        self.is_expanded = True
        self.is_dragging = False
        self.drag_position = None
        self.at_top_edge = False

        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)

        self.expand_timer = QTimer(self)
        self.expand_timer.setSingleShot(True)
        self.expand_timer.timeout.connect(self.expand)

        self.collapse_timer = QTimer(self)
        self.collapse_timer.setSingleShot(True)
        self.collapse_timer.timeout.connect(self.collapse)
        self.screen = QGuiApplication.primaryScreen()

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.expanded_height = 500
        self.collapsed_height = 5
        self.setFixedWidth(300)  # 设置固定宽度为 400

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.is_expanded = True
        self.is_at_top = True
        self.drag_position = None

        # 创建一个用于收缩状态的小部件
        self.collapsed_widget = QWidget(self)
        self.collapsed_widget.setStyleSheet("background-color: #651FFF; border-radius: 2px;")
        self.collapsed_widget.setFixedHeight(self.collapsed_height)
        self.collapsed_widget.setCursor(Qt.PointingHandCursor)
        self.collapsed_widget.mousePressEvent = self.handle_clicked
        self.collapsed_widget.hide()

        self.screen_capture = None
        self.is_capturing = False  # 新增标志

        self.thread_pool = QThreadPool()
        self.setWindowFlags(Qt.FramelessWindowHint)  # 移除默认的窗口框架
        self.setAttribute(Qt.WA_TranslucentBackground)  # 允许使用透明背景

        # self.setStyleSheet("""
        #             QMainWindow {
        #                 background-color: #FFFFFF;  # 设置背景色，可以根据需要调整
        #                 border-radius: 10px;  # 设置圆角半径，可以根据需要调整
        #             }
        #         """)
        # 设置样式
        self.setStyleSheet("""
                    QMainWindow {
                        background: transparent;
                    }
                    QWidget#central_widget {
                        background: white;
                        border-radius: 10px;
                    }
                """)
        self.central_widget.setObjectName("central_widget")

        self.set_rounded_corners()

        self.preview_windows = []
        # 设置窗口标志
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)

        # 创建定时器，每秒提升一次窗口
        self.raise_timer = QTimer(self)
        self.raise_timer.timeout.connect(self.ensure_on_top)
        self.raise_timer.start(1000)  # 每1000毫秒（1秒）触发一次

        # self.preview_dialog = None  # 用于存储当前的预览对话框
        self.preview_dialog = None  # 用于存储当前的预览对话框
    def ensure_on_top(self):
        self.raise_()
        self.activateWindow()

    def show_window(self):
        print("Showing main window")
        self.show()
        self.raise_()
        self.activateWindow()

    def paintEvent(self, event):
        # 重写绘制事件，绘制圆角矩形
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QColor(255, 255, 255))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), 10, 10)

    # 如果需要自定义移动窗口的功能，可以添加以下方法
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragPosition = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.dragPosition)
            event.accept()

    def set_rounded_corners(self):
        radius = 10  # 圆角半径，可以根据需要调整
        path = QPainterPath()
        path.addRoundedRect(self.rect(), radius, radius)
        mask = QRegion(path.toFillPolygon().toPolygon())
        self.setMask(mask)

    def resizeEvent(self, event):
        super().resizeEvent(event)

        if not self.is_expanded:
            self.collapsed_widget.setFixedSize(self.width(), self.collapsed_height)
        self.set_rounded_corners()  # 在窗口大小改变时重新设置圆角

    def close_application(self):
        # 关闭所有子窗口
        for window in QApplication.topLevelWidgets():
            window.close()

        # 退出应用程序
        QApplication.quit()

    def close(self):
        """
        重写关闭方法，清理资源并终止所有进程
        """
        print("Closing ScreenshotTool...")

        # 停止所有可能正在运行的线程
        if hasattr(self, 'info_thread') and self.info_thread.isRunning():
            print("Stopping info thread...")
            self.info_thread.quit()
            self.info_thread.wait()

        # 关闭所有可能打开的对话框
        for child in self.findChildren(QDialog):
            print(f"Closing dialog: {child}")
            child.close()

        # 停止所有动画
        if hasattr(self, 'animation'):
            print("Stopping animation...")
            self.animation.stop()

        # 释放资源
        if hasattr(self, 'screen_capture') and self.screen_capture is not None:
            print("Deleting screen capture...")
            self.screen_capture.deleteLater()
        else:
            print("No screen capture to delete.")

        # 保存任何需要保存的设置
        print("Saving settings...")
        # 这里添加保存设置的代码，如果有的话

        # 关闭主窗口
        print("Closing main window...")
        super().close()

        # 如果这是最后一个窗口，退出应用
        if QApplication.instance().topLevelWindows() == 0:
            print("No more windows, quitting application...")
            QApplication.instance().quit()

    def closeEvent(self, event):
        print("Close event triggered")
        if self.is_capturing:
            event.ignore()  # 如果正在截图，忽略关闭事件
            print("Close event ignored due to ongoing capture")
            self.is_capturing = False
        else:
            event.accept()  # 否则接受关闭事件
            print("Close event accepted")
            self.thread_pool.clear()
            self.thread_pool.waitForDone()

            # 关闭所有可能的子窗口
            for child in self.findChildren(QWidget):
                child.close()

            # 调用基类的 closeEvent
            super().closeEvent(event)
            self.close_application()
            event.accept()

    def show_window(self):
        print("Showing main window")
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.show()
        self.activateWindow()  # 确保窗口被激活

    def enterEvent(self, event):
        if not self.is_expanded and self.is_at_top:
            self.expand()
        self.collapse_timer.stop()

    def leaveEvent(self, event):
        if self.is_expanded and self.is_at_top:
            cursor_pos = QCursor.pos()
            if not self.geometry().contains(cursor_pos):
                self.collapse_timer.start(500)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            new_pos = event.globalPosition().toPoint() - self.drag_position
            self.move(new_pos)
            self.check_top_edge()

    def mouseReleaseEvent(self, event):
        self.check_top_edge()

    def check_top_edge(self):
        if self.y() <= 10:  # 允许一些误差
            self.move(self.x(), 0)
            self.is_at_top = True
        else:
            self.is_at_top = False
            if not self.is_expanded:
                self.expand()

    def snap_to_top(self):
        self.move(self.x(), 0)

    def snap_to_edge(self):
        screen_geometry = self.screen.availableGeometry()
        pos = self.pos()
        if pos.y() < 10:
            self.move(pos.x(), screen_geometry.top())
            self.at_top_edge = True
            # 只有在鼠标释放且窗口在顶部时才触发收缩
            if self.is_expanded:
                self.collapse()
        else:
            self.at_top_edge = False
            self.expand()

    def constrainToScreen(self, pos):
        screen_geometry = self.screen.availableGeometry()
        x = max(screen_geometry.left(), min(pos.x(), screen_geometry.right() - self.width()))
        y = max(screen_geometry.top(), min(pos.y(), screen_geometry.bottom() - self.height()))
        return QPoint(x, y)

    def collapse(self):
        if self.is_expanded and self.is_at_top:
            self.animation.setStartValue(self.geometry())
            self.animation.setEndValue(QRect(self.x(), 0, self.width(), self.collapsed_height))
            self.animation.start()
            self.is_expanded = False
            self.central_widget.hide()
            self.collapsed_widget.show()
            self.collapsed_widget.setFixedSize(self.width(), self.collapsed_height)

    def expand(self):
        if not self.is_expanded:
            self.animation.setStartValue(self.geometry())
            self.animation.setEndValue(QRect(self.x(), self.y(), self.width(), self.expanded_height))
            self.animation.start()
            self.is_expanded = True
            self.central_widget.show()
            self.collapsed_widget.hide()

    def handle_clicked(self, event):
        self.expand()

    # def resizeEvent(self, event):
    #     super().resizeEvent(event)
    #     if not self.is_expanded:
    #         self.collapsed_widget.setFixedSize(self.width(), self.collapsed_height)

    def showEvent(self, event):
        super().showEvent(event)
        self.expand()
        self.move(self.constrainToScreen(self.pos()))
        self.check_top_edge()

    def create_tab_button(self, text, icon_path):
        button = QPushButton()
        button_layout = QHBoxLayout(button)
        button_layout.setContentsMargins(5, 5, 5, 5)
        button_layout.setSpacing(5)

        text_label = QLabel(text)
        text_label.setStyleSheet("""
            color: black;
            font-size: 14px;
            font-weight: bold;
        """)

        icon_label = QLabel()
        icon_pixmap = QPixmap(resource_path(icon_path))
        icon_label.setPixmap(icon_pixmap.scaled(20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation))

        button_layout.addWidget(text_label)
        button_layout.addWidget(icon_label)
        button_layout.addStretch()

        button.setStyleSheet("""
            QPushButton {
                background-color: #3268c7;
                border: none;
                padding: 10px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #2758b3;
            }
            QPushButton:pressed {
                background-color: #1e4c9a;
            }
        """)

        return button

    def start_capture(self):
        print("Starting capture")
        self.is_capturing = True

        # 关闭当前的预览窗口（如果有）
        self.close_preview_window()

        self.hide()
        print("Main window hidden")

        # 清理旧的 screen_capture 对象
        if self.screen_capture is not None:
            self.screen_capture.deleteLater()

        self.screen_capture = ScreenCapture()
        self.screen_capture.screenshot_taken.connect(self.handle_screenshot)
        print("About to show screen capture")
        self.screen_capture.show()
        print("Screen capture shown")

    def close_preview_window(self):
        if self.preview_dialog is not None:
            self.preview_dialog.close()
            self.preview_dialog = None
    def handle_screenshot(self, pixmap, rect):
        print("Handling screenshot")
        try:
            if pixmap:
                save_dialog = SaveDialog(pixmap, rect, self)
                result = save_dialog.exec()
                if result == QDialog.Accepted:
                    filename = f"screenshot_{len(os.listdir('screenshots')) + 1}.png"
                    file_path = os.path.join("screenshots", filename)
                    pixmap.save(file_path)
                    print(f"Screenshot saved: {file_path}")
                    self.load_saved_screenshots()
                else:
                    print("Screenshot cancelled")
        except Exception as e:
            print(f"Error in handle_screenshot: {e}")
            traceback.print_exc()
        finally:
            print("Screenshot handling complete")
            self.show()  # 确保主窗口总是被显示
            print("Showing main window")
            # self.is_capturing = False  # 重置标志
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

    def load_saved_screenshots(self):
        self.screenshot_list.clear()
        if not os.path.exists("screenshots"):
            os.makedirs("screenshots")
        for filename in os.listdir("screenshots"):
            file_path = os.path.join("screenshots", filename)
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                item_widget = ScreenshotItem(pixmap, filename)
                item_widget.delete_button.clicked.connect(
                    lambda checked=False, fp=file_path: self.delete_screenshot(fp))
                item = QListWidgetItem(self.screenshot_list)
                item.setSizeHint(item_widget.sizeHint())
                self.screenshot_list.addItem(item)
                self.screenshot_list.setItemWidget(item, item_widget)
            else:
                print(f"Failed to load image: {file_path}")

    def show_full_screenshot(self, item):
        item_widget = self.screenshot_list.itemWidget(item)
        file_path = os.path.join("screenshots", item_widget.filename)

        if self.preview_dialog is None:
            # 如果没有预览对话框，创建一个新的
            self.preview_dialog = ImagePreviewDialog(file_path, self)
            self.preview_dialog.show()
        else:
            # 如果已存在预览对话框，更新它
            self.preview_dialog.update_image(file_path)
            self.preview_dialog.show()  # 确保对话框可见
            self.preview_dialog.raise_()  # 将对话框置于顶层

    # def closeEvent(self, event):
    #     # 关闭所有预览窗口
    #     for preview in self.preview_windows:
    #         preview.close()
    #     event.accept()
    # def remove_preview(self, preview_window):
    #     if preview_window in self.preview_windows:
    #         self.preview_windows.remove(preview_window)

    def delete_screenshot(self, file_path):
        try:
            os.remove(file_path)
            print(f"File {file_path} has been deleted.")
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")
        finally:
            self.load_saved_screenshots()

    def delete_all_screenshots(self):
        for filename in os.listdir("screenshots"):
            file_path = os.path.join("screenshots", filename)
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Error deleting file {file_path}: {e}")
        self.load_saved_screenshots()
        self.image_label.clear()


from PySide6.QtCore import Signal, QRect, QPoint


class ScreenCapture(QWidget):
    screenshot_taken = Signal(QPixmap, QRect)
    finished = Signal()  # 添加这行

    def __init__(self, parent=None):
        super().__init__(parent, Qt.Window)
        print("Initializing ScreenCapture")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setStyleSheet("background-color:black")
        self.setWindowOpacity(0.3)
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen)
        self.begin = QPoint()
        self.end = QPoint()
        self.rubberBand = QRubberBand(QRubberBand.Rectangle, self)

        # 使用自定义十字光标
        self.setCursor(self.create_cross_cursor())
        print("ScreenCapture initialized")

    def create_cross_cursor(self):
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)

        # 绘制白色十字
        white_pen = QPen(QColor(255, 255, 255))
        white_pen.setWidth(3)
        painter.setPen(white_pen)
        painter.drawLine(QPoint(16, 0), QPoint(16, 32))
        painter.drawLine(QPoint(0, 16), QPoint(32, 16))

        # 绘制黑色边框
        black_pen = QPen(QColor(0, 0, 0))
        black_pen.setWidth(1)
        painter.setPen(black_pen)
        painter.drawLine(QPoint(16, 0), QPoint(16, 32))
        painter.drawLine(QPoint(0, 16), QPoint(32, 16))

        painter.end()
        return QCursor(pixmap, 16, 16)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            print("Escape key pressed, closing ScreenCapture")
            self.close()

    def mousePressEvent(self, event):
        self.begin = event.position().toPoint()
        self.end = self.begin
        self.rubberBand.setGeometry(QRect(self.begin, self.end))
        self.rubberBand.show()

    def mouseMoveEvent(self, event):
        self.end = event.position().toPoint()
        self.rubberBand.setGeometry(QRect(self.begin, self.end).normalized())

    def mouseReleaseEvent(self, event):
        self.rubberBand.hide()
        rect = QRect(self.begin, self.end).normalized()
        if rect.width() > 0 and rect.height() > 0:
            screen = QApplication.primaryScreen()
            pixmap = screen.grabWindow(0, rect.x(), rect.y(), rect.width(), rect.height())
            self.screenshot_taken.emit(pixmap, rect)
        self.finished.emit()  # 发射 finished 信号
        self.close()

    def show(self):
        super().show()
        # 确保在显示窗口时也设置光标
        self.setCursor(self.create_cross_cursor())


class SaveDialog(QDialog):
    def __init__(self, pixmap, rect, parent=None):
        try:
            super().__init__(parent, Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
            self.setWindowTitle("Save Screenshot")
            self.pixmap = pixmap

            # 设置整个对话框背景透明
            self.setAttribute(Qt.WA_TranslucentBackground)
            self.setStyleSheet("background-color: transparent;")

            main_layout = QHBoxLayout(self)
            main_layout.setContentsMargins(0, 0, 0, 0)
            main_layout.setSpacing(0)

            # Image container
            image_container = QWidget()
            image_container.setAttribute(Qt.WA_TranslucentBackground)
            image_layout = QVBoxLayout(image_container)
            image_layout.setContentsMargins(0, 0, 0, 0)
            image_layout.setSpacing(0)

            self.label = QLabel()
            self.label.setPixmap(pixmap)
            image_layout.addWidget(self.label)
            main_layout.addWidget(image_container)

            # Buttons container
            buttons_container = QWidget()
            buttons_container.setAttribute(Qt.WA_TranslucentBackground)
            buttons_layout = QVBoxLayout(buttons_container)
            buttons_layout.setAlignment(Qt.AlignBottom | Qt.AlignRight)
            buttons_layout.setContentsMargins(10, 10, 10, 10)
            buttons_layout.setSpacing(10)

            # Create buttons with icons

            self.cancel_button = QPushButton()
            cancel_icon = QIcon(resource_path("icons/cancel_icon.png"))
            self.cancel_button.setIcon(cancel_icon)
            self.cancel_button.setIconSize(QSize(40, 40))
            self.cancel_button.clicked.connect(self.reject)
            self.cancel_button.setStyleSheet("""
                           QPushButton {
                               background-color: transparent;
                               border: none;
                           }
                           QPushButton:hover {
                               # background-color: rgba(244, 67, 54, 0.3);
                               # border-radius: 20px;
                           }
                       """)

            self.save_button = QPushButton()
            save_icon = QIcon(resource_path("icons/confirm_icon.png"))
            self.save_button.setIcon(save_icon)
            self.save_button.setIconSize(QSize(40, 40))
            self.save_button.clicked.connect(self.accept)
            self.save_button.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                }
                QPushButton:hover {
                    # background-color: rgba(76, 175, 80, 0.3);
                    # border-radius: 20px;
                }
            """)

            # Set button size
            button_size = 50
            self.save_button.setFixedSize(button_size, button_size)
            self.cancel_button.setFixedSize(button_size, button_size)

            buttons_layout.addWidget(self.cancel_button)
            buttons_layout.addWidget(self.save_button)
            main_layout.addWidget(buttons_container)

            self.adjustSize()
            self.move(rect.topLeft())

        except Exception as e:
            print(f"Error in SaveDialog initialization: {e}")
            traceback.print_exc()
    # def accept(self):
    #     try:
    #         super().accept()
    #     except Exception as e:
    #         print(f"Error in SaveDialog accept: {e}")
    #         traceback.print_exc()
    #
    # def reject(self):
    #     try:
    #         super().reject()
    #     except Exception as e:
    #         print(f"Error in SaveDialog reject: {e}")
    #         traceback.print_exc()


class SelectionDialog(QDialog):
    def __init__(self, image, parent=None):
        super().__init__(parent, Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.image = image
        self.setGeometry(QGuiApplication.primaryScreen().geometry())
        self.setStyleSheet("background-color: transparent;")
        self.setWindowOpacity(0.3)

        self.rubberband = QRubberBand(QRubberBand.Rectangle, self)
        self.origin = QPoint()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawImage(self.rect(),
                          QImage(self.image.data, self.image.shape[1], self.image.shape[0], QImage.Format_RGB888))

    def mousePressEvent(self, event):
        self.origin = event.position().toPoint()
        self.rubberband.setGeometry(QRect(self.origin, QSize()))
        self.rubberband.show()

    def mouseMoveEvent(self, event):
        self.rubberband.setGeometry(QRect(self.origin, event.position().toPoint()).normalized())

    def mouseReleaseEvent(self, event):
        self.rubberband.hide()
        self.accept()

    def get_selection(self):
        return self.rubberband.geometry()


from PySide6.QtWidgets import QLabel
from PySide6.QtGui import QMovie
from PySide6.QtCore import Qt, QSize


class RotatingLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(40, 40)  # 设置固定大小
        self.setAttribute(Qt.WA_TranslucentBackground)  # 允许透明背景
        self.setMouseTracking(True)  # 添加这行以支持鼠标跟踪

        # 创建 QMovie 对象
        self.movie = QMovie(resource_path("icons/loading.gif"))
        self.movie.setScaledSize(QSize(40, 40))  # 设置 GIF 大小
        self.setMovie(self.movie)
        self.movie.start()

    def startAnimation(self):
        self.movie.start()

    def stopAnimation(self):
        self.movie.stop()

    # def setRotation(self, rotation):
    #     self._rotation = rotation
    #     self.update()
    #
    # def rotation(self):
    #     return self._rotation
    #
    # rotation = Property(float, rotation, setRotation)

    # def paintEvent(self, event):
    #     painter = QPainter(self)
    #     painter.setRenderHint(QPainter.Antialiasing)
    #     painter.setRenderHint(QPainter.SmoothPixmapTransform)
    #
    #     # 清除背景
    #     painter.eraseRect(self.rect())

    # 绘制旋转的图标
    # painter.translate(self.width() / 2, self.height() / 2)
    # painter.rotate(self._rotation)
    # painter.translate(-self._pixmap.width() / 2, -self._pixmap.height() / 2)
    # painter.drawPixmap(0, 0, self._pixmap)


from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QPushButton, QWidget,
                               QHBoxLayout, QToolTip, QProgressBar)
from PySide6.QtGui import QPixmap, QIcon, QPainter, QColor, QEventPoint
from PySide6.QtCore import Qt, QPoint, QSize, Signal, QTimer, QThread, Signal
import time


class ImageInfoThread(QThread):
    info_received = Signal(str)

    def __init__(self, image_path):
        super().__init__()
        self.image_path = image_path

    def run(self):
        # 模拟异步获取图片信息的过程
        time.sleep(2)  # 模拟网络延迟
        # 这里应该是实际的API调用，获取图片信息
        info = f"图片路径: {self.image_path}\n大小: 1024x768\n格式: PNG\n创建时间: {time.ctime()}"
        self.info_received.emit(info)


class ImageInfoWorker(QRunnable):
    class Signals(QObject):
        result = Signal(str)

    def __init__(self, image_path):
        super().__init__()
        self.image_path = image_path
        self.signals = self.Signals()

    def run(self):
        # 模拟异步获取图片信息的过程
        time.sleep(2)  # 模拟网络延迟
        info = f"图片路径: {self.image_path}\n大小: 1024x768\n格式: PNG\n创建时间: {time.ctime()}"
        self.signals.result.emit(info)


class ImagePreviewDialog(QDialog):
    def __init__(self, image_path, parent=None):
        super().__init__(parent, Qt.Window | Qt.FramelessWindowHint)
        self.setWindowTitle("预览")
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.image_path = image_path

        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 图片容器
        self.image_container = QWidget(self)
        self.image_container.setAttribute(Qt.WA_TranslucentBackground)  # 设置透明背景
        image_layout = QVBoxLayout(self.image_container)
        image_layout.setContentsMargins(0, 0, 0, 0)  # 移除内边距

        # 图片标签
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setAttribute(Qt.WA_TranslucentBackground)  # 设置透明背景
        image_layout.addWidget(self.image_label)

        main_layout.addWidget(self.image_container)

        # 设置图片
        self.original_pixmap = QPixmap(image_path)
        self.updateImageSize()

        # 添加 OverlayWidget
        self.overlay = OverlayWidget(self.image_container)
        self.overlay.setGeometry(self.image_container.rect())

        # 添加关闭按钮
        self.close_button = QPushButton(self)
        self.close_button.setIcon(QIcon(resource_path("icons/close_icon.png")))
        self.close_button.setStyleSheet("""
                    QPushButton {
                        background-color: transparent;
                        border: none;
                    }
                    QPushButton:hover {
                        # background-color: rgba(255, 0, 0, 50);
                    }
                """)
        self.close_button.setFixedSize(40, 40)  # 增大按钮尺寸
        self.close_button.setIconSize(QSize(30, 30))  # 增大图标尺寸
        self.close_button.clicked.connect(self.close)

        # 添加加载动画
        self.loading_icon = LoadingIcon(self)
        self.loading_icon.setFixedSize(40, 40)
        self.loading_icon.hide()

        # 设置窗口大小和位置
        self.updateDialogSize()
        self.centerOnScreen()

        # 启动加载过程
        self.startLoading()

        # 用于窗口拖动的变量
        self.dragging = False
        self.offset = QPoint()

        # 使用 QTimer 来延迟加载图片信息
        QTimer.singleShot(0, self.startLoading)

    def update_image(self, new_image_path):
        self.image_path = new_image_path
        self.original_pixmap = QPixmap(new_image_path)
        self.updateImageSize()
        self.updateDialogSize()
        self.centerOnScreen()

        # 重新开始加载过程
        self.startLoading()
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.offset = event.position().toPoint()

    def mouseMoveEvent(self, event):
        if self.dragging:
            self.move(self.mapToParent(event.position().toPoint() - self.offset))

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False

    def updateImageSize(self):
        screen = QGuiApplication.primaryScreen().geometry()
        max_width = int(screen.width() * 0.7)
        max_height = int(screen.height() * 0.7)

        scaled_pixmap = self.original_pixmap.scaled(
            max_width, max_height,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.image_label.setPixmap(scaled_pixmap)

    def updateDialogSize(self):
        image_size = self.image_label.pixmap().size()
        dialog_size = QSize(image_size.width() + 20, image_size.height() + 20)  # 20是边距
        self.setFixedSize(dialog_size.width() + 40, dialog_size.height() + 20)  # 为按钮预留空间
        self.image_container.setFixedSize(dialog_size)
        self.overlay.setGeometry(self.image_container.geometry())
        self.close_button.move(self.width() - 50, 10)  # 调整按钮位置

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.overlay.setGeometry(self.image_container.rect())
        self.close_button.move(self.width() - 50, 10)  # 调整按钮位置
        self.overlay.updateInfoButtonPosition()

    def centerOnScreen(self):
        screen = self.screen().availableGeometry()
        self.move((screen.width() - self.width()) // 2, (screen.height() - self.height()) // 2)

    def startLoading(self):
        self.loading_icon.show()
        self.loading_icon.move(10, 10)  # 放在左上角
        self.loading_icon.startAnimation()

        # # 创建并启动线程
        # self.info_thread = ImageInfoThread(self.image_path)
        # self.info_thread.info_received.connect(self.onInfoReceived)
        # self.info_thread.start()
        # 使用 QThreadPool 来处理图片信息加载
        worker = ImageInfoWorker(self.image_path)
        worker.signals.result.connect(self.onInfoReceived)
        QThreadPool.globalInstance().start(worker)

    def onInfoReceived(self, info):
        self.loading_icon.stopAnimation()
        self.loading_icon.hide()
        # 更新 OverlayWidget 中的信息
        self.overlay.setInfo(info)

        # 更新 LoadingIcon 的信息
        self.loading_icon.setInfo(info)

    # def closeEvent(self, event):
    #     # 关闭时从父窗口的预览列表中移除自己
    #     if self.parent():
    #         self.parent().remove_preview(self)
    #     event.accept()


class LoadingIcon(RotatingLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.info = "加载中..."
        self.setMouseTracking(True)
        # self.installEventFilter(self)

        # 创建 QMovie 对象
        self.movie = QMovie(resource_path("icons/loading.gif"))
        self.movie.setScaledSize(QSize(40, 40))
        self.setMovie(self.movie)

        self.installEventFilter(self)

    def setInfo(self, info):
        self.info = info

    def eventFilter(self, obj, event):
        if obj == self:
            if event.type() == QEvent.Enter:
                self.showTooltip()
                return True
            elif event.type() == QEvent.Leave:
                self.hideTooltip()
                return True
        return super().eventFilter(obj, event)

    def showTooltip(self):
        QToolTip.showText(self.mapToGlobal(QPoint(0, self.height())), self.info, self)

    def hideTooltip(self):
        QToolTip.hideText()


class OverlayWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setMouseTracking(True)

        self.info_button = QPushButton(self)
        self.info_button.setIcon(QIcon(resource_path("icons/info_icon.png")))  # 替换为实际的信息图标路径
        self.info_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 150);
                border: none;
                border-radius: 15px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 200);
            }
        """)
        self.info_button.setFixedSize(30, 30)
        self.info_button.setCursor(Qt.PointingHandCursor)
        self.info_button.installEventFilter(self)

        self.info = "加载中..."

    def setInfo(self, info):
        self.info = info

    def eventFilter(self, obj, event):
        if obj == self.info_button:
            if event.type() == QEvent.Enter:
                self.showTooltip()
                return True
            elif event.type() == QEvent.Leave:
                self.hideTooltip()
                return True
        return super().eventFilter(obj, event)

    def showTooltip(self):
        QToolTip.showText(self.info_button.mapToGlobal(QPoint(0, self.info_button.height())),
                          self.info, self.info_button)

    def hideTooltip(self):
        QToolTip.hideText()

    def updateInfoButtonPosition(self):
        x = int(self.width() * 0.9)  # 90% 从左边
        y = int(self.height() * 0.1)  # 10% 从上边
        self.info_button.move(x - self.info_button.width(), y)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 1))  # 几乎完全透明的背景


from PySide6.QtCore import QObject, Qt, QRect, QPoint, Signal, QTimer, QSize
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QPushButton,
                               QVBoxLayout, QHBoxLayout, QListWidget, QLabel,
                               QRubberBand, QDialog, QDialogButtonBox, QListWidgetItem,
                               QScrollArea, QMessageBox, QGridLayout, QToolTip)

import sys
import os
import time
import traceback


class GlobalEventFilter(QObject):
    def eventFilter(self, obj, event):
        try:
            return False  # 不处理事件，让它继续传播
        except Exception as e:
            print(f"Exception in event filter: {e}")
            traceback.print_exc()
            return False


if __name__ == "__main__":
    try:
        # if is_already_running():
        #     print("Application is already running.")
        #     sys.exit(0)
        #
        # pipe_handle = create_single_instance_pipe()

        sys.excepthook = global_exception_handler
        app = QApplication(sys.argv)
        global_event_filter = GlobalEventFilter()
        app.installEventFilter(global_event_filter)

        splash = SplashScreen()
        splash.show()

        global tool
        tool = ScreenshotTool()


        def show_main_window():
            splash.close()
            tool.show()


        QTimer.singleShot(500, show_main_window)

        app.aboutToQuit.connect(app.deleteLater)

        sys.exit(app.exec())

    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()
    # finally:
    #     if 'pipe_handle' in locals():
    #         win32file.CloseHandle(pipe_handle)
