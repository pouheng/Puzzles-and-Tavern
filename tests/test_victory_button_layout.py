"""
測試勝利畫面按鈕佈局
驗證按鈕位置計算正確，按鈕不重疊，且功能與位置匹配
"""

import unittest
import sys
import os

# 添加項目根目錄到Python路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/..")

from config import SCREEN_WIDTH, SCREEN_HEIGHT


def calculate_button_positions(has_next_floor=True):
    """
    計算按鈕位置（複製自draw_victory和handle_click中的邏輯）
    返回：(continue_btn, confirm_btn, next_btn) 的(x, y, width, height)元組
    """
    panel_width = 500
    panel_height = 550
    panel_x = SCREEN_WIDTH // 2 - panel_width // 2
    panel_y = SCREEN_HEIGHT // 2 - panel_height // 2

    btn_y = panel_y + panel_height - 100
    btn_width = 140
    btn_height = 50
    btn_spacing = 30

    if has_next_floor:
        # 有三個按鈕：連戰、返回、下一層
        total_width = 3 * btn_width + 2 * btn_spacing
        start_x = panel_x + (panel_width - total_width) // 2

        continue_btn = (start_x, btn_y, btn_width, btn_height)
        confirm_btn = (start_x + btn_width + btn_spacing, btn_y, btn_width, btn_height)
        next_btn = (
            start_x + 2 * btn_width + 2 * btn_spacing,
            btn_y,
            btn_width,
            btn_height,
        )
        return continue_btn, confirm_btn, next_btn
    else:
        # 有兩個按鈕：連戰、返回
        total_width = 2 * btn_width + btn_spacing
        start_x = panel_x + (panel_width - total_width) // 2

        continue_btn = (start_x, btn_y, btn_width, btn_height)
        confirm_btn = (start_x + btn_width + btn_spacing, btn_y, btn_width, btn_height)
        return continue_btn, confirm_btn, None


class TestVictoryButtonLayout(unittest.TestCase):
    def test_button_positions_with_next_floor(self):
        """測試有下一層時的按鈕位置"""
        continue_btn, confirm_btn, next_btn = calculate_button_positions(
            has_next_floor=True
        )

        # 檢查按鈕不為None
        self.assertIsNotNone(continue_btn)
        self.assertIsNotNone(confirm_btn)
        self.assertIsNotNone(next_btn)

        # 解包按鈕坐標
        cont_x, cont_y, cont_w, cont_h = continue_btn
        conf_x, conf_y, conf_w, conf_h = confirm_btn
        next_x, next_y, next_w, next_h = next_btn

        # 檢查按鈕不重疊
        # 連戰按鈕右邊緣應該小於返回按鈕左邊緣
        self.assertLess(cont_x + cont_w, conf_x, "連戰按鈕與返回按鈕重疊")
        # 返回按鈕右邊緣應該小於下一層按鈕左邊緣
        self.assertLess(conf_x + conf_w, next_x, "返回按鈕與下一層按鈕重疊")

        # 檢查按鈕在同一水平線上
        self.assertEqual(cont_y, conf_y, "連戰和返回按鈕Y坐標不同")
        self.assertEqual(cont_y, next_y, "連戰和下一層按鈕Y坐標不同")

        # 檢查按鈕尺寸一致
        self.assertEqual(cont_w, conf_w, "按鈕寬度不一致")
        self.assertEqual(cont_w, next_w, "按鈕寬度不一致")
        self.assertEqual(cont_h, conf_h, "按鈕高度不一致")
        self.assertEqual(cont_h, next_h, "按鈕高度不一致")

        # 檢查間距
        spacing = conf_x - (cont_x + cont_w)
        self.assertEqual(spacing, 30, "按鈕間距不正確")
        spacing = next_x - (conf_x + conf_w)
        self.assertEqual(spacing, 30, "按鈕間距不正確")

        print(f"有下一層時的按鈕位置:")
        print(f"  連戰: x={cont_x}, y={cont_y}, w={cont_w}, h={cont_h}")
        print(f"  返回: x={conf_x}, y={conf_y}, w={conf_w}, h={conf_h}")
        print(f"  下一層: x={next_x}, y={next_y}, w={next_w}, h={next_h}")

    def test_button_positions_without_next_floor(self):
        """測試沒有下一層時的按鈕位置"""
        continue_btn, confirm_btn, next_btn = calculate_button_positions(
            has_next_floor=False
        )

        # 檢查按鈕不為None
        self.assertIsNotNone(continue_btn)
        self.assertIsNotNone(confirm_btn)
        self.assertIsNone(next_btn)

        # 解包按鈕坐標
        cont_x, cont_y, cont_w, cont_h = continue_btn
        conf_x, conf_y, conf_w, conf_h = confirm_btn

        # 檢查按鈕不重疊
        self.assertLess(cont_x + cont_w, conf_x, "連戰按鈕與返回按鈕重疊")

        # 檢查按鈕在同一水平線上
        self.assertEqual(cont_y, conf_y, "連戰和返回按鈕Y坐標不同")

        # 檢查按鈕尺寸一致
        self.assertEqual(cont_w, conf_w, "按鈕寬度不一致")
        self.assertEqual(cont_h, conf_h, "按鈕高度不一致")

        # 檢查間距
        spacing = conf_x - (cont_x + cont_w)
        self.assertEqual(spacing, 30, "按鈕間距不正確")

        print(f"沒有下一層時的按鈕位置:")
        print(f"  連戰: x={cont_x}, y={cont_y}, w={cont_w}, h={cont_h}")
        print(f"  返回: x={conf_x}, y={conf_y}, w={conf_w}, h={conf_h}")

    def test_button_centering(self):
        """測試按鈕在面板中居中"""
        panel_width = 500
        btn_width = 140
        btn_spacing = 30

        # 測試有三個按鈕時
        total_width_3 = 3 * btn_width + 2 * btn_spacing
        panel_x = SCREEN_WIDTH // 2 - panel_width // 2
        start_x_3 = panel_x + (panel_width - total_width_3) // 2

        # 檢查按鈕組在面板中居中
        left_margin = start_x_3 - panel_x
        right_margin = (panel_x + panel_width) - (start_x_3 + total_width_3)
        self.assertEqual(left_margin, right_margin, "三個按鈕未在面板中居中")

        # 測試有兩個按鈕時
        total_width_2 = 2 * btn_width + btn_spacing
        start_x_2 = panel_x + (panel_width - total_width_2) // 2

        left_margin = start_x_2 - panel_x
        right_margin = (panel_x + panel_width) - (start_x_2 + total_width_2)
        self.assertEqual(left_margin, right_margin, "兩個按鈕未在面板中居中")

        print(f"按鈕居中檢查通過:")
        print(
            f"  三個按鈕總寬: {total_width_3}, 左邊距: {left_margin}, 右邊距: {right_margin}"
        )
        print(
            f"  兩個按鈕總寬: {total_width_2}, 左邊距: {left_margin}, 右邊距: {right_margin}"
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
