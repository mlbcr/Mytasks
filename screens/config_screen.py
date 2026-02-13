from PySide6 import QtCore, QtWidgets
import datetime
from widgets.custom_button import RotatableButton
from widgets.note_card import NoteCard
from data_manager import load_notes, save_notes


class ConfigScreen(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(40, 40, 40, 40)
        self.layout.setSpacing(25)

        header_widget = QtWidgets.QWidget()
        header_layout = QtWidgets.QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)

        title_container = QtWidgets.QVBoxLayout()
        title_container.setSpacing(5)

        title = QtWidgets.QLabel("CONFIGURAÇÕES")
        title.setStyleSheet("font-size: 20px; font-weight: bold; letter-spacing: 1px; color: white;")

        underline = QtWidgets.QFrame()
        underline.setFixedHeight(4)
        underline.setFixedWidth(40)
        underline.setStyleSheet("background-color: #5E12F8; border-radius: 2px; border: none;")

        title_container.addWidget(title)
        title_container.addWidget(underline)

        header_layout.addLayout(title_container)
        header_layout.addStretch()

        self.layout.addWidget(header_widget)