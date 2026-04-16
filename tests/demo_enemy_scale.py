"""
敵人圖片倍率功能演示

這個腳本演示了敵人圖片倍率功能：
1. 可以設置不同的圖片倍率（0.5x, 1.0x, 1.5x, 2.0x等）
2. 在開發者工具中編輯敵人圖片倍率
3. 在戰鬥中顯示不同大小的敵人圖片
"""

import pygame
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dungeon.battle import Enemy


def demo_enemy_scales():
    """演示不同倍率的敵人"""
    print("=== 敵人圖片倍率功能演示 ===\n")

    # 創建不同倍率的敵人
    scales = [0.5, 0.8, 1.0, 1.2, 1.5, 2.0]

    print("1. 創建不同倍率的敵人：")
    for scale in scales:
        enemy = Enemy(f"敵人 (倍率{scale}x)", 1000, 100, 50, "火", 3, scale=scale)
        base_size = 150
        actual_size = int(base_size * scale)
        print(
            f"   - {enemy.name}: 基礎大小={base_size}, 實際大小={actual_size}, 倍率={enemy.scale}"
        )

    print("\n2. 在開發者工具中使用：")
    print("   - 在關卡編輯器中，選擇敵人")
    print("   - 在右側面板中找到'圖片倍率'欄位")
    print("   - 點擊該欄位輸入數值（如：1.1、1.2、1.3等）")
    print("   - 按Enter鍵保存")

    print("\n3. 支援的倍率範圍：")
    print("   - 小倍率：0.1 - 0.9（縮小圖片）")
    print("   - 正常倍率：1.0（原始大小）")
    print("   - 大倍率：1.1 - 5.0（放大圖片）")

    print("\n4. 實際應用場景：")
    print("   - 小型敵人：使用0.5-0.8倍率")
    print("   - 普通敵人：使用1.0倍率（預設）")
    print("   - 大型敵人：使用1.2-2.0倍率")
    print("   - BOSS敵人：使用2.0-3.0倍率")

    print("\n5. 技術實現：")
    print("   - 敵人類別(Enemy)已支援scale屬性")
    print("   - EnemyData類別已支援scale屬性")
    print("   - 開發者工具(StageEditorModal)已支援編輯scale")
    print("   - 戰鬥系統已正確使用scale值渲染敵人")

    # 演示計算
    print("\n6. 大小計算示例：")
    base_size = 150
    test_scales = [0.5, 1.0, 1.5, 2.0]
    for scale in test_scales:
        size = int(base_size * scale)
        print(f"   - 倍率{scale}x: {base_size} × {scale} = {size}像素")

    return True


if __name__ == "__main__":
    demo_enemy_scales()
    print("\n=== 演示完成 ===")
