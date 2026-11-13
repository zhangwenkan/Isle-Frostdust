from pathlib import Path
import json,subprocess
from PIL import Image,ImageDraw,ImageFont
import imageio_ffmpeg
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'artifacts/cape-colored-ink-review'
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',24)
comparison=Image.new('RGB',(1280,1512),'#17282b');d=ImageDraw.Draw(comparison)
for row,(file,label) in enumerate([('before-original-start.png','之前：岛角使用另一套黄绿色草面'),('final-original-start.png','当前：同机位，延续左侧彩色水墨草面与灰绿岩色')]):
    d.text((20,row*756+4),label,font=font,fill='#e8e4d5')
    comparison.paste(Image.open(OUT/file),(0,row*756+36))
comparison.save(OUT/'before-after-opening.jpg',quality=94)
ff=imageio_ffmpeg.get_ffmpeg_exe()
for mode in ['original','sunset']:
    frames=sorted((OUT/f'{mode}-frames').glob('*.jpg'));assert len(frames)==360,len(frames)
    video=OUT/f'{mode}-cape-walk-return-18s.mp4'
    subprocess.run([ff,'-hide_banner','-loglevel','error','-y','-framerate','20','-i',str(OUT/f'{mode}-frames/%04d.jpg'),'-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(video)],check=True)
    subprocess.run([ff,'-hide_banner','-loglevel','error','-i',str(video),'-f','null','-'],check=True)
    contact=Image.new('RGB',(1280,1200),'#17282b');d=ImageDraw.Draw(contact)
    for i,frame in enumerate([0,65,95,155,225,350]):
        x=(i%2)*640;y=(i//2)*400
        d.text((x+12,y+5),f'{mode} · {frame/20:g} 秒',font=font,fill='#e8e4d5')
        contact.paste(Image.open(frames[frame]).resize((640,360)),(x,y+40))
    contact.save(OUT/f'{mode}-motion-contact.jpg',quality=94)
for name in ['focus-check-errors.log','pass1-errors.log','motion-errors.log']:
    assert (OUT/name).stat().st_size==0,name
report={'modes':2,'frames_each':360,'fps':20,'seconds_each':18,'decoded_successfully':True,'runtime_errors_empty':True}
(OUT/'video-verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report))
