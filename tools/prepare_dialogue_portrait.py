"""Remove the baked checkerboard from the user-supplied portrait, without repainting."""
from pathlib import Path
import hashlib
import json

import cv2
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path('C:/Users/51440/Desktop/图片资源/孤屿霜尘/安戾行/背景透明.png')
OUT = ROOT / 'artifacts/wuxia-dialogue-review'
DEST = ROOT / 'assets/ui/portraits/an_lixing_transparent.png'

image = Image.open(SOURCE).convert('RGB')
rgb = np.array(image)
values = rgb.astype(np.int16)
candidate = ((values.min(axis=2) >= 170) & (np.ptp(values, axis=2) < 24)).astype(np.uint8)
count, labels, stats, centers = cv2.connectedComponentsWithStats(candidate, 8)
background = np.zeros(candidate.shape, np.uint8)
removed = []
for label in range(1, count):
    x, y, width, height, area = stats[label]
    cx, cy = centers[label]
    # Large checker regions, including gaps in the hair. Keep small highlights
    # and all isolated neutral regions inside the face (especially the eyes).
    touches_edge = x == 0 or y == 0 or x + width == image.width or y + height == image.height
    inside_eyes = 390 < cx < 820 and 670 < cy < 800
    if touches_edge or (area > 24 and not inside_eyes):
        background[labels == label] = 1
        removed.append(int(area))
alpha = (1 - background) * 255
rgba = np.dstack((rgb, alpha)).astype(np.uint8)
rgba[alpha == 0, :3] = 0
Image.fromarray(rgba).save(DEST)
OUT.mkdir(exist_ok=True)
proof = Image.new('RGB', (1024, 720), '#172b34')
portrait = Image.fromarray(rgba)
portrait.thumbnail((510, 680), Image.Resampling.LANCZOS)
proof.paste(portrait, (0, 40), portrait)
paper = Image.new('RGB', (512, 720), '#e3d5b6')
paper.paste(portrait, (0, 40), portrait)
proof.paste(paper, (512, 0))
ImageDraw.Draw(proof).text((20, 15), 'Same cutout on dark and light backgrounds', fill='white')
proof.save(OUT / 'portrait-alpha-review.png')
report = {
    'source': str(SOURCE), 'source_mode': image.mode, 'size': image.size,
    'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
    'source_has_alpha': 'A' in Image.open(SOURCE).getbands(),
    'output': str(DEST.relative_to(ROOT)), 'transparent_pixels': int(background.sum()),
    'removed_component_areas': sorted(removed, reverse=True),
    'opaque_rgb_preserved': bool(np.array_equal(rgba[alpha == 255, :3], rgb[alpha == 255])),
}
(OUT / 'portrait-alpha-verification.json').write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf8')
print(json.dumps(report, ensure_ascii=False))
