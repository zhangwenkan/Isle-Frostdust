"""Package the rendered 24 fps introduction; do not retime character frames."""
from pathlib import Path
import subprocess

import imageio_ffmpeg
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1] / "artifacts/overhead-opening-review"
ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
subprocess.run([
    ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-framerate", "24",
    "-i", str(ROOT / "frames/%04d.jpg"), "-c:v", "libx264", "-crf", "18",
    "-preset", "medium", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
    str(ROOT / "overhead-opening.mp4"),
], check=True)

sheet = Image.new("RGB", (1278, 1056), (13, 24, 29))
draw = ImageDraw.Draw(sheet)
for index, frame in enumerate([0, 36, 72, 108, 144, 172, 195, 220, 250, 280, 312, 400]):
    image = Image.open(ROOT / f"frames/{frame:04d}.jpg")
    image = image.resize((426, 240), Image.Resampling.LANCZOS)
    x, y = index % 3 * 426, index // 3 * 264
    sheet.paste(image, (x, y))
    draw.text((x + 8, y + 242), f"{frame / 24:.2f} s", fill=(235, 235, 220))
sheet.save(ROOT / "sequence-overview.jpg", quality=94)

result = subprocess.run([
    ffmpeg, "-hide_banner", "-i", str(ROOT / "overhead-opening.mp4"), "-f", "null", "-",
], capture_output=True, text=True, check=True)
(ROOT / "video-decode-check.log").write_text(result.stderr, encoding="utf-8")
