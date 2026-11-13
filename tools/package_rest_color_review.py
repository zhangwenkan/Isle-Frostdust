from pathlib import Path
import json
import re
import subprocess

import cv2
import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'artifacts/rest-rise-color-review'
FONT = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 22)
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()


def verify_packaged_frames():
    resource = (ROOT / 'assets/characters/rest_rise_right/color_matched/rest_rise_color_matched.tres').read_text(encoding='utf8')
    atlas_refs = dict((key, ROOT / path.removeprefix('res://')) for path, key in re.findall(r'\[ext_resource type="Texture2D" path="([^"]+)" id="([^"]+)"\]', resource))
    atlases = {key: Image.open(path).convert('RGBA') for key, path in atlas_refs.items()}
    regions = re.findall(r'\[sub_resource type="AtlasTexture" id="Frame_(\d+)"\]\s+atlas = ExtResource\("(\d+)"\)\s+region = Rect2\((\d+), (\d+), (\d+), (\d+)\)', resource)
    assert len(regions) == 103
    changed = []
    for frame, atlas, x, y, w, h in regions:
        frame, x, y, w, h = map(int, [frame, x, y, w, h])
        actual = np.array(atlases[atlas].crop((x, y, x+w, y+h)))
        source = np.array(Image.open(ROOT / f'artifacts/interaction-rest-rise-review/review-chin/hero/transparent_png/frame_{frame:03}.png'))
        assert np.array_equal(actual[:, :, 3], source[:, :, 3])
        ink = source[:, :, :3].max(axis=2) <= 16
        assert np.array_equal(actual[ink], source[ink])
        if frame <= 78:
            assert np.array_equal(actual, source)
        elif not np.array_equal(actual, source):
            changed.append(frame)
    build = json.loads((OUT/'asset-verification.json').read_text(encoding='utf8'))
    assert changed == [r['frame'] for r in build['records'] if r['changed_pixels']>0], changed
    return {'resource_regions_checked':103, 'alpha_and_ink_preserved':True, 'unchanged_frames':f'0–{changed[0]-1}', 'changed_frames':changed}


def main():
    report = verify_packaged_frames()
    # Only matched, near-stationary painted interiors; exclude silhouettes, ink and green ground.
    before = np.array(Image.open(OUT / 'before-frames/101.png')).astype(np.float32)
    after = np.array(Image.open(OUT / 'after-frames/101.png')).astype(np.float32)
    idle = np.array(Image.open(OUT / 'after-frames/102.png')).astype(np.float32)
    sl = np.s_[355:620, 940:1025, :3]
    b, a, t = [cv2.GaussianBlur(x[sl], (3, 3), 0) for x in [before, after, idle]]
    mask = ((b[:,:,0] > b[:,:,1]+3) & (t[:,:,0] > t[:,:,1]+3) & (b.min(axis=2)>35) & (t.min(axis=2)>35))
    mask = cv2.erode(mask.astype(np.uint8), np.ones((3,3),np.uint8)).astype(bool)
    mask &= np.max(np.abs(b-t),axis=2)<20
    report.update({'runtime_color_sample_pixels':int(mask.sum()), 'runtime_before_rgb_bias':(t[mask]-b[mask]).mean(axis=0).tolist(), 'runtime_after_rgb_bias':(t[mask]-a[mask]).mean(axis=0).tolist()})
    traces = {p:json.loads((OUT/f'{p}-runtime.json').read_text(encoding='utf8')) for p in ['before','after']}
    for trace in traces.values():
        assert trace[7]['capture_frame'] == 101 and trace[7]['sprite_frame'] == 102
        assert trace[8]['animation'] == 'idle_right'
        for prop in ['modulate','offset','pixel_size','shaded']:
            assert len({str(r[prop]) for r in trace}) == 1, prop
    report['render_settings_constant_across_switch'] = True
    frames = []
    for frame in range(80,145):
        board = Image.new('RGB',(720,600),'#22302f')
        draw = ImageDraw.Draw(board)
        for i, (phase, label) in enumerate([('before','调整前'),('after','调整后')]):
            im = Image.open(OUT / f'{phase}-frames/{frame:03}.png')
            board.paste(im.crop((900,345,1080,625)).resize((360,560),Image.Resampling.NEAREST),(i*360,40))
            draw.text((i*360+12,7),label,font=FONT,fill='#eee6d3')
        frames.append(board)
    frames[0].save(OUT/'transition-comparison.gif',save_all=True,append_images=frames[1:],duration=[42,42,41]*21+[42,42],loop=0,disposal=2)
    movie = OUT/'transition-comparison.mp4'
    writer = imageio_ffmpeg.write_frames(str(movie),(720,600),fps=24,codec='libx264',quality=8,macro_block_size=1)
    writer.send(None)
    for frame in frames:
        writer.send(np.asarray(frame))
    writer.close()
    contact = Image.new('RGB',(1080,660),'#22302f')
    draw = ImageDraw.Draw(contact)
    for row, phase in enumerate(['before','after']):
        for col, frame in enumerate([100,101,102]):
            x,y=col*360,row*330
            draw.text((x+8,y+6),f'{"调整前" if row==0 else "调整后"} · {"尾帧" if frame<102 else "原待机"}',font=FONT,fill='#eee6d3')
            im=Image.open(OUT/f'{phase}-frames/{frame:03}.png')
            contact.paste(im.crop((930,350,1030,445)).resize((300,285),Image.Resampling.NEAREST),(x+25,y+40))
    contact.save(OUT/'runtime-cut-comparison.png')
    for log in ['before-errors.log','after-errors.log','import-errors.log']:
        assert not (OUT/log).read_text(encoding='utf8').strip(),log
    report['error_logs_empty']=True
    opening = OUT/'opening'
    if (opening/'verification.json').exists():
        assert not (opening/'capture-errors.log').read_text(encoding='utf8').strip()
        subprocess.run([FFMPEG,'-hide_banner','-loglevel','error','-y','-framerate','24','-i',str(opening/'frames/%04d.jpg'),'-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(opening/'opening-after-color-match.mp4')],check=True)
        subprocess.run([FFMPEG,'-hide_banner','-loglevel','error','-i',str(opening/'opening-after-color-match.mp4'),'-f','null','-'],check=True)
        report['opening_integration_verified']=True
    (OUT/'runtime-verification.json').write_text(json.dumps(report,indent=2),encoding='utf8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    main()
