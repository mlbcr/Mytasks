from PySide6 import QtCore, QtWidgets, QtGui
import datetime
from PySide6.QtMultimedia import QSoundEffect
from PySide6.QtCore import QUrl
from data_manager import load_missions, save_missions_to_file
from widgets.mission_card import MissionCard
from widgets.edit_modal import EditMissionModal
from widgets.custom_button import RotatableButton
from data_manager import load_user, save_user
from progression import add_xp_to_user

import sys
import os

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

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
    mission_completed = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_filter = "DIÁRIAS" 

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(40, 40, 40, 40)
        self.layout.setSpacing(25)
        
        self.finished_mission_sound = QSoundEffect(self)
        sound_path = resource_path("audio/complete.wav")

        self.finished_mission_sound.setSource(
            QUrl.fromLocalFile(sound_path)
        )
        self.finished_mission_sound.setVolume(0.5)

        sound_path = resource_path("audio/incomplete.wav")
        self.unfinished_mission_sound = QSoundEffect(self)

        self.unfinished_mission_sound.setSource(
            QUrl.fromLocalFile(sound_path)
        )
        self.unfinished_mission_sound.setVolume(0.3)

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
        self.btn_add.setFixedSize(55, 55)
        self.btn_add.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_add.clicked.connect(self.toggle_add)
        
        self.btn_add.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #7B2FF7, stop:1 #5E12F8);
                color: white;
                border-radius: 27px; /* Metade do tamanho para ser circular */
                font-size: 28px;
                font-weight: bold;
                border: 1px solid rgba(255, 255, 255, 0.1);
                padding-bottom: 5px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #8C4BFF, stop:1 #6D2AF9);
                border: 1px solid rgba(255, 255, 255, 0.3);
            }
            QPushButton:pressed {
                background: #4A0EC7;
                padding-top: 2px; /* Efeito de clique */
            }
        """)

        
        header_layout.addLayout(title_container)
        header_layout.addStretch()
        header_layout.addWidget(self.btn_add)
        self.layout.addWidget(header_widget)

        self.layout.addWidget(self.build_tabs())

        self.input_new = QtWidgets.QLineEdit()
        self.input_new.setPlaceholderText("O que vamos realizar agora?")
        self.input_new.setFixedHeight(45)
        self.input_new.hide()
        self.input_new.setStyleSheet("background-color: #1b1430; border: 1px solid #5E12F8; border-radius: 10px; padding: 0 15px; color: white;")
        self.input_new.returnPressed.connect(self.create_mission)
        self.layout.addWidget(self.input_new)

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

    def get_type_by_date(self, target_date):
        """Helper para definir a aba correta baseada na data."""
        today = datetime.date.today()
        end_week = end_of_week()
        end_month = end_of_month()

        if target_date <= today:
            return "DIÁRIAS"
        elif target_date <= end_week:
            return "SEMANAIS"
        elif target_date <= end_month:
            return "MENSAIS"
        return "MENSAIS"

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


    def migrate_late_to_daily(self, missions):
        today = datetime.date.today()

        for m in missions:
            if m.get("status") in ["Concluída", "deleted"]:
                continue

            prazo_iso = m.get("prazo")
            if not prazo_iso:
                continue

            prazo = datetime.date.fromisoformat(prazo_iso)

            # apenas atualiza a aba
            if prazo <= today:
                m["tipo"] = "DIÁRIAS"
            else:
                m["tipo"] = self.get_type_by_date(prazo)

    def check_repetitions(self, missions):
        """Verifica se missões concluídas ou atrasadas com repetição devem ser resetadas para hoje."""
        today = datetime.date.today()
        today_weekday = today.weekday() 
        
        changed = False
        for m in missions:
            if m.get("status") != "deleted" and any(m.get("repetida", [])):
                prazo_str = m.get("prazo")
                if not prazo_str: continue
                
                prazo_date = datetime.date.fromisoformat(prazo_str)
                
                if prazo_date < today or (prazo_date == today and m["status"] == "Concluída"):
                    if m["repetida"][today_weekday]:
                        m["status"] = "Pendente"
                        m["prazo"] = today.isoformat()
                        changed = True
        return changed

    def load_all(self):
        while self.missions_container.count():
            item = self.missions_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        data = load_missions()
        all_missions = data.get("missions", [])
        
        rep_updated = self.check_repetitions(all_missions)
        
        self.migrate_late_to_daily(all_missions)
        
        if rep_updated:
            save_missions_to_file(data)

        today = datetime.date.today()
        active, late, done = [], [], []

        for m in all_missions:
            if m.get("status") == "deleted": continue
            
            tipo = m.get("tipo", "DIÁRIAS")
            prazo_str = m.get("prazo")
            prazo = datetime.date.fromisoformat(prazo_str) if prazo_str else None

            if tipo != self.current_filter:
                continue

            if m.get("status") == "Concluída":
                done.append(m)
            elif prazo and prazo < today:
                m["status_visual"] = "Atrasada" 
                late.append(m)
            else:
                m["status_visual"] = "Pendente"
                active.append(m)

        def render(m):
            card = MissionCard(
                m["id"], 
                m["titulo"], 
                m.get("status_visual", m.get("status")),
                m.get("xp", 10),
                m.get("descricao"), 
                m.get("categoria"), 
                m.get("prazo"),
                m.get("repetida") 
            )
            card.clicked.connect(self.edit)
            card.status_changed.connect(self.sync)
            main_window = self.window()
            if hasattr(main_window, 'set_focus_mission'):
                card.associate_requested.connect(main_window.set_focus_mission)
            self.missions_container.addWidget(card)

        if active:
            self.add_section_title("ATIVAS")
            for m in active: render(m)

        if late:
            self.add_section_title("ATRASADAS")
            for m in late: render(m)

        if done:
            self.add_section_title("CONCLUÍDAS")
            for m in done: render(m)

        self.status_footer.setVisible(not (late or active or done))

    def create_mission(self):
        title = self.input_new.text().strip()
        if not title: return
        
        data = load_missions()
        today = datetime.date.today()

        if self.current_filter == "DIÁRIAS": prazo = end_of_day()
        elif self.current_filter == "SEMANAIS": prazo = end_of_week()
        elif self.current_filter == "MENSAIS": prazo = end_of_month()
        else: prazo = today

        new_m = {
            "id": max([m["id"] for m in data["missions"]] + [0]) + 1,
            "titulo": title,
            "status": "Pendente",
            "xp": 5,
            "categoria": None,
            "prazo": prazo.isoformat(),
            "data_criacao": today.isoformat(),
            "horario_inicio": None,
            "horario_fim": None, 
            "descricao": "",
            "repetida": [False] * 7,
            "tipo": self.current_filter 
        }

        data["missions"].append(new_m)
        save_missions_to_file(data)
        self.load_all()
        self.input_new.clear()
        self.toggle_add()

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
        user_data = load_user()  

        for m in data["missions"]:
            if m["id"] == card.mission_id:
                if card.is_done:
                    if m["status"] != "Concluída":  
                        m["status"] = "Concluída"
                        self.finished_mission_sound.play()

                        gained_xp = self.calculate_xp(m)
                        user_data = add_xp_to_user(user_data, gained_xp)

                        categoria = m.get("categoria")
                        if categoria:
                            key_map = {
                                "INTELIGÊNCIA": "inteligencia",
                                "FORÇA": "forca",
                                "VITALIDADE": "vitalidade",
                                "CRIATIVIDADE": "criatividade",
                                "SOCIAL": "social"
                            }
                            attr_key = key_map.get(categoria.upper())
                            if attr_key:
                                user_data["usuario"]["atributos"][attr_key] += 1

                        print(f"XP ganho: {gained_xp}")

                else:  
                    if m["status"] == "Concluída":  
                        m["status"] = "Pendente"
                        self.unfinished_mission_sound.play()

                        lost_xp = self.calculate_xp(m)
                        user_data = add_xp_to_user(user_data, -lost_xp)  

                        categoria = m.get("categoria")
                        if categoria:
                            key_map = {
                                "INTELIGÊNCIA": "inteligencia",
                                "FORÇA": "forca",
                                "VITALIDADE": "vitalidade",
                                "CRIATIVIDADE": "criatividade",
                                "SOCIAL": "social"
                            }
                            attr_key = key_map.get(categoria.upper())
                            if attr_key:
                                user_data["usuario"]["atributos"][attr_key] -= 1 

                        print(f"XP perdido: {lost_xp}")

        save_user(user_data)
        save_missions_to_file(data)
        self.mission_completed.emit()
        self.load_all()


    def edit(self, card):
        data = load_missions()
        mission_data = next(m for m in data["missions"] if m["id"] == card.mission_id)

        modal = EditMissionModal(mission_data, self)
        modal.accepted.connect(lambda nv: self.save_edit(card.mission_id, nv))
        modal.deleted.connect(self.delete_mission)
        modal.exec()

    def save_edit(self, m_id, nv):
        data = load_missions()
        for m in data["missions"]:
            if m["id"] == m_id:
                m.update(nv)
                break
        save_missions_to_file(data)
        self.load_all()
        self.mission_completed.emit()
    
    def delete_mission(self, m_id):
        data = load_missions()

        for m in data["missions"]:
            if m["id"] == m_id:
                m["status"] = "deleted"
                break

        save_missions_to_file(data)
        self.load_all()
        self.mission_completed.emit()

