from pathlib import Path
import json
import subprocess

import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'artifacts/cape-road-alignment-review/opening'
frames = sorted((OUT / 'frames').glob('*.jpg'))
assert len(frames) == 360, len(frames)
ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
video = OUT / 'opening-rest-dialogue-15s.mp4'
subprocess.run([
    ffmpeg, '-hide_banner', '-loglevel', 'error', '-y', '-framerate', '24',
    '-i', str(OUT / 'frames/%04d.jpg'), '-c:v', 'libx264', '-crf', '18',
    '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(video),
], check=True)
subprocess.run([ffmpeg, '-hide_banner', '-loglevel', 'error', '-i', str(video), '-f', 'null', '-'], check=True)
font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 23)
contact = Image.new('RGB', (1280, 1200), '#17282b')
draw = ImageDraw.Draw(contact)
for i, (frame, label) in enumerate([
    (0, '岛角躺卧'), (50, '撑地起身'), (98, '右侧站定'),
    (150, '安戾行 · 第一页'), (210, '第二页'), (300, '对白结束 · 自由行走'),
]):
    x, y = i % 2 * 640, i // 2 * 400
    draw.text((x + 12, y + 7), label, font=font, fill='#e8e4d5')
    with Image.open(OUT / f'frame-{frame:03}.png') as image:
        contact.paste(image.resize((640, 360)), (x, y + 40))
contact.save(OUT / 'opening-contact.jpg', quality=94)
for name in ['capture-errors.log']:
    assert not (OUT / name).read_text(encoding='utf-8').strip(), name
report = {'frames': 360, 'fps': 24, 'seconds': 15, 'decode_passed': True, 'runtime_error_logs_empty': True}
(OUT / 'video-verification.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report))
