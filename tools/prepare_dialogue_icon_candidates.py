"""Stage downloaded pixel art for user selection; do not set the production icon."""
from pathlib import Path
import json
import hashlib
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'artifacts/wuxia-dialogue-review/icon-candidates'
choices = [
    ('A', '細刃金鍔劍', 'dcss/32x32/sabre/sabre_02.png', 'Dungeon Crawl Stone Soup', False),
    ('B', '素柄弧刀', 'dcss/32x32/falchion/falchion_04.png', 'Dungeon Crawl Stone Soup', False),
    ('C', '青鋼直劍', '7soul1/32x32/sword_08.png', '7Soul1 / Henrique Lazarini', True),
    ('D', '金鍔長劍', 'dcss/32x32/long_sword/long_sword_02.png', 'Dungeon Crawl Stone Soup', False),
    ('E', '短刃', '7soul1/32x32/dagger_04.png', '7Soul1 / Henrique Lazarini', True),
    ('F', '碧玉柄劍', 'buch/32x32/sword_01_full_green_gem.png', 'Buch', True),
]
(OUT / 'prepared').mkdir(exist_ok=True)
manifest = []
font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 24)
small = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 17)
sheet = Image.new('RGB', (1200, 660), '#e0d2b1')
draw = ImageDraw.Draw(sheet)
for i, (letter, title, relative, author, mirror) in enumerate(choices):
    source = OUT / relative
    icon = Image.open(source).convert('RGBA')
    assert icon.size == (32, 32)
    if mirror:
        icon = icon.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    icon.save(OUT / 'prepared' / f'{letter}.png')
    tile = Image.new('RGBA', (128, 66))
    tile.alpha_composite(icon.resize((64, 64), Image.Resampling.NEAREST), (32, 1))
    tile.save(OUT / 'prepared' / f'{letter}-button.png')
    x, y = i % 3 * 400, i // 3 * 330
    draw.rectangle((x + 14, y + 14, x + 386, y + 316), fill='#e9dec3', outline='#8d805d', width=1)
    draw.text((x + 32, y + 28), f'{letter}  {title}', font=font, fill='#33291e')
    large = icon.resize((128, 128), Image.Resampling.NEAREST)
    sheet.paste(large, (x + 56, y + 94), large)
    sheet.paste(tile, (x + 222, y + 124), tile)
    draw.text((x + 61, y + 230), '放大細節 ×4', font=small, fill='#77684b')
    draw.text((x + 222, y + 230), '遊戲大小 ×2', font=small, fill='#77684b')
    draw.text((x + 32, y + 276), '來源：' + author.split('/')[0].strip(), font=small, fill='#77684b')
    manifest.append({'id':letter,'label':title,'source_file':relative,'author':author,'license':'CC0',
        'source_page':'https://opengameart.org/content/cc0-sword-icons','source_size':[32,32],
        'display_scale':2,'horizontal_flip':mirror,'recolored':False,'production_selected':False,
        'sha256':hashlib.sha256(source.read_bytes()).hexdigest()})
(OUT / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf8')
sheet.save(OUT / 'pixel-weapon-options.png')
print('Prepared six options with exact integer nearest-neighbour scaling.')
