from PySide6 import QtCore, QtWidgets, QtGui

CATEGORIAS = {
    "INTELIGÊNCIA": "#f1c40f", "FORÇA": "#e74c3c",
    "VITALIDADE": "#2ecc71", "CRIATIVIDADE": "#3498db", "SOCIAL": "#95a5a6"
}

class MissionCard(QtWidgets.QFrame):
    status_changed = QtCore.Signal(object)
    clicked = QtCore.Signal(object)
    associate_requested = QtCore.Signal(int)

    def __init__(self, mission_id, titulo, status="Pendente", xp=10, descricao=None, categoria=None, prazo=None, repetida=None):
        super().__init__()
        self.mission_id = mission_id
        self.is_done = (status == "Concluída")
        self.is_late = (status == "Atrasada") 
        self.categoria = categoria
        self.prazo = prazo
        self.repetida = repetida if repetida else [False] * 7
        
        self.setObjectName("MissionCard")
        self.setMinimumHeight(100) 
        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        
        self.text_color = "#FFFFFF"
        self.sub_color = "rgba(255, 255, 255, 0.6)"
        
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(15)

        self.btn_status = QtWidgets.QPushButton()
        self.btn_status.setFixedSize(24, 24)
        self.btn_status.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_status.clicked.connect(self.toggle_status)

        text_container = QtWidgets.QVBoxLayout()
        text_container.setSpacing(2) 
        text_container.setAlignment(QtCore.Qt.AlignVCenter)
        
        self.label_title = QtWidgets.QLabel(titulo)
        self.label_title.setStyleSheet(f"font-weight: bold; color: {self.text_color}; font-size: 15px; background: transparent;")
        
        desc_text = descricao if descricao else "Sem descrição"
        self.label_desc = QtWidgets.QLabel()
        self.label_desc.setStyleSheet(f"color: {self.sub_color}; font-size: 12px; background: transparent;")
        
        self.label_desc.setWordWrap(False)
        metrics = QtGui.QFontMetrics(self.label_desc.font())
        elided_text = metrics.elidedText(desc_text, QtCore.Qt.ElideRight, 250) 
        self.label_desc.setText(elided_text)
        
        tags_layout = QtWidgets.QHBoxLayout()
        tags_layout.setSpacing(8)
        tags_layout.setContentsMargins(0, 4, 0, 0)
        
        self.cat_chip = QtWidgets.QLabel()
        self.cat_chip.setFixedHeight(16)
        
        self.repeat_widget = QtWidgets.QWidget()
        rep_layout = QtWidgets.QHBoxLayout(self.repeat_widget)
        rep_layout.setContentsMargins(0, 0, 0, 0)
        rep_layout.setSpacing(3)
        
        days_names = ["S", "T", "Q", "Q", "S", "S", "D"]
        for i, active in enumerate(self.repetida):
            day_label = QtWidgets.QLabel(days_names[i])
            day_label.setFixedSize(14, 14)
            day_label.setAlignment(QtCore.Qt.AlignCenter)
            color = "#5E12F8" if active else "rgba(255, 255, 255, 0.15)"
            bg = "rgba(94, 18, 248, 0.1)" if active else "transparent"
            day_label.setStyleSheet(f"font-size: 8px; font-weight: 900; color: {color}; background: {bg}; border-radius: 3px;")
            rep_layout.addWidget(day_label)
            
        tags_layout.addWidget(self.cat_chip)
        if any(self.repetida):
            tags_layout.addWidget(self.repeat_widget)
        tags_layout.addStretch()

        text_container.addWidget(self.label_title)
        text_container.addWidget(self.label_desc)
        text_container.addLayout(tags_layout)

        right_container = QtWidgets.QVBoxLayout()
        right_container.setSpacing(2)
        right_container.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        
        self.xp_label = QtWidgets.QLabel(f"{xp} XP")
        self.xp_label.setStyleSheet(f"font-weight: 900; color: #5E12F8; font-size: 14px; background: transparent;")
        
        self.label_prazo = QtWidgets.QLabel()
        self.label_prazo.setStyleSheet(f"color: {self.sub_color}; font-size: 11px; background: transparent;")
        
        right_container.addWidget(self.xp_label)
        right_container.addWidget(self.label_prazo)

        # --- Menu ---
        self.btn_menu = QtWidgets.QPushButton("⋮")
        self.btn_menu.setFixedSize(24, 24)
        self.btn_menu.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_menu.setStyleSheet(f"border: none; color: {self.sub_color}; font-size: 18px; font-weight: bold; background: transparent;")
        self.btn_menu.clicked.connect(self.open_menu)

        layout.addWidget(self.btn_status)
        layout.addLayout(text_container, 1)
        layout.addLayout(right_container)
        layout.addWidget(self.btn_menu)

        self.update_categoria(self.categoria)
        self.update_prazo(self.prazo)
        self.update_visuals()
        

    def update_visuals(self):
        if self.is_done:
            border = "1px solid rgba(255,255,255,0.05)"
            bg = "rgba(30, 27, 46, 0.6)"
            title_style = f"font-weight: bold; color: rgba(255,255,255,0.2); font-size: 15px; text-decoration: line-through; background: transparent;"
            self.btn_status.setStyleSheet("QPushButton { background-color: #5E12F8; border: 2px solid #5E12F8; border-radius: 12px; }")
        
        elif self.is_late: 
            border = "2px solid #e74c3c" 
            bg = "rgba(231, 76, 60, 0.1)" 
            title_style = "font-weight: 900; color: #ff6b6b; font-size: 15px; background: transparent;"
            self.btn_status.setStyleSheet("QPushButton { background-color: transparent; border: 2px solid #e74c3c; border-radius: 12px; }")
        
        else:
            border = "1px solid #322f50"
            bg = "#1b1430"
            title_style = f"font-weight: bold; color: #FFFFFF; font-size: 15px; background: transparent;"
            self.btn_status.setStyleSheet("QPushButton { background-color: transparent; border: 2px solid white; border-radius: 12px; }")

        self.label_title.setStyleSheet(title_style)
        self.setStyleSheet(f"""
            QFrame#MissionCard {{
                background-color: {bg};
                border-radius: 12px;
                border: {border};
            }}
            QFrame#MissionCard:hover {{
                border: 1px solid #5E12F8;
                background-color: rgba(94, 18, 248, 0.05);
            }}
        """)

    def update_categoria(self, categoria):
        self.categoria = categoria
        if not categoria:
            self.cat_chip.hide()
            return
        cor = CATEGORIAS.get(categoria.upper(), "#777")
        self.cat_chip.setText(f" {categoria.upper()} ")
        self.cat_chip.setStyleSheet(f"background-color: {cor}; color: #0e0b1c; border-radius: 4px; font-size: 9px; font-weight: 900; padding: 2px;")
        self.cat_chip.show()

    def update_prazo(self, prazo):
        self.prazo = prazo
        if not prazo:
            self.label_prazo.clear()
            return
            
        p_date = QtCore.QDate.fromString(prazo, "yyyy-MM-dd")
        current_date = QtCore.QDate.currentDate()
        tomorrow = current_date.addDays(1)
        
        if self.is_late:
            self.label_prazo.setText("ATRASADA")
            self.label_prazo.setStyleSheet("font-weight: 900; color: #ff6b6b; font-size: 10px; letter-spacing: 1px;")
        elif p_date == current_date:
            self.label_prazo.setText("Hoje")
            self.label_prazo.setStyleSheet("font-weight: bold; color: white; font-size: 11px;")
        elif p_date == tomorrow:
            self.label_prazo.setText("Amanhã")
            self.label_prazo.setStyleSheet("font-weight: bold; color: #f1c40f; font-size: 11px;")
        else:
            self.label_prazo.setText(f"{p_date.toString('dd/MM')}")
            self.label_prazo.setStyleSheet(f"color: {self.sub_color}; font-size: 11px;")

    def toggle_status(self):
        self.is_done = not self.is_done
        if self.is_done: self.is_late = False
        self.update_visuals()
        self.status_changed.emit(self)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton and not self.btn_status.underMouse() and not self.btn_menu.underMouse():
            self.clicked.emit(self)

    def open_menu(self):
        menu = QtWidgets.QMenu(self)
        menu.setWindowFlags(menu.windowFlags() | QtCore.Qt.FramelessWindowHint)
        menu.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        menu.setStyleSheet("QMenu { background-color: #1e1b2e; color: white; border: 1px solid #322f50; border-radius: 8px; padding: 5px; } QMenu::item:selected { background-color: #5E12F8; border-radius: 4px; }")
        
        action_associate = menu.addAction("Associar ao Foco")
        action_edit = menu.addAction("Editar Missão")
        
        action = menu.exec(QtGui.QCursor.pos())
        if action == action_associate: self.associate_requested.emit(self.mission_id)
        elif action == action_edit: self.clicked.emit(self)