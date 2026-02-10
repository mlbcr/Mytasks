from PySide6 import QtCore, QtWidgets, QtGui

class RotatableButton(QtWidgets.QPushButton):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self._rotation = 0

        self.hover_anim = QtCore.QPropertyAnimation(self, b"rotation")
        self.hover_anim.setDuration(160)
        self.hover_anim.setEasingCurve(QtCore.QEasingCurve.OutCubic)

    def getRotation(self):
        return self._rotation

    def setRotation(self, value):
        self._rotation = value
        self.update()

    rotation = QtCore.Property(float, getRotation, setRotation)

    def enterEvent(self, event):
        if not self.isDown():
            self.hover_anim.stop()
            self.hover_anim.setStartValue(self._rotation)
            self.hover_anim.setEndValue(15)  # 👈 ameaça
            self.hover_anim.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        if not self.isDown():
            self.hover_anim.stop()
            self.hover_anim.setStartValue(self._rotation)
            self.hover_anim.setEndValue(0)
            self.hover_anim.start()
        super().leaveEvent(event)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        rect = self.rect()
        painter.translate(rect.center())
        painter.rotate(self._rotation)
        painter.translate(-rect.center())

        super().paintEvent(event)
