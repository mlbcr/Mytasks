import sys
from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtGui import QFont, QColor
import datetime
import json
import os
import ctypes

DATA_FILE = "user.json"

CATEGORIAS = {
    "INTELIGÊNCIA": "#f1c40f",  
    "FORÇA": "#e74c3c",         
    "VITALIDADE": "#2ecc71",   
    "CRIATIVIDADE": "#3498db", 
    "SOCIAL": "#95a5a6"        
}

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

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

class EditMissionModal(QtWidgets.QWidget):
    accepted = QtCore.Signal(dict)
    rejected = QtCore.Signal()

    def __init__(self, mission_data, parent=None):
        super().__init__(parent)
        self.data = mission_data
        if parent:
            self.resize(parent.size())
        
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        self.bg_overlay = QtWidgets.QFrame()
        self.bg_overlay.setStyleSheet("background-color: rgba(0, 0, 0, 0.5); border: none;")
        self.main_layout.addWidget(self.bg_overlay)

        self.content_card = QtWidgets.QFrame(self.bg_overlay)
        self.content_card.setFixedWidth(400)

        card_layout = QtWidgets.QVBoxLayout(self.content_card)
        card_layout.setContentsMargins(30, 20, 30, 30)

        self.edit_titulo = QtWidgets.QLineEdit(self.data.get("titulo", "NOVA TAREFA"))
        self.edit_titulo.setAlignment(QtCore.Qt.AlignCenter) 
        self.edit_titulo.setObjectName("titulo_principal")
        self.edit_titulo.returnPressed.connect(self.submit)

        self.content_card.setStyleSheet("""
            QFrame { 
                background-color: #1b1430; 
                border: 2px solid #5E12F8; 
                border-radius: 20px; 
            }
            /* Estilo do Título Principal (O antigo "EDITAR TAREFA") */
            QLineEdit#titulo_principal {
                font-size: 18px;
                font-weight: bold;
                color: white;
                background: transparent;
                border: none;
                border-bottom: 1px solid rgba(94, 18, 248, 0.3);
                margin-bottom: 15px;
                padding: 5px;
            }
            QLineEdit#titulo_principal:focus {
                border-bottom: 2px solid #5E12F8;
            }
            
            QLabel { font-weight: bold; color: #5E12F8; margin-top: 10px; border: none; background: transparent; }
            QLineEdit, QTextEdit, QComboBox, QSpinBox, QDateEdit {
                background-color: #161025; color: white; border: 1px solid #3d2b63;
                border-radius: 5px; padding: 5px;
            }
            QPushButton#save { 
                background-color: #5E12F8; color: white; font-weight: bold; 
                border-radius: 10px; padding: 12px; margin-top: 10px;
            }
            QPushButton#cancel { 
                background-color: transparent; color: rgba(255,255,255,0.5); 
                border: 1px solid rgba(255,255,255,0.2); border-radius: 10px; padding: 8px;
            }
        """)
        card_layout.addWidget(self.edit_titulo)

        self.edit_desc = QtWidgets.QTextEdit(self.data.get("descricao") or "")
        self.edit_desc.setFixedHeight(60)
        card_layout.addWidget(QtWidgets.QLabel("DESCRIÇÃO"))
        card_layout.addWidget(self.edit_desc)

        h_layout = QtWidgets.QHBoxLayout()
        v1 = QtWidgets.QVBoxLayout()
        v1.addWidget(QtWidgets.QLabel("CATEGORIA"))
        self.edit_cat = QtWidgets.QComboBox()
        self.edit_cat.addItem("") 
        self.edit_cat.addItems([c for c in CATEGORIAS.keys() if c])


        categoria_atual = self.data.get("categoria")
        point = 1
        if categoria_atual in CATEGORIAS:
            self.edit_cat.setCurrentText(categoria_atual)

    
        v1.addWidget(self.edit_cat)
        v2 = QtWidgets.QVBoxLayout()
        v2.addWidget(QtWidgets.QLabel("XP"))
        self.edit_xp = QtWidgets.QSpinBox()
        self.edit_xp.setRange(0, 1000)
        self.edit_xp.setValue(self.data.get("xp", 10))
        v2.addWidget(self.edit_xp)
        h_layout.addLayout(v1)
        h_layout.addLayout(v2)
        card_layout.addLayout(h_layout)

        self.edit_prazo = QtWidgets.QDateEdit(calendarPopup=True)
        prazo_str = self.data.get("prazo")

        if prazo_str:
            self.edit_prazo.setDate(QtCore.QDate.fromString(prazo_str, "yyyy-MM-dd"))
        else:
            self.edit_prazo.setDate(QtCore.QDate.currentDate())

        card_layout.addWidget(QtWidgets.QLabel("PRAZO"))
        card_layout.addWidget(self.edit_prazo)

        self.btn_save = QtWidgets.QPushButton("SALVAR")
        self.btn_save.setObjectName("save")
        self.btn_save.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_save.clicked.connect(self.submit)
        
        self.btn_cancel = QtWidgets.QPushButton("CANCELAR")
        self.btn_cancel.setObjectName("cancel")
        self.btn_cancel.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_cancel.clicked.connect(self.close_modal)

        card_layout.addWidget(self.btn_save)
        card_layout.addWidget(self.btn_cancel)

        overlay_layout = QtWidgets.QGridLayout(self.bg_overlay)
        overlay_layout.addWidget(self.content_card, 0, 0, QtCore.Qt.AlignCenter)

    def submit(self):
        categoria = self.edit_cat.currentText()
        categoria = categoria.replace("+1 ", "").strip()

        new_data = {
            "titulo": self.edit_titulo.text(),
            "descricao": self.edit_desc.toPlainText(),
            "xp": self.edit_xp.value(),
            "categoria": categoria,
            "prazo": self.edit_prazo.date().toString("yyyy-MM-dd")
        }
        self.accepted.emit(new_data)
        self.close_modal()

    def close_modal(self):
        self.setParent(None)
        self.deleteLater()

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
        if not name: return
        save_name(name)
        self.main.stack.setCurrentIndex(1)
        self.main.resize(self.main.normal_size)
        self.main.center_on_screen()

