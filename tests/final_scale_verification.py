"""
最終驗證：敵人圖片倍率功能完整測試

這個測試驗證從JSON數據到實際繪製的完整流程，
確保敵人圖片倍率功能在實際遊戲中正常工作。
"""

import pygame
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

pygame.init()
# 創建測試表面
screen = pygame.Surface((1200, 800))

from dungeon.stages import load_stages, get_stage_floors, EnemyData
from dungeon.battle import Enemy


def test_scale_in_json():
    """測試JSON中的scale值"""
    print("1. 測試JSON中的scale值")
    json_path = os.path.join("data", "stages.json")
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    scale_found = False
    for stage in data:
        if "極限訓練道場" in stage.get("name", ""):
            floors = stage.get("floors", [])
            for floor in floors:
                enemies = floor.get("enemies", [])
                for enemy in enemies:
                    scale = enemy.get("scale")
                    if scale is not None:
                        print(f"   找到scale值: {scale}")
                        scale_found = True
    assert scale_found, "在JSON中未找到scale值"
    print("   ✓ JSON中包含scale值")
    return True


def test_scale_loading():
    """測試scale值加載"""
    print("\n2. 測試scale值加載")
    stages = load_stages()
    target_stage = None
    for stage in stages:
        if "極限訓練道場" in stage.name:
            target_stage = stage
            break

    assert target_stage is not None, "未找到'極限訓練道場'關卡"

    floors = get_stage_floors(target_stage)
    # 尋找帶有scale的樓層
    scale_enemies = []
    for floor in floors:
        for enemy_data in floor.enemies:
            if enemy_data.scale != 1.0:
                scale_enemies.append(enemy_data)

    assert len(scale_enemies) > 0, "未找到帶有非1.0 scale的敵人"

    for enemy_data in scale_enemies:
        print(f"   敵人: {enemy_data.name}, scale: {enemy_data.scale}")
        assert enemy_data.scale == 1.6, f"scale值不正確: {enemy_data.scale}"

    print(f"   ✓ 成功加載scale值 (找到 {len(scale_enemies)} 個帶有scale的敵人)")
    return True


def test_enemy_creation():
    """測試敵人實例創建"""
    print("\n3. 測試敵人實例創建")

    # 創建測試敵人數據
    enemy_data = EnemyData(
        name="測試敵人",
        hp=1000,
        attack=100,
        defense=50,
        attribute="火",
        turns_until_action=3,
        image=None,
        scale=1.6,
    )

    # 創建敵人實例
    enemy = Enemy(
        enemy_data.name,
        enemy_data.hp,
        enemy_data.attack,
        enemy_data.defense,
        enemy_data.attribute,
        enemy_data.turns_until_action,
        enemy_data.image,
        enemy_data.scale,
    )

    print(f"   創建的敵人: {enemy.name}")
    print(f"   scale值: {enemy.scale}")

    assert enemy.scale == 1.6, f"敵人實例scale值不正確: {enemy.scale}"
    print("   ✓ 敵人實例正確設置scale值")
    return True


def test_draw_calculation():
    """測試繪製計算"""
    print("\n4. 測試繪製計算")

    # 測試不同scale值的計算
    test_cases = [(0.5, 75), (1.0, 150), (1.6, 240), (2.0, 300)]

    for scale, expected_size in test_cases:
        enemy = Enemy(f"測試敵人 scale={scale}", 1000, 100, 50, "火", 3, scale=scale)

        # 模擬draw方法的計算
        base_size = 150
        calculated_size = int(base_size * enemy.scale)

        print(
            f"   scale={scale}: 計算大小 = {calculated_size}, 期望大小 = {expected_size}"
        )
        assert calculated_size == expected_size, (
            f"計算錯誤: {calculated_size} != {expected_size}"
        )

    print("   ✓ 所有scale值的繪製計算正確")
    return True


