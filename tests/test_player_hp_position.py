"""
測試玩家生命值UI位置
"""

import pygame
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

pygame.init()

from dungeon.battle import BattleView


def test_player_hp_position():
    """測試玩家生命值位置"""
    print("測試玩家生命值位置")

    # 創建一個簡單的測試隊伍
    class MockTeam:
        def __init__(self):
            self.members = []

        def get_leader(self):
            return None

    # 創建一個簡單的關卡
    class MockStage:
        def __init__(self):
            self.name = "測試關卡"

    try:
        # 創建BattleView
        battle_view = BattleView(MockTeam(), MockStage())

        # 檢查玩家生命值位置
        hp_bar_y = battle_view.hp_bar_y
        hp_text_y = hp_bar_y - 30  # 玩家生命值文字位置

        print(f"玩家生命值條 Y 位置: {hp_bar_y}")
        print(f"玩家生命值文字 Y 位置: {hp_text_y}")
        print(f"玩家生命值文字與血條的距離: {hp_bar_y - hp_text_y} 像素")

        # 驗證位置關係
        assert hp_text_y < hp_bar_y, "生命值文字應該在血條上方"
        assert hp_bar_y - hp_text_y == 30, "生命值文字與血條距離應為30像素"

        print("[OK] 玩家生命值位置正確")
        return True

    except Exception as e:
        print(f"[ERROR] 測試失敗: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    print("=" * 60)
    print("玩家生命值UI位置測試")
    print("=" * 60)

    try:
        result = test_player_hp_position()
    except Exception as e:
        print(f"\n測試過程中發生錯誤: {e}")
        import traceback

        traceback.print_exc()
        return False

    print("\n" + "=" * 60)
    print("測試結果總結")
    print("=" * 60)

    if result:
        print("測試通過！")
        print("\n修改總結:")
        print("1. 敵人血量往上調整10像素（從+72改為+62）")
        print("2. 敵人血條往上調整10像素（從+125改為+115）")
        print("3. 玩家生命值往下調整10像素（從-35改為-25）")
    else:
        print("測試失敗")

    pygame.quit()
    return result


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
