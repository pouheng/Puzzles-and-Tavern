import json
import sys

sys.path.insert(0, ".")
from data.pets import Pet


def test_skill_names():
    with open("data/pets.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    test_cases = [
        (1, "仙草凍", "無", "仙草凍治癒"),
        (2, "金屬波利", "無", "金屬撞擊"),
        (3, "火炎御廚", "火之魂", "火焰菜刀"),
        (4, "碧槍騎士", "木靈守護", "貫穿一擊"),
        (5, "聖光祭司", "聖光沐浴", "天使的祝福"),
        (6, "暗夜潛伏者", "狂戰士之血", "吸血匕首"),
        (7, "灼炎龍王", "龍王的咆哮", "燃燒殆盡"),
        (8, "深海巨獸", "深淵重壓", "深海水壓"),
        (9, "戰女神瓦爾基里", "勝利之光", "心轉光"),
        (10, "冥府神歐西里斯", "冥府的審判", "死者的時間"),
        (11, "蒼穹嵐龍喚士", "嵐龍共鳴", "水幕結界"),
        (12, "黑炎姬赫拉", "女王之睨", "超重力世界"),
        (13, "雷神托爾", "雷神之怒", "雷電充能"),
        (14, "破戒神別西卜", "蠅王的宴會", "猛毒之滴"),
        (15, "覺醒挪亞", "大洪水", "方舟撞擊"),
        (16, "聖煌天麒麟", "極光四源", "麒麟亂舞"),
        (17, "悠久之綠龍契士", "悠久之盾", "森羅萬象"),
        (18, "極醒暗埃", "冥道殘月破", "死亡之指"),
        (19, "雙子星導機神", "星導循環", "星軌變換"),
        (20, "創世之龍神", "天地創造", "元素歸零"),
    ]

    errors = []
    for pet_id, pet_name, expected_ls, expected_as in test_cases:
        pet_data = [d for d in data["pets"] if d["id"] == pet_id][0]
        pet = Pet(pet_data)

        actual_ls = pet.leader_skill.get_name()
        actual_as = pet.active_skill.get_name()

        if actual_ls != expected_ls:
            errors.append(
                f"ID {pet_id} {pet_name}: LS expected '{expected_ls}', got '{actual_ls}'"
            )
        if actual_as != expected_as:
            errors.append(
                f"ID {pet_id} {pet_name}: AS expected '{expected_as}', got '{actual_as}'"
            )

    if errors:
        print("FAILURES:")
        for e in errors:
            print(f"  {e}")
        return False
    else:
        print("All skill names displayed correctly!")
        return True


if __name__ == "__main__":
    test_skill_names()
