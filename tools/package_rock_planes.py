from pathlib import Path
import json,subprocess,sys
from PIL import Image,ImageDraw,ImageFont
import imageio_ffmpeg
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'artifacts/rock-plane-light-review'
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',23)
for view in ['forest','main-detail','entry']:
    sheet=Image.new('RGB',(1280,1512),'#203638');d=ImageDraw.Draw(sheet)
    for row,(phase,title) in enumerate([('before','调整前：过软的块面与零散皴线'),('review','调整后：干净块面、统一方向的明暗与少量折边提亮')]):
        d.text((16,row*756+5),title,font=font,fill='#eee6d5')
        sheet.paste(Image.open(OUT/(f'{phase}-main-detail.png' if view=='main-detail' else f'{phase}-original-{view}.png')),(0,row*756+36))
    sheet.save(OUT/f'before-after-{view}.jpg',quality=94)
if '--stills' in sys.argv:raise SystemExit(0)
ff=imageio_ffmpeg.get_ffmpeg_exe()
for mode in ['original','sunset']:
    frames=sorted((OUT/f'{mode}-frames').glob('*.jpg'))
    assert len(frames)==440,(mode,len(frames))
    video=OUT/f'{mode}-walk-idle-return-22s.mp4'
    subprocess.run([ff,'-hide_banner','-loglevel','error','-y','-framerate','20','-i',str(OUT/f'{mode}-frames/%04d.jpg'),'-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(video)],check=True)
    subprocess.run([ff,'-hide_banner','-loglevel','error','-i',str(video),'-f','null','-'],check=True)
    contact=Image.new('RGB',(1280,1200),'#203638');d=ImageDraw.Draw(contact)
    for i,n in enumerate([0,90,140,200,300,410]):
        x=(i%2)*640;y=(i//2)*400
        d.text((x+10,y+3),f'{mode} · {n/20:g} 秒',font=font,fill='#eee6d5')
        contact.paste(Image.open(frames[n]).resize((640,360)),(x,y+40))
    contact.save(OUT/f'{mode}-motion-contact.jpg',quality=94)
for name in ['import-errors.log','review-errors.log','motion-errors.log']:
    assert (OUT/name).stat().st_size==0,name
report={'videos':{'modes':['original','sunset'],'frames_each':440,'fps':20,'seconds_each':22,'time_scale':1,'decoded_successfully':True},'errors_empty':True}
(OUT/'video-verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report))
