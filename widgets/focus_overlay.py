from PySide6 import QtCore, QtWidgets, QtGui

class FocusOverlay(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super().__init__(None) 
        self.setFixedSize(180, 50)
        self.setStyleSheet("""
            QFrame {
                background-color: #5E12F8;
                border-radius: 25px;
                color: white;
            }
        """)
        layout = QtWidgets.QHBoxLayout(self)
        self.label = QtWidgets.QLabel("00:00:00")
        self.label.setStyleSheet("font-weight: bold; font-size: 14px; border: none; background: transparent;")
        self.mode_label = QtWidgets.QLabel("FOCADO")
        self.mode_label.setStyleSheet("font-size: 9px; font-weight: 800; border: none; background: transparent; color: rgba(255,255,255,0.7);")
        
        layout.addStretch()
        v_box = QtWidgets.QVBoxLayout()
        v_box.setSpacing(0)
        v_box.addWidget(self.label, alignment=QtCore.Qt.AlignCenter)
        v_box.addWidget(self.mode_label, alignment=QtCore.Qt.AlignCenter)
        layout.addLayout(v_box)
        layout.addStretch()
        self.hide()

    def update_time(self, time_str):
        self.label.setText(time_str)