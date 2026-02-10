from PySide6 import QtCore, QtWidgets, QtGui
import datetime
import json
import os
from data_manager import (
    load_missions, load_name, load_focus_history, 
    DATA_FILE 
)

CATEGORIAS = {
    "INTELIGÊNCIA": "#f1c40f", "FORÇA": "#e74c3c",
    "VITALIDADE": "#2ecc71", "CRIATIVIDADE": "#3498db", "SOCIAL": "#95a5a6"
}

def format_seconds(s):
    hrs = s // 3600
    mins = (s % 3600) // 60
    return f"{int(hrs)}h {int(mins)}min"

class HomeCard(QtWidgets.QFrame):
    def __init__(self, title_text):
        super().__init__()
        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        self.setStyleSheet("""
            QFrame {
                background-color: #1b1430;
                border: 1px solid #2d234a;
                border-radius: 14px;
            }
            QLabel { background: transparent; border: none; color: white; }
        """)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(16, 16, 16, 16)
        self.layout.setSpacing(0)

        self.title_label = QtWidgets.QLabel(title_text.upper())
        self.title_label.setStyleSheet("""
            color: rgba(255,255,255,0.55);
            font-size: 10px;
            font-weight: bold;
            letter-spacing: 1px;
            margin-bottom: 4px;
        """)

        underline = QtWidgets.QFrame()
        underline.setFixedHeight(2)
        underline.setFixedWidth(22)
        underline.setStyleSheet("background-color: #5E12F8; border-radius: 1px; border: none;")

        self.layout.addWidget(self.title_label)
        self.layout.addWidget(underline)
        self.layout.addSpacing(15)

        self.body_widget = QtWidgets.QWidget()
        self.body = QtWidgets.QVBoxLayout(self.body_widget)
        self.body.setContentsMargins(0, 0, 0, 0)
        self.body.setSpacing(10)
        
        self.layout.addWidget(self.body_widget)
        self.layout.addStretch()

