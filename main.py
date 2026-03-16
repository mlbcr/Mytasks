import os, sys, winreg
import ctypes
from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtWidgets import QSystemTrayIcon, QMenu
from data_manager import load_name, resource_path
from screens.mission_screen import MissionScreen
from screens.focus_screen import FocusScreen
from screens.home_screen import HomeScreen
from screens.notes_screen import NotesScreen
from widgets.focus_overlay import FocusOverlay
from screens.loading_screen import LoadingScreen
from screens.planner_screen import PlannerScreen
from screens.name_screen import NameScreen 
from screens.config_screen import ConfigScreen 
from data_manager import load_user
from progression import xp_needed_for_level, get_rank


DEV_MODE = True


def white_standard_icon(widget, standard_icon, size=14):
    icon = widget.style().standardIcon(standard_icon)
    pix = icon.pixmap(size, size)

    result = QtGui.QPixmap(pix.size())
    result.fill(QtCore.Qt.transparent)

    painter = QtGui.QPainter(result)
    painter.drawPixmap(0, 0, pix)
    painter.setCompositionMode(QtGui.QPainter.CompositionMode_SourceIn)
    painter.fillRect(result.rect(), QtGui.QColor("#dcd6ff"))
    painter.end()

    return QtGui.QIcon(result)

