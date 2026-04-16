import pygame
import math
from config import *
from ui.fonts import get_font
from ui.image_loader import (
    load_pet_full_image,
    get_pet_full_image_size,
    load_pet_head_image,
)


class PetDetail:
    def __init__(self, pet, screen, inventory=None):
        self.pet = pet
        self.screen = screen
        self.inventory = inventory
        self.screen_width = SCREEN_WIDTH
        self.screen_height = SCREEN_HEIGHT

        self.panel_width = 450
        self.panel_height = 700
        self.panel_x = (self.screen_width - self.panel_width) // 2
        self.panel_y = (self.screen_height - self.panel_height) // 2

        self.close_button_rect = pygame.Rect(
            self.panel_x + self.panel_width - 50, self.panel_y + 10, 40, 40
        )

        self.show_max_stats = False
        # 按鈕放在卡片外右側，與基礎數值標題對齊
        self.max_stats_button_rect = pygame.Rect(
            self.panel_x + self.panel_width + 20, self.panel_y + 385, 120, 30
        )
        # 經驗值合成按鈕
        self.fusion_button_rect = pygame.Rect(
            self.panel_x + self.panel_width + 20, self.panel_y + 420, 120, 30
        )
        self.show_fusion_panel = False
        self.fusion_materials = []  # 儲存選擇的素材寵物
        self.fusion_selection_mode = False  # 是否正在選擇素材
        self.fusion_selecting_index = -1  # 當前正在選擇哪個位置

        # 選擇列表滾動相關
        self.scroll_offset = 0  # 滾動偏移量
        self.scroll_speed = 30  # 滾輪每次滾動的像素
        self.max_visible_rows = 2  # 可見行數
        self.cell_height = 68  # 每行高度 (cell_size + padding)
        self.last_drag_y = None  # 上次拖曳的Y座標

        self.font_large = get_font(32)
        self.font_medium = get_font(24)
        self.font_small = get_font(20)

        self.leader_skill_title_rect = pygame.Rect(0, 0, 0, 0)
        self.leader_skill_text_rect = pygame.Rect(0, 0, 0, 0)
        self.show_skill_popup = False
        self.skill_popup_type = None
        self.skill_popup_rect = pygame.Rect(0, 0, 0, 0)

    def show_skill_detail_popup(self, skill_type):
        self.show_skill_popup = True
        self.skill_popup_type = skill_type
        if skill_type == "leader":
            skill = self.pet.leader_skill
            title = skill.get_name() if skill else "無"
            text = skill.get_description() if skill else "無"
        elif skill_type == "active":
            skill = self.pet.active_skill
            title = skill.get_name() if skill else "無"
            text = skill.get_description() if skill else "無"
        else:
            title = "無"
            text = "無"

        font = self.font_small
        lines = []
        max_width = 350
        words = text.split()
        current_line = ""
        for word in words:
            test_line = current_line + word + " "
            if font.size(test_line)[0] > max_width and current_line:
                lines.append(current_line)
                current_line = word + " "
            else:
                current_line = test_line
        if current_line:
            lines.append(current_line)
        popup_height = 60 + len(lines) * 26

        self.skill_popup_rect = pygame.Rect(
            self.panel_x + self.panel_width + 20,
            self.panel_y + 300,
            400,
            popup_height,
        )
        self.skill_popup_title = title

    def handle_click(self, pos):
        if self.close_button_rect.collidepoint(pos):
            return "close"
        if hasattr(
            self, "leader_skill_title_rect"
        ) and self.leader_skill_title_rect.collidepoint(pos):
            self.show_skill_detail_popup("leader")
            return "show_skill"
        if hasattr(
            self, "leader_skill_text_rect"
        ) and self.leader_skill_text_rect.collidepoint(pos):
            self.show_skill_detail_popup("leader")
            return "show_skill"
        if hasattr(
            self, "active_skill_title_rect"
        ) and self.active_skill_title_rect.collidepoint(pos):
            self.show_skill_detail_popup("active")
            return "show_skill"
        if hasattr(
            self, "active_skill_text_rect"
        ) and self.active_skill_text_rect.collidepoint(pos):
            if not getattr(self, "show_active_inline", True):
                self.show_skill_detail_popup("active")
                return "show_skill"
        if self.max_stats_button_rect.collidepoint(pos):
            self.show_max_stats = not self.show_max_stats
            return "toggle_max"
        if self.fusion_button_rect.collidepoint(pos):
            self.show_fusion_panel = True
            self.fusion_materials = []  # 重置素材列表
            self.show_skill_popup = False  # 收起技能詳細介面
            return "open_fusion"
        if self.show_skill_popup:
            if not self.skill_popup_rect.collidepoint(pos):
                self.show_skill_popup = False
                return "close_popup"
        # 如果合成面板開啟，處理面板內的點擊
        if self.show_fusion_panel:
            return self.handle_fusion_click(pos)
        return None

    def is_close_button_clicked(self, pos):
        return self.close_button_rect.collidepoint(pos)

    def draw(self):
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        pygame.draw.rect(
            self.screen,
            (50, 50, 65),
            (self.panel_x, self.panel_y, self.panel_width, self.panel_height),
        )

        rarity_color = RARITY_COLORS.get(self.pet.rarity, (150, 150, 150))
        pygame.draw.rect(
            self.screen,
            rarity_color,
            (self.panel_x, self.panel_y, self.panel_width, self.panel_height),
            5,
        )

        self.draw_close_button()
        self.draw_pet_info_top()
        self.draw_pet_image_center()
        self.draw_stats()
        if not self.show_fusion_panel:
            self.draw_skills()
            self.draw_awakenings()

        if self.show_fusion_panel:
            self.draw_fusion_panel()

        if self.show_skill_popup and not self.show_fusion_panel:
            self.draw_skill_popup()

    def draw_close_button(self):
        pygame.draw.rect(
            self.screen,
            (200, 80, 80),
            (
                self.close_button_rect.x,
                self.close_button_rect.y,
                self.close_button_rect.width,
                self.close_button_rect.height,
            ),
        )
        font = get_font(30)
        text = font.render("X", True, (255, 255, 255))
        text_rect = text.get_rect(center=self.close_button_rect.center)
        self.screen.blit(text, text_rect)

    def draw_pet_info_top(self):
        name_color = RARITY_COLORS.get(self.pet.rarity, (255, 255, 255))
        main_attr_color = ATTRIBUTE_COLORS.get(self.pet.attribute, (200, 200, 200))

        name_text = self.font_large.render(self.pet.name, True, name_color)
        self.screen.blit(name_text, (self.panel_x + 20, self.panel_y + 20))

        # 等級顯示在名稱旁邊
        level_text = self.font_medium.render(
            f"Lv.{self.pet.level}", True, (255, 200, 100)
        )
        self.screen.blit(
            level_text,
            (self.panel_x + 20 + name_text.get_width() + 20, self.panel_y + 25),
        )

        info_y = self.panel_y + 60
        attr_text = self.pet.attribute
        sub_attr = getattr(self.pet, "sub_attribute", None)
        if sub_attr:
            attr_text = f"{self.pet.attribute}/{sub_attr}"
        info_text = self.font_medium.render(
            f"[{attr_text}] {self.pet.race}", True, main_attr_color
        )
        self.screen.blit(info_text, (self.panel_x + 20, info_y))

        info_x = self.panel_x + self.panel_width - 20
        stars_text = self.font_medium.render("★" * self.pet.rarity, True, name_color)
        stars_rect = stars_text.get_rect(topright=(info_x, info_y))
        self.screen.blit(stars_text, stars_rect)

        # 經驗值顯示 (在寵物圖片上方)
        if self.pet.level < 99:
            exp_text = self.font_small.render(
                f"EXP: {self.pet.exp}/{self.pet.max_exp}", True, (180, 180, 180)
            )
            self.screen.blit(exp_text, (self.panel_x + 20, self.panel_y + 92))

    def draw_pet_image_center(self):
        box_x = self.panel_x + 30
        box_y = self.panel_y + 100
        box_width = self.panel_width - 60
        box_height = 280

        main_attr_color = ATTRIBUTE_COLORS.get(self.pet.attribute, (200, 200, 200))

        pygame.draw.rect(
            self.screen, (25, 25, 35), (box_x, box_y, box_width, box_height)
        )

        sub_attr = getattr(self.pet, "sub_attribute", None)
        if sub_attr:
            sub_attr_color = ATTRIBUTE_COLORS.get(sub_attr, (200, 200, 200))
            pygame.draw.rect(
                self.screen, main_attr_color, (box_x, box_y, box_width, box_height), 4
            )
            pygame.draw.rect(
                self.screen,
                sub_attr_color,
                (box_x + 4, box_y + 4, box_width - 8, box_height - 8),
                2,
            )
        else:
            pygame.draw.rect(
                self.screen, main_attr_color, (box_x, box_y, box_width, box_height), 4
            )

        original_size = get_pet_full_image_size(self.pet.id)
        if original_size:
            img = load_pet_full_image(self.pet.id)
            if img:
                img_w, img_h = img.get_size()

                max_display_w = box_width * 1.2
                max_display_h = box_height * 1.2

                scale_w = max_display_w / img_w
                scale_h = max_display_h / img_h
                scale = min(scale_w, scale_h, 1.0)

                new_w = int(img_w * scale)
                new_h = int(img_h * scale)

                if scale < 1.0:
                    img = pygame.transform.smoothscale(img, (new_w, new_h))

                center_x = box_x + box_width // 2
                center_y = box_y + box_height // 2
                draw_x = center_x - img.get_width() // 2
                draw_y = center_y - img.get_height() // 2
                self.screen.blit(img, (draw_x, draw_y))
        else:
            font = get_font(80)
            placeholder = font.render("?", True, main_attr_color)
            placeholder_rect = placeholder.get_rect(
                center=(box_x + box_width // 2, box_y + box_height // 2)
            )
            self.screen.blit(placeholder, placeholder_rect)

    def draw_stats(self):
        stats_x = self.panel_x + 30
        stats_y = self.panel_y + 385

        title = self.font_medium.render("基礎數值", True, (255, 220, 100))
        self.screen.blit(title, (stats_x, stats_y))

        # 右側空位的滿級按鈕
        btn_color = (80, 120, 180) if not self.show_max_stats else (100, 150, 100)
        pygame.draw.rect(
            self.screen, btn_color, self.max_stats_button_rect, border_radius=5
        )
        btn_text = "滿級數值" if not self.show_max_stats else "當前數值"
        btn_font = get_font(14)
        btn_surface = btn_font.render(btn_text, True, (255, 255, 255))
        btn_rect = btn_surface.get_rect(center=self.max_stats_button_rect.center)
        self.screen.blit(btn_surface, btn_rect)

        # 經驗值合成按鈕
        fusion_btn_color = (120, 80, 180)
        pygame.draw.rect(
            self.screen, fusion_btn_color, self.fusion_button_rect, border_radius=5
        )
        fusion_btn_text = "經驗值合成"
        fusion_btn_surface = btn_font.render(fusion_btn_text, True, (255, 255, 255))
        fusion_btn_rect = fusion_btn_surface.get_rect(
            center=self.fusion_button_rect.center
        )
        self.screen.blit(fusion_btn_surface, fusion_btn_rect)

        stats_y += 30

        if self.show_max_stats:
            max_hp = self.pet._max_hp
            max_atk = self.pet._max_attack
            max_rcv = self.pet._max_recovery
            hp_text = self.font_small.render(f"HP: {max_hp}", True, (150, 255, 150))
            atk_text = self.font_small.render(f"攻撃: {max_atk}", True, (255, 150, 150))
            rcv_text = self.font_small.render(f"回復: {max_rcv}", True, (150, 220, 255))
        else:
            hp_text = self.font_small.render(
                f"HP: {self.pet.hp}", True, (100, 255, 100)
            )
            atk_text = self.font_small.render(
                f"攻撃: {self.pet.attack}", True, (255, 100, 100)
            )
            rcv_text = self.font_small.render(
                f"回復: {self.pet.recovery}", True, (100, 200, 255)
            )

        self.screen.blit(hp_text, (stats_x, stats_y))
        self.screen.blit(atk_text, (stats_x + 150, stats_y))
        self.screen.blit(rcv_text, (stats_x + 300, stats_y))

    def draw_skills(self):
        skills_x = self.panel_x + 30
        skills_y = self.panel_y + 450

        leader_skill_name = (
            self.pet.leader_skill.get_name() if self.pet.leader_skill else "無"
        )
        if leader_skill_name and leader_skill_name != "無":
            leader_title = self.font_medium.render(
                f"隊長技能: {leader_skill_name}", True, (255, 220, 100)
            )
            title_rect = leader_title.get_rect(x=skills_x, y=skills_y)
            self.leader_skill_title_rect = title_rect
        else:
            leader_title = self.font_medium.render("隊長技能", True, (255, 220, 100))
            self.leader_skill_title_rect = pygame.Rect(skills_x, skills_y, 200, 30)
        self.screen.blit(leader_title, (skills_x, skills_y))

        skills_y += 28
        leader_skill_text = (
            self.pet.leader_skill.get_description() if self.pet.leader_skill else "無"
        )
        self.show_leader_inline = True
        if leader_skill_text and leader_skill_text != "無":
            max_width = self.panel_width - 60
            words = leader_skill_text.split()
            lines = []
            current_line = ""
            for word in words:
                test_line = current_line + word + " "
                if self.font_small.size(test_line)[0] > max_width and current_line:
                    lines.append(current_line)
                    current_line = word + " "
                else:
                    current_line = test_line
            if current_line:
                lines.append(current_line)
            self.leader_skill_text_rect = pygame.Rect(
                skills_x, skills_y, max_width, len(lines) * 24
            )
            if len(lines) <= 3:
                for i, line in enumerate(lines):
                    line_surface = self.font_small.render(
                        line.strip(), True, (220, 220, 220)
                    )
                    self.screen.blit(line_surface, (skills_x, skills_y + i * 24))
                if lines:
                    skills_y += len(lines) * 24 + 12
            else:
                self.show_leader_inline = False
                hint_text = self.font_small.render(
                    "點擊查看詳情", True, (150, 150, 150)
                )
                self.screen.blit(hint_text, (skills_x, skills_y))

        skills_y += 25

        if self.pet.active_skill:
            skill_name = self.pet.active_skill.get_name()
            cooldown_val = self.pet.active_skill.get_cooldown()
            if skill_name and skill_name != "無":
                header_text = f"主動技能: {skill_name} (冷卻:{cooldown_val}回合)"
            else:
                header_text = f"主動技能 (冷卻:{cooldown_val}回合)"
        else:
            header_text = "主動技能"

        self.active_skill_title_rect = pygame.Rect(skills_x, skills_y, 250, 30)
        active_title = self.font_medium.render(header_text, True, (255, 220, 100))
        self.screen.blit(active_title, (skills_x, skills_y))

        skills_y += 32
        active_skill_text = (
            self.pet.active_skill.get_description() if self.pet.active_skill else "無"
        )
        self.show_active_inline = True
        if active_skill_text and active_skill_text != "無":
            max_width = self.panel_width - 60
            words = active_skill_text.split()
            lines = []
            current_line = ""
            for word in words:
                test_line = current_line + word + " "
                if self.font_small.size(test_line)[0] > max_width and current_line:
                    lines.append(current_line)
                    current_line = word + " "
                else:
                    current_line = test_line
            if current_line:
                lines.append(current_line)
            self.active_skill_text_rect = pygame.Rect(
                skills_x, skills_y, max_width, len(lines) * 24
            )
            if len(lines) <= 3:
                for i, line in enumerate(lines):
                    line_surface = self.font_small.render(
                        line.strip(), True, (220, 220, 220)
                    )
                    self.screen.blit(line_surface, (skills_x, skills_y + i * 24))
                if lines:
                    skills_y += len(lines) * 24 + 12
            else:
                self.show_active_inline = False
                hint_text = self.font_small.render(
                    "點擊查看詳情", True, (150, 150, 150)
                )
                self.screen.blit(hint_text, (skills_x, skills_y))

    def draw_awakenings(self):
        awake_x = self.panel_x + 30
        awake_y = self.panel_y + 620

        title = self.font_medium.render("覺醒技能", True, (255, 220, 100))
        self.screen.blit(title, (awake_x, awake_y))

        awake_x += 100
        x_offset = 0

        for awakening in self.pet.awakenings:
            if awake_x + x_offset + 85 > self.panel_x + self.panel_width - 20:
                awake_y += 28
                x_offset = 0

            box_x = self.panel_x + 100 + x_offset
            pygame.draw.rect(self.screen, (80, 160, 220), (box_x, awake_y, 80, 24), 0)
            pygame.draw.rect(self.screen, (120, 200, 255), (box_x, awake_y, 80, 24), 2)

            awake_text = self.font_small.render(awakening, True, (255, 255, 255))
            awake_rect = awake_text.get_rect(center=(box_x + 40, awake_y + 12))
            self.screen.blit(awake_text, awake_rect)

            x_offset += 85

    def draw_skill_popup(self):
        if not self.show_skill_popup:
            return

        rect = self.skill_popup_rect
        pygame.draw.rect(self.screen, (30, 30, 45), rect, border_radius=8)
        pygame.draw.rect(self.screen, (255, 215, 0), rect, 2, border_radius=8)

        skill_prefix = "隊長技能" if self.skill_popup_type == "leader" else "主動技能"
        title = self.font_medium.render(
            f"{skill_prefix}: {getattr(self, 'skill_popup_title', '')}",
            True,
            (255, 220, 100),
        )
        self.screen.blit(title, (rect.x + 15, rect.y + 10))

        text = ""
        if self.skill_popup_type == "leader":
            text = (
                self.pet.leader_skill.get_description()
                if self.pet.leader_skill
                else "無"
            )
        elif self.skill_popup_type == "active":
            text = (
                self.pet.active_skill.get_description()
                if self.pet.active_skill
                else "無"
            )

        font = self.font_small
        max_width = rect.width - 30
        words = text.split()
        lines = []
        current_line = ""
        for word in words:
            test_line = current_line + word + " "
            if font.size(test_line)[0] > max_width and current_line:
                lines.append(current_line)
                current_line = word + " "
            else:
                current_line = test_line
        if current_line:
            lines.append(current_line)

        for i, line in enumerate(lines):
            line_surface = font.render(line.strip(), True, (220, 220, 220))
            self.screen.blit(line_surface, (rect.x + 15, rect.y + 45 + i * 26))

        hint = self.font_small.render("點擊空白處關閉", True, (150, 150, 150))
        self.screen.blit(hint, (rect.x + 15, rect.y + rect.height - 25))

    def draw_fusion_panel(self):
        # 繪製半透明遮罩
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(220)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        # 合成面板
        panel_width = 700
        panel_height = 500
        panel_x = (self.screen_width - panel_width) // 2
        panel_y = (self.screen_height - panel_height) // 2

        # 面板背景
        pygame.draw.rect(
            self.screen,
            (60, 60, 80),
            (panel_x, panel_y, panel_width, panel_height),
            border_radius=10,
        )
        pygame.draw.rect(
            self.screen,
            (100, 100, 140),
            (panel_x, panel_y, panel_width, panel_height),
            width=4,
            border_radius=10,
        )

        # 標題
        title_font = get_font(36)
        title = title_font.render("經驗值合成", True, (255, 220, 100))
        self.screen.blit(
            title, (panel_x + panel_width // 2 - title.get_width() // 2, panel_y + 20)
        )

        # 提示文字
        hint_font = get_font(16)
        hint = hint_font.render(
            "選擇5隻寵物作為素材，合成後將獲得經驗值", True, (200, 200, 200)
        )
        self.screen.blit(
            hint, (panel_x + panel_width // 2 - hint.get_width() // 2, panel_y + 70)
        )

        # 中央：當前寵物
        center_x = panel_x + panel_width // 2
        center_y = panel_y + panel_height // 2
        center_rect = pygame.Rect(center_x - 60, center_y - 60, 120, 120)
        pygame.draw.rect(self.screen, (80, 80, 100), center_rect, border_radius=10)
        pygame.draw.rect(
            self.screen, (120, 120, 180), center_rect, width=3, border_radius=10
        )

        # 繪製當前寵物頭像
        head_img = load_pet_head_image(self.pet.id)
        if head_img:
            img_size = min(center_rect.width - 10, center_rect.height - 10)
            head_img = pygame.transform.smoothscale(head_img, (img_size, img_size))
            self.screen.blit(
                head_img,
                (
                    center_rect.centerx - head_img.get_width() // 2,
                    center_rect.centery - head_img.get_height() // 2,
                ),
            )

        # 周圍5個位置（五角形佈局）
        radius = 180
        angles = [0, 72, 144, 216, 288]  # 每72度一個
        self.material_rects = []

        for i, angle in enumerate(angles):
            rad = angle * 3.14159 / 180
            x = center_x + radius * math.cos(rad)
            y = center_y + radius * math.sin(rad)

            slot_rect = pygame.Rect(x - 50, y - 50, 100, 100)
            pygame.draw.rect(self.screen, (70, 70, 90), slot_rect, border_radius=8)
            pygame.draw.rect(
                self.screen, (100, 100, 140), slot_rect, width=3, border_radius=8
            )

            # 如果已選擇素材，顯示寵物頭像
            if i < len(self.fusion_materials) and self.fusion_materials[i]:
                material = self.fusion_materials[i]
                head_img = load_pet_head_image(material.id)
                if head_img:
                    img_size = min(slot_rect.width - 10, slot_rect.height - 10)
                    head_img = pygame.transform.smoothscale(
                        head_img, (img_size, img_size)
                    )
                    self.screen.blit(
                        head_img,
                        (
                            slot_rect.centerx - head_img.get_width() // 2,
                            slot_rect.centery - head_img.get_height() // 2,
                        ),
                    )
            else:
                # 顯示加號按鈕
                plus_font = get_font(40)
                plus_text = plus_font.render("+", True, (150, 150, 150))
                self.screen.blit(
                    plus_text,
                    (
                        slot_rect.centerx - plus_text.get_width() // 2,
                        slot_rect.centery - plus_text.get_height() // 2,
                    ),
                )

            self.material_rects.append(slot_rect)

        # 按鈕區域
        button_y = panel_y + panel_height - 80
        # 返回按鈕
        back_btn = pygame.Rect(panel_x + 50, button_y, 100, 40)
        pygame.draw.rect(self.screen, (120, 80, 80), back_btn, border_radius=5)
        back_font = get_font(20)
        back_text = back_font.render("返回", True, (255, 255, 255))
        self.screen.blit(
            back_text,
            (
                back_btn.centerx - back_text.get_width() // 2,
                back_btn.centery - back_text.get_height() // 2,
            ),
        )

        # 計算有效的素材數量
        valid_materials = [m for m in self.fusion_materials if m is not None]
        valid_count = len(valid_materials)

        # 選擇按鈕 - 按順序填入素材
        select_btn = pygame.Rect(panel_x + 160, button_y, 100, 40)
        select_color = (80, 100, 180) if valid_count < 5 else (60, 60, 60)
        pygame.draw.rect(self.screen, select_color, select_btn, border_radius=5)
        select_text = back_font.render("選擇", True, (255, 255, 255))
        self.screen.blit(
            select_text,
            (
                select_btn.centerx - select_text.get_width() // 2,
                select_btn.centery - select_text.get_height() // 2,
            ),
        )

        # 確定合成按鈕（僅當有素材時可用）
        confirm_btn = pygame.Rect(panel_x + panel_width - 170, button_y, 120, 40)
        confirm_color = (80, 120, 80) if valid_count > 0 else (60, 60, 60)
        pygame.draw.rect(self.screen, confirm_color, confirm_btn, border_radius=5)
        confirm_font = get_font(20)
        confirm_text = confirm_font.render("確定合成", True, (255, 255, 255))
        self.screen.blit(
            confirm_text,
            (
                confirm_btn.centerx - confirm_text.get_width() // 2,
                confirm_btn.centery - confirm_text.get_height() // 2,
            ),
        )

        # 儲存按鈕矩形供點擊檢測
        self.fusion_back_btn = back_btn
        self.fusion_select_btn = select_btn
        self.fusion_confirm_btn = confirm_btn

        # 顯示總經驗值
        if valid_count > 0:
            total_exp = self.calculate_total_exp()
            exp_font = get_font(24)
            exp_text = exp_font.render(f"總經驗值: {total_exp}", True, (255, 255, 200))
            self.screen.blit(
                exp_text,
                (panel_x + panel_width // 2 - exp_text.get_width() // 2, button_y - 40),
            )

        # 如果處於選擇模式，顯示寵物選擇列表
        if self.fusion_selection_mode and self.inventory:
            # 計算可用寵物列表
            valid_materials = [m for m in self.fusion_materials if m is not None]
            available_pets = []
            for pet in self.inventory.pets:
                if pet.id == self.pet.id:
                    continue  # 不能使用自己
                if pet in valid_materials:
                    continue  # 已經選擇過了
                available_pets.append(pet)

            if available_pets:
                # 計算列表尺寸
                cell_size = 60
                padding = 8
                cols_per_row = 10
                self.cell_height = cell_size + padding

                # 計算總行數和內容高度
                total_rows = (len(available_pets) + cols_per_row - 1) // cols_per_row
                total_content_height = (
                    total_rows * self.cell_height + 40
                )  # 40 for title

                # 可視區域
                list_height = 200
                list_y = panel_y + panel_height + 20
                list_rect = pygame.Rect(panel_x, list_y, panel_width, list_height)

                # 限制滾動範圍
                max_scroll = max(0, total_content_height - list_height)
                self.scroll_offset = max(0, min(self.scroll_offset, max_scroll))

                # 保存列表區域供滾動檢測
                self.selection_list_rect = list_rect

                # 繪製選擇列表背景
                pygame.draw.rect(self.screen, (40, 40, 50), list_rect, border_radius=8)
                pygame.draw.rect(
                    self.screen, (80, 80, 100), list_rect, width=2, border_radius=8
                )

                # 標題
                select_font = get_font(18)
                select_title = select_font.render(
                    f"選擇素材寵物: {len(available_pets)} 隻 (拖曳/滾輪滾動)",
                    True,
                    (255, 220, 100),
                )
                self.screen.blit(select_title, (panel_x + 10, list_y + 10))

                # 顯示寵物頭像網格
                start_x = panel_x + padding
                start_y = list_y + 40 - self.scroll_offset

                self.select_pet_rects = []
                for idx, pet in enumerate(available_pets):
                    col = idx % cols_per_row
                    row = idx // cols_per_row
                    x = start_x + col * (cell_size + padding)
                    y = start_y + row * self.cell_height

                    # 只繪製可見區域內的寵物
                    if y + cell_size < list_y or y > list_y + list_height:
                        self.select_pet_rects.append((pygame.Rect(0, 0, 0, 0), pet))
                        continue

                    pet_rect = pygame.Rect(x, y, cell_size, cell_size)
                    pygame.draw.rect(
                        self.screen, (60, 60, 70), pet_rect, border_radius=6
                    )
                    pygame.draw.rect(
                        self.screen, (100, 100, 140), pet_rect, width=2, border_radius=6
                    )

                    # 寵物頭像
                    head_img = load_pet_head_image(pet.id)
                    if head_img:
                        img_size = cell_size - 10
                        head_img = pygame.transform.smoothscale(
                            head_img, (img_size, img_size)
                        )
                        self.screen.blit(head_img, (x + 5, y + 5))

                    # 寵物名稱和等級
                    name_font = get_font(10)
                    name_text = name_font.render(
                        f"{pet.name} Lv.{pet.level}", True, (255, 255, 255)
                    )
                    name_rect = name_text.get_rect(
                        center=(x + cell_size // 2, y + cell_size - 15)
                    )
                    self.screen.blit(name_text, name_rect)

                    self.select_pet_rects.append((pet_rect, pet))

                # 繪製滾動條（如果需要）
                if max_scroll > 0:
                    scrollbar_width = 10
                    scrollbar_x = panel_x + panel_width - scrollbar_width - 5
                    scrollbar_height = list_height - 20
                    scrollbar_y = list_y + 10

                    # 滾動條背景
                    pygame.draw.rect(
                        self.screen,
                        (60, 60, 70),
                        (scrollbar_x, scrollbar_y, scrollbar_width, scrollbar_height),
                        border_radius=5,
                    )

                    # 滾動條滑塊
                    thumb_height = max(
                        20, scrollbar_height * (list_height / total_content_height)
                    )
                    thumb_y = scrollbar_y + (self.scroll_offset / max_scroll) * (
                        scrollbar_height - thumb_height
                    )
                    pygame.draw.rect(
                        self.screen,
                        (120, 120, 160),
                        (scrollbar_x, thumb_y, scrollbar_width, thumb_height),
                        border_radius=5,
                    )

    def calculate_total_exp(self):
        from data.pets import get_fusion_exp

        total = 0
        for pet in self.fusion_materials:
            if pet is None:
                continue
            total += get_fusion_exp(pet)
        return total

    def handle_fusion_click(self, pos):
        # 檢查返回按鈕
        if hasattr(self, "fusion_back_btn") and self.fusion_back_btn.collidepoint(pos):
            self.show_fusion_panel = False
            self.fusion_materials = []
            self.fusion_selection_mode = False
            self.scroll_offset = 0
            self.last_drag_y = None
            return "fusion_back"

        # 檢查選擇按鈕 - 打開選擇模式，讓玩家從列表中選擇多隻寵物
        if hasattr(self, "fusion_select_btn") and self.fusion_select_btn.collidepoint(
            pos
        ):
            valid_mats = [m for m in self.fusion_materials if m is not None]
            if len(valid_mats) < 5:
                self.fusion_selection_mode = True
                return "open_selection"

        # 檢查確定合成按鈕
        if hasattr(self, "fusion_confirm_btn") and self.fusion_confirm_btn.collidepoint(
            pos
        ):
            valid_mats = [m for m in self.fusion_materials if m is not None]
            if len(valid_mats) > 0:
                total_exp = self.calculate_total_exp()
                self.pet.add_exp(total_exp)

                if self.inventory:
                    for material in valid_mats:
                        if material in self.inventory.pets:
                            self.inventory.pets.remove(material)

                self.fusion_materials = []
                self.show_fusion_panel = False
                self.scroll_offset = 0
                self.last_drag_y = None
                return "fusion_complete"

        # 檢查素材位置點擊
        if hasattr(self, "material_rects"):
            for i, slot_rect in enumerate(self.material_rects):
                if slot_rect.collidepoint(pos):
                    if i >= len(self.fusion_materials):
                        self.show_skill_popup = False
                        self.fusion_selection_mode = True
                        self.fusion_selecting_index = i
                        return f"select_material_{i}"

        # 檢查選擇列表中的寵物點擊
        if self.fusion_selection_mode and hasattr(self, "select_pet_rects"):
            for pet_rect, pet in self.select_pet_rects:
                if pet_rect.collidepoint(pos):
                    valid_mats = [m for m in self.fusion_materials if m is not None]
                    if len(valid_mats) < 5:
                        self.fusion_materials.append(pet)

                        valid_mats = [m for m in self.fusion_materials if m is not None]
                        if len(valid_mats) >= 5:
                            self.fusion_selection_mode = False
                            self.fusion_selecting_index = -1
                            self.scroll_offset = 0
                            self.last_drag_y = None

                    return f"material_selected_{pet.id}"

        return None

    def handle_scroll(self, event, mouse_pos):
        if not hasattr(self, "selection_list_rect"):
            return

        if not self.fusion_selection_mode:
            return

        mouse_x, mouse_y = mouse_pos
        if not self.selection_list_rect.collidepoint((mouse_x, mouse_y)):
            return

        if hasattr(event, "y"):
            scroll_amount = event.y * self.scroll_speed
        elif hasattr(event, "precise_y"):
            scroll_amount = -event.precise_y * self.scroll_speed
        else:
            return

        if not self.inventory:
            return

        valid_materials = [m for m in self.fusion_materials if m is not None]
        available_pets = []
        for pet in self.inventory.pets:
            if pet.id == self.pet.id:
                continue
            if pet in valid_materials:
                continue
            available_pets.append(pet)

        if not available_pets:
            return

        cols_per_row = 10
        total_rows = (len(available_pets) + cols_per_row - 1) // cols_per_row
        total_content_height = total_rows * self.cell_height + 40
        list_height = self.selection_list_rect.height
        max_scroll = max(0, total_content_height - list_height)

        self.scroll_offset = max(0, min(self.scroll_offset - scroll_amount, max_scroll))

    def handle_drag(self, pos):
        if not self.fusion_selection_mode:
            return

        if not hasattr(self, "selection_list_rect"):
            return

        if not self.selection_list_rect.collidepoint(pos):
            return

        if hasattr(self, "last_drag_y") and self.last_drag_y is not None:
            delta_y = self.last_drag_y - pos[1]

            if self.inventory:
                valid_materials = [m for m in self.fusion_materials if m is not None]
                available_pets = []
                for pet in self.inventory.pets:
                    if pet.id != self.pet.id and pet not in valid_materials:
                        available_pets.append(pet)

                if available_pets:
                    cols_per_row = 10
                    total_rows = (
                        len(available_pets) + cols_per_row - 1
                    ) // cols_per_row
                    total_content_height = total_rows * self.cell_height + 40
                    list_height = self.selection_list_rect.height
                    max_scroll = max(0, total_content_height - list_height)
                    self.scroll_offset = max(
                        0, min(self.scroll_offset + delta_y, max_scroll)
                    )

        self.last_drag_y = pos[1]

        self.last_drag_y = pos[1]
