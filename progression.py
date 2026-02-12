def xp_needed_for_level(level):
    return int(40 + (level * 0.3))


def add_xp_to_user(user_data, amount):
    user = user_data["usuario"]

    user["xp"] += amount

    while user["xp"] >= xp_needed_for_level(user["nivel"]):
        user["xp"] -= xp_needed_for_level(user["nivel"])
        user["nivel"] += 1
        user["pontos_disponiveis"] += 1  

    return user_data

def get_rank(level):
    if level >= 350:
        return "X"
    elif level >= 200:
        return "SSS"
    elif level >= 100:
        return "SS"
    elif level >= 50:
        return "S"
    elif level >= 40:
        return "A"
    elif level >= 30:
        return "B"
    elif level >= 20:
        return "C"
    elif level >= 10:
        return "D"
    else:
        return "E"
