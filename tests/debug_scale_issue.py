"""
深度除错：敵人圖片倍率未實現問題

這個測試會檢查從數據文件到實際繪製的完整流程，
輸出每個步驟的詳細資訊，幫助定位問題。
"""

import pygame
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

pygame.init()
# 不需要實際視窗，但需要初始化pygame以便加載圖片
screen = pygame.Surface((1200, 800))

from dungeon.stages import load_stages, EnemyData, DungeonFloor, Stage, get_stage_floors
from dungeon.battle import Enemy, BattleView
from main import Game


def print_section(title):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def step1_check_json():
    """步驟1: 檢查stages.json中的scale數據"""
    print_section("步驟1: 檢查stages.json中的scale數據")

    json_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "data", "stages.json"
    )
    print(f"JSON檔案路徑: {json_path}")

    if not os.path.exists(json_path):
        print("錯誤: stages.json不存在!")
        return False

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"總關卡數量: {len(data)}")

    scale_found = False
    for stage_idx, stage in enumerate(data):
        print(f"\n關卡 {stage_idx}: {stage.get('name', '未命名')}")
        floors = stage.get("floors", [])
        for floor_idx, floor in enumerate(floors):
            enemies = floor.get("enemies", [])
            for enemy_idx, enemy in enumerate(enemies):
                scale = enemy.get("scale")
                has_scale = scale is not None
                scale_found = scale_found or has_scale
                print(
                    f"  樓層 {floor.get('floor_num', 'N/A')}, 敵人 {enemy_idx}: {enemy.get('name')}"
                )
                print(f"    scale: {scale} {'(存在)' if has_scale else '(不存在)'}")
                if has_scale:
                    print(f"    scale值: {scale} (類型: {type(scale)})")

    if not scale_found:
        print("警告: 沒有找到任何帶有scale字段的敵人!")

    return True


def step2_check_stage_loading():
    """步驟2: 檢查關卡加載後的scale數據"""
    print_section("步驟2: 檢查關卡加載後的scale數據")

    try:
        stages = load_stages()
        print(f"成功加載 {len(stages)} 個關卡")

        scale_found = False
        for stage_idx, stage in enumerate(stages):
            print(f"\n關卡 {stage_idx}: {stage.name} (類型: {stage.stage_type})")
            floors = get_stage_floors(stage)
            for floor_idx, floor in enumerate(floors):
                print(f"  樓層 {floor.floor_num}: {len(floor.enemies)} 個敵人")
                for enemy_idx, enemy_data in enumerate(floor.enemies):
                    has_scale = hasattr(enemy_data, "scale")
                    scale_found = scale_found or has_scale
                    print(f"    敵人 {enemy_idx}: {enemy_data.name}")
                    print(f"      scale屬性是否存在: {has_scale}")
                    if has_scale:
                        print(
                            f"      scale值: {enemy_data.scale} (類型: {type(enemy_data.scale)})"
                        )
                    else:
                        print(f"      警告: EnemyData沒有scale屬性!")

        if not scale_found:
            print("警告: 加載後的關卡數據中沒有找到scale屬性!")

        return True
    except Exception as e:
        print(f"錯誤: 加載關卡時發生異常: {e}")
        import traceback

        traceback.print_exc()
        return False


def step3_check_enemy_creation():
    """步驟3: 檢查從EnemyData創建Enemy實例"""
    print_section("步驟3: 檢查從EnemyData創建Enemy實例")

    try:
        # 創建測試EnemyData
        enemy_data = EnemyData(
            name="測試敵人",
            hp=1000,
            attack=100,
            defense=50,
            attribute="火",
            turns_until_action=3,
            image=None,
            scale=1.5,
        )

        print(f"EnemyData創建成功:")
        print(f"  名稱: {enemy_data.name}")
        print(f"  scale: {enemy_data.scale}")

        # 創建Enemy實例
        enemy = Enemy(
            enemy_data.name,
            enemy_data.hp,
            enemy_data.attack,
            enemy_data.defense,
            enemy_data.attribute,
            enemy_data.turns_until_action,
            enemy_data.image,
            enemy_data.scale,
        )

        print(f"Enemy實例創建成功:")
        print(f"  名稱: {enemy.name}")
        print(f"  scale屬性: {enemy.scale}")
        print(f"  scale類型: {type(enemy.scale)}")

        # 檢查draw方法中的計算
        base_size = 150
        calculated_size = int(base_size * enemy.scale)
        print(
            f"  計算大小: base_size({base_size}) * scale({enemy.scale}) = {calculated_size}"
        )

        return True
    except Exception as e:
        print(f"錯誤: 創建敵人時發生異常: {e}")
        import traceback

        traceback.print_exc()
        return False


