import json
import sys

sys.path.insert(0, ".")
from data.pets import Pet


class MockEnemy:
    """Mock enemy for testing"""

    def __init__(self, hp=10000, attribute="none"):
        self.hp = hp
        self.attribute = attribute
        self.max_hp = hp
        self.debuffs = {}

    def take_damage(self, damage):
        actual_damage = min(damage, self.hp)
        self.hp -= actual_damage
        return actual_damage


def test_defense_break_skill():
    """Test 貫穿一擊 skill: 敵方防禦力減少 50%（持續 2 回合）"""
    print("Testing 貫穿一擊 (Defense Break)")
    print("-" * 40)

    with open("data/pets.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    # Get pet ID 4 (碧槍騎士)
    pet_data = [d for d in data["pets"] if d["id"] == 4][0]
    pet = Pet(pet_data)

    # Check skill name
    skill_name = pet.active_skill.get_name()
    if skill_name != "貫穿一擊":
        print(f"  [FAIL] Expected skill name '貫穿一擊', got '{skill_name}'")
        return False
    print(f"  [OK] Skill name: {skill_name}")

    # Check skill description
    desc = pet.active_skill.get_description()
    expected_desc_part = "50%"
    expected_turns_part = "2回合"

    if expected_desc_part not in desc:
        print(
            f"  [FAIL] Description should contain '{expected_desc_part}', got: {desc}"
        )
        return False
    print(f"  [OK] Description contains '{expected_desc_part}': {desc}")

    if expected_turns_part not in desc:
        print(
            f"  [FAIL] Description should contain '{expected_turns_part}', got: {desc}"
        )
        return False
    print(f"  [OK] Description contains '{expected_turns_part}'")

    # Test skill execution
    enemy = MockEnemy(hp=10000)
    context = {
        "attacker": pet,
        "enemies": [enemy],
        "target_index": 0,
    }

    result = pet.active_skill.execute(context)

    if not result.get("success"):
        print(f"  [FAIL] Skill execution failed: {result}")
        return False
    print(f"  [OK] Skill executed successfully")

    # Check debuff applied
    if not hasattr(enemy, "debuffs") or "defense_break" not in enemy.debuffs:
        print(f"  [FAIL] Defense break debuff not applied to enemy")
        return False

    debuff = enemy.debuffs["defense_break"]
    reduction = debuff.get("reduction")
    turns = debuff.get("turns")

    # Check reduction is 0.5 (50%)
    if abs(reduction - 0.5) > 0.01:
        print(f"  [FAIL] Defense reduction should be 0.5 (50%), got {reduction}")
        return False
    print(f"  [OK] Defense reduction: {reduction} (50%)")

    # Check duration is 2 turns
    if turns != 2:
        print(f"  [FAIL] Duration should be 2 turns, got {turns}")
        return False
    print(f"  [OK] Duration: {turns} turns")

    print("  [PASS] 貫穿一擊 test completed successfully\n")
    return True


def test_heal_skill():
    """Test 仙草凍治癒 skill: 回復500hp (no '單體' prefix)"""
    print("Testing 仙草凍治癒 (Heal)")
    print("-" * 40)

    with open("data/pets.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    # Get pet ID 1 (仙草凍)
    pet_data = [d for d in data["pets"] if d["id"] == 1][0]
    pet = Pet(pet_data)

    # Check skill name
    skill_name = pet.active_skill.get_name()
    if skill_name != "仙草凍治癒":
        print(f"  [FAIL] Expected skill name '仙草凍治癒', got '{skill_name}'")
        return False
    print(f"  [OK] Skill name: {skill_name}")

    # Check skill description
    desc = pet.active_skill.get_description()

    # Should contain "500HP"
    if "500HP" not in desc:
        print(f"  [FAIL] Description should contain '500HP', got: {desc}")
        return False
    print(f"  [OK] Description contains '500HP': {desc}")

    # Should NOT contain "單體"
    if "單體" in desc:
        print(f"  [FAIL] Description should NOT contain '單體', got: {desc}")
        return False
    print(f"  [OK] Description does not contain '單體'")

    # Should be simple "回復500HP" or similar
    if not desc.startswith("回復"):
        print(f"  [WARNING] Description might not start with '回復': {desc}")

    print("  [PASS] 仙草凍治癒 test completed successfully\n")
    return True


def main():
    print("=" * 60)
    print("Final Skills Test")
    print("=" * 60)

    all_passed = True

    # Test 1: 貫穿一擊
    if not test_defense_break_skill():
        all_passed = False

    # Test 2: 仙草凍治癒
    if not test_heal_skill():
        all_passed = False

    print("=" * 60)
    if all_passed:
        print("ALL TESTS PASSED!")
        print("[PASS] 貫穿一擊: 敵方防禦力減少 50%（持續 2 回合）")
        print("[PASS] 仙草凍治癒: 回復500hp (no '單體' prefix)")
        return 0
    else:
        print("SOME TESTS FAILED!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
