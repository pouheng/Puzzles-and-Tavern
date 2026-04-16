import pygame
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

pygame.init()

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

from dev_tool import StageEditorModal


def test_buttons():
    print("=== Test Enemy Panel Buttons ===")

    stage_data = {
        "name": "test",
        "floors": [{"enemies": [{"name": "enemy", "hp": 100, "actions": []}]}],
    }
    editor = StageEditorModal(screen, stage_data)
    editor.selected_enemy_index = 0

    panel_x = 750

    btn1_click = pygame.Rect(panel_x + 280, 340, 70, 30)
    print(f"Image button rect: {btn1_click}")

    btn2_click = pygame.Rect(panel_x + 130, 460, 120, 30)
    print(f"Action button rect: {btn2_click}")

    test_pos1 = (panel_x + 285, 350)
    test_pos2 = (panel_x + 135, 470)

    print(
        f"Test pos1 (should hit image btn): {test_pos1}, collide: {btn1_click.collidepoint(test_pos1)}"
    )
    print(
        f"Test pos2 (should hit action btn): {test_pos2}, collide: {btn2_click.collidepoint(test_pos2)}"
    )

    editor.handle_click(test_pos1)
    is_selecting = getattr(editor, "_selecting_enemy_image", False)
    print(f"After test_pos1: _selecting_enemy_image={is_selecting}")

    editor._selecting_enemy_image = False
    editor.handle_click(test_pos2)
    print(f"After test_pos2: editing_field={editor.editing_field}")

    print(f"\nTest: PASS" if is_selecting else "Test: FAIL")
    return is_selecting


def test_draw_positions():
    print("\n=== Check Draw Button Positions ===")

    stage_data = {
        "name": "test",
        "floors": [
            {
                "enemies": [
                    {
                        "name": "enemy",
                        "hp": 100,
                        "actions": [{"type": "attack", "value": 10, "turns": 3}],
                    }
                ]
            }
        ],
    }
    editor = StageEditorModal(screen, stage_data)
    editor.selected_enemy_index = 0

    try:
        editor.draw()
        print("Draw succeeded")
    except Exception as e:
        print(f"Draw failed: {e}")


def test_full_flow():
    results = []
    results.append(("Buttons", test_buttons()))

    print("\n=== Test Results ===")
    for name, result in results:
        print(f"{name}: {'PASS' if result else 'FAIL'}")

    all_passed = all(r for _, r in results)
    print(f"\nOverall: {'PASS' if all_passed else 'FAIL'}")
    return all_passed


if __name__ == "__main__":
    test_full_flow()
    pygame.quit()
