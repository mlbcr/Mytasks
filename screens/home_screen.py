from PySide6 import QtCore, QtWidgets, QtGui
import datetime
import json
import os
from data_manager import (
    load_missions, load_name, load_focus_history, load_user, save_user,
    DATA_FILE
)
from progression import xp_needed_for_level, get_rank
from matplotlib.patches import FancyBboxPatch
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import math


CATEGORIAS = {
    "INTELIGÊNCIA": "#f1c40f", "FORÇA": "#e74c3c",
    "VITALIDADE": "#2ecc71", "CRIATIVIDADE": "#3498db", "SOCIAL": "#95a5a6"
}

def format_seconds_full(s):
    hrs = s // 3600
    mins = (s % 3600) // 60
    secs = s % 60
    return f"{int(hrs)}h {int(mins)}min {int(secs)}s"

class HomeScreen(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.refresh()

    def setup_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(40, 40, 40, 40)
        self.main_layout.setSpacing(30)
        
        # Header
        self.main_layout.addWidget(self.build_header())
        
        # Dashboard grid
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

    def build_header(self):
        header_container = QtWidgets.QWidget()
        header_layout = QtWidgets.QHBoxLayout(header_container)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        title_container = QtWidgets.QVBoxLayout()
        title_container.setSpacing(5)
        
        self.welcome_label = QtWidgets.QLabel()
        self.welcome_label.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: white;
                background: transparent;
                letter-spacing: 1px;
            }
        """)
        
        underline = QtWidgets.QFrame()
        underline.setFixedHeight(4)
        underline.setFixedWidth(40)
        underline.setStyleSheet("""
            QFrame {
                background-color: #5E12F8;
                border-radius: 2px;
                border: none;
            }
        """)
        
        title_container.addWidget(self.welcome_label)
        title_container.addWidget(underline)
        header_layout.addLayout(title_container)
        header_layout.addStretch()
        return header_container

    def refresh(self):
        nome = load_name() or "Recruta"
        self.welcome_label.setText(f"BEM-VINDO, {nome.upper()}")
        self.stats.refresh_data()
        self.skills.refresh_data()
        self.summary.refresh_data()
        self.streak.refresh_data()

class HomeCard(QtWidgets.QFrame):
    def __init__(self, title_text):
        super().__init__()
        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        self.setStyleSheet("""
            HomeCard {
                background-color: #161026;
                border: 1px solid #2d234a;
                border-radius: 14px;
            }
            HomeCard QLabel {
                background: transparent;
                color: white;
                border: none;
            }
        """)
        
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15)
        
        # Header do card
        header_container = QtWidgets.QWidget()
        header_layout = QtWidgets.QVBoxLayout(header_container)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(5)
        
        self.title_label = QtWidgets.QLabel(title_text.upper())
        self.title_label.setStyleSheet("""
            QLabel {
                color: rgba(255,255,255,0.55);
                font-size: 10px;
                font-weight: bold;
                letter-spacing: 1px;
                background: transparent;
                padding: 0;
                margin: 0;
            }
        """)
        
        underline = QtWidgets.QFrame()
        underline.setFixedHeight(2)
        underline.setFixedWidth(22)
        underline.setStyleSheet("""
            QFrame {
                background-color: #5E12F8;
                border-radius: 1px;
                border: none;
            }
        """)
        
        header_layout.addWidget(self.title_label)
        header_layout.addWidget(underline)
        self.layout.addWidget(header_container)

        self.body_widget = QtWidgets.QWidget()
        self.body = QtWidgets.QVBoxLayout(self.body_widget)
        self.body.setContentsMargins(0, 0, 0, 0)
        self.body.setSpacing(12)
        
        self.layout.addWidget(self.body_widget)
        self.layout.addStretch()

class StatsCard(QtWidgets.QFrame):
    def __init__(self):
        super().__init__()
        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        self.setStyleSheet("""
            StatsCard {
                background-color: #161026;
                border: 1px solid #2d234a;
                border-radius: 14px;
            }
            StatsCard QLabel {
                background: transparent;
                color: white;
                border: none;
            }
            StatsCard QProgressBar {
                background-color: #2d234a;
                border-radius: 3px;
                border: none;
            }
            StatsCard QProgressBar::chunk {
                background-color: #5E12F8;
                border-radius: 3px;
            }
        """)
        
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(16)

        self.hover_connection = None

        # Título
        title = QtWidgets.QLabel("ESTATÍSTICAS")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                font-size: 12px;
                font-weight: bold;
                color: rgba(255,255,255,0.7);
                letter-spacing: 1px;
                margin-bottom: 4px;
            }
        """)
        self.layout.addWidget(title)

        # ===== BLOCO DE TEMPO REESTRUTURADO =====

        time_container = QtWidgets.QWidget()
        time_layout = QtWidgets.QVBoxLayout(time_container)
        time_layout.setContentsMargins(0, 0, 0, 0)
        time_layout.setSpacing(2)

        # Label pequeno
        self.lbl_total_title = QtWidgets.QLabel("TEMPO TOTAL")
        self.lbl_total_title.setStyleSheet("""
            QLabel {
                font-size: 10px;
                color: rgba(255,255,255,0.4);
                letter-spacing: 1px;
            }
        """)

        # Valor grande
        self.lbl_foco_total = QtWidgets.QLabel("0h 0min")
        self.lbl_foco_total.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: white;
            }
        """)

        self.lbl_foco_hoje = QtWidgets.QLabel("Hoje: 0h 0min")
        self.lbl_foco_hoje.setStyleSheet("""
            QLabel {
                font-size: 14px;
                padding-top: 10px;
                color: rgba(255,255,255,0.6);
            }
        """)

        time_layout.addWidget(self.lbl_total_title)
        time_layout.addWidget(self.lbl_foco_total)
        time_layout.addSpacing(6)
        time_layout.addWidget(self.lbl_foco_hoje)

        self.layout.addWidget(time_container)


        self.figure = Figure(facecolor="#161026")
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setMinimumHeight(220)
        self.layout.addWidget(self.canvas)


        # Separador
        separator = QtWidgets.QFrame()
        separator.setFixedHeight(1)
        separator.setStyleSheet("QFrame { background-color: #2d234a; border: none; }")
        self.layout.addWidget(separator)

        # Container rank e XP
        rank_container = QtWidgets.QWidget()
        rank_layout = QtWidgets.QVBoxLayout(rank_container)
        rank_layout.setContentsMargins(0, 0, 0, 0)
        rank_layout.setSpacing(8)
        
        self.lbl_rank = QtWidgets.QLabel("RANK E")
        self.lbl_rank.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl_rank.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-size: 16px;
                color: #5E12F8;
            }
        """)
        rank_layout.addWidget(self.lbl_rank)

        self.xp_bar = QtWidgets.QProgressBar()
        self.xp_bar.setFixedHeight(6)
        self.xp_bar.setTextVisible(False)
        rank_layout.addWidget(self.xp_bar)

        self.lbl_xp_info = QtWidgets.QLabel("NÍVEL 1 • 0/100 XP")
        self.lbl_xp_info.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl_xp_info.setStyleSheet("""
            QLabel {
                font-size: 10px;
                color: rgba(255,255,255,0.4);
            }
        """)
        rank_layout.addWidget(self.lbl_xp_info)
        
        self.layout.addWidget(rank_container)

    def refresh_data(self):
        try:
            user_data = load_user()
            history = load_focus_history()
            u = user_data["usuario"]
        except:
            return

        hoje_str = datetime.date.today().isoformat()
        tempo_hoje = history.get(hoje_str, {}).get("total_seconds", 0)
        tempo_total = sum(d.get("total_seconds", 0) for d in history.values())
        self.lbl_foco_total.setText(format_seconds_full(tempo_total))
        self.lbl_foco_hoje.setText(f"Hoje: {format_seconds_full(tempo_hoje)}")


        self.lbl_rank.setText(f"RANK {get_rank(u['nivel'])}")
        xp_prox = xp_needed_for_level(u['nivel'])
        self.xp_bar.setMaximum(xp_prox)
        self.xp_bar.setValue(u['xp'])
        self.lbl_xp_info.setText(f"NÍVEL {u['nivel']} • {u['xp']}/{xp_prox} XP")

        
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        ax.set_facecolor("#161026")
        self.figure.patch.set_facecolor("#161026")

        hoje = datetime.date.today()
        segunda = hoje - datetime.timedelta(days=hoje.weekday())

        dias_labels = ["SEG", "TER", "QUA", "QUI", "SEX", "SAB", "DOM"]
        tempos = []

        for i in range(7):
            dia = (segunda + datetime.timedelta(days=i)).isoformat()
            s = history.get(dia, {}).get("total_seconds", 0)
            tempos.append(s / 3600)  # converter para horas

        max_estudo = max(tempos) if tempos else 0
        max_y = min(math.ceil(max_estudo), 24)

        if max_y == 0:
            max_y = 1

        bars = ax.bar(dias_labels, tempos, width=0.6)

        annot = ax.annotate(
            "",
            xy=(0, 0),
            xytext=(0, 15),
            textcoords="offset points",
            ha="center",
            fontsize=9,
            color="white",
            bbox=dict(
                boxstyle="round,pad=0.3",
                fc="#2d234a",
                ec="#5E12F8",
                lw=1
            )
        )
        annot.set_visible(False)

        def on_hover(event):
            vis = annot.get_visible()

            if event.inaxes == ax:
                for i, bar in enumerate(bars):
                    contains, _ = bar.contains(event)
                    if contains:
                        # Remover glow antigo
                        for artist in ax.patches[:]:
                            if hasattr(artist, "is_glow") and artist.is_glow:
                                artist.remove()

                        # Criar glow
                        glow = FancyBboxPatch(
                            (bar.get_x() - 0.03, 0),
                            bar.get_width() + 0.06,
                            bar.get_height(),
                            boxstyle="round,pad=0.02,rounding_size=0.2",
                            linewidth=0,
                            facecolor="#9B5CFF",
                            alpha=0.25
                        )

                        glow.is_glow = True  # marcar como glow
                        ax.add_patch(glow)
                        glow.set_zorder(bar.get_zorder() - 1)



                        x = bar.get_x() + bar.get_width() / 2
                        y = bar.get_height()
                        

                        annot.xy = (x, y)

                        segundos = history.get(
                            (segunda + datetime.timedelta(days=i)).isoformat(),
                            {}
                        ).get("total_seconds", 0)

                        annot.set_text(format_seconds_full(segundos))
                        annot.set_visible(True)
                        self.canvas.draw_idle()
                        return
                for artist in ax.patches[:]:
                    if hasattr(artist, "is_glow") and artist.is_glow:
                        artist.remove()
            if vis:
                annot.set_visible(False)
                self.canvas.draw_idle()


        for i, bar in enumerate(bars):
            bar.set_color("#5E12F8")
            bar.set_linewidth(0)

        hoje_index = datetime.date.today().weekday()
        bars[hoje_index].set_color("#7B3BFB")

        ax.set_ylim(0, max_y)

        yticks = list(range(0, max_y + 1))
        ax.set_yticks(yticks)
        ax.set_yticklabels(
            [f"{i}h" for i in yticks],
            fontsize=9,
            color=(1, 1, 1, 0.6)
        )

        ax.tick_params(
            axis='x',
            colors="white",
            labelsize=10
        )

        for spine in ax.spines.values():
            spine.set_visible(False)

        ax.tick_params(axis='both', length=0)
        ax.grid(
            axis="y",
            linestyle=":",
            linewidth=1,
            alpha=0.2
        )

        ax.margins(x=0.08)

        if self.hover_connection is not None:
            self.canvas.mpl_disconnect(self.hover_connection)

        self.hover_connection = self.canvas.mpl_connect(
            "motion_notify_event",
            on_hover
        )

        self.canvas.draw()

