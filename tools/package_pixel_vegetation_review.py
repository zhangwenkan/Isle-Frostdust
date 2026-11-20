"""Package actual Godot captures; no model generation."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,subprocess,imageio_ffmpeg
root=Path(__file__).resolve().parents[1]/'artifacts/pixel-vegetation-review'
files=sorted((root/'motion').glob('*.png'))
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',18)
ids=[round(i*(len(files)-1)/7) for i in range(8)]
sheet=Image.new('RGB',(1280,4*385),'#202923')
for j,i in enumerate(ids):
    if i>=len(files):continue
    img=Image.open(files[i]).convert('RGB').resize((640,360))
    x=j%2*640;y=j//2*385;sheet.paste(img,(x,y))
    ImageDraw.Draw(sheet).text((x+12,y+361),f'实机序列 {i:03d}',font=font,fill='#eee9d8')
sheet.save(root/'motion-contact-sheet.jpg',quality=92)
frames=[Image.open(f).convert('RGB').resize((960,540)) for f in files]
times=json.loads((root/'motion-times.json').read_text())
dt=(times[-1]-times[0])/max(1,len(times)-1)
if frames:frames[0].save(root/'living-vegetation.gif',save_all=True,append_images=frames[1:],duration=round(dt*1000),loop=0,optimize=False)
subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-y','-framerate',str(1/dt),'-i',str(root/'motion/%03d.png'),'-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(root/'living-vegetation.mp4')],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
print({'frames':len(files),'gif':str(root/'living-vegetation.gif')})
