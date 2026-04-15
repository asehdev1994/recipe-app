import json

# =========================
# FILE PATHS
# =========================
DATA_FILE = "recipes.json"
SESSION_FILE = "shopping_sessions.json"

# =========================
# LOAD / SAVE RECIPES
# =========================
def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {
            "units": ["g", "kg", "ml", "l", "tsp", "tbsp", "cup", "pcs"],
            "recipes": {}
        }

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# =========================
# LOAD / SAVE SESSIONS
# =========================
def load_sessions():
    try:
        with open(SESSION_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_sessions(data):
    with open(SESSION_FILE, "w") as f:
        json.dump(data, f)