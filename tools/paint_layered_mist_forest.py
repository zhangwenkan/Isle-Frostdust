"""Recompose project-owned leaf artwork into distinct forest silhouettes. Raster only."""
import json,math,random,hashlib
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'assets/layered_island/forest_layers'
W,H=4096,1536
sprays=[Image.open(OUT/f'leaf_spray_{i}.png').convert('RGBA') for i in range(3)]
def retint(src,color):
    a=np.array(src).copy();value=a[:,:,:3].mean(axis=2)/255
    a[:,:,:3]=np.uint8(np.array(color)[None,None,:]*(.82+.18*value[:,:,None]))
    return Image.fromarray(a)
def forest(layer):
    rng=random.Random(7011+layer*197)
    canvas=Image.new('RGBA',(W,H))
    records=[]
    groups=[(.02,5),(.14,4),(.25,7),(.38,3),(.49,5),(.62,6),(.75,4),(.86,6),(.98,4)]
    for group,(cx,count) in enumerate(groups):
        if layer==1:count+=2
        if layer==2:count+=4
        for j in range(count):
            x=(cx+(layer-1)*.021+rng.uniform(-.025,.025))*W
            root=H*rng.uniform(.83,1.02) if layer==0 else (H*rng.uniform(.73,.91) if layer==1 else H*rng.uniform(.51,.62))
            top=H*rng.uniform(-.10,.12) if layer<2 else H*rng.uniform(-.10,.045)
            shaft=rng.uniform(5,9) if layer==0 else (rng.uniform(3.5,6) if layer==1 else rng.uniform(3,5))
            lean=rng.uniform(-35,35);height=root-top
            # Dark forest remains behind locally bright mist. Distant shafts
            # stay thinner than the foreground culms instead of reading as posts.
            color=[(38,63,45),(55,79,58),(66,88,69)][layer]
            color=tuple(int(c+rng.uniform(-6,6)) for c in color)
            tree=Image.new('RGBA',(W,H));draw=ImageDraw.Draw(tree)
            stem_tone=tuple(int(c*.84) for c in color)+(255,)
            draw.polygon([(x-shaft*.5,root),(x+shaft*.5,root),(x+lean+shaft*.22,top),(x+lean-shaft*.22,top)],fill=stem_tone)
            for k in range(3):
                crown_start=.24 if layer<2 else .22
                cy=top+height*(crown_start+k*.105);d=-1 if (j+k+group)%2 else 1
                end=x+lean+d*height*rng.uniform(.075,.12)
                draw.line([(x+lean,cy+height*.016),(end,cy)],fill=stem_tone,width=max(2,int(shaft*.25)))
                src=retint(sprays[(j+k+group)%3],color)
                width=int(height*rng.uniform(.26,.37));sh=int(src.height/src.width*width)
                src=src.resize((width,sh),Image.Resampling.LANCZOS)
                if d<0:src=src.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
                tree.alpha_composite(src,(int(end-width*.5),int(cy-sh*.45)))
            # Vary the lower disappearance height per grove, not a full-width cutoff.
            a=np.asarray(tree).copy();yy=np.arange(H)[:,None]
            cutoff=root-height*rng.uniform(.06,.13)
            fade=np.clip((root-yy)/max(height*.19,1),0,1)
            a[:,:,3]=np.uint8(a[:,:,3]*fade)
            tree=Image.fromarray(a);canvas.alpha_composite(tree)
            records.append({'x':round(x,2),'top':round(top,2),'root':round(root,2),'width':round(shaft,2),'group':group})
    return canvas,records
near,near_rows=forest(0);middle,middle_rows=forest(1);deep,deep_rows=forest(2)
near=near.filter(ImageFilter.GaussianBlur(.65));middle=middle.filter(ImageFilter.GaussianBlur(1.2))
near.save(OUT/'forest_shapes_near.png');middle.save(OUT/'forest_shapes_middle.png')
yy=np.linspace(0,1,H)[:,None,None];xx=np.linspace(0,1,W)[None,:,None]
top=np.array([70,89,62]);bottom=np.array([100,119,88])
rgb=np.broadcast_to(top*(1-yy)+bottom*yy,(H,W,3)).copy()
openings=np.exp(-((xx-.19)/.10)**2)+.8*np.exp(-((xx-.51)/.12)**2)+.9*np.exp(-((xx-.80)/.09)**2)
rgb+=np.exp(-((yy-.34)/.20)**2)*openings*np.array([34,34,30])
dark_groves=np.exp(-((xx-.34)/.072)**2)+.85*np.exp(-((xx-.67)/.090)**2)+.70*np.exp(-((xx-.93)/.065)**2)
rgb-=np.exp(-((yy-.24)/.24)**2)*dark_groves*np.array([20,21,16])
base=Image.fromarray(np.uint8(np.clip(rgb,0,255))).convert('RGBA');base.alpha_composite(deep)
base=base.filter(ImageFilter.GaussianBlur(2.5));base.save(OUT/'forest_depth.png')
source=json.loads((OUT/'SOURCE.json').read_text(encoding='utf-8'))
source['latest_raster_author']='tools/paint_layered_mist_forest.py'
source['layer_silhouettes']={'near':near_rows,'middle':middle_rows,'depth':deep_rows}
source['leaf_spray_hashes']={str(i):hashlib.sha256((OUT/f'leaf_spray_{i}.png').read_bytes()).hexdigest() for i in range(3)}
source['projection_note']='Layer centers corrected through MCP using actual game projection. Crown fragments and thin shafts occupy visible UV bands, with dark groves behind local mist.'
source['spatial_design_source']='artifacts/bamboo-atmosphere-source-study/README.md'
(OUT/'SOURCE.json').write_text(json.dumps(source,indent=2),encoding='utf-8')
preview=Image.new('RGB',(1024,600),'#798269')
for i,im in enumerate([base,middle,near]):
    im=im.copy();im.thumbnail((1024,190));preview.paste(im,(0,i*200),im)
preview.save(ROOT/'artifacts/forest-wind-mist-review/paint-preview.jpg',quality=93)
print(json.dumps({'rows':[len(near_rows),len(middle_rows),len(deep_rows)],'leaf_sprays_unchanged':True}))
