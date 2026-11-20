from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps
import json,hashlib,subprocess
import imageio_ffmpeg
R=Path(__file__).resolve().parents[1];O=R/'artifacts/forest-rocky-terminus-rework'
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',23)
def panel(path,label):
    canvas=Image.new('RGB',(960,594),(35,39,35));im=Image.open(path).convert('RGB');im=ImageOps.contain(im,(960,540),Image.Resampling.LANCZOS)
    canvas.paste(im,((960-im.width)//2,(540-im.height)//2));ImageDraw.Draw(canvas).text((20,553),label,font=font,fill=(235,233,212));return canvas
im=Image.new('RGB',(1920,594));im.paste(panel(O/'../forest-rocky-terminus-review/current-camp.png','修改前实机'),(0,0));im.paste(panel(O/'review-camp.png','本轮实机：形体修订，仍待评价'),(960,0));im.save(O/'before-after.png')
im=Image.new('RGB',(1920,594));im.paste(panel(O/'../forest-rocky-terminus-study/reference/user-forest-coast.png','用户参考原图'),(0,0));im.paste(panel(O/'review-overview.png','当前宽取景实机：仍有明显差距'),(960,0));im.save(O/'reference-current.png')
check=json.loads((O/'review-motion-check.json').read_text(encoding='utf8'))
assert not check['failures'] and check['stages_completed']==4
assert len(list((O/'review-motion-frames').glob('frame-*.jpg')))==check['frames']
ff=imageio_ffmpeg.get_ffmpeg_exe()
subprocess.run([ff,'-y','-framerate','12','-i',str(O/'review-motion-frames/frame-%04d.jpg'),'-c:v','libx264','-crf','19','-pix_fmt','yuv420p','-movflags','+faststart',str(O/'review-motion.mp4')],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
manifest={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [R/'assets/layered_island/layered_island.blend',R/'assets/layered_island/layered_island.glb',R/'assets/layered_island/layout.json',R/'assets/layered_island/rocky_terminus/floor.png',R/'scripts/layered_island.gd']}
(O/'delivery-manifest.json').write_text(json.dumps({'sha256':manifest,'motion':check,'art_status':'Revision presented for user evaluation; reference fidelity not achieved'},indent=2),encoding='utf8')
print(json.dumps({'motion_seconds':check['duration_seconds'],'frames':check['frames'],'errors':check['failures'],'comparison':['before-after.png','reference-current.png']},ensure_ascii=False))
