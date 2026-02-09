import json
import os
import sys

DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "user.json")
MISSIONS_DATA = os.path.join(DATA_DIR, "missions.json")

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

def load_name():
    if not os.path.exists(DATA_FILE): return None
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("usuario", {}).get("nome")

def save_name(nome):
    data = {"usuario": {"nome": nome}}
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)