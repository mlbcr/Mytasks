from PySide6 import QtCore, QtWidgets, QtGui

CATEGORIAS = {
    "INTELIGÊNCIA": "#f1c40f", "FORÇA": "#e74c3c", "VITALIDADE": "#2ecc71",
    "CRIATIVIDADE": "#3498db", "SOCIAL": "#95a5a6"
}

class ConfirmDeletePopup(QtWidgets.QWidget):
    confirmed = QtCore.Signal()
    cancelled = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        # Faz o widget ocupar todo o espaço do pai
        self.setGeometry(parent.rect())
        
        # Layout principal para centralizar o card
        layout = QtWidgets.QGridLayout(self)
        
        # Fundo escurecido (Overlay)
        self.bg = QtWidgets.QFrame()
        self.bg.setStyleSheet("background-color: rgba(0, 0, 0, 180); border-radius: 20px;")
        layout.addWidget(self.bg, 0, 0, 1, 1)

        # Card de mensagem
        self.card = QtWidgets.QFrame()
        self.card.setFixedSize(300, 160)
        self.card.setStyleSheet("""
            QFrame {
                background-color: #25223d;
                border: 1px solid #e74c3c;
                border-radius: 15px;
            }
            QLabel {
                color: white;
                font-size: 14px;
                font-weight: bold;
                border: none;
                background: transparent;
            }
            QPushButton {
                padding: 10px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton#confirm {
                background-color: #e74c3c;
                color: white;
            }
            QPushButton#cancel {
                background-color: #322f50;
                color: rgba(255, 255, 255, 0.7);
            }
        """)
        
        card_layout = QtWidgets.QVBoxLayout(self.card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        
        label = QtWidgets.QLabel("Deseja realmente apagar\nesta missão?")
        label.setAlignment(QtCore.Qt.AlignCenter)
        card_layout.addWidget(label)
        
        card_layout.addStretch()
        
        btn_layout = QtWidgets.QHBoxLayout()
        self.btn_cancel = QtWidgets.QPushButton("VOLTAR")
        self.btn_cancel.setObjectName("cancel")
        self.btn_confirm = QtWidgets.QPushButton("EXCLUIR")
        self.btn_confirm.setObjectName("confirm")
        
        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_confirm)
        card_layout.addLayout(btn_layout)

        layout.addWidget(self.card, 0, 0, QtCore.Qt.AlignCenter)
        
        self.btn_cancel.clicked.connect(self.cancelled.emit)
        self.btn_confirm.clicked.connect(self.confirmed.emit)

class EditMissionModal(QtWidgets.QDialog):
    accepted = QtCore.Signal(dict)
    deleted = QtCore.Signal(int)

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
        
        # --- Card Principal ---
        self.content_card = QtWidgets.QFrame()
        self.content_card.setObjectName("MainCard")
        self.content_card.setFixedWidth(440)
        
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
                font-size: 22px; 
                font-weight: 700; 
                color: #ffffff;
                background: transparent; 
                border: none; 
                border-bottom: 2px solid #322f50;
                border-radius: 0px;
                padding: 5px 0px;
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
            }
            QPushButton#save:hover { background-color: #7227ff; }
            
            QPushButton#cancel { 
                background-color: transparent; 
                color: rgba(255, 255, 255, 0.4); 
                font-size: 12px;
                font-weight: 600;
            }
            QPushButton#cancel:hover { color: #ffffff; }

            QPushButton#delete {
                background-color: rgba(231, 76, 60, 0.1);
                color: #e74c3c;
                border-radius: 8px;
                font-weight: bold;
                font-size: 10px;
                padding: 5px 10px;
                border: 1px solid #e74c3c;
            }
            QPushButton#delete:hover {
                background-color: #e74c3c;
                color: white;
            }
            
            QComboBox::drop-down { border: none; width: 30px; }
        """)

        card_layout = QtWidgets.QVBoxLayout(self.content_card)
        card_layout.setContentsMargins(35, 30, 35, 35)
        card_layout.setSpacing(15)

        # --- Header com Título e Botão Excluir ---
        header_layout = QtWidgets.QHBoxLayout()
        self.edit_titulo = QtWidgets.QLineEdit(self.data.get("titulo", ""))
        self.edit_titulo.setObjectName("titulo_principal")
        self.edit_titulo.setPlaceholderText("Nome da tarefa")
        
        self.btn_delete = QtWidgets.QPushButton("EXCLUIR")
        self.btn_delete.setObjectName("delete")
        self.btn_delete.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_delete.clicked.connect(self.confirm_delete) # Conectado à função de confirmação
        
        header_layout.addWidget(self.edit_titulo, 1) # Título expande
        header_layout.addWidget(self.btn_delete)      # Botão fica no canto superior
        card_layout.addLayout(header_layout)

        # --- Campos de Detalhes ---
        card_layout.addWidget(QtWidgets.QLabel("DETALHES"))
        self.edit_desc = QtWidgets.QTextEdit(self.data.get("descricao") or "")
        self.edit_desc.setPlaceholderText("O que precisa ser feito?")
        self.edit_desc.setFixedHeight(80)
        card_layout.addWidget(self.edit_desc)

        h_layout = QtWidgets.QHBoxLayout()
        h_layout.setSpacing(15)
        
        v1 = QtWidgets.QVBoxLayout()
        v1.addWidget(QtWidgets.QLabel("CATEGORIA"))
        self.edit_cat = QtWidgets.QComboBox()
        self.edit_cat.addItem("")
        self.edit_cat.addItems(list(CATEGORIAS.keys()))

        # Seleciona a categoria atual, se houver
        categoria_inicial = self.data.get("categoria")
        if categoria_inicial and categoria_inicial in CATEGORIAS:
            self.edit_cat.setCurrentText(categoria_inicial)
        else:
            self.edit_cat.setCurrentIndex(0)


        v1.addWidget(self.edit_cat)

        v2 = QtWidgets.QVBoxLayout()
        v2.addWidget(QtWidgets.QLabel("XP"))
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

        card_layout.addSpacing(15)
        
        # --- Rodapé de Ações ---
        actions_layout = QtWidgets.QVBoxLayout()
        actions_layout.setSpacing(10)
        
        self.btn_save = QtWidgets.QPushButton("SALVAR ALTERAÇÕES")
        self.btn_save.setObjectName("save")
        self.btn_save.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_save.clicked.connect(self.submit)
        
        self.btn_cancel = QtWidgets.QPushButton("DESCARTAR")
        self.btn_cancel.setObjectName("cancel")
        self.btn_cancel.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_cancel.clicked.connect(self.reject)
        
        actions_layout.addWidget(self.btn_save)
        actions_layout.addWidget(self.btn_cancel)
        card_layout.addLayout(actions_layout)

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
    def confirm_delete(self):
        self.popup = ConfirmDeletePopup(self)
        self.popup.setGeometry(self.rect())
        self.popup.show()

        self.popup.cancelled.connect(self.popup.deleteLater)
        self.popup.confirmed.connect(self.handle_delete)

    def handle_delete(self):
        self.deleted.emit(self.data.get("id", 0))
        self.popup.deleteLater()
        self.accept()
