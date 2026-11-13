"""Encode the fixed-camera cloud/water review and compare real rendered frames."""
from pathlib import Path
import json, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg

ROOT = Path(__file__).resolve().parents[1]
r = ROOT / 'artifacts/cloud-water-review'
font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 21)
labels = ['midshot', 'bridge', 'east', 'bridge-later', 'horizon-detail', 'low-angle', 'overcast', 'afternoon']
for label in labels:
    im = Image.open(r / f'final-{label}.png')
    assert im.size == (2560, 1440)
    im.thumbnail((1280, 720), Image.Resampling.LANCZOS)
    im.convert('RGB').save(r / f'preview-{label}.jpg', quality=90)

comparison = Image.new('RGB', (1280, 1512), '#192a29')
d = ImageDraw.Draw(comparison)
for i, (file, title) in enumerate([
    (ROOT / 'artifacts/misty-peaks-review/final-bridge.png', '修改前：灰色雾带与海面分离'),
    (r / 'final-bridge.png', '本轮：远海逐渐融入蓝灰海雾，天空双层云缓慢流动'),
]):
    d.text((14, i * 756 + 6), title, font=font, fill='#e4e9de')
    comparison.paste(Image.open(file).resize((1280, 720), Image.Resampling.LANCZOS), (0, i * 756 + 36))
comparison.save(r / 'before-after-bridge.jpg', quality=90)

frames = sorted((r / 'motion-frames').glob('*.jpg'))
assert len(frames) == 540
assert (r / 'final-errors.log').stat().st_size == 0
assert (r / 'motion-errors.log').stat().st_size == 0
ff = imageio_ffmpeg.get_ffmpeg_exe()
movie = r / 'moving-clouds-and-sea.mp4'
subprocess.run([ff, '-hide_banner', '-loglevel', 'error', '-y', '-framerate', '30', '-i', str(r / 'motion-frames/%04d.jpg'), '-c:v', 'libx264', '-crf', '20', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(movie)], check=True)
subprocess.run([ff, '-hide_banner', '-loglevel', 'error', '-i', str(movie), '-f', 'null', '-'], check=True)

sheet = Image.new('RGB', (1280, 456), '#192a29')
d = ImageDraw.Draw(sheet)
for i, n in enumerate([0, 180, 360, 539]):
    x, y = (i % 2) * 640, (i // 2) * 228
    d.text((x + 12, y + 2), f'{n / 30:.1f} 秒 / 天空与海雾', font=font, fill='#e4e9de')
    sheet.paste(Image.open(frames[n]).crop((0, 0, 1280, 396)).resize((640, 198), Image.Resampling.LANCZOS), (x, y + 30))
sheet.save(r / 'cloud-motion-contact-sheet.jpg', quality=91)

# This sky-only rectangle avoids the mountain silhouettes, water, and bamboo.
roi = (420, 5, 700, 55)
skies = [np.asarray(Image.open(p).crop(roi).convert('RGB'), dtype=np.float32) for p in frames]
frame_changes = [float(np.mean(np.abs(a - b))) for a, b in zip(skies, skies[1:])]
first_last = float(np.mean(np.abs(skies[0] - skies[-1])))
assert first_last > 0.3, 'Sky is static'
report = {
    'sky_roi_xyxy': roi,
    'first_last_mean_rgb_difference_0_255': first_last,
    'adjacent_frame_mean_difference_median': float(np.median(frame_changes)),
    'adjacent_frame_mean_difference_max': float(max(frame_changes)),
    'sky_longitude_degrees_per_second': [0.162, 0.0972],
    'video_frames': len(frames),
    'video_duration_seconds': 18,
    'time_scale': 1,
    'interpretation': 'The sky-only region moves continuously; values measure image change, not artistic acceptance.',
}
(r / 'cloud-motion-audit.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report, indent=2))