class TitleBar(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setFixedHeight(46)

        self.setObjectName("TitleBar")

        self.setStyleSheet("""
        QFrame#TitleBar {
            background: qlineargradient(
                x1:0, y1:0, x2:0, y2:1,
                stop:0 #1b1433,
                stop:1 #120d25
            );
            border-bottom: 1px solid #2d234a;
        }

        QLabel#AppTitle {
            font-size: 14px;
            font-weight: 600;
            color: #e8e6ff;
            padding-left: 6px;
        }

        QPushButton {
            border: none;
            background: transparent;
            width: 36px;
            height: 28px;
            border-radius: 6px;
        }

        QPushButton:hover {
            background: rgba(255,255,255,0.08);
        }

        QPushButton#close:hover {
            background: #e81123;
        }
        """)

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 8, 0)

        icon = QtWidgets.QLabel()
        icon.setPixmap(
            QtGui.QPixmap(resource_path("images/icone.ico")).scaled(
                18, 18,
                QtCore.Qt.KeepAspectRatio,
                QtCore.Qt.SmoothTransformation
            )
        )
        icon.setStyleSheet("background: transparent;")
        layout.addWidget(icon)


        title = QtWidgets.QLabel("LevelUp")
        title.setObjectName("AppTitle")
        title.setStyleSheet("background: transparent;")
        layout.addWidget(title)

        layout.addStretch()

        # botões
        self.btn_min = QtWidgets.QPushButton()
        self.btn_max = QtWidgets.QPushButton()
        self.btn_close = QtWidgets.QPushButton()
        self.btn_close.setObjectName("close")

        self.btn_min.setIcon(white_standard_icon(self, QtWidgets.QStyle.SP_TitleBarMinButton))
        self.btn_max.setIcon(white_standard_icon(self, QtWidgets.QStyle.SP_TitleBarMaxButton))
        self.btn_close.setIcon(white_standard_icon(self, QtWidgets.QStyle.SP_TitleBarCloseButton))

        self.btn_min.setIconSize(QtCore.QSize(14,14))
        self.btn_max.setIconSize(QtCore.QSize(14,14))
        self.btn_close.setIconSize(QtCore.QSize(14,14))

        layout.addWidget(self.btn_min)
        layout.addWidget(self.btn_max)
        layout.addWidget(self.btn_close)

        self.btn_min.clicked.connect(self.parent.showMinimized)
        self.btn_max.clicked.connect(self.toggle_max_restore)
        self.btn_close.clicked.connect(self.parent.close)

        self.old_pos = None

    def toggle_max_restore(self):
        if self.parent.isMaximized():
            self.parent.showNormal()
            self.btn_max.setIcon(
                self.style().standardIcon(QtWidgets.QStyle.SP_TitleBarMaxButton)
            )
        else:
            self.parent.showMaximized()
            self.btn_max.setIcon(
                self.style().standardIcon(QtWidgets.QStyle.SP_TitleBarNormalButton)
            )

    # arrastar janela
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.old_pos:
            delta = event.globalPosition().toPoint() - self.old_pos
            self.parent.move(self.parent.pos() + delta)
            self.old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self.old_pos = None

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

        # 1. Logo
        logo = QtWidgets.QLabel("LevelUp")
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
            ("PLANNER", "images/icons/planner.png", 2),
            ("FOCO", "images/icons/focus.png", 3),
            ("ANOTAÇÕES", "images/icons/notes.png", 4),
            ("CONFIGURAÇÕES", "images/icons/settings.png", 5),
        ]

        for text, icon_path, index in menu_items:
            btn = QtWidgets.QPushButton(text)
            btn.setCheckable(True)
            btn.setFixedHeight(45)
            btn.setCursor(QtCore.Qt.PointingHandCursor)
            btn.setIcon(QtGui.QIcon(resource_path(icon_path)))
            btn.setIconSize(QtCore.QSize(18, 18))
            btn.clicked.connect(lambda _, x=index: self.clicked.emit(x))

            self.button_group.addButton(btn)
            self.main_layout.addWidget(btn)
            self.buttons.append(btn)


        self.profile_box = QtWidgets.QFrame()
        self.profile_box.setStyleSheet("""
            QFrame {
                background: #141028;
                border-radius: 14px;
            }
        """)
        
        self.main_layout.addStretch(2)
        self.main_layout.addSpacing(20)
        self.main_layout.addWidget(self.profile_box)
        self.main_layout.addStretch(1)

        profile_main_layout = QtWidgets.QHBoxLayout(self.profile_box)
        profile_main_layout.setContentsMargins(10, 10, 10, 10)
        profile_main_layout.setSpacing(12)

        self.avatar_label = QtWidgets.QLabel()
        self.avatar_label.setFixedSize(42, 42)

        avatar_pix = QtGui.QPixmap(resource_path("images/profile.jpg"))
        if not avatar_pix.isNull():
            avatar_pix = avatar_pix.scaled(
                42, 42,
                QtCore.Qt.KeepAspectRatioByExpanding,
                QtCore.Qt.SmoothTransformation
            )
            self.avatar_label.setPixmap(avatar_pix)

        self.avatar_label.setStyleSheet("""
            QLabel {
                border-radius: 21px;
                background: #120d25;
            }
        """)
                
        profile_main_layout.addWidget(self.avatar_label)

        text_layout = QtWidgets.QVBoxLayout()
        text_layout.setSpacing(2)

        self.name_label = QtWidgets.QLabel("Mary")
        self.name_label.setStyleSheet("""
            font-size:13px;
            font-weight:600;
            color:white;
            background:transparent;
        """)
        self.level_label = QtWidgets.QLabel("Level 9")
        self.level_label.setStyleSheet("color:#bdb6ff; font-size:11px; background: transparent;")

        self.xp_bar = QtWidgets.QProgressBar()
        self.xp_bar.setFixedHeight(6)
        self.xp_bar.setTextVisible(False)
        self.xp_bar.setStyleSheet("""
            QProgressBar { background-color: #120d25; border-radius: 3px; border: none; }
            QProgressBar::chunk { 
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #5E12F8, stop:1 #A277FF);
                border-radius: 3px; 
            }
        """)

        self.rank_label = QtWidgets.QLabel("Rank D")
        self.rank_label.setStyleSheet("color:#888; font-size:10px; background: transparent;")

        text_layout.addWidget(self.name_label)
        lvl_row = QtWidgets.QHBoxLayout()
        lvl_row.setSpacing(6)
        lvl_row.addWidget(self.level_label)
        lvl_row.addStretch()
        lvl_row.addWidget(self.rank_label)

        text_layout.addLayout(lvl_row)
        text_layout.addWidget(self.xp_bar)
        
        profile_main_layout.addLayout(text_layout)
        
        self.timer_widget = FocusOverlay()
        self.timer_widget.setVisible(False)
        self.main_layout.addWidget(self.timer_widget, alignment=QtCore.Qt.AlignCenter)

        if self.buttons:
            self.buttons[0].setChecked(True)

    def refresh_profile(self):
        try:
            data = load_user()
            if not data or "usuario" not in data:
                return
            u = data["usuario"]
            self.name_label.setText(u.get("nome", "Player"))
            self.level_label.setText(f"Level {u.get('nivel', 1)}")
            self.rank_label.setText(f"Rank {get_rank(u.get('nivel', 1))}")
            xp_needed = xp_needed_for_level(u.get("nivel", 1))
            self.xp_bar.setMaximum(xp_needed)
            self.xp_bar.setValue(u.get("xp", 0))
        except Exception as e:
            print("Erro ao atualizar perfil:", e)


