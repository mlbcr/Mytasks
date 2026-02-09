from PySide6 import QtCore, QtWidgets
import datetime
from data_manager import load_missions, save_missions_to_file
from widgets.mission_card import MissionCard
from widgets.edit_modal import EditMissionModal
from widgets.custom_button import RotatableButton

class MissionScreen(QtWidgets.QWidget):
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
        self.btn_add.setStyleSheet("QPushButton { color: white; background-color: #5E12F8; border-radius: 25px; font-size: 28px; border: none; }")
        
        header_layout.addLayout(title_container)
        header_layout.addStretch()
        header_layout.addWidget(self.btn_add)
        self.layout.addWidget(header_widget)

        self.input_new = QtWidgets.QLineEdit()
        self.input_new.setPlaceholderText("O que vamos realizar agora?")
        self.input_new.setFixedHeight(45)
        self.input_new.hide()
        self.input_new.setStyleSheet("background-color: #1b1430; border: 1px solid #5E12F8; border-radius: 10px; padding: 0 15px; color: white;")
        self.input_new.returnPressed.connect(self.create_mission)
        self.layout.addWidget(self.input_new)

        self.missions_container = QtWidgets.QVBoxLayout()
        self.missions_container.setAlignment(QtCore.Qt.AlignTop)
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")
        content = QtWidgets.QWidget()
        content.setLayout(self.missions_container)
        scroll.setWidget(content)
        self.layout.addWidget(scroll)
        
        self.anim = QtCore.QPropertyAnimation(self.btn_add, b"rotation", self)
        self.load_all()

    def load_all(self):
        while self.missions_container.count():
            w = self.missions_container.takeAt(0).widget()
            if w: w.deleteLater()
        data = load_missions()
        for m in sorted(data.get("missions", []), key=lambda x: x["status"] == "Concluída"):
            card = MissionCard(m["id"], m["titulo"], m["status"], m.get("xp", 10), m.get("descricao"), m.get("categoria"), m.get("prazo"))
            card.status_changed.connect(self.sync)
            card.clicked.connect(self.edit)
            self.missions_container.addWidget(card)

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

    def create_mission(self):
        title = self.input_new.text().strip()
        if not title: return
        data = load_missions()
        today = datetime.date.today().isoformat()
        new_m = {"id": max([m["id"] for m in data["missions"]] + [0]) + 1, "titulo": title, "status": "Pendente", "xp": 10, "categoria": "SOCIAL", "prazo": today, "data_criacao": today}
        data["missions"].append(new_m)
        save_missions_to_file(data)
        self.load_all()
        self.input_new.clear()
        self.toggle_add()

    def sync(self, card):
        data = load_missions()
        for m in data["missions"]:
            if m["id"] == card.mission_id: m["status"] = "Concluída" if card.is_done else "Pendente"
        save_missions_to_file(data)
        self.load_all()

    def edit(self, card):
        data = load_missions()
        mission_data = next(m for m in data["missions"] if m["id"] == card.mission_id)
        self.modal = EditMissionModal(mission_data, self.window())
        self.modal.accepted.connect(lambda nv: self.save_edit(card.mission_id, nv))
        self.modal.show()

    def save_edit(self, m_id, nv):
        data = load_missions()
        for m in data["missions"]:
            if m["id"] == m_id:
                m.update(nv)
                break
        save_missions_to_file(data)
        self.load_all()