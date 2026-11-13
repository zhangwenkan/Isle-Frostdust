"""Paint soft mineral washes and broken, tapered structural ink (textures only)."""
from pathlib import Path
import math,json
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'assets/colored_ink_sample'
S=512;atlas=Image.new('RGB',(S*4,S*4))
old_palette=[(147,159,151),(124,140,134),(133,147,139),(142,154,146),
 (119,135,129),(137,151,144),(145,157,149),(128,144,137),
 (139,153,146),(148,161,154),(156,169,161),(144,156,148),
 (136,150,143),(148,160,152),(141,155,148),(143,157,150)]
palette=[]
def stroke(draw,points,width,color):
    left=[];right=[]
    for i,(x,y) in enumerate(points):
        a=points[max(0,i-1)];b=points[min(len(points)-1,i+1)]
        dx,dy=b[0]-a[0],b[1]-a[1];n=max(.01,math.hypot(dx,dy))
        t=i/(len(points)-1);w=width*(.10+.90*math.sin(math.pi*t)**.7)
        left.append((x-dy/n*w,y+dx/n*w));right.append((x+dy/n*w,y-dx/n*w))
    draw.polygon(left+right[::-1],fill=color)

for k,old in enumerate(old_palette):
    # Close the face-to-face palette gap; large planes remain distinguished by
    # actual lighting, with paint softness within each face instead of panels.
    base=np.array((140,153,145))*.78+np.array(old)*.22
    palette.append(base.tolist())
    y,x=np.mgrid[0:S,0:S].astype(float)/S
    # Deliberately broad, overlapping wet washes. No grain/noise field.
    wash=(5.0*np.exp(-((x-(.23+.08*(k%3)))**2/.09+(y-.30)**2/.14))
          -4.2*np.exp(-((x-.73)**2/.09+(y-(.58+.08*(k%2)))**2/.20))
          +2.4*np.exp(-((x-.45)**2/.25+(y-.70)**2/.06)))
    edge=np.clip(np.minimum.reduce([x-.05,.95-x,y-.05,.95-y])/.18,0,1)
    edge=edge*edge*(3-2*edge)
    shared=np.array((140,153,145))
    color=shared+(base-shared+wash[:,:,None])*edge[:,:,None]
    tile=Image.fromarray(np.uint8(np.clip(color,0,255))).convert('RGBA')
    wet=Image.new('RGBA',(S,S));d=ImageDraw.Draw(wet)
    # Transparent mineral-color strokes with restrained warm/cool variation.
    shift=(k%4)*19
    stroke(d,[(70+shift,100),(132+shift,146),(197+shift,209),(244+shift,256)],28,(174,168,137,23))
    stroke(d,[(400,257),(344,305),(312,369),(284,437)],37,(84,113,104,22))
    tile=Image.alpha_composite(tile,wet.filter(ImageFilter.GaussianBlur(13)))
    ink=Image.new('RGBA',(S,S));d=ImageDraw.Draw(ink)
    # Short separated segments, varying pressure, soft absorption and gaps.
    if k in [0,1,2,3,4,5,7,8]:
        stroke(d,[(31,28),(71,30),(124,27),(176,29)],2.7,(65,83,73,80))
        if k%2==0:stroke(d,[(284,29),(324,30),(367,28),(394,31)],2.3,(65,83,73,57))
    if k in [0,2,5,7]:
        stroke(d,[(28,38),(30,94),(27,146),(29,202)],2.4,(66,85,75,67))
        stroke(d,[(29,276),(31,311),(28,352)],1.5,(66,85,75,44))
    if k in [2,4,8]:
        stroke(d,[(360,168),(343,181),(329,193),(310,225)],1.6,(65,82,75,68))
    if k==3:
        stroke(d,[(366,33),(359,88),(352,151),(355,198)],2.0,(55,73,65,76))
        stroke(d,[(359,226),(361,251),(356,291),(349,333)],1.4,(55,73,65,48))
    tile=Image.alpha_composite(tile,ink.filter(ImageFilter.GaussianBlur(1.15)))
    # Coarse hand-drawn brush masks, enlarged without smoothing. Shapes and
    # missing bristles are placed explicitly; this is not a full-surface noise.
    dry=Image.new('RGBA',(128,128));b=ImageDraw.Draw(dry)
    patterns={
      1:([(24,24),(22,43),(26,61),(25,72)],[(34,58),(32,72),(34,85)]),
      2:([(27,29),(32,44),(30,59),(34,72)],[(51,58),(48,74),(52,91)]),
      3:([(47,31),(42,48),(47,67),(43,87)],[(69,64),(65,79),(67,101)]),
      4:([(72,27),(67,47),(71,62),(66,84)],[(44,68),(42,82),(46,101)]),
      5:([(26,35),(30,50),(27,72),(32,89)],[(60,59),(57,77),(61,95)]),
      7:([(30,29),(34,46),(31,64),(35,85)],[(66,66),(63,85),(67,100)]),
      8:([(75,32),(68,49),(72,68),(68,86)],[(42,56),(39,73),(41,92)]),
    }
    if k in patterns:
        main,small=patterns[k]
        # Thin mineral strokes and a pale dry-brush shoulder alongside them.
        stroke(b,[(x+5,y-1) for x,y in main],5.0,(180,181,152,58))
        stroke(b,main,2.0,(55,76,63,92))
        stroke(b,small,1.35,(62,84,68,75))
        # A few deliberate missing brush bristles give broken pixel edges.
        for x,y in [main[1],main[2],small[1]]:
            b.rectangle((x-1,y+2,x+1,y+5),fill=(0,0,0,0))
            b.line([(x+4,y-2),(x+6,y+5)],fill=(191,188,156,48),width=1)
        stroke(b,[(25,104),(40,99),(49,100)],1.0,(65,84,69,62))
    if k==10:
        # Two low-contrast mineral sweeps sit within the cap, not on its edge.
        stroke(b,[(29,48),(42,44),(58,47),(76,43)],4.0,(183,184,158,53))
        stroke(b,[(46,77),(58,74),(73,76),(87,72)],1.1,(74,97,81,64))
        b.rectangle((61,74,64,77),fill=(0,0,0,0))
    tile=Image.alpha_composite(tile,dry.resize((S,S),Image.Resampling.NEAREST))
    atlas.paste(tile.convert('RGB'),((k%4)*S,(k//4)*S))
# Both cap facets use the same planar coordinates. Giving them the same wash
# lets color cross their shared edge instead of drawing a colored triangle.
atlas.paste(atlas.crop((2*S,2*S,3*S,3*S)),(3*S,2*S))
atlas.save(OUT/'rock_watercolor_planes.png')
(OUT/'rock_watercolor_palette.json').write_text(json.dumps({'grid':[4,4],'tile_size':S,'brush_mask_size':128,'palette':palette,'source':'Original broad washes with explicitly drawn pixel dry-brush paths; no reference pixels/noise map'},indent=2),encoding='utf-8')
print(OUT/'rock_watercolor_planes.png')
