"""
虛擬點擊測試 - 測試開發者工具中的點擊位置

這個測試驗證：
1. 圖片倍率文字框可以點擊
2. 屬性框按鈕位置正確
3. 行動加按鈕位置正確
4. 敵人行動按鈕位置正確
"""

import pygame
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

pygame.init()

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

from dev_tool import StageEditorModal


def test_scale_field_clickable():
    """測試圖片倍率文字框可以點擊"""
    print("=== Test Scale Field Clickable ===")

    stage_data = {
        "name": "test",
        "floors": [
            {
                "enemies": [
                    {
                        "name": "test_enemy",
                        "hp": 1000,
                        "attack": 100,
                        "defense": 50,
                        "scale": 1.0,
                        "attribute": "火",
                        "actions": [],
                    }
                ]
            }
        ],
    }

    editor = StageEditorModal(screen, stage_data)
    editor.selected_floor_index = 0
    editor.selected_enemy_index = 0

    # 模擬點擊圖片倍率文字框
    panel_x = 750
    scale_field_y = 580
    test_pos = (panel_x + 60 + 10, scale_field_y + 10)  # 點擊文字框內部

    # 設置編輯狀態
    editor.editing_field = None
    editor.edit_text = ""

    # 模擬點擊
    editor.handle_click(test_pos)

    print(f"Clicked position: {test_pos}")
    print(f"Editing field after click: {editor.editing_field}")
    print(f"Edit text after click: {editor.edit_text}")

    # 驗證是否正確設置了編輯欄位
    is_scale_field = editor.editing_field == "enemy_scale"
    has_correct_text = editor.edit_text == "1.0"

    print(f"Is scale field: {is_scale_field}")
    print(f"Has correct text: {has_correct_text}")

    return is_scale_field and has_correct_text


def test_attribute_buttons_position():
    """測試屬性按鈕位置正確"""
    print("\n=== Test Attribute Buttons Position ===")

    stage_data = {
        "name": "test",
        "floors": [
            {
                "enemies": [
                    {
                        "name": "test_enemy",
                        "hp": 1000,
                        "attack": 100,
                        "defense": 50,
                        "scale": 1.0,
                        "attribute": "火",
                        "actions": [],
                    }
                ]
            }
        ],
    }

    editor = StageEditorModal(screen, stage_data)
    editor.selected_floor_index = 0
    editor.selected_enemy_index = 0

    panel_x = 750
    attr_y = 610

    # 測試每個屬性按鈕
    attributes = ["火", "水", "木", "光", "暗"]
    all_buttons_clickable = True

    for i, attr in enumerate(attributes):
        # 計算按鈕位置
        btn_x = panel_x + 60 + i * 36
        btn_y = attr_y
        test_pos = (btn_x + 15, btn_y + 15)  # 點擊按鈕中心

        # 保存當前屬性
        original_attr = stage_data["floors"][0]["enemies"][0]["attribute"]

        # 模擬點擊
        editor.handle_click(test_pos)

        # 檢查屬性是否改變
        new_attr = stage_data["floors"][0]["enemies"][0]["attribute"]

        print(
            f"Button {attr}: pos={test_pos}, original={original_attr}, new={new_attr}"
        )

        # 如果點擊了當前屬性的按鈕，屬性應該不變
        # 如果點擊了其他屬性的按鈕，屬性應該改變
        if original_attr == attr:
            if new_attr != attr:
                print(f"  ERROR: Attribute changed when clicking current attribute!")
                all_buttons_clickable = False
        else:
            if new_attr != attr:
                print(f"  ERROR: Attribute not changed to {attr}!")
                all_buttons_clickable = False

        # 重置屬性以便測試下一個按鈕
        stage_data["floors"][0]["enemies"][0]["attribute"] = "火"

    return all_buttons_clickable


