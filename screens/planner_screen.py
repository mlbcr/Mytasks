from PySide6 import QtCore, QtWidgets, QtGui
import datetime
from data_manager import load_missions, resource_path, save_missions_to_file

PX_PER_HOUR = 160
MARGIN_LEFT = 100
TIMELINE_PADDING = 40

CATEGORY_COLORS = {
    "INTELIGÊNCIA": "#1d3a7d",
    "FORÇA": "#58182e",
    "VITALIDADE": "#1a582e",
    "CRIATIVIDADE": "#8c6b12",
    "SOCIAL": "#5E12F8",
    "DEFAULT": "#2d234a"
}

def time_to_pixels(time_str):
    try:
        h, m = map(int, time_str.split(':'))
        return (h * PX_PER_HOUR) + (m * (PX_PER_HOUR / 60)) + TIMELINE_PADDING
    except: return TIMELINE_PADDING

def duration_to_pixels(start, end):
    y_start = time_to_pixels(start)
    y_end = time_to_pixels(end)
    return y_end - y_start

class MissionItemWidget(QtWidgets.QWidget):
    def __init__(self, titulo, descricao, xp, categoria):
        super().__init__()
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        
        cat_upper = categoria.upper() if categoria else "DEFAULT"
        self.cor_base = CATEGORY_COLORS.get(cat_upper, CATEGORY_COLORS["DEFAULT"])
        
        self.container = QtWidgets.QFrame()
        self.container.setObjectName("MissionContainer")
        # Removido fundo das labels internas para evitar o "quadrado" esquisito
        self.container.setStyleSheet(f"""
            QFrame#MissionContainer {{
                background-color: rgba({self.hex_to_rgb(self.cor_base)}, 0.15);
                border: 1px solid rgba({self.hex_to_rgb(self.cor_base)}, 0.3);
                border-radius: 12px;
            }}
            QLabel {{
                background: transparent;
                border: none;
            }}
        """)
        
        c_layout = QtWidgets.QHBoxLayout(self.container)
        c_layout.setContentsMargins(15, 10, 15, 10)
        
        self.accent_bar = QtWidgets.QFrame()
        self.accent_bar.setFixedWidth(4)
        self.accent_bar.setStyleSheet(f"background-color: {self.cor_base}; border-radius: 2px;")
        c_layout.addWidget(self.accent_bar)

        info = QtWidgets.QVBoxLayout()
        t = QtWidgets.QLabel(titulo)
        t.setStyleSheet("color: white; font-weight: bold; font-size: 14px;")
        
        desc = descricao if descricao else "Sem descrição"
        d = QtWidgets.QLabel(desc[:45] + "..." if len(desc) > 45 else desc)
        d.setStyleSheet("color: #8a8a8a; font-size: 11px;")
        
        info.addWidget(t)
        info.addWidget(d)
        c_layout.addLayout(info)
        c_layout.addStretch()
        
        self.xp_tag = QtWidgets.QLabel(f"+{xp} XP")
        self.xp_tag.setStyleSheet(f"""
            color: white; font-weight: 900; font-size: 10px; 
            background: {self.cor_base}; border-radius: 6px; padding: 4px 8px;
        """)
        c_layout.addWidget(self.xp_tag)
        
        layout.addWidget(self.container)

    def hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        return f"{int(hex_color[0:2], 16)}, {int(hex_color[2:4], 16)}, {int(hex_color[4:6], 16)}"

    def set_selected(self, selected):
        if selected:
            # Efeito futurista: Borda branca brilhante e fundo mais opaco
            self.container.setStyleSheet(f"""
                QFrame#MissionContainer {{
                    background-color: rgba({self.hex_to_rgb(self.cor_base)}, 0.6);
                    border: 2px solid #FFFFFF;
                }}
                QLabel {{ background: transparent; }}
            """)
        else:
            self.container.setStyleSheet(f"""
                QFrame#MissionContainer {{
                    background-color: rgba({self.hex_to_rgb(self.cor_base)}, 0.15);
                    border: 1px solid rgba({self.hex_to_rgb(self.cor_base)}, 0.3);
                    border-radius: 12px;
                }}
                QLabel {{ background: transparent; }}
            """)

