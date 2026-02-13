from PySide6 import QtCore, QtWidgets, QtGui
from data_manager import load_notes, save_notes
import datetime

class NoteModal(QtWidgets.QWidget):
    note_saved = QtCore.Signal()

    def __init__(self, note_data=None, parent=None):
        super().__init__(parent)
        self.note_data = note_data
        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        
        # Layout principal
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 30) # Aumentei as margens internas
        layout.setSpacing(20)

        # Título estilo caderno (Sem margem esquerda agora)
        self.input_title = QtWidgets.QLineEdit()
        self.input_title.setPlaceholderText("Título da Nota...")

        # Área de texto com as linhas
        self.input_text = QtWidgets.QTextEdit()
        self.input_text.setPlaceholderText("Escreva aqui suas ideias...")
        
        # --- CONFIGURAÇÃO DA PAUTA (ESPAÇAMENTO) ---
        # Aumentei um pouco a altura para 35px para ficar mais confortável no modal maior
        line_height = 35.0 
        cursor = self.input_text.textCursor()
        block_format = cursor.blockFormat()
        block_format.setLineHeight(line_height, QtGui.QTextBlockFormat.LineHeightTypes.FixedHeight.value)
        cursor.setBlockFormat(block_format)
        self.input_text.setTextCursor(cursor)

        self.btn_save = QtWidgets.QPushButton("SALVAR NOTA")
        self.btn_save.setFixedSize(160, 50)
        self.btn_save.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_save.clicked.connect(lambda: self.process_save(close_after=True))

        layout.addWidget(self.input_title)
        layout.addWidget(self.input_text)
        layout.addWidget(self.btn_save, 0, QtCore.Qt.AlignRight)

        # Aplicar o CSS atualizado
        self.setStyleSheet(f"""
            NoteModal {{
                background-color: #2b1f4a;
                border: 2px solid #5E12F8;
                border-radius: 25px;
            }}
            QLineEdit {{
                background: transparent;
                border: none;
                border-bottom: 2px solid rgba(94, 18, 248, 0.3);
                font-size: 28px;
                font-weight: bold;
                color: #FFFFFF;
                padding-bottom: 10px;
            }}
            QTextEdit {{
                background-color: transparent;
                /* Gradiente que cria apenas a linha horizontal no fundo */
                background-image: qlineargradient(
                    spread:pad, x1:0, y1:0, x2:0, y2:1, 
                    stop:0.96 transparent, 
                    stop:0.97 rgba(255, 255, 255, 0.15)
                );
                background-attachment: fixed;
                
                border: none;
                padding: 0px;
                font-size: 18px;
                color: #E0E0E0;
            }}
            QPushButton {{
                background-color: #5E12F8;
                color: white;
                border-radius: 15px;
                font-size: 15px;
                font-weight: bold;
                letter-spacing: 1px;
            }}
            QPushButton:hover {{
                background-color: #7B2FF7;
            }}
        """)

        if note_data:
            self.input_title.setText(note_data["title"])
            self.input_text.setText(note_data["text"])

        self.autosave_timer = QtCore.QTimer(self)
        self.autosave_timer.setSingleShot(True)
        self.autosave_timer.timeout.connect(self.save_note_silent)
        
        self.input_title.textChanged.connect(lambda: self.autosave_timer.start(2000))
        self.input_text.textChanged.connect(lambda: self.autosave_timer.start(2000))
    
    def save_note_silent(self):
        """Salva a nota sem fechar o modal"""
        self.process_save(close_after=False)

    def process_save(self, close_after=True):
        title = self.input_title.text().strip()
        text = self.input_text.toPlainText().strip()
        
        if not title and not text:
            if close_after: self.close_modal()
            return

        if not title:
            title = f"Rascunho {datetime.datetime.now().strftime('%H:%M')}"

        data = load_notes()
        
        if self.note_data:
            for n in data["notes"]:
                if n["id"] == self.note_data["id"]:
                    n["title"], n["text"] = title, text
                    break
        else:
            new_id = max([n["id"] for n in data["notes"]] + [0]) + 1
            self.note_data = {
                "id": new_id,
                "title": title,
                "text": text,
                "created_at": datetime.datetime.now().isoformat()
            }
            data["notes"].append(self.note_data)

        save_notes(data)

        if close_after:
            self.note_saved.emit()
            self.close_modal()

    def close_modal(self):
        if self.parent():
            self.parent().deleteLater()