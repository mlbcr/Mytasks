from PySide6 import QtCore, QtWidgets, QtGui
from datetime import datetime
from data_manager import load_focus_history, save_focus_history, load_missions

class FocusScreen(QtWidgets.QWidget):
    time_updated = QtCore.Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.mode = "TIMER"
        self.running = False
        self.total_seconds = 3600
        self.current_seconds = self.total_seconds
        self.start_time = None
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_time)
        
        self.current_mission_id = None

        self.build_ui()
        self.update_display()
        self.load_initial_history()

    def apply_styles(self):
        self.setStyleSheet("""
            QPushButton {
                background-color: #251b3e;
                color: #a0a0a0;
                border: 1px solid #3d2e63;
                border-radius: 8px;
                font-weight: bold;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: #2d214a;
                color: white;
                border: 1px solid #5E12F8;
            }
            QPushButton:checked {
                background-color: #5E12F8;
                color: white;
                border: none;
            }
            QLineEdit#TimerInput {
                background: transparent;
                border: none;
                color: white;
                font-size: 86px;
                font-weight: 200;
                font-family: 'Segoe UI Semilight';
            }
            QTimeEdit {
                background-color: #1b1430;
                color: white;
                border: 1px solid #3d2e63;
                border-radius: 8px;
                padding: 5px;
            }
            QTimeEdit::up-button, QTimeEdit::down-button { width: 0px; }
            
            QMenu {
                background-color: #1b1430;
                border: 1px solid #3d2e63;
                border-radius: 10px;
                color: white;
                padding: 5px;
            }
            QMenu::item {
                padding: 10px 20px;
                border-radius: 5px;
            }
            QMenu::item:selected {
                background-color: #5E12F8;
            }
        """)

    def build_ui(self):
        outer_layout = QtWidgets.QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        container_widget = QtWidgets.QWidget()
        main_layout = QtWidgets.QVBoxLayout(container_widget)
        main_layout.setSpacing(30)
        main_layout.setContentsMargins(50, 40, 50, 40)

        main_layout.addWidget(self.build_header())
        main_layout.addWidget(self.build_mode_selector())
        main_layout.addWidget(self.build_time_selector())
        main_layout.addWidget(self.build_timer_card())
        main_layout.addWidget(self.build_history_section())
        
        main_layout.addStretch()

        scroll.setWidget(container_widget)
        outer_layout.addWidget(scroll)
        self.apply_styles()

    def build_header(self):
        header = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 0)
        title_container = QtWidgets.QVBoxLayout()
        title = QtWidgets.QLabel("MODO FOCO")
        title.setStyleSheet("font-size: 20px; font-weight: bold; letter-spacing: 1px; color: white;")
        underline = QtWidgets.QFrame()
        underline.setFixedHeight(4); underline.setFixedWidth(40)
        underline.setStyleSheet("background-color: #5E12F8; border-radius: 2px;")
        title_container.addWidget(title); title_container.addWidget(underline)
        layout.addLayout(title_container); layout.addStretch()
        return header

    def build_mode_selector(self):
        container = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(container)
        self.btn_group = QtWidgets.QButtonGroup(self)
        self.btn_timer = QtWidgets.QPushButton("TIMER")
        self.btn_crono = QtWidgets.QPushButton("CRONÔMETRO")
        for btn in (self.btn_timer, self.btn_crono):
            btn.setCheckable(True); btn.setFixedSize(140, 42)
            self.btn_group.addButton(btn)
        self.btn_timer.setChecked(True)
        self.btn_timer.clicked.connect(lambda: self.set_mode("TIMER"))
        self.btn_crono.clicked.connect(lambda: self.set_mode("CRONOMETRO"))
        layout.addStretch(); layout.addWidget(self.btn_timer); layout.addWidget(self.btn_crono); layout.addStretch()
        return container

    def build_time_selector(self):
        self.time_selector = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(self.time_selector)
        layout.setContentsMargins(0, 0, 0, 0); layout.setSpacing(15)
        suggested = QtWidgets.QWidget()
        s_layout = QtWidgets.QHBoxLayout(suggested)
        s_layout.setContentsMargins(0, 0, 0, 0)
        for sec, txt in [(900, "15 MIN"), (1800, "30 MIN"), (3600, "1 HORA")]:
            btn = QtWidgets.QPushButton(txt)
            btn.setFixedHeight(34)
            btn.clicked.connect(lambda _, s=sec: self.set_timer(s))
            s_layout.addWidget(btn)
        custom = QtWidgets.QWidget()
        c_layout = QtWidgets.QHBoxLayout(custom); c_layout.setContentsMargins(0, 0, 0, 0)
        lbl = QtWidgets.QLabel("PERSONALIZADO:")
        lbl.setStyleSheet("font-size: 10px; font-weight: bold; color: #6a6a6a; letter-spacing: 1px;")
        self.custom_time = QtWidgets.QTimeEdit()
        self.custom_time.setDisplayFormat("HH:mm:ss"); self.custom_time.setTime(QtCore.QTime(0, 45, 0)); self.custom_time.setFixedWidth(110)
        btn_apply = QtWidgets.QPushButton("DEFINIR")
        btn_apply.setFixedHeight(30); btn_apply.setStyleSheet("font-size: 11px; background-color: #1b1430;")
        btn_apply.clicked.connect(self.apply_custom_time)
        c_layout.addStretch(); c_layout.addWidget(lbl); c_layout.addWidget(self.custom_time); c_layout.addWidget(btn_apply)
        layout.addWidget(suggested); layout.addLayout(c_layout)
        return self.time_selector

    def build_timer_card(self):
        container = QtWidgets.QFrame()
        container.setObjectName("TimerCard")
        container.setStyleSheet("#TimerCard { background-color: #1b1430; border: 1px solid #3d2e63; border-radius: 24px; }")
        layout = QtWidgets.QVBoxLayout(container)
        layout.setContentsMargins(40, 30, 40, 40)
        layout.setSpacing(20)

        
        self.time_input = QtWidgets.QLineEdit("00:00:00")
        self.time_input.setObjectName("TimerInput")
        self.time_input.setAlignment(QtCore.Qt.AlignCenter)
        self.time_input.setInputMask("99:99:99") 
        self.time_input.editingFinished.connect(self.manual_time_edit)
        
        btn_layout = QtWidgets.QHBoxLayout()
        self.btn_toggle = QtWidgets.QPushButton("INICIAR")
        self.btn_reset = QtWidgets.QPushButton("REINICIAR")
        self.btn_finish = QtWidgets.QPushButton("FINALIZAR")
        self.btn_finish.setVisible(False)
        
        self.btn_toggle.setStyleSheet("background-color: #5E12F8; color: white; height: 48px; font-size: 14px;")
        self.btn_finish.setStyleSheet("background-color: #1b1430; border: 1px solid #00fa9a; color: #00fa9a; height: 48px;")
        self.btn_reset.setStyleSheet("height: 48px;")

        self.btn_toggle.clicked.connect(self.toggle_timer)
        self.btn_reset.clicked.connect(self.stop_timer)
        self.btn_finish.clicked.connect(self.finish_session)

        btn_layout.addWidget(self.btn_toggle, 2)
        btn_layout.addWidget(self.btn_reset, 1)
        btn_layout.addWidget(self.btn_finish, 1)

        # Seletor de Missão (Substituindo o label estático)
        self.btn_mission_selector = QtWidgets.QPushButton("ASSOCIAR MISSÃO")
        self.btn_mission_selector.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_mission_selector.setStyleSheet("""
            QPushButton {
                background-color: rgba(94, 18, 248, 0.1);
                color: #5E12F8;
                border: 1px dashed #5E12F8;
                border-radius: 12px;
                padding: 8px;
                font-size: 11px;
                font-weight: 800;
                letter-spacing: 1px;
            }
            QPushButton:hover {
                background-color: rgba(94, 18, 248, 0.2);
            }
        """)
        self.btn_mission_selector.clicked.connect(self.show_mission_menu)

        layout.addWidget(self.time_input)
        layout.addLayout(btn_layout)
        layout.addWidget(self.btn_mission_selector)
        return container

    def show_mission_menu(self):
        menu = QtWidgets.QMenu(self)
        menu.setWindowFlags(menu.windowFlags() | QtCore.Qt.FramelessWindowHint | QtCore.Qt.NoDropShadowWindowHint)
        menu.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        menu.setStyleSheet("""
            QMenu {
                background-color: #1b1430;
                border: 1px solid #3d2e63;
                border-radius: 12px;
                padding: 8px;
                color: white;
            }
            QMenu::item {
                padding: 12px 25px;
                border-radius: 6px;
                margin: 2px 0px;
                font-size: 13px;
                font-weight: 500;
                min-width: 280px; /* Largura muito mais visível */
            }
            QMenu::item:selected {
                background-color: #5E12F8;
                color: white;
            }
            QMenu::item:disabled {
                color: rgba(255, 255, 255, 0.3);
            }
            QMenu::separator {
                height: 1px;
                background: #3d2e63;
                margin: 6px 10px;
            }
        """)

        data = load_missions()
        missions = [m for m in data.get("missions", []) if m["status"] != "Concluída"]
        
        if not missions:
            action = menu.addAction("Nenhuma missão ativa encontrada")
            action.setEnabled(False)
        else:
            title_action = menu.addAction("SELECIONE UMA MISSÃO")
            title_action.setEnabled(False)
            menu.addSeparator()

            for m in missions:
                action = menu.addAction(f"{m['titulo']}")
                action.triggered.connect(lambda _, mid=m["id"]: self.set_associated_mission(mid))
        
        # Garante que a largura do menu seja no mínimo o tamanho do botão seletor
        menu.setMinimumWidth(self.btn_mission_selector.width())

        # Executa o menu logo abaixo do botão
        menu.exec(self.btn_mission_selector.mapToGlobal(QtCore.QPoint(0, self.btn_mission_selector.height() + 5)))
    def manual_time_edit(self):
        if self.running or self.mode == "CRONOMETRO": return 
        text = self.time_input.text()
        try:
            h, m, s = map(int, text.split(':'))
            seconds = h * 3600 + m * 60 + s
            self.total_seconds = seconds; self.current_seconds = seconds
        except ValueError: self.update_display()

    def build_history_section(self):
        container = QtWidgets.QWidget()
        self.history_layout = QtWidgets.QVBoxLayout(container); self.history_layout.setContentsMargins(0, 20, 0, 0)
        title = QtWidgets.QLabel("SESSÕES RECENTES")
        title.setStyleSheet("font-size: 11px; font-weight: 800; color: #5E12F8; letter-spacing: 2px;")
        self.history_layout.addWidget(title)
        self.history_list_container = QtWidgets.QVBoxLayout(); self.history_list_container.setSpacing(10)
        self.history_layout.addLayout(self.history_list_container)
        return container

    def load_initial_history(self):
        data = load_focus_history()
        for day in sorted(data.keys()):
            for session in data[day].get("sessions", []):
                start_dt = datetime.fromisoformat(session["start"])
                end_dt = datetime.fromisoformat(session["end"])
                self.add_to_history(start_dt, end_dt, session["elapsed"], 
                                    mode=session.get("mode"), 
                                    mission_id=session.get("mission_id"))
    
    def add_to_history(self, start_time, end_time, elapsed_seconds, mode=None, mission_id=None):
        h, rem = divmod(elapsed_seconds, 3600); m, s = divmod(rem, 60)
        duration_str = f"{h:02}:{m:02}:{s:02}"
        time_range = f"{start_time.strftime('%H:%M')} — {end_time.strftime('%H:%M')}"
        
        item = QtWidgets.QFrame()
        item.setStyleSheet("QFrame { background-color: #1b1430; border: 1px solid #2d234a; border-radius: 12px; }")
        layout = QtWidgets.QHBoxLayout(item); layout.setContentsMargins(20, 15, 20, 15)
        
        l_info = QtWidgets.QVBoxLayout()
        t_lbl = QtWidgets.QLabel(f"{duration_str} FOCADO"); t_lbl.setStyleSheet("font-size: 15px; font-weight: bold; color: white; border: none;")
        
        # Container para os badges (Modo e Missão)
        badges_layout = QtWidgets.QHBoxLayout()
        badges_layout.setSpacing(8)
        
        m_lbl = QtWidgets.QLabel(mode if mode else self.mode)
        m_lbl.setStyleSheet("font-size: 9px; color: #5E12F8; font-weight: 900; letter-spacing: 1px; border: none;")
        badges_layout.addWidget(m_lbl)

        # Se houver missão, adiciona o badge da missão
        if mission_id:
            all_missions = load_missions().get("missions", [])
            mission = next((m for m in all_missions if m["id"] == mission_id), None)
            if mission:
                miss_lbl = QtWidgets.QLabel(f"◈ {mission['titulo'].upper()}")
                miss_lbl.setStyleSheet("font-size: 9px; color: #00fa9a; font-weight: 900; letter-spacing: 0.5px; border: none;")
                badges_layout.addWidget(miss_lbl)
        
        badges_layout.addStretch()
        
        l_info.addWidget(t_lbl)
        l_info.addLayout(badges_layout)

        r_info = QtWidgets.QVBoxLayout(); r_info.setAlignment(QtCore.Qt.AlignRight)
        rg_lbl = QtWidgets.QLabel(time_range); rg_lbl.setStyleSheet("font-size: 13px; font-weight: bold; color: #a0a0a0; border: none;")
        d_lbl = QtWidgets.QLabel(start_time.strftime('%d/%m/%Y')); d_lbl.setStyleSheet("font-size: 9px; color: #4a4a4a; font-weight: bold; border: none;")
        r_info.addWidget(rg_lbl); r_info.addWidget(d_lbl)
        
        layout.addLayout(l_info); layout.addStretch(); layout.addLayout(r_info)
        self.history_list_container.insertWidget(0, item)
        
    def finish_session(self):
        if not self.start_time: self.stop_timer(); return
        end_time = datetime.now()
        elapsed = (self.total_seconds - self.current_seconds) if self.mode == "TIMER" else self.current_seconds
        
        if elapsed > 0:
            day_key = self.start_time.strftime("%Y-%m-%d")
            data = load_focus_history()
            if day_key not in data: data[day_key] = {"total_seconds": 0, "sessions": []}
            
            # Salva o ID da missão atual na sessão
            session = {
                "mode": self.mode, 
                "start": self.start_time.isoformat(), 
                "end": end_time.isoformat(), 
                "elapsed": elapsed, 
                "mission_id": self.current_mission_id # ID salvo aqui
            }
            
            data[day_key]["sessions"].append(session)
            data[day_key]["total_seconds"] = sum(s["elapsed"] for s in data[day_key]["sessions"])
            save_focus_history(data)
            
            self.add_to_history(self.start_time, end_time, elapsed, mission_id=self.current_mission_id)
        
        self.stop_timer()

    def set_timer(self, seconds):
        if seconds <= 0: return
        self.stop_timer(); self.total_seconds = seconds; self.current_seconds = seconds; self.update_display()

    def set_mode(self, mode):
        self.mode = mode; self.time_selector.setVisible(mode == "TIMER"); self.stop_timer(); self.time_input.setReadOnly(mode == "CRONOMETRO")

    def apply_custom_time(self):
        t = self.custom_time.time(); seconds = (t.hour() * 3600) + (t.minute() * 60) + t.second()
        if seconds > 0: self.set_timer(seconds)

    def toggle_timer(self):
        if self.running: self.timer.stop(); self.btn_toggle.setText("CONTINUAR")
        else:
            self.manual_time_edit(); self.timer.start(1000); self.btn_toggle.setText("PAUSAR")
            if self.start_time is None: self.start_time = datetime.now()
        self.running = not self.running; self.btn_finish.setVisible(True); self.time_input.setReadOnly(True)

    def update_time(self):
        if self.mode == "TIMER":
            if self.current_seconds > 0: self.current_seconds -= 1
            else: self.finish_session()
        else: self.current_seconds += 1
        self.update_display()

    def update_display(self):
        h, rem = divmod(self.current_seconds, 3600); m, s = divmod(rem, 60)
        time_str = f"{h:02}:{m:02}:{s:02}"
        self.time_input.setText(time_str); self.time_updated.emit(time_str)

    def stop_timer(self):
        self.timer.stop(); self.running = False; self.start_time = None; self.btn_toggle.setText("INICIAR")
        self.btn_finish.setVisible(False); self.time_input.setReadOnly(self.mode == "CRONOMETRO")
        self.current_seconds = self.total_seconds if self.mode == "TIMER" else 0
        self.update_display()
    
    def set_associated_mission(self, mission_id):
        data = load_missions()
        mission = next((m for m in data["missions"] if m["id"] == mission_id), None)
        if mission:
            self.current_mission_id = mission_id
            self.btn_mission_selector.setText(f"FOCO EM: {mission['titulo'].upper()}")
            self.btn_mission_selector.setStyleSheet("""
                QPushButton {
                    background-color: rgba(0, 250, 154, 0.1);
                    color: #00fa9a;
                    border: 1px solid #00fa9a;
                    border-radius: 12px;
                    padding: 8px;
                    font-size: 11px;
                    font-weight: 800;
                    letter-spacing: 1px;
                }
            """)