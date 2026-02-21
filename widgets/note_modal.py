from PySide6 import QtCore, QtWidgets, QtGui
from data_manager import load_notes, save_notes
import datetime

class ConfirmDeletePopup(QtWidgets.QWidget):
    confirmed = QtCore.Signal()
    cancelled = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setGeometry(parent.rect())
        layout = QtWidgets.QGridLayout(self)
        
        self.bg = QtWidgets.QFrame()
        self.bg.setStyleSheet("background-color: rgba(0, 0, 0, 180); border-radius: 20px;")
        layout.addWidget(self.bg, 0, 0, 1, 1)

        self.card = QtWidgets.QFrame()
        self.card.setFixedSize(300, 160)
        self.card.setStyleSheet("""
            QFrame { background-color: #1e1b2e; border: 1px solid #e74c3c; border-radius: 15px; }
            QLabel { color: white; font-size: 14px; font-weight: bold; border: none; background: transparent; }
            QPushButton { padding: 10px; border-radius: 8px; font-weight: bold; font-size: 11px; }
            QPushButton#confirm { background-color: #e74c3c; color: white; }
            QPushButton#cancel { background-color: #322f50; color: rgba(255, 255, 255, 0.7); }
        """)
        
        card_layout = QtWidgets.QVBoxLayout(self.card)
        card_layout.setContentsMargins(20, 25, 20, 20)
        label = QtWidgets.QLabel("Deseja realmente apagar\nesta nota?")
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
class NoteModal(QtWidgets.QWidget):
    note_saved = QtCore.Signal()

    def __init__(self, note_data=None, parent=None):
        super().__init__(parent)
        self.note_data = note_data
        
        self.dark_palette = ["#1b1430", "#3d1c1c", "#1c3d26", "#1c2a3d", "#3d2e1c", "#2e1c3d"]
        
        self.current_color = note_data.get("color", self.dark_palette[0]) if note_data else self.dark_palette[0]
        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(35, 25, 35, 30)
        layout.setSpacing(15)

        toolbar = QtWidgets.QHBoxLayout()
        color_group = QtWidgets.QHBoxLayout()
        color_group.setSpacing(12)
        
        for color in self.dark_palette:
            btn = QtWidgets.QPushButton()
            btn.setFixedSize(22, 22)
            btn.setCursor(QtCore.Qt.PointingHandCursor)
            
            border = f"2px solid white" if color == self.current_color else "none"
            btn.setStyleSheet(f"background-color: {color}; border-radius: 11px; border: {border};")
            
            btn.clicked.connect(lambda checked, c=color: self.change_color(c))
            color_group.addWidget(btn)
        
        toolbar.addLayout(color_group)
        toolbar.addStretch()

        self.btn_delete = QtWidgets.QPushButton("EXCLUIR")
        self.btn_delete.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_delete.setFixedSize(70, 28)
        self.btn_delete.clicked.connect(self.ask_confirm_delete)
        if not self.note_data: self.btn_delete.hide()
        toolbar.addWidget(self.btn_delete)

        layout.addLayout(toolbar)

        self.input_title = QtWidgets.QLineEdit()
        self.input_title.setPlaceholderText("Título da Nota...")
        self.input_text = QtWidgets.QTextEdit()
        self.input_text.setPlaceholderText("Escreva aqui suas ideias...")
        
        line_height = 35.0 
        cursor = self.input_text.textCursor()
        block_format = cursor.blockFormat()
        block_format.setLineHeight(line_height, QtGui.QTextBlockFormat.LineHeightTypes.FixedHeight.value)
        cursor.setBlockFormat(block_format)
        self.input_text.setTextCursor(cursor)

        footer_layout = QtWidgets.QHBoxLayout()
        self.btn_save = QtWidgets.QPushButton("SALVAR NOTA")
        self.btn_save.setFixedSize(160, 45)
        self.btn_save.setCursor(QtCore.Qt.PointingHandCursor)
        footer_layout.addStretch()
        footer_layout.addWidget(self.btn_save)

        layout.addWidget(self.input_title)
        layout.addWidget(self.input_text)
        layout.addLayout(footer_layout)

        self.update_appearance()

        if self.note_data:
            self.input_title.setText(self.note_data.get("title", ""))
            self.input_text.setText(self.note_data.get("text", ""))

        self.btn_save.clicked.connect(lambda: self.process_save(close_after=True))
        
        self.autosave_timer = QtCore.QTimer(self)
        self.autosave_timer.setSingleShot(True)
        self.autosave_timer.timeout.connect(self.save_note_silent)
        self.input_title.textChanged.connect(lambda: self.autosave_timer.start(2000))
        self.input_text.textChanged.connect(lambda: self.autosave_timer.start(2000))

    def change_color(self, color):
        self.current_color = color
        self.update_appearance()
        
        for i in range(self.layout().itemAt(0).layout().itemAt(0).layout().count()):
            btn = self.layout().itemAt(0).layout().itemAt(0).layout().itemAt(i).widget()
            c = self.dark_palette[i]
            border = "2px solid white" if c == color else "none"
            btn.setStyleSheet(f"background-color: {c}; border-radius: 11px; border: {border};")
            
        self.save_note_silent()

    def update_appearance(self):
        self.setStyleSheet(f"""
            NoteModal {{ 
                background-color: {self.current_color}; 
                border: 1px solid #322f50; 
                border-radius: 20px; 
            }}
            QLineEdit {{
                background: transparent; border: none; font-size: 24px; font-weight: 700;
                color: #FFFFFF; border-bottom: 2px solid rgba(255,255,255, 0.05); padding-bottom: 8px;
            }}
            QTextEdit {{
                background-color: transparent; border: none; font-size: 16px; color: #E0E0E0;
                background-image: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0.96 transparent, stop:0.97 rgba(255,255,255,0.03));
                background-attachment: fixed;
            }}
            QPushButton {{ background-color: #5E12F8; color: white; border-radius: 10px; font-weight: 800; }}
            QPushButton:hover {{ background-color: #7227ff; }}
        """)
        
        self.btn_delete.setStyleSheet("""
            QPushButton {
                background-color: rgba(231, 76, 60, 0.1);
                color: #e74c3c; border: 1px solid rgba(231, 76, 60, 0.3);
                border-radius: 6px; font-size: 10px; font-weight: bold;
            }
            QPushButton:hover { background-color: #e74c3c; color: white; }
        """)

    def ask_confirm_delete(self):
        self.popup = ConfirmDeletePopup(self)
        self.popup.show()
        self.popup.cancelled.connect(self.popup.deleteLater)
        self.popup.confirmed.connect(self.handle_delete)

    def handle_delete(self):
        data = load_notes()
        data["notes"] = [n for n in data["notes"] if n["id"] != self.note_data["id"]]
        save_notes(data)
        self.popup.deleteLater()
        self.note_saved.emit()
        self.close_modal()

    def save_note_silent(self):
        self.process_save(close_after=False)

    def process_save(self, close_after=True):
        title, text = self.input_title.text().strip(), self.input_text.toPlainText().strip()
        if not title and not text:
            if close_after: self.close_modal()
            return
        if not title: title = f"Nota {datetime.datetime.now().strftime('%H:%M')}"
        data = load_notes()
        if self.note_data:
            for n in data["notes"]:
                if n["id"] == self.note_data["id"]:
                    n.update({"title": title, "text": text, "color": self.current_color})
                    break
        else:
            new_id = max([n["id"] for n in data["notes"]] + [0]) + 1
            self.note_data = {"id": new_id, "title": title, "text": text, "color": self.current_color, "created_at": datetime.datetime.now().isoformat()}
            data["notes"].append(self.note_data)
        save_notes(data)
        if close_after:
            self.note_saved.emit()
            self.close_modal()

    def close_modal(self):
        if self.parent(): self.parent().deleteLater()