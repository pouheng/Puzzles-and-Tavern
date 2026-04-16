import pygame
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

pygame.init()

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

from dev_tool import StageEditorModal


def test_action_button():
    print("=== Test Action Button Area ===")

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

    panel_x = 750

    action_y = 610

    action_btn_click = pygame.Rect(panel_x + 130, 460, 120, 30)
    action_btn_draw = pygame.Rect(panel_x, action_y, 100, 30)

    print(f"Action button click rect: {action_btn_click}")
    print(f"Action button draw rect: {action_btn_draw}")

    test_pos = (panel_x + 150, 475)
    print(f"Test pos: {test_pos}")
    print(f"Click rect collide: {action_btn_click.collidepoint(test_pos)}")
    print(f"Draw rect collide: {action_btn_draw.collidepoint(test_pos)}")

    editor.handle_click(test_pos)
    print(f"After click editing_field: {editor.editing_field}")
    print(f"Action type selecting: {editor.action_type_selecting}")

    if editor.action_type_selecting:
        print("SUCCESS: Action button clicked")
        return True

    print("FAIL: Action button not clicked")
    return False


def test_action_field_edit():
    print("\n=== Test Action Value/Edit Fields ===")

    stage_data = {
        "name": "test",
        "floors": [
            {
                "enemies": [
                    {
                        "name": "enemy",
                        "hp": 100,
                        "actions": [{"type": "blue_shield", "value": 10, "turns": 3}],
                    }
                ]
            }
        ],
    }
    editor = StageEditorModal(screen, stage_data)
    editor.selected_enemy_index = 0

    panel_x = 750
    action_y = 610

    test_pos_value = (panel_x + 110, 625)
    val_rect = pygame.Rect(panel_x + 100, action_y, 40, 30)
    print(
        f"Value rect: {val_rect}, test pos: {test_pos_value}, collide: {val_rect.collidepoint(test_pos_value)}"
    )

    test_pos_turns = (panel_x + 155, 625)
    turns_rect = pygame.Rect(panel_x + 145, action_y, 40, 30)
    print(
        f"Turns rect: {turns_rect}, test pos: {test_pos_turns}, collide: {turns_rect.collidepoint(test_pos_turns)}"
    )

    editor.handle_click(test_pos_value)
    print(f"After value click: {editor.editing_field}")

    editor.handle_click(test_pos_turns)
    print(f"After turns click: {editor.editing_field}")

    return True


def test_full():
    results = []
    results.append(("Action Button", test_action_button()))
    results.append(("Action Fields", test_action_field_edit()))

    print("\n=== Results ===")
    for name, result in results:
        print(f"{name}: {'PASS' if result else 'FAIL'}")

    return all(r for _, r in results)


if __name__ == "__main__":
    test_full()
    pygame.quit()
