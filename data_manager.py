import json
import os
import sys

DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "user.json")
MISSIONS_DATA = os.path.join(DATA_DIR, "missions.json")
FOCUS_DATA = os.path.join(DATA_DIR, "focus_history.json")

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

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