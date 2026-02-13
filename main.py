import sys
import ctypes
from PySide6 import QtCore, QtWidgets, QtGui
from data_manager import load_name, resource_path
from screens.mission_screen import MissionScreen
from screens.focus_screen import FocusScreen
from screens.home_screen import HomeScreen
from screens.notes_screen import NotesScreen
from widgets.focus_overlay import FocusOverlay
from screens.loading_screen import LoadingScreen
from screens.name_screen import NameScreen 
from screens.config_screen import ConfigScreen 

class SideMenu(QtWidgets.QFrame):
    clicked = QtCore.Signal(int)

    def __init__(self):
        super().__init__()
        self.setFixedWidth(220)
        self.setObjectName("SideMenu")

        self.setStyleSheet("""
        QFrame#SideMenu {
            background-color: #0e0b1c;
            border-right: 1px solid #2d234a;
        }

        QPushButton {
            text-align: left;
            padding-left: 15px;
            background: transparent;
            border: none;
            color: #a0a0a0;
            font-size: 13px;
        }

        QPushButton:hover {
            background: #1b1430;
            color: white;
            border-radius: 8px;
        }

        QPushButton:checked {
            background: #5E12F8;
            color: white;
            border-radius: 8px;
        }
        """)

        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(15, 40, 15, 20)
        self.main_layout.setSpacing(10)

        logo = QtWidgets.QLabel("MyTasks")
        logo.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #5E12F8;
            margin-bottom: 40px;
            margin-left: 20px;
            background: transparent;
        """)
        self.main_layout.addWidget(logo)

        self.buttons = []
        self.button_group = QtWidgets.QButtonGroup(self)
        self.button_group.setExclusive(True)

        menu_items = [
            ("INÍCIO", "images/icons/home.png", 0),
            ("MISSÕES", "images/icons/missions.png", 1),
            ("FOCO", "images/icons/focus.png", 2),
            ("ANOTAÇÕES", "images/icons/notes.png", 3),
            ("CONFIGURAÇÕES", "images/icons/settings.png", 4),
        ]

        for text, icon_path, index in menu_items:
            btn = QtWidgets.QPushButton(text)
            btn.setCheckable(True)
            btn.setFixedHeight(45)
            btn.setCursor(QtCore.Qt.PointingHandCursor)

            icon = QtGui.QIcon(resource_path(icon_path))
            btn.setIcon(icon)
            btn.setIconSize(QtCore.QSize(20, 20))

            btn.clicked.connect(lambda _, x=index: self.clicked.emit(x))

            self.button_group.addButton(btn)
            self.main_layout.addWidget(btn)
            self.buttons.append(btn)

        self.main_layout.addStretch()

        self.timer_widget = FocusOverlay()
        self.timer_widget.setVisible(False)
        self.main_layout.addWidget(self.timer_widget, alignment=QtCore.Qt.AlignCenter)

        if self.buttons:
            self.buttons[0].setChecked(True)


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
        self.screen_missions = MissionScreen(self)
        self.screen_missions.mission_completed.connect(
            self.screen_home.refresh
        )
        self.screen_focus = FocusScreen(self)
        self.screen_focus.foco_finalizado.connect(self.screen_home.refresh)
        self.screen_name = NameScreen(self) 
        self.screen_notes = NotesScreen(self) 
        self.screen_config = ConfigScreen(self)
        self.overlay = self.menu.timer_widget 
        self.screen_focus.time_updated.connect(self.manage_overlay)

        self.stack = QtWidgets.QStackedWidget()
        self.stack.addWidget(self.screen_name)    
        self.stack.addWidget(self.screen_home) 
        self.stack.addWidget(self.screen_missions) 
        self.stack.addWidget(self.screen_focus)    
        self.stack.addWidget(self.screen_notes)
        self.stack.addWidget(self.screen_config)
        layout.addWidget(self.stack)

        nome_salvo = load_name()
        if nome_salvo:
            self.menu.show()
            self.stack.setCurrentIndex(1) 
        else:
            self.menu.hide() 
            self.stack.setCurrentIndex(0) 

    def change(self, i):
        target_index = i + 1

        if target_index < self.stack.count():
            self.stack.setCurrentIndex(target_index)

            # Atualiza botão ativo
            if i < len(self.menu.buttons):
                self.menu.buttons[i].setChecked(True)

            if hasattr(self.screen_focus, "time_input"):
                self.manage_overlay(self.screen_focus.time_input.text())



    def manage_overlay(self, time_str):
        self.overlay.update_time(time_str)

        is_running = self.screen_focus.running
        on_focus_page = self.stack.currentIndex() == 3  

        if is_running and not on_focus_page:
            self.overlay.show()
        else:
            self.overlay.hide()


    def setup_connections(self):
        self.mission_screen.associate_requested.connect(self.handle_mission_association)

    def handle_mission_association(self, mission_id):
        self.focus_screen.set_associated_mission(mission_id)
        self.stack.setCurrentIndex(1)

    def set_focus_mission(self, mission_id):
        self.screen_focus.set_associated_mission(mission_id)
        self.stack.setCurrentIndex(3)  

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

    loading = LoadingScreen()
    window = MainWindow()

    def start_main():
        loading.close()
        window.show()

    loading.finished.connect(start_main)

    loading.show()

    sys.exit(app.exec())