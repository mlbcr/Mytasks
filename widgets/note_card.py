from PySide6 import QtCore, QtWidgets, QtGui

class NoteCard(QtWidgets.QFrame):
    clicked = QtCore.Signal(object)
    pin_toggled = QtCore.Signal(int, bool)

    def __init__(self, note_id, title, text, color="#1b1430", is_pinned=False):
        super().__init__()
        self.note_id = note_id
        self.is_pinned = is_pinned
        self.bg_color = color
        self.setObjectName("NoteCard")
        
        # Cores sempre claras para o texto no tema escuro
        self.text_color = "#FFFFFF"
        self.sub_color = "rgba(255, 255, 255, 0.6)"
        
        self.update_style()

        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(8)

        header = QtWidgets.QHBoxLayout()
        self.title_label = QtWidgets.QLabel(title)
        self.title_label.setStyleSheet(f"font-weight: bold; color: {self.text_color}; font-size: 15px; background: transparent;")
        
        self.btn_menu = QtWidgets.QPushButton("⋮")
        self.btn_menu.setFixedSize(24, 24)
        self.btn_menu.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_menu.setStyleSheet(f"border: none; color: {self.text_color}; font-size: 18px; font-weight: bold; background: transparent;")
        self.btn_menu.clicked.connect(self.show_context_menu)

        header.addWidget(self.title_label)
        
        if self.is_pinned:
            pin_label = QtWidgets.QLabel("FIXADO")
            pin_label.setStyleSheet(f"""
                QLabel {{
                    color: #A277FF;
                    background-color: rgba(162, 119, 255, 0.1);
                    border: 1px solid rgba(162, 119, 255, 0.3);
                    font-size: 9px;
                    font-weight: 900;
                    padding: 2px 8px;
                    border-radius: 4px;
                    letter-spacing: 1px;
                }}
            """)
            header.addWidget(pin_label)
                
        header.addStretch()
        header.addWidget(self.btn_menu)
        layout.addLayout(header)

        display_text = text[:120] + ("..." if len(text) > 120 else "")
        self.text_label = QtWidgets.QLabel(display_text)
        self.text_label.setWordWrap(True)
        self.text_label.setStyleSheet(f"color: {self.sub_color}; font-size: 13px; background: transparent;")
        layout.addWidget(self.text_label)

    def update_style(self):
        base_color = QtGui.QColor(self.bg_color)
        hover_color = base_color.darker(115).name() 
        
        border_style = "1px solid #5E12F8" if self.is_pinned else "1px solid #322f50"
        
        self.setStyleSheet(f"""
            QFrame#NoteCard {{
                background-color: {self.bg_color};
                border-radius: 12px;
                padding: 15px;
                border: {border_style};
            }}
            QFrame#NoteCard:hover {{
                border: 1px solid #5E12F8;
                background-color: {hover_color};
            }}
        """)

    def show_context_menu(self):
        menu = QtWidgets.QMenu(self)
        menu.setStyleSheet("QMenu { background-color: #1e1b2e; color: white; border: 1px solid #322f50; } QMenu::item:selected { background-color: #5E12F8; }")
        pin_action = menu.addAction("Desafixar" if self.is_pinned else "Fixar")
        action = menu.exec_(QtGui.QCursor.pos())
        if action == pin_action:
            self.pin_toggled.emit(self.note_id, not self.is_pinned)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton and not self.btn_menu.underMouse():
            self.clicked.emit(self)