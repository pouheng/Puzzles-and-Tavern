import sys
import os
import json
import importlib

sys.path.insert(0, os.path.dirname(os.path.abspath(".")))

# Force reload stages module to get the debug prints
import dungeon.stages as dstages

importlib.reload(dstag)

# Now import
from dungeon.stages import load_stages, get_stage_dialogue

print("=== Testing Dialogue Name Loading ===")

stages = load_stages()
stage = stages[0]

print("Calling get_stage_dialogue...")
dialogue = get_stage_dialogue(stage)
print(f"Dialogue entries: {len(dialogue)}")

for i, entry in enumerate(dialogue):
    print(f"  {i}: name={repr(entry.name)}, trigger={entry.trigger}")

has_name = any(e.name for e in dialogue)
print(f"Has name: {has_name}")
print(f"Test: {'PASS' if has_name else 'FAIL'}")
