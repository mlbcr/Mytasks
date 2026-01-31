import sys
from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtGui import QFont

class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("My Tasks")
        self.small_size = QtCore.QSize(400, 250)
        self.normal_size = QtCore.QSize(800, 800)

        self.resize(self.small_size)

        self.stack = QtWidgets.QStackedWidget()

        self.screen_name = NameScreen(self)
        self.screen_app = AppScreen()

        self.stack.addWidget(self.screen_name)  # index 0
        self.stack.addWidget(self.screen_app)   # index 1

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.stack)
        self.center_on_screen()

    def center_on_screen(self):
        screen = QtGui.QGuiApplication.primaryScreen().availableGeometry()
        window_geometry = self.frameGeometry()
        window_geometry.moveCenter(screen.center())
        self.move(window_geometry.topLeft())

class NameScreen(QtWidgets.QWidget):
    def __init__(self, main):
        super().__init__()
        self.main = main

        title = QtWidgets.QLabel("Como devemos te chamar?")
        title.setAlignment(QtCore.Qt.AlignCenter)

        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        title.setFont(font)

        self.input = QtWidgets.QLineEdit()
        self.input.setPlaceholderText("Nome")

        btn = QtWidgets.QPushButton("OK")
        btn.clicked.connect(self.go_next)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(60, 60, 60, 60)

        layout.addWidget(title)
        layout.addWidget(self.input)
        layout.addWidget(btn)

    def go_next(self):
        name = self.input.text().strip()
        if not name:
            return

        print("Nome:", name)

        self.main.stack.setCurrentIndex(1)

        self.main.resize(self.main.normal_size)
        self.main.center_on_screen()

class AppScreen(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        label = QtWidgets.QLabel("Tela principal")
        label.setAlignment(QtCore.Qt.AlignCenter)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(label)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

