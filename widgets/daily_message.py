import random
from datetime import date
from data_manager import load_config, save_config

DEFAULT_MESSAGES = [
    "Você consegue.",
    "Um pequeno progresso ainda é progresso.",
    "Disciplina vence motivação.",
    "Seu eu do futuro agradece.",
    "Continue avançando."
]


def get_daily_message():
    config = load_config()

    if "daily_message" not in config:
        return random.choice(DEFAULT_MESSAGES)

    msg = config["daily_message"].get("mensagem", "")

    if not msg:
        return random.choice(DEFAULT_MESSAGES)

    return msg