import pygame
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

pygame.init()

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))


def test_tiandi_skill_parsing():
    print("\n=== Test 天地創造 Skill Parsing ===")

    from dungeon.leader_skills import parse_leader_skill

    data = {
        "type": "composite",
        "effects": [
            {
                "type": "attribute",
                "attributes": ["火", "水", "木"],
                "hp_mult": 2.5,
                "recovery_mult": 2.5,
            },
            {
                "type": "specific_combo",
                "attributes": ["火", "水", "木", "光", "暗"],
                "min_count": 3,
                "attack_mult": 12.0,
            },
            {
                "type": "attribute_count",
                "attribute": "心",
                "min_count": 3,
                "attack_mult": 5.0,
            },
        ],
        "display_name": "天地創造",
    }

    skill = parse_leader_skill(data)
    print(f"Skill name: {skill.get_name()}")
    print(f"Description: {skill.get_description()}")

    return skill.get_name() == "天地創造"


def test_tiandi_hp_recovery_mult():
    print("\n=== Test 天地創造 HP/Recovery ===")

    from dungeon.leader_skills import parse_leader_skill

    data = {
        "type": "composite",
        "effects": [
            {
                "type": "attribute",
                "attributes": ["火", "水", "木"],
                "hp_mult": 2.5,
                "recovery_mult": 2.5,
            },
            {
                "type": "specific_combo",
                "attributes": ["火", "水", "木", "光", "暗"],
                "min_count": 3,
                "attack_mult": 12.0,
            },
            {
                "type": "attribute_count",
                "attribute": "心",
                "min_count": 3,
                "attack_mult": 5.0,
            },
        ],
    }

    skill = parse_leader_skill(data)
    context = {"team_attributes": ["火", "水", "木"]}

    hp_mult = skill.calculate_hp_mult(context)
    rec_mult = skill.calculate_recovery_mult(context)

    print(f"HP mult: {hp_mult}")
    print(f"Recovery mult: {rec_mult}")

    return hp_mult == 2.5 and rec_mult == 2.5


def test_tiandi_attack_3_colors():
    print("\n=== Test 天地創造 Attack (3 colors) ===")

    from dungeon.leader_skills import parse_leader_skill

    data = {
        "type": "composite",
        "effects": [
            {
                "type": "attribute",
                "attributes": ["火", "水", "木"],
                "hp_mult": 2.5,
                "recovery_mult": 2.5,
            },
            {
                "type": "specific_combo",
                "attributes": ["火", "水", "木", "光", "暗"],
                "min_count": 3,
                "attack_mult": 12.0,
            },
            {
                "type": "attribute_count",
                "attribute": "心",
                "min_count": 3,
                "attack_mult": 5.0,
            },
        ],
    }

    skill = parse_leader_skill(data)
    context = {"matched_by_attr": {"火": 5, "水": 4, "木": 3}}

    attack_mult = skill.calculate_attack_mult(context)
    print(f"Attack mult (3 colors): {attack_mult}")

    return attack_mult == 12.0


def test_tiandi_attack_5_colors():
    print("\n=== Test 天地創造 Attack (5 colors) ===")

    from dungeon.leader_skills import parse_leader_skill

    data = {
        "type": "composite",
        "effects": [
            {
                "type": "attribute",
                "attributes": ["火", "水", "木"],
                "hp_mult": 2.5,
                "recovery_mult": 2.5,
            },
            {
                "type": "specific_combo",
                "attributes": ["火", "水", "木", "光", "暗"],
                "min_count": 3,
                "attack_mult": 12.0,
            },
            {
                "type": "attribute_count",
                "attribute": "心",
                "min_count": 3,
                "attack_mult": 5.0,
            },
        ],
    }

    skill = parse_leader_skill(data)
    context = {"matched_by_attr": {"火": 5, "水": 4, "木": 3, "光": 3, "暗": 3}}

    attack_mult = skill.calculate_attack_mult(context)
    print(f"Attack mult (5 colors): {attack_mult}")

    return attack_mult == 12.0


def test_tiandi_attack_5_colors_heart():
    print("\n=== Test 天地創造 Attack (5 colors + heart) ===")

    from dungeon.leader_skills import parse_leader_skill

    data = {
        "type": "composite",
        "effects": [
            {
                "type": "attribute",
                "attributes": ["火", "水", "木"],
                "hp_mult": 2.5,
                "recovery_mult": 2.5,
            },
            {
                "type": "specific_combo",
                "attributes": ["火", "水", "木", "光", "暗"],
                "min_count": 3,
                "attack_mult": 12.0,
            },
            {
                "type": "attribute_count",
                "attribute": "心",
                "min_count": 3,
                "attack_mult": 5.0,
            },
        ],
    }

    skill = parse_leader_skill(data)
    context = {
        "matched_by_attr": {"火": 5, "水": 4, "木": 3, "光": 3, "暗": 3, "心": 3}
    }

    attack_mult = skill.calculate_attack_mult(context)
    print(f"Attack mult (5 colors + heart): {attack_mult}")

    return attack_mult == 60.0


def test_pet_creation():
    print("\n=== Test Pet with 天地創造 ===")

    from data.pets import Pet

    pet_data = {
        "id": 999,
        "name": "test",
        "rarity": 10,
        "hp": 5000,
        "attack": 2000,
        "recovery": 500,
        "attribute": "火",
        "race": "神",
        "leader_skill": {
            "type": "composite",
            "effects": [
                {
                    "type": "attribute",
                    "attributes": ["火", "水", "木"],
                    "hp_mult": 2.5,
                    "recovery_mult": 2.5,
                },
                {
                    "type": "specific_combo",
                    "attributes": ["火", "水", "木", "光", "暗"],
                    "min_count": 3,
                    "attack_mult": 12.0,
                },
                {
                    "type": "attribute_count",
                    "attribute": "心",
                    "min_count": 3,
                    "attack_mult": 5.0,
                },
            ],
            "display_name": "天地創造",
        },
        "active_skill": None,
        "awakenings": [],
    }

    pet = Pet(pet_data)

    print(f"Pet: {pet.name}")
    print(f"Leader skill: {pet.leader_skill.get_name()}")

    return pet.leader_skill.get_name() == "天地創造"


def test_full_flow():
    results = []
    results.append(("天地創造 Skill Parsing", test_tiandi_skill_parsing()))
    results.append(("HP/Recovery Mult", test_tiandi_hp_recovery_mult()))
    results.append(("Attack 3 Colors", test_tiandi_attack_3_colors()))
    results.append(("Attack 5 Colors", test_tiandi_attack_5_colors()))
    results.append(("Attack 5 Colors + Heart", test_tiandi_attack_5_colors_heart()))
    results.append(("Pet Creation", test_pet_creation()))

    print("\n=== Test Results ===")
    for name, result in results:
        print(f"{name}: {'PASS' if result else 'FAIL'}")

    all_passed = all(r for _, r in results)
    print(f"\nOverall: {'PASS' if all_passed else 'FAIL'}")
    return all_passed


if __name__ == "__main__":
    test_full_flow()
    pygame.quit()
