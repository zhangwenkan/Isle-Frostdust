"""Package existing game captures; does not generate or change model geometry."""
import json,hashlib,subprocess
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'artifacts/reference-cape-review'
FONT=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',21)
shots=[('forest','原横向竹林'),('exit','竹林出口'),('neck','连续坡体接到岩台'),('platform','单层岩台与篝火'),('stairs','唯一一条下行石阶'),('sand','崖脚与沙滩')]
board=Image.new('RGB',(1280,3*398),(29,35,36));draw=ImageDraw.Draw(board)
for i,(name,label) in enumerate(shots):
    x=i%2*640;y=i//2*398
    im=Image.open(OUT/f'latest-{name}.png').convert('RGB').resize((640,360),Image.Resampling.LANCZOS)
    board.paste(im,(x,y));draw.text((x+14,y+367),label,font=FONT,fill=(226,229,218))
board.save(OUT/'latest-static-contact.jpg',quality=94)
motion=json.loads((OUT/'latest-motion-check.json').read_text(encoding='utf-8'))
assert not motion['failures'] and motion['stages_completed']==len(motion['stages'])
frames=sorted((OUT/'latest-motion-frames').glob('frame-*.jpg'))
assert len(frames)==motion['frames']
ffmpeg=Path('C:/Users/51440/AppData/Local/hermes/hermes-agent/venv/Lib/site-packages/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v9.0.2.exe')
assert ffmpeg.is_file()
subprocess.run([str(ffmpeg),'-hide_banner','-loglevel','error','-y','-framerate','12','-i',str(OUT/'latest-motion-frames/frame-%04d.jpg'),'-c:v','libx264','-crf','19','-pix_fmt','yuv420p','-movflags','+faststart',str(OUT/'latest-review-motion.mp4')],check=True)
sheet=Image.new('RGB',(1280,4*260),(29,35,36));draw=ImageDraw.Draw(sheet)
for i in range(8):
    index=round(i*(len(frames)-1)/7);x=i%2*640;y=i//2*260
    im=Image.open(frames[index]).resize((640,228),Image.Resampling.LANCZOS);sheet.paste(im,(x,y))
    draw.text((x+12,y+232),f'{index/12:.1f} 秒',font=FONT,fill=(226,229,218))
sheet.save(OUT/'latest-motion-contact.jpg',quality=93)
paths=['assets/layered_island/layered_island.blend','assets/layered_island/layered_island.glb','assets/layered_island/layout.json','scripts/layered_island.gd','scripts/reference_cape_life.gd','shaders/layered_sea.gdshader']
preserved=json.loads((OUT/'geometry-preservation.json').read_text(encoding='utf-8'))
audit=json.loads((OUT/'blender-audit.json').read_text(encoding='utf-8'))
assert not audit['failures']
data={'date':'2026-11-18','continued_thread':'01a1edab-d2f0-7e03-86ba-c7391bcddea9','status':'integrated playable revision, awaiting user art review','assets':{p:{'sha256':hashlib.sha256((ROOT/p).read_bytes()).hexdigest(),'size':(ROOT/p).stat().st_size} for p in paths},'source_reference':'reference/user-cape.png','capture_prefix':'latest','motion':motion,'preservation':{k:v for k,v in preserved.items() if k!='new_objects'},'blender_audit':{'route_samples':audit['route_samples'],'meshes':len(audit['meshes']),'seam_max_distance':max(v['error'] for v in audit['seam_samples']),'grass_root_max_distance':max(audit['grass_root_errors']),'failures':audit['failures']}}
(OUT/'delivery-manifest.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'frames':len(frames),'duration_seconds':len(frames)/12,'route_samples':audit['route_samples'],'protected_objects':preserved['protected_objects'],'failures':audit['failures']}))
