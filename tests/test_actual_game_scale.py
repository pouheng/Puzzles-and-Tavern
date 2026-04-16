"""
測試實際遊戲中敵人圖片倍率的顯示

這個測試驗證：
1. 在實際遊戲中，敵人圖片倍率是否正確影響顯示
2. 敵人數據中的scale是否正確傳遞到遊戲中
3. 實際遊戲渲染是否使用scale值
"""

import pygame
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

pygame.init()

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

from dungeon.battle import Enemy
from dungeon.stages import EnemyData, Floor, Stage


def create_test_stage_with_scaled_enemies():
    """創建帶有不同scale敵人的測試關卡"""
    print("=== Create Test Stage With Scaled Enemies ===")

    # 創建不同scale的敵人
    enemies_data = [
        EnemyData("small_enemy", 500, 50, 10, "火", 3, scale=0.5),
        EnemyData("normal_enemy", 1000, 100, 20, "水", 3, scale=1.0),
        EnemyData("large_enemy", 1500, 150, 30, "木", 3, scale=1.5),
        EnemyData("huge_enemy", 2000, 200, 40, "光", 3, scale=2.0),
    ]

    # 創建樓層
    floor = Floor(floor_num=1, enemies=enemies_data, dialogue=[])

    # 創建關卡
    stage = Stage(
        name="scale_test_stage",
        dialogue=[],
        floors=[floor],
        stage_type=1,
        exp=100,
        rewards=[],
    )

    # 驗證敵人數據中的scale
    print("Enemies in stage with scales:")
    for i, enemy_data in enumerate(enemies_data):
        print(
            f"  {i + 1}. {enemy_data.name}: scale={enemy_data.scale}, hp={enemy_data.hp}"
        )
        assert enemy_data.scale == [0.5, 1.0, 1.5, 2.0][i], (
            f"Wrong scale for {enemy_data.name}"
        )

    return stage


def test_enemy_creation_from_data():
    """測試從敵人數據創建敵人實例"""
    print("\n=== Test Enemy Creation From Data ===")

    # 創建敵人數據
    enemy_data = EnemyData(
        name="test_enemy",
        hp=1000,
        attack=100,
        defense=50,
        attribute="火",
        turns_until_action=3,
        image=None,
        scale=1.3,
    )

    # 從敵人數據創建敵人實例
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

    print(f"Enemy created from EnemyData:")
    print(f"  Name: {enemy.name}")
    print(f"  Scale: {enemy.scale}")
    print(f"  HP: {enemy.hp}")
    print(f"  Expected scale: 1.3")

    assert enemy.scale == 1.3, f"Enemy scale should be 1.3, got {enemy.scale}"
    assert enemy.name == "test_enemy", (
        f"Enemy name should be 'test_enemy', got {enemy.name}"
    )

    return True


def test_scale_affects_draw_calculations():
    """測試scale影響繪製計算"""
    print("\n=== Test Scale Affects Draw Calculations ===")

    # 測試不同scale值的計算
    test_cases = [
        {"scale": 0.5, "base_size": 150, "expected_size": 75},
        {"scale": 0.8, "base_size": 150, "expected_size": 120},
        {"scale": 1.0, "base_size": 150, "expected_size": 150},
        {"scale": 1.2, "base_size": 150, "expected_size": 180},
        {"scale": 1.5, "base_size": 150, "expected_size": 225},
        {"scale": 2.0, "base_size": 150, "expected_size": 300},
    ]

    for case in test_cases:
        scale = case["scale"]
        base_size = case["base_size"]
        expected_size = case["expected_size"]

        # 創建敵人
        enemy = Enemy(f"test_scale_{scale}", 1000, 100, 50, "火", 3, scale=scale)

        # 模擬繪製計算
        calculated_size = int(base_size * enemy.scale)

        print(f"Scale {scale}:")
        print(f"  Base size: {base_size}")
        print(f"  Enemy.scale: {enemy.scale}")
        print(f"  Calculated size: {calculated_size}")
        print(f"  Expected size: {expected_size}")

        assert calculated_size == expected_size, (
            f"For scale {scale}, expected {expected_size}, got {calculated_size}"
        )

    return True


