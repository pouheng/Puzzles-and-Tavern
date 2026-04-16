"""測試滾動功能"""

import pygame
import sys
import os
import math

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

pygame.init()

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800

from ui.pet_detail import PetDetail


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
        self.leader_skill = None
        self.active_skill = None
        self.attribute = "火"
        self.sub_attribute = None
        self.race = "龍"
        self.awakenings = []
        self.exp = 1000
        self.max_exp = 10000
        self.level = 50
        self.max_level = 99

    def add_exp(self, amount):
        self.exp += amount


class MockInventory:
    def __init__(self, pets):
        self.pets = pets


def test_fusion_click_opens_selection():
    """測試點擊加號打開選擇模式"""
    print("=== 測試點擊加號打開選擇模式 ===")

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pet = MockPet()
    detail_view = PetDetail(pet, screen)

    # 設置合成面板
    detail_view.show_fusion_panel = True
    detail_view.show_skill_popup = False
    detail_view.fusion_materials = []

    # 手動初始化 material_rects
    detail_view.material_rects = []
    center_x = SCREEN_WIDTH // 2
    center_y = SCREEN_HEIGHT // 2
    radius = 180
    for angle_deg in [0, 72, 144, 216, 288]:
        angle = angle_deg * math.pi / 180
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        slot_rect = pygame.Rect(x - 50, y - 50, 100, 100)
        detail_view.material_rects.append(slot_rect)

    # 點擊第一個素材位置
    first_slot = detail_view.material_rects[0]
    click_pos = (first_slot.centerx, first_slot.centery)

    print(f"點擊位置: {click_pos}")
    result = detail_view.handle_fusion_click(click_pos)

    print(f"返回結果: {result}")
    print(f"fusion_selection_mode: {detail_view.fusion_selection_mode}")

    success = result is not None and detail_view.fusion_selection_mode

    if success:
        print("[PASS] 點擊加號成功打開選擇模式")
    else:
        print("[FAIL] 點擊加號無法打開選擇模式")

    return success


def test_scroll_offset_initialized():
    """測試滾動偏移量已初始化"""
    print("\n=== 測試滾動偏移量已初始化 ===")

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pet = MockPet()
    detail_view = PetDetail(pet, screen)

    print(f"scroll_offset: {detail_view.scroll_offset}")
    print(f"scroll_speed: {detail_view.scroll_speed}")
    print(f"last_drag_y: {detail_view.last_drag_y}")

    success = (
        detail_view.scroll_offset == 0
        and detail_view.scroll_speed == 30
        and detail_view.last_drag_y is None
    )

    if success:
        print("[PASS] 滾動相關屬性已正確初始化")
    else:
        print("[FAIL] 滾動相關屬性初始化有問題")

    return success


def test_handle_scroll_method_exists():
    """測試 handle_scroll 方法存在"""
    print("\n=== 測試 handle_scroll 方法存在 ===")

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pet = MockPet()
    detail_view = PetDetail(pet, screen)

    has_handle_scroll = hasattr(detail_view, "handle_scroll")
    has_handle_drag = hasattr(detail_view, "handle_drag")

    print(f"handle_scroll 方法存在: {has_handle_scroll}")
    print(f"handle_drag 方法存在: {has_handle_drag}")

    success = has_handle_scroll and has_handle_drag

    if success:
        print("[PASS] 滾動和拖曳方法已實現")
    else:
        print("[FAIL] 滾動或拖曳方法缺失")

    return success


def run_all_tests():
    """運行所有測試"""
    print("=" * 60)
    print("經驗值合成滾動功能測試")
    print("=" * 60)

    results = []

    try:
        results.append(("初始化滾動屬性", test_scroll_offset_initialized()))
        results.append(("滾動方法存在", test_handle_scroll_method_exists()))
        results.append(("點擊加號選擇模式", test_fusion_click_opens_selection()))
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
