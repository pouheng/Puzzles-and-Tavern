import json
import sys

sys.path.insert(0, ".")
from data.pets import Pet


def check_sample_descriptions():
    """检查几个示例宠物的技能描述"""
    with open("data/pets.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    sample_pets = [1, 3, 7, 12, 20]  # 检查几个代表性的宠物

    print("技能描述优化检查:")
    print("=" * 60)

    for pet_id in sample_pets:
        pet_data = [d for d in data["pets"] if d["id"] == pet_id][0]
        pet = Pet(pet_data)

        print(f"\n寵物: {pet_data['name']} (ID: {pet_id})")
        print(f"隊長技能: {pet.leader_skill.get_name()}")
        print(f"  描述: {pet.leader_skill.get_description()}")
        print(f"主動技能: {pet.active_skill.get_name()}")
        print(f"  描述: {pet.active_skill.get_description()}")

    print("\n" + "=" * 60)
    print("描述优化要点检查:")
    print("1. 是否使用自然语言（如'对单体敌人造成X倍伤害'而非'单體攻擊 X倍'）")
    print("2. 是否避免技术性简略表达（如'攻 2.0倍'）")
    print("3. 描述是否完整易懂")


if __name__ == "__main__":
    check_sample_descriptions()
