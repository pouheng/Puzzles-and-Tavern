import pygame
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

pygame.init()

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))


def test_extreme_training_floor_2():
    print("\n=== Test Extreme Training Floor 2 ===")

    with open("data/stages.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    stage = data[2]
    print(f"Stage name: {stage['name']}")
    print(f"Floor count: {len(stage['floors'])}")

    if len(stage["floors"]) >= 2:
        floor2 = stage["floors"][1]
        print(f"Floor 2 has {len(floor2['enemies'])} enemies")

        for i, enemy in enumerate(floor2["enemies"]):
            print(
                f"  Enemy {i + 1}: {enemy['name']}, HP={enemy['hp']}, ATK={enemy['attack']}, DEF={enemy['defense']}"
            )
            actions = enemy.get("actions", [])
            print(f"    Actions: {len(actions)}")
            for j, action in enumerate(actions):
                action_type = action.get("type", "attack")
                action_value = action.get("value", 0)
                action_turns = action.get("turns", 1)
                print(
                    f"      Action {j + 1}: type={action_type}, value={action_value}, turns={action_turns}"
                )

        return len(stage["floors"]) >= 2
    return False


def test_nullify_shield_over_1000():
    print("\n=== Test Nullify Shield Over 1000 ===")

    with open("data/stages.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    stage = data[2]
    floor2 = stage["floors"][1]

    for i, enemy in enumerate(floor2["enemies"]):
        print(f"Enemy {i + 1}: {enemy['name']}")
        actions = enemy.get("actions", [])
        for action in actions:
            if action.get("type") == "nullify_shield":
                value = action.get("value", 0)
                print(f"  Nullify shield value: {value}")
                if value >= 1000:
                    print(f"  Nullify shield >= 1000: PASS")
                    return True

    print("No nullify shield >= 1000 found")
    return False


def test_enemy_defense_in_stage():
    print("\n=== Test Enemy Defense in Stage ===")

    with open("data/stages.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    stage = data[2]
    floor2 = stage["floors"][1]

    enemy = floor2["enemies"][0]
    hp = enemy.get("hp", 0)
    defense = enemy.get("defense", 0)
    attack = enemy.get("attack", 0)

    print(f"Enemy HP: {hp}")
    print(f"Enemy DEF: {defense}")
    print(f"Enemy ATK: {attack}")

    return defense > 0


def test_enemy_in_battle():
    print("\n=== Test Enemy in Battle ===")

    from dungeon.battle import Enemy

    enemy = Enemy("test", 7000, 200, 160, "暗", 3)

    actions = [
        {"type": "attack", "value": 10, "turns": 3, "description": "Attack"},
        {"type": "nullify_shield", "value": 1000, "turns": 3, "description": "Nullify"},
        {"type": "attack", "value": 10, "turns": 3, "description": "Attack"},
        {"type": "attack", "value": 10, "turns": 3, "description": "Attack"},
    ]
    enemy.actions = [type("Action", (), a)() for a in actions]

    print(f"Enemy HP: {enemy.hp}")
    print(f"Enemy DEF: {enemy.defense}")
    print(f"Enemy ATK: {enemy.attack}")
    print(f"Enemy Actions: {len(enemy.actions)}")

    for action in enemy.actions:
        print(f"  {action.type}: {action.value}")

    return len(enemy.actions) >= 4


def test_full_flow():
    results = []
    results.append(("Extreme Training Floor 2", test_extreme_training_floor_2()))
    results.append(("Nullify Shield >= 1000", test_nullify_shield_over_1000()))
    results.append(("Enemy Defense > 0", test_enemy_defense_in_stage()))
    results.append(("Enemy in Battle", test_enemy_in_battle()))

    print("\n=== Test Results ===")
    for name, result in results:
        print(f"{name}: {'PASS' if result else 'FAIL'}")

    all_passed = all(r for _, r in results)
    print(f"\nOverall: {'PASS' if all_passed else 'FAIL'}")
    return all_passed


if __name__ == "__main__":
    test_full_flow()
    pygame.quit()
