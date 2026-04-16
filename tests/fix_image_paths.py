"""
修復圖片路徑
"""

import os
import shutil

# 確保目錄存在
base = "C:/pad-game/assets/images"
for subdir in ["avatar", "enemy"]:
    path = os.path.join(base, subdir)
    os.makedirs(path, exist_ok=True)
    print(f"目錄: {path}")

# 移動測試圖片
test_dir = "C:/pad-game/tests/assets/images"

for subdir in ["avatar", "enemy"]:
    src = os.path.join(
        test_dir,
        subdir,
        "test_avatar_1.png" if subdir == "avatar" else "test_enemy_1.png",
    )
    if os.path.exists(src):
        dst = os.path.join(base, subdir, os.path.basename(src))
        shutil.copy2(src, dst)
        print(f"已複製: {src} -> {dst}")
    else:
        print(f"來源不存在: {src}")

# 列出最終圖片
print("\n最終圖片:")
for subdir in ["avatar", "enemy"]:
    dir_path = os.path.join(base, subdir)
    files = os.listdir(dir_path)
    print(f"  {subdir}: {files}")
