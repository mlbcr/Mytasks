import json
import os
import sys

import datetime

def get_data_dir():
    if sys.platform == "win32":
        base = os.getenv("APPDATA") 
    else:
        base = os.path.expanduser("~")

    data_dir = os.path.join(base, "MyTasks")
    os.makedirs(data_dir, exist_ok=True)
    return data_dir


DATA_DIR = get_data_dir()

DATA_FILE = os.path.join(DATA_DIR, "user.json")
MISSIONS_DATA = os.path.join(DATA_DIR, "missions.json")
FOCUS_DATA = os.path.join(DATA_DIR, "focus_history.json")
NOTES_FILE = os.path.join(DATA_DIR, "notes.json")
CONFIG_PATH = os.path.join(DATA_DIR, "config.json")

DEFAULT_CONFIG = {
    "categorias": {
        "inteligencia": {
            "nome": "INTELIGÊNCIA",
            "cor": "#5E12F8",
            "pontos": 0,
            "ativa": True
        },
        "forca": {
            "nome": "FORÇA",
            "cor": "#FF4C4C",
            "pontos": 0,
            "ativa": True
        },
        "vitalidade": {
            "nome": "VITALIDADE",
            "cor": "#32D583",
            "pontos": 0,
            "ativa": True
        },
        "criatividade": {
            "nome": "CRIATIVIDADE",
            "cor": "#FF9F43",
            "pontos": 0,
            "ativa": True
        },
        "social": {
            "nome": "SOCIAL",
            "cor": "#2D9CDB",
            "pontos": 0,
            "ativa": True
        }
    },
    "gameplay": {
    "min_foco_para_sequencia_min": 10,
    "tolerancia_falha_dias": 0,
    "xp_por_minuto_foco": 1
  }
}

def incrementar_conclusao_missao(mission_id):
    data = load_missions()
    for mission in data.get("missions", []):
        if mission.get("id") == mission_id:
            # Se a chave não existir, ele começa em 1, se existir, soma +1
            mission["completada_count"] = mission.get("completada_count", 0) + 1
            break
    save_missions_to_file(data)

def load_config():
    if not os.path.exists(CONFIG_PATH):
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    if "categorias" not in data:
        data["categorias"] = {}

    for key, cat in data["categorias"].items():
        default_cat = DEFAULT_CONFIG["categorias"].get(key)

        if default_cat:
            if "nome" not in cat:
                cat["nome"] = default_cat["nome"]
            if "cor" not in cat:
                cat["cor"] = default_cat["cor"]

        if "pontos" not in cat:
            cat["pontos"] = 0
        if "ativa" not in cat:
            cat["ativa"] = True
    
    if "gameplay" not in data:
        data["gameplay"] = DEFAULT_CONFIG["gameplay"].copy()

    if "min_foco_para_sequencia_min" not in data["gameplay"]:
        data["gameplay"]["min_foco_para_sequencia_min"] = 10

    save_config(data)
    return data

def save_config(data):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def load_missions():
    if not os.path.exists(MISSIONS_DATA): return {"missions": []}
    with open(MISSIONS_DATA, "r", encoding="utf-8") as f:
        return json.load(f)

def save_missions_to_file(data):
    with open(MISSIONS_DATA, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

DEFAULT_USER_DATA = {
    "usuario": {
        "nome": None,
        "nivel": 0,
        "xp": 0,
        "pontos_disponiveis": 0,
        "atributos": {
            "inteligencia": 0,
            "forca": 0,
            "vitalidade": 0,
            "criatividade": 0,
            "social": 0
        }
    },
    "sequencia": {
        "missoes_consecutivas": 0,
        "foco_consecutivo": 0
    },
    "foco": {
        "tempo_total_segundos": 0,
        "tempo_hoje_segundos": 0,
        "ultima_data": ""
    }
}

def load_name():
    if not os.path.exists(DATA_FILE): return None
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("usuario", {}).get("nome")
    except: return None

def save_name(nome):
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except: data = DEFAULT_USER_DATA.copy()
    else:
        data = DEFAULT_USER_DATA.copy()

    data["usuario"]["nome"] = nome
    
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_focus_history():
    if not os.path.exists(FOCUS_DATA): return {}
    try:
        with open(FOCUS_DATA, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception: return {}

def save_focus_history(data):
    with open(FOCUS_DATA, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_user():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_user(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_notes():
    if not os.path.exists(NOTES_FILE):
        return {"notes": []}

    try:
        with open(NOTES_FILE, "r", encoding="utf-8") as f:
            data = f.read().strip()

            if not data:
                return {"notes": []}

            return json.loads(data)

    except json.JSONDecodeError:
        return {"notes": []}


def save_notes(data):
    with open(NOTES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def verificar_sequencia_foco():
    try:
        user = load_user()
        config = load_config()
        history = load_focus_history()

        hoje = datetime.date.today().isoformat()
        ontem = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()

        limite_minutos = config.get("gameplay", {}).get("min_foco_para_sequencia_min", 10)
        
        tempo_hoje_min = history.get(hoje, {}).get("total_seconds", 0) / 60

        # Se atingiu o tempo mínimo e ainda não foi contabilizado hoje
        if tempo_hoje_min >= limite_minutos:
            if user["foco"].get("ultima_data_streak") != hoje:
                # Se focou ontem, soma. Se não, reseta para 1.
                tempo_ontem_min = history.get(ontem, {}).get("total_seconds", 0) / 60
                if tempo_ontem_min >= limite_minutos:
                    user["sequencia"]["foco_consecutivo"] += 1
                else:
                    user["sequencia"]["foco_consecutivo"] = 1
                
                user["foco"]["ultima_data_streak"] = hoje
        
        user["foco"]["ultima_data"] = hoje
        save_user(user)
    except Exception as e:
        print(f"Erro streak: {e}")