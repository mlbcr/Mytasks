from PySide6 import QtCore, QtWidgets, QtGui
from datetime import datetime

class FocusScreen(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.mode = "TIMER"
        self.running = False
        self.total_seconds = 3600
        self.current_seconds = self.total_seconds
        
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_time)
        
        self.build_ui()
        self.update_display()

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
            QLineEdit#TimerInput:read-only {
                color: #a0a0a0;
            }
            QTimeEdit {
                background-color: #1b1430;
                color: white;
                border: 1px solid #3d2e63;
                border-radius: 8px;
                padding: 5px;
                font-family: 'Segoe UI';
                font-size: 13px;
            }
            QTimeEdit::up-button, QTimeEdit::down-button { width: 0px; }
            
            QScrollBar:vertical {
                border: none;
                background: #0e0b1c;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #3d2e63;
                border-radius: 4px;
            }
        """)

    def build_header(self):
        label = QtWidgets.QLabel("MODO FOCO")
        label.setAlignment(QtCore.Qt.AlignCenter)
        label.setStyleSheet("font-size: 22px; font-weight: 800; color: white; letter-spacing: 3px;")
        return label

    def build_mode_selector(self):
        container = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(container)
        self.btn_group = QtWidgets.QButtonGroup(self)
        self.btn_timer = QtWidgets.QPushButton("TIMER")
        self.btn_crono = QtWidgets.QPushButton("CRONÔMETRO")
        for btn in (self.btn_timer, self.btn_crono):
            btn.setCheckable(True)
            btn.setFixedSize(140, 42)
            self.btn_group.addButton(btn)
        self.btn_timer.setChecked(True)
        self.btn_timer.clicked.connect(lambda: self.set_mode("TIMER"))
        self.btn_crono.clicked.connect(lambda: self.set_mode("CRONOMETRO"))
        layout.addStretch(); layout.addWidget(self.btn_timer); layout.addWidget(self.btn_crono); layout.addStretch()
        return container

    def build_time_selector(self):
        self.time_selector = QtWidgets.QWidget()
        main_layout = QtWidgets.QVBoxLayout(self.time_selector)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(15)

        suggested_container = QtWidgets.QWidget()
        suggested_layout = QtWidgets.QHBoxLayout(suggested_container)
        suggested_layout.setContentsMargins(0, 0, 0, 0)
        times = [(900, "15 MIN"), (1800, "30 MIN"), (3600, "1 HORA")]
        for seconds, text in times:
            btn = QtWidgets.QPushButton(text)
            btn.setFixedHeight(34)
            btn.clicked.connect(lambda _, s=seconds: self.set_timer(s))
            suggested_layout.addWidget(btn)
        
        custom_container = QtWidgets.QWidget()
        custom_layout = QtWidgets.QHBoxLayout(custom_container)
        custom_layout.setContentsMargins(0, 0, 0, 0)
        
        label_custom = QtWidgets.QLabel("PERSONALIZADO:")
        label_custom.setStyleSheet("font-size: 10px; font-weight: bold; color: #6a6a6a; letter-spacing: 1px;")
        
        self.custom_time = QtWidgets.QTimeEdit()
        self.custom_time.setDisplayFormat("HH:mm:ss")
        self.custom_time.setTime(QtCore.QTime(0, 45, 0))
        self.custom_time.setFixedWidth(110)
        
        btn_apply = QtWidgets.QPushButton("DEFINIR")
        btn_apply.setFixedHeight(30)
        btn_apply.setStyleSheet("font-size: 11px; background-color: #1b1430;")
        btn_apply.clicked.connect(self.apply_custom_time)
        
        custom_layout.addStretch()
        custom_layout.addWidget(label_custom)
        custom_layout.addWidget(self.custom_time)
        custom_layout.addWidget(btn_apply)

        main_layout.addWidget(suggested_container)
        main_layout.addLayout(custom_layout)
        return self.time_selector

    def build_timer_card(self):
        container = QtWidgets.QFrame()
        container.setObjectName("TimerCard")
        container.setStyleSheet("#TimerCard { background-color: #1b1430; border: 1px solid #3d2e63; border-radius: 24px; }")
        layout = QtWidgets.QVBoxLayout(container)
        layout.setContentsMargins(40, 40, 40, 40)

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

        layout.addWidget(self.time_input)
        layout.addLayout(btn_layout)
        return container

    def manual_time_edit(self):
        if self.running or self.mode == "CRONOMETRO": return 
        
        text = self.time_input.text()
        try:
            h, m, s = map(int, text.split(':'))
            seconds = h * 3600 + m * 60 + s
            self.total_seconds = seconds
            self.current_seconds = seconds
        except ValueError:
            self.update_display()

    def build_history_section(self):
        container = QtWidgets.QWidget()
        self.history_layout = QtWidgets.QVBoxLayout(container)
        self.history_layout.setContentsMargins(0, 20, 0, 0)
        
        title = QtWidgets.QLabel("SESSÕES RECENTES")
        title.setStyleSheet("font-size: 11px; font-weight: 800; color: #5E12F8; letter-spacing: 2px;")
        self.history_layout.addWidget(title)
        
        self.history_list_container = QtWidgets.QVBoxLayout()
        self.history_list_container.setSpacing(10)
        self.history_layout.addLayout(self.history_list_container)
        return container

    def add_to_history(self, seconds, completed=True):
        h, rem = divmod(seconds, 3600)
        m, s = divmod(rem, 60)
        time_str = f"{h:02}:{m:02}:{s:02}"
        timestamp = datetime.now().strftime("%H:%M • %d/%m")
        mode_text = self.mode

        item = QtWidgets.QFrame()
        item.setStyleSheet("QFrame { background-color: #161025; border: 1px solid #2d234a; border-radius: 10px; }")
        
        layout = QtWidgets.QHBoxLayout(item)
        layout.setContentsMargins(20, 15, 20, 15)

        info_layout = QtWidgets.QVBoxLayout()
        time_display = QtWidgets.QLabel(time_str)
        time_display.setStyleSheet("font-size: 18px; font-weight: bold; color: white;")
        sub_info = QtWidgets.QLabel(f"{mode_text}  |  {timestamp}")
        sub_info.setStyleSheet("font-size: 10px; color: #6a6a6a; font-weight: bold; letter-spacing: 1px;")
        
        info_layout.addWidget(time_display)
        info_layout.addWidget(sub_info)
        
        status_tag = QtWidgets.QLabel("CONCLUÍDO" if completed else "NÃO FINALIZADO")
        status_tag.setStyleSheet(f"font-size: 9px; font-weight: 800; padding: 4px 10px; border-radius: 4px; color: {'#00fa9a' if completed else '#ff7675'}; border: 1px solid {'#00fa9a' if completed else '#ff7675'};")

        layout.addLayout(info_layout)
        layout.addStretch()
        layout.addWidget(status_tag)

        self.history_list_container.insertWidget(0, item)

    def finish_session(self):
        elapsed = (self.total_seconds - self.current_seconds) if self.mode == "TIMER" else self.current_seconds
        if elapsed > 0:
            self.add_to_history(elapsed, completed=True)
        self.stop_timer()

    def set_timer(self, seconds):
        if seconds <= 0: return
        self.stop_timer()
        self.total_seconds = seconds
        self.current_seconds = seconds
        self.update_display()

    def set_mode(self, mode):
        self.mode = mode
        self.time_selector.setVisible(mode == "TIMER")
        self.stop_timer()
        # Bloqueia edição se for Cronômetro
        self.time_input.setReadOnly(mode == "CRONOMETRO")

    def apply_custom_time(self):
        t = self.custom_time.time()
        seconds = (t.hour() * 3600) + (t.minute() * 60) + t.second()
        if seconds > 0:
            self.set_timer(seconds)

    def toggle_timer(self):
        if self.running:
            self.timer.stop()
            self.btn_toggle.setText("CONTINUAR")
            # Só libera edição se estiver no modo TIMER
            self.time_input.setReadOnly(self.mode == "CRONOMETRO")
        else:
            self.manual_time_edit()
            self.timer.start(1000)
            self.update_time()
            self.btn_toggle.setText("PAUSAR")
            self.time_input.setReadOnly(True)
        
        self.running = not self.running
        self.btn_finish.setVisible(self.running)

    def update_time(self):
        if self.mode == "TIMER":
            if self.current_seconds > 0: self.current_seconds -= 1
            else: self.finish_session()
        else:
            self.current_seconds += 1
        self.update_display()

    def update_display(self):
        h, rem = divmod(self.current_seconds, 3600)
        m, s = divmod(rem, 60)
        self.time_input.setText(f"{h:02}:{m:02}:{s:02}")

    def stop_timer(self):
        if self.running:
            elapsed = (self.total_seconds - self.current_seconds) if self.mode == "TIMER" else self.current_seconds
            if elapsed > 0: self.add_to_history(elapsed, completed=False)

        self.timer.stop()
        self.running = False
        self.btn_toggle.setText("INICIAR")
        self.btn_finish.setVisible(False)
        self.time_input.setReadOnly(self.mode == "CRONOMETRO")
        self.current_seconds = self.total_seconds if self.mode == "TIMER" else 0
        self.update_display()