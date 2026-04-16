import json
import sys

sys.path.insert(0, ".")
from data.pets import Pet


class MockEnemy:
    """模拟敌人用于测试"""

    def __init__(self, hp=10000, attribute="無"):
        self.hp = hp
        self.attribute = attribute
        self.max_hp = hp

    def take_damage(self, damage):
        """受到伤害"""
        actual_damage = min(damage, self.hp)
        self.hp -= actual_damage
        return actual_damage


class MockTeam:
    """模拟队伍用于测试"""

    def __init__(self):
        self.buffs = {}


def test_skill_execution():
    """测试技能执行效果"""
    with open("data/pets.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    print("技能執行測試")
    print("=" * 60)

    # 测试火焰菜刀 (ID 3)
    pet_data = [d for d in data["pets"] if d["id"] == 3][0]
    pet = Pet(pet_data)

    print(f"\n1. 測試寵物: {pet_data['name']}")
    print(f"   屬性: {pet_data['attribute']}")
    print(f"   主動技能: {pet.active_skill.get_name()}")
    print(f"   技能描述: {pet.active_skill.get_description()}")

    # 验证描述包含火属性
    desc = pet.active_skill.get_description()
    assert "火" in desc, f"描述 '{desc}' 應包含'火'屬性"
    assert "10.0" in desc, f"描述 '{desc}' 應包含倍率10.0"

    # 模拟技能执行
    enemy = MockEnemy(hp=10000)
    context = {
        "attacker": pet,
        "enemies": [enemy],
        "target_index": 0,
        "team": MockTeam(),
    }

    result = pet.active_skill.execute(context)
    print(f"   執行結果: {result}")

    # 验证结果
    assert result["success"] == True, "技能應執行成功"
    assert "damage" in result, "結果應包含傷害值"
    assert result.get("attribute") == "火", (
        f"結果屬性應為'火'，實際為{result.get('attribute')}"
    )

    print(f"   造成傷害: {result.get('damage')}")
    print(f"   敵人剩餘HP: {enemy.hp}")
    print("   [PASS] 火焰菜刀測試通過")

    # 测试死亡之指 (ID 18)
    pet_data = [d for d in data["pets"] if d["id"] == 18][0]
    pet = Pet(pet_data)

    print(f"\n2. 測試寵物: {pet_data['name']}")
    print(f"   屬性: {pet_data['attribute']}")
    print(f"   主動技能: {pet.active_skill.get_name()}")
    print(f"   技能描述: {pet.active_skill.get_description()}")

    # 验证描述包含暗属性
    desc = pet.active_skill.get_description()
    assert "暗" in desc, f"描述 '{desc}' 應包含'暗'屬性"
    assert "1000.0" in desc, f"描述 '{desc}' 應包含倍率1000.0"

    # 模拟技能执行
    enemy = MockEnemy(hp=1000000)  # 更多HP因为伤害很高
    context = {
        "attacker": pet,
        "enemies": [enemy],
        "target_index": 0,
        "team": MockTeam(),
    }

    result = pet.active_skill.execute(context)
    print(f"   執行結果: {result}")

    # 验证结果
    assert result["success"] == True, "技能應執行成功"
    assert "damage" in result, "結果應包含傷害值"
    assert result.get("attribute") == "暗", (
        f"結果屬性應為'暗'，實際為{result.get('attribute')}"
    )

    print(f"   造成傷害: {result.get('damage')}")
    print(f"   敵人剩餘HP: {enemy.hp}")
    print("   [PASS] 死亡之指測試通過")

    # 测试其他属性攻击技能
    print(f"\n3. 測試其他屬性技能描述")

    test_cases = [
        (7, "灼炎龍王", "燃燒殆盡", "火"),
        (9, "戰女神瓦爾基里", "心轉光", None),  # 转换技能，不是攻击
        (12, "黑炎姬赫拉", "超重力世界", None),  # 重力技能
    ]

    for pet_id, pet_name, skill_name, expected_attribute in test_cases:
        pet_data = [d for d in data["pets"] if d["id"] == pet_id][0]
        pet = Pet(pet_data)

        desc = pet.active_skill.get_description()
        print(f"   {pet_name}: {desc}")

        if expected_attribute:
            assert expected_attribute in desc, (
                f"{pet_name} 描述應包含{expected_attribute}屬性"
            )

    print("\n" + "=" * 60)
    print("所有技能執行測試通過!")
    return True


if __name__ == "__main__":
    try:
        test_skill_execution()
    except AssertionError as e:
        print(f"\n[FAIL] 測試失敗: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] 發生錯誤: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
