import pygame
from config import *
from ui.fonts import get_font
from ui.image_loader import load_pet_head_image

TEAM_MAX_SIZE = 6
MAX_TEAMS = 10


class Team:
    def __init__(self, team_id, name="新隊伍"):
        self.team_id = team_id
        self.name = name
        self.members = [None] * TEAM_MAX_SIZE

    def add_member(self, pet, position):
        if 0 <= position < TEAM_MAX_SIZE:
            self.members[position] = pet

    def remove_member(self, position):
        if 0 <= position < TEAM_MAX_SIZE:
            self.members[position] = None

    def swap_members(self, pos1, pos2):
        self.members[pos1], self.members[pos2] = self.members[pos2], self.members[pos1]

    def get_leader(self):
        return self.members[0] if self.members else None

    def get_leader_skill(self):
        leader = self.get_leader()
        if leader and leader.leader_skill:
            return leader.leader_skill
        return None

    def _build_context(self):
        team_attrs = []
        team_types = []
        for pet in self.members:
            if pet:
                team_attrs.append(pet.attribute)
                team_types.append(pet.race)
                if hasattr(pet, "sub_attribute") and pet.sub_attribute:
                    team_attrs.append(pet.sub_attribute)

        context = {
            "team_types": team_types,
            "team_attributes": team_attrs,
            "board_attributes": [],
            "combo_count": 0,
            "hp_ratio": 1.0,
        }
        leader = self.get_leader()
        if leader:
            context["hp_ratio"] = 1.0
        return context

    def get_total_hp(self):
        base_hp = sum(pet.hp for pet in self.members if pet)
        leader_skill = self.get_leader_skill()
        if leader_skill:
            context = self._build_context()
            hp_mult = leader_skill.calculate_hp_mult(context)
            return int(base_hp * hp_mult)
        return base_hp

    def get_total_attack(self):
        base_attack = sum(pet.attack for pet in self.members if pet)
        leader_skill = self.get_leader_skill()
        if leader_skill:
            context = self._build_context()
            attack_mult = leader_skill.calculate_attack_mult(context)
            return int(base_attack * attack_mult)
        return base_attack

    def get_total_recovery(self):
        base_recovery = sum(pet.recovery for pet in self.members if pet)
        leader_skill = self.get_leader_skill()
        if leader_skill:
            context = self._build_context()
            recovery_mult = leader_skill.calculate_recovery_mult(context)
            return int(base_recovery * recovery_mult)
        return base_recovery

    def get_member_count(self):
        return sum(1 for pet in self.members if pet)

    def get_next_empty_slot(self):
        for i in range(TEAM_MAX_SIZE):
            if self.members[i] is None:
                return i
        return None

    def is_full(self):
        return None not in self.members

    def is_member(self, pet):
        return pet in self.members

    def to_dict(self):
        return {
            "team_id": self.team_id,
            "name": self.name,
            "members": [pet.id if pet else None for pet in self.members],
        }

    @classmethod
    def from_dict(cls, data, pets_dict):
        team = cls(data["team_id"], data["name"])
        for i, pet_id in enumerate(data["members"][:TEAM_MAX_SIZE]):
            if pet_id and pet_id in pets_dict:
                team.members[i] = pets_dict[pet_id]
        return team


class TeamManager:
    def __init__(self, max_teams=MAX_TEAMS):
        self.max_teams = max_teams
        self.teams = [Team(i, f"隊伍{i + 1}") for i in range(max_teams)]
        self.current_team_index = 0
        self.active_team_index = 0

    @property
    def current_team(self):
        return self.teams[self.current_team_index]

    @property
    def active_team(self):
        return self.teams[self.active_team_index]

    def switch_team(self, index):
        if 0 <= index < self.max_teams:
            self.current_team_index = index

    def set_active_team(self, index):
        if 0 <= index < self.max_teams:
            self.active_team_index = index

    def to_dict(self):
        return {
            "current_team_index": self.current_team_index,
            "active_team_index": self.active_team_index,
            "teams": [team.to_dict() for team in self.teams],
        }

    @classmethod
    def from_dict(cls, data, pets_dict):
        manager = cls()
        manager.current_team_index = data.get("current_team_index", 0)
        manager.active_team_index = data.get("active_team_index", 0)
        for i, team_data in enumerate(data.get("teams", [])):
            if i < manager.max_teams:
                manager.teams[i] = Team.from_dict(team_data, pets_dict)
        return manager


