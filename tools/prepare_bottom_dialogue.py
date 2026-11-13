"""Prepare the user's wide frame and shoulder portrait without repainting them."""
from pathlib import Path
import hashlib
import json
import shutil

import cv2
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / 'artifacts/bottom-dialogue-review'
FRAME = Path('C:/Users/51440/Downloads/像素武侠空白对话框UI素材.png')
PORTRAIT = Path('C:/Users/51440/Desktop/图片资源/孤屿霜尘/安戾行/定稿.png')
DESIGN = Path('C:/Users/51440/Desktop/图片资源/孤屿霜尘/菜单/像素武侠对话UI设计.png')
for folder in (REVIEW / 'reference', REVIEW / 'backup'):
    folder.mkdir(parents=True, exist_ok=True)
for relative in ('scenes/ui/an_lixing_dialogue.tscn',
                 'scripts/dialogue/portrait_dialogue.gd',
                 'narrative/dialogue/an_lixing_after_rest.tres'):
    backup = REVIEW / 'backup' / relative
    backup.parent.mkdir(parents=True, exist_ok=True)
    if not backup.exists():
        shutil.copy2(ROOT / relative, backup)
for source in (FRAME, PORTRAIT, DESIGN):
    shutil.copy2(source, REVIEW / 'reference' / source.name)


def rgba_from_mask(rgb, outside):
    result = np.dstack((rgb, np.where(outside, 0, 255).astype(np.uint8)))
    result[outside, :3] = 0
    assert np.array_equal(result[~outside, :3], rgb[~outside])
    return Image.fromarray(result)


frame_rgb = np.array(Image.open(FRAME).convert('RGB'))
v = frame_rgb.astype(np.int16)
neutral = (v.min(axis=2) >= 145) & (np.ptp(v, axis=2) <= 16)
_, labels = cv2.connectedComponents(neutral.astype(np.uint8), 8)
frame = rgba_from_mask(frame_rgb, labels == labels[0, 0])
frame_crop = frame.getbbox()
frame = frame.crop(frame_crop)
frame.save(ROOT / 'assets/ui/dialogue/pixel_wuxia/wide_frame.png')

portrait_rgb = np.array(Image.open(PORTRAIT).convert('RGB'))
v = portrait_rgb.astype(np.int16)
neutral = ((v.min(axis=2) >= 165) & (np.ptp(v, axis=2) <= 24)).astype(np.uint8)
count, labels, stats, centers = cv2.connectedComponentsWithStats(neutral, 8)
outside = np.zeros(neutral.shape, dtype=bool)
removed = []
for label in range(1, count):
    x, y, width, height, area = [int(n) for n in stats[label]]
    cx, cy = centers[label]
    touches_edge = x == 0 or y == 0 or x + width == neutral.shape[1] or y + height == neutral.shape[0]
    # Protect the whole face, including isolated whites and glints in both eyes.
    inside_face = 400 < cx < 1000 and 425 < cy < 925
    if touches_edge or (area > 24 and not inside_face):
        outside[labels == label] = True
        removed.append({'bbox': [x, y, width, height], 'area': area})
portrait = rgba_from_mask(portrait_rgb, outside)
portrait.save(ROOT / 'assets/ui/portraits/an_lixing_bust_transparent.png')
# Crop below the shoulders; leave all retained pixels at their original scale.
portrait_crop = (0, 32, 1536, 1376)
shoulders = portrait.crop(portrait_crop)
shoulders.save(ROOT / 'assets/ui/portraits/an_lixing_shoulders.png')

proof = Image.new('RGB', (1280, 740), '#203d47')
for i, bg in enumerate(('#203d47', '#eadfc7')):
    panel = Image.new('RGBA', (640, 740), bg)
    small_frame = frame.copy()
    small_frame.thumbnail((620, 180), Image.Resampling.NEAREST)
    panel.alpha_composite(small_frame, (10, 20))
    small_portrait = shoulders.copy()
    small_portrait.thumbnail((570, 540), Image.Resampling.NEAREST)
    panel.alpha_composite(small_portrait, ((640 - small_portrait.width) // 2, 190))
    proof.paste(panel.convert('RGB'), (i * 640, 0))
proof.save(REVIEW / 'alpha-review.png')

report = {
    'sources': [{'path': str(p), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest(),
                 'mode': Image.open(p).mode, 'size': Image.open(p).size} for p in (FRAME, PORTRAIT, DESIGN)],
    'frame_crop': frame_crop, 'frame_output_size': frame.size,
    'portrait_crop': portrait_crop, 'portrait_output_size': shoulders.size,
    'removed_portrait_regions': removed, 'opaque_rgb_preserved': True,
    'portrait_eye_area_alpha_min': int(np.asarray(portrait)[515:565, 465:790, 3].min()),
    'operations': 'Remove neutral checker matte, crop only; no RGB repainting or resampling.'
}
(REVIEW / 'asset-manifest.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({k: v for k, v in report.items() if k != 'removed_portrait_regions'}, ensure_ascii=True))