class SkillsCard(HomeCard):
    def __init__(self):
        super().__init__("PONTOS DE HABILIDADES")
        self.refresh_data()

    def refresh_data(self):
        # Limpar body
        while self.body.count():
            item = self.body.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        try:
            user_data = load_user()
            u = user_data["usuario"]
        except:
            return

        # Container info
        info_container = QtWidgets.QWidget()
        info_layout = QtWidgets.QVBoxLayout(info_container)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(4)
        
        classe_lbl = QtWidgets.QLabel("CLASSE: INICIANTE")
        classe_lbl.setStyleSheet("""
            QLabel {
                font-size: 10px;
                color: rgba(255,255,255,0.5);
                font-weight: normal;
            }
        """)
        
        pts_lbl = QtWidgets.QLabel(f"DISPONÍVEIS: {u['pontos_disponiveis']}")
        pts_lbl.setStyleSheet("""
            QLabel {
                font-size: 10px;
                color: #5E12F8;
                font-weight: bold;
            }
        """)
        
        info_layout.addWidget(classe_lbl)
        info_layout.addWidget(pts_lbl)
        self.body.addWidget(info_container)

        # Separador
        separator = QtWidgets.QFrame()
        separator.setFixedHeight(1)
        separator.setStyleSheet("QFrame { background-color: #2d234a; border: none; }")
        self.body.addWidget(separator)

        # Atributos
        map_names = {
            "inteligencia": "INTELIGÊNCIA",
            "forca": "FORÇA",
            "vitalidade": "VITALIDADE",
            "criatividade": "CRIATIVIDADE",
            "social": "SOCIAL"
        }
        
        for key, val in u["atributos"].items():
            row_widget = QtWidgets.QWidget()
            row = QtWidgets.QHBoxLayout(row_widget)
            row.setContentsMargins(0, 0, 0, 0)
            row.setSpacing(8)
            
            name = map_names.get(key, key.upper())
            
            lbl = QtWidgets.QLabel(f"● {name}")
            lbl.setStyleSheet(f"""
                QLabel {{
                    color: {CATEGORIAS.get(name, 'white')};
                    font-weight: bold;
                    font-size: 11px;
                    background: transparent;
                }}
            """)
            
            val_lbl = QtWidgets.QLabel(str(val))
            val_lbl.setStyleSheet("""
                QLabel {
                    font-weight: bold;
                    color: white;
                    font-size: 11px;
                    background: transparent;
                }
            """)
            
            btn = QtWidgets.QPushButton("+")
            btn.setFixedSize(22, 22)
            btn.setCursor(QtCore.Qt.PointingHandCursor)
            btn.setEnabled(u['pontos_disponiveis'] > 0)
            btn.setStyleSheet("""
                QPushButton {
                    background: #5E12F8;
                    border-radius: 11px;
                    color: white;
                    font-weight: bold;
                    font-size: 14px;
                    border: none;
                    padding: 0px 0px 2px 0px;
                }
                QPushButton:hover {
                    background: #7B3BFB;
                }
                QPushButton:pressed {
                    background: #4A0EC9;
                }
                QPushButton:disabled {
                    background: #2d234a;
                    color: rgba(255,255,255,0.3);
                }
            """)
            btn.clicked.connect(lambda checked=False, k=key: self.add_point(k))
            
            row.addWidget(lbl)
            row.addStretch()
            row.addWidget(val_lbl)
            row.addSpacing(4)
            row.addWidget(btn)
            self.body.addWidget(row_widget)

    def add_point(self, k):
        data = load_user()
        if data["usuario"]["pontos_disponiveis"] > 0:
            data["usuario"]["pontos_disponiveis"] -= 1
            data["usuario"]["atributos"][k] += 1
            save_user(data)
            self.refresh_data()

