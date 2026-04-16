import pygame


_FONT_CACHE = {}

# Ordered by common availability on Traditional Chinese Windows setups.
CJK_FONT_CANDIDATES = [
    "Microsoft JhengHei",
    "Microsoft JhengHei UI",
    "PMingLiU",
    "MingLiU",
    "Noto Sans CJK TC",
    "Noto Sans CJK SC",
    "SimHei",
]


def get_font(size):
    key = int(size)
    cached = _FONT_CACHE.get(key)
    if cached is not None:
        return cached

    for name in CJK_FONT_CANDIDATES:
        path = pygame.font.match_font(name)
        if path:
            font = pygame.font.Font(path, key)
            _FONT_CACHE[key] = font
            return font

    # Fallback when no CJK-capable system font is found.
    font = pygame.font.Font(None, key)
    _FONT_CACHE[key] = font
    return font
