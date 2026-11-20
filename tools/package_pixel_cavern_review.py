"""Package real Godot captures; no retouching of delivered images."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,subprocess
root=Path(__file__).resolve().parents[1]
p=root/'artifacts/pixel-cavern-coast-review'
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',22)
canvas=Image.new('RGB',(1280,1000),'#223030');d=ImageDraw.Draw(canvas)
for i,(name,label) in enumerate([('game-bamboo-stairs.png','竹林、桥头与沙湾石阶'),('game-bridge-cavern.png','吊桥、根藤与洞内石阶')]):
    im=Image.open(p/name).resize((640,480),Image.Resampling.NEAREST)
    x=i*640
    canvas.paste(im,(x,42));d.text((x+16,9),label,font=font,fill='#e6e9d9')
overview=Image.open(p/'game-overview.png').resize((640,480),Image.Resampling.NEAREST)
canvas.paste(overview,(320,520));canvas.save(p/'review-contact-sheet.png')
frames=sorted((p/'motion').glob('*.png'))
if len(frames)==24:
    sheet=Image.new('RGB',(1280,1008),'#223030');d=ImageDraw.Draw(sheet)
    for i,j in enumerate([0,7,15,23]):
        im=Image.open(frames[j]).resize((640,480),Image.Resampling.NEAREST)
        x=(i%2)*640;y=(i//2)*504
        sheet.paste(im,(x,y+24));d.text((x+12,y),f'frame {j}',font=font,fill='white')
    sheet.save(p/'motion-contact-sheet.png')
    import imageio_ffmpeg
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-y','-framerate','12','-i',str(p/'motion/%03d.png'),'-c:v','libx264','-crf','18','-pix_fmt','yuv420p',str(p/'short-camera-check.mp4')],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
print(json.dumps({'static_captures':3,'motion_frames':len(frames),'retouched':False}))
