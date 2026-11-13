from pathlib import Path
import subprocess,json
import imageio_ffmpeg
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1];r=ROOT/'artifacts/depth-composition-review'
frames=sorted((r/'motion-frames').glob('*.jpg'));assert len(frames)==420
ff=imageio_ffmpeg.get_ffmpeg_exe()
subprocess.run([ff,'-hide_banner','-loglevel','error','-y','-framerate','30','-i',str(r/'motion-frames/%04d.jpg'),'-c:v','libx264','-crf','20','-pix_fmt','yuv420p','-movflags','+faststart',str(r/'depth-traversal.mp4')],check=True)
subprocess.run([ff,'-hide_banner','-loglevel','error','-i',str(r/'depth-traversal.mp4'),'-f','null','-'],check=True)
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',22)
sheet=Image.new('RGB',(1280,1170),'#192a29');d=ImageDraw.Draw(sheet)
for i,n in enumerate([0,80,160,240,320,419]):
    x,y=(i%2)*640,(i//2)*390
    d.text((x+12,y+2),f'{n/30:.1f} 秒',font=font,fill='#e4e9de')
    sheet.paste(Image.open(frames[n]).resize((640,360),Image.Resampling.LANCZOS),(x,y+30))
sheet.save(r/'motion-contact-sheet.jpg',quality=94)
comparison=Image.new('RGB',(1280,1510),'#192a29');d=ImageDraw.Draw(comparison)
for i,(file,title) in enumerate([('before-midshot.png','调整前：远景空缺，前景缺少遮挡'),('final-midshot.png','调整后：近崖 / 人物 / 竹林 / 隔海群山')]):
    d.text((15,i*755+3),title,font=font,fill='#e4e9de')
    comparison.paste(Image.open(r/file).resize((1280,720),Image.Resampling.LANCZOS),(0,i*755+35))
comparison.save(r/'before-after.jpg',quality=94)
for label in ['midshot','west','bridge','east','no-dof','overcast']:
    Image.open(r/f'final-{label}.png').resize((1600,900),Image.Resampling.LANCZOS).save(r/f'preview-{label}.jpg',quality=94)
print('DEPTH_REVIEW_ENCODED 420 frames / 14 seconds; decoded without errors')
