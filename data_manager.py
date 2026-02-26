import json
import os
import sys


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
    }
}

def load_config():
    if not os.path.exists(CONFIG_PATH):
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    if "categorias" not in data:
        data["categorias"] = {}

    for key, default_cat in DEFAULT_CONFIG["categorias"].items():
        if key not in data["categorias"]:
            data["categorias"][key] = default_cat.copy()
        else:
            cat = data["categorias"][key]
            if "nome" not in cat:
                cat["nome"] = default_cat["nome"]
            if "cor" not in cat:
                cat["cor"] = default_cat["cor"]
            if "pontos" not in cat:
                cat["pontos"] = 0
            if "ativa" not in cat:
                cat["ativa"] = True

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