class MissionCard(QtWidgets.QFrame):
    status_changed = QtCore.Signal(object)
    clicked = QtCore.Signal(object)

    def __init__(self, mission_id, titulo, status="Pendente", xp=10, descricao=None, categoria=None, prazo=None):
        super().__init__()
        self.mission_id = mission_id
        self.is_done = (status == "Concluída")
        self.setFixedHeight(85)
        self.categoria = categoria
        self.prazo = prazo

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 10)
        layout.setSpacing(15)

        self.btn_status = QtWidgets.QPushButton()
        self.btn_status.setFixedSize(22, 22)
        self.btn_status.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_status.clicked.connect(self.toggle_status)

        text_layout = QtWidgets.QVBoxLayout()
        text_layout.setSpacing(2)

        self.label_title = QtWidgets.QLabel(titulo)
        self.label_desc = QtWidgets.QLabel(descricao if descricao else "Adicionar descrição")
        self.label_title.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)
        self.label_desc.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)
        
        text_layout.addWidget(self.label_title)
        text_layout.addWidget(self.label_desc)

        self.cat_chip = None

        if self.categoria:
            cor = CATEGORIAS.get(self.categoria, "#777")
            points = 1
            self.cat_chip = QtWidgets.QLabel()
            self.cat_chip.setFixedHeight(18)
            self.cat_chip.setSizePolicy(
                QtWidgets.QSizePolicy.Fixed,
                QtWidgets.QSizePolicy.Fixed
            )

            text_layout.addWidget(self.cat_chip)
            self.update_categoria(self.categoria)

            self.cat_chip.setStyleSheet(f"""
                QLabel {{
                    background-color: {cor};
                    color: #0e0b1c;
                    padding: 0px 6px;
                    border-radius: 3px;
                    font-size: 10px;
                    font-weight: bold;
                    letter-spacing: 0.5px;
                }}
            """)


        right_layout = QtWidgets.QVBoxLayout()
        right_layout.setSpacing(4)
        right_layout.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

        self.xp_label = QtWidgets.QLabel(f"{xp} XP")
        self.xp_label.setAlignment(QtCore.Qt.AlignRight)
        self.xp_label.setStyleSheet("font-weight: bold; font-size: 18px;")

        self.label_prazo = QtWidgets.QLabel()
        self.label_prazo.setAlignment(QtCore.Qt.AlignRight)

        if self.prazo:
            prazo_date = QtCore.QDate.fromString(self.prazo, "yyyy-MM-dd")
            today = QtCore.QDate.currentDate()

            if prazo_date == today:
                self.label_prazo.setText("Hoje")
                self.label_prazo.setStyleSheet("""
                    font-weight: bold;
                    font-size: 12px;
                """)
            else:
                prazo_fmt = prazo_date.toString("dd/MM")
                self.label_prazo.setText(f"Até {prazo_fmt}")
                self.label_prazo.setStyleSheet("""
                    font-weight: bold;
                    font-size: 12px;
                    color: rgba(255,255,255,0.4);
                """)

        right_layout.addWidget(self.xp_label)
        right_layout.addWidget(self.label_prazo)

        layout.addWidget(self.btn_status)
        layout.addLayout(text_layout)
        layout.addStretch()
        layout.addLayout(right_layout)
        
        self.update_visuals()

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            if not self.btn_status.underMouse():
                self.clicked.emit(self)

    def update_categoria(self, categoria):
        self.categoria = categoria

        if not categoria:
            if self.cat_chip:
                self.cat_chip.hide()
            return

        if self.cat_chip is None:
            self.cat_chip = QtWidgets.QLabel()
            self.cat_chip.setFixedHeight(18)
            self.cat_chip.setSizePolicy(
                QtWidgets.QSizePolicy.Fixed,
                QtWidgets.QSizePolicy.Fixed
            )

            self.layout().itemAt(1).addWidget(self.cat_chip)

        cor = CATEGORIAS.get(categoria, "#777")
        points = 1

        self.cat_chip.setText(f"+{points} {categoria.upper()}")
        self.cat_chip.setStyleSheet(f"""
            QLabel {{
                background-color: {cor};
                color: #0e0b1c;
                padding: 0px 6px;
                border-radius: 3px;
                font-size: 10px;
                font-weight: bold;
                letter-spacing: 0.5px;
            }}
        """)
        self.cat_chip.show()

    def update_prazo(self, prazo):
        self.prazo = prazo

        if not prazo:
            self.label_prazo.clear()
            return

        prazo_date = QtCore.QDate.fromString(prazo, "yyyy-MM-dd")
        today = QtCore.QDate.currentDate()

        if prazo_date == today:
            self.label_prazo.setText("Hoje")
            self.label_prazo.setStyleSheet("""
                font-weight: bold;
                font-size: 12px;
            """)
        else:
            prazo_fmt = prazo_date.toString("dd/MM")
            self.label_prazo.setText(f"Até {prazo_fmt}")
            self.label_prazo.setStyleSheet("""
                font-weight: bold;
                font-size: 12px;
                color: rgba(255,255,255,0.4);
            """)


    def toggle_status(self):
        self.is_done = not self.is_done
        self.update_visuals()
        self.status_changed.emit(self)

    def update_visuals(self):
        common = "border: none; background: transparent;"
        if self.is_done:
            self.setStyleSheet("QFrame { background-color: rgba(94, 18, 248, 0.05); border-radius: 12px; border: 1px solid rgba(255,255,255,0.05); }")
            self.label_title.setStyleSheet(f"color: gray; font-size: 16px; font-weight: bold; text-decoration: line-through; {common}")
            self.label_desc.setStyleSheet(f"color: rgba(255,255,255,0.2); font-size: 11px; {common}")
            self.btn_status.setStyleSheet("background-color: #5E12F8; border: 2px solid #5E12F8; border-radius: 11px;")
            self.xp_label.setStyleSheet(f"color: rgba(255,255,255,0.2); {common}")
        else:
            self.setStyleSheet("QFrame { background-color: #1b1430; border-radius: 12px; border: 1px solid #2d234a; }")
            self.label_title.setStyleSheet(f"color: white; font-size: 16px; font-weight: bold; {common}")
            self.label_desc.setStyleSheet(f"color: rgba(255,255,255,0.5); font-size: 11px; {common}")
            
            self.btn_status.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: 2px solid white;
                    border-radius: 11px;
                }
                QPushButton:hover {
                    background-color: #340b85;
                    border: 2px solid white;
                }
            """)


            self.xp_label.setStyleSheet(f"color: #5E12F8; font-weight: bold; {common}")

class RotatableButton(QtWidgets.QPushButton):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self._rotation = 0

    def getRotation(self):
        return self._rotation

    def setRotation(self, value):
        self._rotation = value
        self.update()

    rotation = QtCore.Property(float, getRotation, setRotation)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        rect = self.rect()
        painter.translate(rect.center())
        painter.rotate(self._rotation)
        painter.translate(-rect.center())

        super().paintEvent(event)

class AppScreen(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(40, 40, 40, 40)
        self.layout.setSpacing(25)
        
        header_row = QtWidgets.QHBoxLayout()
        title_container = QtWidgets.QVBoxLayout()
        title = QtWidgets.QLabel("MISSÕES")
        title.setStyleSheet("font-size: 20px; font-weight: bold; letter-spacing: 1px; border: none;")
        underline = QtWidgets.QFrame()
        underline.setFixedHeight(4)
        underline.setFixedWidth(40)
        underline.setStyleSheet("background-color: #5E12F8; border-radius: 2px; border: none;")
        title_container.addWidget(title)
        title_container.addWidget(underline)
        
        self.btn_add_mission = RotatableButton("+")
        self.btn_add_mission.setFixedSize(50, 50)
        self.btn_add_mission.clicked.connect(self.toggle_add_button)
        self.btn_add_mission.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_add_mission.setStyleSheet("""
            QPushButton { 
                color: white; background-color: #5E12F8; border: none; 
                border-radius: 25px; font-size: 28px; padding-bottom: 4px;
            } 
            QPushButton:hover { background-color: #7a3cf9; }
        """)
        
        self.btn_add_mission_anim = QtCore.QPropertyAnimation(self.btn_add_mission, b"rotation", self)
        self.btn_add_mission_anim.setDuration(220)
        
        header_row.addLayout(title_container)
        header_row.addStretch()
        header_row.addWidget(self.btn_add_mission)
        self.layout.addLayout(header_row)
        
        self.mission_title_input = QtWidgets.QLineEdit()
        self.mission_title_input.setPlaceholderText("O que vamos realizar agora?")
        self.mission_title_input.setFixedHeight(45)
        self.mission_title_input.setStyleSheet("""
            QLineEdit { background-color: #1b1430; border: 1px solid #5E12F8; border-radius: 10px; padding: 0 15px; }
        """)
        self.mission_title_input.returnPressed.connect(self.confirm_create_mission)
        self.mission_title_input.hide()
        self.layout.addWidget(self.mission_title_input)
        
        self.missions_container = QtWidgets.QVBoxLayout()
        self.missions_container.setSpacing(10)
        self.missions_container.setAlignment(QtCore.Qt.AlignTop)
        
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        scroll_content = QtWidgets.QWidget()
        scroll_content.setLayout(self.missions_container)
        scroll.setWidget(scroll_content)
        
        self.layout.addWidget(scroll)
        self.load_missions()

    def get_rotation(self): return self.btn_add_mission._rotation
    def set_rotation(self, value):
        self.btn_add_mission._rotation = value
        self.btn_add_mission.setStyleSheet(f"QPushButton {{ color: white; background-color: #5E12F8; border: none; border-radius: 25px; font-size: 28px; transform: rotate({value}deg); }}")
    rotation = QtCore.Property(float, get_rotation, set_rotation)

    def add_mission_to_ui(self, m_id, title, status, xp=10, desc=None, categoria=None, prazo=None):
        card = MissionCard(m_id, title, status, xp, desc, categoria, prazo)
        card.status_changed.connect(self.on_mission_status_changed)
        card.clicked.connect(self.open_edit_mission)
        if status == "Concluída":
            self.missions_container.addWidget(card)
        else:
            self.missions_container.insertWidget(0, card)

    def open_edit_mission(self, card):
        MISSIONS_DATA = "missions.json"
        with open(MISSIONS_DATA, "r", encoding="utf-8") as f:
            data = json.load(f)
        idx = next(i for i, m in enumerate(data["missions"]) if m["id"] == card.mission_id)
        self.modal = EditMissionModal(data["missions"][idx], self)
        self.modal.accepted.connect(lambda nv: self.save_edit(card, idx, nv))
        self.modal.show()

    def save_edit(self, card, idx, nv):
        MISSIONS_DATA = "missions.json"
        with open(MISSIONS_DATA, "r", encoding="utf-8") as f:
            data = json.load(f)
        data["missions"][idx].update(nv)
        with open(MISSIONS_DATA, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        card.label_title.setText(nv["titulo"])
        card.label_desc.setText(nv["descricao"] if nv["descricao"] else "Adicionar descrição")
        card.xp_label.setText(f"{nv['xp']} xp")
        
        card.update_categoria(nv.get("categoria"))
        card.update_prazo(nv.get("prazo"))
        
        card.update_visuals()

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
        if card.is_done: self.missions_container.addWidget(card)
        else: self.missions_container.insertWidget(0, card)

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
            with open(MISSIONS_DATA, "r", encoding="utf-8") as f: data = json.load(f)
        new_id = max([m["id"] for m in data["missions"]] + [0]) + 1
        today = datetime.date.today().isoformat()
        new_m = {
            "id": new_id,
            "titulo": title,
            "status": "Pendente",
            "xp": 10, 
            "prazo": today,
            "data_criacao": today
            }
        data["missions"].append(new_m)
        with open(MISSIONS_DATA, "w", encoding="utf-8") as f: json.dump(data, f, indent=2, ensure_ascii=False)
        self.add_mission_to_ui(
            new_id,
            title,
            "Pendente",
            xp=10,
            prazo=today
        )

        self.mission_title_input.clear(); self.mission_title_input.hide(); self.toggle_add_button()

    def load_missions(self):
        MISSIONS_DATA = "missions.json"
        if not os.path.exists(MISSIONS_DATA): return
        with open(MISSIONS_DATA, "r", encoding="utf-8") as f: data = json.load(f)
        for m in sorted(data.get("missions", []), key=lambda x: x["status"] == "Concluída"):
            self.add_mission_to_ui(
                m["id"],
                m["titulo"],
                m["status"],
                m.get("xp", 10),
                m.get("descricao"),
                m.get("categoria"),
                m.get("prazo")
            )

if __name__ == "__main__":
    try: ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("my.task.app.v1")
    except: pass
    app = QtWidgets.QApplication(sys.argv)

    app_icon = QtGui.QIcon(resource_path("icone.ico"))
    app.setWindowIcon(app_icon)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())