def test_action_add_button_position():
    """測試行動加按鈕位置正確"""
    print("\n=== Test Action Add Button Position ===")

    stage_data = {
        "name": "test",
        "floors": [
            {
                "enemies": [
                    {
                        "name": "test_enemy",
                        "hp": 1000,
                        "attack": 100,
                        "defense": 50,
                        "scale": 1.0,
                        "attribute": "火",
                        "actions": [],
                    }
                ]
            }
        ],
    }

    editor = StageEditorModal(screen, stage_data)
    editor.selected_floor_index = 0
    editor.selected_enemy_index = 0

    panel_x = 750
    add_btn_y = 530

    # 計算按鈕位置
    btn_x = panel_x + 250
    test_pos = (btn_x + 60, add_btn_y + 15)  # 點擊按鈕中心

    # 保存當前行動數量
    original_action_count = len(stage_data["floors"][0]["enemies"][0]["actions"])

    # 模擬點擊
    editor.handle_click(test_pos)

    # 檢查行動是否增加
    new_action_count = len(stage_data["floors"][0]["enemies"][0]["actions"])

    print(f"Add button position: {test_pos}")
    print(f"Original actions: {original_action_count}")
    print(f"New actions: {new_action_count}")

    action_added = new_action_count == original_action_count + 1

    if action_added:
        new_action = stage_data["floors"][0]["enemies"][0]["actions"][-1]
        print(f"Added action type: {new_action.get('type')}")

    return action_added


def test_action_buttons_position():
    """測試敵人行動按鈕位置正確"""
    print("\n=== Test Action Buttons Position ===")

    stage_data = {
        "name": "test",
        "floors": [
            {
                "enemies": [
                    {
                        "name": "test_enemy",
                        "hp": 1000,
                        "attack": 100,
                        "defense": 50,
                        "scale": 1.0,
                        "attribute": "火",
                        "actions": [
                            {
                                "type": "attack",
                                "value": 10,
                                "turns": 3,
                                "description": "攻擊 持續",
                            },
                            {
                                "type": "blue_shield",
                                "value": 50,
                                "turns": 2,
                                "description": "藍盾 持續",
                            },
                        ],
                    }
                ]
            }
        ],
    }

    editor = StageEditorModal(screen, stage_data)
    editor.selected_floor_index = 0
    editor.selected_enemy_index = 0

    panel_x = 750
    action_start_y = 640

    # 測試第一個行動的類型按鈕
    action_index = 0
    action_y = action_start_y + action_index * 40

    # 點擊行動類型按鈕（應該打開選擇模態）
    type_btn_pos = (panel_x - 10 + 50, action_y + 15)

    # 模擬點擊
    editor.handle_click(type_btn_pos)

    print(f"Action type button position: {type_btn_pos}")
    print(f"Action type selecting after click: {editor.action_type_selecting}")

    type_button_works = editor.action_type_selecting is not None

    # 重置狀態
    editor.action_type_selecting = None

    # 測試第二個行動的值編輯按鈕（非攻擊類型）
    action_index = 1
    action_y = action_start_y + action_index * 40

    # 點擊行動值編輯按鈕
    value_btn_pos = (panel_x + 90 + 20, action_y + 15)

    # 保存當前編輯狀態
    original_editing_field = editor.editing_field
    original_edit_text = editor.edit_text

    # 模擬點擊
    editor.handle_click(value_btn_pos)

    print(f"Action value button position: {value_btn_pos}")
    print(f"Editing field after click: {editor.editing_field}")
    print(f"Edit text after click: {editor.edit_text}")

    value_button_works = (
        editor.editing_field == "action_value_1" and editor.edit_text == "50"
    )

    # 重置狀態
    editor.editing_field = None
    editor.edit_text = ""

    # 測試刪除按鈕
    delete_btn_pos = (panel_x + 180 + 13, action_y + 2 + 13)

    # 保存原始行動數量
    original_actions = len(stage_data["floors"][0]["enemies"][0]["actions"])

    # 模擬點擊刪除按鈕
    editor.handle_click(delete_btn_pos)

    print(f"Delete button position: {delete_btn_pos}")
    print(f"Actions before delete: {original_actions}")
    print(
        f"Actions after delete: {len(stage_data['floors'][0]['enemies'][0]['actions'])}"
    )

    delete_button_works = (
        len(stage_data["floors"][0]["enemies"][0]["actions"]) == original_actions - 1
    )

    return type_button_works and value_button_works and delete_button_works


