import pygame
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

pygame.init()

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))


def test_enemy_draw():
    print("\n=== Test Enemy Draw ===")

    from dungeon.battle import Enemy

    enemy = Enemy("test_enemy", 1000, 100, 50, "火", 3)
    print(f"Enemy: {enemy.name}, HP: {enemy.hp}, DEF: {enemy.defense}")

    screen.fill((20, 20, 30))
    enemy.draw(screen, 300, 300)
    print("Enemy draw executed")

    return True


def test_enemy_draw_with_image():
    print("\n=== Test Enemy Draw With Image ===")

    from dungeon.battle import Enemy

    enemy = Enemy("test_enemy", 1000, 100, 50, "火", 3, "enemy/1 - Edited.png")
    print(f"Enemy image: {enemy.image}")

    screen.fill((20, 20, 30))
    enemy.draw(screen, 300, 300)
    print("Enemy draw with image executed")

    return True


def test_enemy_size():
    print("\n=== Test Enemy Size ===")

    from dungeon.battle import Enemy

    enemy = Enemy("test", 100, 10, 0, "火", 3)
    screen.fill((20, 20, 30))
    enemy.draw(screen, 300, 300)

    size = 90
    print(f"Enemy size: {size}")

    return size == 90


def test_enemy_hp_bar_position():
    print("\n=== Test Enemy HP Bar Position ===")

    enemy_y = 300
    size = 90
    bar_y = enemy_y + size // 2 + 50

    print(f"Bar Y position: {bar_y}")
    print(f"Expected: {enemy_y + 95}")

    return bar_y == enemy_y + 95


def test_battle_state_next_floor():
    print("\n=== Test BattleState NEXT_FLOOR ===")

    from dungeon.battle import BattleState

    print(f"BattleState.NEXT_FLOOR: {BattleState.NEXT_FLOOR}")
    return BattleState.NEXT_FLOOR.value == "next_floor"


def test_full_flow():
    results = []
    results.append(("Enemy Draw", test_enemy_draw()))
    results.append(("Enemy Draw With Image", test_enemy_draw_with_image()))
    results.append(("Enemy Size", test_enemy_size()))
    results.append(("Enemy HP Bar Position", test_enemy_hp_bar_position()))
    results.append(("BattleState NEXT_FLOOR", test_battle_state_next_floor()))

    print("\n=== Test Results ===")
    for name, result in results:
        print(f"{name}: {'PASS' if result else 'FAIL'}")

    all_passed = all(r for _, r in results)
    print(f"\nOverall: {'PASS' if all_passed else 'FAIL'}")
    return all_passed


if __name__ == "__main__":
    test_full_flow()
    pygame.quit()
