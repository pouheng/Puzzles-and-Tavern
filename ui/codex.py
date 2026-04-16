import pygame
from config import *
from data.pets import Pet
from ui.fonts import get_font
from ui.image_loader import load_pet_head_image


class Codex:
    def __init__(self, owned_pets):
        if owned_pets and isinstance(owned_pets[0], Pet):
            self.owned_pet_ids = {p.id for p in owned_pets}
        else:
            self.owned_pet_ids = set(owned_pets)
        self.all_pets = Pet.get_all()

        self.grid_cols = 5
        self.grid_rows = 4
        self.cell_size = 110
        self.margin = 10
        self.start_x = 60
        self.start_y = 30

    def set_owned_pets(self, owned_pet_ids):
        self.owned_pet_ids = owned_pet_ids

    def get_pet_at(self, pos):
        for pet in self.all_pets:
            pet_pos = self.get_pet_position(pet)
            if pet_pos and self.is_point_in_cell(pos, pet_pos):
                return pet
        return None

    def get_pet_position(self, pet):
        try:
            index = self.all_pets.index(pet)
            row = index // self.grid_cols
            col = index % self.grid_cols
            x = self.start_x + col * (self.cell_size + self.margin)
            y = self.start_y + row * (self.cell_size + self.margin)
            return (x, y)
        except ValueError:
            return None

    def is_point_in_cell(self, pos, cell_pos):
        x, y = pos
        cx, cy = cell_pos
        return cx <= x <= cx + self.cell_size and cy <= y <= cy + self.cell_size

    def is_owned(self, pet):
        return pet.id in self.owned_pet_ids

    def draw(self, screen):
        title_font = get_font(40)
        title = title_font.render("圖鑑", True, (255, 220, 100))
        screen.blit(title, (60, 0))

        collected = len([p for p in self.all_pets if self.is_owned(p)])
        total = len(self.all_pets)
        count_font = get_font(24)
        count_text = count_font.render(
            f"已收集: {collected}/{total}", True, (180, 180, 180)
        )
        screen.blit(count_text, (180, 8))

        for pet in self.all_pets:
            pet_pos = self.get_pet_position(pet)
            if pet_pos:
                owned = self.is_owned(pet)
                self.draw_pet_card(screen, pet, pet_pos, owned=owned)

    def draw_pet_card(self, screen, pet, pos, owned=True):
        x, y = pos

        if owned:
            border_color = RARITY_COLORS.get(pet.rarity, (150, 150, 150))
            bg_color = (40, 40, 50)
        else:
            border_color = (80, 80, 80)
            bg_color = (25, 25, 30)

        pygame.draw.rect(screen, bg_color, (x, y, self.cell_size, self.cell_size))
        pygame.draw.rect(
            screen, border_color, (x, y, self.cell_size, self.cell_size), 3
        )

        img_w = self.cell_size - 16
        img_h = self.cell_size - 30
        img_x = x + 8
        img_y = y + 8

        if owned:
            img = load_pet_head_image(pet.id, (img_w, img_h))
            if img:
                screen.blit(img, (img_x, img_y))
            else:
                pygame.draw.rect(screen, (35, 35, 45), (img_x, img_y, img_w, img_h))
                main_attr_color = ATTRIBUTE_COLORS.get(pet.attribute, (200, 200, 200))
                sub_attr = getattr(pet, "sub_attribute", None)
                if sub_attr:
                    sub_attr_color = ATTRIBUTE_COLORS.get(sub_attr, (200, 200, 200))
                    pygame.draw.rect(
                        screen, main_attr_color, (img_x, img_y, img_w, img_h), 2
                    )
                    pygame.draw.rect(
                        screen,
                        sub_attr_color,
                        (img_x + 2, img_y + 2, img_w - 4, img_h - 4),
                        1,
                    )
                else:
                    pygame.draw.rect(
                        screen, main_attr_color, (img_x, img_y, img_w, img_h), 2
                    )

            stars = "★" * pet.rarity
            star_font = get_font(18)
            stars_surface = star_font.render(stars, True, border_color)
            stars_rect = stars_surface.get_rect(
                center=(x + self.cell_size // 2, y + self.cell_size - 12)
            )
            screen.blit(stars_surface, stars_rect)
        else:
            font = get_font(30)
            lock_text = font.render("?", True, (80, 80, 80))
            lock_rect = lock_text.get_rect(
                center=(x + self.cell_size // 2, y + self.cell_size // 2)
            )
            screen.blit(lock_text, lock_rect)
