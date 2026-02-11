import random
from PySide6 import QtCore, QtWidgets, QtGui
from data_manager import resource_path

FRASES = [
    "Nem todo progresso é visível. Continue mesmo assim.",
    "Cada pequeno passo é um lembrete de que você importa e merece isso.",
    "Você está se tornando a pessoa que o seu eu do passado sempre esperou que você se tornasse.",
    "Motivação te ajuda a começar, consistência te permite continuar.",
    "Um foco de cada vez.",
    "Seu futuro agradece pelo esforço de agora.",
    "Progresso, não perfeição.",
    "Parabéns por se dedicar a si mesmo hoje.",
    "Recomeçar também é progresso.",
    "Continue.",
    "Fracasso não cancela evolução.",
    "Respire fundo e aproveite o que este dia traz.",
    "Você está se tornando a pessoa que o seu eu do passado sempre quis se tornar.",
    "Você não precisa ser perfeito, apenas continue tentando.",
    "Que bom te ver de volta, cada dia conta.",
    "Você está presente hoje, e isso importa mais do que imagina.",
    "Sorria, hoje é um novo dia. :)",
    "O passado é história, o futuro é mistério, o agora é uma dádiva e por isso se chama presente.",
    "O dia de hoje jamais voltará, aproveite.",
    "Você voltou! Isso já é um grande progresso.",
]


class LoadingScreen(QtWidgets.QWidget):
    finished = QtCore.Signal()

    def __init__(self):
        super().__init__()

        self.setFixedSize(600, 350)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setStyleSheet("""
            background-color: #161025;
            color: white;
            font-family: 'Segoe UI';
        """)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setAlignment(QtCore.Qt.AlignCenter)
        layout.setSpacing(25)

        title = QtWidgets.QLabel("MyTasks")
        title.setStyleSheet("""
            font-size: 32px;
            font-weight: bold;
            color: #5E12F8;
        """)
        title.setAlignment(QtCore.Qt.AlignCenter)

        self.label_phrase = QtWidgets.QLabel(random.choice(FRASES))
        self.label_phrase.setWordWrap(True)
        self.label_phrase.setAlignment(QtCore.Qt.AlignCenter)
        self.label_phrase.setStyleSheet("""
            font-size: 16px;
            color: rgba(255,255,255,0.7);
            padding: 0 40px;
        """)

        self.progress = QtWidgets.QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(6)
        self.progress.setStyleSheet("""
            QProgressBar {
                background-color: #1b1430;
                border-radius: 3px;
            }
            QProgressBar::chunk {
                background-color: #5E12F8;
                border-radius: 3px;
            }
        """)

        layout.addStretch()
        layout.addWidget(title)
        layout.addWidget(self.label_phrase)
        layout.addWidget(self.progress)
        layout.addStretch()

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(40)

        self.value = 0

    def update_progress(self):
        self.value += 1
        self.progress.setValue(self.value)

        if self.value >= 100:
            self.timer.stop()
            self.finished.emit()