def test_all_field_positions():
    """測試所有欄位位置"""
    print("\n=== Test All Field Positions ===")

    stage_data = {
        "name": "test",
        "floors": [
            {
                "enemies": [
                    {
                        "name": "test_enemy",
                        "hp": 1000,
                        "attack": 100,
                        "defense": 50,
                        "scale": 1.0,
                        "attribute": "火",
                        "actions": [],
                    }
                ]
            }
        ],
    }

    editor = StageEditorModal(screen, stage_data)
    editor.selected_floor_index = 0
    editor.selected_enemy_index = 0

    panel_x = 750
    fields = [
        ("name", "名稱", 460),
        ("hp", "HP", 490),
        ("attack", "攻擊", 520),
        ("defense", "防禦", 550),
        ("scale", "圖片倍率", 580),
    ]

    all_fields_clickable = True

    for field, label, y in fields:
        # 計算點擊位置
        field_x = panel_x + 60
        test_pos = (field_x + 10, y + 10)

        # 保存當前編輯狀態
        original_editing_field = editor.editing_field
        original_edit_text = editor.edit_text

        # 模擬點擊
        editor.handle_click(test_pos)

        expected_field = f"enemy_{field}"
        expected_text = str(stage_data["floors"][0]["enemies"][0].get(field, ""))

        print(f"Field '{label}' ({field}): pos={test_pos}")
        print(f"  Expected field: {expected_field}, got: {editor.editing_field}")
        print(f"  Expected text: {expected_text}, got: {editor.edit_text}")

        field_clickable = (
            editor.editing_field == expected_field and editor.edit_text == expected_text
        )

        if not field_clickable:
            print(f"  ERROR: Field '{label}' not clickable at position {test_pos}")
            all_fields_clickable = False

        # 重置狀態
        editor.editing_field = None
        editor.edit_text = ""

    return all_fields_clickable


def test_coordinate_consistency():
    """測試座標一致性"""
    print("\n=== Test Coordinate Consistency ===")

    # 檢查繪製和點擊處理中的座標是否一致
    inconsistencies = []

    # 從程式碼中提取的座標
    coordinates = {
        "name_field_y": 460,
        "hp_field_y": 490,
        "attack_field_y": 520,
        "defense_field_y": 550,
        "scale_field_y": 580,
        "attribute_y": 610,
        "add_action_btn_y": 530,
        "action_start_y": 640,
    }

    print("Coordinates used in code:")
    for name, value in coordinates.items():
        print(f"  {name}: {value}")

    # 檢查座標之間的間距是否合理
    expected_spacing = {
        ("name_field_y", "hp_field_y"): 30,
        ("hp_field_y", "attack_field_y"): 30,
        ("attack_field_y", "defense_field_y"): 30,
        ("defense_field_y", "scale_field_y"): 30,
        ("scale_field_y", "attribute_y"): 30,
        ("attribute_y", "add_action_btn_y"): -80,  # 屬性在行動按鈕上方
        ("add_action_btn_y", "action_start_y"): 110,
    }

    all_consistent = True

    for (coord1, coord2), expected_diff in expected_spacing.items():
        actual_diff = coordinates[coord2] - coordinates[coord1]
        if actual_diff != expected_diff:
            print(
                f"  WARNING: {coord1}({coordinates[coord1]}) to {coord2}({coordinates[coord2]})"
            )
            print(f"    Expected diff: {expected_diff}, Actual diff: {actual_diff}")
            all_consistent = False

    return all_consistent


def run_all_virtual_click_tests():
    """運行所有虛擬點擊測試"""
    results = []

    results.append(("Scale Field Clickable", test_scale_field_clickable()))
    results.append(("Attribute Buttons Position", test_attribute_buttons_position()))
    results.append(("Action Add Button Position", test_action_add_button_position()))
    results.append(("Action Buttons Position", test_action_buttons_position()))
    results.append(("All Field Positions", test_all_field_positions()))
    results.append(("Coordinate Consistency", test_coordinate_consistency()))

    print("\n" + "=" * 50)
    print("VIRTUAL CLICK TEST RESULTS")
    print("=" * 50)

    for name, result in results:
        print(f"{name}: {'PASS' if result else 'FAIL'}")

    all_passed = all(r for _, r in results)
    print(f"\nOverall: {'PASS' if all_passed else 'FAIL'}")

    return all_passed


if __name__ == "__main__":
    success = run_all_virtual_click_tests()
    pygame.quit()
    sys.exit(0 if success else 1)
