"""
自動測試腳本：運行第1章第1關
"""

import sys
import os

# 確保路徑正確
script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(script_dir)
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

os.chdir(project_dir)

from dungeon.stages import load_stages, get_stage_dialogue, get_stage_floors
from data.pets import init_pet_database, create_sample_pets, Pet


def test_chapter1_stage1():
    """測試第1章第1關"""
    print("=" * 50)
    print("開始測試：第1章第1關")
    print("=" * 50)

    # 載入關卡
    stages = load_stages()
    if not stages:
        print("錯誤：無法載入關卡")
        return None

    stage = stages[0]
    stage_name = stage.get("name", "未命名")
    print(f"\n關卡名稱：{stage_name}")

    # 獲取對話
    print("\n--- 關卡對話 ---")
    stage_dialogue = get_stage_dialogue(stage)
    print(f"對話數量：{len(stage_dialogue)}")
    for i, entry in enumerate(stage_dialogue):
        print(
            f'  [{i}] avatar={entry.avatar_image}, text="{entry.text}", position={entry.position}'
        )

    # 獲取樓層
    print("\n--- 樓層資訊 ---")
    floors = get_stage_floors(stage)
    print(f"樓層數量：{len(floors)}")
    for i, floor in enumerate(floors):
        print(f"\n  樓層 {i + 1}:")
        print(f"    敵人數量：{len(floor.enemies)}")
        print(f"    對話數量：{len(floor.dialogue)}")
        for j, dlg in enumerate(floor.dialogue):
            print(f"      對話[{j}]: {dlg}")

    # 測試團隊
    print("\n--- 測試團隊 ---")
    from ui.team import Team
    from data.pets import Pet

    init_pet_database()
    create_sample_pets()

    team = Team(0, "測試隊伍")

    # 添加一些寵物
    test_pets = [1, 2, 3, 4, 5, 6]  # 使用前6個寵物
    for i, pet_id in enumerate(test_pets):
        pet = Pet.get_by_id(pet_id)
        if pet:
            team.add_member(pet, i)

    print(f"團隊成員：")
    for i, pet in enumerate(team.members):
        if pet:
            print(f"  [{i}] {pet.name} (HP: {pet.hp}, ATK: {pet.attack})")

    # 模擬戰鬥
    print("\n--- 模擬戰鬥 ---")
    from dungeon.battle import BattleView

    battle = BattleView(team, stage)

    print(f"戰鬥初始狀態：{battle.state}")
    print(f"對話條目數：{len(battle.dialogue_entries)}")
    print(f"對話是否啟用：{battle.dialogue_active}")

    # 列出對話內容
    print("\n戰鬥對話內容：")
    for i, entry in enumerate(battle.dialogue_entries):
        print(f'  [{i}] text="{entry.text}"')

    # 測試完成
    print("\n" + "=" * 50)
    print("測試完成")
    print("=" * 50)

    return {
        "stage_name": stage_name,
        "stage_dialogue_count": len(stage_dialogue),
        "stage_dialogue_entries": [(e.text, e.avatar_image) for e in stage_dialogue],
        "floor_count": len(floors),
        "floor_dialogue_counts": [len(f.dialogue) for f in floors],
        "battle_state": str(battle.state),
        "battle_dialogue_count": len(battle.dialogue_entries),
        "battle_dialogue_active": battle.dialogue_active,
    }


if __name__ == "__main__":
    result = test_chapter1_stage1()
    print("\n\n=== 測試結果 ===")
    print(result)
