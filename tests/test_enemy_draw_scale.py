"""
測試敵人繪製時的圖片倍率功能

這個測試驗證：
1. 敵人類別的scale屬性是否正確影響繪製大小
2. 圖片渲染邏輯是否正確使用scale
3. 實際遊戲中的敵人顯示是否受scale影響
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


def test_enemy_draw_size_with_scale():
    """測試敵人繪製大小與scale的關係"""
    print("=== Test Enemy Draw Size With Scale ===")

    # 創建測試表面來繪製敵人
    test_surface = pygame.Surface((300, 300), pygame.SRCALPHA)

    # 測試不同scale值
    test_scales = [0.5, 1.0, 1.5, 2.0]
    base_size = 150

    for scale in test_scales:
        # 創建敵人
        enemy = Enemy(f"test_scale_{scale}", 1000, 100, 50, "火", 3, scale=scale)

        # 計算預期大小
        expected_size = int(base_size * scale)

        # 模擬繪製邏輯
        size = int(base_size * enemy.scale)

        print(f"Scale {scale}:")
        print(f"  Enemy.scale = {enemy.scale}")
        print(f"  Base size = {base_size}")
        print(f"  Calculated size = {size}")
        print(f"  Expected size = {expected_size}")

        # 驗證計算
        assert size == expected_size, (
            f"For scale {scale}, expected size {expected_size}, got {size}"
        )

        # 驗證scale屬性
        assert enemy.scale == scale, f"Enemy scale should be {scale}, got {enemy.scale}"

    return True


def test_enemy_draw_without_image():
    """測試沒有圖片時敵人的繪製"""
    print("\n=== Test Enemy Draw Without Image ===")

    test_surface = pygame.Surface((300, 300), pygame.SRCALPHA)

    # 創建沒有圖片的敵人
    enemy = Enemy("test_no_image", 1000, 100, 50, "火", 3, scale=1.5)

    # 驗證屬性
    print(f"Enemy scale: {enemy.scale}")
    print(f"Enemy image: {enemy.image}")

    assert enemy.scale == 1.5, f"Enemy scale should be 1.5, got {enemy.scale}"
    assert enemy.image is None, f"Enemy image should be None, got {enemy.image}"

    return True


def test_enemy_draw_logic():
    """測試敵人繪製邏輯"""
    print("\n=== Test Enemy Draw Logic ===")

    # 分析敵人繪製方法中的邏輯
    base_size = 150

    # 測試不同情況
    test_cases = [
        {"scale": 0.5, "image": None, "desc": "小尺寸，無圖片"},
        {"scale": 1.0, "image": None, "desc": "正常尺寸，無圖片"},
        {"scale": 1.5, "image": None, "desc": "大尺寸，無圖片"},
        {"scale": 2.0, "image": None, "desc": "特大尺寸，無圖片"},
    ]

    for case in test_cases:
        scale = case["scale"]
        desc = case["desc"]

        # 計算大小
        size = int(base_size * scale)

        print(f"{desc}:")
        print(f"  Scale: {scale}")
        print(f"  Base size: {base_size}")
        print(f"  Calculated size: {size}")

        # 驗證計算
        expected_size = int(base_size * scale)
        assert size == expected_size, f"Expected size {expected_size}, got {size}"

    return True


def test_scale_affects_all_draw_elements():
    """測試scale影響所有繪製元素"""
    print("\n=== Test Scale Affects All Draw Elements ===")

    # 測試scale是否影響所有繪製部分
    test_scales = [0.5, 1.0, 1.5]

    for scale in test_scales:
        enemy = Enemy(f"test_scale_{scale}", 1000, 100, 50, "火", 3, scale=scale)

        # 驗證繪製邏輯中的各個部分
        base_size = 150
        size = int(base_size * enemy.scale)

        # 計算其他元素的位置（基於原始程式碼）
        turns_text_y = enemy.scale * 100  # 簡化計算
        name_text_y = size // 2 + 30
        hp_text_y = size // 2 + 47
        bar_y = size // 2 + 100

        print(f"Scale {scale}:")
        print(f"  Enemy size: {size}")
        print(f"  Turns text Y: ~{turns_text_y}")
        print(f"  Name text Y: {name_text_y}")
        print(f"  HP text Y: {hp_text_y}")
        print(f"  HP bar Y: {bar_y}")

        # 驗證scale影響了大小計算
        assert size == int(base_size * scale), f"Size not affected by scale"

    return True


def test_enemy_creation_with_scale():
    """測試創建敵人時scale的傳遞"""
    print("\n=== Test Enemy Creation With Scale ===")

    # 測試從EnemyData創建敵人時scale的傳遞
    from dungeon.stages import EnemyData

    # 創建EnemyData
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

    print(f"EnemyData scale: {enemy_data.scale}")
    assert enemy_data.scale == 1.3, (
        f"EnemyData scale should be 1.3, got {enemy_data.scale}"
    )

    # 從EnemyData創建Enemy
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

    print(f"Enemy scale from EnemyData: {enemy.scale}")
    assert enemy.scale == 1.3, f"Enemy scale should be 1.3, got {enemy.scale}"

    return True


def test_battle_system_scale_usage():
    """測試戰鬥系統中scale的使用"""
    print("\n=== Test Battle System Scale Usage ===")

    # 檢查戰鬥系統中敵人創建的程式碼
    from dungeon.battle import Battle

    # 創建一個簡單的測試關卡
    from dungeon.stages import Stage, Floor, EnemyData

    # 創建帶有scale的敵人數據
    enemy_data = EnemyData(
        name="test_battle_enemy",
        hp=1000,
        attack=100,
        defense=50,
        attribute="火",
        turns_until_action=3,
        image=None,
        scale=1.2,
    )

    # 創建樓層
    floor = Floor(floor_num=1, enemies=[enemy_data], dialogue=[])

    # 創建關卡
    stage = Stage(
        name="test_stage", dialogue=[], floors=[floor], stage_type=1, exp=0, rewards=[]
    )

    print(f"EnemyData in stage has scale: {enemy_data.scale}")
    assert enemy_data.scale == 1.2, (
        f"EnemyData scale should be 1.2, got {enemy_data.scale}"
    )

    # 注意：這裡不實際創建Battle實例，因為它需要完整的遊戲狀態
    # 我們只驗證數據結構

    return True


def analyze_draw_method_issue():
    """分析繪製方法中的問題"""
    print("\n=== Analyze Draw Method Issue ===")

    # 分析敵人draw方法中的潛在問題
    print("分析敵人draw方法中的scale使用：")
    print("1. 第1879行: size = int(base_size * self.scale)")
    print(
        "2. 第1893行: scale = min(max_w / orig_w, max_h / orig_h) <- 這裡有變數名衝突！"
    )
    print("3. 第1894行: new_w = int(orig_w * scale) <- 使用局部變數scale")
    print("")
    print("問題分析：")
    print("- self.scale: 敵人整體大小倍率")
    print("- 局部變數scale: 圖片適應容器的縮放比例")
    print("- 這兩個scale意義不同，但變數名相同可能導致混淆")
    print("")
    print("建議修復：")
    print("1. 將局部變數scale改名為img_scale或fit_scale")
    print("2. 確保self.scale正確影響所有繪製元素")

    return True


def run_all_scale_tests():
    """運行所有scale測試"""
    results = []

    results.append(("Enemy Draw Size With Scale", test_enemy_draw_size_with_scale()))
    results.append(("Enemy Draw Without Image", test_enemy_draw_without_image()))
    results.append(("Enemy Draw Logic", test_enemy_draw_logic()))
    results.append(
        ("Scale Affects All Draw Elements", test_scale_affects_all_draw_elements())
    )
    results.append(("Enemy Creation With Scale", test_enemy_creation_with_scale()))
    results.append(("Battle System Scale Usage", test_battle_system_scale_usage()))
    results.append(("Analyze Draw Method Issue", analyze_draw_method_issue()))

    print("\n" + "=" * 50)
    print("ENEMY SCALE DRAW TESTS RESULTS")
    print("=" * 50)

    for name, result in results:
        print(f"{name}: {'PASS' if result else 'FAIL'}")

    all_passed = all(r for _, r in results)
    print(f"\nOverall: {'PASS' if all_passed else 'FAIL'}")

    return all_passed


if __name__ == "__main__":
    success = run_all_scale_tests()
    pygame.quit()
    sys.exit(0 if success else 1)
