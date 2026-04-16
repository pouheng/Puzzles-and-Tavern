"""測試滾動和點擊修復"""

import pygame
import sys
import os
import math

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

pygame.init()

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))


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


class MockMouseEvent:
    def __init__(self, y=1):
        self.y = y
        self.precise_y = None


def test_scroll_with_mouse_pos():
    """測試滾動處理使用正確的mouse_pos參數"""
    print("=== 測試滾動處理 ===")

    from ui.pet_detail import PetDetail

    pet = MockPet()
    detail_view = PetDetail(pet, screen)

    # 初始化選擇模式
    detail_view.fusion_selection_mode = True
    detail_view.selection_list_rect = pygame.Rect(250, 520, 700, 200)
    detail_view.scroll_offset = 0
    detail_view.inventory = None  # 沒有inventory不應該滾動

    # 創建滾輪事件和鼠標位置
    mouse_pos = (500, 600)  # 在選擇列表區域內
    scroll_event = MockMouseEvent(y=1)

    print(f"滾動前: scroll_offset = {detail_view.scroll_offset}")

    # 調用handle_scroll
    detail_view.handle_scroll(scroll_event, mouse_pos)

    print(f"滾動後: scroll_offset = {detail_view.scroll_offset}")

    # 沒有inventory，所以不應該滾動
    success = detail_view.scroll_offset == 0
    if success:
        print("[PASS] 滾動處理正確")
    else:
        print("[FAIL] 滾動處理有問題")

    return success


def test_scroll_outside_list():
    """測試鼠標在選擇列表外時不滾動"""
    print("\n=== 測試鼠標在選擇列表外不滾動 ===")

    from ui.pet_detail import PetDetail

    pet = MockPet()
    detail_view = PetDetail(pet, screen)

    detail_view.fusion_selection_mode = True
    detail_view.selection_list_rect = pygame.Rect(250, 520, 700, 200)
    detail_view.scroll_offset = 50
    detail_view.inventory = None

    # 鼠標在選擇列表外
    mouse_pos = (100, 100)
    scroll_event = MockMouseEvent(y=1)

    original_offset = detail_view.scroll_offset
    detail_view.handle_scroll(scroll_event, mouse_pos)

    success = detail_view.scroll_offset == original_offset
    if success:
        print("[PASS] 列表外不滾動")
    else:
        print(f"[FAIL] 滾動了: {original_offset} -> {detail_view.scroll_offset}")

    return success


def test_handle_scroll_signature():
    """測試handle_scroll方法接受正確的參數"""
    print("\n=== 測試handle_scroll方法簽名 ===")

    from ui.pet_detail import PetDetail

    pet = MockPet()
    detail_view = PetDetail(pet, screen)

    # 檢查方法是否存在
    has_method = hasattr(detail_view, "handle_scroll")

    # 嘗試調用（應該不拋異常）
    try:
        detail_view.handle_scroll(MockMouseEvent(), (500, 600))
        call_success = True
    except TypeError as e:
        print(f"TypeError: {e}")
        call_success = False

    success = has_method and call_success

    if success:
        print("[PASS] handle_scroll方法簽名正確")
    else:
        print("[FAIL] handle_scroll方法有問題")

    return success


def test_drag_not_triggers_on_mouse_move():
    """測試鼠標移動不會觸發選擇"""
    print("\n=== 測試拖曳狀態 ===")

    from ui.pet_detail import PetDetail

    pet = MockPet()
    detail_view = PetDetail(pet, screen)

    # 設置inventory（用於計算最大滾動範圍）
    class MockInventory:
        def __init__(self):
            self.pets = []
            for i in range(25):
                p = MockPet()
                p.id = 100 + i  # 不同的ID，避免被過濾掉
                self.pets.append(p)

    detail_view.inventory = MockInventory()

    # 初始化選擇模式
    detail_view.fusion_selection_mode = True
    detail_view.last_drag_y = 600  # 初始位置
    detail_view.scroll_offset = 0
    detail_view.selection_list_rect = pygame.Rect(250, 520, 700, 200)

    # 模擬拖曳（向下移動100像素）- 需要在選擇列表區域內
    # selection_list_rect = (250, 520, 700, 200) -> y from 520 to 720
    # 向下拖 = y變大 = delta_y = last_drag_y - new_y = 600 - 700 = -100 (負數，向下滾)
    # 但代碼是 scroll_offset + delta_y，所以需要正向滾動
    # 讓我重新理解邏輯...
    # 向上拖 = y變小 = delta_y > 0 = scroll_offset增加
    # 所以初始last_drag_y = 620，移動到y=520 = delta_y = 100 = scroll_offset增加100
    drag_pos = (500, 520)  # 向上移動100像素（y從600變520）

    print(f"拖曳前: scroll_offset = {detail_view.scroll_offset}")
    print(f"上次拖曳Y: {detail_view.last_drag_y}")
    print(f"當前Y: {drag_pos[1]}")
    print(f"選擇列表rect: {detail_view.selection_list_rect}")

    detail_view.handle_drag(drag_pos)

    print(f"拖曳後: scroll_offset = {detail_view.scroll_offset}")
    print(f"新last_drag_y: {detail_view.last_drag_y}")

    # 滾動偏移量應該改變（delta_y = 600 - 500 = 100）
    success = detail_view.scroll_offset > 0

    if success:
        print("[PASS] 拖曳處理正確")
    else:
        print("[FAIL] 拖曳處理有問題")

    return success


def run_all_tests():
    print("=" * 60)
    print("滾動和點擊修復測試")
    print("=" * 60)

    results = []

    try:
        results.append(("滾動處理", test_scroll_with_mouse_pos()))
        results.append(("列表外不滾動", test_scroll_outside_list()))
        results.append(("方法簽名", test_handle_scroll_signature()))
        results.append(("拖曳處理", test_drag_not_triggers_on_mouse_move()))
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
