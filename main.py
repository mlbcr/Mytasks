import sys
from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtGui import QFont, QColor
import datetime
import json
import os
import ctypes

DATA_FILE = "user.json"

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
                background-color: #161025;
                color: white;
                font-family: 'Segoe UI', sans-serif;
            }
            QStackedWidget {
                background: transparent;
            }
        """)
        self.setWindowTitle("MyTasks")
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
                background-color: #161025;
            }
            QLabel { color: white; font-size: 14px; border: none; }
            QLineEdit {
                background-color: #1b1430;
                color: white;
                border: 1px solid #5E12F8;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
            }
            QPushButton {
                color: white;
                border: 1px solid white;
                border-radius: 15px;
                padding: 8px 25px;
                background: transparent;
                font-weight: bold;
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
        if not name: return
        save_name(name)
        self.main.stack.setCurrentIndex(1)
        self.main.resize(self.main.normal_size)
        self.main.center_on_screen()

class MissionCard(QtWidgets.QFrame):
    status_changed = QtCore.Signal(object)

    def __init__(self, mission_id, titulo, status="Pendente", xp=2):
        super().__init__()
        self.mission_id = mission_id
        self.is_done = (status == "Concluída")
        self.setFixedHeight(75)
        
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 10)
        layout.setSpacing(15)

        self.btn_status = QtWidgets.QPushButton()
        self.btn_status.setFixedSize(20, 20)
        self.btn_status.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_status.clicked.connect(self.toggle_status)

        text_layout = QtWidgets.QVBoxLayout()
        text_layout.setSpacing(2)
        self.label_title = QtWidgets.QLabel(titulo)
        self.label_desc = QtWidgets.QLabel("Adicionar descrição")
        
        text_layout.addWidget(self.label_title)
        text_layout.addWidget(self.label_desc)

        self.xp_label = QtWidgets.QLabel(f"{xp} xp")
        self.xp_label.setFixedWidth(50)
        self.xp_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

        layout.addWidget(self.btn_status)
        layout.addLayout(text_layout)
        layout.addStretch()
        layout.addWidget(self.xp_label)
        
        self.update_visuals()

    def toggle_status(self):
        self.is_done = not self.is_done
        self.update_visuals()
        self.status_changed.emit(self)

    def update_visuals(self):
        common_label_style = "border: none; background: transparent;"
        
        if self.is_done:
            self.setStyleSheet("""
                QFrame { background-color: rgba(94, 18, 248, 0.08); border-radius: 12px; border: 1px solid rgba(94, 18, 248, 0.2); }
                QFrame:hover { background-color: rgba(94, 18, 248, 0.12); }
            """)
            self.btn_status.setStyleSheet("""
                QPushButton { background-color: #5E12F8; border: 2px solid #5E12F8; border-radius: 10px; }
                QPushButton:hover { background-color: #4a0ec4; }
            """)
            self.label_title.setStyleSheet(f"color: rgba(255,255,255,0.3); font-size: 17px; font-weight: bold; text-decoration: line-through; {common_label_style}")
            self.label_desc.setStyleSheet(f"color: rgba(255,255,255,0.2); font-size: 11px; {common_label_style}")
            self.xp_label.setStyleSheet(f"color: rgba(94, 18, 248, 0.4); font-weight: bold; {common_label_style}")
        else:
            self.setStyleSheet("""
                QFrame { background-color: #1b1430; border-radius: 12px; border: 1px solid transparent; }
                QFrame:hover { background-color: #221a3b; border: 1px solid #5E12F8; }
            """)
            self.btn_status.setStyleSheet("""
                QPushButton { background-color: transparent; border: 2px solid white; border-radius: 10px; }
                QPushButton:hover { border-color: #5E12F8; background-color: rgba(94, 18, 248, 0.1); }
            """)
            self.label_title.setStyleSheet(f"color: white; font-size: 17px; font-weight: bold; {common_label_style}")
            self.label_desc.setStyleSheet(f"color: rgba(255,255,255,0.5); font-size: 11px; {common_label_style}")
            self.xp_label.setStyleSheet(f"color: #5E12F8; font-weight: bold; {common_label_style}")

class AppScreen(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(25)
        
        header_row = QtWidgets.QHBoxLayout()
        
        title_container = QtWidgets.QVBoxLayout()
        title_container.setSpacing(5)
        title = QtWidgets.QLabel("MISSÕES")
        title.setStyleSheet("font-size: 20px; font-weight: bold; letter-spacing: 1px; border: none;")
        
        underline = QtWidgets.QFrame()
        underline.setFixedHeight(4)
        underline.setFixedWidth(40)
        underline.setStyleSheet("background-color: #5E12F8; border-radius: 2px; border: none;")
        
        title_container.addWidget(title)
        title_container.addWidget(underline)
        
        self.btn_add_mission = QtWidgets.QPushButton("+")
        self.btn_add_mission.setFixedSize(50, 50)
        self.btn_add_mission.clicked.connect(self.toggle_add_button)
        self.btn_add_mission.setCursor(QtCore.Qt.PointingHandCursor)
        
        self.btn_add_mission._rotation = 0

        self.btn_add_mission.setStyleSheet("""
            QPushButton { 
                color: white; 
                background-color: #5E12F8; 
                border: none; 
                border-radius: 25px; 
                font-size: 28px; 
                padding-bottom: 4px;
            } 
            QPushButton:hover { background-color: #7a3cf9; }
            QPushButton:pressed { background-color: #4a0ec4; }
        """)
        
        self.btn_add_mission_anim = QtCore.QPropertyAnimation(
            self.btn_add_mission, b"rotation", self
        )
        self.btn_add_mission_anim.setDuration(220)
        self.btn_add_mission_anim.setEasingCurve(QtCore.QEasingCurve.OutCubic)

        header_row.addLayout(title_container)
        header_row.addStretch()
        header_row.addWidget(self.btn_add_mission)
        layout.addLayout(header_row)
        
        self.mission_title_input = QtWidgets.QLineEdit()
        self.mission_title_input.setPlaceholderText("O que vamos realizar agora?")
        self.mission_title_input.setFixedHeight(45)
        self.mission_title_input.setStyleSheet("""
            QLineEdit { 
                background-color: #1b1430; 
                border: 1px solid #5E12F8; 
                border-radius: 10px; 
                padding: 0 15px;
                font-size: 14px;
            }
        """)
        self.mission_title_input.returnPressed.connect(self.confirm_create_mission)
        self.mission_title_input.hide()
        layout.addWidget(self.mission_title_input)
        
        self.missions_container = QtWidgets.QVBoxLayout()
        self.missions_container.setSpacing(10)
        self.missions_container.setAlignment(QtCore.Qt.AlignTop)
        
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        scroll_content = QtWidgets.QWidget()
        scroll_content.setLayout(self.missions_container)
        scroll.setWidget(scroll_content)
        
        layout.addWidget(scroll)
        self.load_missions()

    def get_rotation(self):
        return self.btn_add_mission._rotation

    def set_rotation(self, value):
        self.btn_add_mission._rotation = value
        self.btn_add_mission.setStyleSheet(
            f"""
            QPushButton {{
                color: white;
                background-color: #5E12F8;
                border: none;
                border-radius: 25px;
                font-size: 28px;
                transform: rotate({value}deg);
            }}
            """
        )

    rotation = QtCore.Property(float, get_rotation, set_rotation)


    def add_mission_to_ui(self, m_id, title, status):
        card = MissionCard(m_id, title, status)
        card.status_changed.connect(self.on_mission_status_changed)
        if status == "Concluída":
            self.missions_container.addWidget(card)
        else:
            self.missions_container.insertWidget(0, card)

    def on_mission_status_changed(self, card):
        MISSIONS_DATA = "missions.json"
        if os.path.exists(MISSIONS_DATA):
            with open(MISSIONS_DATA, "r", encoding="utf-8") as f:
                data = json.load(f)
            for m in data["missions"]:
                if m["id"] == card.mission_id:
                    m["status"] = "Concluída" if card.is_done else "Pendente"
                    break
            with open(MISSIONS_DATA, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        
        self.missions_container.removeWidget(card)
        if card.is_done:
            self.missions_container.addWidget(card)
        else:
            self.missions_container.insertWidget(0, card)

    def toggle_add_button(self):
        is_open = self.mission_title_input.isVisible()

        if is_open:
            self.mission_title_input.hide()
            self.btn_add_mission.setText("+")
            self.btn_add_mission_anim.setStartValue(45)
            self.btn_add_mission_anim.setEndValue(0)
        else:
            self.mission_title_input.show()
            self.mission_title_input.setFocus()
            self.btn_add_mission.setText("×")
            self.btn_add_mission_anim.setStartValue(0)
            self.btn_add_mission_anim.setEndValue(45)

        self.btn_add_mission_anim.start()


    def confirm_create_mission(self):
        title = self.mission_title_input.text().strip()
        if not title: return
        MISSIONS_DATA = "missions.json"
        data = {"missions": []}
        if os.path.exists(MISSIONS_DATA):
            with open(MISSIONS_DATA, "r", encoding="utf-8") as f:
                data = json.load(f)
        new_id = max([m["id"] for m in data["missions"]] + [0]) + 1
        new_mission = {"id": new_id, "titulo": title, "status": "Pendente", "data_criacao": datetime.date.today().isoformat()}
        data["missions"].append(new_mission)
        with open(MISSIONS_DATA, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        self.add_mission_to_ui(new_id, title, "Pendente")
        self.mission_title_input.clear()
        self.mission_title_input.hide()

    def load_missions(self):
        MISSIONS_DATA = "missions.json"
        if not os.path.exists(MISSIONS_DATA): return
        with open(MISSIONS_DATA, "r", encoding="utf-8") as f:
            data = json.load(f)
        for m in sorted(data.get("missions", []), key=lambda x: x["status"] == "Concluída"):
            self.add_mission_to_ui(m["id"], m["titulo"], m["status"])

if __name__ == "__main__":
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("my.task.app.v1")
    except: pass
    app = QtWidgets.QApplication(sys.argv)
    
    icon = QtGui.QIcon("icone.png")
    app.setWindowIcon(icon)
    window = MainWindow()
    
    window.show()
    sys.exit(app.exec())