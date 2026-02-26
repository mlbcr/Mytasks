from PySide6 import QtCore, QtWidgets, QtGui
from data_manager import load_config, save_config


class ColorPicker(QtWidgets.QFrame):
    color_selected = QtCore.Signal(str)

    COLORS = [
        "#5E12F8", "#FF4C4C", "#32D583", "#FF9F43",
        "#2D9CDB", "#E056FD", "#00C2A8", "#F368E0"
    ]

    def __init__(self, parent=None):
        super().__init__(parent, QtCore.Qt.Popup)
        self.setStyleSheet("""
            QFrame {
                background:#1b1430;
                border:1px solid #322f50;
                border-radius:10px;
            }
        """)

        layout = QtWidgets.QGridLayout(self)
        layout.setContentsMargins(10,10,10,10)
        layout.setSpacing(8)

        for i, color in enumerate(self.COLORS):
            btn = QtWidgets.QPushButton()
            btn.setFixedSize(28,28)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background:{color};
                    border-radius:14px;
                    border:2px solid #322f50;
                }}
                QPushButton:hover {{
                    border:2px solid white;
                }}
            """)
            btn.clicked.connect(lambda _, c=color: self.pick(c))
            layout.addWidget(btn, i//4, i%4)

    def pick(self, color):
        self.color_selected.emit(color)
        self.close()


class ConfigScreen(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = load_config()
        self.new_color = "#5E12F8"
        self.setup_ui()

    def setup_ui(self):
        self.setStyleSheet("background:#141022;")

        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(40,40,40,40)
        self.main_layout.setSpacing(25)

        title = QtWidgets.QLabel("CONFIGURAÇÕES")
        title.setStyleSheet("font-size:20px;font-weight:bold;color:white;")
        self.main_layout.addWidget(title)

        self.scroll = QtWidgets.QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QtWidgets.QFrame.NoFrame)

        self.scroll_content = QtWidgets.QWidget()
        self.categories_container = QtWidgets.QVBoxLayout(self.scroll_content)
        self.categories_container.setSpacing(12)
        self.categories_container.setAlignment(QtCore.Qt.AlignTop)

        self.scroll.setWidget(self.scroll_content)
        self.main_layout.addWidget(self.scroll)

        input_card = QtWidgets.QFrame()
        input_card.setStyleSheet("""
            QFrame {
                background:#1b1430;
                border:1px solid #322f50;
                border-radius:12px;
            }
            QFrame:focus-within {
                border:1px solid #5E12F8;
            }
        """)
        card_layout = QtWidgets.QHBoxLayout(input_card)
        card_layout.setContentsMargins(14,8,8,8)

        self.line_edit = QtWidgets.QLineEdit()
        self.line_edit.setPlaceholderText("Nova categoria…")
        self.line_edit.setStyleSheet("""
            QLineEdit {
                background:transparent;
                border:none;
                color:white;
                font-size:14px;
            }
        """)
        self.line_edit.returnPressed.connect(self.process_new_category)

        self.color_btn = QtWidgets.QPushButton()
        self.color_btn.setFixedSize(26,26)
        self.color_btn.setCursor(QtCore.Qt.PointingHandCursor)
        self.update_color_btn()
        self.color_btn.clicked.connect(self.open_color_picker)

        add_btn = QtWidgets.QPushButton("Adicionar")
        add_btn.setCursor(QtCore.Qt.PointingHandCursor)
        add_btn.setStyleSheet("""
            QPushButton {
                background:#5E12F8;
                color:white;
                border:none;
                border-radius:8px;
                padding:6px 14px;
                font-weight:bold;
            }
            QPushButton:hover {
                background:#6d28ff;
            }
        """)
        add_btn.clicked.connect(self.process_new_category)

        card_layout.addWidget(self.line_edit)
        card_layout.addWidget(self.color_btn)
        card_layout.addWidget(add_btn)

        self.main_layout.addWidget(input_card)

        self.load_categories()

    # ---------- helpers ----------
    def update_color_btn(self):
        self.color_btn.setStyleSheet(f"""
            QPushButton {{
                background:{self.new_color};
                border-radius:13px;
                border:2px solid #322f50;
            }}
        """)

    def open_color_picker(self):
        picker = ColorPicker(self)
        picker.color_selected.connect(self.set_new_color)
        pos = self.color_btn.mapToGlobal(QtCore.QPoint(0, self.color_btn.height()))
        picker.move(pos)
        picker.show()

    def set_new_color(self, color):
        self.new_color = color
        self.update_color_btn()

    # ---------- categorias ----------
    def load_categories(self):
        while self.categories_container.count():
            item = self.categories_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for key, cat in self.config.get("categorias", {}).items():
            self.categories_container.addWidget(self.create_category_card(key, cat))

    def create_category_card(self, key, cat):
        color = cat.get("cor", "#5E12F8")

        card = QtWidgets.QFrame()
        card.setObjectName("CategoryCard")
        card.setFixedHeight(56)
        card.setStyleSheet("""
            QFrame#CategoryCard {
                border-radius:12px;
                border:1px solid #322f50;
            }
            QFrame#CategoryCard:hover {
                border:1px solid #5E12F8;
            }
        """)

        layout = QtWidgets.QHBoxLayout(card)
        layout.setContentsMargins(15,0,12,0)

        dot = QtWidgets.QPushButton()
        dot.setFixedSize(16,16)
        dot.setCursor(QtCore.Qt.PointingHandCursor)
        dot.setStyleSheet(f"""
            QPushButton {{
                background:{color};
                border-radius:8px;
                border:2px solid #322f50;
            }}
        """)
        dot.clicked.connect(lambda _, k=key: self.change_color(k, dot))

        label = QtWidgets.QLabel(cat.get("nome", key))
        label.setStyleSheet("color:white;font-weight:bold;")

        remove_btn = QtWidgets.QPushButton("Remover")
        remove_btn.setCursor(QtCore.Qt.PointingHandCursor)
        remove_btn.setStyleSheet("color:#ff6b6b;border:none;")
        remove_btn.clicked.connect(lambda _, k=key: self.remove_category(k))

        layout.addWidget(dot)
        layout.addWidget(label)
        layout.addStretch()
        layout.addWidget(remove_btn)

        return card

    # ---------- ações ----------
    def process_new_category(self):
        text = self.line_edit.text().strip()
        if not text:
            return

        key = text.lower().replace(" ", "_")

        self.config["categorias"][key] = {
            "nome": text,
            "cor": self.new_color,
            "pontos": 0,
            "ativa": True
        }

        save_config(self.config)
        self.load_categories()
        self.line_edit.clear()

    def remove_category(self, key):
        if key in self.config["categorias"]:
            del self.config["categorias"][key]
            save_config(self.config)
            self.load_categories()

    def change_color(self, key, btn):
        picker = ColorPicker(self)
        picker.color_selected.connect(lambda c: self.apply_color(key, c))
        pos = btn.mapToGlobal(QtCore.QPoint(0, btn.height()))
        picker.move(pos)
        picker.show()

    def apply_color(self, key, color):
        self.config["categorias"][key]["cor"] = color
        save_config(self.config)
        self.load_categories()