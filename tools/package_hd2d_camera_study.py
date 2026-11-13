"""Make a compact reference sheet from the publisher's locally saved trailer."""
from pathlib import Path

import cv2
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
STUDY = ROOT / "artifacts/hd2d-character-camera-study"
font_path = "C:/Windows/Fonts/msyh.ttc"
title_font = ImageFont.truetype(font_path, 26)
body_font = ImageFont.truetype(font_path, 21)
sheet = Image.new("RGB", (1440, 535), "#172427")
draw = ImageDraw.Draw(sheet)
capture = cv2.VideoCapture(str(STUDY / "reference/sword-trailer/official-excerpt.mp4"))
items = [
    (14.75, "逸剑风云决 · 竹林探索", "观察角度稳定，镜头跟随队伍移动"),
    (28.85, "逸剑风云决 · 弯桥探索", "桥面有坡度，人物视觉上仍保持直立"),
]
for index, (time, title, note) in enumerate(items):
    capture.set(cv2.CAP_PROP_POS_MSEC, time * 1000)
    ok, frame = capture.read()
    if not ok:
        raise RuntimeError(f"Cannot read frame at {time}")
    picture = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    picture = picture.resize((720, 405), Image.Resampling.LANCZOS)
    x = index * 720
    draw.text((x + 20, 12), title, font=title_font, fill="#e5eddf")
    sheet.paste(picture, (x, 53))
    draw.text((x + 20, 470), note, font=body_font, fill="#e5eddf")
    draw.text((x + 20, 502), f"Steam 官方 Lively Open World Microvideo_EN · {time:.2f}s", font=ImageFont.truetype(font_path, 15), fill="#a5b9b6")
capture.release()
sheet.save(STUDY / "reference/wandering-sword-camera-reference.jpg", quality=93)
print(STUDY / "reference/wandering-sword-camera-reference.jpg")
