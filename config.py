SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 900
FPS = 60
GAME_TITLE = "轉珠遊戲 - PAD Clone"

BG_COLOR = (30, 30, 40)

INVENTORY_GRID_COLS = 8
INVENTORY_GRID_ROWS = 5
INVENTORY_CELL_SIZE = 130
INVENTORY_MARGIN = 20
INVENTORY_START_X = 50
INVENTORY_START_Y = 50

CARD_WIDTH = 90
CARD_HEIGHT = 90
CARD_BORDER_WIDTH = 3

RARITY_COLORS = {
    1: (150, 150, 150),
    2: (100, 200, 100),
    3: (100, 150, 255),
    4: (200, 150, 255),
    5: (255, 200, 100),
    6: (255, 100, 100),
}

ATTRIBUTE_COLORS = {
    "火": (255, 80, 80),
    "水": (80, 150, 255),
    "木": (80, 200, 80),
    "光": (255, 255, 150),
    "暗": (180, 100, 200),
    "心": (255, 150, 180),
}

ORB_COLORS = {
    "火": (255, 80, 80),
    "水": (80, 150, 255),
    "木": (80, 200, 80),
    "光": (255, 255, 150),
    "暗": (180, 100, 200),
    "心": (255, 150, 180),
}

RACE_NAMES = {
    "神": "神",
    "龍": "龍",
    "獸": "獸",
    "魔": "魔",
    "機械": "機械",
    "人": "人",
    "妖": "妖",
}

BOARD_COLS = 6
BOARD_ROWS = 5
BOARD_CELL_SIZE = 70
BOARD_MARGIN = 4
BOARD_START_X = (SCREEN_WIDTH - BOARD_COLS * (BOARD_CELL_SIZE + BOARD_MARGIN)) // 2

ORB_TYPES = ["火", "水", "木", "光", "暗", "心"]

ATTRIBUTE_ADVANTAGE = {
    "火": {"木": 2.0},
    "水": {"火": 2.0},
    "木": {"水": 2.0},
    "光": {"暗": 2.0},
    "暗": {"光": 2.0},
}

SUB_ATTRIBUTE_SAME = 0.1
SUB_ATTRIBUTE_DIFFERENT = 0.3

MASS_ATTACK_MIN_ORBS = 5

ORB_SKINS = {
    "default": {
        "name": "預設",
        "火": "orbs/default/fire",
        "水": "orbs/default/water",
        "木": "orbs/default/wood",
        "光": "orbs/default/light",
        "暗": "orbs/default/dark",
        "心": "orbs/default/heart",
    },
}

DEFAULT_ORB_SKIN = "default"


def get_current_orb_skin():
    import os
    import json

    base_path = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_path, "data", "orb_skins.json")
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("default", "default")
    return "default"
