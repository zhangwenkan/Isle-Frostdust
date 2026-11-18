"""Edit our existing transparent bamboo artwork into sprays and distant paintings.

Raster work only. Three-dimensional carriers are authored separately in Blender MCP.
"""
import hashlib,json,math
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFilter

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'assets/bamboo_fine'
OUT=ROOT/'assets/layered_island/forest_layers'
OUT.mkdir(parents=True,exist_ok=True)
sources={key:Image.open(SOURCE/(key+'_color.png')).convert('RGBA') for key in ['slender_a','slender_b','slender_c']}
# Separate directional sprays, including their fine connecting twig, not whole trees.
sprays=[('slender_b',(0,365,315,640)),('slender_b',(500,590,832,785)),('slender_c',(455,325,768,490))]
for i,(key,box) in enumerate(sprays):
    im=sources[key].crop(box)
    # Twig attachments may terminate at the crop. Transparent padding keeps mip edges clean.
    padded=Image.new('RGBA',(im.width+32,im.height+32));padded.alpha_composite(im,(16,16))
    padded.save(OUT/f'leaf_spray_{i}.png')

W,H=4096,1536
def retint(im,color,strength):
    p=np.asarray(im).copy().astype(float)
    value=p[:,:,:3].mean(axis=2)/255.0
    p[:,:,:3]=np.array(color)[None,None,:]*(1-strength+strength*value[:,:,None])
    return Image.fromarray(np.uint8(np.clip(p,0,255)),'RGBA')

def tree(canvas,key,x,root,height,color,contrast,lean=0):
    # Draw the distant shaft as a silhouette. Reusing the entire old tree would
    # repeat low crowns through the viewing gap and fill it with clutter again.
    top=root-height;drift=lean*8
    draw=ImageDraw.Draw(canvas)
    shaft=max(5,round(height*.009))
    tone=tuple(round(v*.73) for v in color)+(210,)
    draw.polygon([(x-shaft/2,root),(x+shaft/2,root),(x+drift+shaft*.25,top),(x+drift-shaft*.25,top)],fill=tone)
    for k in range(3):
        q=.10+k*.12;cy=top+height*q;direction=-1 if (round(x)+k)%2 else 1
        end=x+drift*(1-q)+direction*height*(.10+.025*(k%2))
        draw.line([(x+drift*(1-q),cy+height*.025),(end,cy)],fill=tone,width=max(2,shaft//3))
        src=Image.open(OUT/f'leaf_spray_{(round(x)+k)%3}.png').convert('RGBA')
        src=retint(src,color,contrast)
        width=round(height*(.39 if k<2 else .31));h=round(src.height/src.width*width)
        src=src.resize((width,h),Image.Resampling.LANCZOS)
        if direction<0:src=src.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        canvas.alpha_composite(src,(round(end-width*.5),round(cy-h*.42)))

# An opaque forest depth painting: olive floor, mist-lit interior, shaded canopy.
# It has no sky, horizon line, ocean, architecture or borrowed game textures.
yy=np.linspace(0,1,H)[:,None,None]
xx=np.linspace(0,1,W)[None,:,None]
top=np.array([48,64,40]);bottom=np.array([82,95,66])
rgb=np.broadcast_to(top*(1-yy)+bottom*yy,(H,W,3)).copy()
openings=np.exp(-((xx-.24)/.11)**2)+.85*np.exp(-((xx-.58)/.13)**2)+.7*np.exp(-((xx-.84)/.09)**2)
lit=np.exp(-((yy-.60)/.27)**2)*openings
rgb+=lit*np.array([42,45,34])
base=Image.fromarray(np.uint8(np.clip(rgb,0,255)),'RGB').convert('RGBA')
for j in range(72):
    x=-70+j*60+[0,17,-11,9,-7][j%5]
    root=H*(.80+.035*math.sin(j*.71));height=H*(.86+.12*math.sin(j*.83+1.2))
    tone=[(76,92,59),(85,101,68),(69,86,54)][j%3]
    tree(base,['slender_a','slender_b','slender_c'][j%3],x,root,height,tone,.20,[-1,2,0,-2][j%4])
base=base.filter(ImageFilter.GaussianBlur(4.5))
base.save(OUT/'forest_depth.png')

for layer in [0,1]:
    canvas=Image.new('RGBA',(W,H))
    count=35 if layer==0 else 47
    for j in range(count):
        x=-80+j*(W+160)/(count-1)+[0,27,-18,12,-8][j%5]
        root=H*(.90+.033*math.sin(j*.78+layer))
        height=H*((.93 if layer==0 else .82)+.10*math.sin(j*.69+layer))
        color=[(57,78,38),(66,86,48),(54,75,39)][j%3] if layer==0 else [(88,104,71),(97,111,80),(82,99,66)][j%3]
        tree(canvas,['slender_b','slender_c','slender_a'][(j+layer)%3],x,root,height,color,.32 if layer==0 else .20,[0,-2,1,2,-1][j%5])
    pixels=np.asarray(canvas).copy()
    fade=np.clip((1-np.linspace(0,1,H))/.18,0,1)
    fade=fade*fade*(3-2*fade)
    pixels[:,:,3]=np.uint8(pixels[:,:,3]*fade[:,None])
    canvas=Image.fromarray(pixels,'RGBA').filter(ImageFilter.GaussianBlur(1.1 if layer==0 else 3.0))
    canvas.save(OUT/('forest_shapes_near.png' if layer==0 else 'forest_shapes_middle.png'))

manifest={'source':'Project-owned bamboo_fine color sprites, originally baked in Blender MCP from eastern bamboo',
          'source_hashes':{key:hashlib.sha256((SOURCE/(key+'_color.png')).read_bytes()).hexdigest() for key in sources},
          'leaf_spray_crops':sprays,'backgrounds':{'forest_depth.png':'opaque low-contrast forest painting','forest_shapes_middle.png':'transparent distant silhouettes','forest_shapes_near.png':'transparent nearer forest silhouettes'},
          'new_ai_generation':False,'geometry_generated':False,'dimensions':[W,H]}
(OUT/'SOURCE.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
preview=Image.new('RGB',(960,550),'#aaa98b')
for i in range(3):
    im=Image.open(OUT/f'leaf_spray_{i}.png');im.thumbnail((300,220));preview.paste(im,(i*320,0),im)
for i,name in enumerate(['forest_depth.png','forest_shapes_middle.png','forest_shapes_near.png']):
    im=Image.open(OUT/name);im.thumbnail((960,100));preview.paste(im,(0,240+i*100),im)
preview.save(OUT/'source-preview.jpg',quality=91)
print(json.dumps({'leaf_sprays':3,'forest_paintings':3,'output':str(OUT)}))
