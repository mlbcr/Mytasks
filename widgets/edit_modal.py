from PySide6 import QtCore, QtWidgets

CATEGORIAS = {
    "INTELIGÊNCIA": "#f1c40f", "FORÇA": "#e74c3c", "VITALIDADE": "#2ecc71",
    "CRIATIVIDADE": "#3498db", "SOCIAL": "#95a5a6"
}

class EditMissionModal(QtWidgets.QWidget):
    accepted = QtCore.Signal(dict)
    rejected = QtCore.Signal()

    def __init__(self, mission_data, parent=None):
        super().__init__(parent)
        self.data = mission_data
        if parent: self.resize(parent.size())
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.bg_overlay = QtWidgets.QFrame()
        self.bg_overlay.setStyleSheet("background-color: rgba(0, 0, 0, 0.7); border: none;")
        layout.addWidget(self.bg_overlay)
        self.content_card = QtWidgets.QFrame(self.bg_overlay)
        self.content_card.setFixedWidth(400)
        card_layout = QtWidgets.QVBoxLayout(self.content_card)
        card_layout.setContentsMargins(30, 20, 30, 30)
        self.edit_titulo = QtWidgets.QLineEdit(self.data.get("titulo", ""))
        self.edit_titulo.setAlignment(QtCore.Qt.AlignCenter) 
        self.edit_titulo.setObjectName("titulo_principal")
        self.edit_titulo.returnPressed.connect(self.submit)
        self.content_card.setStyleSheet("QFrame { background-color: #1b1430; border: 2px solid #5E12F8; border-radius: 20px; } QLineEdit#titulo_principal { font-size: 18px; font-weight: bold; color: white; background: transparent; border: none; border-bottom: 1px solid rgba(94, 18, 248, 0.3); margin-bottom: 15px; padding: 5px; } QLabel { font-weight: bold; color: #5E12F8; margin-top: 10px; background: transparent; border: none; } QLineEdit, QTextEdit, QComboBox, QSpinBox, QDateEdit { background-color: #161025; color: white; border: 1px solid #3d2b63; border-radius: 5px; padding: 5px; } QPushButton#save { background-color: #5E12F8; color: white; font-weight: bold; border-radius: 10px; padding: 12px; margin-top: 10px; } QPushButton#cancel { background-color: transparent; color: rgba(255,255,255,0.5); border: 1px solid rgba(255,255,255,0.2); border-radius: 10px; padding: 8px; }")
        card_layout.addWidget(self.edit_titulo)
        self.edit_desc = QtWidgets.QTextEdit(self.data.get("descricao") or "")
        self.edit_desc.setFixedHeight(60)
        card_layout.addWidget(QtWidgets.QLabel("DESCRIÇÃO"))
        card_layout.addWidget(self.edit_desc)
        h_layout = QtWidgets.QHBoxLayout()
        v1 = QtWidgets.QVBoxLayout()
        v1.addWidget(QtWidgets.QLabel("CATEGORIA"))
        self.edit_cat = QtWidgets.QComboBox()
        self.edit_cat.addItems(list(CATEGORIAS.keys()))
        self.edit_cat.setCurrentText(self.data.get("categoria", "SOCIAL"))
        v1.addWidget(self.edit_cat)
        v2 = QtWidgets.QVBoxLayout()
        v2.addWidget(QtWidgets.QLabel("XP"))
        self.edit_xp = QtWidgets.QSpinBox()
        self.edit_xp.setRange(0, 1000); self.edit_xp.setValue(self.data.get("xp", 10))
        v2.addWidget(self.edit_xp)
        h_layout.addLayout(v1); h_layout.addLayout(v2)
        card_layout.addLayout(h_layout)
        self.edit_prazo = QtWidgets.QDateEdit(calendarPopup=True)
        self.edit_prazo.setDate(QtCore.QDate.fromString(self.data.get("prazo", ""), "yyyy-MM-dd") if self.data.get("prazo") else QtCore.QDate.currentDate())
        card_layout.addWidget(QtWidgets.QLabel("PRAZO")); card_layout.addWidget(self.edit_prazo)
        self.btn_save = QtWidgets.QPushButton("SALVAR"); self.btn_save.setObjectName("save"); self.btn_save.clicked.connect(self.submit)
        self.btn_cancel = QtWidgets.QPushButton("CANCELAR"); self.btn_cancel.setObjectName("cancel"); self.btn_cancel.clicked.connect(self.close_modal)
        card_layout.addWidget(self.btn_save); card_layout.addWidget(self.btn_cancel)
        QtWidgets.QGridLayout(self.bg_overlay).addWidget(self.content_card, 0, 0, QtCore.Qt.AlignCenter)

    def submit(self):
        new_data = {"titulo": self.edit_titulo.text(), "descricao": self.edit_desc.toPlainText(), "xp": self.edit_xp.value(), "categoria": self.edit_cat.currentText(), "prazo": self.edit_prazo.date().toString("yyyy-MM-dd")}
        self.accepted.emit(new_data); self.close_modal()

    def close_modal(self):
        self.setParent(None); self.deleteLater()