import pygame
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import *
from dungeon.battle import Enemy
from dungeon.board import OrbBoard

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Screen Layout Test")


def test_screen_resolution():
    print("\n=== Test Screen Resolution ===")
    print(f"SCREEN_WIDTH: {SCREEN_WIDTH}, SCREEN_HEIGHT: {SCREEN_HEIGHT}")
    print(f"Expected: 1600x900")

    if SCREEN_WIDTH == 1600 and SCREEN_HEIGHT == 900:
        print("[OK] Screen resolution correct")
        return True
    else:
        print(f"[FAIL] Screen resolution incorrect: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")
        return False


def test_board_position():
    print("\n=== Test Board Position ===")
    print(f"BOARD_START_X: {BOARD_START_X}")
    print(f"BOARD_CELL_SIZE: {BOARD_CELL_SIZE}, BOARD_MARGIN: {BOARD_MARGIN}")

    # 計算珠子區域的位置
    board_width = BOARD_COLS * (BOARD_CELL_SIZE + BOARD_MARGIN)
    board_height = BOARD_ROWS * (BOARD_CELL_SIZE + BOARD_MARGIN)

    print(f"Board size: {board_width}x{board_height}")
    print(f"Board position: ({BOARD_START_X}, expected > 300)")

    # 直接檢查 battle.py 文件中的配置值
    battle_file = os.path.join(os.path.dirname(__file__), "..", "dungeon", "battle.py")
    with open(battle_file, "r", encoding="utf-8") as f:
        content = f.read()

    # 查找 board_start_y 的定義
    import re

    # 查找 __init__ 中的 board_start_y
    init_match = re.search(
        r"def __init__.*?self\.board_start_y = (\d+)", content, re.DOTALL
    )
    if init_match:
        board_start_y_init = int(init_match.group(1))
        print(f"Found board_start_y in __init__: {board_start_y_init}")
    else:
        print("[FAIL] Could not find board_start_y in __init__")
        return False

    # 查找 restart_battle 中的 board_start_y
    restart_match = re.search(
        r"def restart_battle.*?self\.board_start_y = (\d+)", content, re.DOTALL
    )
    if restart_match:
        board_start_y_restart = int(restart_match.group(1))
        print(f"Found board_start_y in restart_battle: {board_start_y_restart}")
    else:
        print("[FAIL] Could not find board_start_y in restart_battle")
        return False

    # 檢查是否都設置為500
    if board_start_y_init == 500 and board_start_y_restart == 500:
        print("[OK] Board y-position correctly set to 500 in both methods")

        # 也檢查其他位置值
        enemy_y_match = re.search(r"self\.enemy_y = (\d+)", content)
        team_members_y_match = re.search(r"self\.team_members_y = (\d+)", content)
        hp_bar_x_match = re.search(r"self\.hp_bar_x = (\d+)", content)
        hp_bar_y_match = re.search(r"self\.hp_bar_y = (\d+)", content)

        if enemy_y_match:
            enemy_y = int(enemy_y_match.group(1))
            print(f"enemy_y: {enemy_y} (should be 160)")

        if team_members_y_match:
            team_members_y = int(team_members_y_match.group(1))
            print(f"team_members_y: {team_members_y} (should be 360)")

        if hp_bar_x_match:
            hp_bar_x = int(hp_bar_x_match.group(1))
            print(f"hp_bar_x: {hp_bar_x} (should be 400)")

        if hp_bar_y_match:
            hp_bar_y = int(hp_bar_y_match.group(1))
            print(f"hp_bar_y: {hp_bar_y} (should be 440)")

        return True
    else:
        print(
            f"[FAIL] Board y-position incorrect: init={board_start_y_init}, restart={board_start_y_restart}"
        )
        return False


