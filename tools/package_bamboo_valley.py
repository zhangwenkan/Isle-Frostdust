"""Package actual Godot captures; no generated or repainted game screenshots."""
from pathlib import Path
import json,subprocess
from PIL import Image,ImageDraw,ImageFont
import imageio_ffmpeg
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'artifacts/bamboo-valley-review'
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',23)
def sheet(items,target,columns=2):
    w,h=640,360;canvas=Image.new('RGB',(w*columns,(h+36)*((len(items)+columns-1)//columns)),'#1d3030');d=ImageDraw.Draw(canvas)
    for i,(label,path) in enumerate(items):
        x=(i%columns)*w;y=(i//columns)*(h+36)
        d.text((x+12,y+2),label,font=font,fill='#ede9da');canvas.paste(Image.open(path).convert('RGB').resize((w,h),Image.Resampling.LANCZOS),(x,y+36))
    canvas.save(OUT/target,quality=95)
sheet([('调整前：竹林后直接看见群山',OUT/'before-x-6.8.png'),('当前：后方谷坡与多层竹林',OUT/'final-x-6.8.png'),('谷口逐渐打开',OUT/'final-x01.5.png'),('桥上展开群山',OUT/'final-x07.8.png')],'before-after.jpg')
files=sorted((OUT/'motion-frames').glob('*.jpg'));assert len(files)==360
exe=imageio_ffmpeg.get_ffmpeg_exe();video=OUT/'bamboo-valley-walk-18s.mp4'
subprocess.run([exe,'-y','-framerate','20','-i',str(OUT/'motion-frames/%04d.jpg'),'-c:v','libx264','-crf','19','-pix_fmt','yuv420p','-movflags','+faststart',str(video)],capture_output=True,check=True)
subprocess.run([exe,'-v','error','-i',str(video),'-f','null','-'],capture_output=True,check=True)
sheet([(f'{n/20:.1f} 秒',files[n]) for n in [0,45,90,140,180,220,270,350]],'motion-contact.jpg')
for name in ['import-errors.log','final-errors.log','motion-errors.log']:
    assert not (OUT/name).read_text(encoding='utf-8-sig').strip(),name
report={'video_frames':360,'fps':20,'seconds':18,'decoded':True,'final_logs_empty':True}
(OUT/'final-verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report))
