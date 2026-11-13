"""Create compact review images and encode the verified gameplay traversal."""
from pathlib import Path
import subprocess, json
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
r = ROOT / 'artifacts/misty-peaks-review'
font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 21)
labels = ['midshot', 'west', 'bridge', 'east', 'no-dof', 'mountain-detail', 'mountain-no-clouds', 'overcast', 'afternoon']
sizes = {}
for label in labels:
    im = Image.open(r / f'final-{label}.png')
    sizes[label] = im.size
    im.thumbnail((1280, 720), Image.Resampling.LANCZOS)
    im.convert('RGB').save(r / f'preview-{label}.jpg', quality=89)

comparison = Image.new('RGB', (1280, 1512), '#192a29')
d = ImageDraw.Draw(comparison)
for i, (file, title) in enumerate([
    ('pass3-bridge.png', '接续前：较厚重的山体与均匀雾层'),
    ('final-bridge.png', '本轮：偏斜峰顶、疏散峰群与云中留白'),
]):
    d.text((14, i * 756 + 6), title, font=font, fill='#e4e9de')
    comparison.paste(Image.open(r / file).resize((1280, 720), Image.Resampling.LANCZOS), (0, i * 756 + 36))
comparison.save(r / 'before-after-bridge.jpg', quality=91)

verification = json.loads((r / 'motion-verification.json').read_text(encoding='utf-8'))
assert verification['landed_x'] > 23.0
assert (r / 'motion-errors.log').stat().st_size == 0
frames = sorted((r / 'motion-frames').glob('*.jpg'))
assert len(frames) == 420
ff = imageio_ffmpeg.get_ffmpeg_exe()
movie = r / 'misty-peaks-traversal.mp4'
subprocess.run([ff, '-hide_banner', '-loglevel', 'error', '-y', '-framerate', '30', '-i', str(r / 'motion-frames/%04d.jpg'), '-c:v', 'libx264', '-crf', '20', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(movie)], check=True)
subprocess.run([ff, '-hide_banner', '-loglevel', 'error', '-i', str(movie), '-f', 'null', '-'], check=True)
sheet = Image.new('RGB', (1280, 1170), '#192a29')
d = ImageDraw.Draw(sheet)
for i, n in enumerate([0, 80, 160, 240, 320, 419]):
    x, y = (i % 2) * 640, (i // 2) * 390
    d.text((x + 12, y + 2), f'{n / 30:.1f} 秒', font=font, fill='#e4e9de')
    sheet.paste(Image.open(frames[n]).resize((640, 360), Image.Resampling.LANCZOS), (x, y + 30))
sheet.save(r / 'motion-contact-sheet.jpg', quality=89)
(r / 'capture-sizes.json').write_text(json.dumps(sizes, indent=2), encoding='utf-8')
print('MIST_REVIEW_ENCODED', len(frames), 'frames;', sizes)
