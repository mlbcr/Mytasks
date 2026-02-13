from PySide6 import QtCore, QtWidgets, QtGui

class NoteCard(QtWidgets.QFrame):
    clicked = QtCore.Signal(object)

    def __init__(self, note_id, title, text):
        super().__init__()
        self.note_id = note_id
        self.setObjectName("NoteCard")

        # Estilo do Card (Mantenha o seu tema escuro aqui para contrastar com o modal)
        self.setStyleSheet("""
        QFrame#NoteCard {
            background-color: #2b1f4a;
            border-radius: 14px;
            padding: 15px;
            border: 1px solid #33294D;
        }
        QFrame#NoteCard:hover {
            background-color: #34245e;
            border: 1px solid #5E12F8;
        }
        """)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(8)

        self.title_label = QtWidgets.QLabel(title)
        self.title_label.setStyleSheet("font-weight: bold; color: white; font-size: 15px;")

        # Resumo do texto
        display_text = text[:120] + ("..." if len(text) > 120 else "")
        self.text_label = QtWidgets.QLabel(display_text)
        self.text_label.setWordWrap(True)
        self.text_label.setStyleSheet("color: rgba(255,255,255,0.7); font-size: 13px;")

        layout.addWidget(self.title_label)
        layout.addWidget(self.text_label)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.clicked.emit(self)