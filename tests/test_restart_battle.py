"""
自動測試腳本：測試連戰功能
模擬打敗主線第2關的兩個敵人，並測試連戰按鈕
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
from ui.team import Team
from dungeon.battle import BattleView, BattleState


def test_restart_battle():
    """測試連戰功能"""
    print("=" * 50)
    print("開始測試：連戰功能")
    print("=" * 50)

    # 載入關卡
    stages = load_stages()
    if not stages:
        print("錯誤：無法載入關卡")
        return None

    # 選擇主線第2關（索引3）
    if len(stages) <= 3:
        print(f"錯誤：關卡數量不足 {len(stages)}")
        return None

    stage = stages[3]
    stage_name = stage.name
    print(f"\n關卡名稱：{stage_name}")

    # 檢查敵人數量
    floors = get_stage_floors(stage)
    if not floors:
        print("錯誤：沒有樓層")
        return None

    floor = floors[0]
    print(f"敵人數量：{len(floor.enemies)}")
    for i, enemy_data in enumerate(floor.enemies):
        print(f"  敵人 {i}: {enemy_data.name} HP={enemy_data.hp}")

    # 初始化寵物資料庫
    init_pet_database()
    create_sample_pets()

    # 建立強力隊伍（使用高攻擊寵物）
    team = Team(0, "測試隊伍")

    # 添加寵物（使用雙子星導機神 ID=9 和仙草凍 ID=10？需要檢查pets.json）
    # 先嘗試獲取高攻擊寵物
    test_pet_ids = []
    for pet_id in range(1, 20):
        pet = Pet.get_by_id(pet_id)
        if pet and pet.attack > 1000:
            test_pet_ids.append(pet_id)
            if len(test_pet_ids) >= 6:
                break

    if not test_pet_ids:
        # 使用前6個寵物
        test_pet_ids = [1, 2, 3, 4, 5, 6]

    for i, pet_id in enumerate(test_pet_ids):
        pet = Pet.get_by_id(pet_id)
        if pet:
            team.add_member(pet, i)

    print(f"\n團隊成員：")
    for i, pet in enumerate(team.members):
        if pet:
            print(f"  [{i}] {pet.name} (HP: {pet.hp}, ATK: {pet.attack})")

    # 創建戰鬥視圖
    battle = BattleView(team, stage)
    print(f"\n戰鬥初始狀態：{battle.state}")
    print(f"敵人數量：{len(battle.enemies)}")

    # 跳過對話，確保可以進入勝利狀態
    battle.dialogue_active = False
    battle.death_dialogue_active = False
    battle.dialogue_entries = []
    battle.state = BattleState.PLAYING
    print(f"設定後狀態：{battle.state}")

    # 直接讓敵人死亡以測試勝利和連戰
    print("\n--- 直接擊敗敵人 ---")
    for enemy in battle.enemies:
        enemy.hp = 0
        enemy._was_alive = False  # 避免觸發死亡對話
        print(f"  設定 {enemy.name} HP=0")

    # 測試修復：死亡敵人不應行動
    print("\n--- 測試死亡敵人不攻擊 ---")
    initial_hp = battle.player_hp
    print(f"玩家初始HP: {initial_hp}")

    # 設定敵人行動計數，模擬他們即將攻擊
    for enemy in battle.enemies:
        enemy.turns_until_action = 1  # 下回合攻擊
        print(f"  設定 {enemy.name} 行動計數=1")

    # 結束玩家回合，死亡敵人應該不會攻擊
    battle.end_player_turn()
    print(f"結束玩家回合後玩家HP: {battle.player_hp}")

    if battle.player_hp < initial_hp:
        print(f"錯誤：玩家HP減少，表示死亡敵人仍在攻擊！")
        return False
    else:
        print("OK 死亡敵人沒有攻擊，修復有效")

    # 檢查勝利
    victory = battle.check_victory()
    print(f"檢查勝利結果：{victory}")
    print(f"戰鬥狀態：{battle.state}")

    # 應該進入VICTORY狀態
    if battle.state != BattleState.VICTORY:
        print("錯誤：戰鬥未進入VICTORY狀態")
        return False

    print("\n--- 測試連戰按鈕 ---")

    # 模擬點擊連戰按鈕
    # 先獲取連戰按鈕位置（參考battle.py的draw_victory方法）
    from config import SCREEN_WIDTH, SCREEN_HEIGHT

    panel_width = 500
    panel_height = 550
    panel_x = SCREEN_WIDTH // 2 - panel_width // 2
    panel_y = SCREEN_HEIGHT // 2 - panel_height // 2

    btn_y = panel_y + panel_height - 100
    btn_width = 140
    btn_height = 50
    btn_spacing = 30

    continue_btn = (
        panel_x + panel_width // 2 + btn_spacing // 2,
        btn_y,
        btn_width,
        btn_height,
    )

    print(f"連戰按鈕位置：{continue_btn}")

    # 模擬點擊連戰按鈕
    import pygame

    # 初始化pygame（如果未初始化）
    if not pygame.get_init():
        pygame.init()

    # 創建一個虛擬事件位置
    pos = (continue_btn[0] + btn_width // 2, continue_btn[1] + btn_height // 2)

    # 呼叫handle_click（這會設定_should_restart標記）
    battle.handle_click(pos)

    print(f"戰鬥是否結束：{battle.is_finished}")
    print(f"是否應該重啟：{getattr(battle, '_should_restart', False)}")

    # 檢查是否設定了重啟標記
    should_restart = getattr(battle, "_should_restart", False)
    if not should_restart:
        print("錯誤：連戰按鈕未設定重啟標記")
        return False

    # 現在模擬主迴圈處理重啟（如main.py中）
    if should_restart:
        print("\n--- 執行重啟 ---")
        battle._should_restart = False
        battle.restart_battle()

        print(f"重啟後狀態：{battle.state}")
        print(f"敵人數量：{len(battle.enemies)}")

        # 檢查敵人是否重置
        if len(battle.enemies) != 2:
            print(f"錯誤：重啟後敵人數量不正確 {len(battle.enemies)}")
            return False

        # 檢查敵人HP是否重置
        for enemy in battle.enemies:
            if enemy.hp <= 0:
                print(f"錯誤：敵人 {enemy.name} HP={enemy.hp} 未重置")
                return False
            print(f"  敵人 {enemy.name} HP={enemy.hp}/{enemy.max_hp}")

        # 測試技能殺死敵人
        print("\n--- 測試技能殺死敵人 ---")
        # 降低敵人HP以便技能能殺死
        for enemy in battle.enemies:
            enemy.hp = 50000  # 降低HP
            enemy.max_hp = 50000
            enemy._was_alive = True  # 確保標誌重置
            print(f"  降低 {enemy.name} HP={enemy.hp}")

        # 模擬技能造成傷害 (殺死第一個敵人)
        result = {"damage": 100000, "success": True, "target": 0}
        battle._process_skill_result(result)

        # 檢查第一個敵人是否死亡
        if not battle.enemies[0].is_defeated():
            print(
                f"錯誤：敵人 {battle.enemies[0].name} 未被技能殺死, HP={battle.enemies[0].hp}"
            )
            return False

        # 技能應該觸發check_victory，但我們再呼叫一次確保
        victory = battle.check_victory()
        print(f"技能後檢查勝利結果: {victory}")
        print(f"戰鬥狀態: {battle.state}")

        # 注意：當只有一個敵人死亡，另一個還活著時，不應該進入VICTORY狀態
        # 所以我們期望state不是VICTORY
        if battle.state == BattleState.VICTORY:
            print("錯誤：只有一個敵人死亡時不應進入VICTORY狀態")
            return False

        # 現在殺死第二個敵人
        result2 = {"damage": 100000, "success": True, "target": 1}
        battle._process_skill_result(result2)

        victory2 = battle.check_victory()
        print(f"殺死第二敵人後檢查勝利結果: {victory2}")
        print(f"戰鬥狀態: {battle.state}")

        if battle.state != BattleState.VICTORY:
            print("錯誤：所有敵人死亡後未進入VICTORY狀態")
            return False

        print("✓ 技能殺死敵人後正確進入勝利狀態")

    print("\n" + "=" * 50)
    print("連戰功能測試完成")
    print("=" * 50)

    return True


if __name__ == "__main__":
    success = test_restart_battle()
    if success:
        print("\n測試成功！")
        sys.exit(0)
    else:
        print("\n測試失敗！")
        sys.exit(1)
