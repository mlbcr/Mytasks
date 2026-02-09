from PySide6 import QtCore, QtWidgets, QtGui

class RotatableButton(QtWidgets.QPushButton):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self._rotation = 0

    def getRotation(self): return self._rotation
    def setRotation(self, value):
        self._rotation = value
        self.update()

    rotation = QtCore.Property(float, getRotation, setRotation)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        rect = self.rect()
        painter.translate(rect.center())
        painter.rotate(self._rotation)
        painter.translate(-rect.center())
        super().paintEvent(event)