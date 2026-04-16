import pygame
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

pygame.init()

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

from dev_tool import DialogueEditorModal
from dungeon.stages import DialogueEntry


def test_add_entry_with_name():
    print("=== Test Add Entry Includes Name Field ===")

    editor = DialogueEditorModal(screen, "test")
    editor.dialogue_data = {"name": "test", "entries": []}

    test_pos = (160, 130)
    editor.handle_click(test_pos)

    entries = editor.dialogue_data.get("entries", [])
    print(f"Entry count: {len(entries)}")
    print(f"Entry has name field: {'name' in entries[0]}")
    return len(entries) == 1 and "name" in entries[0]


def test_edit_name_field():
    print("\n=== Test Edit Name Field ===")

    editor = DialogueEditorModal(screen, "test")
    editor.dialogue_data = {
        "name": "test",
        "entries": [{"text": "hello", "name": "", "avatar": None, "position": "left"}],
    }

    test_pos = (400, 175)
    editor.handle_click(test_pos)

    print(f"Editing name index: {editor.editing_entry_name}")
    print(f"Edit text: '{editor.edit_text}'")

    if editor.editing_entry_name is not None:
        editor.edit_text = "主角"
        editor.apply_edit()

        entries = editor.dialogue_data.get("entries", [])
        print(f"Name after: '{entries[0].get('name')}'")
        return entries[0].get("name") == "主角"
    return False


def test_dialogue_entry_name():
    print("\n=== Test DialogueEntry Name ===")

    entry = DialogueEntry("avatar/test.png", "hello", "left", "on_enter_floor", "主角")
    print(f"avatar: {entry.avatar_image}")
    print(f"text: {entry.text}")
    print(f"name: {entry.name}")
    print(f"trigger: {entry.trigger}")

    return entry.name == "主角"


def test_avatar_button():
    print("\n=== Test Avatar Button ===")

    editor = DialogueEditorModal(screen, "test")
    editor.dialogue_data = {
        "name": "test",
        "entries": [{"text": "test", "name": "", "avatar": None, "position": "left"}],
    }

    test_pos = (510, 175)
    editor.handle_click(test_pos)

    result = hasattr(editor, "_selecting_avatar") and editor._selecting_avatar
    print(f"Avatar selector active: {result}")
    return result


def test_delete_entry():
    print("\n=== Test Delete Entry ===")

    editor = DialogueEditorModal(screen, "test")
    editor.dialogue_data = {
        "name": "test",
        "entries": [
            {"text": "entry1", "name": "A", "avatar": None, "position": "left"},
            {"text": "entry2", "name": "B", "avatar": None, "position": "left"},
        ],
    }

    test_pos = (590, 180)
    editor.handle_click(test_pos)

    entries = editor.dialogue_data.get("entries", [])
    print(f"Remaining: {[e['text'] for e in entries]}")
    return len(entries) == 1


def test_edit_text():
    print("\n=== Test Edit Text ===")

    editor = DialogueEditorModal(screen, "test")
    editor.dialogue_data = {
        "name": "test",
        "entries": [
            {"text": "original", "name": "", "avatar": None, "position": "left"}
        ],
    }

    test_pos = (170, 175)
    editor.handle_click(test_pos)

    if editor.editing_entry_text is not None:
        editor.edit_text = "edited"
        editor.apply_edit()

        entries = editor.dialogue_data.get("entries", [])
        print(f"Text after: {entries[0]['text']}")
        return entries[0]["text"] == "edited"
    return False


def test_save():
    print("\n=== Test Save With Name ===")

    editor = DialogueEditorModal(screen, "test_save")
    editor.dialogue_data = {
        "name": "test",
        "entries": [
            {"text": "hello", "name": "主角", "avatar": None, "position": "left"}
        ],
    }
    editor.dialogue_key = "test_save"

    test_pos = (SCREEN_WIDTH - 180 + 40, 60 + 15)
    editor.handle_click(test_pos)

    print(f"Saved: {editor.result}")
    entries = editor.dialogue_data.get("entries", [])
    print(f"Name: {entries[0].get('name')}")
    return editor.result == "test_save" and entries[0].get("name") == "主角"


def test_name_display():
    print("\n=== Test Name Display in Draw ===")

    editor = DialogueEditorModal(screen, "test")
    editor.dialogue_data = {
        "name": "test",
        "entries": [
            {"text": "hello", "name": "主角", "avatar": None, "position": "left"}
        ],
    }

    try:
        editor.draw()
        print("Draw succeeded")
        return True
    except Exception as e:
        print(f"Draw failed: {e}")
        return False


def test_full_flow():
    results = []
    results.append(("Add Entry", test_add_entry_with_name()))
    results.append(("Edit Name", test_edit_name_field()))
    results.append(("DialogueEntry", test_dialogue_entry_name()))
    results.append(("Avatar Button", test_avatar_button()))
    results.append(("Delete Entry", test_delete_entry()))
    results.append(("Edit Text", test_edit_text()))
    results.append(("Save", test_save()))
    results.append(("Name Display", test_name_display()))

    print("\n=== Test Results ===")
    for name, result in results:
        print(f"{name}: {'PASS' if result else 'FAIL'}")

    all_passed = all(r for _, r in results)
    print(f"\nOverall: {'PASS' if all_passed else 'FAIL'}")
    return all_passed


if __name__ == "__main__":
    test_full_flow()
    pygame.quit()
