"""Encode and inspect the continuous gameplay review captured in Godot."""
from pathlib import Path
import json
import subprocess
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "artifacts/living-coast-review"
frames = sorted((REVIEW / "final-frames").glob("*.jpg"))
report = json.loads((REVIEW / "final-verification.json").read_text(encoding="utf-8"))
assert len(frames) == report["frames"] == 1170
assert report["flock_events"] == 1
assert report["flock_z_range"][1] - report["flock_z_range"][0] > 60
for name in ("final-errors.log", "final-motion-errors.log"):
    assert not (REVIEW / name).read_text(encoding="utf-8").strip(), name

ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
movie = REVIEW / "living-coast-walk-pause-return.mp4"
subprocess.run([ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-framerate", "30",
                "-i", str(REVIEW / "final-frames/%04d.jpg"), "-c:v", "libx264", "-crf", "18",
                "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(movie)], check=True)
subprocess.run([ffmpeg, "-hide_banner", "-loglevel", "error", "-i", str(movie),
                "-f", "null", "-"], check=True)

font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 20)
sheet = Image.new("RGB", (1280, 1560), "#192a29")
draw = ImageDraw.Draw(sheet)
moments = [(0, "林内停留"), (5, "林缘散开"), (8, "鸟群进入开阔处"), (13, "桥上继续前进"),
           (18, "东岸停留"), (24, "回头向西"), (32, "林内停步，风仍在动"), (38, "再次向右，无重复惊鸟")]
for i, (seconds, label) in enumerate(moments):
    x, y = (i % 2) * 640, (i // 2) * 390
    draw.text((x + 12, y + 4), f"{seconds:02d}s · {label}", font=font, fill="#e4e9de")
    sheet.paste(Image.open(frames[seconds * 30]).resize((640, 360), Image.Resampling.LANCZOS), (x, y + 30))
sheet.save(REVIEW / "motion-contact-sheet.jpg", quality=93)

idle = Image.new("RGB", (1350, 340), "#192a29")
draw = ImageDraw.Draw(idle)
for i, seconds in enumerate((31, 33, 34.5)):
    draw.text((i * 450 + 8, 4), f"停步中 {seconds:g}s", font=font, fill="#e4e9de")
    crop = Image.open(frames[int(seconds * 30)]).crop((60, 5, 510, 315))
    idle.paste(crop, (i * 450, 30))
idle.save(REVIEW / "idle-bamboo-contact.jpg", quality=95)

for label in ("idle-forest", "flock-departure", "bridge-paused", "east", "overcast", "bird-detail"):
    im = Image.open(REVIEW / f"final-{label}.png")
    assert im.size == (2560, 1440)
    im.thumbnail((1280, 720), Image.Resampling.LANCZOS)
    im.convert("RGB").save(REVIEW / f"preview-{label}.jpg", quality=93)

print(json.dumps({"video":str(movie), "duration":report["duration"], "frames":len(frames),
                  "flock_events":report["flock_events"], "flock_z_range":report["flock_z_range"],
                  "decode":"passed", "error_logs":"empty"}, ensure_ascii=False, indent=2))
