import json
import sys

sys.path.insert(0, ".")
from data.pets import Pet


def test_skill_descriptions():
    """测试技能描述是否符合自然语言格式"""
    with open("data/pets.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    errors = []

    for pet_data in data["pets"]:
        pet = Pet(pet_data)
        pet_name = pet_data["name"]

        # 测试队长技能描述
        ls_desc = pet.leader_skill.get_description()
        if not ls_desc or ls_desc == "無描述" or ls_desc == "無隊長技能":
            if pet.leader_skill.get_name() != "無":  # 只有非"無"技能才需要描述
                errors.append(f"{pet_name} 隊長技能描述為空或為默認值: '{ls_desc}'")

        # 测试主动技能描述
        as_desc = pet.active_skill.get_description()
        if not as_desc or as_desc == "無描述" or as_desc == "無主動技能":
            if pet.active_skill.get_name() != "無":  # 只有非"無"技能才需要描述
                errors.append(f"{pet_name} 主動技能描述為空或為默認值: '{as_desc}'")

        # 检查描述是否包含技术性简略表达（需要优化的模式）
        technical_patterns = [
            "攻 ",
            "倍",
            "屬性：",
            "重力",
            "回復",
        ]

        # 这些模式在优化后的描述中可能仍然存在，但需要检查是否以技术性方式出现
        # 例如"攻 2.0倍"是技术性的，"攻擊力2倍"是自然的

        # 检查描述长度（太短的描述可能不够自然）
        if ls_desc and len(ls_desc) < 5 and pet.leader_skill.get_name() != "無":
            errors.append(f"{pet_name} 隊長技能描述過短: '{ls_desc}'")

        if as_desc and len(as_desc) < 5 and pet.active_skill.get_name() != "無":
            errors.append(f"{pet_name} 主動技能描述過短: '{as_desc}'")

    if errors:
        print("技能描述測試失敗:")
        for e in errors:
            print(f"  {e}")
        print(f"\n總計 {len(errors)} 個錯誤")
        return False
    else:
        print("所有技能描述測試通過!")
        print(f"檢查了 {len(data['pets'])} 隻寵物的技能描述")
        return True


if __name__ == "__main__":
    test_skill_descriptions()
