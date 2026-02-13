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

        # ---------- BOTÃO ADICIONAR (REESTILIZADO) ----------
        self.btn_add = RotatableButton("+") # Use apenas o símbolo
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
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #9A5CFF,
                    stop:1 #7B2FF7
                );
            }
            QPushButton:pressed {
                background: #4A0EC7;
                padding-top: 2px; /* Efeito de clique */
            }
        """)

        header_layout.addLayout(title_container)
        header_layout.addStretch()
        header_layout.addWidget(self.btn_add)

        self.layout.addWidget(header_widget)

        self.input_container = QtWidgets.QWidget()
        input_layout = QtWidgets.QVBoxLayout(self.input_container)
        input_layout.setSpacing(10)

        self.input_title = QtWidgets.QLineEdit()
        self.input_title.setPlaceholderText("Note title...")
        self.input_title.setFixedHeight(40)
        self.input_title.setStyleSheet("background:#1b1430; border:1px solid #5E12F8; border-radius:8px; padding:0 10px; color:white;")

        self.input_text = QtWidgets.QTextEdit()
        self.input_text.setPlaceholderText("Write your note here...")
        self.input_text.setFixedHeight(100)
        self.input_text.setStyleSheet("background:#1b1430; border:1px solid #5E12F8; border-radius:8px; padding:10px; color:white;")

        self.btn_save = QtWidgets.QPushButton("Save Note")
        self.btn_save.setFixedHeight(40)
        self.btn_save.setStyleSheet("""
            QPushButton {
                background-color: #5E12F8;
                color: white;
                border-radius: 8px;
                font-weight: bold;
            }
        """)
        self.btn_save.clicked.connect(self.create_note)

        input_layout.addWidget(self.input_title)
        input_layout.addWidget(self.input_text)
        input_layout.addWidget(self.btn_save)

        self.input_container.hide()
        self.layout.addWidget(self.input_container)

        # ---------- NOTES LIST ----------
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
        while self.notes_container.count():
            w = self.notes_container.takeAt(0).widget()
            if w:
                w.deleteLater()

        data = load_notes()
        notes = data.get("notes", [])

        for n in reversed(notes):
            card = NoteCard(n["id"], n["title"], n["text"])
            card.clicked.connect(lambda c, note=n: self.open_note(note))
            self.notes_container.addWidget(card)

    def create_note(self):
        title = self.input_title.text().strip()
        text = self.input_text.toPlainText().strip()

        if not title:
            return

        data = load_notes()
        today = datetime.datetime.now().isoformat()

        new_note = {
            "id": max([n["id"] for n in data["notes"]] + [0]) + 1,
            "title": title,
            "text": text,
            "created_at": today
        }

        data["notes"].append(new_note)
        save_notes(data)

        self.input_title.clear()
        self.input_text.clear()
        self.toggle_add()
        self.load_all()

    def toggle_add(self):

        # Se já existe overlay, significa que está aberto → fechar
        if self.overlay:
            self.overlay.deleteLater()
            self.overlay = None

            self.anim.setDuration(220)
            self.anim.setStartValue(45)
            self.anim.setEndValue(0)
            self.anim.start()

            self.btn_add.setText("+")
            return

        # Se não está aberto → abrir
        self.anim.setDuration(220)
        self.anim.setStartValue(0)
        self.anim.setEndValue(45)
        self.anim.start()

        self.btn_add.setText("×")
        self.show_modal()


    def open_new_note(self):
        self.show_modal()

    def open_note(self, note_data):
        self.show_modal(note_data)

    def show_modal(self, note_data=None):

        self.overlay = QtWidgets.QWidget(self)
        self.overlay.setGeometry(self.rect())
        self.overlay.setStyleSheet("background-color: rgba(0, 0, 0, 180);")
        self.overlay.destroyed.connect(self._clear_overlay_reference)


        self.modal = NoteModal(note_data, parent=self.overlay)
        self.modal.setFixedSize(500, 600)

        m_x = (self.width() - self.modal.width()) // 2
        m_y = (self.height() - self.modal.height()) // 2
        self.modal.move(m_x, m_y)

        self.modal.note_saved.connect(self.load_all)
        self.modal.note_saved.connect(self.close_modal)

        def click_outside(event):
            if not self.modal:
                return

            modal_rect = self.modal.geometry()
            self.btn_add.setText("+")

            if not modal_rect.contains(event.pos()):
                self.modal.process_save(close_after=True)


        self.overlay.mousePressEvent = click_outside

        self.overlay.show()

    def _clear_overlay_reference(self):
            self.overlay = None

    def close_modal(self):
        if self.overlay:
            self.overlay.deleteLater()
            self.overlay = None

        self.anim.setDuration(220)
        self.anim.setStartValue(45)
        self.anim.setEndValue(0)
        self.anim.start()

        self.btn_add.setText("+")


    
