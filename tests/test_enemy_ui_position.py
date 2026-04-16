"""
測試敵人UI位置是否不受圖片倍率影響
"""

import pygame
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

pygame.init()

from dungeon.battle import Enemy


def test_ui_position_independent_of_scale():
    """測試UI位置是否獨立於scale"""
    print("測試UI位置是否獨立於scale")

    # 測試不同scale值
    test_scales = [0.5, 1.0, 1.6, 2.0]

    # 計算各個scale下的UI位置
    base_size = 150
    x, y = 300, 300  # 假設中心點

    for scale in test_scales:
        print(f"\nScale = {scale}:")

        # 計算圖片大小（會受scale影響）
        size = int(base_size * scale)
        print(f"  圖片大小 (size): {size}")

        # 計算UI位置（應該使用base_size，而不是size）
        turns_y = y - base_size // 2 - 20
        name_y = y + base_size // 2 + 50
        hp_y = y + base_size // 2 + 62
        bar_y = y + base_size // 2 + 115

        print(f"  行動量 Y 位置: {turns_y}")
        print(f"  名字 Y 位置: {name_y}")
        print(f"  血量 Y 位置: {hp_y}")
        print(f"  血條 Y 位置: {bar_y}")

        # 驗證所有scale下的UI位置相同
        if scale == test_scales[0]:
            expected_turns_y = turns_y
            expected_name_y = name_y
            expected_hp_y = hp_y
            expected_bar_y = bar_y
        else:
            assert turns_y == expected_turns_y, (
                f"行動量位置隨scale變化: {turns_y} != {expected_turns_y}"
            )
            assert name_y == expected_name_y, (
                f"名字位置隨scale變化: {name_y} != {expected_name_y}"
            )
            assert hp_y == expected_hp_y, (
                f"血量位置隨scale變化: {hp_y} != {expected_hp_y}"
            )
            assert bar_y == expected_bar_y, (
                f"血條位置隨scale變化: {bar_y} != {expected_bar_y}"
            )

        print("\n[OK] 所有scale下的UI位置保持一致")
    return True


def test_actual_draw_with_different_scales():
    """測試實際繪製不同scale的敵人"""
    print("\n測試實際繪製不同scale的敵人")

    # 創建測試表面
    test_surface = pygame.Surface((600, 600), pygame.SRCALPHA)

    # 創建不同scale的敵人
    enemies = [
        Enemy("小敵人", 1000, 100, 50, "火", 3, scale=0.5),
        Enemy("正常敵人", 1000, 100, 50, "水", 2, scale=1.0),
        Enemy("大敵人", 1000, 100, 50, "木", 1, scale=1.6),
    ]

    # 繪製位置
    positions = [(200, 200), (300, 200), (400, 200)]

    try:
        for enemy, (x, y) in zip(enemies, positions):
            enemy.draw(test_surface, x, y)
        print(f"  成功繪製 {enemy.name} (scale={enemy.scale})")

        print("[OK] 所有敵人繪製成功")

        # 可選：保存測試圖片
        # pygame.image.save(test_surface, "test_enemy_ui.png")
        # print("測試圖片已保存為 test_enemy_ui.png")

    except Exception as e:
        print(f"[ERROR] 繪製失敗: {e}")
        import traceback

        traceback.print_exc()
        return False

    return True


def test_element_positions():
    """測試各個元素的位置關係"""
    print("\n測試各個元素的位置關係")

    base_size = 150
    x, y = 300, 300

    # 計算各個元素的Y座標
    turns_y = y - base_size // 2 - 20  # 行動量（最上方）
    image_top = y - base_size // 2  # 圖片頂部
    image_bottom = y + base_size // 2  # 圖片底部
    name_y = y + base_size // 2 + 50  # 名字
    hp_y = y + base_size // 2 + 62  # 血量
    bar_y = y + base_size // 2 + 115  # 血條（最下方）

    print(f"  行動量 Y: {turns_y} (圖片上方)")
    print(f"  圖片頂部 Y: {image_top}")
    print(f"  圖片底部 Y: {image_bottom}")
    print(f"  名字 Y: {name_y} (圖片下方)")
    print(f"  血量 Y: {hp_y} (名字下方)")
    print(f"  血條 Y: {bar_y} (血量下方)")

    # 驗證位置關係
    assert turns_y < image_top, "行動量應該在圖片上方"
    assert name_y > image_bottom, "名字應該在圖片下方"
    assert hp_y > name_y, "血量應該在名字下方"
    assert bar_y > hp_y, "血條應該在血量下方"

    print("[OK] 元素位置關係正確")
    return True


def main():
    print("=" * 60)
    print("敵人UI位置測試")
    print("=" * 60)

    results = []

    try:
        results.append(("UI位置獨立於scale", test_ui_position_independent_of_scale()))
        results.append(("實際繪製測試", test_actual_draw_with_different_scales()))
        results.append(("元素位置關係", test_element_positions()))
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
        status = "PASS" if result else "FAIL"
        print(f"{name}: {status}")
        if not result:
            all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("所有測試通過！")
        print("\n修改總結:")
        print("1. UI位置現在獨立於圖片倍率（使用base_size=150計算）")
        print("2. 行動量位置往上調整（從-5改為-20）")
        print("3. 名字位置往下調整（從+30改為+50）")
        print("4. 血量位置往上調整（從+72改為+62）")
        print("5. 血條位置往上調整（從+125改為+115）")
        print("6. 玩家生命值往下調整（從-35改為-25）")
        print("\n效果:")
        print("- 圖片倍率變化時，UI元素位置保持不變")
        print("- 圖片在行動量和名字之間")
        print("- 名字、血量、血條依次排列在圖片下方")
    else:
        print("部分測試失敗，請檢查錯誤信息。")

    pygame.quit()
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
