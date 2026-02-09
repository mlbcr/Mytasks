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
        self.categoria = categoria
        self.prazo = prazo
        self.setFixedHeight(85)
        
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
        self.cat_chip = QtWidgets.QLabel()
        self.cat_chip.setFixedHeight(18)
        self.cat_chip.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        text_layout.addWidget(self.label_title)
        text_layout.addWidget(self.label_desc)
        text_layout.addWidget(self.cat_chip)

        right_layout = QtWidgets.QVBoxLayout()
        right_layout.setSpacing(4)
        right_layout.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.xp_label = QtWidgets.QLabel(f"{xp} XP")
        self.xp_label.setStyleSheet("font-weight: bold; font-size: 18px;")
        self.label_prazo = QtWidgets.QLabel()
        self.label_prazo.setAlignment(QtCore.Qt.AlignRight)
        right_layout.addWidget(self.xp_label)
        right_layout.addWidget(self.label_prazo)

        layout.addWidget(self.btn_status)
        layout.addLayout(text_layout)
        layout.addStretch()
        layout.addLayout(right_layout)

        self.update_categoria(self.categoria)
        self.update_prazo(self.prazo)
        self.update_visuals()

    def update_categoria(self, categoria):
        self.categoria = categoria
        if not categoria:
            self.cat_chip.hide()
            return
        cor = CATEGORIAS.get(categoria, "#777")
        self.cat_chip.setText(f"+1 {categoria.upper()}")
        self.cat_chip.setStyleSheet(f"background-color: {cor}; color: #0e0b1c; padding: 0px 8px; border-radius: 4px; font-size: 9px; font-weight: bold;")
        self.cat_chip.show()

    def update_prazo(self, prazo):
        self.prazo = prazo
        if not prazo:
            self.label_prazo.clear()
            return
        p_date = QtCore.QDate.fromString(prazo, "yyyy-MM-dd")
        if p_date == QtCore.QDate.currentDate():
            self.label_prazo.setText("Hoje")
            self.label_prazo.setStyleSheet("font-weight: bold; font-size: 12px;")
        else:
            self.label_prazo.setText(f"Até {p_date.toString('dd/MM')}")
            self.label_prazo.setStyleSheet("font-weight: bold; font-size: 12px; color: rgba(255,255,255,0.4);")

    def toggle_status(self):
        self.is_done = not self.is_done
        self.update_visuals()
        self.status_changed.emit(self)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton and not self.btn_status.underMouse():
            self.clicked.emit(self)

    def update_visuals(self):
        common = "border: none; background: transparent;"
        if self.is_done:
            self.setStyleSheet("QFrame { background-color: rgba(94, 18, 248, 0.05); border-radius: 12px; border: 1px solid rgba(255,255,255,0.05); }")
            self.label_title.setStyleSheet(f"color: gray; font-size: 16px; font-weight: bold; text-decoration: line-through; {common}")
            self.btn_status.setStyleSheet("background-color: #5E12F8; border: 2px solid #5E12F8; border-radius: 11px;")
            self.xp_label.setStyleSheet(f"color: rgba(255,255,255,0.2); {common}")
        else:
            self.setStyleSheet("QFrame { background-color: #1b1430; border-radius: 12px; border: 1px solid #2d234a; }")
            self.label_title.setStyleSheet(f"color: white; font-size: 16px; font-weight: bold; {common}")
            self.btn_status.setStyleSheet("background-color: transparent; border: 2px solid white; border-radius: 11px;")
            self.xp_label.setStyleSheet(f"color: #5E12F8; font-weight: bold; {common}")