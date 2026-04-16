import pygame
import json
import os
import sys

try:
    import pyperclip
except ImportError:
    pyperclip = None
from config import SCREEN_WIDTH, SCREEN_HEIGHT, BG_COLOR
from ui.fonts import get_font


def log(msg):
    print(msg, flush=True)


class SkillEditorModal:
    def __init__(self, screen, skill_data, skill_type):
        self.screen = screen
        self.skill_data = skill_data if skill_data else {}
        self.skill_type = skill_type
        self.running = True
        self.closed_result = None

        # Normalize single-effect leader skills into a composite wrapper so UI can edit uniformly
        self._unwrap_single_effect = False
        self._unwrap_single_effect_active = False
        if self.skill_type == "leader_skill" and isinstance(self.skill_data, dict):
            if "effects" not in self.skill_data:
                # Treat as a single effect dict and wrap it
                self._unwrap_single_effect = True
                self.skill_data = {"type": "composite", "effects": [self.skill_data]}
        elif self.skill_type == "active_skill" and isinstance(self.skill_data, dict):
            if "effects" not in self.skill_data:
                self._unwrap_single_effect_active = True
                self.skill_data = {"type": "composite", "effects": [self.skill_data]}
        self.running = True
        self.result = None

        self.effect_types = self.get_effect_types()
        self.selected_effect_index = 0
        self.editing_effect_field = None
        self.edit_text = ""
        self.dropdown_open = None  # (effect_index, dropdown_open)

        if self.skill_type == "leader_skill":
            self.skill_type_key = "type"
            self.effects_key = "effects"
        else:
            self.skill_type_key = "type"
            self.effects_key = "effects"

        if "type" not in self.skill_data:
            self.skill_data["type"] = "composite"
        if "effects" not in self.skill_data:
            self.skill_data["effects"] = []

        self.scroll_offset = 0
        self.display_name_input_active = False
        self.display_name_text = self.skill_data.get(
            "display_name", self.skill_data.get("name", "")
        )

    def get_effect_types(self):
        if self.skill_type == "leader_skill":
            return [
                (
                    "attribute",
                    [
                        "attributes",
                        "hp_mult",
                        "attack_mult",
                        "recovery_mult",
                        "min_attributes",
                    ],
                ),
                ("type", ["types", "hp_mult", "attack_mult", "recovery_mult"]),
                ("combo", ["min_combos", "attack_mult"]),
                (
                    "hp_threshold",
                    ["hp_threshold", "attack_mult_above", "attack_mult_below"],
                ),
                ("damage_reduction", ["reduction"]),
                ("auto_heal", ["heal_amount"]),
                ("extra_damage", ["damage_mult", "min_matches"]),
                ("counter_attack", ["chance", "attack_mult"]),
                ("resurrection", ["chance", "hp_percent"]),
                ("time_extension", ["extension"]),
                (
                    "multi_attribute",
                    ["min_attributes", "attack_mult", "damage_reduction"],
                ),
                ("specific_combo", ["attributes", "min_count", "attack_mult"]),
                ("attribute_count", ["attribute", "min_count", "attack_mult"]),
            ]
        elif self.skill_type == "active_skill":
            return [
                ("single_attack", ["attack_mult", "fixed_damage"]),
                ("attribute_attack", ["attribute", "attack_mult", "fixed_damage"]),
                ("all_attack", ["attack_mult", "fixed_damage"]),
                ("attribute_all_attack", ["attribute", "attack_mult", "fixed_damage"]),
                ("fixed_damage", ["damage"]),
                ("gravity", ["percentage"]),
                ("poison", ["damage"]),
                ("delay", ["delay_turns"]),
                ("genesis_dragon", ["delay_turns", "count", "cooldown", "name"]),
                ("defense_break", ["defense_reduction", "turns"]),
                ("drain_hp", ["damage_mult", "heal_percent"]),
                ("heal", ["heal_amount"]),
                ("remove_debuff", ["remove_awakening_nullify"]),
                ("damage_reduction", ["reduction", "turns"]),
                ("atk_boost", ["attack_mult", "turns", "target_all"]),
                ("rcv_boost", ["recovery_mult", "turns"]),
                ("def_boost", ["defense_mult", "turns"]),
                ("transform_board", ["transform_type"]),
                ("enhance_orbs", ["attribute", "enhance_count"]),
                ("haste", ["turns"]),
                ("time_extend", ["extension"]),
                ("shield", ["hp_percent", "turns"]),
            ]
        return []

    def run(self):
        while self.running:
            for event in pygame.event.get():
                log(
                    f"SkillEditor: event.type={event.type}, key={event.key if hasattr(event, 'key') else 'N/A'}"
                )
                if event.type == pygame.QUIT:
                    self.running = False
                    return None
                elif event.type == pygame.KEYDOWN:
                    log(
                        f"SkillEditor: keydown key={event.key}, editing_effect_field={repr(self.editing_effect_field)}"
                    )
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                        return None
                    elif event.key == pygame.K_RETURN:
                        if self.editing_effect_field:
                            self.apply_effect_field_edit()
                    if self.editing_effect_field:
                        log(f"SkillEditor: handling key={event.key}")
                        if event.key == pygame.K_BACKSPACE:
                            self.edit_text = self.edit_text[:-1]
                        elif event.key == pygame.K_DELETE:
                            self.edit_text = ""
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos)
                elif event.type == pygame.TEXTINPUT and self.editing_effect_field:
                    self.edit_text += event.text
                elif self.display_name_input_active and event.type == pygame.TEXTINPUT:
                    self.display_name_text += event.text
                elif self.display_name_input_active and event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        self.display_name_text = self.display_name_text[:-1]
                    elif event.key == pygame.K_DELETE:
                        self.display_name_text = ""
                    elif event.key == pygame.K_RETURN:
                        self.skill_data["display_name"] = self.display_name_text
                        self.display_name_input_active = False
                    elif event.key == pygame.K_ESCAPE:
                        self.display_name_input_active = False
                        self.display_name_text = self.skill_data.get(
                            "display_name", self.skill_data.get("name", "")
                        )

            self.draw()
            pygame.display.flip()

        # If we saved, prefer the possibly unwrapped result; otherwise return current skill_data
        if self.closed_result is not None:
            return self.closed_result
        return self.skill_data

    def handle_click(self, pos):
        if (
            pos[0] < 100
            or pos[0] > SCREEN_WIDTH - 100
            or pos[1] < 50
            or pos[1] > SCREEN_HEIGHT - 50
        ):
            self.running = False
            return

        y = pos[1]

        if pygame.Rect(SCREEN_WIDTH - 200, 60, 80, 30).collidepoint(pos):
            # Commit display name if editing
            if self.display_name_input_active:
                self.skill_data["display_name"] = self.display_name_text
                self.display_name_input_active = False
            # Use unified save path which handles unwrap for single-effect leader skills
            self.save_and_close()
            return

        if pygame.Rect(SCREEN_WIDTH - 200, 100, 80, 30).collidepoint(pos):
            self.running = False
            return

        # Activate display name editing when clicking the field area
        display_name_area = pygame.Rect(150, 60, 420, 28)
        if display_name_area.collidepoint(pos):
            self.display_name_input_active = True
            return

        add_btn_y = 150 + len(self.skill_data.get("effects", [])) * 180
        if pygame.Rect(SCREEN_WIDTH // 2 - 50, add_btn_y, 100, 35).collidepoint(pos):
            self.add_new_effect()
            return

        effects = self.skill_data.get("effects", [])
        for i, effect in enumerate(effects):
            effect_y = 170 + i * 180

            dropdown_rect = pygame.Rect(150, effect_y, 200, 30)
            if dropdown_rect.collidepoint(pos):
                self.selected_effect_index = i
                type_options = [t[0] for t in self.effect_types]
                current_type = effect.get("type", "")
                current_idx = (
                    type_options.index(current_type)
                    if current_type in type_options
                    else 0
                )
                next_idx = (current_idx + 1) % len(type_options)
                effect["type"] = type_options[next_idx]
                return

            effect_type = effect.get("type", "")
            params = self.get_params_for_type(effect_type)

            for j, param in enumerate(params):
                param_y = effect_y + 40 + j * 35
                if pygame.Rect(150, param_y, 250, 30).collidepoint(pos):
                    self.selected_effect_index = i
                    self.editing_effect_field = param
                    self.edit_text = str(effect.get(param, ""))
                    return

            if pygame.Rect(SCREEN_WIDTH - 180, effect_y + 10, 60, 25).collidepoint(pos):
                self.remove_effect(i)
                return

    def get_params_for_type(self, effect_type):
        for t, params in self.effect_types:
            if t == effect_type:
                return params
        return []

    def add_new_effect(self):
        effects = self.skill_data.get("effects", [])
        if self.effect_types:
            new_effect = {"type": self.effect_types[0][0]}
            for param in self.effect_types[0][1]:
                if param in ["attributes", "types"]:
                    new_effect[param] = ["火"]
                elif param == "attribute":
                    new_effect[param] = "火"
                elif param in [
                    "attack_mult",
                    "hp_mult",
                    "recovery_mult",
                    "defense_mult",
                    "recovery",
                    "damage_mult",
                    "reduction",
                    "heal_amount",
                    "damage",
                    "percentage",
                    "extension",
                    "hp_percent",
                    "chance",
                    "defense_reduction",
                ]:
                    new_effect[param] = 1.0
                else:
                    new_effect[param] = 1
            effects.append(new_effect)

    def remove_effect(self, index):
        effects = self.skill_data.get("effects", [])
        if 0 <= index < len(effects):
            effects.pop(index)

    def apply_effect_field_edit(self):
        if self.selected_effect_index >= len(self.skill_data.get("effects", [])):
            return

        effect = self.skill_data["effects"][self.selected_effect_index]

        if self.editing_effect_field in ["attributes", "types"]:
            effect[self.editing_effect_field] = self.edit_text.split(",")
        elif self.editing_effect_field == "attribute":
            effect[self.editing_effect_field] = self.edit_text
        elif self.editing_effect_field in ["target_all"]:
            effect[self.editing_effect_field] = self.edit_text.lower() == "true"
        elif self.editing_effect_field in [
            "attack_mult",
            "hp_mult",
            "recovery_mult",
            "defense_mult",
            "recovery",
            "damage_mult",
            "reduction",
            "heal_amount",
            "damage",
            "percentage",
            "extension",
            "hp_percent",
            "chance",
            "defense_reduction",
            "min_combos",
            "hp_threshold",
            "attack_mult_above",
            "attack_mult_below",
            "delay_turns",
            "turns",
            "enhance_count",
        ]:
            try:
                effect[self.editing_effect_field] = (
                    float(self.edit_text)
                    if "." in self.edit_text
                    else int(self.edit_text)
                )
            except ValueError:
                pass
        else:
            effect[self.editing_effect_field] = self.edit_text

        self.editing_effect_field = None
        self.edit_text = ""

    def save_and_close(self):
        # Unwrap single-effect leader skills
        if (
            self._unwrap_single_effect
            and isinstance(self.skill_data, dict)
            and "effects" in self.skill_data
        ):
            effects = self.skill_data.get("effects", [])
            self.closed_result = effects[0] if effects else None
        # Unwrap single-effect active skills
        elif (
            self._unwrap_single_effect_active
            and isinstance(self.skill_data, dict)
            and "effects" in self.skill_data
        ):
            effects = self.skill_data.get("effects", [])
            self.closed_result = effects[0] if effects else None
        else:
            self.closed_result = self.skill_data

        self.running = False
        return self.closed_result

    def draw(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        modal_rect = pygame.Rect(100, 50, SCREEN_WIDTH - 200, SCREEN_HEIGHT - 100)
        pygame.draw.rect(self.screen, (40, 40, 50), modal_rect, border_radius=10)
        pygame.draw.rect(self.screen, (100, 100, 150), modal_rect, 2, border_radius=10)

        font = get_font(24)
        title = font.render(
            f"{'隊長技能' if self.skill_type == 'leader_skill' else '主動技能'}編輯器",
            True,
            (255, 220, 100),
        )
        self.screen.blit(title, (modal_rect.centerx - title.get_width() // 2, 65))

        # 顯示名稱欄位
        label = get_font(16).render("顯示名稱:", True, (180, 180, 180))
        self.screen.blit(label, (150, 60))
        input_bg = pygame.Rect(230, 58, 320, 28)
        pygame.draw.rect(self.screen, (60, 60, 70), input_bg, border_radius=3)
        text = (
            self.display_name_text
            if not self.display_name_input_active
            else self.display_name_text + "|"
        )
        text_surf = get_font(14).render(text, True, (255, 255, 255))
        self.screen.blit(text_surf, (input_bg.x + 6, input_bg.y + 6))

        save_btn = pygame.Rect(SCREEN_WIDTH - 200, 60, 80, 30)
        pygame.draw.rect(self.screen, (50, 100, 50), save_btn, border_radius=5)
        save_text = get_font(16).render("保存", True, (255, 255, 255))
        self.screen.blit(save_text, (save_btn.centerx - 20, save_btn.centery - 8))

        close_btn = pygame.Rect(SCREEN_WIDTH - 200, 100, 80, 30)
        pygame.draw.rect(self.screen, (100, 50, 50), close_btn, border_radius=5)
        close_text = get_font(16).render("取消", True, (255, 255, 255))
        self.screen.blit(close_text, (close_btn.centerx - 20, close_btn.centery - 8))

        effects = self.skill_data.get("effects", [])
        add_y = 150 + len(effects) * 180
        add_btn = pygame.Rect(SCREEN_WIDTH // 2 - 50, add_y, 100, 35)
        pygame.draw.rect(self.screen, (60, 80, 120), add_btn, border_radius=5)
        add_text = get_font(18).render("+ 新增效果", True, (255, 255, 255))
        self.screen.blit(add_text, (add_btn.centerx - 45, add_btn.centery - 9))

        for i, effect in enumerate(effects):
            effect_y = 170 + i * 180

            pygame.draw.rect(
                self.screen,
                (50, 50, 60),
                (130, effect_y, SCREEN_WIDTH - 340, 160),
                border_radius=5,
            )

            effect_type = effect.get("type", "")

            label = get_font(16).render("類型:", True, (180, 180, 180))
            self.screen.blit(label, (140, effect_y + 5))

            dropdown_rect = pygame.Rect(190, effect_y, 200, 30)
            pygame.draw.rect(self.screen, (60, 60, 70), dropdown_rect, border_radius=3)

            type_options = [t[0] for t in self.effect_types]
            current_idx = (
                type_options.index(effect_type) if effect_type in type_options else 0
            )
            type_text = get_font(16).render(effect_type, True, (255, 255, 255))
            self.screen.blit(type_text, (dropdown_rect.x + 10, dropdown_rect.y + 5))

            hint_text = get_font(12).render("點擊切換", True, (100, 150, 100))
            self.screen.blit(hint_text, (dropdown_rect.right + 10, dropdown_rect.y + 8))

            params = self.get_params_for_type(effect_type)
            for j, param in enumerate(params):
                param_y = effect_y + 40 + j * 35

                param_label = get_font(14).render(f"{param}:", True, (160, 160, 160))
                self.screen.blit(param_label, (140, param_y + 3))

                value_rect = pygame.Rect(200, param_y, 180, 28)
                pygame.draw.rect(self.screen, (50, 50, 60), value_rect, border_radius=3)

                if (
                    self.selected_effect_index == i
                    and self.editing_effect_field == param
                ):
                    display = self.edit_text + "▌"
                else:
                    display = str(effect.get(param, ""))

                value_text = get_font(14).render(display, True, (255, 255, 255))
                self.screen.blit(value_text, (value_rect.x + 5, value_rect.y + 5))

            del_btn = pygame.Rect(SCREEN_WIDTH - 180, effect_y + 10, 60, 25)
            pygame.draw.rect(self.screen, (120, 50, 50), del_btn, border_radius=3)
            del_text = get_font(12).render("刪除", True, (255, 255, 255))
            self.screen.blit(del_text, (del_btn.centerx - 15, del_btn.centery - 6))

        hint = get_font(14).render("點擊參數可直接編輯", True, (120, 120, 120))
        self.screen.blit(hint, (140, SCREEN_HEIGHT - 70))


class AwakeningEditorModal:
    def __init__(self, screen, awakenings):
        self.screen = screen
        self.awakenings = awakenings if awakenings else []
        # Normalize to list to support single-string awakening representations
        if not isinstance(self.awakenings, list):
            self.awakenings = [self.awakenings]
        self.running = True
        self.result = None

        self.available_awakenings = [
            "單體攻擊+",
            "全體攻擊+",
            "單體回復+",
            "全體回復+",
            "火屬性+",
            "水屬性+",
            "木屬性+",
            "光屬性+",
            "暗屬性+",
            "綁敵無效",
            "操作時間+",
            "操作時間++",
            "自我康復",
            "防禦+",
            "攻擊+",
            "回復+",
            " HP+",
            "傷害無效貫穿",
            " combo",
            "毒_drop",
            "猛毒",
            "火_drop",
            "水_drop",
            "木_drop",
            "光_drop",
            "暗_drop",
            "心_drop",
            "drop+",
            "L型消除",
            "寶珠強化",
            "屬性強化",
            "超覺醒",
        ]

        self.selected_index = 0
        self.editing_name = False
        self.edit_text = ""

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return None
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                        return None
                    elif event.key == pygame.K_RETURN:
                        if self.editing_name:
                            self.apply_new_awakening()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos)
                elif event.type == pygame.TEXTINPUT and self.editing_name:
                    self.edit_text += event.text
                elif event.type == pygame.KEYDOWN and self.editing_name:
                    if event.key == pygame.K_BACKSPACE:
                        self.edit_text = self.edit_text[:-1]
                    elif event.key == pygame.K_DELETE:
                        self.edit_text = ""

            self.draw()
            pygame.display.flip()

        return self.result

    def handle_click(self, pos):
        if (
            pos[0] < 100
            or pos[0] > SCREEN_WIDTH - 100
            or pos[1] < 50
            or pos[1] > SCREEN_HEIGHT - 50
        ):
            self.running = False
            return

        if pygame.Rect(SCREEN_WIDTH - 200, 60, 80, 30).collidepoint(pos):
            self.result = self.awakenings
            self.running = False
            return

        close_btn = pygame.Rect(SCREEN_WIDTH - 200, 100, 80, 30)
        if close_btn.collidepoint(pos):
            self.running = False
            return

        y = 160
        for i in range(len(self.awakenings)):
            rect = pygame.Rect(150, y + i * 40, 300, 35)
            if rect.collidepoint(pos):
                self.selected_index = i
                return

        add_y = 160 + len(self.awakenings) * 40
        if pygame.Rect(150, add_y, 300, 35).collidepoint(pos):
            self.editing_name = True
            self.edit_text = ""
            return

        for i, aw in enumerate(self.available_awakenings):
            btn_y = 160 + len(self.awakenings) * 40 + 50 + i * 35
            if pygame.Rect(150, btn_y, 150, 30).collidepoint(pos):
                if len(self.awakenings) < 10:
                    self.awakenings.append(aw)
                return

    def apply_new_awakening(self):
        if self.edit_text.strip():
            self.awakenings.append(self.edit_text.strip())
        self.editing_name = False
        self.edit_text = ""

    def draw(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        modal_rect = pygame.Rect(100, 50, SCREEN_WIDTH - 200, SCREEN_HEIGHT - 100)
        pygame.draw.rect(self.screen, (40, 40, 50), modal_rect, border_radius=10)
        pygame.draw.rect(self.screen, (100, 100, 150), modal_rect, 2, border_radius=10)

        font = get_font(24)
        title = font.render("覺醒技能編輯器", True, (255, 220, 100))
        self.screen.blit(title, (modal_rect.centerx - title.get_width() // 2, 65))

        close_btn = pygame.Rect(SCREEN_WIDTH - 200, 60, 80, 30)
        pygame.draw.rect(self.screen, (50, 100, 50), close_btn, border_radius=5)
        close_text = get_font(16).render("關閉", True, (255, 255, 255))
        self.screen.blit(close_text, (close_btn.centerx - 20, close_btn.centery - 8))

        label = get_font(18).render("已選擇覺醒:", True, (200, 200, 200))
        self.screen.blit(label, (150, 120))

        y = 160
        for i, aw in enumerate(self.awakenings):
            rect = pygame.Rect(150, y + i * 40, 300, 35)
            pygame.draw.rect(self.screen, (60, 60, 70), rect, border_radius=3)

            aw_text = get_font(16).render(aw, True, (255, 255, 255))
            self.screen.blit(aw_text, (rect.x + 10, rect.y + 8))

            del_btn = pygame.Rect(460, y + i * 40, 50, 30)
            pygame.draw.rect(self.screen, (120, 50, 50), del_btn, border_radius=3)
            del_text = get_font(14).render("X", True, (255, 255, 255))
            self.screen.blit(del_text, (del_btn.centerx - 5, del_btn.centery - 7))

            if (
                rect.collidepoint(pygame.mouse.get_pos())
                and pygame.mouse.get_pressed()[0]
            ):
                self.awakenings.pop(i)
                return

        add_rect = pygame.Rect(150, y + len(self.awakenings) * 40, 300, 35)
        pygame.draw.rect(self.screen, (50, 80, 50), add_rect, border_radius=3)
        if self.editing_name:
            display = self.edit_text + "▌"
        else:
            display = "+ 自訂覺醒"
        add_text = get_font(16).render(display, True, (200, 200, 200))
        self.screen.blit(add_text, (add_rect.x + 10, add_rect.y + 8))

        if len(self.awakenings) < 10:
            preset_label = get_font(18).render("可用覺醒:", True, (200, 200, 200))
            self.screen.blit(preset_label, (150, y + len(self.awakenings) * 40 + 50))

            for i, aw in enumerate(self.available_awakenings):
                btn_y = y + len(self.awakenings) * 40 + 80 + i * 35
                if btn_y > SCREEN_HEIGHT - 100:
                    break
                btn = pygame.Rect(150, btn_y, 150, 30)
                pygame.draw.rect(self.screen, (70, 70, 90), btn, border_radius=3)
                btn_text = get_font(14).render(aw, True, (255, 255, 255))
                self.screen.blit(btn_text, (btn.x + 5, btn.y + 6))


class ImageCropModal:
    def __init__(self, screen, image_path, pet_id, img_type):
        self.screen = screen
        self.image_path = image_path
        self.pet_id = pet_id
        self.img_type = img_type
        self.running = True
        self.result = None

        self.original_image = pygame.image.load(image_path).convert_alpha()

        self.zoom = 1.0
        self.min_zoom = 0.1
        self.max_zoom = 5.0

        self.offset_x = 0
        self.offset_y = 0
        self.dragging = False
        self.last_mouse_pos = None

        self.canvas_size = 300
        self.canvas_x = (SCREEN_WIDTH - self.canvas_size) // 2
        self.canvas_y = 150

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return None
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                        return None
                    elif event.key == pygame.K_RETURN:
                        self.save_and_close()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        mx, my = event.pos
                        if (
                            self.canvas_x <= mx <= self.canvas_x + self.canvas_size
                            and self.canvas_y <= my <= self.canvas_y + self.canvas_size
                        ):
                            self.dragging = True
                            self.last_mouse_pos = (mx, my)

                        save_btn = pygame.Rect(SCREEN_WIDTH - 180, 60, 80, 30)
                        if save_btn.collidepoint(mx, my):
                            self.save_and_close()
                            continue

                        close_btn = pygame.Rect(SCREEN_WIDTH - 180, 100, 80, 30)
                        if close_btn.collidepoint(mx, my):
                            self.running = False
                            continue
                    elif event.button == 4:
                        self.zoom = min(self.max_zoom, self.zoom * 1.1)
                    elif event.button == 5:
                        self.zoom = max(self.min_zoom, self.zoom / 1.1)
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.dragging = False
                        self.last_mouse_pos = None
                elif event.type == pygame.MOUSEMOTION:
                    if self.dragging and self.last_mouse_pos:
                        mx, my = event.pos
                        dx = mx - self.last_mouse_pos[0]
                        dy = my - self.last_mouse_pos[1]
                        self.offset_x += dx / self.zoom
                        self.offset_y += dy / self.zoom
                        self.last_mouse_pos = (mx, my)

            self.draw()
            pygame.display.flip()

        return self.result

    def save_and_close(self):
        base_path = os.path.dirname(os.path.abspath(__file__))
        if self.img_type == "head":
            save_dir = os.path.join(base_path, "assets", "images", "head")
        else:
            save_dir = os.path.join(base_path, "assets", "images", "full")
        os.makedirs(save_dir, exist_ok=True)

        target_path = os.path.join(save_dir, f"{self.pet_id}.png")

        cropped = self.get_cropped_image()
        pygame.image.save(cropped, target_path)

        self.result = target_path
        self.running = False
        print(f"已保存裁剪後的圖片: {target_path}")

    def get_cropped_image(self):
        img = self.original_image
        orig_w, orig_h = img.get_size()

        base_size = max(orig_w, orig_h)
        scaled_w = int(orig_w * self.zoom)
        scaled_h = int(orig_h * self.zoom)
        scaled = pygame.transform.scale(img, (scaled_w, scaled_h))

        canvas = pygame.Surface((self.canvas_size, self.canvas_size), pygame.SRCALPHA)
        canvas.fill((40, 40, 50))

        offset_x = (self.canvas_size - scaled_w) // 2 + int(self.offset_x * self.zoom)
        offset_y = (self.canvas_size - scaled_h) // 2 + int(self.offset_y * self.zoom)

        canvas.blit(scaled, (offset_x, offset_y))

        return pygame.transform.scale(canvas, (128, 128))

    def draw(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        modal_rect = pygame.Rect(100, 50, SCREEN_WIDTH - 200, SCREEN_HEIGHT - 100)
        pygame.draw.rect(self.screen, (30, 30, 40), modal_rect, border_radius=10)
        pygame.draw.rect(self.screen, (100, 100, 150), modal_rect, 2, border_radius=10)

        font = get_font(24)
        title = font.render(f"頭像裁剪 - {self.img_type}", True, (255, 220, 100))
        self.screen.blit(title, (modal_rect.centerx - title.get_width() // 2, 65))

        pygame.draw.rect(
            self.screen,
            (60, 60, 70),
            (self.canvas_x, self.canvas_y, self.canvas_size, self.canvas_size),
            border_radius=5,
        )
        pygame.draw.rect(
            self.screen,
            (100, 100, 150),
            (self.canvas_x, self.canvas_y, self.canvas_size, self.canvas_size),
            2,
            border_radius=5,
        )

        img = self.original_image
        orig_w, orig_h = img.get_size()

        scaled_w = int(orig_w * self.zoom)
        scaled_h = int(orig_h * self.zoom)
        scaled = pygame.transform.scale(img, (scaled_w, scaled_h))

        offset_x = (self.canvas_size - scaled_w) // 2 + int(self.offset_x * self.zoom)
        offset_y = (self.canvas_size - scaled_h) // 2 + int(self.offset_y * self.zoom)

        self.screen.blit(scaled, (self.canvas_x + offset_x, self.canvas_y + offset_y))

        pygame.draw.rect(
            self.screen,
            (80, 80, 100),
            (self.canvas_x, self.canvas_y, self.canvas_size, self.canvas_size),
            3,
        )

        preview_x = SCREEN_WIDTH - 200
        preview_y = 250
        pygame.draw.rect(
            self.screen, (50, 50, 60), (preview_x, preview_y, 128, 128), border_radius=5
        )
        pygame.draw.rect(
            self.screen,
            (100, 100, 150),
            (preview_x, preview_y, 128, 128),
            2,
            border_radius=5,
        )

        preview = self.get_cropped_image()
        self.screen.blit(preview, (preview_x, preview_y))

        small_font = get_font(14)
        preview_label = small_font.render("預覽 (128x128)", True, (180, 180, 180))
        self.screen.blit(preview_label, (preview_x, preview_y + 135))

        controls = [
            "拖曳: 移動圖片",
            "滾輪: 放大/縮小",
            "Enter: 確認",
            "ESC: 取消",
        ]
        for i, text in enumerate(controls):
            ctrl = small_font.render(text, True, (150, 150, 150))
            self.screen.blit(ctrl, (150, 400 + i * 25))

        save_btn = pygame.Rect(SCREEN_WIDTH - 180, 60, 80, 30)
        pygame.draw.rect(self.screen, (50, 100, 50), save_btn, border_radius=5)
        save_text = get_font(16).render("確認", True, (255, 255, 255))
        self.screen.blit(save_text, (save_btn.centerx - 20, save_btn.centery - 8))

        close_btn = pygame.Rect(SCREEN_WIDTH - 180, 100, 80, 30)
        pygame.draw.rect(self.screen, (100, 50, 50), close_btn, border_radius=5)
        close_text = get_font(16).render("取消", True, (255, 255, 255))
        self.screen.blit(close_text, (close_btn.centerx - 20, close_btn.centery - 8))


class StageEditorModal:
    def __init__(self, screen, stage_data):
        self.screen = screen
        self.stage_data = (
            stage_data
            if stage_data
            else {
                "name": "新關卡",
                "dialogue": [],
                "floors": [{"floor_num": 1, "dialogue": [], "enemies": []}],
                "stage_type": 1,
                "exp": 0,
                "rewards": [],
            }
        )
        if "stage_type" not in self.stage_data:
            self.stage_data["stage_type"] = 1
        if "exp" not in self.stage_data:
            self.stage_data["exp"] = 0
        if "rewards" not in self.stage_data:
            self.stage_data["rewards"] = []

        self.running = True
        self.result = None
        self.selected_floor_index = 0
        self.selected_enemy_index = 0
        self.editing_field = None
        self.edit_text = ""
        self.add_dialogue_mode = False
        self.dialogue_list = []
        self.selected_dialogue_index = 0

        # 初始化敵人圖片列表
        self._enemy_images = []
        self._enemy_image_scroll = 0

        self.load_dialogues()
        self.load_pets_data()

        self.stage_type_options = [
            (1, "主線劇情"),
            (2, "降臨關卡"),
            (3, "活動關卡"),
        ]

        self.enemy_action_types = [
            "attack",
            "blue_shield",
            "absorb_shield",
            "nullify_shield",
        ]

        self.action_type_selecting = None
        self.dialogue_picker_open = None

        self.trigger_types = [
            ("manual", "手動"),
            ("on_enter_floor", "進入樓層"),
            ("on_enemy_action", "敵人行動"),
            ("on_enemy_death", "敵人死亡"),
        ]
        self.trigger_picker_open = False
        self.selected_dialogue_for_trigger = None
        self.reward_picker_open = False

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return None
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                        return None
                    elif event.key == pygame.K_RETURN:
                        if self.editing_field:
                            self.apply_edit()
                    elif event.key == pygame.K_BACKSPACE:
                        if self.editing_field:
                            self.edit_text = self.edit_text[:-1]
                    elif event.key == pygame.K_TAB:
                        if self.editing_field:
                            self.apply_edit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 4:
                        if enemies and self.selected_enemy_index < len(enemies):
                            self._enemy_image_scroll = max(
                                0, getattr(self, "_enemy_image_scroll", 0) - 1
                            )
                    elif event.button == 5:
                        if enemies and self.selected_enemy_index < len(enemies):
                            max_scroll = max(
                                0, len(self._enemy_images) - max(1, 100 // 80)
                            )
                            self._enemy_image_scroll = min(
                                max_scroll, getattr(self, "_enemy_image_scroll", 0) + 1
                            )
                    elif (
                        hasattr(self, "_selecting_enemy_image")
                        and self._selecting_enemy_image
                    ):
                        if not self.handle_enemy_image_selector_click(event.pos):
                            self.handle_click(event.pos)
                    else:
                        self.handle_click(event.pos)
                elif event.type == pygame.TEXTINPUT:
                    if self.editing_field:
                        self.edit_text += event.text
                elif event.type == pygame.DROPFILE:
                    self.handle_file_drop(event.file)

            self.draw()
            self.draw_enemy_image_selector()
            pygame.display.flip()

        return self.stage_data

    def load_dialogues(self):
        import json
        import os

        base_path = os.path.dirname(os.path.abspath(__file__))
        dialogues_path = os.path.join(base_path, "data", "dialogues.json")
        if os.path.exists(dialogues_path):
            with open(dialogues_path, "r", encoding="utf-8") as f:
                self.dialogues_data = json.load(f)
        else:
            self.dialogues_data = {"dialogues": {}}

    def get_dialogue_list(self):
        return self.dialogues_data.get("dialogues", {})

    def load_pets_data(self):
        import json
        import os

        base_path = os.path.dirname(os.path.abspath(__file__))
        pets_path = os.path.join(base_path, "data", "pets.json")
        if os.path.exists(pets_path):
            with open(pets_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.pets_data = data.get("pets", [])
        else:
            self.pets_data = []

    def get_action_type_name(self, action_type):
        names = {
            "attack": "攻擊",
            "blue_shield": "藍盾",
            "absorb_shield": "吸收盾",
            "nullify_shield": "無效盾",
        }
        return names.get(action_type, action_type)

    def get_trigger_type_name(self, trigger_type):
        for t, name in self.trigger_types:
            if t == trigger_type:
                return name
        return trigger_type

    def handle_click(self, pos):
        # Save button
        if pygame.Rect(SCREEN_WIDTH - 180, 60, 80, 30).collidepoint(pos):
            self.result = self.stage_data
            self.running = False
            return

        # Close button
        if pygame.Rect(SCREEN_WIDTH - 180, 100, 80, 30).collidepoint(pos):
            self.running = False
            return

        # Stage name editing
        if pygame.Rect(180, 70, 250, 30).collidepoint(pos):
            self.editing_field = "stage_name"
            self.edit_text = self.stage_data.get("name", "")
            return

        # Stage type toggle
        if pygame.Rect(500, 70, 120, 30).collidepoint(pos):
            current_type = self.stage_data.get("stage_type", 1)
            for i, (t, name) in enumerate(self.stage_type_options):
                if t == current_type:
                    next_idx = (i + 1) % len(self.stage_type_options)
                    self.stage_data["stage_type"] = self.stage_type_options[next_idx][0]
                    break
            return

        # Exp editing
        if pygame.Rect(720, 70, 80, 30).collidepoint(pos):
            self.editing_field = "stage_exp"
            self.edit_text = str(self.stage_data.get("exp", 0))
            return

        # Rewards button
        if pygame.Rect(860, 70, 80, 30).collidepoint(pos):
            self.reward_picker_open = True
            return

        # Close modal when clicking outside
        if (
            pos[0] < 50
            or pos[0] > SCREEN_WIDTH - 50
            or pos[1] < 50
            or pos[1] > SCREEN_HEIGHT - 50
        ):
            self.running = False
            return

        # Check reward delete buttons
        rewards = self.stage_data.get("rewards", [])
        reward_y = 110
        for reward_idx, reward in enumerate(rewards):
            del_reward_btn = pygame.Rect(890, reward_y, 18, 18)
            if del_reward_btn.collidepoint(pos):
                rewards.pop(reward_idx)
                self.stage_data["rewards"] = rewards
                return
            reward_y += 25

        # If reward picker is open, handle input-based picker
        if self.reward_picker_open:
            print(f"DEBUG: reward picker is open, pos = {pos}")
            picker_w = 200
            picker_h = 300
            picker_x = (SCREEN_WIDTH - picker_w) // 2
            picker_y = (SCREEN_HEIGHT - picker_h) // 2

            confirm_btn = pygame.Rect(picker_x + 30, picker_y + 80, picker_w - 60, 30)
            print(
                f"DEBUG: confirm_btn = {confirm_btn}, collides = {confirm_btn.collidepoint(pos)}"
            )
            if confirm_btn.collidepoint(pos) and self.edit_text:
                print(f"DEBUG: Clicked confirm button, adding reward")
                try:
                    pet_id = int(self.edit_text)
                    rewards = self.stage_data.get("rewards", [])
                    rewards.append({"pet_id": pet_id, "count": 1})
                    self.stage_data["rewards"] = rewards
                    self.reward_picker_open = False
                    self.editing_field = None
                    self.edit_text = ""
                except ValueError:
                    pass
                return

            input_rect = pygame.Rect(picker_x + 20, picker_y + 40, picker_w - 40, 30)
            print(
                f"DEBUG: input_rect = {input_rect}, collides = {input_rect.collidepoint(pos)}"
            )
            if input_rect.collidepoint(pos):
                print(
                    f"DEBUG: Clicked input box, setting editing_field = reward_id_input"
                )
                self.editing_field = "reward_id_input"
                self.edit_text = ""
                return

            modal_rect = pygame.Rect(picker_x, picker_y, picker_w, picker_h)
            if not modal_rect.collidepoint(pos):
                self.reward_picker_open = False
                self.editing_field = None
                self.edit_text = ""
                return
            return

        # Add dialogue button (stage level)
        if pygame.Rect(650, 105, 120, 28).collidepoint(pos):
            self.dialogue_picker_open = ("stage", None)
            return

        # Check stage dialogue delete buttons
        stage_dialogue = self.stage_data.get("dialogue", [])
        dlg_y = 135
        for dlg_idx, dlg_ref in enumerate(stage_dialogue):
            del_dlg_btn = pygame.Rect(770, dlg_y + 2, 18, 18)
            if del_dlg_btn.collidepoint(pos):
                stage_dialogue.pop(dlg_idx)
                self.stage_data["dialogue"] = stage_dialogue
                return
            dlg_y += 42

        # Floor selection and add floor button
        floors = self.stage_data.get("floors", [])
        for i, floor in enumerate(floors):
            floor_y = 180 + i * 60

            del_floor_btn = pygame.Rect(500, floor_y + 10, 35, 30)
            if del_floor_btn.collidepoint(pos):
                if len(floors) > 1:
                    floors.pop(i)
                    if self.selected_floor_index >= len(floors):
                        self.selected_floor_index = len(floors) - 1
                return

            if pygame.Rect(50, floor_y, 460, 50).collidepoint(pos):
                self.selected_floor_index = i
                return

        add_floor_btn = pygame.Rect(50, 180 + len(floors) * 60, 150, 35)
        if add_floor_btn.collidepoint(pos):
            new_floor = {"floor_num": len(floors) + 1, "dialogue": [], "enemies": []}
            floors.append(new_floor)
            self.selected_floor_index = len(floors) - 1
            return

        # Right panel - floor dialogue, enemy, actions
        if floors and self.selected_floor_index < len(floors):
            floor = floors[self.selected_floor_index]
            right_panel_x = 570

            # Add floor dialogue
            if pygame.Rect(right_panel_x, 140, 80, 30).collidepoint(pos):
                self.dialogue_picker_open = ("floor", self.selected_floor_index)
                return

            # Add enemy
            if pygame.Rect(right_panel_x, 180, 80, 30).collidepoint(pos):
                enemies = floor.get("enemies", [])
                new_enemy = {
                    "name": f"敵人 {len(enemies) + 1}",
                    "hp": 1000,
                    "attack": 100,
                    "defense": 0,
                    "attribute": "火",
                    "scale": 1.0,
                    "actions": [],
                }
                enemies.append(new_enemy)
                self.selected_enemy_index = len(enemies) - 1
                return

            enemies = floor.get("enemies", [])

            # Delete enemy button (check BEFORE selection)
            for i, enemy in enumerate(enemies):
                enemy_y = 220 + i * 70
                del_btn = pygame.Rect(right_panel_x + 120, enemy_y + 15, 30, 30)
                if del_btn.collidepoint(pos):
                    del enemies[i]
                    if self.selected_enemy_index >= len(enemies):
                        self.selected_enemy_index = max(0, len(enemies) - 1)
                    return

            # Enemy selection
            for i, enemy in enumerate(enemies):
                enemy_y = 220 + i * 70
                if pygame.Rect(right_panel_x, enemy_y, 150, 60).collidepoint(pos):
                    self.selected_enemy_index = i
                    return

            # Enemy field editing and add action
            if enemies and self.selected_enemy_index < len(enemies):
                enemy = enemies[self.selected_enemy_index]
                panel_x = 750

                fields = [
                    ("name", "名稱", 460),
                    ("hp", "HP", 490),
                    ("attack", "攻擊", 520),
                    ("defense", "防禦", 550),
                    ("scale", "圖片倍率", 580),
                ]
                for field, label, y in fields:
                    if pygame.Rect(panel_x + 60, y, 180, 30).collidepoint(pos):
                        self.editing_field = f"enemy_{field}"
                        self.edit_text = str(enemy.get(field, ""))
                        return

                attributes = ["火", "水", "木", "光", "暗"]
                attr_y = 610
                for i, attr in enumerate(attributes):
                    attr_btn = pygame.Rect(panel_x + 60 + i * 36, attr_y, 34, 30)
                    if attr_btn.collidepoint(pos):
                        enemy["attribute"] = attr
                        return
                if pygame.Rect(panel_x + 60, attr_y, 180, 30).collidepoint(pos):
                    current = enemy.get("attribute", "火")
                    idx = attributes.index(current) if current in attributes else 0
                    enemy["attribute"] = attributes[(idx + 1) % len(attributes)]
                    return

                img_height = 70
                img_spacing = 80
                visible_count = max(1, 100 // img_spacing)
                start_idx = getattr(self, "_enemy_image_scroll", 0)
                end_idx = min(
                    start_idx + visible_count, len(getattr(self, "_enemy_images", []))
                )

                for i in range(start_idx, end_idx):
                    idx = i - start_idx
                    img_x = panel_x + 105 + idx * img_spacing
                    if img_x > panel_x + 245:
                        break
                    if pygame.Rect(img_x, 345, 70, 70).collidepoint(pos):
                        base_path = os.path.dirname(os.path.abspath(__file__))
                        img_file = self._enemy_images[i]
                        enemy["image"] = f"enemy/{img_file}"
                        return

                if len(self._enemy_images) > visible_count:
                    scroll_bar_height = 90
                    thumb_y = 345 + (start_idx / len(self._enemy_images)) * (
                        scroll_bar_height
                        - max(
                            10,
                            scroll_bar_height
                            // len(self._enemy_images)
                            * visible_count,
                        )
                    )
                    thumb_h = max(
                        10, scroll_bar_height // len(self._enemy_images) * visible_count
                    )
                    if pygame.Rect(
                        panel_x + 245, 345, 6, scroll_bar_height
                    ).collidepoint(pos):
                        if pos[1] < thumb_y + thumb_h // 2:
                            self._enemy_image_scroll = max(
                                0, self._enemy_image_scroll - 1
                            )
                        else:
                            self._enemy_image_scroll = min(
                                len(self._enemy_images) - visible_count,
                                self._enemy_image_scroll + 1,
                            )
                        return

                # Action button - show action type selection
                if pygame.Rect(panel_x + 250, 530, 120, 30).collidepoint(pos):
                    actions = enemy.get("actions", [])
                    current_type = (
                        actions[-1].get("type", "attack") if actions else "attack"
                    )
                    current_idx = (
                        self.enemy_action_types.index(current_type)
                        if current_type in self.enemy_action_types
                        else 0
                    )
                    next_idx = (current_idx + 1) % len(self.enemy_action_types)
                    new_type = self.enemy_action_types[next_idx]
                    new_action = {
                        "type": new_type,
                        "value": 10,
                        "turns": 3,
                        "description": f"{self.get_action_type_name(new_type)} 持續",
                    }
                    actions.append(new_action)
                    return

                # Attribute field (must check AFTER action button)
                attr_rect = pygame.Rect(panel_x + 60, 470, 180, 30)
                if attr_rect.collidepoint(pos):
                    self.editing_field = "enemy_attribute"
                    self.edit_text = str(enemy.get("attribute", ""))
                    return

                # Action type dropdown and edit
                actions = enemy.get("actions", [])
                for i, action in enumerate(actions):
                    action_y = 640 + i * 40
                    action_type = action.get("type", "attack")

                    # Click action type button to open selection modal
                    if pygame.Rect(panel_x - 10, action_y, 100, 30).collidepoint(pos):
                        self.action_type_selecting = (i, action_y)
                        return

                    # Edit action value (only for non-attack)
                    if action_type != "attack" and pygame.Rect(
                        panel_x + 90, action_y, 40, 30
                    ).collidepoint(pos):
                        self.editing_field = f"action_value_{i}"
                        self.edit_text = str(action.get("value", 0))
                        return

                    # Edit action turns (only for non-attack)
                    if action_type != "attack" and pygame.Rect(
                        panel_x + 135, action_y, 40, 30
                    ).collidepoint(pos):
                        self.editing_field = f"action_turns_{i}"
                        self.edit_text = str(action.get("turns", 0))
                        return

                    # Delete action
                    if pygame.Rect(panel_x + 180, action_y + 2, 26, 26).collidepoint(
                        pos
                    ):
                        actions.pop(i)
                        return

        # Action type selection modal (fixed position at top-left)
        if self.action_type_selecting is not None:
            modal_x = 50
            modal_y = 50
            modal_w = 200
            modal_h = 150

            # Check if clicked on modal options
            for j, atype in enumerate(self.enemy_action_types):
                opt_rect = pygame.Rect(modal_x, modal_y + 30 + j * 30, modal_w - 20, 28)
                if opt_rect.collidepoint(pos):
                    enemies = floors[self.selected_floor_index].get("enemies", [])
                    if enemies and self.selected_enemy_index < len(enemies):
                        enemy = enemies[self.selected_enemy_index]
                        action = enemy.get("actions", [])[action_idx]
                        action["type"] = atype
                        if atype != "attack":
                            action["value"] = action.get("value", 10)
                            action["turns"] = action.get("turns", 3)
                    self.action_type_selecting = None
                    return

            # Close modal if clicked outside
            modal_rect = pygame.Rect(modal_x, modal_y, modal_w, modal_h)
            if not modal_rect.collidepoint(pos):
                self.action_type_selecting = None
                return

        # Dialogue picker modal (skip if trigger picker is open)
        if self.dialogue_picker_open is not None and not self.trigger_picker_open:
            picker_w = 400
            picker_h = 350
            picker_x = (SCREEN_WIDTH - picker_w) // 2
            picker_y = (SCREEN_HEIGHT - picker_h) // 2

            target_type, target_index = self.dialogue_picker_open

            # Check if clicked on a dialogue option
            dialogues = self.get_dialogue_list()
            dialogue_items = list(dialogues.items())
            for i, (dlg_key, dlg_data) in enumerate(dialogue_items):
                opt_rect = pygame.Rect(
                    picker_x + 20, picker_y + 50 + i * 45, picker_w - 40, 40
                )
                if opt_rect.collidepoint(pos):
                    self.selected_dialogue_for_trigger = (
                        target_type,
                        target_index,
                        dlg_key,
                    )
                    if target_type == "stage":
                        self.selected_enemy_index = 0
                    self.trigger_picker_open = True
                    return

            # Close modal if clicked outside
            modal_rect = pygame.Rect(picker_x, picker_y, picker_w, picker_h)
            if not modal_rect.collidepoint(pos):
                self.dialogue_picker_open = None
                return

        # Trigger picker modal
        if self.trigger_picker_open and self.selected_dialogue_for_trigger:
            target_type, target_index, dlg_key = self.selected_dialogue_for_trigger
            trigger_w = 300
            trigger_h = 350
            trigger_x = (SCREEN_WIDTH - trigger_w) // 2
            trigger_y = (SCREEN_HEIGHT - trigger_h) // 2
            print(f"[DEBUG] trigger_picker pos: {pos}, trigger_y: {trigger_y}")
            small_font = get_font(14)

            pygame.draw.rect(
                self.screen,
                (30, 30, 40),
                (trigger_x, trigger_y, trigger_w, trigger_h),
                border_radius=10,
            )
            pygame.draw.rect(
                self.screen,
                (100, 100, 150),
                (trigger_x, trigger_y, trigger_w, trigger_h),
                2,
                border_radius=10,
            )

            title_text = small_font.render("選擇觸發條件", True, (255, 220, 100))
            self.screen.blit(title_text, (trigger_x + 20, trigger_y + 5))

            for i, (trigger_type, trigger_name) in enumerate(self.trigger_types):
                opt_rect = pygame.Rect(
                    trigger_x + 20, trigger_y + 40 + i * 40, trigger_w - 40, 35
                )
                pygame.draw.rect(self.screen, (60, 60, 70), opt_rect, border_radius=3)
                opt_text = small_font.render(trigger_name, True, (255, 255, 255))
                self.screen.blit(opt_text, (opt_rect.x + 5, opt_rect.y + 8))

                if trigger_type == "on_enemy_action":
                    action_y = trigger_y + 40 + i * 40 + 35
                    floors = self.stage_data.get("floors", [])
                    if target_type == "floor" and 0 <= target_index < len(floors):
                        enemies = floors[target_index].get("enemies", [])
                        if enemies and self.selected_enemy_index < len(enemies):
                            enemy = enemies[self.selected_enemy_index]
                            actions = enemy.get("actions", [])
                            for j, action in enumerate(actions):
                                action_rect = pygame.Rect(
                                    trigger_x + 40, action_y + j * 25, 100, 22
                                )
                                pygame.draw.rect(
                                    self.screen,
                                    (50, 50, 60),
                                    action_rect,
                                    border_radius=2,
                                )
                                action_type = action.get("type", "attack")
                                type_name = self.get_action_type_name(action_type)
                                action_text = small_font.render(
                                    f"第{j + 1}次 {type_name}", True, (180, 180, 180)
                                )
                                self.screen.blit(
                                    action_text, (action_rect.x + 3, action_rect.y + 2)
                                )

            for i, (trigger_type, trigger_name) in enumerate(self.trigger_types):
                opt_rect = pygame.Rect(
                    trigger_x + 20, trigger_y + 40 + i * 40, trigger_w - 40, 35
                )
                # Debug: Draw a visible border to verify position
                pygame.draw.rect(self.screen, (60, 60, 70), opt_rect, border_radius=3)
                opt_text = small_font.render(trigger_name, True, (255, 255, 255))
                self.screen.blit(opt_text, (opt_rect.x + 5, opt_rect.y + 8))

                if opt_rect.collidepoint(pos):
                    print(
                        f"[DEBUG] Clicked on trigger: {trigger_type} at rect {opt_rect}"
                    )
                    selected_action_index = None
                    # Only require action index for on_enemy_action on floor level
                    if trigger_type == "on_enemy_action" and target_type == "floor":
                        floors = self.stage_data.get("floors", [])
                        if 0 <= target_index < len(floors):
                            enemies = floors[target_index].get("enemies", [])
                            if enemies and self.selected_enemy_index < len(enemies):
                                enemy = enemies[self.selected_enemy_index]
                                actions = enemy.get("actions", [])
                                action_y = trigger_y + 40 + i * 40 + 35
                                for j in range(len(actions)):
                                    action_rect = pygame.Rect(
                                        trigger_x + 40, action_y + j * 25, 100, 22
                                    )
                                    if action_rect.collidepoint(pos):
                                        selected_action_index = j
                                        break

                        if selected_action_index is None:
                            return

                    new_dialogue_ref = {
                        "dialogue_id": dlg_key,
                        "trigger": trigger_type,
                    }

                    if trigger_type == "on_enemy_action" and target_type == "floor":
                        new_dialogue_ref["action_index"] = selected_action_index
                        new_dialogue_ref["enemy_index"] = self.selected_enemy_index

                    if target_type == "stage":
                        stage_dialogue = self.stage_data.get("dialogue", [])
                        stage_dialogue.append(new_dialogue_ref)
                        self.stage_data["dialogue"] = stage_dialogue
                    elif target_type == "floor":
                        floors = self.stage_data.get("floors", [])
                        if 0 <= target_index < len(floors):
                            floor_dialogue = floors[target_index].get("dialogue", [])
                            floor_dialogue.append(new_dialogue_ref)
                            floors[target_index]["dialogue"] = floor_dialogue

                    self.trigger_picker_open = False
                    self.selected_dialogue_for_trigger = None
                    self.dialogue_picker_open = None
                    return

            modal_rect = pygame.Rect(trigger_x, trigger_y, trigger_w, trigger_h)
            if not modal_rect.collidepoint(pos):
                self.trigger_picker_open = False
                self.selected_dialogue_for_trigger = None
                return

        # Reward picker modal
        if self.reward_picker_open:
            picker_w = 200
            picker_h = 300
            picker_x = (SCREEN_WIDTH - picker_w) // 2
            picker_y = (SCREEN_HEIGHT - picker_h) // 2
            small_font = get_font(14)

            pygame.draw.rect(
                self.screen,
                (30, 30, 40),
                (picker_x, picker_y, picker_w, picker_h),
                border_radius=10,
            )
            pygame.draw.rect(
                self.screen,
                (100, 100, 150),
                (picker_x, picker_y, picker_w, picker_h),
                2,
                border_radius=10,
            )

            title_text = small_font.render("輸入寵物 ID", True, (255, 220, 100))
            self.screen.blit(title_text, (picker_x + 20, picker_y + 10))

            input_rect = pygame.Rect(picker_x + 20, picker_y + 40, picker_w - 40, 30)
            pygame.draw.rect(self.screen, (50, 50, 60), input_rect, border_radius=3)
            if self.editing_field == "reward_id_input":
                input_text = small_font.render(
                    self.edit_text + "▌", True, (255, 255, 255)
                )
            else:
                input_text = small_font.render("輸入 ID...", True, (120, 120, 120))
            self.screen.blit(input_text, (input_rect.x + 5, input_rect.y + 5))

            confirm_btn = pygame.Rect(picker_x + 30, picker_y + 80, picker_w - 60, 30)
            pygame.draw.rect(self.screen, (60, 80, 120), confirm_btn, border_radius=3)
            confirm_text = small_font.render("確認", True, (255, 255, 255))
            self.screen.blit(
                confirm_text, (confirm_btn.centerx - 15, confirm_btn.centery - 7)
            )

            close_hint = get_font(12).render("點擊空白關閉", True, (120, 120, 120))
            self.screen.blit(close_hint, (picker_x + 20, picker_y + picker_h - 25))

            modal_rect = pygame.Rect(picker_x, picker_y, picker_w, picker_h)
            if not modal_rect.collidepoint(pos):
                self.reward_picker_open = False
                self.editing_field = None
                self.edit_text = ""
                return

            if confirm_btn.collidepoint(pos) and self.edit_text:
                try:
                    pet_id = int(self.edit_text)
                    rewards = self.stage_data.get("rewards", [])
                    rewards.append({"pet_id": pet_id, "count": 1})
                    self.stage_data["rewards"] = rewards
                    self.reward_picker_open = False
                    self.editing_field = None
                    self.edit_text = ""
                except ValueError:
                    pass
                return

            if input_rect.collidepoint(pos):
                self.editing_field = "reward_id_input"
                self.edit_text = ""
                return

    def handle_file_drop(self, filepath):
        import os

        ext = os.path.splitext(filepath)[1].lower()
        if ext not in [".png", ".jpg", ".jpeg", ".bmp"]:
            return

        base_path = os.path.dirname(os.path.abspath(__file__))
        enemy_dir = os.path.join(base_path, "assets", "images", "enemy")
        os.makedirs(enemy_dir, exist_ok=True)

        floors = self.stage_data.get("floors", [])
        if not floors or self.selected_floor_index >= len(floors):
            return

        floor = floors[self.selected_floor_index]
        enemies = floor.get("enemies", [])
        if not enemies or self.selected_enemy_index >= len(enemies):
            return

        enemy = enemies[self.selected_enemy_index]
        enemy_id = enemy.get("image") or f"enemy_{len(enemies)}"

        target_path = os.path.join(enemy_dir, f"{enemy_id}.png")
        import shutil

        shutil.copy2(filepath, target_path)
        enemy["image"] = f"enemy/{enemy_id}"
        print(f"已設定敵人圖片: {target_path}")

        # 刷新圖片列表
        self._load_enemy_images()

    def _load_enemy_images(self):
        import os

        base_path = os.path.dirname(os.path.abspath(__file__))
        enemy_dir = os.path.join(base_path, "assets", "images", "enemy")
        if os.path.exists(enemy_dir):
            self._enemy_images = [
                f
                for f in os.listdir(enemy_dir)
                if f.endswith((".png", ".jpg", ".jpeg"))
            ]
        else:
            self._enemy_images = []

    def show_enemy_image_selector(self):
        self._load_enemy_images()
        self._selecting_enemy_image = True

    def handle_enemy_image_selector_click(self, pos):
        if (
            not hasattr(self, "_selecting_enemy_image")
            or not self._selecting_enemy_image
        ):
            return False

        # 關閉按鈕
        close_btn = pygame.Rect(SCREEN_WIDTH - 120, 60, 80, 30)
        if close_btn.collidepoint(pos):
            self._selecting_enemy_image = False
            return True

        # 選擇圖片
        if hasattr(self, "_enemy_images"):
            for i, img in enumerate(self._enemy_images):
                row = i // 4
                col = i % 4
                img_x = 100 + col * 100
                img_y = 120 + row * 100
                img_rect = pygame.Rect(img_x, img_y, 80, 80)
                if img_rect.collidepoint(pos):
                    floors = self.stage_data.get("floors", [])
                    if floors and self.selected_floor_index < len(floors):
                        floor = floors[self.selected_floor_index]
                        enemies = floor.get("enemies", [])
                        if enemies and self.selected_enemy_index < len(enemies):
                            enemies[self.selected_enemy_index]["image"] = f"enemy/{img}"
                    self._selecting_enemy_image = False
                    return True
        return False

    def draw_enemy_image_selector(self):
        if (
            not hasattr(self, "_selecting_enemy_image")
            or not self._selecting_enemy_image
        ):
            return

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        modal_rect = pygame.Rect(50, 50, SCREEN_WIDTH - 100, SCREEN_HEIGHT - 100)
        pygame.draw.rect(self.screen, (30, 30, 40), modal_rect, border_radius=10)
        pygame.draw.rect(self.screen, (100, 100, 150), modal_rect, 2, border_radius=10)

        font = get_font(24)
        title = font.render("選擇敵人圖片", True, (255, 220, 100))
        self.screen.blit(title, (modal_rect.centerx - title.get_width() // 2, 60))

        # 關閉按鈕
        close_btn = pygame.Rect(SCREEN_WIDTH - 120, 60, 80, 30)
        pygame.draw.rect(self.screen, (100, 50, 50), close_btn, border_radius=5)
        close_text = get_font(14).render("關閉", True, (255, 255, 255))
        self.screen.blit(close_text, (close_btn.centerx - 20, close_btn.centery - 7))

        # 顯示圖片列表
        if hasattr(self, "_enemy_images"):
            for i, img in enumerate(self._enemy_images):
                row = i // 4
                col = i % 4
                img_x = 100 + col * 100
                img_y = 120 + row * 100
                img_rect = pygame.Rect(img_x, img_y, 80, 80)
                pygame.draw.rect(self.screen, (50, 50, 60), img_rect, border_radius=3)

                try:
                    base_path = os.path.dirname(os.path.abspath(__file__))
                    img_path = os.path.join(base_path, "assets", "images", "enemy", img)
                    img_surf = pygame.image.load(img_path)
                    img_surf = pygame.transform.scale(img_surf, (70, 70))
                    self.screen.blit(img_surf, (img_x + 5, img_y + 5))
                except:
                    img_text = get_font(12).render(img[:10], True, (150, 150, 150))
                    self.screen.blit(img_text, (img_x + 5, img_y + 30))

        # 提示
        hint = get_font(14).render(
            "拖入新圖片到敵人區域自動新增", True, (150, 150, 150)
        )
        self.screen.blit(hint, (100, SCREEN_HEIGHT - 80))

    def draw(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        modal_rect = pygame.Rect(50, 50, SCREEN_WIDTH - 100, SCREEN_HEIGHT - 100)
        pygame.draw.rect(self.screen, (30, 30, 40), modal_rect, border_radius=10)
        pygame.draw.rect(self.screen, (100, 100, 150), modal_rect, 2, border_radius=10)

        # Draw reward picker if open
        if self.reward_picker_open:
            picker_w = 200
            picker_h = 300
            picker_x = (SCREEN_WIDTH - picker_w) // 2
            picker_y = (SCREEN_HEIGHT - picker_h) // 2
            small_font = get_font(14)

            pygame.draw.rect(
                self.screen,
                (30, 30, 40),
                (picker_x, picker_y, picker_w, picker_h),
                border_radius=10,
            )
            pygame.draw.rect(
                self.screen,
                (100, 100, 150),
                (picker_x, picker_y, picker_w, picker_h),
                2,
                border_radius=10,
            )

            title_text = small_font.render("輸入寵物 ID", True, (255, 220, 100))
            self.screen.blit(title_text, (picker_x + 20, picker_y + 10))

            input_rect = pygame.Rect(picker_x + 20, picker_y + 40, picker_w - 40, 30)
            pygame.draw.rect(self.screen, (50, 50, 60), input_rect, border_radius=3)
            if self.editing_field == "reward_id_input":
                input_text = small_font.render(
                    self.edit_text + "▌", True, (255, 255, 255)
                )
            else:
                input_text = small_font.render("輸入 ID...", True, (120, 120, 120))
            self.screen.blit(input_text, (input_rect.x + 5, input_rect.y + 5))

            confirm_btn = pygame.Rect(picker_x + 30, picker_y + 80, picker_w - 60, 30)
            pygame.draw.rect(self.screen, (60, 80, 120), confirm_btn, border_radius=3)
            confirm_text = small_font.render("確認", True, (255, 255, 255))
            self.screen.blit(
                confirm_text, (confirm_btn.centerx - 15, confirm_btn.centery - 7)
            )

            close_hint = get_font(12).render("點擊空白關閉", True, (120, 120, 120))
            self.screen.blit(close_hint, (picker_x + 20, picker_y + picker_h - 25))

        font = get_font(24)
        title = font.render("關卡編輯器", True, (255, 220, 100))
        self.screen.blit(title, (modal_rect.centerx - title.get_width() // 2, 65))

        save_btn = pygame.Rect(SCREEN_WIDTH - 180, 60, 80, 30)
        pygame.draw.rect(self.screen, (50, 100, 50), save_btn, border_radius=5)
        save_text = get_font(16).render("保存", True, (255, 255, 255))
        self.screen.blit(save_text, (save_btn.centerx - 20, save_btn.centery - 8))

        close_btn = pygame.Rect(SCREEN_WIDTH - 180, 100, 80, 30)
        pygame.draw.rect(self.screen, (100, 50, 50), close_btn, border_radius=5)
        close_text = get_font(16).render("取消", True, (255, 255, 255))
        self.screen.blit(close_text, (close_btn.centerx - 20, close_btn.centery - 8))

        small_font = get_font(14)
        label = small_font.render("關卡名稱:", True, (180, 180, 180))
        self.screen.blit(label, (100, 75))

        type_label = small_font.render("類型:", True, (180, 180, 180))
        self.screen.blit(type_label, (450, 75))

        current_type = self.stage_data.get("stage_type", 1)
        type_text = ""
        for t, name in self.stage_type_options:
            if t == current_type:
                type_text = name
                break
        type_rect = pygame.Rect(500, 70, 120, 30)
        pygame.draw.rect(self.screen, (50, 50, 60), type_rect, border_radius=3)
        type_surf = get_font(14).render(type_text, True, (255, 255, 255))
        self.screen.blit(type_surf, (type_rect.x + 5, type_rect.y + 5))

        exp_label = small_font.render("經驗值:", True, (180, 180, 180))
        self.screen.blit(exp_label, (650, 75))

        exp_rect = pygame.Rect(720, 70, 80, 30)
        pygame.draw.rect(self.screen, (50, 50, 60), exp_rect, border_radius=3)
        if self.editing_field == "stage_exp":
            exp_display = self.edit_text + "▌"
        else:
            exp_display = str(self.stage_data.get("exp", 0))
        exp_surf = get_font(14).render(exp_display, True, (255, 255, 255))
        self.screen.blit(exp_surf, (exp_rect.x + 5, exp_rect.y + 5))

        reward_label = small_font.render("獎勵:", True, (180, 180, 180))
        self.screen.blit(reward_label, (810, 75))

        reward_btn = pygame.Rect(860, 70, 80, 30)
        pygame.draw.rect(self.screen, (60, 80, 120), reward_btn, border_radius=3)
        reward_text = small_font.render("+ 添加", True, (255, 255, 255))
        self.screen.blit(reward_text, (reward_btn.centerx - 20, reward_btn.centery - 7))

        rewards = self.stage_data.get("rewards", [])
        reward_y = 110
        for reward in rewards:
            pet_id = reward.get("pet_id", 0)
            pet_count = reward.get("count", 1)
            reward_rect = pygame.Rect(810, reward_y, 80, 22)
            pygame.draw.rect(self.screen, (50, 50, 60), reward_rect, border_radius=2)
            reward_surf = get_font(10).render(
                f"ID:{pet_id} x{pet_count}", True, (200, 200, 200)
            )
            self.screen.blit(reward_surf, (reward_rect.x + 3, reward_rect.y + 3))

            del_reward_btn = pygame.Rect(890, reward_y + 2, 18, 18)
            pygame.draw.rect(
                self.screen, (100, 50, 50), del_reward_btn, border_radius=2
            )
            del_text = get_font(10).render("X", True, (255, 255, 255))
            self.screen.blit(
                del_text, (del_reward_btn.centerx - 4, del_reward_btn.centery - 5)
            )
            reward_y += 25

        name_rect = pygame.Rect(180, 70, 250, 30)
        pygame.draw.rect(self.screen, (50, 50, 60), name_rect, border_radius=3)
        if self.editing_field == "stage_name":
            display = self.edit_text + "▌"
        else:
            display = self.stage_data.get("name", "新關卡")
        text_surf = get_font(16).render(display, True, (255, 255, 255))
        self.screen.blit(text_surf, (name_rect.x + 5, name_rect.y + 5))

        add_dlg_btn = pygame.Rect(650, 105, 120, 28)
        pygame.draw.rect(self.screen, (60, 80, 120), add_dlg_btn, border_radius=3)
        dlg_text = small_font.render("+ 對話", True, (255, 255, 255))
        self.screen.blit(dlg_text, (add_dlg_btn.centerx - 25, add_dlg_btn.centery - 7))

        stage_dialogue = self.stage_data.get("dialogue", [])
        if stage_dialogue:
            dlg_y = 135
            for dlg_idx, dlg_ref in enumerate(stage_dialogue):
                dlg_id = dlg_ref.get("dialogue_id", "")
                trigger = dlg_ref.get("trigger", "manual")
                dlg_info = self.get_dialogue_list().get(dlg_id, {})
                dlg_name = (
                    dlg_info.get("name", dlg_id)
                    if isinstance(dlg_info, dict)
                    else dlg_id
                )
                trigger_name = self.get_trigger_type_name(trigger)

                dlg_rect = pygame.Rect(650, dlg_y, 120, 22)
                pygame.draw.rect(self.screen, (50, 50, 60), dlg_rect, border_radius=2)
                dlg_surf = get_font(10).render(
                    f"{dlg_name[:10]}..", True, (200, 200, 200)
                )
                self.screen.blit(dlg_surf, (dlg_rect.x + 3, dlg_rect.y + 3))

                trigger_rect = pygame.Rect(650, dlg_y + 22, 120, 18)
                pygame.draw.rect(
                    self.screen, (40, 40, 50), trigger_rect, border_radius=2
                )
                trigger_surf = get_font(9).render(trigger_name, True, (150, 180, 150))
                self.screen.blit(trigger_surf, (trigger_rect.x + 3, trigger_rect.y + 2))

                del_dlg_btn = pygame.Rect(770, dlg_y + 2, 18, 18)
                pygame.draw.rect(
                    self.screen, (100, 50, 50), del_dlg_btn, border_radius=2
                )
                del_text = get_font(10).render("X", True, (255, 255, 255))
                self.screen.blit(
                    del_text, (del_dlg_btn.centerx - 4, del_dlg_btn.centery - 5)
                )
                dlg_y += 42

        floors = self.stage_data.get("floors", [])
        for i, floor in enumerate(floors):
            floor_y = 180 + i * 60
            bg_color = (50, 80, 120) if i == self.selected_floor_index else (40, 50, 60)
            floor_rect = pygame.Rect(50, floor_y, 500, 50)
            pygame.draw.rect(self.screen, bg_color, floor_rect, border_radius=3)

            floor_text = get_font(18).render(
                f"層 {floor.get('floor_num', 1)}", True, (255, 255, 255)
            )
            self.screen.blit(floor_text, (60, floor_y + 15))

            enemy_count = len(floor.get("enemies", []))
            enemy_text = small_font.render(
                f"敵人: {enemy_count}", True, (180, 180, 180)
            )
            self.screen.blit(enemy_text, (150, floor_y + 18))

            del_floor_btn = pygame.Rect(500, floor_y + 10, 35, 30)
            pygame.draw.rect(self.screen, (100, 50, 50), del_floor_btn, border_radius=3)
            del_text = small_font.render("X", True, (255, 255, 255))
            self.screen.blit(
                del_text, (del_floor_btn.centerx - 5, del_floor_btn.centery - 7)
            )

        add_floor_btn = pygame.Rect(50, 180 + len(floors) * 60, 150, 35)
        pygame.draw.rect(self.screen, (50, 80, 50), add_floor_btn, border_radius=3)
        add_floor_text = small_font.render("+ 新增樓層", True, (255, 255, 255))
        self.screen.blit(
            add_floor_text, (add_floor_btn.centerx - 40, add_floor_btn.centery - 7)
        )

        if floors and self.selected_floor_index < len(floors):
            floor = floors[self.selected_floor_index]
            right_panel_x = 570

            add_floor_dlg_btn = pygame.Rect(right_panel_x, 140, 80, 30)
            pygame.draw.rect(
                self.screen, (60, 80, 120), add_floor_dlg_btn, border_radius=3
            )
            floor_dlg_text = small_font.render("+ 對話", True, (255, 255, 255))
            self.screen.blit(
                floor_dlg_text,
                (add_floor_dlg_btn.centerx - 25, add_floor_dlg_btn.centery - 7),
            )

            add_enemy_btn = pygame.Rect(right_panel_x, 180, 80, 30)
            pygame.draw.rect(self.screen, (60, 80, 120), add_enemy_btn, border_radius=3)
            enemy_text = small_font.render("+ 敵人", True, (255, 255, 255))
            self.screen.blit(
                enemy_text, (add_enemy_btn.centerx - 25, add_enemy_btn.centery - 7)
            )

            enemies = floor.get("enemies", [])
            for i, enemy in enumerate(enemies):
                enemy_y = 220 + i * 70
                enemy_rect = pygame.Rect(right_panel_x, enemy_y, 150, 60)
                bg = (50, 80, 120) if i == self.selected_enemy_index else (40, 50, 60)
                pygame.draw.rect(self.screen, bg, enemy_rect, border_radius=3)

                enemy_name = small_font.render(
                    enemy.get("name", "新敵人")[:12], True, (255, 255, 255)
                )
                self.screen.blit(enemy_name, (right_panel_x + 10, enemy_y + 5))

                enemy_hp = small_font.render(
                    f"HP: {enemy.get('hp', 0)}", True, (180, 180, 180)
                )
                self.screen.blit(enemy_hp, (right_panel_x + 10, enemy_y + 30))

                del_btn = pygame.Rect(right_panel_x + 120, enemy_y + 15, 30, 30)
                pygame.draw.rect(self.screen, (120, 50, 50), del_btn, border_radius=3)
                del_text = small_font.render("X", True, (255, 255, 255))
                self.screen.blit(del_text, (del_btn.centerx - 5, del_btn.centery - 7))

            if enemies and self.selected_enemy_index < len(enemies):
                enemy = enemies[self.selected_enemy_index]
                panel_x = 750

                # 敵人圖片顯示區域
                img_area = pygame.Rect(panel_x - 10, 340, 230, 100)
                pygame.draw.rect(self.screen, (35, 35, 45), img_area, border_radius=5)

                enemy_img_path = enemy.get("image")
                if enemy_img_path:
                    base_path = os.path.dirname(os.path.abspath(__file__))
                    full_path = os.path.join(
                        base_path,
                        "assets",
                        "images",
                        enemy_img_path.replace("/", os.sep),
                    )
                    if os.path.exists(full_path):
                        try:
                            img = pygame.image.load(full_path)
                            img = pygame.transform.scale(img, (90, 90))
                            self.screen.blit(img, (panel_x, 345))
                        except:
                            img_text = small_font.render(
                                "載入失敗", True, (150, 150, 150)
                            )
                            self.screen.blit(img_text, (panel_x + 20, 380))
                    else:
                        img_text = small_font.render("無圖片", True, (150, 150, 150))
                        self.screen.blit(img_text, (panel_x + 20, 380))
                else:
                    img_text = small_font.render("選擇圖片", True, (150, 150, 150))
                    self.screen.blit(img_text, (panel_x + 20, 380))

                if not hasattr(self, "_enemy_image_scroll"):
                    self._enemy_image_scroll = 0
                if not hasattr(self, "_enemy_images"):
                    self._load_enemy_images()

                img_selector_bg = pygame.Rect(panel_x + 95, 340, 160, 100)
                pygame.draw.rect(
                    self.screen, (30, 30, 40), img_selector_bg, border_radius=5
                )
                pygame.draw.rect(
                    self.screen, (100, 100, 150), img_selector_bg, 1, border_radius=5
                )

                img_height = 70
                img_spacing = 80
                visible_count = max(1, 100 // img_spacing)
                start_idx = self._enemy_image_scroll
                end_idx = min(start_idx + visible_count, len(self._enemy_images))

                for i in range(start_idx, end_idx):
                    idx = i - start_idx
                    img_x = panel_x + 105 + idx * img_spacing
                    if img_x > panel_x + 245:
                        break
                    img_rect = pygame.Rect(img_x, 345, 70, 70)
                    pygame.draw.rect(
                        self.screen, (50, 50, 60), img_rect, border_radius=3
                    )
                    try:
                        base_path = os.path.dirname(os.path.abspath(__file__))
                        img_path = os.path.join(
                            base_path,
                            "assets",
                            "images",
                            "enemy",
                            self._enemy_images[i],
                        )
                        img = pygame.image.load(img_path)
                        img = pygame.transform.scale(img, (60, 60))
                        self.screen.blit(img, (img_x + 5, 350))
                    except:
                        pass

                if len(self._enemy_images) > visible_count:
                    scroll_bar_height = 90
                    thumb_height = max(
                        10, scroll_bar_height // len(self._enemy_images) * visible_count
                    )
                    scroll_y = 345 + (
                        self._enemy_image_scroll / len(self._enemy_images)
                    ) * (scroll_bar_height - thumb_height)
                    pygame.draw.rect(
                        self.screen,
                        (80, 80, 100),
                        (panel_x + 245, 345, 6, scroll_bar_height),
                        border_radius=3,
                    )
                    pygame.draw.rect(
                        self.screen,
                        (150, 150, 200),
                        (panel_x + 245, scroll_y, 6, thumb_height),
                        border_radius=3,
                    )

                pygame.draw.rect(
                    self.screen,
                    (35, 35, 45),
                    (panel_x - 10, 450, 250, 140),
                    border_radius=5,
                )

                fields = [
                    ("name", "名稱", 460),
                    ("hp", "HP", 490),
                    ("attack", "攻擊", 520),
                    ("defense", "防禦", 550),
                    ("scale", "圖片倍率", 580),
                ]
                for field, label, y in fields:
                    label_text = small_font.render(f"{label}:", True, (180, 180, 180))
                    self.screen.blit(label_text, (panel_x, y))

                    rect = pygame.Rect(panel_x + 60, y, 180, 30)
                    pygame.draw.rect(self.screen, (50, 50, 60), rect, border_radius=3)

                    if self.editing_field == f"enemy_{field}":
                        display = self.edit_text + "▌"
                    else:
                        display = str(enemy.get(field, ""))
                    val_text = get_font(14).render(display[:15], True, (255, 255, 255))
                    self.screen.blit(val_text, (rect.x + 5, rect.y + 5))

                attr_label = small_font.render("屬性:", True, (180, 180, 180))
                self.screen.blit(attr_label, (panel_x, 610))
                attributes = ["火", "水", "木", "光", "暗"]
                ATTR_COLORS = {
                    "火": (200, 50, 50),
                    "水": (50, 100, 200),
                    "木": (50, 180, 50),
                    "光": (220, 220, 100),
                    "暗": (150, 50, 180),
                }
                current_attr = enemy.get("attribute", "火")
                for i, attr in enumerate(attributes):
                    attr_btn = pygame.Rect(panel_x + 60 + i * 36, 610, 34, 30)
                    color = ATTR_COLORS.get(attr, (100, 100, 100))
                    pygame.draw.rect(self.screen, color, attr_btn, border_radius=3)
                    if attr == current_attr:
                        pygame.draw.rect(
                            self.screen, (255, 255, 255), attr_btn, 2, border_radius=3
                        )
                    attr_text = small_font.render(attr, True, (255, 255, 255))
                    self.screen.blit(
                        attr_text, (attr_btn.centerx - 10, attr_btn.centery - 7)
                    )

                actions = enemy.get("actions", [])
                add_action_btn = pygame.Rect(panel_x + 250, 530, 120, 30)
                pygame.draw.rect(
                    self.screen, (60, 80, 120), add_action_btn, border_radius=3
                )
                action_text = small_font.render("+ 行動", True, (255, 255, 255))
                self.screen.blit(
                    action_text,
                    (add_action_btn.centerx - 25, add_action_btn.centery - 7),
                )

                for i, action in enumerate(actions):
                    action_y = 640 + i * 40
                    action_type = action.get("type", "attack")
                    type_name = self.get_action_type_name(action_type)
                    action_val = action.get("value", 0)
                    action_turns = action.get("turns", 0)

                    action_num_text = small_font.render(
                        f"第{i + 1}次", True, (150, 150, 150)
                    )
                    self.screen.blit(action_num_text, (panel_x - 40, action_y + 5))

                    action_btn = pygame.Rect(panel_x, action_y, 100, 30)
                    pygame.draw.rect(
                        self.screen, (50, 50, 60), action_btn, border_radius=3
                    )
                    type_text = small_font.render(type_name, True, (255, 255, 255))
                    self.screen.blit(type_text, (panel_x + 5, action_y + 5))

                    hint_text = get_font(10).render("▼", True, (100, 150, 100))
                    self.screen.blit(hint_text, (panel_x + 85, action_y + 8))

                    if action_type != "attack":
                        val_rect = pygame.Rect(panel_x + 100, action_y, 40, 30)
                        pygame.draw.rect(
                            self.screen, (50, 50, 60), val_rect, border_radius=3
                        )
                        if self.editing_field == f"action_value_{i}":
                            val_display = self.edit_text + "▌"
                        else:
                            val_display = str(action_val)
                        val_text = small_font.render(val_display, True, (255, 255, 255))
                        self.screen.blit(val_text, (val_rect.x + 3, val_rect.y + 5))

                        turns_rect = pygame.Rect(panel_x + 145, action_y, 40, 30)
                        pygame.draw.rect(
                            self.screen, (50, 50, 60), turns_rect, border_radius=3
                        )
                        if self.editing_field == f"action_turns_{i}":
                            turns_display = self.edit_text + "▌"
                        else:
                            turns_display = f"{action_turns}回合"
                        turns_text = small_font.render(
                            turns_display, True, (255, 255, 255)
                        )
                        self.screen.blit(
                            turns_text, (turns_rect.x + 3, turns_rect.y + 5)
                        )

                    del_btn = pygame.Rect(panel_x + 190, action_y + 2, 26, 26)
                    pygame.draw.rect(
                        self.screen, (120, 50, 50), del_btn, border_radius=3
                    )
                    del_text = small_font.render("X", True, (255, 255, 255))
                    self.screen.blit(
                        del_text, (del_btn.centerx - 4, del_btn.centery - 6)
                    )

        # Dialogue picker modal (skip if trigger picker is open)
        if self.dialogue_picker_open is not None and not self.trigger_picker_open:
            picker_w = 400
            picker_h = 350
            picker_x = (SCREEN_WIDTH - picker_w) // 2
            picker_y = (SCREEN_HEIGHT - picker_h) // 2

            pygame.draw.rect(
                self.screen,
                (30, 30, 40),
                (picker_x, picker_y, picker_w, picker_h),
                border_radius=10,
            )
            pygame.draw.rect(
                self.screen,
                (100, 100, 150),
                (picker_x, picker_y, picker_w, picker_h),
                2,
                border_radius=10,
            )

            title_font = get_font(20)
            title = title_font.render("選擇對話", True, (255, 220, 100))
            self.screen.blit(title, (picker_x + 20, picker_y + 10))

            dialogues = self.get_dialogue_list()
            dialogue_items = list(dialogues.items())

            small_font = get_font(14)
            for i, (dlg_key, dlg_data) in enumerate(dialogue_items):
                if i >= 5:
                    break
                opt_rect = pygame.Rect(
                    picker_x + 20, picker_y + 50 + i * 45, picker_w - 40, 40
                )
                pygame.draw.rect(self.screen, (60, 60, 70), opt_rect, border_radius=3)
                dlg_name = dlg_data.get("name", dlg_key)
                opt_text = small_font.render(dlg_name, True, (255, 255, 255))
                self.screen.blit(opt_text, (opt_rect.x + 5, opt_rect.y + 10))

            close_hint = get_font(12).render("點擊空白關閉", True, (120, 120, 120))
            self.screen.blit(close_hint, (picker_x + 20, picker_y + picker_h - 25))

        if self.trigger_picker_open and self.selected_dialogue_for_trigger:
            target_type, target_index, dlg_key = self.selected_dialogue_for_trigger
            trigger_w = 300
            trigger_h = 350
            trigger_x = (SCREEN_WIDTH - trigger_w) // 2
            trigger_y = (SCREEN_HEIGHT - trigger_h) // 2

            pygame.draw.rect(
                self.screen,
                (30, 30, 40),
                (trigger_x, trigger_y, trigger_w, trigger_h),
                border_radius=10,
            )
            pygame.draw.rect(
                self.screen,
                (100, 100, 150),
                (trigger_x, trigger_y, trigger_w, trigger_h),
                2,
                border_radius=10,
            )

            title_text = small_font.render("選擇觸發條件", True, (255, 220, 100))
            self.screen.blit(title_text, (trigger_x + 20, trigger_y + 5))

            for i, (trigger_type, trigger_name) in enumerate(self.trigger_types):
                opt_rect = pygame.Rect(
                    trigger_x + 20, trigger_y + 40 + i * 40, trigger_w - 40, 35
                )
                pygame.draw.rect(self.screen, (60, 60, 70), opt_rect, border_radius=3)
                opt_text = small_font.render(trigger_name, True, (255, 255, 255))
                self.screen.blit(opt_text, (opt_rect.x + 5, opt_rect.y + 8))

            close_hint = get_font(12).render("點擊空白取消", True, (120, 120, 120))
            self.screen.blit(close_hint, (trigger_x + 20, trigger_y + trigger_h - 20))

        if self.action_type_selecting is not None:
            modal_x = 50
            modal_y = 50
            modal_w = 200
            modal_h = 150

            pygame.draw.rect(
                self.screen,
                (40, 40, 50),
                (modal_x, modal_y, modal_w, modal_h),
                border_radius=8,
            )
            pygame.draw.rect(
                self.screen,
                (100, 100, 150),
                (modal_x, modal_y, modal_w, modal_h),
                2,
                border_radius=8,
            )

            title_text = small_font.render("選擇行動類型", True, (255, 220, 100))
            self.screen.blit(title_text, (modal_x + 20, modal_y + 5))

            for j, atype in enumerate(self.enemy_action_types):
                opt_rect = pygame.Rect(
                    modal_x + 10, modal_y + 30 + j * 30, modal_w - 20, 28
                )
                pygame.draw.rect(self.screen, (60, 60, 70), opt_rect, border_radius=3)
                opt_text = small_font.render(
                    self.get_action_type_name(atype), True, (255, 255, 255)
                )
                self.screen.blit(opt_text, (opt_rect.x + 5, opt_rect.y + 5))

            close_hint = get_font(12).render("點擊空白關閉", True, (120, 120, 120))
            self.screen.blit(close_hint, (modal_x + 20, modal_y + modal_h - 20))

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return None
                elif event.type == pygame.KEYDOWN:
                    log(
                        f"StageEditor: keydown key={event.key}, editing_field={repr(self.editing_field)}"
                    )
                    if event.key == pygame.K_ESCAPE:
                        if self.dialogue_picker_open:
                            self.dialogue_picker_open = None
                        elif self.action_type_selecting:
                            self.action_type_selecting = None
                        elif self.trigger_picker_open:
                            self.trigger_picker_open = False
                        elif self.reward_picker_open:
                            self.reward_picker_open = False
                        else:
                            self.running = False
                            return None
                    elif event.key == pygame.K_RETURN:
                        if self.editing_field:
                            self.apply_edit()
                    elif self.editing_field and event.key == pygame.K_BACKSPACE:
                        self.edit_text = self.edit_text[:-1]
                    elif self.editing_field and event.key == pygame.K_DELETE:
                        self.edit_text = ""
                    elif (
                        self.editing_field
                        and event.key == pygame.K_v
                        and (event.mod & pygame.KMOD_CTRL)
                    ):
                        if pyperclip:
                            try:
                                pasted = pyperclip.paste()
                                if pasted:
                                    self.edit_text += pasted
                            except:
                                pass
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos)
                elif event.type == pygame.TEXTINPUT and self.editing_field:
                    self.edit_text += event.text

            self.draw()
            pygame.display.flip()

        return self.result if self.result is not None else self.stage_data

    def apply_edit(self):
        if self.editing_field == "stage_name":
            self.stage_data["name"] = self.edit_text
        elif self.editing_field == "stage_exp":
            try:
                self.stage_data["exp"] = int(self.edit_text)
            except ValueError:
                pass
        elif self.editing_field == "reward_id_input":
            pass
        elif self.editing_field == "dialogue_text":
            pass
        elif self.editing_field and self.editing_field.startswith("enemy_"):
            field = self.editing_field.replace("enemy_", "")
            floors = self.stage_data.get("floors", [])
            if floors and self.selected_floor_index < len(floors):
                enemies = floors[self.selected_floor_index].get("enemies", [])
                if enemies and self.selected_enemy_index < len(enemies):
                    if field in ["hp", "attack", "defense"]:
                        try:
                            enemies[self.selected_enemy_index][field] = int(
                                self.edit_text
                            )
                        except ValueError:
                            pass
                    elif field == "scale":
                        try:
                            enemies[self.selected_enemy_index][field] = float(
                                self.edit_text
                            )
                        except ValueError:
                            pass
                    else:
                        enemies[self.selected_enemy_index][field] = self.edit_text
        elif self.editing_field and self.editing_field.startswith("action_"):
            parts = self.editing_field.split("_")
            if len(parts) == 3 and parts[1] in ["value", "turns"]:
                idx = int(parts[2])
                floors = self.stage_data.get("floors", [])
                if floors and self.selected_floor_index < len(floors):
                    enemies = floors[self.selected_floor_index].get("enemies", [])
                    if enemies and self.selected_enemy_index < len(enemies):
                        actions = enemies[self.selected_enemy_index].get("actions", [])
                        if idx < len(actions):
                            try:
                                actions[idx][parts[1]] = int(self.edit_text)
                            except ValueError:
                                pass
        self.editing_field = None
        self.edit_text = ""


class DialogueEditorModal:
    def __init__(self, screen, dialogue_key=None):
        self.screen = screen
        self.running = True
        self.result = None
        self.edit_text = ""

        self.load_dialogues()

        if dialogue_key and dialogue_key in self.dialogues_data.get("dialogues", {}):
            self.dialogue_key = dialogue_key
            self.dialogue_data = self.dialogues_data["dialogues"][dialogue_key]
        else:
            self.dialogue_key = (
                f"dialogue_{len(self.dialogues_data.get('dialogues', {})) + 1}"
            )
            self.dialogue_data = {"name": "新對話", "entries": []}

        self.editing_name = False
        self.editing_entry_text = None
        self.editing_entry_name = None
        self.selected_entry_index = 0
        self._copied_entry = None

    def load_dialogues(self):
        import json
        import os

        base_path = os.path.dirname(os.path.abspath(__file__))
        dialogues_path = os.path.join(base_path, "data", "dialogues.json")
        if os.path.exists(dialogues_path):
            with open(dialogues_path, "r", encoding="utf-8") as f:
                self.dialogues_data = json.load(f)
        else:
            self.dialogues_data = {"dialogues": {}}

    def save_dialogues(self):
        import json
        import os

        base_path = os.path.dirname(os.path.abspath(__file__))
        dialogues_path = os.path.join(base_path, "data", "dialogues.json")
        with open(dialogues_path, "w", encoding="utf-8") as f:
            json.dump(self.dialogues_data, f, ensure_ascii=False, indent=2)

    def handle_click(self, pos):
        if (
            pos[0] < 50
            or pos[0] > SCREEN_WIDTH - 50
            or pos[1] < 50
            or pos[1] > SCREEN_HEIGHT - 50
        ):
            self.running = False
            return

        if pygame.Rect(SCREEN_WIDTH - 180, 60, 80, 30).collidepoint(pos):
            self.dialogues_data["dialogues"][self.dialogue_key] = self.dialogue_data
            self.save_dialogues()
            self.result = self.dialogue_key
            self.running = False
            return

        if pygame.Rect(SCREEN_WIDTH - 180, 100, 80, 30).collidepoint(pos):
            self.running = False
            return

        if pygame.Rect(150, 70, 300, 30).collidepoint(pos):
            if (
                self.editing_name
                or self.editing_entry_text is not None
                or self.editing_entry_name is not None
            ):
                self.apply_edit()
            self.editing_name = True
            self.edit_text = self.dialogue_data.get("name", "")
            return

        add_entry_btn = pygame.Rect(150, 120, 80, 30)
        if add_entry_btn.collidepoint(pos):
            entries = self.dialogue_data.get("entries", [])
            entries.append(
                {"text": "新對話", "avatar": None, "position": "left", "name": ""}
            )
            self.dialogue_data["entries"] = entries
            self.selected_entry_index = len(entries) - 1
            return

        copy_btn = pygame.Rect(240, 120, 50, 30)
        if copy_btn.collidepoint(pos):
            entries = self.dialogue_data.get("entries", [])
            if 0 <= self.selected_entry_index < len(entries):
                self._copied_entry = dict(entries[self.selected_entry_index])
                print(f"已複製: {self._copied_entry}")
            return

        paste_btn = pygame.Rect(300, 120, 50, 30)
        if paste_btn.collidepoint(pos):
            if self._copied_entry:
                entries = self.dialogue_data.get("entries", [])
                new_entry = dict(self._copied_entry)
                new_entry["text"] = new_entry.get("text", "新對話") + " (副本)"
                entries.append(new_entry)
                self.dialogue_data["entries"] = entries
                self.selected_entry_index = len(entries) - 1
                print(f"已貼上: {new_entry}")
            return

        entries = self.dialogue_data.get("entries", [])
        for i, entry in enumerate(entries):
            entry_y = 160 + i * 50

            avatar_btn = pygame.Rect(470, entry_y + 5, 70, 35)
            if avatar_btn.collidepoint(pos):
                self.show_avatar_selector()
                return

            delete_btn = pygame.Rect(580, entry_y + 10, 30, 25)
            if delete_btn.collidepoint(pos):
                entries = self.dialogue_data.get("entries", [])
                if 0 <= i < len(entries):
                    entries.pop(i)
                    self.dialogue_data["entries"] = entries
                    if self.selected_entry_index >= len(entries):
                        self.selected_entry_index = max(0, len(entries) - 1)
                return

            text_rect = pygame.Rect(160, entry_y + 5, 200, 25)
            if text_rect.collidepoint(pos):
                if (
                    self.editing_name
                    or self.editing_entry_text is not None
                    or self.editing_entry_name is not None
                ):
                    self.apply_edit()
                self.editing_entry_text = i
                self.edit_text = entry.get("text", "")
                return

            name_rect = pygame.Rect(370, entry_y + 5, 120, 25)
            if name_rect.collidepoint(pos):
                if (
                    self.editing_name
                    or self.editing_entry_text is not None
                    or self.editing_entry_name is not None
                ):
                    self.apply_edit()
                self.editing_entry_name = i
                self.edit_text = entry.get("name", "")
                return

            entry_rect = pygame.Rect(150, entry_y, 500, 45)
            if entry_rect.collidepoint(pos):
                self.selected_entry_index = i
                return

    def show_avatar_selector(self):
        self._load_avatar_images()
        self._selecting_avatar = True

    def _load_avatar_images(self):
        import os

        base_path = os.path.dirname(os.path.abspath(__file__))
        avatar_dir = os.path.join(base_path, "assets", "images", "avatar")
        if os.path.exists(avatar_dir):
            self._avatar_images = [
                f
                for f in os.listdir(avatar_dir)
                if f.endswith((".png", ".jpg", ".jpeg"))
            ]
        else:
            self._avatar_images = []

    def handle_avatar_selector_click(self, pos):
        if not hasattr(self, "_selecting_avatar") or not self._selecting_avatar:
            return False

        close_btn = pygame.Rect(SCREEN_WIDTH - 120, 60, 80, 30)
        if close_btn.collidepoint(pos):
            self._selecting_avatar = False
            return True

        if hasattr(self, "_avatar_images"):
            for i, img in enumerate(self._avatar_images):
                row = i // 4
                col = i % 4
                img_x = 100 + col * 100
                img_y = 120 + row * 100
                img_rect = pygame.Rect(img_x, img_y, 80, 80)
                if img_rect.collidepoint(pos):
                    entries = self.dialogue_data.get("entries", [])
                    if 0 <= self.selected_entry_index < len(entries):
                        entries[self.selected_entry_index]["avatar"] = f"avatar/{img}"
                        self.dialogue_data["entries"] = entries
                    self._selecting_avatar = False
                    return True
        return False

    def draw_avatar_selector(self):
        if not hasattr(self, "_selecting_avatar") or not self._selecting_avatar:
            return

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        modal_rect = pygame.Rect(50, 50, SCREEN_WIDTH - 100, SCREEN_HEIGHT - 100)
        pygame.draw.rect(self.screen, (30, 30, 40), modal_rect, border_radius=10)
        pygame.draw.rect(self.screen, (100, 100, 150), modal_rect, 2, border_radius=10)

        font = get_font(24)
        title = font.render("選擇立繪圖片", True, (255, 220, 100))
        self.screen.blit(title, (modal_rect.centerx - title.get_width() // 2, 60))

        close_btn = pygame.Rect(SCREEN_WIDTH - 120, 60, 80, 30)
        pygame.draw.rect(self.screen, (100, 50, 50), close_btn, border_radius=5)
        close_text = get_font(14).render("關閉", True, (255, 255, 255))
        self.screen.blit(close_text, (close_btn.centerx - 20, close_btn.centery - 7))

        if hasattr(self, "_avatar_images"):
            for i, img in enumerate(self._avatar_images):
                row = i // 4
                col = i % 4
                img_x = 100 + col * 100
                img_y = 120 + row * 100
                img_rect = pygame.Rect(img_x, img_y, 80, 80)
                pygame.draw.rect(self.screen, (50, 50, 60), img_rect, border_radius=3)

                try:
                    base_path = os.path.dirname(os.path.abspath(__file__))
                    img_path = os.path.join(
                        base_path, "assets", "images", "avatar", img
                    )
                    img_surf = pygame.image.load(img_path)
                    img_surf = pygame.transform.scale(img_surf, (70, 70))
                    self.screen.blit(img_surf, (img_x + 5, img_y + 5))
                except:
                    img_text = get_font(12).render(img[:10], True, (150, 150, 150))
                    self.screen.blit(img_text, (img_x + 5, img_y + 30))

    def apply_edit(self):
        if self.editing_name:
            self.dialogue_data["name"] = self.edit_text
            self.editing_name = False
        elif self.editing_entry_text is not None:
            entries = self.dialogue_data.get("entries", [])
            if 0 <= self.editing_entry_text < len(entries):
                entries[self.editing_entry_text]["text"] = self.edit_text
                self.dialogue_data["entries"] = entries
            self.editing_entry_text = None
        elif self.editing_entry_name is not None:
            entries = self.dialogue_data.get("entries", [])
            if 0 <= self.editing_entry_name < len(entries):
                entries[self.editing_entry_name]["name"] = self.edit_text
                self.dialogue_data["entries"] = entries
            self.editing_entry_name = None
        self.edit_text = ""

    def handle_file_drop(self, filepath):
        import os
        import shutil

        ext = os.path.splitext(filepath)[1].lower()
        if ext not in [".png", ".jpg", ".jpeg", ".bmp"]:
            return

        base_path = os.path.dirname(os.path.abspath(__file__))
        avatar_dir = os.path.join(base_path, "assets", "images", "avatar")
        os.makedirs(avatar_dir, exist_ok=True)

        filename = os.path.basename(filepath)
        target_filename = f"avatar_{len(os.listdir(avatar_dir)) + 1}.png"
        target_path = os.path.join(avatar_dir, target_filename)

        shutil.copy2(filepath, target_path)

        entries = self.dialogue_data.get("entries", [])
        if 0 <= self.selected_entry_index < len(entries):
            entries[self.selected_entry_index]["avatar"] = f"avatar/{target_filename}"
            self.dialogue_data["entries"] = entries
        print(f"已設定頭像: {target_path}")

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return None
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if (
                            hasattr(self, "_selecting_avatar")
                            and self._selecting_avatar
                        ):
                            self._selecting_avatar = False
                        else:
                            self.running = False
                            return None
                    elif (
                        event.key == pygame.K_v
                        and pygame.key.get_mods() & pygame.KMOD_CTRL
                    ):
                        if (
                            self.editing_name
                            or self.editing_entry_text is not None
                            or self.editing_entry_name is not None
                        ):
                            try:
                                import tkinter as tk

                                root = tk.Tk()
                                root.withdraw()
                                pasted = root.clipboard_get()
                                root.destroy()
                                if pasted:
                                    self.edit_text += pasted
                            except:
                                pass
                    elif event.key == pygame.K_RETURN:
                        if (
                            self.editing_name
                            or self.editing_entry_text is not None
                            or self.editing_entry_name is not None
                        ):
                            self.apply_edit()
                    elif event.key == pygame.K_BACKSPACE:
                        if (
                            self.editing_name
                            or self.editing_entry_text is not None
                            or self.editing_entry_name is not None
                        ):
                            self.edit_text = self.edit_text[:-1]
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if hasattr(self, "_selecting_avatar") and self._selecting_avatar:
                        if not self.handle_avatar_selector_click(event.pos):
                            self.handle_click(event.pos)
                    else:
                        self.handle_click(event.pos)
                elif event.type == pygame.TEXTINPUT:
                    if (
                        self.editing_name
                        or self.editing_entry_text is not None
                        or self.editing_entry_name is not None
                    ):
                        self.edit_text += event.text
                elif event.type == pygame.DROPFILE:
                    self.handle_file_drop(event.file)

            self.draw()
            self.draw_avatar_selector()
            pygame.display.flip()

        return self.result

    def draw(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        modal_rect = pygame.Rect(50, 50, SCREEN_WIDTH - 100, SCREEN_HEIGHT - 100)
        pygame.draw.rect(self.screen, (30, 30, 40), modal_rect, border_radius=10)
        pygame.draw.rect(self.screen, (100, 100, 150), modal_rect, 2, border_radius=10)

        font = get_font(24)
        title = font.render("對話編輯器", True, (255, 220, 100))
        self.screen.blit(title, (modal_rect.centerx - title.get_width() // 2, 65))

        save_btn = pygame.Rect(SCREEN_WIDTH - 180, 60, 80, 30)
        pygame.draw.rect(self.screen, (50, 100, 50), save_btn, border_radius=5)
        save_text = get_font(16).render("保存", True, (255, 255, 255))
        self.screen.blit(save_text, (save_btn.centerx - 20, save_btn.centery - 8))

        close_btn = pygame.Rect(SCREEN_WIDTH - 180, 100, 80, 30)
        pygame.draw.rect(self.screen, (100, 50, 50), close_btn, border_radius=5)
        close_text = get_font(16).render("取消", True, (255, 255, 255))
        self.screen.blit(close_text, (close_btn.centerx - 20, close_btn.centery - 8))

        small_font = get_font(14)

        name_label = small_font.render("對話名稱:", True, (180, 180, 180))
        self.screen.blit(name_label, (80, 75))

        name_rect = pygame.Rect(150, 70, 300, 30)
        pygame.draw.rect(self.screen, (50, 50, 60), name_rect, border_radius=3)
        if self.editing_name:
            display = self.edit_text + "▌"
        else:
            display = self.dialogue_data.get("name", "新對話")
        name_text = get_font(16).render(display, True, (255, 255, 255))
        self.screen.blit(name_text, (name_rect.x + 5, name_rect.y + 5))

        entries_label = small_font.render("對話条目:", True, (180, 180, 180))
        self.screen.blit(entries_label, (80, 125))

        add_entry_btn = pygame.Rect(150, 120, 80, 30)
        pygame.draw.rect(self.screen, (60, 80, 120), add_entry_btn, border_radius=3)
        add_text = small_font.render("+ 新增", True, (255, 255, 255))
        self.screen.blit(
            add_text, (add_entry_btn.centerx - 20, add_entry_btn.centery - 7)
        )

        copy_btn = pygame.Rect(240, 120, 50, 30)
        pygame.draw.rect(self.screen, (60, 80, 120), copy_btn, border_radius=3)
        copy_text = small_font.render("複製", True, (255, 255, 255))
        self.screen.blit(copy_text, (copy_btn.centerx - 20, copy_btn.centery - 7))

        paste_btn = pygame.Rect(300, 120, 50, 30)
        pygame.draw.rect(self.screen, (60, 80, 120), paste_btn, border_radius=3)
        paste_text = small_font.render("貼上", True, (255, 255, 255))
        self.screen.blit(paste_text, (paste_btn.centerx - 20, paste_btn.centery - 7))

        entries = self.dialogue_data.get("entries", [])
        for i, entry in enumerate(entries):
            entry_y = 160 + i * 50
            entry_rect = pygame.Rect(150, entry_y, 500, 45)
            bg_color = (50, 80, 120) if i == self.selected_entry_index else (40, 50, 60)
            pygame.draw.rect(self.screen, bg_color, entry_rect, border_radius=3)

            text_rect = pygame.Rect(160, entry_y + 5, 200, 25)
            pygame.draw.rect(self.screen, (50, 50, 60), text_rect, border_radius=2)
            if self.editing_entry_text == i:
                display = self.edit_text + "▌"
            else:
                display = entry.get("text", "")
            text_surf = small_font.render(display[:25], True, (255, 255, 255))
            self.screen.blit(text_surf, (text_rect.x + 3, text_rect.y + 3))

            name_rect = pygame.Rect(370, entry_y + 5, 120, 25)
            pygame.draw.rect(self.screen, (50, 50, 60), name_rect, border_radius=2)
            name_display = entry.get("name", "")
            if not name_display:
                name_display = "名稱"
            if self.editing_entry_name == i:
                name_display = self.edit_text + "▌"
            name_surf = small_font.render(
                name_display[:15],
                True,
                (255, 255, 255) if self.editing_entry_name == i else (180, 180, 180),
            )
            self.screen.blit(name_surf, (name_rect.x + 3, name_rect.y + 3))

            avatar_btn = pygame.Rect(500, entry_y + 5, 70, 35)
            pygame.draw.rect(self.screen, (60, 60, 70), avatar_btn, border_radius=3)
            avatar_path = entry.get("avatar")
            if avatar_path:
                base_path = os.path.dirname(os.path.abspath(__file__))
                full_path = os.path.join(
                    base_path, "assets", "images", avatar_path.replace("/", os.sep)
                )
                if os.path.exists(full_path):
                    try:
                        img = pygame.image.load(full_path)
                        img = pygame.transform.scale(img, (60, 30))
                        self.screen.blit(img, (475, entry_y + 7))
                    except:
                        avatar_hint = small_font.render("圖片", True, (150, 150, 150))
                        self.screen.blit(
                            avatar_hint,
                            (avatar_btn.centerx - 15, avatar_btn.centery - 7),
                        )
                else:
                    avatar_hint = small_font.render("無", True, (150, 150, 150))
                    self.screen.blit(
                        avatar_hint, (avatar_btn.centerx - 8, avatar_btn.centery - 7)
                    )
            else:
                avatar_hint = small_font.render("選擇", True, (120, 120, 120))
                self.screen.blit(
                    avatar_hint, (avatar_btn.centerx - 15, avatar_btn.centery - 7)
                )

            delete_btn = pygame.Rect(580, entry_y + 10, 30, 25)
            pygame.draw.rect(self.screen, (120, 50, 50), delete_btn, border_radius=3)
            del_text = small_font.render("X", True, (255, 255, 255))
            self.screen.blit(del_text, (delete_btn.centerx - 5, delete_btn.centery - 6))

        hint = small_font.render("拖曳圖片到對話框設定角色圖片", True, (120, 120, 120))
        self.screen.blit(hint, (150, SCREEN_HEIGHT - 80))


class DevTool:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("開發者工具")
        self.clock = pygame.time.Clock()

        self.pets_data = []
        self.load_pets()

        self.stages_data = []
        self.load_stages()

        self.selected_index = 0
        self.scroll_offset = 0
        self.editing_field = None
        self.edit_text = ""

        self.tabs = [
            "角色列表",
            "編輯角色",
            "新增角色",
            "圖片管理",
            "關卡編輯",
            "對話編輯",
            "寶珠Skin",
        ]
        self.current_tab = 0

        base_path = os.path.dirname(os.path.abspath(__file__))
        self.image_dir = os.path.join(base_path, "assets", "images")

        self.field_groups = {
            "basic": [
                ("id", "ID", 120, "int"),
                ("name", "名稱", 160, "str"),
                ("attribute", "屬性", 200, "str"),
                ("race", "種族", 240, "str"),
                ("rarity", "稀有度", 280, "int"),
                ("hp", "HP", 320, "int"),
                ("attack", "攻擊", 360, "int"),
                ("recovery", "回覆", 400, "int"),
            ],
            "desc": [
                ("description", "描述", 440, "str"),
            ],
        }

        self.attr_options = ["火", "水", "木", "光", "暗"]
        self.race_options = [
            "神",
            "人",
            "獸",
            "龍",
            "惡魔",
            "機械",
            "平衡",
            "柯洛尼",
            "研造",
            "稀有",
            "妨害",
            "球",
            "轉換",
        ]
        self.rarity_options = [1, 2, 3, 4, 5, 6]

        self.skill_editor = None
        self.awakening_editor = None
        self.stage_editor = None
        self.dialogue_editor = None
        self.image_cropper = None
        self.selected_stage_index = 0
        self.stage_scroll_offset = 0

    def load_pets(self):
        base_path = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(base_path, "data", "pets.json")
        with open(json_path, "r", encoding="utf-8") as f:
            self.pets_data = json.load(f)["pets"]

    def load_stages(self):
        import json
        import os

        base_path = os.path.dirname(os.path.abspath(__file__))
        stages_path = os.path.join(base_path, "data", "stages.json")
        if os.path.exists(stages_path):
            with open(stages_path, "r", encoding="utf-8") as f:
                self.stages_data = json.load(f)
        else:
            self.stages_data = []

    def save_stages(self):
        import json
        import os

        base_path = os.path.dirname(os.path.abspath(__file__))
        stages_path = os.path.join(base_path, "data", "stages.json")
        with open(stages_path, "w", encoding="utf-8") as f:
            json.dump(self.stages_data, f, ensure_ascii=False, indent=2)
        print("已保存到 stages.json")

    def save_pets(self):
        base_path = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(base_path, "data", "pets.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump({"pets": self.pets_data}, f, ensure_ascii=False, indent=2)
        print("已保存到 pets.json")

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.editing_field = None
                        self.edit_text = ""
                        self.add_dialogue_mode = False
                        if self.skill_editor:
                            self.skill_editor = None
                        if self.awakening_editor:
                            self.awakening_editor = None
                    elif event.key == pygame.K_TAB:
                        if self.editing_field:
                            self.apply_edit()
                        self.current_tab = (self.current_tab + 1) % len(self.tabs)
                    elif (
                        event.key == pygame.K_s
                        and pygame.key.get_mods() & pygame.KMOD_CTRL
                    ):
                        self.save_pets()
                    elif event.key == pygame.K_UP:
                        if self.editing_field:
                            self.apply_edit()
                        if self.current_tab == 0:
                            self.selected_index = max(0, self.selected_index - 1)
                            if self.selected_index < self.scroll_offset:
                                self.scroll_offset = self.selected_index
                    elif event.key == pygame.K_DOWN:
                        if self.editing_field:
                            self.apply_edit()
                        if self.current_tab == 0:
                            self.selected_index = min(
                                len(self.pets_data) - 1, self.selected_index + 1
                            )
                            if (
                                self.selected_index
                                >= self.scroll_offset + self.get_visible_count()
                            ):
                                self.scroll_offset = (
                                    self.selected_index - self.get_visible_count() + 1
                                )
                    elif event.key == pygame.K_DELETE:
                        if (
                            not self.editing_field
                            and self.current_tab == 0
                            and self.pets_data
                        ):
                            self.delete_current_pet()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.handle_click(event.pos)
                    elif event.button == 4:
                        self.scroll(-1)
                    elif event.button == 5:
                        self.scroll(1)
                elif event.type == pygame.DROPFILE:
                    self.handle_file_drop(event.file)
                elif event.type == pygame.TEXTINPUT and self.editing_field:
                    self.edit_text += event.text
                if event.type == pygame.KEYDOWN and self.editing_field:
                    log(
                        f"DEBUG: KEYDOWN editing_field={self.editing_field}, key={event.key}"
                    )
                    if event.key == pygame.K_BACKSPACE:
                        self.edit_text = self.edit_text[:-1]
                        log(f"DEBUG: after backspace edit_text={self.edit_text}")
                    elif event.key == pygame.K_DELETE:
                        self.edit_text = ""
                        log(f"DEBUG: after delete edit_text={self.edit_text}")
                    elif event.key == pygame.K_RETURN:
                        self.apply_edit()
                    elif event.key == pygame.K_LEFT:
                        pass
                    elif event.key == pygame.K_RIGHT:
                        pass

            if self.skill_editor:
                result = self.skill_editor.run()
                if result is not None:
                    pet = self.pets_data[self.selected_index]
                    if self.skill_editor.skill_type == "leader_skill":
                        pet["leader_skill"] = result
                    else:
                        pet["active_skill"] = result
                self.skill_editor = None
                continue

            if self.awakening_editor:
                result = self.awakening_editor.run()
                if result is not None:
                    pet = self.pets_data[self.selected_index]
                    pet["awakenings"] = result
                self.awakening_editor = None
                continue

            if self.stage_editor:
                result = self.stage_editor.run()
                if result is not None:
                    if self.selected_stage_index < len(self.stages_data):
                        self.stages_data[self.selected_stage_index] = result
                    else:
                        self.stages_data.append(result)
                    self.save_stages()
                self.stage_editor = None
                continue

            if self.dialogue_editor:
                result = self.dialogue_editor.run()
                if result is not None:
                    # 對話已保存
                    pass
                self.dialogue_editor = None
                continue

            if self.image_cropper:
                result = self.image_cropper.run()
                if result:
                    self.save_pets()
                self.image_cropper = None
                continue

            self.draw()
            pygame.display.flip()

    def delete_current_pet(self):
        if not self.pets_data or self.selected_index >= len(self.pets_data):
            return
        pet = self.pets_data[self.selected_index]
        pet_id = pet["id"]
        pet_name = pet["name"]
        del self.pets_data[self.selected_index]
        if self.selected_index >= len(self.pets_data):
            self.selected_index = max(0, len(self.pets_data) - 1)
        self.save_pets()
        print(f"已刪除角色 #{pet_id} {pet_name}")

    def scroll(self, delta):
        max_offset = max(0, len(self.pets_data) - self.get_visible_count())
        self.scroll_offset = max(0, min(max_offset, self.scroll_offset + delta))

    def get_visible_count(self):
        return (SCREEN_HEIGHT - 180) // 50

    def handle_click(self, pos):
        if pos[1] < 50 or pos[1] > SCREEN_HEIGHT - 60:
            return

        if pos[1] < 90:
            for i, tab in enumerate(self.tabs):
                rect = pygame.Rect(50 + i * 130, 50, 120, 40)
                if rect.collidepoint(pos):
                    if self.editing_field:
                        self.apply_edit()
                    self.current_tab = i
                    self.editing_field = None
                    return
            return

        if self.current_tab == 0:
            self.handle_list_click(pos)
        elif self.current_tab == 1:
            self.handle_edit_click(pos)
        elif self.current_tab == 2:
            self.handle_add_click(pos)
        elif self.current_tab == 3:
            self.handle_image_click(pos)
        elif self.current_tab == 4:
            self.handle_stage_click(pos)
        elif self.current_tab == 5:
            self.handle_dialogue_click(pos)
        elif self.current_tab == 6:
            if hasattr(self, "_orb_skin_select_mode") and self._orb_skin_select_mode:
                self.handle_orb_skin_drop_selector_click(pos)
            else:
                self.handle_orb_skin_click(pos)

    def handle_list_click(self, pos):
        y = 140
        visible = self.get_visible_count()
        for i in range(visible):
            idx = i + self.scroll_offset
            if idx >= len(self.pets_data):
                break

            rect = pygame.Rect(45, y + i * 50 - 5, SCREEN_WIDTH - 90, 45)
            if rect.collidepoint(pos):
                self.selected_index = idx
                self.current_tab = 1
                return

    def handle_edit_click(self, pos):
        pet = self.pets_data[self.selected_index]

        for group in self.field_groups.values():
            for field, label, y_pos, field_type in group:
                if field_type in ["str", "int"]:
                    rect = pygame.Rect(200, y_pos, 350, 35)
                    if rect.collidepoint(pos):
                        if self.editing_field and self.editing_field != field:
                            self.apply_edit()
                        self.editing_field = field
                        self.edit_text = str(pet.get(field, ""))
                        return

        if pygame.Rect(50, 160, 140, 35).collidepoint(pos):
            current = pet.get("attribute", "火")
            idx = (
                self.attr_options.index(current) if current in self.attr_options else 0
            )
            pet["attribute"] = self.attr_options[(idx + 1) % len(self.attr_options)]
            return

        if pygame.Rect(50, 200, 140, 35).collidepoint(pos):
            current = pet.get("race", "神")
            idx = (
                self.race_options.index(current) if current in self.race_options else 0
            )
            pet["race"] = self.race_options[(idx + 1) % len(self.race_options)]
            return

        if pygame.Rect(50, 240, 140, 35).collidepoint(pos):
            current = pet.get("rarity", 5)
            idx = (
                self.rarity_options.index(current)
                if current in self.rarity_options
                else 0
            )
            pet["rarity"] = self.rarity_options[(idx + 1) % len(self.rarity_options)]
            return

        if pygame.Rect(50, 600, 200, 40).collidepoint(pos):
            self.save_pets()
            return

        leader_rect = pygame.Rect(550, 480, 80, 30)
        if leader_rect.collidepoint(pos):
            self.skill_editor = SkillEditorModal(
                self.screen, pet.get("leader_skill"), "leader_skill"
            )
            return

        active_rect = pygame.Rect(550, 520, 80, 30)
        if active_rect.collidepoint(pos):
            self.skill_editor = SkillEditorModal(
                self.screen, pet.get("active_skill"), "active_skill"
            )
            return

        awake_rect = pygame.Rect(550, 560, 80, 30)
        if awake_rect.collidepoint(pos):
            self.awakening_editor = AwakeningEditorModal(
                self.screen, pet.get("awakenings", [])
            )
            return

    def handle_add_click(self, pos):
        if pygame.Rect(50, 150, 200, 40).collidepoint(pos):
            new_id = max([p["id"] for p in self.pets_data], default=0) + 1
            new_pet = {
                "id": new_id,
                "name": "新角色",
                "attribute": "火",
                "race": "神",
                "rarity": 5,
                "hp": 1000,
                "attack": 500,
                "recovery": 100,
                "leader_skill": None,
                "active_skill": None,
                "awakenings": [],
                "description": "",
            }
            self.pets_data.append(new_pet)
            self.selected_index = len(self.pets_data) - 1
            self.current_tab = 1
            self.save_pets()

    def handle_image_click(self, pos):
        if not self.pets_data:
            return

        pet = self.pets_data[self.selected_index]
        pet_id = str(pet["id"])

        head_rect = pygame.Rect(50, 220, 100, 80)
        if head_rect.collidepoint(pos):
            base_path = os.path.dirname(os.path.abspath(__file__))
            head_path = os.path.join(
                base_path, "assets", "images", "head", f"{pet_id}.png"
            )
            if os.path.exists(head_path):
                self.image_cropper = ImageCropModal(
                    self.screen, head_path, pet_id, "head"
                )
            return

        full_rect = pygame.Rect(50, 340, 100, 80)
        if full_rect.collidepoint(pos):
            base_path = os.path.dirname(os.path.abspath(__file__))
            full_path = os.path.join(
                base_path, "assets", "images", "full", f"{pet_id}.png"
            )
            if os.path.exists(full_path):
                self.open_image_folder("full")
            return

        folder_y = 450
        head_folder_btn = pygame.Rect(50, folder_y, 100, 30)
        if head_folder_btn.collidepoint(pos):
            self.open_image_folder("head")
            return

        full_folder_btn = pygame.Rect(160, folder_y, 100, 30)
        if full_folder_btn.collidepoint(pos):
            self.open_image_folder("full")
            return

    def open_image_folder(self, img_type):
        base_path = os.path.dirname(os.path.abspath(__file__))
        if img_type == "head":
            folder = os.path.join(base_path, "assets", "images", "head")
        else:
            folder = os.path.join(base_path, "assets", "images", "full")

        if os.path.exists(folder):
            os.startfile(folder)

    def handle_file_drop(self, filepath):
        if self.current_tab == 6:
            self.handle_orb_skin_file_drop(filepath)
            return

        if self.current_tab == 4 and self.stage_editor:
            return
        elif self.current_tab != 3:
            return

        if not self.pets_data:
            return

        pet = self.pets_data[self.selected_index]
        pet_id = str(pet["id"])

        base_path = os.path.dirname(os.path.abspath(__file__))

        ext = os.path.splitext(filepath)[1].lower()
        if ext not in [".png", ".jpg", ".jpeg", ".bmp"]:
            print(f"不支援的圖片格式: {ext}")
            return

        filename = os.path.basename(filepath)
        name_without_ext = os.path.splitext(filename)[0]

        head_dir = os.path.join(base_path, "assets", "images", "head")
        full_dir = os.path.join(base_path, "assets", "images", "full")

        os.makedirs(head_dir, exist_ok=True)
        os.makedirs(full_dir, exist_ok=True)

        is_head = False

        if name_without_ext == pet_id:
            is_head = True
        elif name_without_ext == f"full_{pet_id}":
            is_head = False
        elif name_without_ext.startswith("full"):
            is_head = False
        elif name_without_ext in ["head", "icon", "avatar"]:
            is_head = True
        elif name_without_ext in ["full", "body"]:
            is_head = False
        else:
            head_exists = os.path.exists(os.path.join(head_dir, f"{pet_id}.png"))
            full_exists = os.path.exists(os.path.join(full_dir, f"{pet_id}.png"))

            if not head_exists:
                is_head = True
            elif not full_exists:
                is_head = False
            else:
                is_head = False

        if is_head:
            self.image_cropper = ImageCropModal(self.screen, filepath, pet_id, "head")
        else:
            target_path = os.path.join(full_dir, f"{pet_id}.png")
            import shutil

            shutil.copy2(filepath, target_path)
            print(f"已將圖片複製到 全身圖: {target_path}")

    def apply_edit(self):
        if not self.editing_field:
            return

        if (
            self.editing_field == "orb_skin_path"
            and hasattr(self, "_editing_orb_skin_key")
            and hasattr(self, "_editing_orb_type")
        ):
            import json
            import os

            base_path = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(base_path, "data", "orb_skins.json")

            if os.path.exists(config_path):
                with open(config_path, "r", encoding="utf-8") as f:
                    skin_config = json.load(f)

                if self._editing_orb_skin_key in skin_config.get("skins", {}):
                    skin_config["skins"][self._editing_orb_skin_key][
                        self._editing_orb_type
                    ] = self.edit_text

                    with open(config_path, "w", encoding="utf-8") as f:
                        json.dump(skin_config, f, ensure_ascii=False, indent=2)
                    print(
                        f"已設定 {self._editing_orb_skin_key} - {self._editing_orb_type}: {self.edit_text}"
                    )

            self.editing_field = None
            self.edit_text = ""
            self._editing_orb_skin_key = None
            self._editing_orb_type = None
            return

        if self.editing_field == "orb_skin_name":
            import json
            import os

            base_path = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(base_path, "data", "orb_skins.json")

            if os.path.exists(config_path):
                with open(config_path, "r", encoding="utf-8") as f:
                    skin_config = json.load(f)

                if hasattr(
                    self, "_editing_orb_skin_key"
                ) and self._editing_orb_skin_key in skin_config.get("skins", {}):
                    skin_config["skins"][self._editing_orb_skin_key]["name"] = (
                        self.edit_text
                    )
                    with open(config_path, "w", encoding="utf-8") as f:
                        json.dump(skin_config, f, ensure_ascii=False, indent=2)
                    print(f"已設定 skin 名稱: {self.edit_text}")

            self.editing_field = None
            self.edit_text = ""
            return

        pet = self.pets_data[self.selected_index]

        field_type = "str"
        for group in self.field_groups.values():
            for f, l, y, t in group:
                if f == self.editing_field:
                    field_type = t
                    break

        if field_type == "int":
            try:
                pet[self.editing_field] = int(self.edit_text)
            except ValueError:
                pass
        else:
            pet[self.editing_field] = self.edit_text

        self.editing_field = None
        self.edit_text = ""

    def draw(self):
        self.screen.fill((25, 25, 35))

        title_font = get_font(28)
        title = title_font.render("開發者工具 - 角色管理器", True, (255, 220, 100))
        self.screen.blit(title, (50, 10))

        for i, tab in enumerate(self.tabs):
            color = (60, 120, 200) if i == self.current_tab else (50, 50, 60)
            rect = pygame.Rect(50 + i * 130, 50, 120, 40)
            pygame.draw.rect(self.screen, color, rect, border_radius=5)
            font = get_font(18)
            text = font.render(tab, True, (255, 255, 255))
            text_rect = text.get_rect(center=rect.center)
            self.screen.blit(text, text_rect)

        if self.current_tab == 0:
            self.draw_list()
        elif self.current_tab == 1:
            self.draw_edit()
        elif self.current_tab == 2:
            self.draw_add()
        elif self.current_tab == 3:
            self.draw_image_manager()
        elif self.current_tab == 4:
            self.draw_stage_editor()
        elif self.current_tab == 5:
            self.draw_dialogue_tab()
        elif self.current_tab == 6:
            self.draw_orb_skin_tab()

        if hasattr(self, "_orb_skin_select_mode") and self._orb_skin_select_mode:
            self.draw_orb_skin_drop_selector()

        if self.editing_field:
            input_display_rect = pygame.Rect(
                50, SCREEN_HEIGHT - 80, SCREEN_WIDTH - 100, 40
            )
            pygame.draw.rect(
                self.screen, (40, 40, 50), input_display_rect, border_radius=5
            )
            pygame.draw.rect(
                self.screen, (100, 100, 150), input_display_rect, 2, border_radius=5
            )

            input_label = get_font(14).render("輸入: ", True, (180, 180, 180))
            self.screen.blit(input_label, (60, SCREEN_HEIGHT - 72))

            input_text = get_font(16).render(
                self.edit_text + "▌", True, (255, 255, 255)
            )
            self.screen.blit(input_text, (120, SCREEN_HEIGHT - 70))

            hint = get_font(12).render("Enter 確認 | ESC 取消", True, (120, 120, 120))
            self.screen.blit(hint, (SCREEN_WIDTH - 200, SCREEN_HEIGHT - 70))
        elif self.current_tab == 6:
            drop_hint = get_font(14).render(
                "拖入圖片檔案自動設定路徑", True, (100, 200, 100)
            )
            self.screen.blit(drop_hint, (50, SCREEN_HEIGHT - 25))
        elif self.editing_field:
            hint_font = get_font(14)
            hint = hint_font.render(
                "Tab: 切換 | ↑↓: 選擇 | 滾輪: 滾動 | Del: 刪除 | Ctrl+S: 保存 | ESC: 取消",
                True,
                (120, 120, 120),
            )
            self.screen.blit(hint, (50, SCREEN_HEIGHT - 25))
        else:
            hint_font = get_font(14)
            hint = hint_font.render(
                "Tab: 切換 | ↑↓: 選擇 | 滾輪: 滾動 | Del: 刪除 | Ctrl+S: 保存 | ESC: 取消",
                True,
                (120, 120, 120),
            )
            self.screen.blit(hint, (50, SCREEN_HEIGHT - 25))

    def draw_list(self):
        font = get_font(18)

        header = font.render(
            "ID   名稱        屬性  種族   稀有 HP      攻擊    回覆",
            True,
            (180, 180, 180),
        )
        self.screen.blit(header, (50, 120))
        pygame.draw.line(
            self.screen, (80, 80, 80), (50, 145), (SCREEN_WIDTH - 50, 145), 1
        )

        visible = self.get_visible_count()
        for i in range(visible):
            idx = i + self.scroll_offset
            if idx >= len(self.pets_data):
                break

            pet = self.pets_data[idx]
            y = 150 + i * 50

            bg_color = (40, 70, 120) if idx == self.selected_index else (35, 35, 45)
            pygame.draw.rect(
                self.screen, bg_color, (45, y, SCREEN_WIDTH - 90, 42), border_radius=3
            )

            color = (255, 255, 255) if idx == self.selected_index else (200, 200, 200)
            text = f"{pet['id']:<4} {pet['name']:<10} {pet['attribute']:<4} {pet['race']:<6} {pet['rarity']:<2} {pet['hp']:<7} {pet['attack']:<7} {pet['recovery']:<5}"
            line = font.render(text, True, color)
            self.screen.blit(line, (55, y + 10))

    def draw_edit(self):
        if not self.pets_data:
            return

        pet = self.pets_data[self.selected_index]
        font = get_font(22)
        small_font = get_font(16)

        title = font.render(
            f"編輯角色 #{pet['id']} - {pet['name']}", True, (255, 200, 80)
        )
        self.screen.blit(title, (50, 110))

        for field, label, y, field_type in self.field_groups["basic"]:
            label_text = font.render(f"{label}:", True, (180, 180, 180))
            self.screen.blit(label_text, (50, y))

            if self.editing_field == field:
                display = self.edit_text + "▌"
            else:
                display = str(pet.get(field, ""))

            value_color = (
                (100, 255, 100) if field in ["id", "rarity"] else (255, 255, 255)
            )
            value_text = font.render(display, True, value_color)
            self.screen.blit(value_text, (200, y))

            if field == "attribute":
                hint = small_font.render("← 點擊切換", True, (100, 150, 100))
                self.screen.blit(hint, (560, y + 5))
            elif field == "race":
                hint = small_font.render("← 點擊切換", True, (100, 150, 100))
                self.screen.blit(hint, (560, y + 5))
            elif field == "rarity":
                hint = small_font.render("← 點擊切換", True, (100, 150, 100))
                self.screen.blit(hint, (560, y + 5))

        for field, label, y, field_type in self.field_groups["desc"]:
            label_text = font.render(f"{label}:", True, (180, 180, 180))
            self.screen.blit(label_text, (50, y))

            if self.editing_field == field:
                display = self.edit_text + "▌"
            else:
                display = str(pet.get(field, ""))
                if len(display) > 40:
                    display = display[:40] + "..."

            value_text = font.render(display, True, (255, 255, 255))
            self.screen.blit(value_text, (200, y))

        skills = [
            ("leader_skill", "隊長技能", 480),
            ("active_skill", "主動技能", 520),
            ("awakenings", "覺醒技能", 560),
        ]

        for field, label, y in skills:
            label_text = font.render(f"{label}:", True, (180, 180, 180))
            self.screen.blit(label_text, (50, y))

            data = pet.get(field)
            if field == "awakenings":
                display = ", ".join(data) if data else "無"
            elif data:
                display = json.dumps(data, ensure_ascii=False)
                if len(display) > 40:
                    display = display[:40] + "..."
            else:
                display = "None"

            color = (150, 200, 255) if self.editing_field == field else (200, 200, 200)
            value_text = small_font.render(display, True, color)
            self.screen.blit(value_text, (200, y + 3))

            edit_rect = pygame.Rect(550, y, 80, 30)
            pygame.draw.rect(self.screen, (60, 60, 80), edit_rect, border_radius=3)
            edit_text = small_font.render("編輯", True, (255, 255, 255))
            self.screen.blit(edit_text, (edit_rect.centerx - 15, edit_rect.centery - 8))

        save_rect = pygame.Rect(50, 600, 200, 40)
        pygame.draw.rect(self.screen, (50, 100, 50), save_rect, border_radius=5)
        save_text = font.render("保存修改", True, (255, 255, 255))
        self.screen.blit(save_text, (save_rect.centerx - 45, save_rect.centery - 12))

    def draw_add(self):
        font = get_font(22)
        title = font.render("新增角色", True, (255, 200, 80))
        self.screen.blit(title, (50, 110))

        btn_rect = pygame.Rect(50, 160, 200, 45)
        pygame.draw.rect(self.screen, (50, 100, 50), btn_rect, border_radius=5)
        btn_text = font.render("創建新角色", True, (255, 255, 255))
        self.screen.blit(btn_text, (btn_rect.centerx - 50, btn_rect.centery - 12))

        info = font.render(f"目前角色數: {len(self.pets_data)}", True, (180, 180, 180))
        self.screen.blit(info, (50, 230))

    def draw_image_manager(self):
        font = get_font(22)
        small_font = get_font(16)

        title = font.render("圖片管理", True, (255, 200, 80))
        self.screen.blit(title, (50, 110))

        current_pet = None
        if self.pets_data:
            current_pet = self.pets_data[self.selected_index]
            pet_info = font.render(
                f"當前角色: #{current_pet['id']} {current_pet['name']}",
                True,
                (200, 200, 200),
            )
            self.screen.blit(pet_info, (50, 150))

        head_label = small_font.render("頭像 (head)", True, (180, 180, 180))
        self.screen.blit(head_label, (50, 200))

        head_rect = pygame.Rect(50, 220, 100, 80)
        pygame.draw.rect(self.screen, (60, 60, 70), head_rect, border_radius=5)
        pygame.draw.rect(self.screen, (100, 100, 150), head_rect, 2, border_radius=5)

        if current_pet:
            head_path = os.path.join(self.image_dir, "head", f"{current_pet['id']}.png")
            if os.path.exists(head_path):
                try:
                    head_img = pygame.image.load(head_path)
                    head_img = pygame.transform.scale(head_img, (80, 70))
                    self.screen.blit(head_img, (60, 225))
                except:
                    drop_text = small_font.render("無法載入", True, (150, 150, 150))
                    self.screen.blit(
                        drop_text, (head_rect.centerx - 30, head_rect.centery - 8)
                    )
            else:
                drop_text = small_font.render("拖曳圖片", True, (120, 120, 120))
                self.screen.blit(
                    drop_text, (head_rect.centerx - 35, head_rect.centery - 8)
                )
                hint = small_font.render("到這裡", True, (100, 100, 100))
                self.screen.blit(hint, (head_rect.centerx - 25, head_rect.centery + 12))

        full_label = small_font.render("全身圖 (full)", True, (180, 180, 180))
        self.screen.blit(full_label, (50, 320))

        full_rect = pygame.Rect(50, 340, 100, 80)
        pygame.draw.rect(self.screen, (60, 60, 70), full_rect, border_radius=5)
        pygame.draw.rect(self.screen, (100, 100, 150), full_rect, 2, border_radius=5)

        if current_pet:
            full_path = os.path.join(self.image_dir, "full", f"{current_pet['id']}.png")
            if os.path.exists(full_path):
                try:
                    full_img = pygame.image.load(full_path)
                    full_img = pygame.transform.scale(full_img, (80, 70))
                    self.screen.blit(full_img, (60, 345))
                except:
                    drop_text = small_font.render("無法載入", True, (150, 150, 150))
                    self.screen.blit(
                        drop_text, (full_rect.centerx - 30, full_rect.centery - 8)
                    )
            else:
                drop_text = small_font.render("拖曳圖片", True, (120, 120, 120))
                self.screen.blit(
                    drop_text, (full_rect.centerx - 35, full_rect.centery - 8)
                )
                hint = small_font.render("到這裡", True, (100, 100, 100))
                self.screen.blit(hint, (full_rect.centerx - 25, full_rect.centery + 12))

        folder_y = 450

        head_folder_btn = pygame.Rect(50, folder_y, 100, 30)
        pygame.draw.rect(self.screen, (70, 70, 90), head_folder_btn, border_radius=3)
        folder_text = small_font.render("開啟資料夾", True, (255, 255, 255))
        self.screen.blit(
            folder_text, (head_folder_btn.centerx - 35, head_folder_btn.centery - 8)
        )

        full_folder_btn = pygame.Rect(160, folder_y, 100, 30)
        pygame.draw.rect(self.screen, (70, 70, 90), full_folder_btn, border_radius=3)
        self.screen.blit(
            folder_text, (full_folder_btn.centerx - 35, full_folder_btn.centery - 8)
        )

        drop_hint = small_font.render(
            "拖曳圖片檔案到視窗中自動注入", True, (120, 180, 120)
        )
        self.screen.blit(drop_hint, (50, folder_y + 50))

        filename_hint = small_font.render(
            "檔名可用: id.png, full_id.png, head.png, full.png", True, (100, 100, 100)
        )
        self.screen.blit(filename_hint, (50, folder_y + 80))

    def handle_stage_click(self, pos):
        if pos[1] < 110 or pos[1] > SCREEN_HEIGHT - 60:
            return

        max_stage_y = 120 + len(self.stages_data) * 50
        if pos[1] < max_stage_y:
            for i in range(len(self.stages_data)):
                stage_y = 120 + i * 50
                if pygame.Rect(50, stage_y, 300, 45).collidepoint(pos):
                    self.selected_stage_index = i
                    return

        add_btn_y = 120 + len(self.stages_data) * 50
        add_btn_rect = pygame.Rect(50, add_btn_y, 150, 35)
        if add_btn_rect.collidepoint(pos):
            new_stage = {
                "name": f"新關卡 {len(self.stages_data) + 1}",
                "dialogue": [],
                "floors": [{"floor_num": 1, "dialogue": [], "enemies": []}],
            }
            self.stages_data.append(new_stage)
            self.selected_stage_index = len(self.stages_data) - 1
            self.save_stages()
            return

        edit_btn = pygame.Rect(380, 110, 80, 35)
        if edit_btn.collidepoint(pos):
            if self.selected_stage_index < len(self.stages_data):
                self.stage_editor = StageEditorModal(
                    self.screen, self.stages_data[self.selected_stage_index]
                )
            else:
                self.stage_editor = StageEditorModal(self.screen, None)
            return

        delete_btn = pygame.Rect(380, 150, 80, 35)
        if delete_btn.collidepoint(pos):
            if 0 <= self.selected_stage_index < len(self.stages_data):
                del self.stages_data[self.selected_stage_index]
                if self.selected_stage_index >= len(self.stages_data):
                    self.selected_stage_index = max(0, len(self.stages_data) - 1)
                self.save_stages()
            return

    def draw_stage_editor(self):
        font = get_font(22)
        small_font = get_font(14)

        title = font.render("關卡管理", True, (255, 200, 80))
        self.screen.blit(title, (50, 110))

        if not self.stages_data:
            empty_text = small_font.render(
                "尚未有関卡，點擊下方按鈕新增", True, (150, 150, 150)
            )
            self.screen.blit(empty_text, (50, 160))

        for i, stage in enumerate(self.stages_data):
            stage_y = 120 + i * 50
            bg_color = (40, 70, 120) if i == self.selected_stage_index else (35, 35, 45)
            stage_rect = pygame.Rect(50, stage_y, 300, 45)
            pygame.draw.rect(self.screen, bg_color, stage_rect, border_radius=3)

            stage_name = (
                stage.get("name", "新關卡") if isinstance(stage, dict) else "新關卡"
            )
            stage_text = get_font(16).render(stage_name, True, (255, 255, 255))
            self.screen.blit(stage_text, (60, stage_y + 12))

            floor_count = len(stage.get("floors", [])) if isinstance(stage, dict) else 1
            floor_text = small_font.render(f"{floor_count} 層", True, (180, 180, 180))
            self.screen.blit(floor_text, (200, stage_y + 15))

        add_btn_y = 120 + len(self.stages_data) * 50
        add_btn = pygame.Rect(50, add_btn_y, 150, 35)
        pygame.draw.rect(self.screen, (50, 80, 50), add_btn, border_radius=3)
        add_text = small_font.render("+ 新增關卡", True, (255, 255, 255))
        self.screen.blit(add_text, (add_btn.centerx - 35, add_btn.centery - 7))

        edit_btn = pygame.Rect(380, 110, 80, 35)
        pygame.draw.rect(self.screen, (60, 80, 120), edit_btn, border_radius=3)
        edit_text = small_font.render("編輯", True, (255, 255, 255))
        self.screen.blit(edit_text, (edit_btn.centerx - 20, edit_btn.centery - 7))

        delete_btn = pygame.Rect(380, 150, 80, 35)
        pygame.draw.rect(self.screen, (120, 50, 50), delete_btn, border_radius=3)
        delete_text = small_font.render("刪除", True, (255, 255, 255))
        self.screen.blit(delete_text, (delete_btn.centerx - 20, delete_btn.centery - 7))

        if 0 <= self.selected_stage_index < len(self.stages_data):
            stage = self.stages_data[self.selected_stage_index]
            detail_panel = pygame.Rect(500, 110, 400, 400)
            pygame.draw.rect(self.screen, (35, 35, 45), detail_panel, border_radius=5)

            stage_name = stage.get("name", "新關卡")
            name_text = font.render(f"名稱: {stage_name}", True, (255, 255, 255))
            self.screen.blit(name_text, (520, 120))

            floors = stage.get("floors", [])
            for i, floor in enumerate(floors):
                floor_y = 160 + i * 60
                floor_text = small_font.render(
                    f"第 {floor.get('floor_num', i + 1)} 層", True, (200, 200, 200)
                )
                self.screen.blit(floor_text, (520, floor_y))

                enemy_count = len(floor.get("enemies", []))
                enemy_text = small_font.render(
                    f"  敵人: {enemy_count}", True, (160, 160, 160)
                )
                self.screen.blit(enemy_text, (620, floor_y))

                dialogue_count = len(floor.get("dialogue", []))
                if dialogue_count > 0:
                    dlg_text = small_font.render(
                        f"  對話: {dialogue_count}", True, (160, 160, 160)
                    )
                    self.screen.blit(dlg_text, (700, floor_y))

            hint_text = small_font.render(
                "點擊「編輯」打開詳細編輯器", True, (120, 120, 120)
            )
            self.screen.blit(hint_text, (520, 480))

    def draw_dialogue_tab(self):
        font = get_font(22)
        small_font = get_font(14)

        title = font.render("對話管理", True, (255, 200, 80))
        self.screen.blit(title, (50, 110))

        import json
        import os

        base_path = os.path.dirname(os.path.abspath(__file__))
        dialogues_path = os.path.join(base_path, "data", "dialogues.json")
        if os.path.exists(dialogues_path):
            with open(dialogues_path, "r", encoding="utf-8") as f:
                dialogues_data = json.load(f)
        else:
            dialogues_data = {"dialogues": {}}

        dialogues = dialogues_data.get("dialogues", {})
        if not dialogues:
            empty_text = small_font.render(
                "尚未有對話，點擊下方按鈕新增", True, (150, 150, 150)
            )
            self.screen.blit(empty_text, (50, 160))

        for i, (dlg_key, dlg_data) in enumerate(dialogues.items()):
            dlg_y = 120 + i * 50
            dlg_rect = pygame.Rect(50, dlg_y, 400, 45)
            bg_color = (40, 70, 120) if i == 0 else (35, 35, 45)
            pygame.draw.rect(self.screen, bg_color, dlg_rect, border_radius=3)

            dlg_name = (
                dlg_data.get("name", dlg_key) if isinstance(dlg_data, dict) else dlg_key
            )
            dlg_text = get_font(16).render(dlg_name, True, (255, 255, 255))
            self.screen.blit(dlg_text, (60, dlg_y + 12))

            entry_count = (
                len(dlg_data.get("entries", [])) if isinstance(dlg_data, dict) else 0
            )
            entry_text = small_font.render(f"{entry_count} 條", True, (180, 180, 180))
            self.screen.blit(entry_text, (280, dlg_y + 15))

            edit_btn = pygame.Rect(380, dlg_y + 5, 60, 35)
            pygame.draw.rect(self.screen, (60, 80, 120), edit_btn, border_radius=3)
            edit_text = small_font.render("編輯", True, (255, 255, 255))
            self.screen.blit(edit_text, (edit_btn.centerx - 15, edit_btn.centery - 7))

            # 刪除按鈕
            del_btn = pygame.Rect(450, dlg_y + 5, 40, 35)
            pygame.draw.rect(self.screen, (120, 50, 50), del_btn, border_radius=3)
            del_text = small_font.render("X", True, (255, 255, 255))
            self.screen.blit(del_text, (del_btn.centerx - 5, del_btn.centery - 7))

        add_btn_y = 120 + len(dialogues) * 50
        add_btn = pygame.Rect(50, add_btn_y, 150, 35)
        pygame.draw.rect(self.screen, (50, 80, 50), add_btn, border_radius=3)
        add_text = small_font.render("+ 新增對話", True, (255, 255, 255))
        self.screen.blit(add_text, (add_btn.centerx - 35, add_btn.centery - 7))

    def handle_dialogue_click(self, pos):
        import json
        import os

        base_path = os.path.dirname(os.path.abspath(__file__))
        dialogues_path = os.path.join(base_path, "data", "dialogues.json")
        if os.path.exists(dialogues_path):
            with open(dialogues_path, "r", encoding="utf-8") as f:
                dialogues_data = json.load(f)
        else:
            dialogues_data = {"dialogues": {}}

        dialogues = dialogues_data.get("dialogues", {})
        dialogue_items = list(dialogues.items())

        for i, (dlg_key, dlg_data) in enumerate(dialogue_items):
            dlg_y = 120 + i * 50

            # 檢查是否點擊了對話項目（選擇）
            dlg_rect = pygame.Rect(50, dlg_y, 280, 45)
            if dlg_rect.collidepoint(pos):
                self.selected_dialogue_index = i
                return

            # 檢查編輯按鈕
            edit_btn = pygame.Rect(380, dlg_y + 5, 60, 35)
            if edit_btn.collidepoint(pos):
                self.dialogue_editor = DialogueEditorModal(self.screen, dlg_key)
                return

            # 檢查刪除按鈕
            del_btn = pygame.Rect(450, dlg_y + 5, 40, 35)
            if del_btn.collidepoint(pos):
                # 刪除對話
                del dialogues_data["dialogues"][dlg_key]
                with open(dialogues_path, "w", encoding="utf-8") as f:
                    json.dump(dialogues_data, f, ensure_ascii=False, indent=2)
                return

        add_btn_y = 120 + len(dialogues) * 50
        if pygame.Rect(50, add_btn_y, 150, 35).collidepoint(pos):
            new_key = f"dialogue_{len(dialogues) + 1}"
            dialogues_data["dialogues"][new_key] = {
                "name": f"新對話 {len(dialogues) + 1}",
                "entries": [],
            }
            with open(dialogues_path, "w", encoding="utf-8") as f:
                json.dump(dialogues_data, f, ensure_ascii=False, indent=2)

    def draw_orb_skin_tab(self):
        from config import ORB_SKINS, DEFAULT_ORB_SKIN
        import json
        import os

        font = get_font(22)
        small_font = get_font(14)

        title = font.render("寶珠 Skin 管理", True, (255, 200, 80))
        self.screen.blit(title, (50, 110))

        hint = small_font.render(
            "拖入圖片到對應位置自動設定路徑", True, (150, 150, 150)
        )
        self.screen.blit(hint, (50, 145))

        hint2 = small_font.render(
            "點擊圖片框可設定路徑，按钮可刪除", True, (120, 120, 120)
        )
        self.screen.blit(hint2, (50, 165))

        base_path = os.path.dirname(os.path.abspath(__file__))

        config_path = os.path.join(base_path, "data", "orb_skins.json")
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                skin_config = json.load(f)
        else:
            skin_config = {"skins": {}, "default": "default"}

        y_start = 195
        row_height = 90
        orb_types = ["火", "水", "木", "光", "暗", "心"]

        self._orb_skin_rects = {}

        for i, skin_key in enumerate(skin_config.get("skins", {}).keys()):
            y = y_start + i * row_height
            skin_data = skin_config["skins"].get(skin_key, {})
            skin_name = skin_data.get("name", skin_key)

            bg_rect = pygame.Rect(50, y, 750, 80)
            pygame.draw.rect(self.screen, (40, 50, 60), bg_rect, border_radius=5)

            name_text = small_font.render(f"名稱: {skin_name}", True, (255, 255, 255))
            self.screen.blit(name_text, (60, y + 5))

            preview_x = 60
            for j, orb_type in enumerate(orb_types):
                box_x = preview_x + j * 60
                box_rect = pygame.Rect(box_x, y + 30, 50, 40)
                pygame.draw.rect(self.screen, (30, 30, 40), box_rect, border_radius=3)

                self._orb_skin_rects[(skin_key, orb_type)] = box_rect

                path_key = skin_data.get(orb_type, "")
                if path_key:
                    img_path = os.path.join(
                        base_path, "assets", "images", f"{path_key}.png"
                    )
                    if os.path.exists(img_path):
                        try:
                            img = pygame.image.load(img_path)
                            img = pygame.transform.scale(img, (46, 36))
                            self.screen.blit(img, (box_x + 2, y + 32))
                        except:
                            pass

                type_text = small_font.render(orb_type, True, (100, 100, 100))
                self.screen.blit(type_text, (box_x + 18, y + 72))

            del_btn = pygame.Rect(730, y + 5, 50, 25)
            pygame.draw.rect(self.screen, (120, 50, 50), del_btn, border_radius=3)
            del_text = small_font.render("刪除", True, (255, 255, 255))
            self.screen.blit(del_text, (del_btn.centerx - 15, del_btn.centery - 7))

            name_btn = pygame.Rect(680, y + 5, 45, 25)
            pygame.draw.rect(self.screen, (50, 100, 50), name_btn, border_radius=3)
            name_text = small_font.render("命名", True, (255, 255, 255))
            self.screen.blit(name_text, (name_btn.centerx - 15, name_btn.centery - 7))

        add_skin_btn_y = y_start + len(skin_config.get("skins", {})) * row_height
        add_skin_btn = pygame.Rect(50, add_skin_btn_y, 150, 35)
        pygame.draw.rect(self.screen, (50, 80, 50), add_skin_btn, border_radius=3)
        add_text = small_font.render("+ 新增 Skin", True, (255, 255, 255))
        self.screen.blit(
            add_text, (add_skin_btn.centerx - 35, add_skin_btn.centery - 7)
        )

        for i, skin_key in enumerate(skin_config.get("skins", {}).keys()):
            y = y_start + i * row_height
            bg_rect = pygame.Rect(50, y, 750, 80)

            if bg_rect.collidepoint(pygame.mouse.get_pos()):
                pygame.draw.rect(
                    self.screen, (80, 100, 140), bg_rect, 2, border_radius=5
                )
                drop_hint = small_font.render("拖放圖片到這裡", True, (255, 255, 100))
                self.screen.blit(drop_hint, (60, y + 30))

    def handle_orb_skin_click(self, pos):
        import json
        import os

        base_path = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(base_path, "data", "orb_skins.json")

        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                skin_config = json.load(f)
        else:
            skin_config = {"skins": {}, "default": "default"}

        y_start = 195
        row_height = 90
        orb_types = ["火", "水", "木", "光", "暗", "心"]
        skin_keys = list(skin_config.get("skins", {}).keys())

        for i, skin_key in enumerate(skin_keys):
            y = y_start + i * row_height

            del_btn = pygame.Rect(730, y + 5, 50, 25)
            if del_btn.collidepoint(pos):
                del skin_config["skins"][skin_key]
                with open(config_path, "w", encoding="utf-8") as f:
                    json.dump(skin_config, f, ensure_ascii=False, indent=2)
                return

            name_btn = pygame.Rect(680, y + 5, 45, 25)
            if name_btn.collidepoint(pos):
                self._editing_orb_skin_key = skin_key
                self.editing_field = "orb_skin_name"
                skin_data = skin_config["skins"].get(skin_key, {})
                self.edit_text = skin_data.get("name", skin_key)
                return

        add_skin_btn_y = y_start + len(skin_keys) * row_height
        if pygame.Rect(50, add_skin_btn_y, 150, 35).collidepoint(pos):
            new_skin_key = f"skin_{len(skin_keys) + 1}"
            skin_config.setdefault("skins", {})[new_skin_key] = {
                "name": f"新 Skin {len(skin_keys) + 1}",
                "火": "",
                "水": "",
                "木": "",
                "光": "",
                "暗": "",
                "心": "",
            }
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(skin_config, f, ensure_ascii=False, indent=2)

    def handle_orb_skin_file_drop(self, filepath):
        import json
        import os

        ext = os.path.splitext(filepath)[1].lower()
        if ext not in [".png", ".jpg", ".jpeg", ".bmp"]:
            return

        base_path = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(base_path, "data", "orb_skins.json")

        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                skin_config = json.load(f)
        else:
            return

        if not skin_config.get("skins"):
            print("沒有可用的 Skin 組，請先新增")
            return

        self._pending_orb_skin_file = filepath
        self._orb_skin_select_mode = True

    def draw_orb_skin_drop_selector(self):
        if not hasattr(self, "_pending_orb_skin_file"):
            return

        import os
        import json

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        modal_rect = pygame.Rect(
            SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 150, 400, 300
        )
        pygame.draw.rect(self.screen, (40, 40, 50), modal_rect, border_radius=10)
        pygame.draw.rect(self.screen, (100, 100, 150), modal_rect, 2, border_radius=10)

        font = get_font(20)
        title = font.render("選擇要設定的 Skin 和屬性", True, (255, 220, 100))
        self.screen.blit(
            title, (modal_rect.centerx - title.get_width() // 2, modal_rect.y + 20)
        )

        base_path = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(base_path, "data", "orb_skins.json")

        with open(config_path, "r", encoding="utf-8") as f:
            skin_config = json.load(f)

        y_start = modal_rect.y + 60

        for i, skin_key in enumerate(skin_config.get("skins", {}).keys()):
            skin_data = skin_config["skins"].get(skin_key, {})
            skin_name = skin_data.get("name", skin_key)

            row_y = y_start + i * 100

            skin_btn = pygame.Rect(modal_rect.x + 20, row_y, 360, 40)
            color = (
                (60, 100, 160)
                if i == getattr(self, "_selected_skin_index", 0)
                else (50, 50, 60)
            )
            pygame.draw.rect(self.screen, color, skin_btn, border_radius=5)

            skin_text = get_font(16).render(skin_name, True, (255, 255, 255))
            self.screen.blit(skin_text, (skin_btn.x + 10, skin_btn.y + 10))

            for j, orb_type in enumerate(["火", "水", "木", "光", "暗", "心"]):
                orb_x = skin_btn.x + 20 + j * 55
                orb_btn = pygame.Rect(orb_x, row_y + 45, 45, 35)
                pygame.draw.rect(self.screen, (40, 40, 50), orb_btn, border_radius=3)

                orb_text = get_font(14).render(orb_type, True, (150, 150, 150))
                self.screen.blit(orb_text, (orb_btn.centerx - 10, orb_btn.y + 10))

        hint = get_font(14).render("點擊屬性框設定圖片", True, (180, 180, 180))
        self.screen.blit(hint, (modal_rect.x + 20, modal_rect.y + 270))

        close_btn = pygame.Rect(modal_rect.x + 150, modal_rect.y + 270, 100, 30)
        pygame.draw.rect(self.screen, (80, 50, 50), close_btn, border_radius=5)
        close_text = get_font(14).render("取消", True, (255, 255, 255))
        self.screen.blit(close_text, (close_btn.centerx - 20, close_btn.centery - 7))

    def handle_orb_skin_drop_selector_click(self, pos):
        if not hasattr(self, "_pending_orb_skin_file"):
            return

        import os
        import json

        base_path = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(base_path, "data", "orb_skins.json")

        with open(config_path, "r", encoding="utf-8") as f:
            skin_config = json.load(f)

        y_start = SCREEN_HEIGHT // 2 - 150 + 60

        for i, skin_key in enumerate(skin_config.get("skins", {}).keys()):
            row_y = y_start + i * 100

            for j, orb_type in enumerate(["火", "水", "木", "光", "暗", "心"]):
                orb_x = 20 + 20 + j * 55
                orb_btn = pygame.Rect(
                    SCREEN_WIDTH // 2 - 200 + orb_x, row_y + 45, 45, 35
                )

                if orb_btn.collidepoint(pos):
                    orbs_dir = os.path.join(
                        base_path, "assets", "images", "orbs", skin_key
                    )
                    os.makedirs(orbs_dir, exist_ok=True)

                    target_path = os.path.join(orbs_dir, f"{orb_type}.png")
                    import shutil

                    shutil.copy2(self._pending_orb_skin_file, target_path)

                    relative_path = f"orbs/{skin_key}/{orb_type}"
                    skin_config["skins"][skin_key][orb_type] = relative_path

                    with open(config_path, "w", encoding="utf-8") as f:
                        json.dump(skin_config, f, ensure_ascii=False, indent=2)

                    print(f"已設定 {skin_key} - {orb_type}: {relative_path}")

                    del self._pending_orb_skin_file
                    self._orb_skin_select_mode = False
                    return

        close_btn = pygame.Rect(
            SCREEN_WIDTH // 2 - 200 + 150, SCREEN_HEIGHT // 2 - 150 + 270, 100, 30
        )
        if close_btn.collidepoint(pos):
            del self._pending_orb_skin_file
            self._orb_skin_select_mode = False


if __name__ == "__main__":
    tool = DevTool()
    tool.run()
