"""
測試經驗值合成時收起技能詳細介面
"""

import pygame
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

pygame.init()

from ui.pet_detail import PetDetail


def test_fusion_hides_skill_popup():
    """測試按下經驗值合成時是否收起技能詳細介面"""
    print("測試按下經驗值合成時是否收起技能詳細介面")

    try:
        # 創建一個簡單的寵物類別用於測試
        class MockPet:
            def __init__(self):
                self.name = "測試寵物"
                self.rarity = 5
                self.hp = 1000
                self.attack = 500
                self.recovery = 200
                self._max_hp = 2000
                self._max_attack = 1000
                self._max_recovery = 400
                self.leader_skill = "測試隊長技能"
                self.active_skill = "測試主動技能"
                self.skill_turn = 10
                self.max_skill_turn = 15
                self.attribute = "火"
                self.sub_attributes = []
                self.types = ["體力型"]
                self.exp = 1000
                self.max_exp = 10000
                self.level = 50
                self.max_level = 99

        # 創建測試表面
        screen = pygame.Surface((1200, 800))

        # 創建寵物詳細視圖
        pet = MockPet()
        detail_view = PetDetail(screen, pet)

        # 模擬顯示技能詳細介面
        detail_view.show_skill_popup = True
        detail_view.skill_popup_type = "leader"

        print(f"初始狀態: show_skill_popup = {detail_view.show_skill_popup}")
        print(f"技能彈窗類型: {detail_view.skill_popup_type}")

        # 模擬點擊經驗值合成按鈕
        fusion_button_pos = (
            detail_view.fusion_button_rect.centerx,
            detail_view.fusion_button_rect.centery,
        )

        result = detail_view.handle_click(fusion_button_pos)

        print(f"\n點擊經驗值合成按鈕後:")
        print(f"返回結果: {result}")
        print(f"show_skill_popup = {detail_view.show_skill_popup}")
        print(f"show_fusion_panel = {detail_view.show_fusion_panel}")

        # 驗證結果
        assert result == "open_fusion", f"應返回'open_fusion'，但返回了'{result}'"
        assert detail_view.show_skill_popup == False, "技能詳細介面應被收起"
        assert detail_view.show_fusion_panel == True, "合成面板應被開啟"

        print("\n[OK] 經驗值合成按鈕正確收起技能詳細介面")
        return True

    except Exception as e:
        print(f"[ERROR] 測試失敗: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_skill_popup_stays_when_not_fusion():
    """測試非經驗值合成點擊時技能詳細介面保持開啟"""
    print("\n測試非經驗值合成點擊時技能詳細介面保持開啟")

    try:
        # 創建一個簡單的寵物類別用於測試
        class MockPet:
            def __init__(self):
                self.name = "測試寵物"
                self.rarity = 5
                self.hp = 1000
                self.attack = 500
                self.recovery = 200
                self._max_hp = 2000
                self._max_attack = 1000
                self._max_recovery = 400
                self.leader_skill = "測試隊長技能"
                self.active_skill = "測試主動技能"
                self.skill_turn = 10
                self.max_skill_turn = 15
                self.attribute = "火"
                self.sub_attributes = []
                self.types = ["體力型"]
                self.exp = 1000
                self.max_exp = 10000
                self.level = 50
                self.max_level = 99

        # 創建測試表面
        screen = pygame.Surface((1200, 800))

        # 創建寵物詳細視圖
        pet = MockPet()
        detail_view = PetDetail(screen, pet)

        # 模擬顯示技能詳細介面
        detail_view.show_skill_popup = True
        detail_view.skill_popup_type = "leader"

        print(f"初始狀態: show_skill_popup = {detail_view.show_skill_popup}")

        # 模擬點擊關閉按鈕（非經驗值合成）
        close_button_pos = (
            detail_view.close_button_rect.centerx,
            detail_view.close_button_rect.centery,
        )

        result = detail_view.handle_click(close_button_pos)

        print(f"\n點擊關閉按鈕後:")
        print(f"返回結果: {result}")
        print(f"show_skill_popup = {detail_view.show_skill_popup}")

        # 驗證結果
        assert result == "close", f"應返回'close'，但返回了'{result}'"
        assert detail_view.show_skill_popup == True, (
            "技能詳細介面應保持開啟（點擊關閉按鈕不影響）"
        )

        print("\n[OK] 非經驗值合成點擊時技能詳細介面保持開啟")
        return True

    except Exception as e:
        print(f"[ERROR] 測試失敗: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    print("=" * 60)
    print("經驗值合成時收起技能詳細介面測試")
    print("=" * 60)

    results = []

    try:
        results.append(("經驗值合成收起技能介面", test_fusion_hides_skill_popup()))
        results.append(
            ("非合成點擊保持技能介面", test_skill_popup_stays_when_not_fusion())
        )
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
        print("1. 在按下經驗值合成按鈕時，自動設置 show_skill_popup = False")
        print("2. 確保隊長技能詳細額外介面被收起")
        print("3. 確保主動技能詳細額外介面被收起")
        print("\n效果:")
        print("- 按下經驗值合成時，所有技能詳細介面自動關閉")
        print("- 避免誤觸下方的技能詳細介面元素")
        print("- 提升用戶操作體驗")
    else:
        print("部分測試失敗")

    pygame.quit()
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