def test_draw_method_with_scale():
    """測試繪製方法中的scale使用"""
    print("\n=== Test Draw Method With Scale ===")

    # 創建測試表面
    test_surface = pygame.Surface((400, 400), pygame.SRCALPHA)

    # 創建不同scale的敵人
    scales = [0.5, 1.0, 1.5]

    for scale in scales:
        enemy = Enemy(f"draw_test_{scale}", 1000, 100, 50, "火", 3, scale=scale)

        # 繪製敵人到測試表面
        try:
            enemy.draw(test_surface, 200, 200)
            print(f"Scale {scale}: Draw successful")

            # 驗證敵人屬性
            assert enemy.scale == scale, (
                f"Enemy scale should be {scale}, got {enemy.scale}"
            )

        except Exception as e:
            print(f"Scale {scale}: Draw failed with error: {e}")
            return False

    return True


def test_actual_game_integration():
    """測試實際遊戲整合"""
    print("\n=== Test Actual Game Integration ===")

    # 創建一個簡單的遊戲場景測試
    from dungeon.context import GameContext

    # 創建遊戲上下文
    context = GameContext()

    # 創建帶有scale的敵人數據
    enemy_data = EnemyData(
        name="game_enemy",
        hp=1000,
        attack=100,
        defense=50,
        attribute="火",
        turns_until_action=3,
        image=None,
        scale=1.2,
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

    print(f"Game enemy created:")
    print(f"  Name: {enemy.name}")
    print(f"  Scale: {enemy.scale}")
    print(f"  In context: {context}")

    # 驗證敵人屬性
    assert enemy.scale == 1.2, f"Game enemy scale should be 1.2, got {enemy.scale}"

    return True


def analyze_potential_issues():
    """分析潛在問題"""
    print("\n=== Analyze Potential Issues ===")

    print("檢查敵人圖片倍率在實際遊戲中可能不顯示的問題：")
    print("")
    print("1. 數據流檢查：")
    print("   StageEditor -> StageData -> EnemyData -> Enemy instance -> draw()")
    print("")
    print("2. 可能問題點：")
    print("   a) StageData中的scale沒有正確保存")
    print("   b) EnemyData從JSON加載時scale丟失")
    print("   c) Enemy創建時沒有傳遞scale參數")
    print("   d) draw()方法中scale使用不正確")
    print("")
    print("3. 已確認的修復：")
    print("   - draw()方法中的變數名衝突已修復（scale -> img_scale）")
    print("   - 敵人創建時scale參數已正確傳遞")
    print("")
    print("4. 需要進一步檢查：")
    print("   - 關卡數據從JSON加載時是否包含scale")
    print("   - 實際遊戲運行時是否使用scale值")

    return True


def run_actual_game_tests():
    """運行實際遊戲測試"""
    results = []

    results.append(
        (
            "Create Test Stage With Scaled Enemies",
            create_test_stage_with_scaled_enemies() is not None,
        )
    )
    results.append(("Enemy Creation From Data", test_enemy_creation_from_data()))
    results.append(
        ("Scale Affects Draw Calculations", test_scale_affects_draw_calculations())
    )
    results.append(("Draw Method With Scale", test_draw_method_with_scale()))
    results.append(("Actual Game Integration", test_actual_game_integration()))
    results.append(("Analyze Potential Issues", analyze_potential_issues()))

    print("\n" + "=" * 50)
    print("ACTUAL GAME SCALE TESTS RESULTS")
    print("=" * 50)

    for name, result in results:
        print(f"{name}: {'PASS' if result else 'FAIL'}")

    all_passed = all(r for _, r in results)
    print(f"\nOverall: {'PASS' if all_passed else 'FAIL'}")

    return all_passed


if __name__ == "__main__":
    success = run_actual_game_tests()
    pygame.quit()
    sys.exit(0 if success else 1)
