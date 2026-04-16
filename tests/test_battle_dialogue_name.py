import pygame
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

pygame.init()

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

from dungeon.stages import load_stages, get_stage_dialogue


def test_load_dialogue_with_name():
    print("=== Test Load Dialogue With Name ===")

    stages = load_stages()
    stage = stages[0]

    dialogue = get_stage_dialogue(stage)
    print(f"Dialogue entries: {len(dialogue)}")

    for i, entry in enumerate(dialogue):
        print(f"  {i}: name={repr(entry.name)}, text={entry.text[:15]}")

    has_name = any(e.name for e in dialogue if e.name)
    print(f"Has name: {has_name}")
    return has_name


def test_full_flow():
    results = []
    results.append(("Load Dialogue", test_load_dialogue_with_name()))

    print("\n=== Test Results ===")
    for name, result in results:
        print(f"{name}: {'PASS' if result else 'FAIL'}")

    all_passed = all(r for _, r in results)
    print(f"\nOverall: {'PASS' if all_passed else 'FAIL'}")
    return all_passed


if __name__ == "__main__":
    test_full_flow()
    pygame.quit()
