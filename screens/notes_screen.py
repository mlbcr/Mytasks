from PySide6 import QtCore, QtWidgets
import datetime
from widgets.custom_button import RotatableButton
from widgets.note_card import NoteCard
from data_manager import load_notes, save_notes
from widgets.note_modal import NoteModal

class NotesScreen(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.overlay = None

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(40, 40, 40, 40)
        self.layout.setSpacing(25)

        header_widget = QtWidgets.QWidget()
        header_layout = QtWidgets.QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)

        title_container = QtWidgets.QVBoxLayout()
        title_container.setSpacing(5)

        title = QtWidgets.QLabel("NOTES")
        title.setStyleSheet("font-size: 20px; font-weight: bold; letter-spacing: 1px; color: white;")

        underline = QtWidgets.QFrame()
        underline.setFixedHeight(4)
        underline.setFixedWidth(40)
        underline.setStyleSheet("background-color: #5E12F8; border-radius: 2px; border: none;")

        title_container.addWidget(title)
        title_container.addWidget(underline)

        self.btn_add = RotatableButton("+")
        self.btn_add.setFixedSize(55, 55)
        self.btn_add.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_add.clicked.connect(self.toggle_add)
        
        self.btn_add.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #7B2FF7, stop:1 #5E12F8);
                color: white;
                border-radius: 27px;
                font-size: 28px;
                font-weight: bold;
                border: 1px solid rgba(255, 255, 255, 0.1);
                padding-bottom: 5px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #9A5CFF, stop:1 #7B2FF7);
            }
        """)

        header_layout.addLayout(title_container)
        header_layout.addStretch()
        header_layout.addWidget(self.btn_add)

        self.layout.addWidget(header_widget)

        # ---------- LISTA DE NOTAS COM SCROLL ----------
        self.notes_container = QtWidgets.QVBoxLayout()
        self.notes_container.setAlignment(QtCore.Qt.AlignTop)
        self.notes_container.setSpacing(12)

        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")

        content = QtWidgets.QWidget()
        content.setLayout(self.notes_container)
        content.setStyleSheet("background: transparent;")

        scroll.setWidget(content)
        self.layout.addWidget(scroll)

        self.anim = QtCore.QPropertyAnimation(self.btn_add, b"rotation", self)
        self.load_all()

    def load_all(self):
        # Limpa o container
        while self.notes_container.count():
            item = self.notes_container.takeAt(0)
            w = item.widget()
            if w: w.deleteLater()

        data = load_notes()
        notes = data.get("notes", [])

        # ORDENAÇÃO: 1º Pinned (True/False), 2º ID (Maior primeiro)
        sorted_notes = sorted(
            notes, 
            key=lambda x: (x.get("pinned", False), x.get("id", 0)), 
            reverse=True
        )

        for n in sorted_notes:
            # Passamos ID, Título, Texto, Cor e se está Pinned
            card = NoteCard(
                n["id"], 
                n["title"], 
                n["text"], 
                n.get("color", "#1e1b2e"), 
                n.get("pinned", False)
            )
            card.clicked.connect(lambda c, note=n: self.open_note(note))
            card.pin_toggled.connect(self.toggle_pin_status)
            self.notes_container.addWidget(card)

    def toggle_pin_status(self, note_id, status):
        data = load_notes()
        for n in data["notes"]:
            if n["id"] == note_id:
                n["pinned"] = status
                break
        save_notes(data)
        self.load_all()

    def open_note(self, note_data):
        self.show_modal(note_data)

    def toggle_add(self):
        if self.overlay:
            self.close_modal()
            return

        self.anim.setDuration(220)
        self.anim.setStartValue(0)
        self.anim.setEndValue(45)
        self.anim.start()
        self.btn_add.setText("×")
        self.show_modal()

    def show_modal(self, note_data=None):
        self.overlay = QtWidgets.QWidget(self)
        self.overlay.setGeometry(self.rect())
        self.overlay.setStyleSheet("background-color: rgba(0, 0, 0, 180);")
        
        self.modal = NoteModal(note_data, parent=self.overlay)
        self.modal.setFixedSize(500, 600)

        m_x = (self.width() - self.modal.width()) // 2
        m_y = (self.height() - self.modal.height()) // 2
        self.modal.move(m_x, m_y)

        self.modal.note_saved.connect(self.load_all)
        self.modal.note_saved.connect(self.close_modal)

        def click_outside(event):
            if not self.modal: return
            if not self.modal.geometry().contains(event.pos()):
                self.modal.process_save(close_after=True)

        self.overlay.mousePressEvent = click_outside
        self.overlay.show()

    def close_modal(self):
        if self.overlay:
            self.overlay.deleteLater()
            self.overlay = None

        self.anim.setDuration(220)
        self.anim.setStartValue(45)
        self.anim.setEndValue(0)
        self.anim.start()
        self.btn_add.setText("+")