from PySide6 import QtCore, QtWidgets, QtGui

class Notification(QtWidgets.QWidget):
    def __init__(self, title, message, session_time=None, total_today=None, parent=None):
        super().__init__(parent)

        self.setWindowFlags(
            QtCore.Qt.FramelessWindowHint |
            QtCore.Qt.Tool |
            QtCore.Qt.WindowStaysOnTopHint |
            QtCore.Qt.WindowDoesNotAcceptFocus 
        )
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        
        self.setFixedWidth(320) 

        self.container = QtWidgets.QFrame(self)
        self.container.setObjectName("MainContainer")
        self.container.setStyleSheet("""
            #MainContainer {
                background-color: rgba(30, 30, 35, 240);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 20px;
            }
        """)
        
        shadow = QtWidgets.QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(30)
        shadow.setOffset(0, 12)
        shadow.setColor(QtGui.QColor(0, 0, 0, 150))
        self.container.setGraphicsEffect(shadow)

        layout = QtWidgets.QVBoxLayout(self.container)
        layout.setContentsMargins(22, 22, 22, 15)
        layout.setSpacing(10)

        header_layout = QtWidgets.QHBoxLayout()
        
        title_lbl = QtWidgets.QLabel(title.upper())
        title_lbl.setStyleSheet("""
            color: #8B5CF6; 
            font-size: 11px; 
            font-weight: 900; 
            letter-spacing: 1.5px;
        """)
        header_layout.addWidget(title_lbl)
        header_layout.addStretch()
        
        close_btn = QtWidgets.QPushButton("×")
        close_btn.setFixedSize(20, 20)
        close_btn.setCursor(QtCore.Qt.PointingHandCursor)
        close_btn.clicked.connect(self.fade_out)
        close_btn.setStyleSheet("color: #555; border: none; font-size: 18px; background: none;")
        header_layout.addWidget(close_btn)
        
        layout.addLayout(header_layout)

        msg_lbl = QtWidgets.QLabel(message)
        msg_lbl.setWordWrap(True)
        msg_lbl.setStyleSheet("color: #E2E2E7; font-size: 14px; font-weight: 400;")
        layout.addWidget(msg_lbl)

        layout.addSpacing(5)

        if session_time or total_today:
            stats_layout = QtWidgets.QHBoxLayout()
            stats_layout.setSpacing(6)

            if session_time:
                s_badge = QtWidgets.QLabel(f"● {session_time}")
                s_badge.setStyleSheet("color: #10B981; font-size: 11px; font-weight: 700;")
                stats_layout.addWidget(s_badge)

            if total_today:
                sep = QtWidgets.QLabel("|")
                sep.setStyleSheet("color: #333;")
                stats_layout.addWidget(sep)
                
                t_badge = QtWidgets.QLabel(f"{total_today} focado")
                t_badge.setStyleSheet("color: #71717A; font-size: 11px;")
                stats_layout.addWidget(t_badge)
            
            stats_layout.addStretch()
            layout.addLayout(stats_layout)

        self.prog_container = QtWidgets.QFrame()
        self.prog_container.setFixedHeight(3)
        self.prog_container.setStyleSheet("background: #2A2A2E; border-radius: 1px;")
        
        self.prog_bar = QtWidgets.QFrame(self.prog_container)
        self.prog_bar.setFixedHeight(3)
        self.prog_bar.setStyleSheet("""
            background: qlineargradient(x1:0, x2:1, stop:0 #8B5CF6, stop:1 #D8B4FE);
            border-radius: 1px;
        """)
        
        layout.addSpacing(10)
        layout.addWidget(self.prog_container)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.addWidget(self.container)

        self.adjustSize()
        self.reposition()
        self.setup_animations()

    def reposition(self):
        screen = QtWidgets.QApplication.primaryScreen().availableGeometry()
        self.move(screen.width() - self.width() - 20, screen.height() - self.height() - 20)

    def setup_animations(self):
        self.setWindowOpacity(0)
        self.fade_anim = QtCore.QPropertyAnimation(self, b"windowOpacity")
        self.fade_anim.setDuration(500)
        self.fade_anim.setStartValue(0)
        self.fade_anim.setEndValue(1)
        self.fade_anim.setEasingCurve(QtCore.QEasingCurve.OutQuart)
        self.fade_anim.start()

        self.bar_anim = QtCore.QPropertyAnimation(self.prog_bar, b"geometry")
        self.bar_anim.setDuration(5000)
        self.bar_anim.setStartValue(QtCore.QRect(0, 0, 0, 3))
        self.bar_anim.setEndValue(QtCore.QRect(0, 0, 276, 3))
        self.bar_anim.start()

        QtCore.QTimer.singleShot(5000, self.fade_out)

    def fade_out(self):
        self.fade_anim.setDirection(QtCore.QAbstractAnimation.Backward)
        self.fade_anim.finished.connect(self.close)
        self.fade_anim.start()