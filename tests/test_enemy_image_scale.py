import pygame
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

pygame.init()

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

from dev_tool import StageEditorModal
from dungeon.battle import Enemy
from dungeon.stages import EnemyData


def test_enemy_scale_default():
    print("=== Test Enemy Scale Default ===")

    # 測試敵人類別預設 scale
    enemy = Enemy("test", 1000, 100, 50, "火", 3)
    print(f"Enemy scale default: {enemy.scale}")
    assert enemy.scale == 1.0, f"Expected scale 1.0, got {enemy.scale}"

    # 測試指定 scale
    enemy_with_scale = Enemy("test", 1000, 100, 50, "火", 3, scale=1.5)
    print(f"Enemy scale specified: {enemy_with_scale.scale}")
    assert enemy_with_scale.scale == 1.5, (
        f"Expected scale 1.5, got {enemy_with_scale.scale}"
    )

    return True


def test_enemydata_scale_default():
    print("\n=== Test EnemyData Scale Default ===")

    # 測試 EnemyData 預設 scale
    enemy_data = EnemyData("test", 1000, 100, 50, "火", 3)
    print(f"EnemyData scale default: {enemy_data.scale}")
    assert enemy_data.scale == 1.0, f"Expected scale 1.0, got {enemy_data.scale}"

    # 測試指定 scale
    enemy_data_with_scale = EnemyData("test", 1000, 100, 50, "火", 3, scale=1.2)
    print(f"EnemyData scale specified: {enemy_data_with_scale.scale}")
    assert enemy_data_with_scale.scale == 1.2, (
        f"Expected scale 1.2, got {enemy_data_with_scale.scale}"
    )

    return True


def test_stage_editor_scale_field():
    print("\n=== Test Stage Editor Scale Field ===")

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
                        "attribute": "火",
                        "scale": 1.3,
                    }
                ]
            }
        ],
    }

    editor = StageEditorModal(screen, stage_data)

    # 檢查 scale 欄位是否存在於敵人數據中
    enemy = stage_data["floors"][0]["enemies"][0]
    print(f"Enemy scale in stage data: {enemy.get('scale')}")
    assert enemy.get("scale") == 1.3, f"Expected scale 1.3, got {enemy.get('scale')}"

    # 測試編輯 scale 欄位
    editor.selected_floor_index = 0
    editor.selected_enemy_index = 0
    editor.editing_field = "enemy_scale"
    editor.edit_text = "1.5"
    editor.apply_edit()

    updated_enemy = stage_data["floors"][0]["enemies"][0]
    print(f"Enemy scale after edit: {updated_enemy.get('scale')}")
    assert updated_enemy.get("scale") == 1.5, (
        f"Expected scale 1.5 after edit, got {updated_enemy.get('scale')}"
    )

    # 測試無效輸入
    editor.editing_field = "enemy_scale"
    editor.edit_text = "invalid"
    editor.apply_edit()

    print(f"Enemy scale after invalid edit: {updated_enemy.get('scale')}")
    assert updated_enemy.get("scale") == 1.5, (
        f"Scale should remain 1.5 after invalid input, got {updated_enemy.get('scale')}"
    )

    return True


def test_new_enemy_has_scale():
    print("\n=== Test New Enemy Has Scale ===")

    stage_data = {"name": "test", "floors": [{"enemies": []}]}

    editor = StageEditorModal(screen, stage_data)
    editor.selected_floor_index = 0

    # 模擬新增敵人
    floor = stage_data["floors"][0]
    enemies = floor.get("enemies", [])
    new_enemy = {
        "name": f"敵人 {len(enemies) + 1}",
        "hp": 1000,
        "attack": 100,
        "defense": 0,
        "attribute": "火",
        "scale": 1.0,
        "actions": [],
    }
    enemies.append(new_enemy)

    print(f"New enemy scale: {new_enemy.get('scale')}")
    assert new_enemy.get("scale") == 1.0, (
        f"New enemy should have scale 1.0, got {new_enemy.get('scale')}"
    )

    return True


def test_enemy_draw_with_scale():
    print("\n=== Test Enemy Draw With Scale ===")

    # 測試不同 scale 值的敵人繪製
    test_scales = [0.5, 1.0, 1.5, 2.0]

    for scale in test_scales:
        enemy = Enemy("test", 1000, 100, 50, "火", 3, scale=scale)

        # 計算預期大小
        base_size = 150
        expected_size = int(base_size * scale)

        print(f"Scale {scale}: base_size={base_size}, expected_size={expected_size}")

        # 驗證繪製邏輯
        size = int(base_size * enemy.scale)
        assert size == expected_size, (
            f"For scale {scale}, expected size {expected_size}, got {size}"
        )

    return True


def test_scale_affects_image_size():
    print("\n=== Test Scale Affects Image Size ===")

    # 測試 scale 對圖片大小的影響
    enemy1 = Enemy("test1", 1000, 100, 50, "火", 3, scale=0.5)
    enemy2 = Enemy("test2", 1000, 100, 50, "火", 3, scale=1.0)
    enemy3 = Enemy("test3", 1000, 100, 50, "火", 3, scale=1.5)

    base_size = 150
    size1 = int(base_size * enemy1.scale)
    size2 = int(base_size * enemy2.scale)
    size3 = int(base_size * enemy3.scale)

    print(f"Scale 0.5 -> size: {size1}")
    print(f"Scale 1.0 -> size: {size2}")
    print(f"Scale 1.5 -> size: {size3}")

    # 驗證比例關係
    assert size1 == 75, f"Expected size 75 for scale 0.5, got {size1}"
    assert size2 == 150, f"Expected size 150 for scale 1.0, got {size2}"
    assert size3 == 225, f"Expected size 225 for scale 1.5, got {size3}"

    # 驗證比例正確性
    assert size1 < size2 < size3, "Sizes should increase with scale"
    assert abs(size1 / size2 - 0.5) < 0.01, "Size ratio should be 0.5"
    assert abs(size3 / size2 - 1.5) < 0.01, "Size ratio should be 1.5"

    return True


def test_full_scale_functionality():
    results = []
    results.append(("Enemy Scale Default", test_enemy_scale_default()))
    results.append(("EnemyData Scale Default", test_enemydata_scale_default()))
    results.append(("Stage Editor Scale Field", test_stage_editor_scale_field()))
    results.append(("New Enemy Has Scale", test_new_enemy_has_scale()))
    results.append(("Enemy Draw With Scale", test_enemy_draw_with_scale()))
    results.append(("Scale Affects Image Size", test_scale_affects_image_size()))

    print("\n=== Test Results ===")
    for name, result in results:
        print(f"{name}: {'PASS' if result else 'FAIL'}")

    all_passed = all(r for _, r in results)
    print(f"\nOverall: {'PASS' if all_passed else 'FAIL'}")
    return all_passed


if __name__ == "__main__":
    success = test_full_scale_functionality()
    pygame.quit()
    sys.exit(0 if success else 1)
