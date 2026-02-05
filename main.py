import sys
from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtGui import QFont
import datetime
import json
import os

DATA_FILE = "user.json"
id = 0

def load_name():
    if not os.path.exists(DATA_FILE):
        return None

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data.get("usuario", {}).get("nome")

def save_name(nome):
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {"usuario": {}}

    data.setdefault("usuario", {})
    data["usuario"]["nome"] = nome

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.setStyleSheet("""
            QWidget {
                background-color: #12002b;
                color: white;
                font-family: Segoe UI;
            }

            QStackedWidget {
                background: transparent;
            }
        """)

        self.setWindowTitle("My Tasks")
        self.small_size = QtCore.QSize(400, 250)
        self.normal_size = QtCore.QSize(800, 800)

        self.resize(self.small_size)

        self.stack = QtWidgets.QStackedWidget()

        self.screen_name = NameScreen(self)
        self.screen_app = AppScreen()

        self.stack.addWidget(self.screen_name)
        self.stack.addWidget(self.screen_app)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.stack)

        nome = load_name()

        if nome:
            self.stack.setCurrentIndex(1)
            self.resize(self.normal_size)
        else:
            self.stack.setCurrentIndex(0)
            self.resize(self.small_size)

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

        self.setStyleSheet("""
            QWidget {
                background-color: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #12002b,
                    stop:1 #1e003f
                );
            }

            QLabel {
                color: white;
                font-size: 14px;
            }

            QLineEdit {
                background-color: #6f5cc2;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px;
                font-size: 14px;
            }

            QLineEdit::placeholder {
                color: #dcd6ff;
            }

            QPushButton {
                color: white;
                border: 1px solid white;
                border-radius: 15px;
                padding: 6px 20px;
                background: transparent;
            }

            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
        """)

        title = QtWidgets.QLabel("Como deseja se chamar?")
        title.setAlignment(QtCore.Qt.AlignCenter)

        self.input = QtWidgets.QLineEdit()
        self.input.setFixedHeight(32)
        self.input.setAlignment(QtCore.Qt.AlignCenter)

        btn = QtWidgets.QPushButton("OK")
        btn.setFixedWidth(60)
        btn.clicked.connect(self.go_next)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(80, 60, 80, 60)
        layout.setAlignment(QtCore.Qt.AlignCenter)

        layout.addWidget(title)
        layout.addWidget(self.input)
        layout.addWidget(btn, alignment=QtCore.Qt.AlignCenter)

    def go_next(self):
        name = self.input.text().strip()
        if not name:
            return

        save_name(name)
        self.main.stack.setCurrentIndex(1)
        self.main.resize(self.main.normal_size)
        self.main.center_on_screen()

class MissionCard(QtWidgets.QFrame):
    def __init__(self, titulo, xp=2, cor="#2b0b3f"):
        super().__init__()

        self.setFixedHeight(70)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {cor};
                border-radius: 14px;
            }}               
        """ )

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(16, 10, 16, 10)
        layout.setSpacing(12)

        self.btn_status = QtWidgets.QPushButton()
        self.btn_status.setFixedSize(18, 18)
        self.btn_status.setCursor(QtCore.Qt.PointingHandCursor)

        self.btn_status.setStyleSheet("""
            QPushButton {
                background-color: white;
                border: 2px solid white;
                border-radius: 9px;
            }
            QPushButton:hover {
                background-color: rgba(255,255,255,0.1);
            }
        """)
        self.btn_status.clicked.connect(self.toggle_status)

        text_layout = QtWidgets.QVBoxLayout()
        text_layout.setSpacing(2)

        title = QtWidgets.QLabel(titulo)
        title.setStyleSheet("color: white; font-weight: bold;")

        desc = QtWidgets.QLabel("Adicionar descrição")
        desc.setStyleSheet("color: rgba(255,255,255,0.6); font-size: 11px;")

        text_layout.addWidget(title)
        text_layout.addWidget(desc)

        xp_label = QtWidgets.QLabel(f"{xp} xp")
        xp_label.setStyleSheet("color: white; font-weight: bold;")

        layout.addWidget(self.btn_status)
        layout.addLayout(text_layout)
        layout.addStretch()
        layout.addWidget(xp_label)
    
    def toggle_status(self):
        self.btn_status.setStyleSheet("""
            QPushButton {
                background-color: black;      /* cor do miolo */
                border: 2px solid white;      /* borda branca */
                border-radius: 9px;
                padding: 2px;                 /* cria o “vazio” visual */
            }
        """)

class AppScreen(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        nome = load_name() or "aventureiro"
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(20)

        header = QtWidgets.QHBoxLayout()

        title = QtWidgets.QLabel("MISSÕES")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))

        self.btn_add_mission = QtWidgets.QPushButton("+")
        self.btn_add_mission.setFixedSize(80, 60)
        self.btn_add_mission.clicked.connect(self.create_mission)
        self.mission_title_input = QtWidgets.QLineEdit()
        self.mission_title_input.setPlaceholderText("Digite o nome da missão e pressione Enter")
        self.mission_title_input.returnPressed.connect(self.confirm_create_mission)
        self.mission_title_input.hide()

        self.btn_add_mission.setStyleSheet(
            """
            QPushButton {
                color: white;
                border: 1px solid white;
                border-radius: 20px;
                padding: 6px 20px;
                font-size: 24px; 
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
            """
        )

        self.mission_title_input.setStyleSheet("""
            QLineEdit {
                background-color: #1e003f;
                border: 1px solid #6f5cc2;
                border-radius: 10px;
                padding: 10px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #9d8cff;
            }
        """)


        header.addWidget(title)
        header.addStretch()
        header.addWidget(self.btn_add_mission)

        layout.addLayout(header)
        layout.addWidget(self.mission_title_input)

        self.missions_container = QtWidgets.QVBoxLayout()
        self.missions_container.setSpacing(12)

        self.load_missions()

        layout.addLayout(self.missions_container)
        layout.addStretch()

    def add_mission(self, titulo):
        card = MissionCard(titulo)
        self.missions_container.addWidget(card)

    def create_mission(self):
        if self.mission_title_input.isVisible():
            self.mission_title_input.hide()
        else:
            self.mission_title_input.clear()
            self.mission_title_input.show()
            self.mission_title_input.setFocus()
        self.mission_title_input.setFocus()

    def confirm_create_mission(self):
        title = self.mission_title_input.text()
        if not title:
            return

        MISSIONS_DATA = "missions.json"

        if os.path.exists(MISSIONS_DATA):
            with open(MISSIONS_DATA, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = {"missions": []}

        if data["missions"]:
            new_id = max(m["id"] for m in data["missions"]) + 1
        else:
            new_id = 1

        mission = {
            "id": new_id,
            "titulo": title,
            "descricao": None,
            "status": "Pendente",
            "data_criacao": datetime.date.today().isoformat()
        }

        data["missions"].append(mission)
        self.add_mission(title)

        with open(MISSIONS_DATA, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        self.mission_title_input.clear()
        self.mission_title_input.hide()
    
    def load_missions(self):
        MISSIONS_DATA = "missions.json"

        if not os.path.exists(MISSIONS_DATA):
            return

        with open(MISSIONS_DATA, "r", encoding="utf-8") as f:
            data = json.load(f)

        for mission in data.get("missions", []):
            self.add_mission(mission["titulo"])


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

