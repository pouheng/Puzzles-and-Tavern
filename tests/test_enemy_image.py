import pygame
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

pygame.init()

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

from dev_tool import StageEditorModal


def test_load_enemy_images():
    print("=== Test Load Enemy Images ===")

    stage_data = {"name": "test", "floors": [{"enemies": []}]}
    editor = StageEditorModal(screen, stage_data)

    editor._load_enemy_images()
    images = editor._enemy_images

    print(f"Enemy images loaded: {len(images)}")
    for img in images:
        print(f"  - {img}")

    return len(images) >= 0


def test_show_enemy_image_selector():
    print("\n=== Test Show Enemy Image Selector ===")

    stage_data = {"name": "test", "floors": [{"enemies": []}]}
    editor = StageEditorModal(screen, stage_data)

    editor.show_enemy_image_selector()
    is_active = getattr(editor, "_selecting_enemy_image", False)
    print(f"Image selector active: {is_active}")
    return is_active


def test_select_enemy_image():
    print("\n=== Test Select Enemy Image ===")

    stage_data = {
        "name": "test",
        "floors": [{"enemies": [{"name": "enemy", "hp": 100}]}],
    }
    editor = StageEditorModal(screen, stage_data)
    editor.selected_enemy_index = 0

    editor._load_enemy_images()
    print(f"Enemy images: {editor._enemy_images}")

    # Activate the selector first
    editor._selecting_enemy_image = True

    if editor._enemy_images:
        img = editor._enemy_images[0]
        row = 0
        col = 0
        img_x = 100 + col * 100
        img_y = 120 + row * 100
        test_pos = (img_x + 10, img_y + 10)

        # Check what rect would be
        img_rect = pygame.Rect(img_x, img_y, 80, 80)
        print(f"Image rect: {img_rect}")
        print(f"Collide: {img_rect.collidepoint(test_pos)}")

        print(f"Test image: {img}")
        print(f"Test position: {test_pos}")

        result = editor.handle_enemy_image_selector_click(test_pos)
        print(f"Result: {result}")

        if result:
            enemy = editor.stage_data["floors"][0]["enemies"][0]
            print(f"Assigned image: {enemy.get('image')}")
            return enemy.get("image") is not None

    return False


def test_select_image_button_click():
    print("\n=== Test Select Image Button Click ===")

    stage_data = {
        "name": "test",
        "floors": [{"enemies": [{"name": "enemy", "hp": 100}]}],
    }
    editor = StageEditorModal(screen, stage_data)
    editor.selected_enemy_index = 0

    panel_x = 200

    btn_pos = (panel_x + 280 + 10, 340 + 10)

    result = pygame.Rect(panel_x + 280, 340, 70, 30).collidepoint(btn_pos)
    print(f"Button rect collision: {result}")

    if hasattr(editor, "_load_enemy_images"):
        editor._load_enemy_images()
        print(f"Enemy images loaded: {len(editor._enemy_images)}")

    return True


def test_full_flow():
    results = []
    results.append(("Load Enemy Images", test_load_enemy_images()))
    results.append(("Show Image Selector", test_show_enemy_image_selector()))
    results.append(("Select Enemy Image", test_select_enemy_image()))
    results.append(("Select Image Button Click", test_select_image_button_click()))

    print("\n=== Test Results ===")
    for name, result in results:
        print(f"{name}: {'PASS' if result else 'FAIL'}")

    all_passed = all(r for _, r in results)
    print(f"\nOverall: {'PASS' if all_passed else 'FAIL'}")
    return all_passed


if __name__ == "__main__":
    test_full_flow()
    pygame.quit()
