import sys
import ctypes
from PySide6 import QtCore, QtWidgets, QtGui
from data_manager import load_name, resource_path
from screens.mission_screen import MissionScreen
from screens.focus_screen import FocusScreen

class SideMenu(QtWidgets.QFrame):
    clicked = QtCore.Signal(int)
    def __init__(self):
        super().__init__()
        self.setFixedWidth(200)
        self.setStyleSheet("background-color: #0e0b1c; border-right: 1px solid #2d234a;")
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(10, 40, 10, 20)
        logo = QtWidgets.QLabel("MyTasks")
        logo.setStyleSheet("font-size: 18px; font-weight: bold; color: #5E12F8; margin-bottom: 40px;")
        layout.addWidget(logo, alignment=QtCore.Qt.AlignCenter)
        btns = [("Início", 0), ("Missões", 1), ("Foco", 2), ("Config", 3)]
        for t, i in btns:
            b = QtWidgets.QPushButton(t)
            b.setFixedHeight(45)
            b.setCursor(QtCore.Qt.PointingHandCursor)
            b.setStyleSheet("QPushButton { text-align: left; padding-left: 15px; background: transparent; border: none; color: #a0a0a0; } QPushButton:hover { color: white; background: #1b1430; border-radius: 8px; }")
            b.clicked.connect(lambda _, x=i: self.clicked.emit(x))
            layout.addWidget(b)
        layout.addStretch()

class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MyTasks")
        self.resize(1100, 850)
        self.setStyleSheet("background-color: #161025; color: white; font-family: 'Segoe UI';")
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.menu = SideMenu()
        self.menu.clicked.connect(self.change)
        layout.addWidget(self.menu)
        self.stack = QtWidgets.QStackedWidget()
        self.stack.addWidget(QtWidgets.QLabel("Início"))
        self.stack.addWidget(MissionScreen())
        self.stack.addWidget(FocusScreen())
        layout.addWidget(self.stack)
        self.stack.setCurrentIndex(1)

    def change(self, i):
        if i < self.stack.count(): self.stack.setCurrentIndex(i)

if __name__ == "__main__":
    try: ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("mytasks.app")
    except: pass
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())