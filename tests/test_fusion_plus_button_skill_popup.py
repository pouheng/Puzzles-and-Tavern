"""
測試點擊加號按鈕時收起技能詳細介面

這個測試驗證：
1. 打開合成面板
2. 顯示技能詳細介面
3. 點擊加號按鈕
4. 技能詳細介面是否被正確關閉
"""

import pygame
import sys
import os
import math

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

pygame.init()

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800

from ui.pet_detail import PetDetail


class MockSkill:
    def __init__(self, name="測試技能", desc="這是一個很長的技能描述" * 10):
        self._name = name
        self._desc = desc

    def get_name(self):
        return self._name

    def get_description(self):
        return self._desc


class MockPet:
    def __init__(self):
        self.id = 1
        self.name = "測試寵物"
        self.rarity = 5
        self.hp = 1000
        self.attack = 500
        self.recovery = 200
        self._max_hp = 2000
        self._max_attack = 1000
        self._max_recovery = 400
        self.leader_skill = MockSkill("隊長技能", "隊長技能描述 " * 20)
        self.active_skill = MockSkill("主動技能", "主動技能描述 " * 20)
        self.attribute = "火"
        self.sub_attribute = None
        self.race = "龍"
        self.awakenings = ["超加強"]
        self.exp = 1000
        self.max_exp = 10000
        self.level = 50
        self.max_level = 99

    def add_exp(self, amount):
        self.exp += amount


def test_open_fusion_hides_pet_detail():
    """測試打開合成面板時隱藏寵物詳情面板"""
    print("=== 測試打開合成面板時隱藏寵物詳情面板 ===")

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pet = MockPet()
    detail_view = PetDetail(pet, screen)

    # 初始狀態
    print(f"初始狀態: show_fusion_panel={detail_view.show_fusion_panel}")
    print(f"初始狀態: show_skill_popup={detail_view.show_skill_popup}")

    # 點擊經驗值合成按鈕
    fusion_btn_pos = (
        detail_view.fusion_button_rect.centerx,
        detail_view.fusion_button_rect.centery,
    )

    print(f"\n點擊經驗值合成按鈕: {fusion_btn_pos}")

    result = detail_view.handle_click(fusion_btn_pos)

    print(f"\n點擊後:")
    print(f"返回結果: {result}")
    print(f"show_fusion_panel={detail_view.show_fusion_panel}")
    print(f"show_skill_popup={detail_view.show_skill_popup}")

    # 驗證
    # 1. 返回 open_fusion
    # 2. 技能详情被关闭
    success = (
        result == "open_fusion"
        and detail_view.show_fusion_panel == True
        and detail_view.show_skill_popup == False
    )

    if success:
        print("[PASS] 打開合成面板時技能詳情被關閉")
    else:
        print("[FAIL] 測試失敗")

    return success


def test_plus_button_closes_skill_popup():
    """測試點擊加號按鈕時關閉技能詳細介面"""
    print("=== 測試點擊加號按鈕時關閉技能詳細介面 ===")

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pet = MockPet()
    detail_view = PetDetail(pet, screen)

    # 1. 打開合成面板
    detail_view.show_fusion_panel = True
    detail_view.show_skill_popup = True  # 模擬技能詳細介面開啟
    detail_view.skill_popup_type = "leader"
    detail_view.fusion_materials = []  # 空素材列表

    # 手動初始化 material_rects
    detail_view.material_rects = []
    center_x = SCREEN_WIDTH // 2
    center_y = SCREEN_HEIGHT // 2
    radius = 180
    for i, angle_deg in enumerate([0, 72, 144, 216, 288]):
        angle = angle_deg * math.pi / 180
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        slot_rect = pygame.Rect(x - 50, y - 50, 100, 100)
        detail_view.material_rects.append(slot_rect)

    print(f"初始狀態: show_fusion_panel={detail_view.show_fusion_panel}")
    print(f"初始狀態: show_skill_popup={detail_view.show_skill_popup}")

    # 2. 使用第一個素材位置（加號按鈕位置）
    first_slot = detail_view.material_rects[0]
    plus_button_pos = (first_slot.centerx, first_slot.centery)

    print(f"\n加號按鈕位置: {plus_button_pos}")

    # 3. 點擊加號按鈕
    result = detail_view.handle_fusion_click(plus_button_pos)

    print(f"\n點擊後:")
    print(f"返回結果: {result}")
    print(f"show_skill_popup: {detail_view.show_skill_popup}")
    print(f"fusion_selection_mode: {detail_view.fusion_selection_mode}")

    # 4. 驗證
    popup_closed = not detail_view.show_skill_popup
    selection_mode_opened = detail_view.fusion_selection_mode

    print(f"\n驗證結果:")
    print(f"技能彈窗已關閉: {popup_closed}")
    print(f"選擇模式已開啟: {selection_mode_opened}")

    if popup_closed and selection_mode_opened:
        print("\n[PASS] 測試通過！點擊加號按鈕時技能詳細介面已被關閉")
        return True
    else:
        print("\n[FAIL] 測試失敗！")
        if not popup_closed:
            print("  - 技能詳細介面應該被關閉但沒有關閉")
        if not selection_mode_opened:
            print("  - 選擇模式應該被開啟但沒有開啟")
        return False


