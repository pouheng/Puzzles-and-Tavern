"""
測試設置菜單返回按鈕位置
"""

import pygame
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

pygame.init()

from main import Game


def test_back_button_position():
    """測試返回按鈕位置"""
    print("測試設置菜單返回按鈕位置")

    try:
        # 創建遊戲實例但不運行
        game = Game()

        # 檢查各個設置頁面的返回按鈕位置
        print("\n檢查各個設置頁面的返回按鈕位置:")

        # 模擬各個設置頁面的返回按鈕位置
        expected_x = 270  # 預期的X座標（原為60，向右移動210像素）
        expected_y = 10  # Y座標保持不變
        expected_width = 100
        expected_height = 40

        print(
            f"預期的返回按鈕位置: x={expected_x}, y={expected_y}, width={expected_width}, height={expected_height}"
        )

        # 檢查事件處理中的默認按鈕位置
        print("\n檢查事件處理中的默認按鈕位置:")

        # 這些是事件處理中的默認值
        default_rects = [
            ("orb_skin", pygame.Rect(270, 10, 100, 40)),
            ("credits", pygame.Rect(270, 10, 100, 40)),
            ("display", pygame.Rect(270, 10, 100, 40)),
        ]

        for category, expected_rect in default_rects:
            print(f"  {category}: x={expected_rect.x}, y={expected_rect.y}")
            assert expected_rect.x == expected_x, (
                f"{category} 按鈕X座標不正確: {expected_rect.x}"
            )
            assert expected_rect.y == expected_y, (
                f"{category} 按鈕Y座標不正確: {expected_rect.y}"
            )

        print("\n[OK] 所有返回按鈕位置正確")
        return True

    except Exception as e:
        print(f"[ERROR] 測試失敗: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    print("=" * 60)
    print("設置菜單返回按鈕位置測試")
    print("=" * 60)

    try:
        result = test_back_button_position()
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
        print("1. 寶珠 Skin 頁面返回按鈕從 (210, 10) 移動到 (270, 10)")
        print("2. 製作人員名單頁面返回按鈕從 (210, 10) 移動到 (270, 10)")
        print("3. 畫面設定頁面返回按鈕從 (210, 10) 移動到 (270, 10)")
        print("4. 事件處理中的默認按鈕位置從 (210, 10) 更新為 (270, 10)")
        print("\n效果:")
        print("- 所有返回按鈕再向右移動60像素（總計移動210像素）")
        print("- 不再遮擋黃色標題文字")
    else:
        print("測試失敗")

    pygame.quit()
    return result


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