class StatsCard(QtWidgets.QFrame):
    def __init__(self):
        super().__init__()
        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        self.setStyleSheet("""
            QFrame { background-color: #1b1430; border: 1px solid #2d234a; border-radius: 14px; }
            QLabel { background: transparent; border: none; color: white; }
        """)
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15)

        title = QtWidgets.QLabel("ESTATÍSTICAS")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet("font-size: 12px; font-weight: bold; color: rgba(255,255,255,0.7);")
        self.layout.addWidget(title)

        self.lbl_foco_hoje = QtWidgets.QLabel("TEMPO HOJE: 0h 0min")
        self.lbl_foco_total = QtWidgets.QLabel("TEMPO TOTAL: 0h 0min")
        self.lbl_foco_hoje.setStyleSheet("font-size: 13px; font-weight: bold;")
        self.lbl_foco_total.setStyleSheet("color: rgba(255,255,255,0.5); font-size: 11px;")
        
        self.layout.addWidget(self.lbl_foco_hoje)
        self.layout.addWidget(self.lbl_foco_total)

        self.chart_widget = QtWidgets.QWidget()
        self.chart_widget.setMinimumHeight(160)
        self.chart_layout = QtWidgets.QHBoxLayout(self.chart_widget)
        self.chart_layout.setContentsMargins(0, 0, 0, 0)
        self.chart_layout.setSpacing(8)
        self.chart_layout.setAlignment(QtCore.Qt.AlignBottom)
        
        self.layout.addWidget(self.chart_widget)

        days_layout = QtWidgets.QHBoxLayout()
        for d in ["SEG", "TER", "QUA", "QUI", "SEX", "SAB", "DOM"]:
            lbl = QtWidgets.QLabel(d)
            lbl.setAlignment(QtCore.Qt.AlignCenter)
            lbl.setStyleSheet("font-size: 9px; color: rgba(255,255,255,0.4);")
            days_layout.addWidget(lbl)
        self.layout.addLayout(days_layout)

        self.layout.addSpacing(10)
        self.lbl_rank = QtWidgets.QLabel("RANK E")
        self.lbl_rank.setStyleSheet("font-weight: bold; color: #5E12F8;")
        self.layout.addWidget(self.lbl_rank)

        self.xp_bar = QtWidgets.QProgressBar()
        self.xp_bar.setFixedHeight(8)
        self.xp_bar.setTextVisible(False)
        self.xp_bar.setStyleSheet("""
            QProgressBar { background-color: #2d234a; border-radius: 4px; border: none; }
            QProgressBar::chunk { background-color: #5E12F8; border-radius: 4px; }
        """)
        self.layout.addWidget(self.xp_bar)

        self.lbl_xp_info = QtWidgets.QLabel("NÍVEL 1 • 0/100 XP")
        self.lbl_xp_info.setStyleSheet("font-size: 10px; color: rgba(255,255,255,0.4);")
        self.layout.addWidget(self.lbl_xp_info)

        self.refresh_data()

    def refresh_data(self):
        history = load_focus_history()
        today_date = datetime.date.today()
        
        while self.chart_layout.count():
            item = self.chart_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        total_acumulado = sum(d.get("total_seconds", 0) for d in history.values())
        hoje_segundos = history.get(today_date.isoformat(), {}).get("total_seconds", 0)
        
        self.lbl_foco_hoje.setText(f"TEMPO HOJE: {format_seconds(hoje_segundos)}")
        self.lbl_foco_total.setText(f"TEMPO TOTAL: {format_seconds(total_acumulado)}")

        start_of_week = today_date - datetime.timedelta(days=today_date.weekday())
        week_data = []
        for i in range(7):
            date = start_of_week + datetime.timedelta(days=i)
            date_str = date.isoformat()
            seconds = history.get(date_str, {}).get("total_seconds", 0)
            week_data.append(seconds)

        max_seconds = max(week_data) if max(week_data) > 0 else 3600
        MAX_HEIGHT = 100

        for seconds in week_data:
            col = QtWidgets.QWidget()
            v_lay = QtWidgets.QVBoxLayout(col)
            v_lay.setContentsMargins(0, 0, 0, 0)
            v_lay.setSpacing(4)
            v_lay.setAlignment(QtCore.Qt.AlignBottom)

            if seconds > 0:
                h_val = max(int((seconds / max_seconds) * MAX_HEIGHT), 5)
                time_str = format_seconds(seconds).split()[0] + format_seconds(seconds).split()[1][:1]
                t_lbl = QtWidgets.QLabel(time_str)
                t_lbl.setStyleSheet("font-size: 8px; color: white;")
                t_lbl.setAlignment(QtCore.Qt.AlignCenter)
                v_lay.addWidget(t_lbl)
            else:
                h_val = 5

            bar = QtWidgets.QFrame()
            bar.setFixedWidth(24)
            bar.setFixedHeight(h_val)
            color = "#5E12F8" if seconds > 0 else "#2d234a"
            bar.setStyleSheet(f"background-color: {color}; border-radius: 4px;")
            
            v_lay.addWidget(bar)
            self.chart_layout.addWidget(col)

        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                u = json.load(f)["usuario"]
                self.lbl_rank.setText(f"RANK {self.get_rank(u['nivel'])}")
                self.xp_bar.setValue(u['xp'] % 100)
                self.lbl_xp_info.setText(f"NÍVEL {u['nivel']} • {u['xp']%100}/100 XP")
        except: pass

    def get_rank(self, nivel):
        if nivel < 10: return "E"
        if nivel < 20: return "D"
        if nivel < 30: return "C"
        if nivel < 40: return "B"
        if nivel < 50: return "A"
        return "S"

class SkillsCard(HomeCard):
    def __init__(self):
        super().__init__("PONTOS DE HABILIDADES")
        self.refresh_data()

    def refresh_data(self):
        while self.body.count():
            item = self.body.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                u = data["usuario"]
        except: return

        sub = QtWidgets.QLabel(f"CLASSE: INICIANTE\nDISPONÍVEIS: {u['pontos_disponiveis']}")
        sub.setStyleSheet("font-size: 10px; color: rgba(255,255,255,0.5); margin-bottom: 5px;")
        self.body.addWidget(sub)

        attrs = u["atributos"]
        map_names = {"inteligencia": "INTELIGÊNCIA", "forca": "FORÇA", "vitalidade": "VITALIDADE", "criatividade": "CRIATIVIDADE", "social": "SOCIAL"}
        
        for key, val in attrs.items():
            row_widget = QtWidgets.QWidget()
            row = QtWidgets.QHBoxLayout(row_widget)
            row.setContentsMargins(0, 0, 0, 0)
            name = map_names.get(key, key.upper())
            lbl = QtWidgets.QLabel(f"● {name}")
            lbl.setStyleSheet(f"color: {CATEGORIAS.get(name, 'white')}; font-weight: bold; font-size: 11px;")
            val_lbl = QtWidgets.QLabel(str(val))
            val_lbl.setStyleSheet("font-weight: bold; color: white;")
            row.addWidget(lbl)
            row.addStretch()
            row.addWidget(val_lbl)
            row.addSpacing(10)
            btn_up = QtWidgets.QPushButton("+")
            btn_up.setFixedSize(20, 20)
            btn_up.setStyleSheet("QPushButton { background: #5E12F8; border-radius: 10px; color: white; border: none; }")
            row.addWidget(btn_up)
            self.body.addWidget(row_widget)

