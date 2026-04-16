import pygame
from config import *
from ui.fonts import get_font
from ui.image_loader import load_pet_head_image


class Inventory:
    def __init__(self):
        self.grid_cols = INVENTORY_GRID_COLS
        self.grid_rows = INVENTORY_GRID_ROWS
        self.cell_size = INVENTORY_CELL_SIZE
        self.margin = INVENTORY_MARGIN
        self.start_x = INVENTORY_START_X
        self.start_y = INVENTORY_START_Y

        self.pets = []
        self.dragged_pet = None
        self.drag_offset = (0, 0)
        self.drag_pos = (0, 0)
        self.original_pos = None

    def add_pet(self, pet):
        self.pets.append(pet)

    def get_owned_ids(self):
        return [pet.id for pet in self.pets]

    def get_all_pet_ids(self):
        from data.pets import Pet

        return [p.id for p in Pet.get_all()]

    def get_pet_at(self, pos):
        if self.is_dragging():
            return self.dragged_pet

        for pet in self.pets:
            pet_pos = self.get_pet_position(pet)
            if pet_pos and self.is_point_in_cell(pos, pet_pos):
                return pet
        return None

    def get_pet_position(self, pet):
        try:
            index = self.pets.index(pet)
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

    def is_dragging(self):
        return self.dragged_pet is not None

    def start_drag(self, pet, pos):
        self.dragged_pet = pet
        self.original_pos = self.get_pet_position(pet)
        self.drag_pos = pos
        if self.original_pos:
            self.drag_offset = (
                pos[0] - self.original_pos[0],
                pos[1] - self.original_pos[1],
            )

    def update_drag_position(self, pos):
        self.drag_pos = pos

    def drop_pet(self, pos):
        if not self.dragged_pet:
            return

        new_index = self.calculate_drop_index(pos)

        if new_index != -1:
            current_index = self.pets.index(self.dragged_pet)
            if current_index != new_index:
                self.pets.remove(self.dragged_pet)
                self.pets.insert(new_index, self.dragged_pet)

        self.dragged_pet = None
        self.original_pos = None

    def calculate_drop_index(self, pos):
        col = (pos[0] - self.start_x) // (self.cell_size + self.margin)
        row = (pos[1] - self.start_y) // (self.cell_size + self.margin)

        col = max(0, min(col, self.grid_cols - 1))
        row = max(0, min(row, self.grid_rows - 1))

        return row * self.grid_cols + col

    def draw(self, screen):
        for i in range(self.grid_cols * self.grid_rows):
            row = i // self.grid_cols
            col = i % self.grid_cols
            x = self.start_x + col * (self.cell_size + self.margin)
            y = self.start_y + row * (self.cell_size + self.margin)

            pygame.draw.rect(
                screen, (50, 50, 60), (x, y, self.cell_size, self.cell_size), 0
            )
            pygame.draw.rect(
                screen, (70, 70, 80), (x, y, self.cell_size, self.cell_size), 2
            )

        for pet in self.pets:
            if pet == self.dragged_pet:
                continue

            pet_pos = self.get_pet_position(pet)
            if pet_pos:
                self.draw_pet_card(screen, pet, pet_pos)

        if self.is_dragging() and self.original_pos:
            self.draw_pet_card(
                screen, self.dragged_pet, self.drag_pos, is_dragging=True
            )

    def draw_pet_card(self, screen, pet, pos, is_dragging=False):
        x, y = pos
        if is_dragging:
            x = pos[0] - self.drag_offset[0]
            y = pos[1] - self.drag_offset[1]

        border_color = RARITY_COLORS.get(pet.rarity, (150, 150, 150))
        if is_dragging:
            border_color = (255, 255, 255)

        pygame.draw.rect(
            screen, (35, 35, 45), (x, y, self.cell_size, self.cell_size), 0
        )
        pygame.draw.rect(
            screen,
            border_color,
            (x, y, self.cell_size, self.cell_size),
            CARD_BORDER_WIDTH,
        )

        img_w = self.cell_size - 16
        img_h = self.cell_size - 30
        img_x = x + 8
        img_y = y + 8

        img = load_pet_head_image(pet.id, (img_w, img_h))
        if img:
            screen.blit(img, (img_x, img_y))
        else:
            pygame.draw.rect(screen, (45, 45, 55), (img_x, img_y, img_w, img_h))
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

        level_font = get_font(16)
        level_text = f"Lv.{pet.level}"
        level_surface = level_font.render(level_text, True, (255, 200, 100))
        level_rect = level_surface.get_rect(topright=(x + self.cell_size - 4, y + 4))
        screen.blit(level_surface, level_rect)
