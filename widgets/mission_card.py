from PySide6 import QtCore, QtWidgets, QtGui

CATEGORIAS = {
    "INTELIGÊNCIA": "#f1c40f", "FORÇA": "#e74c3c",
    "VITALIDADE": "#2ecc71", "CRIATIVIDADE": "#3498db", "SOCIAL": "#95a5a6"
}

class MissionCard(QtWidgets.QFrame):
    status_changed = QtCore.Signal(object)
    clicked = QtCore.Signal(object)

    def __init__(self, mission_id, titulo, status="Pendente", xp=10, descricao=None, categoria=None, prazo=None):
        super().__init__()
        self.mission_id = mission_id
        self.is_done = (status == "Concluída")
        self.is_late = (status == "Atrasada")
        self.categoria = categoria
        self.prazo = prazo
        
        # Ajuste de altura dinâmica para comportar descrição
        self.setMinimumHeight(85)
        self.setAttribute(QtCore.Qt.WA_StyledBackground, True) # Garante que o QSS pegue no frame customizado
        
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(15)

        # --- Botão de Status com Hover ---
        self.btn_status = QtWidgets.QPushButton()
        self.btn_status.setFixedSize(22, 22)
        self.btn_status.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_status.clicked.connect(self.toggle_status)

        # --- Layout de Texto (Esquerda) ---
        text_layout = QtWidgets.QVBoxLayout()
        text_layout.setSpacing(4)
        
        self.label_title = QtWidgets.QLabel(titulo)
        
        self.label_desc = QtWidgets.QLabel(descricao if descricao else "Sem descrição")
        self.label_desc.setStyleSheet("color: rgba(255, 255, 255, 0.5); font-size: 12px;")
        
        self.cat_chip = QtWidgets.QLabel()
        self.cat_chip.setFixedHeight(18)
        self.cat_chip.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        text_layout.addWidget(self.label_title)
        text_layout.addWidget(self.label_desc)
        text_layout.addWidget(self.cat_chip)

        right_container = QtWidgets.QWidget()
        right_container.setFixedWidth(80) 
        right_layout = QtWidgets.QVBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(4)
        right_layout.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        
        self.xp_label = QtWidgets.QLabel(f"{xp} XP")
        self.xp_label.setAlignment(QtCore.Qt.AlignRight)
        
        self.label_prazo = QtWidgets.QLabel()
        self.label_prazo.setAlignment(QtCore.Qt.AlignRight)
        
        right_layout.addWidget(self.xp_label)
        right_layout.addWidget(self.label_prazo)

        layout.addWidget(self.btn_status)
        layout.addLayout(text_layout)
        layout.addStretch()
        layout.addWidget(right_container)

        self.update_categoria(self.categoria)
        self.update_prazo(self.prazo)
        self.update_visuals()

    def update_categoria(self, categoria):
        self.categoria = categoria
        if not categoria:
            self.cat_chip.hide()
            return
        cor = CATEGORIAS.get(categoria, "#777")
        self.cat_chip.setText(f" {categoria.upper()} ")
        self.cat_chip.setStyleSheet(f"""
            background-color: {cor}; 
            color: #0e0b1c; 
            border-radius: 4px; 
            font-size: 10px; 
            font-weight: bold;
        """)
        self.cat_chip.show()

    def update_prazo(self, prazo):
        self.prazo = prazo
        if not prazo:
            self.label_prazo.clear()
            return
        p_date = QtCore.QDate.fromString(prazo, "yyyy-MM-dd")
        if p_date == QtCore.QDate.currentDate():
            self.label_prazo.setText("Hoje")
            self.label_prazo.setStyleSheet("font-weight: bold; font-size: 11px; color: #e74c3c;")
        else:
            self.label_prazo.setText(f"{p_date.toString('dd/MM')}")
            self.label_prazo.setStyleSheet("font-size: 11px; color: rgba(255,255,255,0.4);")

    def toggle_status(self):
        self.is_done = not self.is_done

        if not self.is_done and self.prazo:
            today = QtCore.QDate.currentDate()
            prazo = QtCore.QDate.fromString(self.prazo, "yyyy-MM-dd")
            self.is_late = today > prazo
        else:
            self.is_late = False

        self.update_visuals()
        self.status_changed.emit(self)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton and not self.btn_status.underMouse():
            self.clicked.emit(self)

    def update_visuals(self):
        if self.is_done:
            self.setStyleSheet("""
                MissionCard { background-color: rgba(94, 18, 248, 0.05); border-radius: 12px; border: 1px solid rgba(255,255,255,0.05); }
            """)
            self.label_title.setStyleSheet("color: #666; font-size: 15px; font-weight: bold; text-decoration: line-through; background: transparent;")
            self.label_desc.setStyleSheet("color: rgba(100, 100, 100, 0.4); font-size: 12px; background: transparent;")
            self.xp_label.setStyleSheet("color: rgba(255,255,255,0.2); font-weight: bold; font-size: 16px; background: transparent;")
            
            # Botão concluído
            self.btn_status.setStyleSheet("""
                QPushButton { background-color: #5E12F8; border: 2px solid #5E12F8; border-radius: 11px; }
                QPushButton:hover { background-color: #7a3efb; }
            """)
        elif self.is_late:
            self.setStyleSheet("""
                MissionCard {
                    background-color: #241c3a;
                    border-radius: 12px;
                    border: 1px solid #a60319;
                }
            """)
            self.label_title.setStyleSheet(
                "color: #b8a9ff; font-size: 15px; font-weight: bold;"
            )
            self.xp_label.setStyleSheet(
                "color: rgba(255,255,255,0.5); font-weight: bold; font-size: 16px;"
            )
            self.btn_status.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: 2px dashed #a60319;
                    border-radius: 11px;
                }
            """)
        else:
            self.setStyleSheet("""
                MissionCard { background-color: #1b1430; border-radius: 12px; border: 1px solid #2d234a; }
            """)
            self.label_title.setStyleSheet("color: white; font-size: 15px; font-weight: bold; background: transparent;")
            self.label_desc.setStyleSheet("color: rgba(255, 255, 255, 0.6); font-size: 12px; background: transparent;")
            self.xp_label.setStyleSheet("color: #5E12F8; font-weight: bold; font-size: 16px; background: transparent;")
            
            # Botão pendente com Hover de "ameaça"
            self.btn_status.setStyleSheet("""
                QPushButton { background-color: transparent; border: 2px solid white; border-radius: 11px; }
                QPushButton:hover { background-color: rgba(94, 18, 248, 0.3); border: 2px solid #5E12F8; }
            """)