def test_enemy_size():
    print("\n=== Test Enemy Size ===")
    # 直接檢查 battle.py 文件中的敵人大小
    try:
        battle_file = os.path.join(
            os.path.dirname(__file__), "..", "dungeon", "battle.py"
        )
        with open(battle_file, "r", encoding="utf-8") as f:
            content = f.read()

        # 查找 Enemy 類的 draw 方法中的 size
        import re

        # 查找 draw 方法中的 size = 150
        draw_match = re.search(
            r"def draw\(self, screen, x, y\):.*?size = (\d+)", content, re.DOTALL
        )
        if draw_match:
            size = int(draw_match.group(1))
            print(f"Enemy draw size found: {size}")

            if size == 150:
                print("[OK] Enemy size is 150")
                return True
            else:
                print(f"[FAIL] Enemy size incorrect: {size}")
                return False
        else:
            # 嘗試其他模式
            size_match = re.search(r"size = 150", content)
            if size_match:
                print("[OK] Enemy size is 150 (found in file)")
                return True
            else:
                print("[FAIL] Enemy size not found as 150")
                return False
    except Exception as e:
        print(f"Error testing enemy size: {e}")
        return False


def test_inventory_size():
    print("\n=== Test Inventory Size ===")
    print(f"INVENTORY_CELL_SIZE: {INVENTORY_CELL_SIZE}")
    print(
        f"INVENTORY_GRID_COLS: {INVENTORY_GRID_COLS}, INVENTORY_GRID_ROWS: {INVENTORY_GRID_ROWS}"
    )

    if INVENTORY_CELL_SIZE == 130:
        print("[OK] Inventory cell size is 130")
        return True
    else:
        print(f"[FAIL] Inventory cell size incorrect: {INVENTORY_CELL_SIZE}")
        return False


def test_team_member_size():
    print("\n=== Test Team Member Size ===")
    # 直接檢查 battle.py 文件中的隊伍成員大小
    try:
        battle_file = os.path.join(
            os.path.dirname(__file__), "..", "dungeon", "battle.py"
        )
        with open(battle_file, "r", encoding="utf-8") as f:
            content = f.read()

        # 查找 team_member_size 的定義
        import re

        match = re.search(r"self\.team_member_size = (\d+)", content)
        if match:
            team_member_size = int(match.group(1))
            print(f"team_member_size found: {team_member_size}")

            if team_member_size == 80:
                print("[OK] Team member size is 80")

                # 也檢查 team_member_margin
                margin_match = re.search(r"self\.team_member_margin = (\d+)", content)
                if margin_match:
                    margin = int(margin_match.group(1))
                    print(f"team_member_margin: {margin}")

                return True
            else:
                print(f"[FAIL] Team member size incorrect: {team_member_size}")
                return False
        else:
            print("[FAIL] Could not find team_member_size in battle.py")
            return False
    except Exception as e:
        print(f"Error testing team member size: {e}")
        return False


def test_enemy_spacing():
    print("\n=== Test Enemy Spacing ===")
    # 檢查敵人間距
    try:
        battle_file = os.path.join(
            os.path.dirname(__file__), "..", "dungeon", "battle.py"
        )
        with open(battle_file, "r", encoding="utf-8") as f:
            content = f.read()

            # 查找draw_enemies方法中的spacing
            import re

            match = re.search(
                r"def draw_enemies\(self, screen\):.*?spacing = (\d+)",
                content,
                re.DOTALL,
            )
            if match:
                spacing = int(match.group(1))
                print(f"Enemy spacing in draw_enemies: {spacing}")

                if spacing == 200:
                    print("[OK] Enemy spacing is 200")
                    return True
                else:
                    print(f"[FAIL] Enemy spacing incorrect: {spacing}")
                    return False
            else:
                print("[FAIL] Could not find draw_enemies method")
                return False
    except Exception as e:
        print(f"Error testing enemy spacing: {e}")
        return False


def main():
    print("Testing Screen Layout and Element Sizes")
    print("=" * 50)

    results = []

    results.append(("Screen Resolution", test_screen_resolution()))
    results.append(("Board Position", test_board_position()))
    results.append(("Enemy Size", test_enemy_size()))
    results.append(("Inventory Size", test_inventory_size()))
    results.append(("Team Member Size", test_team_member_size()))
    results.append(("Enemy Spacing", test_enemy_spacing()))

    print("\n" + "=" * 50)
    print("Test Results:")
    print("=" * 50)

    all_passed = True
    for test_name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{test_name}: {status}")
        if not passed:
            all_passed = False

    print("=" * 50)
    if all_passed:
        print("All tests passed!")
    else:
        print("Some tests failed.")

    return all_passed


if __name__ == "__main__":
    success = main()
    pygame.quit()
    sys.exit(0 if success else 1)
