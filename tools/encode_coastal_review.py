"""Encode rendered Godot frames and prepare a visual review sheet."""
from pathlib import Path
import json
import subprocess
import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageFont

root = Path(__file__).resolve().parents[1]
review = root/'artifacts/water-light-review'
ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
frames = sorted((review/'motion-frames').glob('*.jpg'))
assert len(frames) == 540, f'Incomplete movie: {len(frames)} frames'
subprocess.run([ffmpeg, '-hide_banner', '-loglevel', 'warning', '-y', '-framerate', '30',
    '-i', str(review/'motion-frames/%04d.jpg'), '-c:v', 'libx264', '-crf', '20',
    '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(review/'water-light-motion.mp4')], check=True)
subprocess.run([ffmpeg, '-hide_banner', '-loglevel', 'error', '-i', str(review/'water-light-motion.mp4'),
    '-f', 'null', '-'], check=True)
font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 22)
sheet = Image.new('RGB', (1280, 3*390), '#152a30')
draw = ImageDraw.Draw(sheet)
for i, frame in enumerate([0, 210, 240, 330, 419, 539]):
    x, y = (i%2)*640, (i//2)*390
    draw.text((x+10,y+1), f'{frame/30:.1f} 秒', font=font, fill='#edf5f0')
    sheet.paste(Image.open(frames[frame]).resize((640,360),Image.Resampling.LANCZOS),(x,y+30))
sheet.save(review/'motion-contact-sheet.jpg',quality=93)
for suffix in ['midshot','bridge','east','water-detail','water-detail-later','overcast','afternoon']:
    p = review/f'final-{suffix}.png'
    if not p.exists():
        continue
    Image.open(p).resize((1280,720),Image.Resampling.LANCZOS).save(review/f'preview-{suffix}.jpg',quality=94)
before = Image.open(review/'before-midshot.png').convert('RGB').resize((1280,720),Image.Resampling.LANCZOS)
after = Image.open(review/'final-midshot.png').convert('RGB').resize((1280,720),Image.Resampling.LANCZOS)
comparison = Image.new('RGB',(1280,1510),'#152a30')
draw = ImageDraw.Draw(comparison)
draw.text((16,5),'修改前 · 规则远海横纹，光照偏平',font=font,fill='white')
draw.text((16,760),'修改后 · 不规则水波、方向日照与柔和树影',font=font,fill='white')
comparison.paste(before,(0,35)); comparison.paste(after,(0,790))
comparison.save(review/'before-after.jpg',quality=94)
a = np.asarray(Image.open(review/'final-water-detail.png')).astype(float)
b = np.asarray(Image.open(review/'final-water-detail-later.png')).astype(float)
metrics = {'fixed_camera_water_frame_mean_difference_8bit':float(np.abs(a-b).mean()),
    'encoded_frames':540, 'duration_seconds':18, 'movie_decoded_without_errors':True}
(review/'visual-verification.json').write_text(json.dumps(metrics,indent=2),encoding='utf-8')
print(json.dumps(metrics,indent=2))
