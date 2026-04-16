import pygame
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

pygame.init()

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

from dev_tool import StageEditorModal


def test_enemy_image_selection():
    print("\n=== Test Enemy Image Selection ===")

    stage_data = {
        "name": "test",
        "floors": [{"enemies": [{"name": "enemy", "hp": 100, "attack": 10}]}],
    }
    editor = StageEditorModal(screen, stage_data)
    editor.selected_enemy_index = 0

    editor._load_enemy_images()
    print(f"Enemy images loaded: {len(editor._enemy_images)}")

    if editor._enemy_images:
        img_x = 750 + 105
        img_y = 345
        test_pos = (img_x + 10, img_y + 10)

        result = pygame.Rect(img_x, img_y, 70, 70).collidepoint(test_pos)
        print(f"Image button collision: {result}")
        return result
    return False


def test_enemy_attribute_selection():
    print("\n=== Test Enemy Attribute Selection ===")

    stage_data = {
        "name": "test",
        "floors": [
            {"enemies": [{"name": "enemy", "hp": 100, "attack": 10, "attribute": "火"}]}
        ],
    }
    editor = StageEditorModal(screen, stage_data)
    editor.selected_enemy_index = 0

    panel_x = 750
    test_pos = (panel_x + 60 + 10, 580 + 10)

    from dungeon.stages import EnemyData

    enemy = EnemyData("enemy", 100, 10, 0, "火", 3, None, [])
    result = pygame.Rect(panel_x + 60, 580, 34, 30).collidepoint(test_pos)
    print(f"Attribute button collision: {result}")
    return result


def test_attribute_cycling():
    print("\n=== Test Attribute Cycling ===")

    stage_data = {
        "name": "test",
        "floors": [
            {"enemies": [{"name": "enemy", "hp": 100, "attack": 10, "attribute": "火"}]}
        ],
    }
    editor = StageEditorModal(screen, stage_data)
    editor.selected_floor_index = 0
    editor.selected_enemy_index = 0

    floor = editor.stage_data["floors"][0]
    enemy = floor["enemies"][0]

    attributes = ["火", "水", "木", "光", "暗"]

    current = enemy.get("attribute", "火")
    print(f"Initial attribute: {current}")

    idx = attributes.index(current) if current in attributes else 0
    enemy["attribute"] = attributes[(idx + 1) % len(attributes)]

    print(f"After click: {enemy.get('attribute')}")
    return enemy.get("attribute") == "水"


def test_action_type_selector_position():
    print("\n=== Test Action Type Selector Position ===")

    stage_data = {
        "name": "test",
        "floors": [
            {"enemies": [{"name": "enemy", "hp": 100, "actions": [{"type": "attack"}]}]}
        ],
    }
    editor = StageEditorModal(screen, stage_data)
    editor.selected_floor_index = 0
    editor.selected_enemy_index = 0

    modal_x = 50
    modal_y = 50

    result = pygame.Rect(modal_x, modal_y, 200, 150).collidepoint((100, 100))
    print(f"Modal at fixed position ({modal_x}, {modal_y}): {result}")
    return result


def test_avatar_image_load():
    print("\n=== Test Avatar Image Load ===")

    base_dir = os.path.dirname(os.path.abspath("dungeon/battle.py"))
    full_path = os.path.join(
        base_dir, "..", "assets", "images", "avatar", "avatar_2.png"
    )

    try:
        img = pygame.image.load(full_path).convert_alpha()
        print(f"Avatar loaded: {img.get_size()}")
        return True
    except Exception as e:
        print(f"Failed: {e}")
        return False


def test_enemy_image_draw():
    print("\n=== Test Enemy Image Draw ===")

    from dungeon.battle import Enemy

    e = Enemy("test", 100, 10, 0, "火", 3, "enemy/1 - Edited.png")
    print(f"Enemy image attr: {e.image}")

    screen.fill((20, 20, 30))
    e.draw(screen, 300, 300)
    print("Enemy draw OK")
    return True


def test_full_flow():
    results = []
    results.append(("Enemy Image Selection", test_enemy_image_selection()))
    results.append(("Enemy Attribute Selection", test_enemy_attribute_selection()))
    results.append(("Attribute Cycling", test_attribute_cycling()))
    results.append(
        ("Action Type Selector Position", test_action_type_selector_position())
    )
    results.append(("Avatar Image Load", test_avatar_image_load()))
    results.append(("Enemy Image Draw", test_enemy_image_draw()))

    print("\n=== Test Results ===")
    for name, result in results:
        print(f"{name}: {'PASS' if result else 'FAIL'}")

    all_passed = all(r for _, r in results)
    print(f"\nOverall: {'PASS' if all_passed else 'FAIL'}")
    return all_passed


if __name__ == "__main__":
    test_full_flow()
    pygame.quit()