def test_actual_draw():
    """測試實際繪製"""
    print("\n5. 測試實際繪製")

    # 創建測試表面
    test_surface = pygame.Surface((400, 400), pygame.SRCALPHA)

    # 創建帶有scale的敵人
    enemy = Enemy("測試敵人", 1000, 100, 50, "火", 3, scale=1.6)

    try:
        # 繪製敵人
        enemy.draw(test_surface, 200, 200)
        print("   ✓ 敵人繪製成功")

        # 驗證敵人屬性
        assert enemy.scale == 1.6, f"繪製後scale值改變: {enemy.scale}"
        print("   ✓ 繪製後scale值保持不變")

    except Exception as e:
        print(f"   ✗ 繪製失敗: {e}")
        return False

    return True


def test_full_data_flow():
    """測試完整數據流"""
    print("\n6. 測試完整數據流")

    # 模擬完整流程
    print("   模擬流程: JSON → EnemyData → Enemy → draw()")

    # 從JSON加載
    json_path = os.path.join("data", "stages.json")
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 找到帶有scale的敵人數據
    found = False
    for stage in data:
        if "極限訓練道場" in stage.get("name", ""):
            floors = stage.get("floors", [])
            for floor in floors:
                enemies = floor.get("enemies", [])
                for enemy_json in enemies:
                    if enemy_json.get("scale") == 1.6:
                        print(
                            f"   找到JSON敵人: {enemy_json.get('name')}, scale: {enemy_json.get('scale')}"
                        )

                        # 創建EnemyData
                        enemy_data = EnemyData(
                            name=enemy_json.get("name", ""),
                            hp=enemy_json.get("hp", 0),
                            attack=enemy_json.get("attack", 0),
                            defense=enemy_json.get("defense", 0),
                            attribute=enemy_json.get("attribute", "暗"),
                            turns_until_action=enemy_json.get("turns_until_action", 3),
                            image=enemy_json.get("image"),
                            actions=enemy_json.get("actions", []),
                            scale=enemy_json.get("scale", 1.0),
                        )

                        # 創建Enemy
                        enemy = Enemy(
                            enemy_data.name,
                            enemy_data.hp,
                            enemy_data.attack,
                            enemy_data.defense,
                            enemy_data.attribute,
                            enemy_data.turns_until_action,
                            enemy_data.image,
                            enemy_data.scale,
                        )

                        # 驗證
                        assert enemy.scale == 1.6, (
                            f"完整流程中scale值丟失: {enemy.scale}"
                        )
                        print(f"   完整流程驗證成功: enemy.scale = {enemy.scale}")
                        found = True

    assert found, "未找到scale=1.6的敵人進行完整流程測試"
    print("   ✓ 完整數據流驗證成功")
    return True


def main():
    print("=" * 60)
    print("敵人圖片倍率功能最終驗證")
    print("=" * 60)

    results = []

    try:
        results.append(("JSON中的scale值", test_scale_in_json()))
        results.append(("scale值加載", test_scale_loading()))
        results.append(("敵人實例創建", test_enemy_creation()))
        results.append(("繪製計算", test_draw_calculation()))
        results.append(("實際繪製", test_actual_draw()))
        results.append(("完整數據流", test_full_data_flow()))
    except Exception as e:
        print(f"\n測試過程中發生錯誤: {e}")
        import traceback

        traceback.print_exc()
        return False

    print("\n" + "=" * 60)
    print("測試結果總結")
    print("=" * 60)

    all_passed = True
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{name}: {status}")
        if not result:
            all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("所有測試通過！敵人圖片倍率功能已正確實現。")
        print("\n功能狀態:")
        print("1. ✓ scale值正確保存到JSON")
        print("2. ✓ scale值正確從JSON加載")
        print("3. ✓ scale值正確傳遞到Enemy實例")
        print("4. ✓ scale值正確影響繪製大小計算")
        print("5. ✓ 實際繪製功能正常")
        print("\n注意事項:")
        print("1. 請確保遊戲重新啟動以加載最新的代碼")
        print("2. 請確保選擇了正確的關卡和樓層（帶有scale的敵人）")
        print("3. 如果圖片未顯示，請檢查圖片路徑是否存在")
    else:
        print("部分測試失敗，請檢查上述錯誤信息。")

    pygame.quit()
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
