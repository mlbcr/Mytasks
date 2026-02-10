from PySide6 import QtCore, QtWidgets, QtGui
import datetime
from data_manager import load_missions, save_missions_to_file
from widgets.mission_card import MissionCard
from widgets.edit_modal import EditMissionModal
from widgets.custom_button import RotatableButton

def end_of_day():
    return datetime.date.today()

def end_of_week():
    today = datetime.date.today()
    return today + datetime.timedelta(days=(6 - today.weekday()))
    # segunda=0, domingo=6

def end_of_month():
    today = datetime.date.today()
    next_month = today.replace(day=28) + datetime.timedelta(days=4)
    return next_month - datetime.timedelta(days=next_month.day)


class MissionScreen(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_filter = "DIÁRIAS" 

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(40, 40, 40, 40)
        self.layout.setSpacing(25)
        
        # --- HEADER ---
        header_widget = QtWidgets.QWidget()
        header_layout = QtWidgets.QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setAlignment(QtCore.Qt.AlignVCenter)


        title_container = QtWidgets.QVBoxLayout()
        title_container.setSpacing(5)
        title = QtWidgets.QLabel("MISSÕES")
        title.setStyleSheet("font-size: 20px; font-weight: bold; letter-spacing: 1px; color: white;")
        underline = QtWidgets.QFrame()
        underline.setFixedHeight(4)
        underline.setFixedWidth(40)
        underline.setStyleSheet("background-color: #5E12F8; border-radius: 2px; border: none;")
        title_container.addWidget(title)
        title_container.addWidget(underline)
        
        self.btn_add = RotatableButton("+")
        self.btn_add.setFixedSize(50, 50)
        self.btn_add.clicked.connect(self.toggle_add)
        self.btn_add.setStyleSheet("""
            QPushButton {
                color: white;
                background-color: #5E12F8;
                border-radius: 25px;
                font-size: 28px;
                line-height: 50px;
                padding: 0px 0px 4px 0px;
                border: none;
            }
            """)

        
        header_layout.addLayout(title_container)
        header_layout.addStretch()
        header_layout.addWidget(self.btn_add)
        self.layout.addWidget(header_widget)

        # --- SELETOR DE CATEGORIA (TABS) ---
        self.layout.addWidget(self.build_tabs())

        # --- INPUT NOVA MISSÃO ---
        self.input_new = QtWidgets.QLineEdit()
        self.input_new.setPlaceholderText("O que vamos realizar agora?")
        self.input_new.setFixedHeight(45)
        self.input_new.hide()
        self.input_new.setStyleSheet("background-color: #1b1430; border: 1px solid #5E12F8; border-radius: 10px; padding: 0 15px; color: white;")
        self.input_new.returnPressed.connect(self.create_mission)
        self.layout.addWidget(self.input_new)

        # --- LISTA DE MISSÕES ---
        self.missions_container = QtWidgets.QVBoxLayout()
        self.missions_container.setAlignment(QtCore.Qt.AlignTop)
        self.missions_container.setSpacing(12)
        
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")
        content = QtWidgets.QWidget()
        content.setStyleSheet("background: transparent;")
        content.setLayout(self.missions_container)
        scroll.setWidget(content)
        self.layout.addWidget(scroll)

        self.status_footer = QtWidgets.QLabel("Nenhuma missão restante.")
        self.status_footer.setAlignment(QtCore.Qt.AlignCenter)
        self.status_footer.setStyleSheet("color: rgba(255,255,255,0.4); font-size: 11px; margin-top: 10px;")
        self.layout.addWidget(self.status_footer)
        
        self.anim = QtCore.QPropertyAnimation(self.btn_add, b"rotation", self)
        self.load_all()

    def build_tabs(self):
        container = QtWidgets.QFrame()
        container.setFixedHeight(45)
        container.setStyleSheet("""
            QFrame {
                background-color: #161026;
                border-radius: 10px;
                border: 1px solid #2d234a;
            }
        """)
        
        layout = QtWidgets.QHBoxLayout(container)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(0)

        self.tab_group = QtWidgets.QButtonGroup(self)
        
        tabs = ["DIÁRIAS", "SEMANAIS", "MENSAIS"]
        for i, text in enumerate(tabs):
            btn = QtWidgets.QPushButton(text)
            btn.setCheckable(True)
            btn.setFixedHeight(38)
            btn.setCursor(QtCore.Qt.PointingHandCursor)
            
            # Estilo dinâmico para os botões das abas
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: rgba(255,255,255,0.4);
                    border: none;
                    font-size: 10px;
                    font-weight: bold;
                    letter-spacing: 1px;
                    border-radius: 8px;
                }
                QPushButton:checked {
                    background-color: #5E12F8;
                    color: white;
                }
            """)
            
            if text == self.current_filter:
                btn.setChecked(True)
                
            btn.clicked.connect(self.change_filter)
            self.tab_group.addButton(btn)
            layout.addWidget(btn)
            
        return container

    def change_filter(self):
        self.current_filter = self.tab_group.checkedButton().text()
        self.load_all()

    def add_section_title(self, text):
        label = QtWidgets.QLabel(text)
        label.setStyleSheet("""
            color: rgba(255,255,255,0.5);
            font-size: 11px;
            letter-spacing: 1px;
            margin-top: 15px;
            margin-bottom: 5px;
        """)
        self.missions_container.addWidget(label)


    def load_all(self):
        while self.missions_container.count():
            w = self.missions_container.takeAt(0).widget()
            if w:
                w.deleteLater()

        data = load_missions()
        all_missions = data.get("missions", [])

        today = datetime.date.today()
        end_week = end_of_week()
        end_month = end_of_month()

        active = []
        late = []
        done = []

        # --- FILTRO POR ABA ---
        for m in all_missions:
            tipo = m.get("tipo", "DIÁRIAS")
            prazo = datetime.date.fromisoformat(m["prazo"]) if m.get("prazo") else None

            if tipo != self.current_filter:
                continue

            valid = False
            if tipo == "DIÁRIAS" and prazo == today:
                valid = True
            elif tipo == "SEMANAIS" and prazo <= end_week:
                valid = True
            elif tipo == "MENSAIS" and prazo <= end_month:
                valid = True

            if not valid:
                continue

            # --- CLASSIFICAÇÃO ---
            if m["status"] == "Concluída":
                done.append(m)
            elif self.is_late(m.get("prazo")):
                m["status"] = "Atrasada"
                late.append(m)
            else:
                active.append(m)

        # --- RENDERIZAÇÃO ---
        def render(m):
            card = MissionCard(
                m["id"],
                m["titulo"],
                m["status"],
                m.get("xp", 10),
                m.get("descricao"),
                m.get("categoria"),
                m.get("prazo")
            )
            card.clicked.connect(self.edit)
            card.status_changed.connect(self.sync)
            self.missions_container.addWidget(card)

        if late:
            self.add_section_title("ATRASADAS")
            for m in late:
                render(m)

        if active:
            self.add_section_title("ATIVAS")
            for m in active:
                render(m)

        if done:
            self.add_section_title("CONCLUÍDAS")
            for m in done:
                render(m)

        if not (late or active or done):
            self.status_footer.setText("Nenhuma missão restante.")
            self.status_footer.show()
        else:
            self.status_footer.hide()


    def create_mission(self):
        title = self.input_new.text().strip()
        if not title: return
        
        data = load_missions()
        today = datetime.date.today()

        if self.current_filter == "DIÁRIAS":
            prazo = end_of_day()
        elif self.current_filter == "SEMANAIS":
            prazo = end_of_week()
        elif self.current_filter == "MENSAIS":
            prazo = end_of_month()
        else:
            prazo = today

        new_m = {
            "id": max([m["id"] for m in data["missions"]] + [0]) + 1,
            "titulo": title,
            "status": "Pendente",
            "xp": 10,
            "categoria": "INTELIGÊNCIA",
            "prazo": prazo.isoformat(),
            "data_criacao": today.isoformat(),
            "descricao": "",
            "tipo": self.current_filter
        }

        data["missions"].append(new_m)
        save_missions_to_file(data)
        self.load_all()
        self.input_new.clear()
        self.toggle_add()

    # (Mantenha os métodos toggle_add, sync, edit e save_edit iguais ao seu código original)

    def toggle_add(self):
        is_open = self.input_new.isVisible()
        self.anim.setDuration(220)
        if is_open:
            self.input_new.hide()
            self.btn_add.setText("+")
            self.anim.setStartValue(45); self.anim.setEndValue(0)
        else:
            self.input_new.show()
            self.input_new.setFocus()
            self.btn_add.setText("×")
            self.anim.setStartValue(0); self.anim.setEndValue(45)
        self.anim.start()


    @staticmethod
    def is_late(prazo_iso):
        if not prazo_iso:
            return False
        prazo = datetime.date.fromisoformat(prazo_iso)
        return datetime.date.today() > prazo

    @staticmethod
    def calculate_xp(mission):
        base_xp = mission.get("xp", 10)

        if MissionScreen.is_late(mission.get("prazo")):
            return int(base_xp * 0.7)

        return base_xp

    def sync(self, card):
        data = load_missions()

        for m in data["missions"]:
            if m["id"] == card.mission_id:
                if card.is_done:
                    m["status"] = "Concluída"
                    gained_xp = self.calculate_xp(m)
                    print(f"XP ganho: {gained_xp}")
                else:
                    m["status"] = "Pendente"

        save_missions_to_file(data)
        self.load_all()


    def edit(self, card):
        data = load_missions()
        mission_data = next(m for m in data["missions"] if m["id"] == card.mission_id)

        modal = EditMissionModal(mission_data, self)
        modal.accepted.connect(lambda nv: self.save_edit(card.mission_id, nv))
        modal.exec()

    def save_edit(self, m_id, nv):
        data = load_missions()
        for m in data["missions"]:
            if m["id"] == m_id:
                m.update(nv)
                break
        save_missions_to_file(data)
        self.load_all()