class SummaryCard(HomeCard):
    def __init__(self):
        super().__init__("MISSÕES DIÁRIAS")
        self.refresh_data()

    def refresh_data(self):
        while self.body.count():
            item = self.body.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        data = load_missions()
        m_list = data.get("missions", [])
        pendentes = len([m for m in m_list if m["status"] == "Pendente"])
        feitas = len([m for m in m_list if m["status"] == "Concluída"])
        
        grid_widget = QtWidgets.QWidget()
        grid = QtWidgets.QGridLayout(grid_widget)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(20)
        grid.setVerticalSpacing(8)
        
        lbl_disponiveis = QtWidgets.QLabel("DISPONÍVEIS")
        lbl_disponiveis.setAlignment(QtCore.Qt.AlignCenter)
        lbl_disponiveis.setStyleSheet("""
            QLabel {
                font-size: 9px;
                color: rgba(255,255,255,0.4);
                font-weight: bold;
                letter-spacing: 1px;
            }
        """)
        
        val_disponiveis = QtWidgets.QLabel(str(pendentes))
        val_disponiveis.setAlignment(QtCore.Qt.AlignCenter)
        val_disponiveis.setStyleSheet("""
            QLabel {
                font-size: 32px;
                font-weight: bold;
                color: white;
            }
        """)
        
        lbl_realizadas = QtWidgets.QLabel("REALIZADAS")
        lbl_realizadas.setAlignment(QtCore.Qt.AlignCenter)
        lbl_realizadas.setStyleSheet("""
            QLabel {
                font-size: 9px;
                color: rgba(255,255,255,0.4);
                font-weight: bold;
                letter-spacing: 1px;
            }
        """)
        
        val_realizadas = QtWidgets.QLabel(str(feitas))
        val_realizadas.setAlignment(QtCore.Qt.AlignCenter)
        val_realizadas.setStyleSheet("""
            QLabel {
                font-size: 32px;
                font-weight: bold;
                color: white;
            }
        """)
        
        grid.addWidget(lbl_disponiveis, 0, 0)
        grid.addWidget(val_disponiveis, 1, 0)
        grid.addWidget(lbl_realizadas, 0, 1)
        grid.addWidget(val_realizadas, 1, 1)
        
        self.body.addWidget(grid_widget)

