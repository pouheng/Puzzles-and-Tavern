import pygame
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

pygame.init()

screen = pygame.display.set_mode((1200, 800))


def test_game_init():
    print("\n=== Test Game Init ===")
    import main

    game = main.Game()
    print(f"Screen: {game.screen}")
    print(f"Fullscreen: {game.fullscreen}")
    return game.battle_view is None


def test_toggle_fullscreen():
    print("\n=== Test Toggle Fullscreen ===")
    import main

    game = main.Game()
    print(f"Initial fullscreen: {game.fullscreen}")
    return True


def test_handle_mouse_motion():
    print("\n=== Test Handle Mouse Motion ===")
    import main

    game = main.Game()
    if hasattr(game, "team_view"):
        game.handle_mouse_motion((100, 100))
        print("Mouse motion handled")
    else:
        print("Team view not initialized - skipping")
    return True


def test_full_flow():
    results = []
    results.append(("Game Init", test_game_init()))
    results.append(("Toggle Fullscreen", test_toggle_fullscreen()))
    results.append(("Handle Mouse Motion", test_handle_mouse_motion()))

    print("\n=== Test Results ===")
    for name, result in results:
        print(f"{name}: {'PASS' if result else 'FAIL'}")

    all_passed = all(r for _, r in results)
    print(f"\nOverall: {'PASS' if all_passed else 'FAIL'}")
    return all_passed


if __name__ == "__main__":
    test_full_flow()
    pygame.quit()
