from pathlib import Path
import json,subprocess
from PIL import Image,ImageDraw,ImageFont
import imageio_ffmpeg
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'artifacts/cape-road-alignment-review'
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',24)
im=Image.new('RGB',(1280,1512),'#17282b');d=ImageDraw.Draw(im)
for i,(name,label) in enumerate([('before-lying.png','此前：斜向坡路与横向躺姿不一致'),('final-original-rise-000.png','当前：横向开场路面，平缓承托躺姿')]):
    d.text((20,i*756+5),label,font=font,fill='#e8e4d5');im.paste(Image.open(OUT/name),(0,i*756+36))
im.save(OUT/'before-after-road.jpg',quality=94)
frames=sorted((OUT/'motion-frames').glob('*.jpg'));assert len(frames)==240
ff=imageio_ffmpeg.get_ffmpeg_exe();video=OUT/'road-walk-return-12s.mp4'
subprocess.run([ff,'-hide_banner','-loglevel','error','-y','-framerate','20','-i',str(OUT/'motion-frames/%04d.jpg'),'-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(video)],check=True)
subprocess.run([ff,'-hide_banner','-loglevel','error','-i',str(video),'-f','null','-'],check=True)
contact=Image.new('RGB',(1280,1200),'#17282b');d=ImageDraw.Draw(contact)
for i,f in enumerate([0,38,64,110,150,225]):
    x=i%2*640;y=i//2*400;d.text((x+12,y+5),'%.2f 秒'%(f/20),font=font,fill='#e8e4d5')
    contact.paste(Image.open(frames[f]).resize((640,360)),(x,y+40))
contact.save(OUT/'motion-contact.jpg',quality=94)
for f in ['import-errors.log','final-errors.log','route-check-errors.log','motion-errors.log','opening/capture-errors.log']:
    assert not (OUT/f).read_text(encoding='utf-8').strip(),f
projection=json.loads((OUT/'route-projection.json').read_text(encoding='utf-8'))
assert all(abs(p['screen_angle_degrees'])<.1 for p in projection['samples'] if p['x']<=-18.5)
report={'motion_frames':240,'fps':20,'seconds':12,'video_decode_passed':True,'opening_core_horizontal':True,'final_error_logs_empty':True}
(OUT/'final-verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report))