class SummaryCard(HomeCard):
    def __init__(self):
        super().__init__("MISSÕES")
        self.refresh_data()

    def refresh_data(self):
        while self.body.count():
            item = self.body.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        data = load_missions()
        m_list = data.get("missions", [])
        pendentes = len([m for m in m_list if m["status"] == "Pendente"])
        feitas = len([m for m in m_list if m["status"] == "Concluída"])
        grid_widget = QtWidgets.QWidget()
        grid = QtWidgets.QGridLayout(grid_widget)
        grid.setContentsMargins(0, 0, 0, 0)
        def add_info(label, value, col):
            l = QtWidgets.QLabel(label)
            l.setStyleSheet("font-size: 9px; color: rgba(255,255,255,0.4); font-weight: bold;")
            v = QtWidgets.QLabel(str(value))
            v.setStyleSheet("font-size: 28px; font-weight: bold; color: white;")
            grid.addWidget(l, 0, col, QtCore.Qt.AlignCenter)
            grid.addWidget(v, 1, col, QtCore.Qt.AlignCenter)
        add_info("DISPONÍVEIS", pendentes, 0)
        add_info("REALIZADAS", feitas, 1)
        self.body.addWidget(grid_widget)

class StreakCard(HomeCard):
    def __init__(self):
        super().__init__("SEQUÊNCIA")
        self.refresh_data()

    def refresh_data(self):
        while self.body.count():
            item = self.body.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                s = json.load(f)["sequencia"]
        except: return
        row_widget = QtWidgets.QWidget()
        row = QtWidgets.QHBoxLayout(row_widget)
        row.setContentsMargins(0, 0, 0, 0)
        for label, val in [("MISSÕES DIÁRIAS", f"{s['missoes_consecutivas']} d"), ("FOCO", f"{s['foco_consecutivo']} d")]:
            v = QtWidgets.QVBoxLayout()
            l = QtWidgets.QLabel(label)
            l.setStyleSheet("font-size: 9px; color: rgba(255,255,255,0.4); font-weight: bold;")
            n = QtWidgets.QLabel(val)
            n.setStyleSheet("font-size: 24px; font-weight: bold; color: #5E12F8;")
            v.addWidget(l, alignment=QtCore.Qt.AlignCenter)
            v.addWidget(n, alignment=QtCore.Qt.AlignCenter)
            row.addLayout(v)
        self.body.addWidget(row_widget)

class HomeScreen(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(40, 40, 40, 40)
        self.main_layout.setSpacing(30)
        nome = load_name() or "Recruta"
        header_container = QtWidgets.QWidget()
        header_v = QtWidgets.QVBoxLayout(header_container)
        header_v.setContentsMargins(0, 0, 0, 0)
        self.welcome_label = QtWidgets.QLabel(f"BEM-VINDO, {nome.upper()}")
        self.welcome_label.setStyleSheet("font-size: 20px; font-weight: bold; color: white;")
        underline = QtWidgets.QFrame()
        underline.setFixedHeight(4)
        underline.setFixedWidth(50)
        underline.setStyleSheet("background-color: #5E12F8; border-radius: 2px; border: none;")
        header_v.addWidget(self.welcome_label)
        header_v.addWidget(underline)
        self.main_layout.addWidget(header_container)
        dash_layout = QtWidgets.QHBoxLayout()
        dash_layout.setSpacing(20)
        self.stats = StatsCard()
        dash_layout.addWidget(self.stats, 4)
        right_col = QtWidgets.QVBoxLayout()
        right_col.setSpacing(20)
        self.skills = SkillsCard()
        self.summary = SummaryCard()
        self.streak = StreakCard()
        right_col.addWidget(self.skills, 3)
        right_col.addWidget(self.summary, 2)
        right_col.addWidget(self.streak, 2)
        dash_layout.addLayout(right_col, 3)
        self.main_layout.addLayout(dash_layout)

    def refresh(self):
        nome = load_name() or "Recruta"
        self.welcome_label.setText(f"BEM-VINDO, {nome.upper()}")
        self.stats.refresh_data()
        self.skills.refresh_data()
        self.summary.refresh_data()
        self.streak.refresh_data()