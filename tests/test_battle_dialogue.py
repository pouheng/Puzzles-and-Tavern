"""
自動戰鬥測試：第1關敵人死亡對話
"""

import sys
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(script_dir)
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

os.chdir(project_dir)

import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT
from dungeon.stages import load_stages, get_stage_dialogue
from ui.team import Team
from data.pets import init_pet_database, create_sample_pets, Pet
from dungeon.battle import BattleView, BattleState


def test_enemy_death_dialogue():
    """測試敵人死亡對話"""
    print("=" * 60)
    print("測試：敵人死亡對話觸發")
    print("=" * 60)

    # 初始化
    init_pet_database()
    create_sample_pets()

    # 載入關卡
    stages = load_stages()
    if not stages:
        print("錯誤：無法載入關卡")
        return False

    stage = stages[0]
    print(f"\n關卡: {stage.name}")

    # 檢查關卡對話設定
    stage_dialogue = get_stage_dialogue(stage)
    print(f"關卡對話數: {len(stage_dialogue)}")
    for i, entry in enumerate(stage_dialogue):
        print(f"  [{i}] trigger={entry.trigger}, text={entry.text[:20]}...")

    # 檢查樓層對話
    floors = stage.floors
    print(f"樓層數: {len(floors)}")
    if floors:
        floor_dialogue = floors[0].dialogue
        print(f"樓層對話數: {len(floor_dialogue)}")
        for i, entry in enumerate(floor_dialogue):
            print(f"  [{i}] trigger={entry.trigger}, text={entry.text[:20]}...")

    # 創建團隊
    team = Team(0, "測試團隊")
    for i in range(6):
        pet = Pet.get_by_id(i + 1)
        if pet:
            team.add_member(pet, i)

    print(f"\n團隊: {[pet.name if pet else 'None' for pet in team.members]}")

    # 創建戰鬥
    battle = BattleView(team, stage)

    print(f"\n初始狀態: {battle.state}")
    print(f"對話條目數: {len(battle.dialogue_entries)}")
    print(f"對話啟用: {battle.dialogue_active}")

    # 模擬戰鬥流程
    print("\n--- 模擬戰鬥開始 ---")

    # 1. 檢查初始對話（應該是 on_enter_floor）
    if battle.dialogue_active:
        print(f"初始對話狀態: {battle.state}")
        print(
            f"對話內容: {battle.dialogue_entries[0].text if battle.dialogue_entries else 'None'}"
        )
        print(
            f"觸發條件: {battle.dialogue_entries[0].trigger if battle.dialogue_entries else 'None'}"
        )

    # 2. 模擬消除所有敵人（自動獲勝）
    print("\n--- 模擬敵人死亡 ---")
    for enemy in battle.enemies:
        enemy.hp = 0  # 設定敵人HP為0

    # 完成初始對話（點擊直到對話結束）
    print("\n--- 完成初始對話 ---")
    while battle.dialogue_active and battle.current_dialogue_index < len(
        battle.dialogue_entries
    ):
        battle.handle_dialogue_click((100, 100))
    print(f"對話完成後狀態: {battle.state}")
    print(f"對話啟用: {battle.dialogue_active}")

    # 3. 檢查勝利
    battle.check_victory()
    print(f"檢查後狀態: {battle.state}")
    print(f"對話啟用: {battle.dialogue_active}")
    print(f"對話條目數: {len(battle.dialogue_entries)}")

    # 4. 模擬點擊對話（繼續）
    print("\n--- 模擬點擊對話 ---")
    if battle.dialogue_active:
        battle.handle_dialogue_click((100, 100))
        print(f"點擊後狀態: {battle.state}")
        print(f"對話啟用: {battle.dialogue_active}")

    # 5. 檢查最終狀態
    print("\n--- 最終狀態 ---")
    print(f"最終狀態: {battle.state}")
    if battle.state == BattleState.VICTORY:
        print(f"獲得經驗: {battle.earned_exp}")
        print(f"獲得獎勵: {len(battle.earned_rewards)}")

    # 測試結果
    success = battle.state == BattleState.VICTORY and len(battle.earned_rewards) > 0

    print("\n" + "=" * 60)
    print(f"測試結果: {'通過' if success else '失敗'}")
    print("=" * 60)

    return success


def test_full_battle_flow():
    """測試完整戰鬥流程"""
    print("\n" + "=" * 60)
    print("測試：完整戰鬥流程")
    print("=" * 60)

    # 初始化
    init_pet_database()
    create_sample_pets()

    # 載入關卡
    stages = load_stages()
    stage = stages[0]

    # 創建團隊
    team = Team(0, "測試團隊")
    for i in range(6):
        pet = Pet.get_by_id(i + 1)
        if pet:
            team.add_member(pet, i)

    # 創建戰鬥視圖
    class MockScreen:
        def fill(self, color):
            pass

        def blit(self, *args):
            pass

    battle = BattleView(team, stage)

    # 模擬完整流程
    print("\n流程1: 戰鬥開始")
    print(f"  狀態: {battle.state}")
    print(f"  敵人數: {len(battle.enemies)}")
    print(f"  敵人HP: {[e.hp for e in battle.enemies]}")

    # 流程2: 消除所有敵人（造成大量傷害）
    print("\n流程2: 造成傷害")
    for enemy in battle.enemies:
        damage = enemy.hp + 100  # 超過HP
        enemy.hp = max(0, enemy.hp - damage)
    print(f"  敵人HP: {[e.hp for e in battle.enemies]}")
    print(f"  敵人死亡: {[e.is_defeated() for e in battle.enemies]}")

    # 流程3: 檢查勝利（會觸發對話）
    print("\n流程3: 檢查勝利")
    battle.check_victory()
    print(f"  狀態: {battle.state}")
    print(f"  對話啟用: {battle.dialogue_active}")

    # 流程4: 模擬玩家點擊繼續
    print("\n流程4: 點擊對話")
    if battle.dialogue_active:
        battle.handle_dialogue_click((100, 100))
        print(f"  點擊後狀態: {battle.state}")

    # 流程5: 檢查最終勝利
    print("\n流程5: 最終勝利")
    if battle.state == BattleState.VICTORY:
        print(f"  勝利！獲得經驗: {battle.earned_exp}")
        print(f"  獲得獎勵數: {len(battle.earned_rewards)}")
        return True

    return False


if __name__ == "__main__":
    print("開始戰鬥對話測試...\n")

    results = []

    try:
        results.append(("敵人死亡對話", test_enemy_death_dialogue()))
    except Exception as e:
        print(f"錯誤: {e}")
        import traceback

        traceback.print_exc()
        results.append(("敵人死亡對話", False))

    try:
        results.append(("完整戰鬥流程", test_full_battle_flow()))
    except Exception as e:
        print(f"錯誤: {e}")
        import traceback

        traceback.print_exc()
        results.append(("完整戰鬥流程", False))

    print("\n" + "=" * 60)
    print("測試結果")
    print("=" * 60)
    for name, passed in results:
        status = "通過" if passed else "失敗"
        print(f"  {name}: {status}")

    all_passed = all(p for _, p in results)
    print(f"\n總結: {'全部通過' if all_passed else '有測試失敗'}")