class StreakCard(HomeCard):
    def __init__(self):
        super().__init__("SEQUÊNCIA")
        self.refresh_data()

    def refresh_data(self):
        while self.body.count():
            item = self.body.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        try:
            s = load_user()["sequencia"]
        except:
            return
        
        container = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)
        
        missoes_box = QtWidgets.QVBoxLayout()
        missoes_box.setSpacing(4)
        
        lbl_missoes = QtWidgets.QLabel("MISSÕES DIÁRIAS")
        lbl_missoes.setAlignment(QtCore.Qt.AlignCenter)
        lbl_missoes.setStyleSheet("""
            QLabel {
                font-size: 9px;
                color: rgba(255,255,255,0.4);
                font-weight: bold;
                letter-spacing: 1px;
            }
        """)
        
        val_missoes = QtWidgets.QLabel(f"{s['missoes_consecutivas']} d")
        val_missoes.setAlignment(QtCore.Qt.AlignCenter)
        val_missoes.setStyleSheet("""
            QLabel {
                font-size: 28px;
                font-weight: bold;
                color: #5E12F8;
            }
        """)
        
        missoes_box.addWidget(lbl_missoes)
        missoes_box.addWidget(val_missoes)
        
        foco_box = QtWidgets.QVBoxLayout()
        foco_box.setSpacing(4)
        
        lbl_foco = QtWidgets.QLabel("FOCO")
        lbl_foco.setAlignment(QtCore.Qt.AlignCenter)
        lbl_foco.setStyleSheet("""
            QLabel {
                font-size: 9px;
                color: rgba(255,255,255,0.4);
                font-weight: bold;
                letter-spacing: 1px;
            }
        """)
        
        val_foco = QtWidgets.QLabel(f"{s['foco_consecutivo']} d")
        val_foco.setAlignment(QtCore.Qt.AlignCenter)
        val_foco.setStyleSheet("""
            QLabel {
                font-size: 28px;
                font-weight: bold;
                color: #5E12F8;
            }
        """)
        
        foco_box.addWidget(lbl_foco)
        foco_box.addWidget(val_foco)
        
        layout.addLayout(missoes_box)
        layout.addLayout(foco_box)
        
        self.body.addWidget(container)