class AddMissionOverlay(QtWidgets.QFrame):
    finished = QtCore.Signal(object)

    def __init__(self, missions, parent, data_selecionada):
        super().__init__(parent)
        weekday = data_selecionada.weekday()

        self.available_missions = []

        for m in missions:

            if m.get("horario_inicio") and not any(m.get("repetida", [])):
                continue

            prazo = m.get("prazo")
            repet = m.get("repetida", [])

            aparece = False

            if prazo and prazo == data_selecionada.isoformat():
                aparece = True

            if repet and len(repet) > weekday and repet[weekday]:
                aparece = True

            if aparece:
                self.available_missions.append(m)
        
        self.filtered = self.available_missions
        
        self.setGeometry(0, 0, parent.width(), parent.height())
        self.setStyleSheet("background-color: rgba(10, 7, 20, 0.9);")

        self.panel = QtWidgets.QFrame(self)
        self.panel.setFixedSize(520, 680)
        self.panel.setObjectName("MainPanel")
        self.panel.setStyleSheet("""
            QFrame#MainPanel {
                background-color: #161025;
                border: 1px solid #5E12F8;
                border-radius: 30px;
            }
            QLabel { background: transparent; color: white; }
            QLineEdit {
                background: #0e0b1c; border: 1px solid #2d234a; border-radius: 15px;
                padding: 15px; color: white; font-size: 14px;
            }
            QListWidget { background: transparent; border: none; outline: none; }
            QTimeEdit {
                background: #1b1430; color: #5E12F8; font-size: 42px; font-weight: 900;
                border-radius: 15px; border: 1px solid #2d234a; padding: 5px;
            }
            QTimeEdit::up-button, QTimeEdit::down-button { width: 0px; }
        """)

        layout = QtWidgets.QVBoxLayout(self.panel)
        layout.setContentsMargins(35, 35, 35, 35)
        layout.setSpacing(20)

        header = QtWidgets.QLabel("PLANEJAR MISSÃO")
        header.setStyleSheet("font-size: 16px; font-weight: 800; letter-spacing: 3px;")
        layout.addWidget(header, alignment=QtCore.Qt.AlignCenter)

        self.search = QtWidgets.QLineEdit()
        self.search.setPlaceholderText("Pesquisar missão")
        layout.addWidget(self.search)

        self.list_widget = QtWidgets.QListWidget()
        layout.addWidget(self.list_widget)

        time_layout = QtWidgets.QHBoxLayout()
        for label_text, attr in [("INÍCIO", "start_edit"), ("FIM", "end_edit")]:
            v_box = QtWidgets.QVBoxLayout()
            l = QtWidgets.QLabel(label_text)
            l.setStyleSheet("color: #4a4a4a; font-size: 10px; font-weight: bold;")
            te = QtWidgets.QTimeEdit(QtCore.QTime(12, 0))
            te.setDisplayFormat("HH:mm")
            te.setAlignment(QtCore.Qt.AlignCenter)
            setattr(self, attr, te)
            v_box.addWidget(l, alignment=QtCore.Qt.AlignCenter)
            v_box.addWidget(te)
            time_layout.addLayout(v_box)
        layout.addLayout(time_layout)

        self.btn_confirm = QtWidgets.QPushButton("CONFIRMAR AGENDAMENTO")
        self.btn_confirm.setFixedHeight(55)
        self.btn_confirm.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_confirm.setStyleSheet("""
            QPushButton {
                background: #5E12F8; color: white; border-radius: 15px; font-weight: 800; font-size: 14px;
            }
            QPushButton:hover { background: #7B2FF7; border: 1px solid white; }
        """)
        layout.addWidget(self.btn_confirm)

        self.panel.move((self.width()-520)//2, (self.height()-680)//2)

        self.search.textChanged.connect(self.filter_list)
        self.btn_confirm.clicked.connect(self.send_data)
        self.list_widget.itemSelectionChanged.connect(self.update_selection_visual)
        self.populate()

    def mousePressEvent(self, event):
        if not self.panel.geometry().contains(event.pos()):
            self.deleteLater()

    def populate(self):
        self.list_widget.clear()
        for m in self.filtered:
            item = QtWidgets.QListWidgetItem(self.list_widget)
            item.setSizeHint(QtCore.QSize(0, 85))
            widget = MissionItemWidget(m['titulo'], m.get('descricao',''), m.get('xp', 5), m.get('categoria', ''))
            self.list_widget.setItemWidget(item, widget)

    def update_selection_visual(self):
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            widget = self.list_widget.itemWidget(item)
            if widget: widget.set_selected(item.isSelected())

    def filter_list(self, text):
        self.filtered = [m for m in self.available_missions if text.lower() in m["titulo"].lower()]
        self.populate()

    def send_data(self):
        row = self.list_widget.currentRow()
        if row >= 0:
            res = {
                "id": self.filtered[row]["id"],
                "start": self.start_edit.time().toString("HH:mm"),
                "end": self.end_edit.time().toString("HH:mm")
            }
            self.finished.emit(res)
            self.deleteLater()

class MissionDetailsOverlay(QtWidgets.QFrame):
    finished = QtCore.Signal(object)

    def __init__(self, mission, parent):
        super().__init__(parent)
        self.mission = mission
        self.setGeometry(0, 0, parent.width(), parent.height())
        self.setStyleSheet("background-color: rgba(7, 5, 15, 0.95);") # Fundo ainda mais profundo

        # Efeito de Fade
        self.opacity_effect = QtWidgets.QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.anim = QtCore.QPropertyAnimation(self.opacity_effect, b"opacity")
        self.anim.setDuration(250); self.anim.setStartValue(0); self.anim.setEndValue(1); self.anim.start()

        self.panel = QtWidgets.QFrame(self)
        self.panel.setFixedSize(450, 550) # Aumentei um pouco a altura para respirar
        cat_raw = mission.get('categoria')
        cat_upper = cat_raw.upper() if cat_raw else "DEFAULT"
        cor_cat = CATEGORY_COLORS.get(cat_upper, CATEGORY_COLORS["DEFAULT"])
        
        # Design Moderno: Borda lateral colorida e fundo escuro facetado
        self.panel.setStyleSheet(f"""
            QFrame#Panel {{ 
                background-color: #161025; 
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-top: 4px solid {cor_cat}; /* Barra de cor no topo estilo Notion/Modern */
                border-radius: 20px; 
            }}
            QLabel {{ color: white; border: none; background: transparent; }}
            
            QTimeEdit {{ 
                background: #0e0b1c; 
                color: {cor_cat}; 
                font-size: 38px; 
                font-weight: 900; 
                border-radius: 12px; 
                border: 1px solid #2d234a;
                padding: 10px;
            }}
            QTimeEdit::up-button, QTimeEdit::down-button {{ width: 0px; }} /* Esconde setas feias */

            QPushButton#Save {{ 
                background: {cor_cat}; 
                color: white; 
                border-radius: 12px; 
                font-weight: bold; 
                font-size: 14px;
                height: 50px; 
            }}
            QPushButton#Save:hover {{ background: white; color: {cor_cat}; }}
            
            QPushButton#Cancel {{ 
                background: transparent; 
                color: #6a6a6a; 
                font-weight: bold; 
                font-size: 12px;
            }}
            QPushButton#Cancel:hover {{ color: white; }}
        """)
        self.panel.setObjectName("Panel")

        layout = QtWidgets.QVBoxLayout(self.panel)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        # --- CABEÇALHO ---
        top_info = QtWidgets.QVBoxLayout()
        texto_categoria = (mission.get('categoria') or 'GERAL').upper()
        cat_badge = QtWidgets.QLabel(texto_categoria) 
        
        cat_badge.setStyleSheet(f"""
            color: {cor_cat}; font-size: 11px; font-weight: 800; 
            letter-spacing: 2px; background: rgba({self.hex_to_rgb(cor_cat)}, 0.1);
            padding: 4px 10px; border-radius: 5px;
        """)
        cat_badge.setFixedWidth(cat_badge.sizeHint().width() + 20)
        
        title_lbl = QtWidgets.QLabel(mission['titulo'])
        title_lbl.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        title_lbl.setStyleSheet("font-size: 26px; font-weight: 800; color: white; margin-top: 10px;")
        title_lbl.setWordWrap(True)
        
        top_info.addWidget(cat_badge)
        top_info.addWidget(title_lbl)
        layout.addLayout(top_info)

        # --- DESCRIÇÃO ---
        desc_box = QtWidgets.QVBoxLayout()
        desc_title = QtWidgets.QLabel("NOTAS / DESCRIÇÃO")
        desc_title.setStyleSheet("color: #4a4a4a; font-size: 9px; font-weight: bold; letter-spacing: 1px;")
        
        desc_txt = mission.get('descricao', 'Nenhuma descrição detalhada para esta missão.')
        desc_lbl = QtWidgets.QLabel(desc_txt if desc_txt else "Sem notas...")
        desc_lbl.setStyleSheet("color: #a0a0a0; font-size: 13px; line-height: 18px;")
        desc_lbl.setWordWrap(True)
        
        desc_box.addWidget(desc_title)
        desc_box.addWidget(desc_lbl)
        layout.addLayout(desc_box)

        layout.addStretch()

        # --- SELETOR DE HORÁRIO ---
        time_container = QtWidgets.QVBoxLayout()
        time_header = QtWidgets.QLabel("AJUSTAR CRONOGRAMA")
        time_header.setStyleSheet("color: #4a4a4a; font-size: 9px; font-weight: bold; letter-spacing: 1px;")
        time_header.setAlignment(QtCore.Qt.AlignCenter)
        time_container.addWidget(time_header)

        h_layout = QtWidgets.QHBoxLayout()
        self.start_edit = QtWidgets.QTimeEdit(QtCore.QTime.fromString(mission['horario_inicio'], "HH:mm"))
        self.end_edit = QtWidgets.QTimeEdit(QtCore.QTime.fromString(mission['horario_fim'], "HH:mm"))
        self.start_edit.setDisplayFormat("HH:mm"); self.end_edit.setDisplayFormat("HH:mm")
        self.start_edit.setAlignment(QtCore.Qt.AlignCenter); self.end_edit.setAlignment(QtCore.Qt.AlignCenter)
        
        sep = QtWidgets.QLabel("→")
        sep.setStyleSheet(f"color: #2d234a; font-size: 24px; font-weight: bold;")

        h_layout.addWidget(self.start_edit)
        h_layout.addWidget(sep)
        h_layout.addWidget(self.end_edit)
        time_container.addLayout(h_layout)
        layout.addLayout(time_container)

        layout.addSpacing(20)

        # --- BOTÕES ---
        btn_layout = QtWidgets.QHBoxLayout()
        self.btn_cancel = QtWidgets.QPushButton("CANCELAR")
        self.btn_cancel.setObjectName("Cancel")
        self.btn_cancel.setCursor(QtCore.Qt.PointingHandCursor)
        
        self.btn_save = QtWidgets.QPushButton("SALVAR AGENDA")
        self.btn_save.setObjectName("Save")
        self.btn_save.setCursor(QtCore.Qt.PointingHandCursor)

        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_save, 2) # Botão salvar maior
        layout.addLayout(btn_layout)

        self.panel.move((parent.width()-450)//2, (parent.height()-550)//2)
        
        self.btn_cancel.clicked.connect(self.close_overlay)
        self.btn_save.clicked.connect(self.save_data)

    def hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        return f"{int(hex_color[0:2], 16)}, {int(hex_color[2:4], 16)}, {int(hex_color[4:6], 16)}"

    def save_data(self):
        res = {
            "id": self.mission["id"], 
            "start": self.start_edit.time().toString("HH:mm"), 
            "end": self.end_edit.time().toString("HH:mm")
        }
        self.finished.emit(res)
        self.close_overlay()

    def close_overlay(self):
        self.anim.setDirection(QtCore.QAbstractAnimation.Backward)
        self.anim.finished.connect(self.deleteLater)
        self.anim.start()

class PlannerCard(QtWidgets.QFrame):
    clicked = QtCore.Signal(dict)

    def __init__(self, parent, m, x_offset=0, width_percent=100):
        super().__init__(parent)
        self.mission_data = m
        is_done = m['status'] == "Concluída"
        
        cat_raw = m.get('categoria')
        cat_upper = cat_raw.upper() if cat_raw else "DEFAULT"
        cor_base = CATEGORY_COLORS.get(cat_upper, CATEGORY_COLORS["DEFAULT"])
        bg_color = "#1b1430" if not is_done else "#120e1f"
        accent_color = cor_base if not is_done else "#4a4a4a"
        
        start, end = m['horario_inicio'], m['horario_fim']
        y = time_to_pixels(start)
        h_real = duration_to_pixels(start, end)
        
        h_visual = max(h_real, 60) 
        
        available_width = parent.width() - MARGIN_LEFT - 30
        self.setGeometry(MARGIN_LEFT + (available_width * x_offset) / 100, y, (available_width * width_percent) / 100, h_visual)

        self.setStyleSheet(f"""
            QFrame#Card {{
                background-color: {bg_color};
                border-left: 5px solid {accent_color};
                border-radius: 10px;
            }}
        """)
        self.setObjectName("Card")
        self.setCursor(QtCore.Qt.PointingHandCursor)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(12, 5, 12, 5)
        main_layout.setSpacing(3)

        if h_visual < 80:
            row_layout = QtWidgets.QHBoxLayout()
            row_layout.setSpacing(10)
            
            time_lbl = QtWidgets.QLabel(f"{start}-{end}")
            time_lbl.setStyleSheet(f"color: {accent_color}; font-size: 14px; font-weight: 900;")
            time_lbl.setAttribute(QtCore.Qt.WA_TranslucentBackground)

            title_lbl = QtWidgets.QLabel(m['titulo'])
            title_lbl.setAttribute(QtCore.Qt.WA_TranslucentBackground)
            title_lbl.setStyleSheet("color: white; font-size: 15px; font-weight: 700;")
            
            row_layout.addWidget(time_lbl)
            row_layout.addWidget(title_lbl, 1)
            main_layout.addLayout(row_layout)
        else:
            time_lbl = QtWidgets.QLabel(f"{start} — {end}")
            time_lbl.setAttribute(QtCore.Qt.WA_TranslucentBackground)
            time_lbl.setStyleSheet(f"""
                color: {accent_color}; 
                font-size: 14px; 
                font-weight: 900; 
                letter-spacing: 1px;
                padding: 2px 5px; 
                border-radius: 4px;
            """)
            main_layout.addWidget(time_lbl)

            titulo_lbl = QtWidgets.QLabel(m['titulo'])
            titulo_lbl.setWordWrap(True)
            decoration = "text-decoration: line-through;" if is_done else ""
            titulo_lbl.setStyleSheet(f"""
                color: {'#8a8a8a' if is_done else 'white'}; 
                font-size: 14px; 
                font-weight: 700;
                line-height: 1.2;
                {decoration}
            """)
            main_layout.addWidget(titulo_lbl)
            main_layout.addStretch()

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.clicked.emit(self.mission_data)

class DaySelectorWidget(QtWidgets.QWidget):
    day_selected = QtCore.Signal(datetime.date)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.setContentsMargins(20, 10, 20, 10)
        self.layout.setSpacing(10)
        self.buttons = []
        self.selected_date = datetime.date.today()

        # Gerar 7 dias (3 passados, hoje, 3 futuros)
        today = datetime.date.today()
        for i in range(-3, 4):
            date = today + datetime.timedelta(days=i)
            btn = self.create_day_button(date)
            self.layout.addWidget(btn)
            self.buttons.append(btn)
        
        self.update_styles()

    def create_day_button(self, date):
        btn = QtWidgets.QPushButton()
        btn.setFixedSize(55, 70)
        btn.setCursor(QtCore.Qt.PointingHandCursor)
        
        dias_semana = ["SEG", "TER", "QUA", "QUI", "SEX", "SÁB", "DOM"]
        texto = f"{dias_semana[date.weekday()]}\n{date.day}"
        btn.setText(texto)
        btn.setProperty("date", date)
        btn.clicked.connect(lambda: self.select_date(date))
        return btn

    def select_date(self, date):
        self.selected_date = date
        self.update_styles()
        self.day_selected.emit(date)

    def update_styles(self):
        for btn in self.buttons:
            date = btn.property("date")
            if date == self.selected_date:
                btn.setStyleSheet("""
                    QPushButton {
                        background: #5E12F8; color: white; border-radius: 12px;
                        font-weight: bold; font-size: 13px; border: 2px solid #7B2FF7;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background: #1b1430; color: #6a6a6a; border-radius: 12px;
                        font-weight: bold; font-size: 11px; border: 1px solid #2d234a;
                    }
                    QPushButton:hover { color: white; background: #251b3d; }
                """)

class PlannerScreen(QtWidgets.QWidget):
    planner_updated = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        # Estado inicial: data de hoje
        self.current_date = datetime.date.today() 
        
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 10, 0, 0)
        self.main_layout.setSpacing(10)

        title = QtWidgets.QLabel("PLANNER")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet("color: white; font-weight: 800; font-size: 18px; letter-spacing: 2px;")
        self.main_layout.addWidget(title)

        self.day_selector = DaySelectorWidget()
        self.day_selector.day_selected.connect(self.change_date)
        self.main_layout.addWidget(self.day_selector)

        self.btn_add = QtWidgets.QPushButton("+ Adicionar Missão")
        self.btn_add.setFixedHeight(50)
        self.btn_add.setStyleSheet("background: #5E12F8; color: white; border-radius: 15px; font-weight: bold; margin: 0 30px;")
        self.btn_add.clicked.connect(self.open_add_modal)
        self.main_layout.addWidget(self.btn_add)

        self.setup_timeline()
        self.load_all()

    def change_date(self, date):
        """Método chamado sempre que você clica em um dia no seletor"""
        self.current_date = date
        self.load_all() 

    def setup_timeline(self):
        self.scroll = QtWidgets.QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("background: transparent; border: none;")
        
        self.timeline_container = QtWidgets.QWidget()
        self.timeline_container.setFixedHeight(24 * PX_PER_HOUR + (TIMELINE_PADDING * 2))
        self.timeline_container.setStyleSheet("background: #161025;")
        
        for h in range(24):
            y_pos = (h * PX_PER_HOUR) + TIMELINE_PADDING
            line = QtWidgets.QFrame(self.timeline_container)
            line.setGeometry(MARGIN_LEFT - 10, y_pos, 2000, 1)
            line.setStyleSheet("background-color: #2d234a;")
            
            lbl = QtWidgets.QLabel(f"{h:02d}:00", self.timeline_container)
            lbl.setGeometry(10, y_pos - 12, 80, 25) 
            lbl.setStyleSheet("""
                color: #8a8a8a; 
                font-size: 14px; 
                font-weight: 800; 
                background: transparent; 
                border: none;
            """)

        self.scroll.setWidget(self.timeline_container)
        self.main_layout.addWidget(self.scroll)

    def load_all(self):
        """Lógica de carregamento filtrada estritamente pela data selecionada"""
        for child in self.timeline_container.findChildren(PlannerCard): 
            child.deleteLater()
            
        data = load_missions()
        data_selecionada = self.current_date 
        
        missions_filtered = []

        weekday = data_selecionada.weekday()

        for m in data.get("missions", []):

            if m.get("status") == "deleted" or not m.get("horario_inicio"):
                continue

            prazo = m.get("prazo")
            repet = m.get("repetida", [])

            aparece = False

            # ✔ missão normal por data
            if prazo:
                prazo_missao = datetime.date.fromisoformat(prazo)
                if prazo_missao == data_selecionada:
                    aparece = True

            # ✔ missão repetida pelo weekday
            if repet and len(repet) > weekday and repet[weekday]:
                aparece = True

            if aparece:
                missions_filtered.append(m)

        missions_filtered.sort(key=lambda x: x['horario_inicio'])

        groups = []
        for m in missions_filtered:
            placed = False
            for group in groups:
                if any(self.check_overlap(m, existing) for existing in group):
                    group.append(m)
                    placed = True
                    break
            if not placed:
                groups.append([m])

        for group in groups:
            num_cols = len(group)
            width_p = 100 / num_cols
            for i, m in enumerate(group):
                card = PlannerCard(self.timeline_container, m, x_offset=(i * width_p), width_percent=width_p)
                card.clicked.connect(self.open_details_modal)
                card.show()

    def check_overlap(self, m1, m2):
        s1, e1 = time_to_pixels(m1['horario_inicio']), time_to_pixels(m1['horario_fim'])
        s2, e2 = time_to_pixels(m2['horario_inicio']), time_to_pixels(m2['horario_fim'])
        
        return s1 < e2 and s2 < e1

    def open_add_modal(self):
        missions = [m for m in load_missions().get("missions", []) if m.get("status") != "deleted"]
        
        self.overlay = AddMissionOverlay(missions, self, self.current_date) 
        
        self.overlay.finished.connect(self.save_and_refresh)
        self.overlay.show()

    def open_details_modal(self, mission_data):
        self.overlay = MissionDetailsOverlay(mission_data, self)
        self.overlay.finished.connect(self.save_and_refresh); self.overlay.show()

    def save_and_refresh(self, res):
        if not res: return
        data = load_missions()
        for m in data.get("missions", []):
            if m["id"] == res.get("id") or (res.get("mission") and m["id"] == res["mission"]["id"]):
                m["horario_inicio"], m["horario_fim"] = res["start"], res["end"]
                break
        save_missions_to_file(data)
        self.load_all()
        self.planner_updated.emit()

    def resizeEvent(self, event):
        super().resizeEvent(event); self.load_all()