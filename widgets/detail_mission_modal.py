from PySide6 import QtCore, QtWidgets, QtGui


class DetailsMissionModal(QtWidgets.QDialog):
    edit_requested = QtCore.Signal() # Sinal para abrir o editor se o usuário quiser

    def __init__(self, mission_data, parent=None):
        super().__init__(parent)
        self.setModal(True)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.data = mission_data
        
        if parent:
            self.setGeometry(parent.geometry())

        layout_principal = QtWidgets.QVBoxLayout(self)
        layout_principal.setContentsMargins(0, 0, 0, 0)

        self.overlay = QtWidgets.QFrame()
        self.overlay.setStyleSheet("background-color: rgba(10, 8, 18, 0.85);")
        layout_principal.addWidget(self.overlay)

        grid_layout = QtWidgets.QGridLayout(self.overlay)
        
        self.content_card = QtWidgets.QFrame()
        self.content_card.setFixedWidth(400)
        self.content_card.setStyleSheet("""
            QFrame { 
                background-color: #1e1b2e; 
                border-radius: 20px; 
                border: 1px solid #322f50; 
            }
            QLabel#titulo { 
                color: white; 
                font-size: 24px; 
                font-weight: bold; 
                border: none;
            }
            QLabel#stats_label { 
                color: #8b5cf6; 
                font-size: 11px; 
                font-weight: 800; 
                text-transform: uppercase;
                border: none;
            }
            QLabel#stats_value { 
                color: white; 
                font-size: 18px; 
                font-weight: bold; 
                border: none;
            }
            QLabel#desc { 
                color: #a1a1aa; 
                font-size: 14px; 
                border: none;
            }
        """)

        card_layout = QtWidgets.QVBoxLayout(self.content_card)
        card_layout.setContentsMargins(30, 30, 30, 30)
        card_layout.setSpacing(15)

        # Header: Título
        lbl_titulo = QtWidgets.QLabel(self.data.get("titulo", "Missão Sem Nome"))
        lbl_titulo.setObjectName("titulo")
        lbl_titulo.setWordWrap(True)
        card_layout.addWidget(lbl_titulo)

        # Descrição
        lbl_desc = QtWidgets.QLabel(self.data.get("descricao") or "Sem descrição disponível.")
        lbl_desc.setObjectName("desc")
        lbl_desc.setWordWrap(True)
        card_layout.addWidget(lbl_desc)

        # Separador
        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setStyleSheet("background-color: #322f50;")
        card_layout.addWidget(line)

        # Grid de Estatísticas (Vezes completada, XP, Categoria)
        stats_grid = QtWidgets.QGridLayout()
        
        # Quantas vezes foi completa (Supondo que você tenha a chave 'completada_count')
        count = self.data.get("completada_count", 0)
        stats_grid.addWidget(self.create_stat_widget("COMPLETADA", f"{count}x"), 0, 0)
        stats_grid.addWidget(self.create_stat_widget("RECOMPENSA", f"{self.data.get('xp', 0)} XP"), 0, 1)
        stats_grid.addWidget(self.create_stat_widget("CATEGORIA", self.data.get("categoria", "GERAL")), 1, 0)
        
        card_layout.addLayout(stats_grid)

        # Botões de Ação
        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.setSpacing(10)

        self.btn_edit = QtWidgets.QPushButton("EDITAR MISSÃO")
        self.btn_edit.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_edit.setStyleSheet("""
            QPushButton { 
                background: #322f50; color: white; border-radius: 10px; 
                padding: 12px; font-weight: bold; 
            }
            QPushButton:hover { background: #45416e; }
        """)
        self.btn_edit.clicked.connect(self.request_edit)

        self.btn_close = QtWidgets.QPushButton("FECHAR")
        self.btn_close.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_close.setStyleSheet("""
            QPushButton { 
                background: #5E12F8; color: white; border-radius: 10px; 
                padding: 12px; font-weight: bold; 
            }
            QPushButton:hover { background: #7c3aed; }
        """)
        self.btn_close.clicked.connect(self.accept)

        btn_layout.addWidget(self.btn_edit)
        btn_layout.addWidget(self.btn_close)
        card_layout.addLayout(btn_layout)

        grid_layout.addWidget(self.content_card, 0, 0, QtCore.Qt.AlignCenter)

    def create_stat_widget(self, label, value):
        w = QtWidgets.QWidget()
        l = QtWidgets.QVBoxLayout(w)
        l.setContentsMargins(0,0,0,0)
        l.setSpacing(2)
        
        lbl = QtWidgets.QLabel(label)
        lbl.setObjectName("stats_label")
        val = QtWidgets.QLabel(str(value))
        val.setObjectName("stats_value")
        
        l.addWidget(lbl)
        l.addWidget(val)
        return w

    def request_edit(self):
        self.edit_requested.emit()
        self.accept()