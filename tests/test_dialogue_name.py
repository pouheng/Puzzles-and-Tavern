import pygame
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

pygame.init()

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

from dev_tool import DialogueEditorModal


def test_click_name_field():
    print("=== Test Click Name Field ===")

    editor = DialogueEditorModal(screen, "test")
    editor.dialogue_data = {
        "name": "test",
        "entries": [{"text": "hello", "name": "", "avatar": None, "position": "left"}],
    }

    i = 0
    entry_y = 160 + i * 50
    name_rect = pygame.Rect(370, entry_y + 5, 120, 25)
    print(f"name_rect: {name_rect}")

    test_pos = (400, 175)
    print(f"Click position: {test_pos}")
    print(f"Collide: {name_rect.collidepoint(test_pos)}")

    editor.handle_click(test_pos)

    print(f"Editing name: {editor.editing_entry_name}")
    print(f"Edit text: '{editor.edit_text}'")

    return editor.editing_entry_name == 0


def test_edit_name():
    print("\n=== Test Edit Name ===")

    editor = DialogueEditorModal(screen, "test")
    editor.dialogue_data = {
        "name": "test",
        "entries": [{"text": "hello", "name": "", "avatar": None, "position": "left"}],
    }

    test_pos = (400, 175)
    editor.handle_click(test_pos)

    if editor.editing_entry_name is not None:
        editor.edit_text = "主角"
        editor.apply_edit()

        entries = editor.dialogue_data.get("entries", [])
        print(f"Name after edit: '{entries[0].get('name')}'")
        return entries[0].get("name") == "主角"

    return False


def test_click_text_field():
    print("\n=== Test Click Text Field ===")

    editor = DialogueEditorModal(screen, "test")
    editor.dialogue_data = {
        "name": "test",
        "entries": [{"text": "hello", "name": "", "avatar": None, "position": "left"}],
    }

    text_rect = pygame.Rect(160, 165, 200, 25)
    test_pos = (200, 175)
    print(f"text_rect: {text_rect}, collide: {text_rect.collidepoint(test_pos)}")

    editor.handle_click(test_pos)

    print(f"Editing text: {editor.editing_entry_text}")
    return editor.editing_entry_text == 0


def test_full_flow():
    results = []
    results.append(("Click Name", test_click_name_field()))
    results.append(("Edit Name", test_edit_name()))
    results.append(("Click Text", test_click_text_field()))

    print("\n=== Test Results ===")
    for name, result in results:
        print(f"{name}: {'PASS' if result else 'FAIL'}")

    all_passed = all(r for _, r in results)
    print(f"\nOverall: {'PASS' if all_passed else 'FAIL'}")
    return all_passed


if __name__ == "__main__":
    test_full_flow()
    pygame.quit()
