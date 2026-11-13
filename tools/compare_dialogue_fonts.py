"""Compare the supplied brush font and downloaded Traditional Chinese fonts."""
from pathlib import Path
import hashlib
import json
import logging
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / 'artifacts/pixel-dialogue-font-review'
sys.path.insert(0, str(REVIEW / 'python-deps'))
from fontTools.ttLib import TTFont
logging.getLogger('fontTools').setLevel(logging.ERROR)

FONTS = [
    ('A', '一點顏體', REVIEW / 'candidates/i-yan.ttf'),
    ('B', '王漢宗中行書繁', REVIEW / 'candidates/wang-xingshu.ttf'),
    ('C', '演示夏行楷（用户提供）', REVIEW / 'candidates/yanshi-xiaxingkai.ttf'),
    ('D', '全字庫正楷體', REVIEW / 'candidates/tw-kai.ttf'),
]
REFERENCE = '……既已至此，便不再遲疑。天色不早，我們即刻上路，趕在雨前出山。'
LINES = ['安戾行　昨天竟然一不小心睡著了，太陽都曬屁股了，',
         '趕緊去找師傅吧，不然又要被他老人家說了。']
LABEL = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 25)
SMALL = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 21)
fonts = [item for item in FONTS if item[2].exists()]
if not fonts:
    print('Historical font candidates were removed after the final selection; retained previews are in artifacts/pixel-dialogue-font-review/.')
    raise SystemExit(0)
canvas = Image.new('RGB', (1440, 200 + 220 * len(fonts)), '#f2e7d3')
draw = ImageDraw.Draw(canvas)
draw.text((26, 8), '原参考图：笔锋与字重对照', font=LABEL, fill='#49382a')
reference = Image.open(REVIEW.parent / 'pixel-dialogue-review/reference/像素武侠对话UI设计.png')
canvas.paste(reference.crop((250, 865, 1400, 995)), (25, 48))
report = []

for i, (letter, name, path) in enumerate(fonts):
    tt = TTFont(path)
    cmap = tt.getBestCmap()
    missing = ''.join(dict.fromkeys(c for c in ''.join(LINES) if not c.isspace() and ord(c) not in cmap))
    missing_ref = ''.join(dict.fromkeys(c for c in REFERENCE if ord(c) not in cmap))
    y = 200 + i * 220
    draw.line((24, y - 6, 1416, y - 6), fill='#c8b595', width=1)
    draw.text((26, y + 4), letter + ' · ' + name, font=LABEL, fill='#773f30')
    coverage = '当前繁体台词无缺字' if not missing else '当前繁体台词缺字：' + missing
    draw.text((660, y + 8), coverage, font=SMALL, fill='#3c6551' if not missing else '#a33529')
    font = ImageFont.truetype(str(path), 43)
    draw.text((26, y + 50), REFERENCE, font=font, fill='#17100b')
    for line_no, text in enumerate(LINES):
        # Raw font only: missing glyphs stay visible, never silently fall back.
        draw.text((26, y + 105 + 48 * line_no), text, font=font, fill='#17100b')
    report.append({'id': letter, 'label': name, 'path': str(path),
                   'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                   'font_family': tt['name'].getDebugName(1),
                   'mapped_characters': len(cmap), 'missing_dialogue': missing,
                   'missing_reference': missing_ref, 'system_fallback': False})

canvas.save(REVIEW / 'traditional-font-comparison.png')
(REVIEW / 'font-coverage.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(report, ensure_ascii=True, indent=2))
