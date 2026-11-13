from pathlib import Path
import json,subprocess,shutil
from PIL import Image,ImageDraw,ImageFont
import imageio_ffmpeg

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'artifacts/colored-ink-sample-review'
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',23)
sheet=Image.new('RGB',(1280,1512),'#203638');d=ImageDraw.Draw(sheet)
for row,(path,title) in enumerate([
    (OUT/'backup/clouds-v3-original-forest.png','修改前：钓鱼参考阶段的地表与圆润石头'),
    (OUT/'review-original-forest.png','西岸样区：新地表笔触、结构线与局部形体调整'),
]):
    d.text((16,row*756+5),title,font=font,fill='#eee6d5');sheet.paste(Image.open(path),(0,row*756+36))
sheet.save(OUT/'before-after.jpg',quality=94)
ff=imageio_ffmpeg.get_ffmpeg_exe()
for mode in ['original','sunset']:
    frames=sorted((OUT/f'{mode}-frames').glob('*.jpg'))
    assert len(frames)==360,(mode,len(frames))
    video=OUT/f'{mode}-walk-idle-return-18s.mp4'
    subprocess.run([ff,'-hide_banner','-loglevel','error','-y','-framerate','20','-i',str(OUT/f'{mode}-frames/%04d.jpg'),'-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(video)],check=True)
    subprocess.run([ff,'-hide_banner','-loglevel','error','-i',str(video),'-f','null','-'],check=True)
    contact=Image.new('RGB',(1280,800),'#203638');d=ImageDraw.Draw(contact)
    for i,n in enumerate([0,100,180,300]):
        x=(i%2)*640;y=(i//2)*400
        d.text((x+10,y+3),f'{mode} · {n/20:g} 秒',font=font,fill='#eee6d5')
        contact.paste(Image.open(frames[n]).resize((640,360)),(x,y+40))
    contact.save(OUT/f'{mode}-motion-contact.jpg',quality=94)
for name in ['import-errors.log','review-errors.log','motion-errors.log']:
    assert (OUT/name).stat().st_size==0,name
report={'videos':{'modes':['original','sunset'],'frames_each':360,'fps':20,'seconds_each':18,'time_scale':1,'decoded_successfully':True},'errors_empty':True}
(OUT/'video-verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report))
