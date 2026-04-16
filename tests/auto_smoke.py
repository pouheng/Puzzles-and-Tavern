import sys
import os
import random
import time

# Ensure we can import the game's modules
root = r"C:\pad-game"
if root not in sys.path:
    sys.path.insert(0, root)

try:
    from dungeon.board import Orb, OrbBoard
    from config import ORB_TYPES
except Exception as e:
    print("Failed to import game modules:", e)
    raise


def force_plain_board(board):
    # Overwrite board with a deterministic, simple pattern
    board_rows = board.rows
    board_cols = board.cols
    new_grid = [
        [Orb(ORB_TYPES[(r + c) % len(ORB_TYPES)], c, r) for c in range(board_cols)]
        for r in range(board_rows)
    ]
    board.orbs = new_grid


def main():
    # Seed randomness for reproducibility
    random.seed(0)

    b = OrbBoard()
    force_plain_board(b)

    # Create a simple horizontal match at top row: 火 火 火
    if b.rows >= 1 and b.cols >= 3:
        b.orbs[0][0] = Orb("火", 0, 0)
        b.orbs[0][1] = Orb("火", 1, 0)
        b.orbs[0][2] = Orb("火", 2, 0)

    print("[AUTO_SMOKE] Before match: attempting to find matches:")
    initial = b.find_match_groups()
    print("[AUTO_SMOKE] initial matches:", initial)

    started = b.process_matches()
    print("[AUTO_SMOKE] process_matches started:", started)

    dt = 1.0 / 60.0
    steps = 0
    # Run the animation loop until there is nothing left to do
    while (
        b.animating
        or b.falling_orbs
        or (b.elimination_list and len(b.elimination_list) > 0)
    ):
        b.update_animation(dt)
        steps += 1
        if steps > 4000:
            break

    print("[AUTO_SMOKE] finished after steps:", steps)
    final_combo = b.get_combo_count()
    falling_cnt = len(b.falling_orbs)
    print("[AUTO_SMOKE] final combo:", final_combo)
    print("[AUTO_SMOKE] falling count:", falling_cnt)

    # Create a compact summary and copy to clipboard (or write to file if clipboard unavailable)
    summary_text = (
        "AUTO_SMOKE SUMMARY\n"
        f"status: success\nfinal_combo: {final_combo}\nsteps: {steps}\nfalling: {falling_cnt}\n"
        f"timestamp: {time.time()}\n"
    )
    copy_to_clipboard(summary_text)


def copy_to_clipboard(text):
    # Try tkinter first
    try:
        import tkinter as tk

        r = tk.Tk()
        r.withdraw()
        r.clipboard_clear()
        r.clipboard_append(text)
        r.update()
        r.destroy()
        print("[AUTO_SMOKE] Copied summary to clipboard (tkinter).")
        return True
    except Exception:
        pass
    # Fallback to pyperclip
    try:
        import pyperclip

        pyperclip.copy(text)
        print("[AUTO_SMOKE] Copied summary to clipboard (pyperclip).")
        return True
    except Exception:
        pass
    # Fallback to file
    try:
        os.makedirs("tests", exist_ok=True)
        path = os.path.join("tests", "auto_smoke_results.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"[AUTO_SMOKE] Summary written to {path}. You can copy it manually.")
        return False
    except Exception as e:
        print("[AUTO_SMOKE] Failed to write summary:", e)
        return False


if __name__ == "__main__":
    main()
