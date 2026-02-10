from PySide6 import QtCore, QtWidgets, QtGui

CATEGORIAS = {
    "INTELIGÊNCIA": "#f1c40f", "FORÇA": "#e74c3c", "VITALIDADE": "#2ecc71",
    "CRIATIVIDADE": "#3498db", "SOCIAL": "#95a5a6"
}

class EditMissionModal(QtWidgets.QDialog):
    accepted = QtCore.Signal(dict)

    def __init__(self, mission_data, parent=None):
        super().__init__(parent)
        self.setModal(True)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowSystemMenuHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.data = mission_data
        
        if parent:
            self.setGeometry(parent.geometry())

        full_layout = QtWidgets.QVBoxLayout(self)
        full_layout.setContentsMargins(0, 0, 0, 0)

        self.bg_overlay = QtWidgets.QFrame()
        self.bg_overlay.setStyleSheet("background-color: rgba(15, 12, 28, 0.85);")
        full_layout.addWidget(self.bg_overlay)

        overlay_layout = QtWidgets.QGridLayout(self.bg_overlay)
        
        self.content_card = QtWidgets.QFrame()
        self.content_card.setObjectName("MainCard")
        self.content_card.setFixedWidth(420)
        
        self.content_card.setStyleSheet("""
            QFrame#MainCard { 
                background-color: #1e1b2e; 
                border-radius: 20px; 
                border: 1px solid #322f50;
            }
            QLabel { 
                color: #5E12F8; 
                font-size: 10px; 
                font-weight: 800; 
                letter-spacing: 0.5px;
                text-transform: uppercase;
                background: transparent; 
            }
            QLineEdit, QTextEdit, QComboBox, QSpinBox, QDateEdit { 
                background-color: #25223d; 
                color: #ffffff; 
                border: 1px solid #322f50; 
                border-radius: 10px; 
                padding: 12px; 
                font-size: 14px;
            }
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QSpinBox:focus, QDateEdit:focus { 
                border: 1px solid #5E12F8; 
            }
            QLineEdit#titulo_principal { 
                font-size: 24px; 
                font-weight: 700; 
                color: #ffffff;
                background: transparent; 
                border: none; 
                border-bottom: 2px solid #322f50;
                border-radius: 0px;
                padding: 0px;
                margin-bottom: 5px;
            }
            QLineEdit#titulo_principal:focus {
                border-bottom: 2px solid #5E12F8;
            }
            QPushButton#save { 
                background-color: #5E12F8;
                color: white; 
                font-size: 14px;
                font-weight: 700; 
                border-radius: 12px; 
                padding: 16px; 
                border: none;
            }
            QPushButton#save:hover { 
                background-color: #7227ff; 
            }
            QPushButton#cancel { 
                background-color: transparent; 
                color: rgba(255, 255, 255, 0.4); 
                font-size: 12px;
                font-weight: 600;
                border: none;
            }
            QPushButton#cancel:hover { color: #ff4d4d; }
            QComboBox::drop-down { border: none; width: 30px; }
            QSpinBox::up-button, QSpinBox::down-button { border: none; }
        """)

        card_layout = QtWidgets.QVBoxLayout(self.content_card)
        card_layout.setContentsMargins(45, 45, 45, 45)
        card_layout.setSpacing(15)

        self.edit_titulo = QtWidgets.QLineEdit(self.data.get("titulo", ""))
        self.edit_titulo.setObjectName("titulo_principal")
        self.edit_titulo.setPlaceholderText("Nome da tarefa")
        card_layout.addWidget(self.edit_titulo)

        card_layout.addWidget(QtWidgets.QLabel("DETALHES"))
        self.edit_desc = QtWidgets.QTextEdit(self.data.get("descricao") or "")
        self.edit_desc.setPlaceholderText("O que precisa ser feito?")
        self.edit_desc.setFixedHeight(100)
        card_layout.addWidget(self.edit_desc)

        h_layout = QtWidgets.QHBoxLayout()
        h_layout.setSpacing(20)
        
        v1 = QtWidgets.QVBoxLayout()
        v1.addWidget(QtWidgets.QLabel("CATEGORIA"))
        self.edit_cat = QtWidgets.QComboBox()
        self.edit_cat.addItems(list(CATEGORIAS.keys()))
        self.edit_cat.setCurrentText(self.data.get("categoria", "SOCIAL"))
        v1.addWidget(self.edit_cat)

        v2 = QtWidgets.QVBoxLayout()
        v2.addWidget(QtWidgets.QLabel("RECOMPENSA"))
        self.edit_xp = QtWidgets.QSpinBox()
        self.edit_xp.setRange(0, 1000)
        self.edit_xp.setSuffix(" XP")
        self.edit_xp.setValue(self.data.get("xp", 10))
        v2.addWidget(self.edit_xp)
        
        h_layout.addLayout(v1)
        h_layout.addLayout(v2)
        card_layout.addLayout(h_layout)

        card_layout.addWidget(QtWidgets.QLabel("DATA LIMITE"))
        self.edit_prazo = QtWidgets.QDateEdit(calendarPopup=True)
        self.edit_prazo.setDisplayFormat("dd MMMM yyyy")
        self.edit_prazo.setDate(QtCore.QDate.fromString(self.data.get("prazo", ""), "yyyy-MM-dd") if self.data.get("prazo") else QtCore.QDate.currentDate())
        card_layout.addWidget(self.edit_prazo)

        card_layout.addSpacing(20)
        
        self.btn_save = QtWidgets.QPushButton("SALVAR ALTERAÇÕES")
        self.btn_save.setObjectName("save")
        self.btn_save.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_save.clicked.connect(self.submit)
        
        self.btn_cancel = QtWidgets.QPushButton("DESCARTAR")
        self.btn_cancel.setObjectName("cancel")
        self.btn_cancel.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_cancel.clicked.connect(self.reject)
        
        card_layout.addWidget(self.btn_save)
        card_layout.addWidget(self.btn_cancel)

        overlay_layout.addWidget(self.content_card, 0, 0, QtCore.Qt.AlignCenter)

    def submit(self):
        new_data = {
            "titulo": self.edit_titulo.text(),
            "descricao": self.edit_desc.toPlainText(),
            "xp": self.edit_xp.value(),
            "categoria": self.edit_cat.currentText(),
            "prazo": self.edit_prazo.date().toString("yyyy-MM-dd")
        }
        self.accepted.emit(new_data)
        self.accept()