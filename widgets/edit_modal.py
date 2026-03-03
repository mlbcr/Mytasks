from PySide6 import QtCore, QtWidgets, QtGui
from data_manager import load_config

class ConfirmDeletePopup(QtWidgets.QWidget):
    confirmed = QtCore.Signal()
    cancelled = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setGeometry(parent.rect())
        layout = QtWidgets.QGridLayout(self)
        
        self.bg = QtWidgets.QFrame()
        # Escurecimento sutil para o popup de confirmação
        self.bg.setStyleSheet("background-color: rgba(0, 0, 0, 150);")
        layout.addWidget(self.bg, 0, 0, 1, 1)

        self.card = QtWidgets.QFrame()
        self.card.setFixedSize(320, 180)
        self.card.setStyleSheet("""
            QFrame { 
                background-color: #1e1b2e; 
                border: 2px solid #e74c3c; 
                border-radius: 20px; 
            }
            QLabel { 
                color: white; 
                font-size: 14px; 
                font-weight: bold; 
                background: transparent; 
                border: none;
            }
            QPushButton { 
                padding: 10px; 
                border-radius: 8px; 
                font-weight: 800; 
                font-size: 11px; 
            }
            QPushButton#confirm { 
                background-color: #e74c3c; 
                color: white; 
            }
            QPushButton#confirm:hover { background-color: #ff5e4d; }
            
            QPushButton#cancel { 
                background-color: #322f50; 
                color: white; 
            }
            QPushButton#cancel:hover { background-color: #45416e; }
        """)
        
        card_layout = QtWidgets.QVBoxLayout(self.card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        
        label = QtWidgets.QLabel("Deseja apagar esta missão?")
        label.setAlignment(QtCore.Qt.AlignCenter)
        card_layout.addWidget(label)
        
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
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.data = mission_data
        
        config = load_config()
        categorias_cfg = config.get("categorias", {})

        if parent:
            self.setGeometry(parent.geometry())

        # Layout principal sem margens e sem cor de fundo esquisita
        layout_principal = QtWidgets.QVBoxLayout(self)
        layout_principal.setContentsMargins(0, 0, 0, 0)

        # Overlay único (escurece o fundo)
        self.overlay = QtWidgets.QFrame()
        self.overlay.setStyleSheet("background-color: rgba(10, 8, 18, 0.8);")
        layout_principal.addWidget(self.overlay)

        grid_layout = QtWidgets.QGridLayout(self.overlay)
        
        self.content_card = QtWidgets.QFrame()
        self.content_card.setObjectName("MainCard")
        self.content_card.setFixedWidth(460)
        self.content_card.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        
        self.content_card.setStyleSheet("""
            QFrame#MainCard { 
                background-color: #1e1b2e; 
                border-radius: 20px; 
                border: 1px solid #322f50; 
            }
            QLabel { 
                color: #8b5cf6; 
                font-size: 10px; 
                font-weight: 800; 
                letter-spacing: 1px; 
                text-transform: uppercase; 
            }
            QLineEdit, QTextEdit, QSpinBox, QDateEdit { 
                background-color: #161424; 
                color: white; 
                border: 1px solid #322f50; 
                border-radius: 10px; 
                padding: 10px; 
                font-size: 14px;
            }
            QLineEdit:focus, QTextEdit:focus, QSpinBox:focus, QDateEdit:focus { 
                border: 1px solid #8b5cf6; 
                background-color: #1e1b2e;
            }
            QLineEdit#titulo_principal { 
                font-size: 22px; 
                font-weight: 700; 
                border: none; 
                border-bottom: 2px solid #322f50; 
                border-radius: 0; 
                background-color: transparent;
                padding: 5px 0px;
            }
            QLineEdit#titulo_principal:focus { border-bottom: 2px solid #8b5cf6; }
            
            QPushButton#save { 
                background-color: #5E12F8; 
                color: white; 
                font-weight: 700; 
                border-radius: 10px; 
                padding: 14px; 
            }
            QPushButton#save:hover { background-color: #7c3aed; }
            
            QPushButton#cancel { 
                color: rgba(255, 255, 255, 0.4); 
                font-weight: 600; 
                background: transparent; 
            }
            QPushButton#cancel:hover { color: white; }

            QPushButton#delete { 
                background: transparent; 
                color: #ef4444; 
                border: 1px solid #ef4444; 
                border-radius: 8px; 
                font-size: 10px; 
                padding: 6px 12px; 
            }
            QPushButton#delete:hover { background: #ef4444; color: white; }
            
            QSpinBox::up-button, QSpinBox::down-button { width: 0px; }
        """)

        card_layout = QtWidgets.QVBoxLayout(self.content_card)
        card_layout.setContentsMargins(35, 35, 35, 35)
        card_layout.setSpacing(18)

        # Título e Delete
        header = QtWidgets.QHBoxLayout()
        self.edit_titulo = QtWidgets.QLineEdit(self.data.get("titulo", ""))
        self.edit_titulo.setObjectName("titulo_principal")
        self.btn_delete = QtWidgets.QPushButton("EXCLUIR")
        self.btn_delete.setObjectName("delete")
        self.btn_delete.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_delete.clicked.connect(self.confirm_delete)
        header.addWidget(self.edit_titulo, 1)
        header.addWidget(self.btn_delete)
        card_layout.addLayout(header)

        # Detalhes
        card_layout.addWidget(self.title("DETALHES DA MISSÃO"))
        self.edit_desc = QtWidgets.QTextEdit(self.data.get("descricao") or "")
        self.edit_desc.setFixedHeight(65)
        card_layout.addWidget(self.edit_desc)

        # Categorias
        card_layout.addWidget(self.title("CATEGORIA"))
        cat_widget = QtWidgets.QWidget()
        cat_grid = QtWidgets.QGridLayout(cat_widget)
        cat_grid.setContentsMargins(0, 0, 0, 0)
        cat_grid.setSpacing(8)
        
        self.cat_group = QtWidgets.QButtonGroup(self)
        self.cat_buttons = {}
        categoria_inicial = self.data.get("categoria")

        row, col = 0, 0
        for key, cat in categorias_cfg.items():
            if not cat.get("ativa", True): continue
            nome = cat.get("nome", key)
            cor = cat.get("cor", "#888888")

            btn = QtWidgets.QPushButton(nome.upper())
            btn.setCheckable(True)
            btn.setCursor(QtCore.Qt.PointingHandCursor)
            btn.setMinimumHeight(35)
            
            # Estilo das categorias sem fundos escuros pesados
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {cor};
                    border: 1px solid {cor};
                    border-radius: 8px;
                    font-size: 10px;
                    font-weight: bold;
                }}
                QPushButton:hover {{ 
                    background-color: {cor}; 
                    color: #1e1b2e; 
                }}
                QPushButton:checked {{
                    background-color: {cor};
                    color: #1e1b2e;
                }}
            """)

            if nome == categoria_inicial: btn.setChecked(True)
            self.cat_group.addButton(btn)
            self.cat_buttons[nome] = btn
            cat_grid.addWidget(btn, row, col)
            col += 1
            if col > 2: col = 0; row += 1

        card_layout.addWidget(cat_widget)

        # XP e Data (Layout Lado a Lado)
        h_info = QtWidgets.QHBoxLayout()
        
        v_xp = QtWidgets.QVBoxLayout()
        v_xp.addWidget(self.title("XP"))
        self.edit_xp = QtWidgets.QSpinBox()
        self.edit_xp.setRange(0, 1000)
        self.edit_xp.setSuffix(" XP")
        self.edit_xp.setValue(self.data.get("xp", 10))
        v_xp.addWidget(self.edit_xp)
        
        v_data = QtWidgets.QVBoxLayout()
        v_data.addWidget(self.title("DATA LIMITE"))
        self.edit_prazo = QtWidgets.QDateEdit()
        self.edit_prazo.setCalendarPopup(True)
        if self.data.get("prazo"):
            self.edit_prazo.setDate(QtCore.QDate.fromString(self.data.get("prazo"), "yyyy-MM-dd"))
        else:
            self.edit_prazo.setDate(QtCore.QDate.currentDate())
        v_data.addWidget(self.edit_prazo)
        
        h_info.addLayout(v_xp)
        h_info.addLayout(v_data)
        card_layout.addLayout(h_info)

        # Repetição (Dias da Semana)
        card_layout.addWidget(self.title("REPETIÇÃO"))
        days_layout = QtWidgets.QHBoxLayout()
        days_layout.setSpacing(6)
        self.day_buttons = []
        for name in ["S", "T", "Q", "Q", "S", "S", "D"]:
            btn = QtWidgets.QPushButton(name)
            btn.setCheckable(True)
            btn.setFixedSize(32, 32)
            btn.setCursor(QtCore.Qt.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton { 
                    border-radius: 16px; 
                    background: #161424; 
                    color: white; 
                    border: 1px solid #322f50; 
                    font-weight: bold;
                }
                QPushButton:hover { border: 1px solid #8b5cf6; }
                QPushButton:checked { background: #8b5cf6; border: none; }
            """)
            days_layout.addWidget(btn)
            self.day_buttons.append(btn)
        card_layout.addLayout(days_layout)

        # Rodapé
        card_layout.addSpacing(10)
        self.btn_save = QtWidgets.QPushButton("SALVAR ALTERAÇÕES")
        self.btn_save.setObjectName("save")
        self.btn_save.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_save.clicked.connect(self.submit)
        card_layout.addWidget(self.btn_save)

        self.btn_cancel = QtWidgets.QPushButton("DESCARTAR")
        self.btn_cancel.setObjectName("cancel")
        self.btn_cancel.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_cancel.clicked.connect(self.reject)
        card_layout.addWidget(self.btn_cancel)

        grid_layout.addWidget(self.content_card, 0, 0, QtCore.Qt.AlignCenter)

    def title(self, text):
        lbl = QtWidgets.QLabel(text)
        lbl.setAutoFillBackground(False)
        lbl.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
        return lbl

    def submit(self):
        categoria = ""
        for nome, btn in self.cat_buttons.items():
            if btn.isChecked():
                categoria = nome
                break
        new_data = {
            "titulo": self.edit_titulo.text(),
            "descricao": self.edit_desc.toPlainText(),
            "xp": self.edit_xp.value(),
            "categoria": categoria,
            "prazo": self.edit_prazo.date().toString("yyyy-MM-dd"),
            "repetida": [btn.isChecked() for btn in self.day_buttons]
        }
        self.accepted.emit(new_data)
        self.accept()

    def confirm_delete(self):
        self.popup = ConfirmDeletePopup(self)
        self.popup.show()
        self.popup.cancelled.connect(self.popup.deleteLater)
        self.popup.confirmed.connect(self.handle_delete)

    def handle_delete(self):
        self.deleted.emit(self.data.get("id", 0))
        self.popup.deleteLater()
        self.accept()