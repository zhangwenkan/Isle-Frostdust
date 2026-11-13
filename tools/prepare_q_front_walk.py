"""Install the reviewed Q front sprite and matching 2D contact/normal data."""
from pathlib import Path
import hashlib
import json
import shutil
import sys
import numpy as np
from PIL import Image
sys.path.insert(0, str(Path(__file__).resolve().parent))
from prepare_hero_volume import normal_image, sole_points, import_settings

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'artifacts/q-sprite-front-walk-review/review-v1'
OUT = ROOT / 'assets/characters/q_front_walk'
REVIEW = ROOT / 'artifacts/q-front-integration-review'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    REVIEW.mkdir(parents=True, exist_ok=True)
    backup = REVIEW / 'backup'
    backup.mkdir(exist_ok=True)
    for name in ('island.gd', 'hero_presentation.gd'):
        if not (backup / name).exists():
            shutil.copy2(ROOT / 'scripts' / name, backup / name)
    baseline = REVIEW / 'original-asset-hashes.json'
    if not baseline.exists():
        paths = [p for p in (ROOT/'assets/characters/green_three_walk').iterdir() if p.suffix in ('.png','.tres','.json')]
        baseline.write_text(json.dumps({str(p.relative_to(ROOT)):sha(p) for p in paths},indent=2),encoding='utf8')
    contacts = {'walk_down_q': []}
    sources = {}
    for page in range(2):
        src = SOURCE / f'spritesheet_{page:02}.png'
        target = OUT / f'q_front_{page:02}.png'
        shutil.copy2(src,target)
        import_settings(target)
        assert sha(src)==sha(target)
        sources[target.name] = {'source': str(src), 'sha256': sha(target)}
        atlas = Image.open(target).convert('RGBA')
        normals = Image.new('RGB',atlas.size,(128,128,255))
        for local in range(min(16,23-page*16)):
            x,y = (local%4)*512,(local//4)*768
            frame = atlas.crop((x,y,x+512,y+768))
            normals.paste(normal_image(frame),(x,y))
            data = sole_points(frame)
            assert len(data['feet']) == 2
            contacts['walk_down_q'].append(data)
        target_normal = OUT / f'q_front_{page:02}_normal.png'
        normals.save(target_normal)
        import_settings(target_normal)
    source_idle = Image.open(SOURCE/'reference-transparent.png').convert('RGBA')
    offset = 724-source_idle.getbbox()[3]
    idle = Image.new('RGBA',source_idle.size)
    idle.paste(source_idle,(0,offset))
    reverse = Image.new('RGBA',source_idle.size)
    reverse.paste(idle,(0,-offset))
    assert np.array_equal(np.asarray(source_idle),np.asarray(reverse))
    for name,im in [('q_front_idle.png',idle),('q_front_idle_normal.png',normal_image(idle))]:
        path=OUT/name
        im.save(path)
        import_settings(path)
    contacts['idle_down_q']=[sole_points(idle)]
    (OUT/'contacts.json').write_text(json.dumps(contacts,indent=2),encoding='utf8')
    resource=(SOURCE/'walk.tres').read_text(encoding='utf8')
    resource=resource.replace('load_steps=26','load_steps=27')
    for page in range(2):
        resource=resource.replace(f'path="spritesheet_{page:02}.png"',f'path="res://assets/characters/q_front_walk/q_front_{page:02}.png"')
    resource=resource.replace('[sub_resource type="AtlasTexture" id="Frame_0"]','[ext_resource type="Texture2D" path="res://assets/characters/q_front_walk/q_front_idle.png" id="3"]\n\n[sub_resource type="AtlasTexture" id="Frame_0"]')
    resource=resource.replace('&"walk_down"','&"walk_down_q"').replace('"speed": 24.0','"speed": 31.2')
    resource=resource.rstrip()[:-1]+', {"frames": [{"duration": 1.0, "texture": ExtResource("3")}], "loop": true, "name": &"idle_down_q", "speed": 1.0}]\n'
    (OUT/'q_front_walk.tres').write_text(resource,encoding='utf8')
    (OUT/'source.json').write_text(json.dumps({'source_review':str(SOURCE),'source_indices':list(range(23,46)),
        'frames':23,'fps':31.2,'source_fps':24,'speed_multiplier':1.3,'loop_seconds':23/31.2,
        'idle_integer_shift_y':offset,'walk_atlases_byte_identical':True,'sources':sources,
        'geometry_created':False,'normals':'Broad 2D silhouette relief, same function as existing walk assets.'},indent=2),encoding='utf8')
    print('Prepared 23 unchanged frames at 31.2fps, matching idle, 2D normals and two-foot contact data.')

if __name__=='__main__':
    main()