class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, False)

        self.setWindowTitle("LevelUp")
        
        self.normal_size = QtCore.QSize(1100, 850) 
        self.resize(self.normal_size)
        self.setStyleSheet("background-color: #161025; color: white; font-family: 'Segoe UI';")
        
        root_layout = QtWidgets.QVBoxLayout(self)
        root_layout.setContentsMargins(0,0,0,0)
        root_layout.setSpacing(0)

        self.titlebar = TitleBar(self)
        root_layout.addWidget(self.titlebar)

        content = QtWidgets.QHBoxLayout()
        content.setContentsMargins(0,0,0,0)
        content.setSpacing(0)

        root_layout.addLayout(content)
        
        self.menu = SideMenu()
        self.menu.clicked.connect(self.change)
        
        content.addWidget(self.menu)
        
        self.screen_home = HomeScreen()
        self.screen_missions = MissionScreen(self)
        self.screen_missions.mission_completed.connect(
            self.screen_home.refresh
        )
        self.screen_planner = PlannerScreen(self)
        self.screen_focus = FocusScreen(self)
        self.screen_focus.foco_finalizado.connect(self.screen_home.refresh)
        self.screen_name = NameScreen(self) 
        self.screen_notes = NotesScreen(self) 
        self.screen_config = ConfigScreen(self)
        self.overlay = self.menu.timer_widget 
        self.screen_focus.time_updated.connect(self.manage_overlay)
        self.screen_missions.mission_completed.connect(self.screen_planner.load_all)


        self.stack = QtWidgets.QStackedWidget()
        self.stack.addWidget(self.screen_name)    
        self.stack.addWidget(self.screen_home) 
        self.stack.addWidget(self.screen_missions) 
        self.stack.addWidget(self.screen_planner)
        self.stack.addWidget(self.screen_focus)    
        self.stack.addWidget(self.screen_notes)
        self.stack.addWidget(self.screen_config)
        content.addWidget(self.stack)

        nome_salvo = load_name()
        if nome_salvo:
            self.menu.show()
            self.stack.setCurrentIndex(1) 
        else:
            self.menu.hide() 
            self.stack.setCurrentIndex(0) 
        
        self.tray = QSystemTrayIcon(self)
        self.tray.setIcon(QtGui.QIcon(resource_path("images/icone.ico")))

        menu = QMenu()
        abrir = menu.addAction("Abrir LevelUp")
        sair = menu.addAction("Sair")

        abrir.triggered.connect(self.show_window)
        sair.triggered.connect(QtWidgets.QApplication.quit)

        self.tray.setContextMenu(menu)
        self.tray.activated.connect(self.tray_clicked)

        self.tray.show()

    def change(self, i):
        target_index = i + 1

        if target_index < self.stack.count():

            if target_index == 1:
                self.screen_home.refresh()

            self.stack.setCurrentIndex(target_index)

            if i < len(self.menu.buttons):
                self.menu.buttons[i].setChecked(True)

            if hasattr(self.screen_focus, "time_input"):
                self.manage_overlay(self.screen_focus.time_input.text())

    def tray_clicked(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            self.show_window()

    def show_window(self):
        self.show()
        self.raise_()
        self.activateWindow()

    def closeEvent(self, event):
        if DEV_MODE:
            event.accept()   # fecha direto (modo dev)
            return

        event.ignore()
        self.hide()
        self.tray.showMessage(
            "LevelUp",
            "O app continua rodando em segundo plano.",
            QSystemTrayIcon.Information,
            2000
        )

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

def add_to_startup():
    if getattr(sys, 'frozen', False):
        exe = sys.executable
    else:
        exe = os.path.abspath(sys.argv[0])

    key = winreg.OpenKey(
        winreg.HKEY_CURRENT_USER,
        r"Software\Microsoft\Windows\CurrentVersion\Run",
        0,
        winreg.KEY_SET_VALUE
    )

    winreg.SetValueEx(key, "LevelUp", 0, winreg.REG_SZ, exe)
    winreg.CloseKey(key)

if __name__ == "__main__":
    try: ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("mytasks.app")
    except: pass
    app = QtWidgets.QApplication(sys.argv)
    # add_to_startup()

    app_icon = QtGui.QIcon(resource_path("images/icone.ico"))
    app.setWindowIcon(app_icon)

    loading = LoadingScreen()
    window = MainWindow()

    def start_main():
        loading.close()

        window.screen_home.refresh()
        window.screen_missions.load_all()
        window.screen_planner.load_all()
        window.menu.refresh_profile()

        window.show() 

    loading.finished.connect(start_main)

    loading.show()

    sys.exit(app.exec())