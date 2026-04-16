import pygame
import sys
import time
import json
import os
from config import *
from ui.inventory import Inventory
from ui.pet_detail import PetDetail
from ui.tab_bar import TabBar
from ui.codex import Codex
from ui.team import TeamManager, TeamView, TeamEditView, MAX_TEAMS
from ui.fonts import get_font
from data.pets import init_pet_database, create_sample_pets, Pet
from dungeon.battle import BattleView, BattleState
from dungeon.stages import (
    create_test_stage,
    load_stages,
    get_stage_name,
    get_stage_type,
)


pygame.init()


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(GAME_TITLE)
        self.clock = pygame.time.Clock()
        self.fullscreen = False
        self.battle_view = None

        self.inventory = Inventory()
        self.codex = None
        self.pet_detail = None
        self.selected_pet = None

        self.drag_start_time = 0
        self.drag_threshold = 0.15
        self.is_dragging = False
        self.drag_pet = None
        self.drag_start_pos = None

        self.team_manager = TeamManager(max_teams=MAX_TEAMS)
        self.team_view = TeamView(self.team_manager)
        self.team_edit_view = None

        self.tabs = TabBar(
            [
                ("地牢", None),
                ("組隊", None),
                ("背包", None),
                ("圖鑑", None),
                ("設置", None),
            ],
            x=0,
            y=SCREEN_HEIGHT - 70,
            width=SCREEN_WIDTH,
            height=70,
        )

        self.load_pets()

        self.orb_skin_config = self.load_orb_skin_config()
        self.selected_orb_skin = self.orb_skin_config.get("default", "default")

        self.stages = []
        self.load_stages()
        self.selected_stage_type = 1
        self.selected_stage_index = 0
        self.stage_scroll_offset = 0

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            self.screen = pygame.display.set_mode(
                (SCREEN_WIDTH, SCREEN_HEIGHT),
                pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF,
            )
        else:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        if self.battle_view:
            self.battle_view.screen = self.screen

    def load_stages(self):
        self.stages = load_stages()
        if not self.stages:
            # 如果沒有關卡資料，使用測試關卡
            self.stages = [create_test_stage()]

    def get_filtered_stages(self):
        return [s for s in self.stages if get_stage_type(s) == self.selected_stage_type]

    def load_pets(self):
        init_pet_database()
        sample_pets = create_sample_pets()
        for pet in sample_pets:
            self.inventory.add_pet(pet)

        self.codex = Codex(sample_pets)

        if sample_pets:
            self.team_manager.teams[0].add_member(sample_pets[0], 0)
            self.team_manager.set_active_team(0)

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F11:
                        self.toggle_fullscreen()
                        self.draw()
                        pygame.display.flip()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_mouse_down(event.pos)
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.handle_mouse_up(event.pos)
                elif event.type == pygame.MOUSEMOTION:
                    self.handle_mouse_motion(event.pos)
                elif event.type == pygame.MOUSEWHEEL:
                    self.handle_mouse_wheel(event, pygame.mouse.get_pos())

            self.draw()
            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

    def handle_mouse_down(self, pos):
        if self.battle_view is not None:
            self.battle_view.handle_mouse_down(pos)
            return

        if self.team_edit_view is not None:
            should_close = not self.team_edit_view.handle_click(pos)
            if should_close:
                self.team_edit_view = None
            return

        if self.pet_detail:
            if self.pet_detail.is_close_button_clicked(pos):
                self.pet_detail = None
                self.selected_pet = None
            elif hasattr(self.pet_detail, "handle_click"):
                result = self.pet_detail.handle_click(pos)
                if result == "close":
                    self.pet_detail = None
                    self.selected_pet = None
            return

        if self.tabs.handle_click(pos):
            return

        current_view = self.tabs.get_active_tab()

        if current_view == "地牢":
            if hasattr(self, "start_battle_rect"):
                self.handle_dungeon_click(pos)
            return
        elif current_view == "組隊":
            result = self.team_view.handle_click(pos)
            if result == "select":
                self.team_edit_view = TeamEditView(
                    self.team_manager,
                    self.inventory.pets,
                    None,
                )
            elif isinstance(result, int):
                self.team_edit_view = TeamEditView(
                    self.team_manager,
                    self.inventory.pets,
                    result,
                )
        elif current_view == "背包":
            clicked_pet = self.inventory.get_pet_at(pos)
            if clicked_pet:
                self.drag_pet = clicked_pet
                self.drag_start_pos = pos
                self.drag_start_time = time.time()
                self.is_dragging = False
        elif current_view == "圖鑑":
            clicked_pet = self.codex.get_pet_at(pos)
            if clicked_pet and clicked_pet.id in self.inventory.get_owned_ids():
                self.selected_pet = clicked_pet
                self.pet_detail = PetDetail(clicked_pet, self.screen, self.inventory)
        elif current_view == "設置":
            self.handle_settings_click(pos)

    def handle_mouse_up(self, pos):
        if self.battle_view is not None:
            self.battle_view.handle_mouse_up(pos)
            return

        if self.team_edit_view is None:
            if self.drag_pet and self.is_dragging:
                self.inventory.drop_pet(pos)
            elif self.drag_pet and not self.is_dragging:
                elapsed = time.time() - self.drag_start_time
                if elapsed < self.drag_threshold:
                    self.selected_pet = self.drag_pet
                    self.pet_detail = PetDetail(
                        self.drag_pet, self.screen, self.inventory
                    )

            if self.team_view:
                self.team_view.handle_mouse_up(pos)

        self.drag_pet = None
        self.drag_start_pos = None
        self.is_dragging = False

        # 重置pet_detail的拖曳狀態
        if self.pet_detail:
            self.pet_detail.last_drag_y = None

    def handle_mouse_wheel(self, event, mouse_pos):
        if self.pet_detail and self.pet_detail.fusion_selection_mode:
            self.pet_detail.handle_scroll(event, mouse_pos)

    def handle_mouse_motion(self, pos):
        if not hasattr(self, "battle_view"):
            return
        if self.battle_view is not None:
            self.battle_view.handle_mouse_motion(pos)
            return

        if self.team_view:
            self.team_view.handle_mouse_down(pos)

        # 處理pet_detail的拖曳滾動（只在按住鼠標時）
        if (
            self.pet_detail
            and self.pet_detail.fusion_selection_mode
            and pygame.mouse.get_pressed()[0]
        ):
            self.pet_detail.handle_drag(pos)

        if self.drag_pet and self.drag_start_pos:
            dx = pos[0] - self.drag_start_pos[0]
            dy = pos[1] - self.drag_start_pos[1]
            distance = (dx**2 + dy**2) ** 0.5

            if distance > 10:
                self.is_dragging = True
                self.inventory.start_drag(self.drag_pet, pos)
                self.drag_start_pos = None

    def draw(self):
        self.screen.fill(BG_COLOR)

        if self.battle_view is not None:
            self.battle_view.draw(self.screen)
            self.battle_view.update(1 / FPS)

            if self.battle_view.is_finished:
                should_restart = getattr(self.battle_view, "_should_restart", False)

                if hasattr(self.battle_view, "earned_rewards"):
                    for pet in self.battle_view.earned_rewards:
                        if pet:
                            new_pet_copy = pet.copy()
                            self.inventory.add_pet(new_pet_copy)
                if hasattr(self.battle_view, "earned_exp"):
                    if self.team_manager.active_team:
                        for pet in self.team_manager.active_team.members:
                            if pet:
                                pet.exp += self.battle_view.earned_exp

                if should_restart:
                    # 連戰模式：清除重啟標記並重新開始戰鬥
                    self.battle_view._should_restart = False
                    self.battle_view.restart_battle()
                else:
                    self.battle_view = None
                    self.team_manager.current_team_index = (
                        self.team_manager.active_team_index
                    )
            elif self.battle_view.state in (
                BattleState.VICTORY,
                BattleState.DEFEAT,
            ):
                pass  # 等待玩家點擊確認
            return

        current_view = self.tabs.get_active_tab()

        if self.team_edit_view is not None:
            self.team_edit_view.draw(self.screen)
            return

        if current_view == "地牢":
            self.draw_dungeon()
        elif current_view == "組隊":
            self.team_view.draw(self.screen, self.inventory.pets)
        elif current_view == "背包":
            self.draw_header(
                "背包",
                len(self.inventory.get_owned_ids()),
                len(self.inventory.get_all_pet_ids()),
            )
            self.inventory.draw(self.screen)
            hint_font = get_font(24)
            hint = hint_font.render(
                "點擊查看詳情 | 拖曳移動位置", True, (150, 150, 150)
            )
            self.screen.blit(hint, (50, SCREEN_HEIGHT - 90))
        elif current_view == "圖鑑":
            self.codex.draw(self.screen)
        elif current_view == "設置":
            self.draw_settings()

        self.tabs.draw(self.screen)

        if self.pet_detail:
            self.pet_detail.draw()

    def draw_dungeon(self):
        title_font = get_font(36)
        title = title_font.render("地牢", True, (255, 220, 100))
        self.screen.blit(title, (60, 10))

        active_team = self.team_manager.active_team
        info_font = get_font(24)
        info_text = info_font.render(
            f"出戰隊伍: {active_team.name}", True, (200, 200, 200)
        )
        self.screen.blit(info_text, (60, 55))

        member_count = active_team.get_member_count()
        count_text = info_font.render(f"隊員: {member_count}/6", True, (180, 180, 180))
        self.screen.blit(count_text, (60, 85))

        # 關卡類型分頁
        self.draw_stage_type_tabs()

        # 關卡列表
        self.draw_stage_list()

        # 開始戰鬥按鈕
        self.draw_start_battle_button()

    def draw_stage_type_tabs(self):
        stage_types = [
            (1, "主線劇情"),
            (2, "降臨關卡"),
            (3, "活動關卡"),
        ]

        font = get_font(20)
        y = 130
        for type_id, type_name in stage_types:
            x = 50 + (type_id - 1) * 140
            btn_rect = pygame.Rect(x, y, 130, 40)
            bg_color = (
                (50, 100, 200) if self.selected_stage_type == type_id else (40, 50, 60)
            )
            pygame.draw.rect(self.screen, bg_color, btn_rect, border_radius=5)
            text = font.render(type_name, True, (255, 255, 255))
            text_rect = text.get_rect(center=btn_rect.center)
            self.screen.blit(text, text_rect)

    def draw_stage_list(self):
        filtered_stages = self.get_filtered_stages()

        font = get_font(18)
        small_font = get_font(14)
        y = 190

        if not filtered_stages:
            empty_text = small_font.render("此分類暫無關卡", True, (150, 150, 150))
            self.screen.blit(empty_text, (60, y))
            return

        # 計算可顯示的數量
        visible_count = (SCREEN_HEIGHT - 300) // 60

        for i, stage in enumerate(filtered_stages):
            if i >= visible_count:
                break
            stage_y = y + i * 55
            bg_color = (40, 80, 150) if i == self.selected_stage_index else (35, 45, 55)
            rect = pygame.Rect(50, stage_y, SCREEN_WIDTH - 100, 50)
            pygame.draw.rect(self.screen, bg_color, rect, border_radius=3)

            name = get_stage_name(stage)
            name_text = font.render(name, True, (255, 255, 255))
            self.screen.blit(name_text, (60, stage_y + 10))

            from dungeon.stages import get_stage_exp

            exp = get_stage_exp(stage)
            exp_text = small_font.render(f"經驗: {exp}", True, (180, 180, 180))
            self.screen.blit(exp_text, (60, stage_y + 32))

    def draw_start_battle_button(self):
        filtered_stages = self.get_filtered_stages()
        if not filtered_stages:
            return

        btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 500, 200, 50)
        pygame.draw.rect(self.screen, (80, 120, 80), btn_rect, border_radius=5)
        pygame.draw.rect(self.screen, (120, 200, 120), btn_rect, 2)

        font = get_font(22)
        text = font.render("開始戰鬥", True, (255, 255, 255))
        text_rect = text.get_rect(center=btn_rect.center)
        self.screen.blit(text, text_rect)

        self.start_battle_rect = btn_rect

    def handle_dungeon_click(self, pos):
        # 檢查類型分頁點擊
        stage_types = [
            (1, "主線劇情"),
            (2, "降臨關卡"),
            (3, "活動關卡"),
        ]

        y = 130
        for type_id, type_name in stage_types:
            x = 50 + (type_id - 1) * 140
            btn_rect = pygame.Rect(x, y, 130, 40)
            if btn_rect.collidepoint(pos):
                self.selected_stage_type = type_id
                self.selected_stage_index = 0
                return

        # 檢查關卡列表點擊
        filtered_stages = self.get_filtered_stages()
        stage_y = 190
        visible_count = (SCREEN_HEIGHT - 300) // 60

        for i in range(min(len(filtered_stages), visible_count)):
            rect = pygame.Rect(50, stage_y + i * 55, SCREEN_WIDTH - 100, 50)
            if rect.collidepoint(pos):
                self.selected_stage_index = i
                return

        # 開始戰鬥按鈕
        if hasattr(self, "start_battle_rect") and self.start_battle_rect.collidepoint(
            pos
        ):
            self.start_battle()
            return

    def start_battle(self):
        filtered_stages = self.get_filtered_stages()
        if filtered_stages and self.selected_stage_index < len(filtered_stages):
            team = self.team_manager.active_team
            stage = filtered_stages[self.selected_stage_index]
            self.battle_view = BattleView(team, stage)

    def draw_header(self, title, count, total):
        title_font = get_font(40)
        title_text = title_font.render(title, True, (255, 220, 100))
        self.screen.blit(title_text, (60, 10))
        count_font = get_font(24)
        count_text = count_font.render(f"({count}/{total})", True, (180, 180, 180))
        self.screen.blit(count_text, (160, 15))

    def load_orb_skin_config(self):
        base_path = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(base_path, "data", "orb_skins.json")
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"skins": {}, "default": "default"}

    def save_orb_skin_config(self):
        base_path = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(base_path, "data", "orb_skins.json")
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(self.orb_skin_config, f, ensure_ascii=False, indent=2)

    def draw_settings(self):
        self.settings_category = getattr(self, "settings_category", "main")

        if self.settings_category == "main":
            self.draw_settings_main()
        elif self.settings_category == "orb_skin":
            self.draw_settings_orb_skin()
        elif self.settings_category == "credits":
            self.draw_settings_credits()
        elif self.settings_category == "display":
            self.draw_settings_display()

    def draw_settings_main(self):
        title_font = get_font(36)
        title = title_font.render("設置", True, (255, 220, 100))
        self.screen.blit(title, (60, 10))

        options = [
            ("寶珠 Skin", "orb_skin"),
            ("製作人員名單", "credits"),
            ("畫面設定", "display"),
        ]
        y = 80
        for label, category in options:
            btn_rect = pygame.Rect(60, y, 500, 60)
            bg_color = (
                (50, 80, 120)
                if getattr(self, "settings_category", "") != category
                else (70, 100, 150)
            )
            pygame.draw.rect(self.screen, bg_color, btn_rect, border_radius=5)
            label_text = get_font(22).render(label, True, (255, 255, 255))
            self.screen.blit(label_text, (80, y + 15))
            y += 70

    def draw_settings_orb_skin(self):
        title_font = get_font(36)
        title = title_font.render("寶珠 Skin", True, (255, 220, 100))
        self.screen.blit(title, (60, 10))

        back_btn = pygame.Rect(270, 10, 100, 40)
        pygame.draw.rect(self.screen, (60, 60, 80), back_btn, border_radius=5)
        back_text = get_font(18).render("← 返回", True, (255, 255, 255))
        self.screen.blit(back_text, (280, 18))
        self.settings_back_btn = back_btn

        section_y = 80
        section_label = get_font(22).render("選擇皮膚", True, (200, 200, 200))
        self.screen.blit(section_label, (60, section_y))

        y = section_y + 50
        skin_list = self.orb_skin_config.get("skins", {})

        if not skin_list:
            empty_text = get_font(16).render(
                "尚未有 Skin 配置，請使用開發者工具新增", True, (150, 150, 150)
            )
            self.screen.blit(empty_text, (60, y + 20))
            return

        for skin_key, skin_data in skin_list.items():
            skin_name = skin_data.get("name", skin_key)
            is_selected = skin_key == self.selected_orb_skin

            bg_color = (50, 100, 150) if is_selected else (40, 50, 60)
            btn_rect = pygame.Rect(60, y, 500, 60)
            pygame.draw.rect(self.screen, bg_color, btn_rect, border_radius=5)

            name_text = get_font(18).render(skin_name, True, (255, 255, 255))
            self.screen.blit(name_text, (75, y + 15))

            preview_x = 80
            for j, orb_type in enumerate(["火", "水", "木", "光", "暗", "心"]):
                path_key = skin_data.get(orb_type, "")
                if path_key:
                    base_path = os.path.dirname(os.path.abspath(__file__))
                    img_path = os.path.join(
                        base_path, "assets", "images", f"{path_key}.png"
                    )
                    if os.path.exists(img_path):
                        try:
                            img = pygame.image.load(img_path)
                            img = pygame.transform.scale(img, (30, 30))
                            self.screen.blit(img, (preview_x + j * 40, y + 30))
                        except:
                            pass

            if is_selected:
                check_text = get_font(14).render("✓ 已選", True, (100, 255, 100))
                self.screen.blit(check_text, (420, y + 20))

            y += 70

    def handle_settings_click(self, pos):
        category = getattr(self, "settings_category", "main")

        if category == "main":
            options = [
                ("寶珠 Skin", "orb_skin"),
                ("製作人員名單", "credits"),
                ("畫面設定", "display"),
            ]
            y = 80
            for label, cat in options:
                btn_rect = pygame.Rect(60, y, 500, 60)
                if btn_rect.collidepoint(pos):
                    self.settings_category = cat
                    return
                y += 70
        elif category == "orb_skin":
            back_btn = getattr(self, "settings_back_btn", pygame.Rect(270, 10, 100, 40))
            if back_btn.collidepoint(pos):
                self.settings_category = "main"
                return

            if pos[1] < 130:
                return

            y = 130
            skin_list = self.orb_skin_config.get("skins", {})

            for skin_key in skin_list.keys():
                btn_rect = pygame.Rect(60, y, 500, 60)
                if btn_rect.collidepoint(pos):
                    self.selected_orb_skin = skin_key
                    self.orb_skin_config["default"] = skin_key
                    self.save_orb_skin_config()
                    return
                y += 70
        elif category == "credits":
            back_btn = getattr(self, "settings_back_btn", pygame.Rect(270, 10, 100, 40))
            if back_btn.collidepoint(pos):
                self.settings_category = "main"
                return
        elif category == "display":
            back_btn = getattr(self, "settings_back_btn", pygame.Rect(270, 10, 100, 40))
            if back_btn.collidepoint(pos):
                self.settings_category = "main"
                return
            if hasattr(
                self, "display_window_btn"
            ) and self.display_window_btn.collidepoint(pos):
                if self.fullscreen:
                    self.toggle_fullscreen()
            elif hasattr(
                self, "display_fullscreen_btn"
            ) and self.display_fullscreen_btn.collidepoint(pos):
                if not self.fullscreen:
                    self.toggle_fullscreen()

    def draw_settings_credits(self):
        title_font = get_font(36)
        title = title_font.render("製作人員名單", True, (255, 220, 100))
        self.screen.blit(title, (60, 10))

        back_btn = pygame.Rect(270, 10, 100, 40)
        pygame.draw.rect(self.screen, (60, 60, 80), back_btn, border_radius=5)
        back_text = get_font(18).render("← 返回", True, (255, 255, 255))
        self.screen.blit(back_text, (280, 18))
        self.settings_back_btn = back_btn

        y = 80

        credits = [
            ("製作人", "头皮慶"),
            ("使用模型", "Opencode的Big Pickle"),
            ("", "深度求索官方api"),
            ("", "Deep seek chat"),
            ("", "deep seek reasoner"),
        ]

        for label, value in credits:
            if label:  # 如果有標籤，顯示標籤和值
                label_text = get_font(22).render(f"{label}:", True, (200, 200, 200))
                self.screen.blit(label_text, (60, y))
                value_text = get_font(22).render(value, True, (255, 255, 255))
                self.screen.blit(value_text, (180, y))
            else:  # 如果沒有標籤，只顯示值（用於換行顯示）
                value_text = get_font(22).render(value, True, (255, 255, 255))
                self.screen.blit(value_text, (180, y))
            y += 50

    def draw_settings_display(self):
        title_font = get_font(36)
        title = title_font.render("画面设定", True, (255, 220, 100))
        self.screen.blit(title, (60, 10))

        back_btn = pygame.Rect(270, 10, 100, 40)
        pygame.draw.rect(self.screen, (60, 60, 80), back_btn, border_radius=5)
        back_text = get_font(18).render("← 返回", True, (255, 255, 255))
        self.screen.blit(back_text, (280, 18))
        self.settings_back_btn = back_btn

        y = 80

        mode_label = get_font(22).render("显示模式:", True, (200, 200, 200))
        self.screen.blit(mode_label, (60, y))

        y += 45

        window_btn = pygame.Rect(60, y, 200, 50)
        fullscreen_btn = pygame.Rect(280, y, 200, 50)

        is_window = not self.fullscreen

        pygame.draw.rect(
            self.screen,
            (50, 120, 80) if is_window else (40, 50, 60),
            window_btn,
            border_radius=5,
        )
        window_text = get_font(20).render("窗口模式", True, (255, 255, 255))
        self.screen.blit(
            window_text,
            (
                window_btn.centerx - window_text.get_width() // 2,
                window_btn.centery - 10,
            ),
        )

        pygame.draw.rect(
            self.screen,
            (50, 100, 150) if not is_window else (40, 50, 60),
            fullscreen_btn,
            border_radius=5,
        )
        fullscreen_text = get_font(20).render("全萤幕", True, (255, 255, 255))
        self.screen.blit(
            fullscreen_text,
            (
                fullscreen_btn.centerx - fullscreen_text.get_width() // 2,
                fullscreen_btn.centery - 10,
            ),
        )

        self.display_window_btn = window_btn
        self.display_fullscreen_btn = fullscreen_btn


if __name__ == "__main__":
    game = Game()
    game.run()
