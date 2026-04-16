import pygame
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

pygame.init()

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

from dungeon.battle import BattleState


def test_battle_state_next_floor():
    print("\n=== Test BattleState NEXT_FLOOR ===")
    print(f"BattleState.NEXT_FLOOR: {BattleState.NEXT_FLOOR}")
    return BattleState.NEXT_FLOOR.value == "next_floor"


def test_draw_next_floor_exists():
    print("\n=== Test Draw Next Floor Method ===")
    from dungeon.battle import BattleView

    result = hasattr(BattleView, "draw_next_floor")
    print(f"draw_next_floor exists: {result}")
    return result


def test_init_floor_exists():
    print("\n=== Test Init Floor Method ===")
    from dungeon.battle import BattleView

    result = hasattr(BattleView, "init_floor")
    print(f"init_floor exists: {result}")
    return result


def test_full_flow():
    results = []
    results.append(("BattleState NEXT_FLOOR", test_battle_state_next_floor()))
    results.append(("Draw Next Floor Method", test_draw_next_floor_exists()))
    results.append(("Init Floor Method", test_init_floor_exists()))

    print("\n=== Test Results ===")
    for name, result in results:
        print(f"{name}: {'PASS' if result else 'FAIL'}")

    all_passed = all(r for _, r in results)
    print(f"\nOverall: {'PASS' if all_passed else 'FAIL'}")
    return all_passed


if __name__ == "__main__":
    test_full_flow()
    pygame.quit()
