"""Encode normal-speed gameplay captures and audit the rendered sky, not just shader text."""
from pathlib import Path
import hashlib
import json
import subprocess

import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'artifacts/procedural-sky-review'
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
FONT = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 22)


def encode(mode, section, start, count):
    video = OUT / f'{mode}-{section}-18s.mp4'
    subprocess.run([
        FFMPEG, '-hide_banner', '-loglevel', 'error', '-y',
        '-framerate', '20', '-start_number', str(start),
        '-i', str(OUT / f'{mode}-frames/%04d.jpg'), '-frames:v', str(count),
        '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p',
        '-movflags', '+faststart', str(video),
    ], check=True)
    subprocess.run([FFMPEG, '-hide_banner', '-loglevel', 'error', '-i', str(video), '-f', 'null', '-'], check=True)


audit = {'time_scale': 1, 'fps': 20, 'modes': {}}
for mode in ('original', 'sunset'):
    frames = sorted((OUT / f'{mode}-frames').glob('*.jpg'))
    assert len(frames) == 720, (mode, len(frames))
    encode(mode, 'fixed', 0, 360)
    encode(mode, 'walk', 360, 360)
    # These rectangles avoid peaks, birds, bamboo and the sunset disc.
    rois = [(430, 6, 550, 35), (660, 6, 840, 29)]
    crops = [np.concatenate([
        np.asarray(Image.open(p).crop(roi), dtype=np.float32).reshape(-1, 3)
        for roi in rois
    ]) for p in frames[:360]]
    adjacent = [float(np.abs(a-b).mean()) for a, b in zip(crops, crops[1:])]
    delta = float(np.abs(crops[-1]-crops[0]).mean())
    assert delta > .5, (mode, 'Sky is effectively static', delta)
    assert max(adjacent) < 3.0, (mode, 'Unexpected sky discontinuity', max(adjacent))
    audit['modes'][mode] = {
        'sky_rois_xyxy': rois,
        '18s_first_last_mean_rgb_difference': delta,
        'adjacent_mean_rgb_difference_median': float(np.median(adjacent)),
        'adjacent_mean_rgb_difference_max': max(adjacent),
        'video_frames': 720,
    }

sun_samples = []
for seconds in (1, 13, 25, 61, 121):
    a = np.asarray(Image.open(OUT / f'clouds-v3-sunset-bridge-{seconds:03}.png'), dtype=np.float32)
    sun_samples.append(a[34:48, 362:376].mean(axis=(0, 1)).tolist())
sun_range = np.ptp(np.asarray(sun_samples), axis=0)
assert max(sun_range) < 2.0, ('Sun was obscured', sun_range)
audit['sun'] = {'seconds': [1, 13, 25, 61, 121], 'center_mean_rgb': sun_samples, 'max_channel_variation': sun_range.tolist()}

hashes = json.loads((OUT / 'continuation-backup/asset-hashes.json').read_text(encoding='utf-8'))
for name, expected in hashes.items():
    assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest() == expected, name
audit['unchanged_asset_and_cloudsea_hashes'] = hashes
for name in ('clouds-v3-errors.log', 'motion-errors.log'):
    assert (OUT/name).stat().st_size == 0, name
audit['note'] = 'Image differences establish motion and stable sun visibility, not artistic acceptance. Cloud density is analytic; this is not a fluid simulation.'

comparison = Image.new('RGB', (1280, 1512), '#182b2c')
d = ImageDraw.Draw(comparison)
for i, (path, label) in enumerate([
    (OUT/'continuation-backup/procedural-1-bridge.png', '接续前：日轮被天空云遮淡'),
    (OUT/'clouds-v3-sunset-bridge-001.png', '本轮：夕阳显示在云层前；大云团持续变形、聚散'),
]):
    d.text((16, i*756+6), label, font=FONT, fill='#ede6d4')
    comparison.paste(Image.open(path), (0, i*756+36))
comparison.save(OUT/'sunset-before-after.jpg', quality=94)

# Enlarged inspection views are explicitly labeled and are not the gameplay camera.
sheet = Image.new('RGB', (1280, 1080), '#182b2c')
d = ImageDraw.Draw(sheet)
for row, seconds in enumerate((1, 25, 61)):
    for col, mode in enumerate(('original', 'sunset')):
        x, y = col*640, row*360
        d.text((x+12, y+5), f'{mode} · {seconds}s · 天空诊断视角', font=FONT, fill='#ede6d4')
        im = Image.open(OUT/f'clouds-v3-{mode}-sky-{seconds:03}.png').crop((0, 0, 1280, 650)).resize((640, 325))
        sheet.paste(im, (x, y+35))
sheet.save(OUT/'cloud-evolution.jpg', quality=94)
(OUT/'verification.json').write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(audit, ensure_ascii=False, indent=2))
