import pygame
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

pygame.init()

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

from dev_tool import DevTool


def test_orb_skin_edit():
    print("=== Test Orb Skin Rename Button ===")

    d = DevTool()
    d.current_tab = 3

    try:
        d.draw()
        print("Draw OK")

        import json

        with open("data/orb_skins.json", encoding="utf-8") as f:
            config = json.load(f)

        print(f"Current skins: {list(config['skins'].keys())}")
        for k, v in config["skins"].items():
            print(f"  {k}: {v.get('name')}")

        return True
    except Exception as e:
        print(f"Error: {e}")
        return False


if __name__ == "__main__":
    result = test_orb_skin_edit()
    print(f"Test: {'PASS' if result else 'FAIL'}")
    pygame.quit()
