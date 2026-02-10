import sys
import ctypes
from PySide6 import QtCore, QtWidgets, QtGui
from data_manager import load_name, resource_path
from screens.mission_screen import MissionScreen
from screens.focus_screen import FocusScreen
from screens.home_screen import HomeScreen
from widgets.focus_overlay import FocusOverlay

class SideMenu(QtWidgets.QFrame):
    clicked = QtCore.Signal(int)
    def __init__(self):
        super().__init__()
        self.setFixedWidth(200)
        self.setStyleSheet("background-color: #0e0b1c; border-right: 1px solid #2d234a;")
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 40, 10, 20)
        logo = QtWidgets.QLabel("MyTasks")
        logo.setStyleSheet("font-size: 18px; font-weight: bold; color: #5E12F8; margin-bottom: 40px;")
        btns = [("Início", 0), ("Missões", 1), ("Foco", 2), ("Configurações", 3)]
        for t, i in btns:
            b = QtWidgets.QPushButton(t)
            b.setFixedHeight(45)
            b.setCursor(QtCore.Qt.PointingHandCursor)
            b.setStyleSheet("QPushButton { text-align: left; padding-left: 15px; background: transparent; border: none; color: #a0a0a0; } QPushButton:hover { color: white; background: #1b1430; border-radius: 8px; }")
            b.clicked.connect(lambda _, x=i: self.clicked.emit(x))
            self.main_layout.addWidget(b)
        
        self.main_layout.addStretch()
        self.timer_widget = FocusOverlay()
        self.timer_widget.setVisible(False)
        self.main_layout.addWidget(self.timer_widget, alignment=QtCore.Qt.AlignCenter)

from screens.name_screen import NameScreen 

class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MyTasks")
        
        self.normal_size = QtCore.QSize(1100, 850) 
        self.resize(self.normal_size)
        self.setStyleSheet("background-color: #161025; color: white; font-family: 'Segoe UI';")
        
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        self.menu = SideMenu()
        self.menu.clicked.connect(self.change)
        layout.addWidget(self.menu)
        
        self.screen_home = HomeScreen()
        self.screen_missions = MissionScreen()
        self.screen_focus = FocusScreen()
        self.screen_name = NameScreen(self) 
        
        self.overlay = self.menu.timer_widget 
        self.screen_focus.time_updated.connect(self.manage_overlay)

        self.stack = QtWidgets.QStackedWidget()
        self.stack.addWidget(self.screen_name)    
        self.stack.addWidget(self.screen_home) 
        self.stack.addWidget(self.screen_missions) 
        self.stack.addWidget(self.screen_focus)    

        layout.addWidget(self.stack)

        nome_salvo = load_name()
        if nome_salvo:
            self.menu.show()
            self.stack.setCurrentIndex(1) 
        else:
            self.menu.hide() 
            self.stack.setCurrentIndex(0) 

    def change(self, i):
        target = i + 1
        if target < self.stack.count(): 
            self.stack.setCurrentIndex(target)
            self.manage_overlay(self.screen_focus.time_input.text())

    def manage_overlay(self, time_str):
        self.overlay.update_time(time_str)

        is_running = self.screen_focus.running
        on_focus_page = self.stack.currentIndex() == 2 

        if is_running and not on_focus_page:
            self.overlay.show()
        else:
            self.overlay.hide()


    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.overlay.isVisible():
            self.overlay.move(self.width() - 180, self.height() - 70)

if __name__ == "__main__":
    try: ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("mytasks.app")
    except: pass
    app = QtWidgets.QApplication(sys.argv)


    app_icon = QtGui.QIcon(resource_path("images/icone.ico"))
    app.setWindowIcon(app_icon)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())