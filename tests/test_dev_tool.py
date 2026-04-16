"""
開發者工具測試腳本
"""

import sys
import os

# 確保路徑正確
script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(script_dir)
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

os.chdir(project_dir)

import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT


def test_dialogue_editor():
    """測試對話編輯器"""
    print("=" * 50)
    print("測試：對話編輯器")
    print("=" * 50)

    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("測試對話編輯器")

    from dev_tool import DialogueEditorModal

    # 創建對話編輯器
    editor = DialogueEditorModal(screen, "welcome_1")

    print(f"對話key: {editor.dialogue_key}")
    print(f"對話名稱: {editor.dialogue_data.get('name')}")
    print(f"對話條目數: {len(editor.dialogue_data.get('entries', []))}")

    # 測試圖片加載
    editor._load_avatar_images()
    print(f"立繪圖片數: {len(getattr(editor, '_avatar_images', []))}")

    # 測試選擇器
    editor.show_avatar_selector()
    print(f"選擇器狀態: {getattr(editor, '_selecting_avatar', False)}")

    print("\n對話編輯器測試通過！")
    pygame.quit()
    return True


def test_stage_editor():
    """測試關卡編輯器"""
    print("\n" + "=" * 50)
    print("測試：關卡編輯器")
    print("=" * 50)

    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("測試關卡編輯器")

    from dev_tool import StageEditorModal

    # 創建關卡編輯器
    stage_data = {
        "name": "測試關卡",
        "floors": [
            {
                "floor_num": 1,
                "enemies": [{"name": "敵人1", "hp": 100, "attack": 10}],
                "dialogue": [],
            }
        ],
        "dialogue": [],
    }
    editor = StageEditorModal(screen, stage_data)

    print(f"關卡名稱: {editor.stage_data.get('name')}")
    print(f"樓層數: {len(editor.stage_data.get('floors', []))}")

    # 測試敵人圖片加載
    editor._load_enemy_images()
    print(f"敵人圖片數: {len(getattr(editor, '_enemy_images', []))}")

    # 測試選擇器
    editor.show_enemy_image_selector()
    print(f"選擇器狀態: {getattr(editor, '_selecting_enemy_image', False)}")

    print("\n關卡編輯器測試通過！")
    pygame.quit()
    return True


def test_image_directories():
    """測試圖片目錄"""
    print("\n" + "=" * 50)
    print("測試：圖片目錄")
    print("=" * 50)

    base_path = os.path.dirname(os.path.abspath(__file__))

    # 對話立繪目錄
    avatar_dir = os.path.join(base_path, "assets", "images", "avatar")
    if os.path.exists(avatar_dir):
        avatar_files = [
            f for f in os.listdir(avatar_dir) if f.endswith((".png", ".jpg", ".jpeg"))
        ]
        print(f"對話立繪圖片: {len(avatar_files)} 個")
    else:
        print("對話立繪目錄不存在，需要創建")
        os.makedirs(avatar_dir, exist_ok=True)

    # 敵人立繪目錄
    enemy_dir = os.path.join(base_path, "assets", "images", "enemy")
    if os.path.exists(enemy_dir):
        enemy_files = [
            f for f in os.listdir(enemy_dir) if f.endswith((".png", ".jpg", ".jpeg"))
        ]
        print(f"敵人立繪圖片: {len(enemy_files)} 個")
    else:
        print("敵人立繪目錄不存在，需要創建")
        os.makedirs(enemy_dir, exist_ok=True)

    print("\n圖片目錄測試通過！")
    return True


if __name__ == "__main__":
    print("開始開發者工具測試...\n")

    results = []

    try:
        results.append(("圖片目錄", test_image_directories()))
    except Exception as e:
        print(f"圖片目錄測試失敗: {e}")
        results.append(("圖片目錄", False))

    try:
        results.append(("對話編輯器", test_dialogue_editor()))
    except Exception as e:
        print(f"對話編輯器測試失敗: {e}")
        results.append(("對話編輯器", False))

    try:
        results.append(("關卡編輯器", test_stage_editor()))
    except Exception as e:
        print(f"關卡編輯器測試失敗: {e}")
        results.append(("關卡編輯器", False))

    print("\n" + "=" * 50)
    print("測試結果")
    print("=" * 50)
    for name, passed in results:
        status = "通過" if passed else "失敗"
        print(f"  {name}: {status}")

    all_passed = all(p for _, p in results)
    print(f"\n總結: {'全部通過' if all_passed else '有測試失敗'}")
