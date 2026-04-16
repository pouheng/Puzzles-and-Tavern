import json
import sys

sys.path.insert(0, ".")
from data.pets import Pet


class MockEnemy:
    def __init__(self, hp=10000, attribute="none"):
        self.hp = hp
        self.max_hp = hp
        self.attribute = attribute
        self.debuffs = {}

    def take_damage(self, damage):
        actual = min(damage, self.hp)
        self.hp -= actual
        return actual


def test_all_skills():
    with open("data/pets.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    print("=" * 60)
    print("Testing Multiple Skills")
    print("=" * 60)

    test_cases = [
        {"id": 2, "name": "金屬波利", "skill_name": "金屬撞擊"},
        {"id": 6, "name": "暗夜潛伏者", "ls_name": "狂戦士之血", "as_name": "吸血匕首"},
        {"id": 8, "name": "深海巨獸", "skill_name": "深海水壓"},
    ]

    all_passed = True

    for tc in test_cases:
        pet_data = [d for d in data["pets"] if d["id"] == tc["id"]][0]
        pet = Pet(pet_data)

        print(f"\n--- {tc['name']} (ID: {tc['id']}) ---")

        # Test leader skill if applicable
        if "ls_name" in tc:
            ls = pet.leader_skill
            ls_name = ls.get_name()
            ls_desc = ls.get_description()
            print(f"  Leader: {ls_name}")
            print(f"    Desc: {ls_desc}")

            # Verify description
            if "80%以下" in ls_desc and "80%以上" in ls_desc:
                print(f"    [PASS] Contains HP thresholds")
            else:
                print(f"    [FAIL] Missing HP thresholds in description")
                all_passed = False

        # Test active skill
        as_skill = pet.active_skill
        as_name = as_skill.get_name()
        as_desc = as_skill.get_description()

        print(f"  Active: {as_name}")
        print(f"    Desc: {as_desc}")

        # Test ID 2: 金屬撞擊 - should say "單體"
        if tc["id"] == 2:
            if "單體" in as_desc and "無視防禦" in as_desc:
                print(f"    [PASS] Contains 單體 and 無視防禦")
            else:
                print(f"    [FAIL] Missing required words")
                all_passed = False

        # Test ID 6: 吸血匕首 - should say "單體", attack mult, and heal percent
        if tc["id"] == 6:
            if "單體" in as_desc and "50" in as_desc and "回復" in as_desc:
                print(f"    [PASS] Contains correct info")
            else:
                print(f"    [FAIL] Missing required info")
                all_passed = False

        # Test ID 8: 深海水壓 - should say "當前HP" and "無法終結"
        if tc["id"] == 8:
            if "當前HP" in as_desc and ("無法終結" in as_desc or "無法" in as_desc):
                print(f"    [PASS] Contains current HP and cannot kill")
            else:
                print(f"    [FAIL] Missing required words")
                all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("ALL TESTS PASSED!")
        return 0
    else:
        print("SOME TESTS FAILED!")
        return 1


if __name__ == "__main__":
    sys.exit(test_all_skills())