def step4_check_battleview_initialization():
    """步驟4: 檢查BattleView初始化"""
    print_section("步驟4: 檢查BattleView初始化")

    try:
        # 加載關卡
        stages = load_stages()
        if not stages:
            print("錯誤: 沒有加載到關卡數據")
            return False

        # 尋找帶有scale的關卡
        target_stage = None
        for stage in stages:
            floors = get_stage_floors(stage)
            for floor in floors:
                for enemy_data in floor.enemies:
                    if hasattr(enemy_data, "scale") and enemy_data.scale != 1.0:
                        target_stage = stage
                        break
                if target_stage:
                    break
            if target_stage:
                break

        if not target_stage:
            print("警告: 沒有找到帶有非1.0 scale的關卡，使用第一個關卡")
            target_stage = stages[0]

        print(f"使用關卡: {target_stage.name}")

        # 創建簡單的隊伍（空隊伍）
        class MockTeam:
            def __init__(self):
                self.members = []

        mock_team = MockTeam()

        # 創建BattleView
        battle_view = BattleView(mock_team, target_stage)

        print(f"BattleView創建成功")
        print(f"  敵人數量: {len(battle_view.enemies)}")

        # 檢查每個敵人的scale
        for i, enemy in enumerate(battle_view.enemies):
            print(f"  敵人 {i}: {enemy.name}")
            print(f"    scale: {enemy.scale}")
            print(f"    scale類型: {type(enemy.scale)}")

            # 計算預期大小
            base_size = 150
            expected_size = int(base_size * enemy.scale)
            print(f"    預期繪製大小: {expected_size}")

        return True
    except Exception as e:
        print(f"錯誤: BattleView初始化時發生異常: {e}")
        import traceback

        traceback.print_exc()
        return False


def step5_check_draw_calculation():
    """步驟5: 檢查draw方法的計算"""
    print_section("步驟5: 檢查draw方法的計算")

    try:
        # 創建測試敵人
        test_scales = [0.5, 1.0, 1.5, 2.0]

        for scale in test_scales:
            enemy = Enemy(
                f"測試敵人 scale={scale}", 1000, 100, 50, "火", 3, scale=scale
            )

            print(f"\n測試 scale={scale}:")
            print(f"  enemy.scale: {enemy.scale}")

            # 模擬draw方法的計算
            base_size = 150
            size = int(base_size * enemy.scale)
            print(f"  計算的size: {size}")

            # 檢查圖片加載路徑
            if enemy.image:
                base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                img_path = os.path.join(
                    base_path, "assets", "images", enemy.image.replace("/", os.sep)
                )
                print(f"  圖片路徑: {img_path}")
                print(f"  圖片是否存在: {os.path.exists(img_path)}")
            else:
                print(f"  沒有圖片，將繪製矩形")

        return True
    except Exception as e:
        print(f"錯誤: 檢查draw計算時發生異常: {e}")
        import traceback

        traceback.print_exc()
        return False


def step6_check_actual_game_flow():
    """步驟6: 檢查實際遊戲流程"""
    print_section("步驟6: 檢查實際遊戲流程")

    try:
        # 創建Game實例（但不運行）
        print("創建Game實例...")
        game = Game()

        print(f"Game加載的關卡數量: {len(game.stages)}")

        # 尋找極限訓練道場
        target_stage = None
        for stage in game.stages:
            if "極限訓練道場" in stage.name:
                target_stage = stage
                break

        if target_stage:
            print(f"找到目標關卡: {target_stage.name}")
            floors = get_stage_floors(target_stage)
            for floor_idx, floor in enumerate(floors):
                print(f"  樓層 {floor.floor_num}: {len(floor.enemies)} 個敵人")
                for enemy_idx, enemy_data in enumerate(floor.enemies):
                    scale = getattr(enemy_data, "scale", None)
                    print(f"    敵人 {enemy_idx}: {enemy_data.name}")
                    print(f"      scale: {scale}")
        else:
            print("警告: 未找到'極限訓練道場'關卡")

        return True
    except Exception as e:
        print(f"錯誤: 檢查遊戲流程時發生異常: {e}")
        import traceback

        traceback.print_exc()
        return False


def step7_analyze_issues():
    """步驟7: 問題分析"""
    print_section("步驟7: 問題分析")

    print("可能的問題點:")
    print("1. 數據未正確保存到stages.json")
    print("2. 關卡加載時scale字段丟失")
    print("3. EnemyData沒有scale屬性")
    print("4. Enemy實例創建時未傳遞scale參數")
    print("5. draw方法中scale未正確使用")
    print("6. 圖片加載失敗，回退到矩形繪製")
    print("7. 遊戲加載了錯誤的關卡（非極限訓練道場）")
    print("8. 遊戲緩存了舊的關卡數據")
    print("\n建議的檢查步驟:")
    print("1. 確認stages.json中有scale字段")
    print("2. 確認遊戲重啟後加載了最新的stages.json")
    print("3. 在draw方法中添加調試輸出，確認scale值")
    print("4. 檢查敵人圖片是否存在")

    return True


def main():
    print("開始深度除錯敵人圖片倍率問題")
    print("=" * 60)

    results = []

    results.append(("檢查JSON數據", step1_check_json()))
    results.append(("檢查關卡加載", step2_check_stage_loading()))
    results.append(("檢查敵人創建", step3_check_enemy_creation()))
    results.append(("檢查BattleView初始化", step4_check_battleview_initialization()))
    results.append(("檢查Draw計算", step5_check_draw_calculation()))
    results.append(("檢查遊戲流程", step6_check_actual_game_flow()))
    results.append(("問題分析", step7_analyze_issues()))

    print_section("除錯結果總結")

    all_passed = all(result for _, result in results)

    for name, result in results:
        print(f"{name}: {'PASS' if result else 'FAIL'}")

    print(f"\n整體結果: {'所有檢查通過' if all_passed else '有檢查失敗'}")

    if all_passed:
        print("\n所有數據流檢查都通過，但功能仍未實現。")
        print("可能的原因:")
        print("1. 實際遊戲運行時使用了不同的代碼路徑")
        print("2. 圖片加載或繪製有問題")
        print("3. 需要實際運行遊戲觀察渲染結果")
    else:
        print("\n發現問題點，請查看上面的詳細輸出。")

    return all_passed


if __name__ == "__main__":
    success = main()
    pygame.quit()
    sys.exit(0 if success else 1)
