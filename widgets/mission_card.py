from PySide6 import QtCore, QtWidgets, QtGui

CATEGORIAS = {
    "INTELIGÊNCIA": "#f1c40f", "FORÇA": "#e74c3c",
    "VITALIDADE": "#2ecc71", "CRIATIVIDADE": "#3498db", "SOCIAL": "#95a5a6"
}

class MissionCard(QtWidgets.QFrame):
    status_changed = QtCore.Signal(object)
    clicked = QtCore.Signal(object)
    associate_requested = QtCore.Signal(int)

    def __init__(self, mission_id, titulo, status="Pendente", xp=10, descricao=None, categoria=None, prazo=None):
        super().__init__()
        self.mission_id = mission_id
        self.is_done = (status == "Concluída")
        self.is_late = (status == "Atrasada")
        self.categoria = categoria
        self.prazo = prazo
        
        self.setMinimumHeight(90)
        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        
        # Layout Principal
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(20, 12, 15, 12)
        layout.setSpacing(15)

        # 1. Checkbox (Esquerda)
        self.btn_status = QtWidgets.QPushButton()
        self.btn_status.setFixedSize(24, 24)
        self.btn_status.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_status.clicked.connect(self.toggle_status)

        # 2. Área de Texto (Centro)
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

        # 3. Informações de XP/Prazo (Direita)
        right_info_container = QtWidgets.QWidget()
        right_info_layout = QtWidgets.QVBoxLayout(right_info_container)
        right_info_layout.setContentsMargins(0, 0, 0, 0)
        right_info_layout.setSpacing(2)
        right_info_layout.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        
        self.xp_label = QtWidgets.QLabel(f"{xp} XP")
        self.xp_label.setAlignment(QtCore.Qt.AlignRight)
        
        self.label_prazo = QtWidgets.QLabel()
        self.label_prazo.setAlignment(QtCore.Qt.AlignRight)
        
        right_info_layout.addWidget(self.xp_label)
        right_info_layout.addWidget(self.label_prazo)

        self.btn_menu = QtWidgets.QPushButton("⋮")
        self.btn_menu.setFixedSize(30, 30)
        self.btn_menu.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_menu.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: rgba(255, 255, 255, 0.3);
                font-size: 22px;
                font-weight: bold;
                border: none;
                border-radius: 15px;
            }
            QPushButton:hover { 
                color: white; 
                background-color: rgba(255, 255, 255, 0.1);
            }
        """)
        self.btn_menu.clicked.connect(self.open_menu)

        # Montagem do Layout Horizontal
        layout.addWidget(self.btn_status)
        layout.addLayout(text_layout, 1) # Ocupa o espaço disponível
        layout.addStretch()
        layout.addWidget(right_info_container)
        layout.addWidget(self.btn_menu) # Fica por último (extremo direito)

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
        self.cat_chip.setStyleSheet(f"background-color: {cor}; color: #0e0b1c; border-radius: 4px; font-size: 10px; font-weight: bold;")
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
        if self.is_done:
            self.is_late = False
        self.update_visuals()
        self.status_changed.emit(self)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            if not self.btn_status.underMouse() and not self.btn_menu.underMouse():
                self.clicked.emit(self)

    def update_visuals(self):

        if self.is_done:
            self.setStyleSheet("""
                MissionCard {
                    background-color: rgba(30, 27, 46, 0.6);
                    border-radius: 15px;
                    border: 1px solid rgba(255,255,255,0.05);
                }
            """)
            self.label_title.setStyleSheet("""
                color: rgba(255,255,255,0.2);
                font-size: 15px;
                font-weight: bold;
                text-decoration: line-through;
                background: transparent;
            """)
            self.xp_label.setStyleSheet("""
                color: rgba(255,255,255,0.1);
                font-weight: bold;
                font-size: 16px;
                background: transparent;
            """)
            self.btn_status.setStyleSheet("""
                QPushButton {
                    background-color: #5E12F8;
                    border: 2px solid #5E12F8;
                    border-radius: 12px;
                }
            """)

        elif self.is_late:
            self.setStyleSheet("""
                MissionCard {
                    background-color: rgba(30, 27, 46, 0.8);
                    border-radius: 15px;
                    border: 1px solid #e74c3c;
                }
            """)
            self.label_title.setStyleSheet("""
                color: #ff6b6b;
                font-size: 15px;
                font-weight: bold;
                background: transparent;
            """)
            self.xp_label.setStyleSheet("""
                color: #e74c3c;
                font-weight: bold;
                font-size: 16px;
                background: transparent;
            """)
            self.btn_status.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: 2px solid #e74c3c;
                    border-radius: 12px;
                }
                QPushButton:hover {
                    background-color: rgba(231, 76, 60, 0.15);
                }
            """)

        # -------------------------
        # NORMAL
        # -------------------------
        else:
            self.setStyleSheet("""
                MissionCard {
                    background-color: #1b1430;
                    border-radius: 15px;
                    border: 1px solid #2d234a;
                }
            """)
            self.label_title.setStyleSheet("""
                color: white;
                font-size: 15px;
                font-weight: bold;
                background: transparent;
            """)
            self.xp_label.setStyleSheet("""
                color: #5E12F8;
                font-weight: bold;
                font-size: 16px;
                background: transparent;
            """)
            self.btn_status.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: 2px solid white;
                    border-radius: 12px;
                }
                QPushButton:hover {
                    border: 2px solid #5E12F8;
                    background-color: rgba(94, 18, 248, 0.1);
                }
            """)

    def open_menu(self):
        menu = QtWidgets.QMenu(self)
        menu.setWindowFlags(menu.windowFlags() | QtCore.Qt.FramelessWindowHint | QtCore.Qt.NoDropShadowWindowHint)
        menu.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        menu.setStyleSheet("""
            QMenu {
                background-color: #1b1430;
                border: 1px solid #3d2e63;
                border-radius: 10px;
                padding: 5px;
                color: white;
            }
            QMenu::item {
                padding: 10px 25px;
                border-radius: 5px;
                font-size: 12px;
                font-weight: bold;
            }
            QMenu::item:selected {
                background-color: #5E12F8;
                color: white;
            }
        """)

        action_associate = menu.addAction("Associar ao Foco")
        action_edit = menu.addAction("Editar Missão")

        # Posiciona o menu abaixo do botão de 3 pontos
        pos = self.btn_menu.mapToGlobal(QtCore.QPoint(0, self.btn_menu.height()))
        action = menu.exec(pos)

        if action == action_associate:
            self.associate_requested.emit(self.mission_id)
        elif action == action_edit:
            self.clicked.emit(self)