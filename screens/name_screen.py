from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtGui import QFont, QColor
from data_manager import save_name 


class NameScreen(QtWidgets.QWidget):
    def __init__(self, main):
        super().__init__()
        self.main = main
        self.setStyleSheet("""
            QWidget { background-color: #161025; }
            QLabel { color: white; font-size: 14px; border: none; }
            QLineEdit {
                background-color: #1b1430; color: white; border: 1px solid #5E12F8;
                border-radius: 8px; padding: 10px; font-size: 14px;
            }
            QPushButton {
                color: white; border: 1px solid white; border-radius: 15px;
                padding: 8px 25px; background: transparent; font-weight: bold;
            }
            QPushButton:hover { background-color: rgba(94, 18, 248, 0.4); border-color: #5E12F8; }
        """)
        title = QtWidgets.QLabel("Como deseja se chamar?")
        title.setAlignment(QtCore.Qt.AlignCenter)
        self.input = QtWidgets.QLineEdit()
        self.input.setFixedHeight(40)
        self.input.setAlignment(QtCore.Qt.AlignCenter)
        btn = QtWidgets.QPushButton("COMEÇAR")
        btn.setCursor(QtCore.Qt.PointingHandCursor)
        btn.clicked.connect(self.go_next)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(60, 40, 60, 40)
        layout.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(title)
        layout.addWidget(self.input)
        layout.addWidget(btn, alignment=QtCore.Qt.AlignCenter)

    def go_next(self):
        name = self.input.text().strip()
        if not name:
            return

        save_name(name)

        self.main.menu.show()    
        self.main.stack.setCurrentIndex(1)
        self.main.resize(self.main.normal_size)