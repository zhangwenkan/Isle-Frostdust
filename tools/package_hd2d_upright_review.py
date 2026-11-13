"""Package native gameplay stills; resize only the review sheet, never source sprites."""
from pathlib import Path
import json
import re

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1] / "artifacts/hd2d-upright-review"
FONT = "C:/Windows/Fonts/msyh.ttc"


def overview(phase, output):
    sheet = Image.new("RGB", (1600, 980), "#1c2327")
    draw = ImageDraw.Draw(sheet)
    for i, (key, title) in enumerate([
        ("cape", "岛角 · 探索镜头"), ("grove", "竹林"),
        ("bridge-entry", "桥头"), ("bridge-middle", "桥中"),
    ]):
        picture = Image.open(ROOT / f"{phase}-{key}-right.png")
        picture.thumbnail((800, 450))
        x, y = i % 2 * 800, i // 2 * 490
        sheet.paste(picture, (x, y + 40))
        draw.text((x + 12, y + 4), title, font=ImageFont.truetype(FONT, 24), fill="white")
    sheet.save(ROOT / output, quality=94)


def bridge_comparison():
    sheet = Image.new("RGB", (1200, 470), "#1c2327")
    draw = ImageDraw.Draw(sheet)
    for i, (phase, direction, title) in enumerate([
        ("before", "right", "修改前 · 侧面"), ("pass2", "right", "现在 · 侧面"),
        ("before", "down", "修改前 · 正面"), ("pass2", "down", "现在 · 正面"),
    ]):
        rows = json.loads((ROOT / f"{phase}-poses.json").read_text(encoding="utf8"))
        row = next(r for r in rows if r["label"] == "bridge-entry" and r["direction"] == direction)
        x, y = map(float, re.findall(r"-?\d+(?:\.\d+)?", row["foot"]))
        picture = Image.open(ROOT / f"{phase}-bridge-entry-{direction}.png")
        crop = picture.crop((int(x) - 100, int(y) - 240, int(x) + 100, int(y) + 40))
        sheet.paste(crop.resize((300, 420), Image.Resampling.NEAREST), (i * 300, 45))
        draw.text((i * 300 + 16, 8), title, font=ImageFont.truetype(FONT, 24), fill="white")
    sheet.save(ROOT / "bridge-before-after.png")


if __name__ == "__main__":
    overview("before", "before-overview.jpg")
    overview("pass2", "after-overview.jpg")
    bridge_comparison()
    print("Review sheets saved")