class TeamView:
    SLOT_COUNT = 6

    def __init__(self, team_manager):
        self.team_manager = team_manager
        self.clicked_slot_index = None
        self.drag_start = None

        self.team_slots_x = 80
        self.team_slots_y = 200
        self.slot_size = 100
        self.slot_margin = 15

        self.left_arrow_rect = pygame.Rect(20, 280, 50, 80)
        self.right_arrow_rect = pygame.Rect(830, 280, 50, 80)
        self.select_btn_rect = pygame.Rect(680, 120, 150, 45)
        self.active_btn_rect = pygame.Rect(680, 175, 150, 45)

    def get_slot_at(self, pos):
        for i in range(self.SLOT_COUNT):
            slot_x = self.team_slots_x + i * (self.slot_size + self.slot_margin)
            slot_rect = pygame.Rect(
                slot_x, self.team_slots_y, self.slot_size, self.slot_size
            )
            if slot_rect.collidepoint(pos):
                return i
        return None

    def handle_click(self, pos):
        if self.left_arrow_rect.collidepoint(pos):
            current = self.team_manager.current_team_index
            self.team_manager.switch_team((current - 1) % self.team_manager.max_teams)
            return "arrow"

        if self.right_arrow_rect.collidepoint(pos):
            current = self.team_manager.current_team_index
            self.team_manager.switch_team((current + 1) % self.team_manager.max_teams)
            return "arrow"

        if self.select_btn_rect.collidepoint(pos):
            return "select"

        if self.active_btn_rect.collidepoint(pos):
            self.team_manager.set_active_team(self.team_manager.current_team_index)
            return "active"

        slot_index = self.get_slot_at(pos)
        if slot_index is not None:
            self.clicked_slot_index = slot_index
            return slot_index

        return None

    def handle_mouse_down(self, pos):
        self.drag_start = pos

    def handle_mouse_up(self, pos):
        if self.drag_start and abs(pos[0] - self.drag_start[0]) > 30:
            current = self.team_manager.current_team_index
            direction = 1 if pos[0] > self.drag_start[0] else -1
            self.team_manager.switch_team(
                (current - direction) % self.team_manager.max_teams
            )
        self.drag_start = None

    def draw(self, screen, inventory_pets):
        team = self.team_manager.current_team

        title_font = get_font(36)
        title = title_font.render("組隊", True, (255, 220, 100))
        screen.blit(title, (60, 10))

        team_font = get_font(28)
        team_title = team_font.render(
            f"{team.name} ({self.team_manager.current_team_index + 1}/{self.team_manager.max_teams})",
            True,
            (255, 255, 255),
        )
        screen.blit(team_title, (60, 55))

        self.draw_select_button(screen)
        self.draw_active_button(screen)
        self.draw_arrows(screen)
        self.draw_team_slots(screen, team)
        self.draw_totals(screen, team)

    def draw_select_button(self, screen):
        pygame.draw.rect(screen, (60, 100, 60), self.select_btn_rect)
        pygame.draw.rect(screen, (100, 200, 100), self.select_btn_rect, 2)
        btn_font = get_font(22)
        btn_text = btn_font.render("選擇隊員", True, (255, 255, 255))
        btn_rect = btn_text.get_rect(center=self.select_btn_rect.center)
        screen.blit(btn_text, btn_rect)

    def draw_active_button(self, screen):
        is_active = (
            self.team_manager.current_team_index == self.team_manager.active_team_index
        )
        if is_active:
            color = (100, 80, 120)
            border_color = (150, 120, 180)
            text = "已設為出戰"
        else:
            color = (80, 60, 100)
            border_color = (120, 100, 150)
            text = "設為出戰"
        pygame.draw.rect(screen, color, self.active_btn_rect)
        pygame.draw.rect(screen, border_color, self.active_btn_rect, 2)
        btn_font = get_font(20)
        btn_text = btn_font.render(text, True, (255, 255, 255))
        btn_rect = btn_text.get_rect(center=self.active_btn_rect.center)
        screen.blit(btn_text, btn_rect)

    def draw_arrows(self, screen):
        pygame.draw.rect(screen, (60, 60, 80), self.left_arrow_rect)
        pygame.draw.rect(screen, (60, 60, 80), self.right_arrow_rect)

        font = get_font(40)
        left_text = font.render("<", True, (255, 255, 255))
        left_rect = left_text.get_rect(center=self.left_arrow_rect.center)
        screen.blit(left_text, left_rect)

        right_text = font.render(">", True, (255, 255, 255))
        right_rect = right_text.get_rect(center=self.right_arrow_rect.center)
        screen.blit(right_text, right_rect)

    def _draw_dual_border(self, screen, x, y, width, height, color1, color2):
        pygame.draw.rect(screen, color1, (x, y, width, height), 2)
        pygame.draw.rect(screen, color2, (x + 2, y + 2, width - 4, height - 4), 1)

    def draw_team_slots(self, screen, team):
        for i in range(TEAM_MAX_SIZE):
            slot_x = self.team_slots_x + i * (self.slot_size + self.slot_margin)
            slot_y = self.team_slots_y

            border_color = (255, 200, 100) if i == 0 else (80, 80, 100)

            pygame.draw.rect(
                screen, (40, 40, 55), (slot_x, slot_y, self.slot_size, self.slot_size)
            )
            pygame.draw.rect(
                screen,
                border_color,
                (slot_x, slot_y, self.slot_size, self.slot_size),
                3,
            )

            pet = team.members[i]
            if pet:
                img_w = self.slot_size - 16
                img_h = self.slot_size - 30
                img = load_pet_head_image(pet.id, (img_w, img_h))
                if img:
                    screen.blit(img, (slot_x + 8, slot_y + 8))
                else:
                    pygame.draw.rect(
                        screen, (50, 50, 60), (slot_x + 8, slot_y + 8, img_w, img_h)
                    )
                    main_attr_color = ATTRIBUTE_COLORS.get(
                        pet.attribute, (200, 200, 200)
                    )
                    sub_attr = getattr(pet, "sub_attribute", None)
                    if sub_attr:
                        sub_attr_color = ATTRIBUTE_COLORS.get(sub_attr, (200, 200, 200))
                        self._draw_dual_border(
                            screen,
                            slot_x + 8,
                            slot_y + 8,
                            img_w,
                            img_h,
                            main_attr_color,
                            sub_attr_color,
                        )
                    else:
                        pygame.draw.rect(
                            screen,
                            main_attr_color,
                            (slot_x + 8, slot_y + 8, img_w, img_h),
                            2,
                        )
            else:
                font = get_font(36)
                empty_text = font.render("+", True, (100, 100, 120))
                empty_rect = empty_text.get_rect(
                    center=(slot_x + self.slot_size // 2, slot_y + self.slot_size // 2)
                )
                screen.blit(empty_text, empty_rect)

    def draw_totals(self, screen, team):
        y = self.team_slots_y + self.slot_size + 30

        title_font = get_font(26)
        title = title_font.render("合計數值", True, (255, 220, 100))
        screen.blit(title, (60, y))

        y += 35
        stat_font = get_font(24)

        hp_text = stat_font.render(f"HP: {team.get_total_hp()}", True, (100, 255, 100))
        screen.blit(hp_text, (60, y))

        atk_text = stat_font.render(
            f"攻撃: {team.get_total_attack()}", True, (255, 100, 100)
        )
        screen.blit(atk_text, (250, y))

        rcv_text = stat_font.render(
            f"回復: {team.get_total_recovery()}", True, (100, 200, 255)
        )
        screen.blit(rcv_text, (450, y))

        self.draw_leader_skill(screen, team, y + 40)

        hint_font = get_font(20)
        hint = hint_font.render(
            "點擊「選擇隊員」按鈕進入選擇模式", True, (150, 150, 150)
        )
        screen.blit(hint, (60, y + 130))

    def draw_leader_skill(self, screen, team, y):
        leader = team.get_leader()
        leader_skill = team.get_leader_skill()

        title_font = get_font(22)
        title = title_font.render("隊長技能", True, (255, 220, 100))
        screen.blit(title, (60, y))

        y += 30

        if leader and leader_skill:
            name_font = get_font(20)
            name_text = name_font.render(f"【{leader.name}】", True, (255, 255, 200))
            screen.blit(name_text, (60, y))

            y += 28
            desc_font = get_font(18)
            desc = leader_skill.get_description()
            desc_text = desc_font.render(desc, True, (200, 200, 200))
            screen.blit(desc_text, (60, y))
        else:
            desc_font = get_font(18)
            desc_text = desc_font.render("請設置隊長", True, (150, 150, 150))
            screen.blit(desc_text, (60, y))


class TeamEditView:
    def __init__(self, team_manager, inventory_pets, slot_index=None):
        self.team_manager = team_manager
        self.inventory_pets = inventory_pets
        self.slot_index = slot_index
        self.target_mode = slot_index is not None

        self.team_slots_x = 80
        self.team_slots_y = 130
        self.slot_size = 80
        self.slot_margin = 10

        self.grid_cols = 6
        self.cell_size = 90
        self.margin = 10
        self.start_x = 60
        self.start_y = 240

        self.exit_btn_rect = pygame.Rect(SCREEN_WIDTH - 150, 10, 120, 40)

    def _draw_dual_border(self, screen, x, y, width, height, color1, color2):
        pygame.draw.rect(screen, color1, (x, y, width, height), 2)
        pygame.draw.rect(screen, color2, (x + 2, y + 2, width - 4, height - 4), 1)

    def handle_click(self, pos):
        team = self.team_manager.current_team

        if self.exit_btn_rect.collidepoint(pos):
            return False

        team_slot = self._get_team_slot_at(pos)
        if team_slot is not None:
            team.remove_member(team_slot)
            return True

        pet_index = self._get_pet_index_at(pos)
        if pet_index is not None:
            pet = self.inventory_pets[pet_index]
            if team.is_member(pet):
                return True

            if self.target_mode:
                team.remove_member(self.slot_index)
                team.add_member(pet, self.slot_index)
            else:
                next_slot = team.get_next_empty_slot()
                if next_slot is not None:
                    team.add_member(pet, next_slot)

            return True

        return True

    def _get_team_slot_at(self, pos):
        for i in range(TEAM_MAX_SIZE):
            slot_x = self.team_slots_x + i * (self.slot_size + self.slot_margin)
            slot_rect = pygame.Rect(
                slot_x, self.team_slots_y, self.slot_size, self.slot_size
            )
            if slot_rect.collidepoint(pos):
                return i
        return None

    def _get_pet_index_at(self, pos):
        for i, pet in enumerate(self.inventory_pets):
            row = i // self.grid_cols
            col = i % self.grid_cols
            x = self.start_x + col * (self.cell_size + self.margin)
            y = self.start_y + row * (self.cell_size + self.margin)

            slot_rect = pygame.Rect(x, y, self.cell_size, self.cell_size)
            if slot_rect.collidepoint(pos):
                return i
        return None

    def draw(self, screen):
        team = self.team_manager.current_team

        pygame.draw.rect(screen, (30, 30, 40), (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT - 60))

        title_font = get_font(32)
        title_text = (
            f"選擇第 {self.slot_index + 1} 位置隊員"
            if self.target_mode
            else "選擇隊員（按順序添加）"
        )
        title = title_font.render(title_text, True, (255, 220, 100))
        screen.blit(title, (60, 15))

        pygame.draw.rect(screen, (200, 80, 80), self.exit_btn_rect)
        pygame.draw.rect(screen, (255, 100, 100), self.exit_btn_rect, 2)
        btn_font = get_font(24)
        btn_text = btn_font.render("返回", True, (255, 255, 255))
        btn_rect = btn_text.get_rect(center=self.exit_btn_rect.center)
        screen.blit(btn_text, btn_rect)

        hint_font = get_font(18)
        hint = hint_font.render("點擊上方欄位可移除已選隊員", True, (180, 180, 180))
        screen.blit(hint, (60, 100))

        self.draw_team_slots(screen, team)
        self.draw_pet_grid(screen, team)
        self.draw_hint(screen)

    def draw_team_slots(self, screen, team):
        for i in range(TEAM_MAX_SIZE):
            slot_x = self.team_slots_x + i * (self.slot_size + self.slot_margin)
            slot_y = self.team_slots_y

            if self.target_mode and i == self.slot_index:
                border_color = (255, 200, 100)
            elif i == 0:
                border_color = (200, 200, 100)
            else:
                border_color = (80, 80, 100)

            pygame.draw.rect(
                screen, (40, 40, 55), (slot_x, slot_y, self.slot_size, self.slot_size)
            )
            pygame.draw.rect(
                screen,
                border_color,
                (slot_x, slot_y, self.slot_size, self.slot_size),
                3,
            )

            num_font = get_font(18)
            num_text = num_font.render(f"{i + 1}", True, border_color)
            screen.blit(num_text, (slot_x + 5, slot_y + 5))

            pet = team.members[i]
            if pet:
                img_w = self.slot_size - 16
                img_h = self.slot_size - 30
                img = load_pet_head_image(pet.id, (img_w, img_h))
                if img:
                    screen.blit(img, (slot_x + 8, slot_y + 12))
                else:
                    pygame.draw.rect(
                        screen, (50, 50, 60), (slot_x + 8, slot_y + 12, img_w, img_h)
                    )
                    main_attr_color = ATTRIBUTE_COLORS.get(
                        pet.attribute, (200, 200, 200)
                    )
                    sub_attr = getattr(pet, "sub_attribute", None)
                    if sub_attr:
                        sub_attr_color = ATTRIBUTE_COLORS.get(sub_attr, (200, 200, 200))
                        self._draw_dual_border(
                            screen,
                            slot_x + 8,
                            slot_y + 12,
                            img_w,
                            img_h,
                            main_attr_color,
                            sub_attr_color,
                        )
                    else:
                        pygame.draw.rect(
                            screen,
                            main_attr_color,
                            (slot_x + 8, slot_y + 12, img_w, img_h),
                            2,
                        )
            else:
                font = get_font(32)
                empty_text = font.render("+", True, (100, 100, 120))
                empty_rect = empty_text.get_rect(
                    center=(
                        slot_x + self.slot_size // 2,
                        slot_y + self.slot_size // 2 + 10,
                    )
                )
                screen.blit(empty_text, empty_rect)

    def draw_pet_grid(self, screen, team):
        for i, pet in enumerate(self.inventory_pets):
            row = i // self.grid_cols
            col = i % self.grid_cols
            x = self.start_x + col * (self.cell_size + self.margin)
            y = self.start_y + row * (self.cell_size + self.margin)

            border_color = RARITY_COLORS.get(pet.rarity, (150, 150, 150))
            in_team = team.is_member(pet)

            pygame.draw.rect(
                screen, (40, 40, 55), (x, y, self.cell_size, self.cell_size)
            )
            pygame.draw.rect(
                screen, border_color, (x, y, self.cell_size, self.cell_size), 3
            )

            if in_team:
                overlay = pygame.Surface(
                    (self.cell_size, self.cell_size), pygame.SRCALPHA
                )
                overlay.fill((30, 30, 40, 150))
                screen.blit(overlay, (x, y))

            img_w = self.cell_size - 16
            img_h = self.cell_size - 30
            img = load_pet_head_image(pet.id, (img_w, img_h))
            if img:
                screen.blit(img, (x + 8, y + 8))
            else:
                attr_color = ATTRIBUTE_COLORS.get(pet.attribute, (200, 200, 200))
                pygame.draw.rect(screen, (50, 50, 60), (x + 8, y + 8, img_w, img_h))
                pygame.draw.rect(screen, attr_color, (x + 8, y + 8, img_w, img_h), 2)

            stars = "★" * pet.rarity
            star_font = get_font(16)
            stars_surface = star_font.render(stars, True, border_color)
            stars_rect = stars_surface.get_rect(
                center=(x + self.cell_size // 2, y + self.cell_size - 12)
            )
            screen.blit(stars_surface, stars_rect)

            if in_team:
                check_font = get_font(20)
                check_text = check_font.render("已選", True, (150, 255, 150))
                check_rect = check_text.get_rect(
                    center=(x + self.cell_size // 2, y + self.cell_size // 2)
                )
                screen.blit(check_text, check_rect)

    def draw_hint(self, screen):
        team = self.team_manager.current_team
        hint_text = (
            f"選擇寵物放入第 {self.slot_index + 1} 位置"
            if self.target_mode
            else f"已選 {team.get_member_count()}/{TEAM_MAX_SIZE} 位置"
        )
        hint_font = get_font(20)
        hint = hint_font.render(hint_text, True, (150, 150, 150))
        grid_height = ((len(self.inventory_pets) - 1) // self.grid_cols + 1) * (
            self.cell_size + self.margin
        )
        screen.blit(hint, (60, self.start_y + grid_height + 15))
