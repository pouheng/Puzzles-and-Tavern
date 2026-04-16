"""
測試對話和敵人圖片功能
"""

import sys
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(script_dir)
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

os.chdir(project_dir)

import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT
import shutil


def create_test_image(filepath, width=100, height=100, color=(255, 0, 0)):
    """創建測試圖片"""
    surface = pygame.Surface((width, height))
    surface.fill(color)
    pygame.image.save(surface, filepath)
    print(f"已創建測試圖片: {filepath}")


def test_avatar_image_injection():
    """測試對話立繪圖片注入"""
    print("=" * 50)
    print("測試：對話立繪圖片注入")
    print("=" * 50)

    base_path = os.path.dirname(os.path.abspath(__file__))
    avatar_dir = os.path.join(base_path, "assets", "images", "avatar")
    os.makedirs(avatar_dir, exist_ok=True)

    # 創建測試圖片
    test_file = os.path.join(avatar_dir, "test_avatar_1.png")
    create_test_image(test_file, color=(255, 0, 0))

    # 檢查檔案是否存在
    if os.path.exists(test_file):
        print(f"圖片已注入: {test_file}")
        print(f"檔案大小: {os.path.getsize(test_file)} bytes")

        # 嘗試加載圖片
        try:
            img = pygame.image.load(test_file)
            print(f"圖片尺寸: {img.get_width()}x{img.get_height()}")
            print("對話立繪圖片注入測試通過！")
            return True
        except Exception as e:
            print(f"加載圖片失敗: {e}")
            return False
    else:
        print("圖片注入失敗")
        return False


def test_enemy_image_injection():
    """測試敵人立繪圖片注入"""
    print("\n" + "=" * 50)
    print("測試：敵人立繪圖片注入")
    print("=" * 50)

    base_path = os.path.dirname(os.path.abspath(__file__))
    enemy_dir = os.path.join(base_path, "assets", "images", "enemy")
    os.makedirs(enemy_dir, exist_ok=True)

    # 創建測試圖片
    test_file = os.path.join(enemy_dir, "test_enemy_1.png")
    create_test_image(test_file, color=(0, 255, 0))

    # 檢查檔案是否存在
    if os.path.exists(test_file):
        print(f"圖片已注入: {test_file}")

        # 嘗試加載圖片
        try:
            img = pygame.image.load(test_file)
            print(f"圖片尺寸: {img.get_width()}x{img.get_height()}")
            print("敵人立繪圖片注入測試通過！")
            return True
        except Exception as e:
            print(f"加載圖片失敗: {e}")
            return False
    else:
        print("圖片注入失敗")
        return False


def test_avatar_image_selection():
    """測試對話立繪圖片選擇"""
    print("\n" + "=" * 50)
    print("測試：對話立繪圖片選擇")
    print("=" * 50)

    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    from dev_tool import DialogueEditorModal

    # 創建編輯器
    editor = DialogueEditorModal(screen)

    # 加载圖片列表
    editor._load_avatar_images()
    images = getattr(editor, "_avatar_images", [])

    print(f"對話立繪圖片列表: {len(images)} 張")
    for img in images[:5]:  # 顯示前5張
        print(f"  - {img}")

    # 測試選擇器
    editor.show_avatar_selector()
    selecting = getattr(editor, "_selecting_avatar", False)
    print(f"選擇器已打開: {selecting}")

    # 模擬選擇第一張圖片
    if images:
        first_img = images[0]
        print(f"模擬選擇圖片: {first_img}")

        # 測試 handle_avatar_selector_click
        test_pos = (100 + 50, 120 + 50)  # 測試位置
        result = editor.handle_avatar_selector_click(test_pos)
        print(f"點擊結果: {result}")

    pygame.quit()
    print("對話立繪圖片選擇測試通過！")
    return True


def test_enemy_image_selection():
    """測試敵人立繪圖片選擇"""
    print("\n" + "=" * 50)
    print("測試：敵人立繪圖片選擇")
    print("=" * 50)

    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    from dev_tool import StageEditorModal

    # 創建編輯器
    stage_data = {"name": "測試", "floors": [{"enemies": [{}], "dialogue": []}]}
    editor = StageEditorModal(screen, stage_data)

    # 加載圖片列表
    editor._load_enemy_images()
    images = getattr(editor, "_enemy_images", [])

    print(f"敵人立繪圖片列表: {len(images)} 張")
    for img in images[:5]:
        print(f"  - {img}")

    # 測試選擇器
    editor.show_enemy_image_selector()
    selecting = getattr(editor, "_selecting_enemy_image", False)
    print(f"選擇器已打開: {selecting}")

    # 模擬選擇
    if images:
        first_img = images[0]
        print(f"模擬選擇圖片: {first_img}")

        test_pos = (100 + 50, 120 + 50)
        result = editor.handle_enemy_image_selector_click(test_pos)
        print(f"點擊結果: {result}")

    pygame.quit()
    print("敵人立繪圖片選擇測試通過！")
    return True


def test_draw_selector():
    """測試繪製選擇器"""
    print("\n" + "=" * 50)
    print("測試：繪製選擇器")
    print("=" * 50)

    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.fill((0, 0, 0))

    # 測試對話立繪選擇器
    from dev_tool import DialogueEditorModal

    editor = DialogueEditorModal(screen)
    editor._load_avatar_images()
    editor.show_avatar_selector()
    editor.draw_avatar_selector()
    print("對話立繪選擇器繪製完成")

    # 測試敵人立繪選擇器
    from dev_tool import StageEditorModal

    stage_data = {"name": "測試", "floors": [{"enemies": [{}], "dialogue": []}]}
    editor2 = StageEditorModal(screen, stage_data)
    editor2._load_enemy_images()
    editor2.show_enemy_image_selector()
    editor2.draw_enemy_image_selector()
    print("敵人立繪選擇器繪製完成")

    pygame.quit()
    print("繪製選擇器測試通過！")
    return True


if __name__ == "__main__":
    print("開始圖片功能測試...\n")

    results = []

    try:
        results.append(("對話立繪圖片注入", test_avatar_image_injection()))
    except Exception as e:
        print(f"錯誤: {e}")
        results.append(("對話立繪圖片注入", False))

    try:
        results.append(("敵人立繪圖片注入", test_enemy_image_injection()))
    except Exception as e:
        print(f"錯誤: {e}")
        results.append(("敵人立繪圖片注入", False))

    try:
        results.append(("對話立繪圖片選擇", test_avatar_image_selection()))
    except Exception as e:
        print(f"錯誤: {e}")
        results.append(("對話立繪圖片選擇", False))

    try:
        results.append(("敵人立繪圖片選擇", test_enemy_image_selection()))
    except Exception as e:
        print(f"錯誤: {e}")
        results.append(("敵人立繪圖片選擇", False))

    try:
        results.append(("繪製選擇器", test_draw_selector()))
    except Exception as e:
        print(f"錯誤: {e}")
        results.append(("繪製選擇器", False))

    print("\n" + "=" * 50)
    print("測試結果")
    print("=" * 50)
    for name, passed in results:
        status = "通過" if passed else "失敗"
        print(f"  {name}: {status}")

    all_passed = all(p for _, p in results)
    print(f"\n總結: {'全部通過' if all_passed else '有測試失敗'}")
