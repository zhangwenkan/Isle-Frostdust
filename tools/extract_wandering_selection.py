"""Read selected cooked assets into a separate analysis folder; never modify the game."""
from pathlib import Path
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1] / "artifacts/wandering-sword-local-study"
PAK = Path(r"D:\Y 逸jian风yun决 v1.23.26 全DLC xg器\WanderingSword\Wandering_Sword\Content\Paks\Wandering_Sword-WindowsNoEditor.pak")
paths = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8-sig"))
existing = set((ROOT / "pak-files.txt").read_text(encoding="utf-8-sig").splitlines())
for start in range(0, len(paths), 30):
    command = [str(ROOT / "tools/repak/repak.exe"), "unpack", str(PAK), "-o", str(ROOT / "extracted"), "-q", "-f"]
    for path in paths[start:start + 30]:
        prefix = path.rsplit(".", 1)[0]
        for candidate in [path, prefix + ".uexp", prefix + ".ubulk"]:
            if candidate in existing:
                command.extend(["-i", candidate])
    subprocess.run(command, check=True)
print(f"Extracted {len(paths)} selected asset groups")