def test_material_rect_click():
    """測試素材位置點擊"""
    print("\n=== 測試素材位置點擊 ===")

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pet = MockPet()
    detail_view = PetDetail(pet, screen)

    # 打開合成面板
    detail_view.show_fusion_panel = True
    detail_view.show_skill_popup = True
    detail_view.fusion_materials = []

    # 手動初始化 material_rects（因為不繪製螢幕）
    detail_view.material_rects = []
    center_x = SCREEN_WIDTH // 2
    center_y = SCREEN_HEIGHT // 2
    radius = 180
    for i, angle_deg in enumerate([0, 72, 144, 216, 288]):
        angle = angle_deg * math.pi / 180
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        slot_rect = pygame.Rect(x - 50, y - 50, 100, 100)
        detail_view.material_rects.append(slot_rect)

    print(f"素材位置數量: {len(detail_view.material_rects)}")

    # 點擊第一個素材位置
    first_slot = detail_view.material_rects[0]
    click_pos = (first_slot.centerx, first_slot.centery)

    print(f"點擊位置: {click_pos}")
    print(f"第一個素材槽: {first_slot}")

    result = detail_view.handle_fusion_click(click_pos)

    print(f"\n點擊後:")
    print(f"返回結果: {result}")
    print(f"show_skill_popup: {detail_view.show_skill_popup}")
    print(f"fusion_selection_mode: {detail_view.fusion_selection_mode}")

    # 驗證
    success = (
        result is not None
        and not detail_view.show_skill_popup
        and detail_view.fusion_selection_mode
    )

    if success:
        print("\n[PASS] 測試通過！")
    else:
        print("\n[FAIL] 測試失敗！")

    return success


def test_leader_skill_popup_closes():
    """測試隊長技能彈窗關閉"""
    print("\n=== 測試隊長技能彈窗關閉 ===")

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pet = MockPet()
    detail_view = PetDetail(pet, screen)

    # 打開合成面板並顯示技能彈窗
    detail_view.show_fusion_panel = True
    detail_view.show_skill_popup = True
    detail_view.skill_popup_type = "leader"
    detail_view.fusion_materials = []

    # 手動初始化 material_rects
    detail_view.material_rects = []
    center_x = SCREEN_WIDTH // 2
    center_y = SCREEN_HEIGHT // 2
    radius = 180
    for i, angle_deg in enumerate([0, 72, 144, 216, 288]):
        angle = angle_deg * math.pi / 180
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        slot_rect = pygame.Rect(x - 50, y - 50, 100, 100)
        detail_view.material_rects.append(slot_rect)

    # 點擊第一個素材位置
    first_slot = detail_view.material_rects[0]
    click_pos = (first_slot.centerx, first_slot.centery)

    detail_view.handle_fusion_click(click_pos)

    print(
        f"技能類型: {detail_view.skill_popup_type if hasattr(detail_view, 'skill_popup_type') else 'N/A'}"
    )
    print(f"技能彈窗已關閉: {not detail_view.show_skill_popup}")

    success = not detail_view.show_skill_popup

    if success:
        print("[PASS] 測試通過！")
    else:
        print("[FAIL] 測試失敗！")

    return success


def run_all_tests():
    """運行所有測試"""
    print("=" * 60)
    print("點擊加號按鈕時收起技能詳細介面測試")
    print("=" * 60)

    results = []

    try:
        results.append(("打開合成隱藏詳情", test_open_fusion_hides_pet_detail()))
        results.append(("加號按鈕關閉技能彈窗", test_plus_button_closes_skill_popup()))
        results.append(("素材位置點擊", test_material_rect_click()))
        results.append(("隊長技能彈窗關閉", test_leader_skill_popup_closes()))
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
    else:
        print("部分測試失敗")

    pygame.quit()
    return all_passed


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
