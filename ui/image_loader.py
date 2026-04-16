import os
import pygame

_head_cache = {}
_full_cache = {}


def get_image_path(pet_id, image_type="head"):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if image_type == "full":
        return os.path.join(base_dir, "assets", "images", "full", f"{pet_id}.png")
    else:
        return os.path.join(base_dir, "assets", "images", "head", f"{pet_id}.png")


def load_pet_head_image(pet_id, size=None):
    cache_key = (pet_id, size)
    if cache_key in _head_cache:
        return _head_cache[cache_key]

    image_path = get_image_path(pet_id, "head")

    if os.path.exists(image_path):
        try:
            img = pygame.image.load(image_path)
            img = img.convert_alpha()
            if size:
                img = pygame.transform.smoothscale(img, size)
            _head_cache[cache_key] = img
            return img
        except Exception:
            pass

    _head_cache[cache_key] = None
    return None


def load_pet_full_image(pet_id, size=None):
    cache_key = (pet_id, size if size else "original")
    if cache_key in _full_cache:
        return _full_cache[cache_key]

    image_path = get_image_path(pet_id, "full")

    if os.path.exists(image_path):
        try:
            img = pygame.image.load(image_path)
            img = img.convert_alpha()
            if size:
                img = pygame.transform.smoothscale(img, size)
            _full_cache[cache_key] = img
            return img
        except Exception:
            pass

    _full_cache[cache_key] = None
    return None


def get_pet_full_image_size(pet_id):
    image_path = get_image_path(pet_id, "full")
    if os.path.exists(image_path):
        try:
            img = pygame.image.load(image_path)
            return img.get_size()
        except Exception:
            pass
    return None


_orb_skin_cache = {}


def get_orb_image_path(orb_type, skin_key, size=None):
    import json

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(base_dir, "data", "orb_skins.json")

    skin_data = None

    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
            skins = config.get("skins", {})
            if skin_key in skins:
                skin_data = skins[skin_key]

    if skin_data is None:
        from config import ORB_SKINS

        if skin_key not in ORB_SKINS:
            skin_key = "default"
        skin_data = ORB_SKINS.get(skin_key, ORB_SKINS.get("default", {}))

    relative_path = skin_data.get(orb_type, "")

    if not relative_path:
        return None

    return os.path.join(base_dir, "assets", "images", f"{relative_path}.png")


def load_orb_image(orb_type, skin_key, size=None):
    cache_key = (orb_type, skin_key, size)
    if cache_key in _orb_skin_cache:
        return _orb_skin_cache[cache_key]

    image_path = get_orb_image_path(orb_type, skin_key, size)

    if image_path and os.path.exists(image_path):
        try:
            img = pygame.image.load(image_path)
            img = img.convert_alpha()
            if size:
                img = pygame.transform.smoothscale(img, size)
            _orb_skin_cache[cache_key] = img
            return img
        except Exception:
            pass

    _orb_skin_cache[cache_key] = None
    return None
