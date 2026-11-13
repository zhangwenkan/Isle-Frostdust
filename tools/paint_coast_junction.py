"""Paint a dedicated unfolded surface for the Blender-authored coast sample.
This draws bitmap pigments only. All geometry/UV is authored in Blender MCP.
"""
from pathlib import Path
import json,math
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
R=Path(__file__).resolve().parents[1];A=R/'assets/coast_junction';O=R/'artifacts/coast-junction-refine-review'
d=json.loads((O/'authoring.json').read_text(encoding='utf8'));W,H=2048,640
xx,yy=np.meshgrid(np.linspace(0,1,W),np.linspace(0,1,H))
# Broad watercolor value changes, not a repeated photographic or noise tile.
pigment=np.zeros((H,W,3),dtype=float)+[171,145,123]
wash=2.2*np.sin(xx*10+yy*4)+1.3*np.sin(xx*27-yy*3)+.8*np.cos(yy*19+xx*7)
pigment+=wash[:,:,None]*[1,.88,.65]
topwash=1-np.clip((yy-.13)/.065,0,1)
pigment-=topwash[:,:,None]*[29,17,14]
im=Image.fromarray(np.clip(pigment,0,255).astype('uint8'),'RGB').convert('RGBA')
def u(x):return (x+23)/18
def pt(x,y):return (int(u(x)*(W-1)),int(y*(H-1)))
def poly(points,color):
 layer=Image.new('RGBA',im.size);ImageDraw.Draw(layer).polygon([pt(*p) for p in points],fill=color);im.alpha_composite(layer)
# Pigment mass follows the actual three main mineral faces and the low shoulder.
poly([(-23,.20),(-21,.22),(-19.2,.29),(-18.1,.45),(-18.3,.79),(-21.4,.9),(-23,.86)],(146,126,112,75))
poly([(-21.6,.25),(-19.25,.24),(-18.6,.42),(-19,.48),(-20.4,.42),(-21.4,.48)],(202,174,143,43))
poly([(-17.6,.23),(-16.7,.22),(-15,.3),(-13.5,.35),(-13,.50),(-14.4,.55),(-16.5,.48)],(199,174,145,48))
poly([(-17.4,.64),(-16.2,.60),(-14.7,.64),(-13.4,.74),(-13.0,.96),(-17.5,.94)],(128,116,106,64))
poly([(-11.7,.24),(-9.6,.21),(-7.5,.34),(-7.1,.49),(-9.5,.45),(-10.8,.5)],(196,167,139,46))
poly([(-11.8,.46),(-10.5,.51),(-9.1,.47),(-7.1,.61),(-6.8,.82),(-9,.9),(-11.3,.8)],(142,126,113,61))
# Top pigments are softly interrupted; color does not draw a uniform bright rim.
poly([(-22.2,.02),(-20.8,.0),(-19.4,.07),(-18.2,.14),(-19.4,.17),(-21.3,.12)],(180,161,129,90))
poly([(-17.3,0),(-16.2,.025),(-14.7,0),(-13.1,.12),(-13.9,.17),(-16,.13)],(187,167,135,100))
poly([(-11.3,.015),(-9.7,0),(-7.4,.03),(-6.6,.12),(-8.6,.17),(-10.7,.13)],(185,168,140,90))
poly([(-22.5,0),(-19,0),(-18.3,.045),(-19.6,.055),(-21.4,.032)],(124,123,91,130))
poly([(-17.5,0),(-14.5,0),(-13.0,.03),(-15,.07),(-16.3,.035)],(128,129,95,120))
poly([(-12,0),(-8.8,0),(-7.7,.03),(-9.6,.058),(-11.3,.04)],(123,123,92,135))
# Restrained planar brushwork: deliberate slanted patches, large quiet areas remain.
for x,y,w,h in [(-21,.36,.5,.06),(-20.4,.64,.7,.065),(-19.7,.75,.33,.11),
 (-16.5,.31,.65,.05),(-15.7,.39,.8,.04),(-14.4,.69,.48,.09),(-16.2,.80,.7,.05),
 (-10.6,.30,.9,.035),(-9.9,.68,.55,.08),(-8.1,.45,.5,.055),(-7.2,.78,.35,.1)]:
 poly([(x,y),(x+w*.8,y-.009),(x+w,y+h*.3),(x+w*.55,y+h),(x-.06,y+h*.75)],(210,182,151,24))
def stroke(points,width=2,alpha=155):
 layer=Image.new('RGBA',im.size);draw=ImageDraw.Draw(layer)
 pts=[pt(*p) for p in points]
 # A warm broken inner edge plus a short, offset pale shoulder gives ink depth.
 draw.line([(x,y+2) for x,y in pts],fill=(207,183,148,int(alpha*.46)),width=max(1,width))
 draw.line(pts,fill=(79,77,67,alpha),width=width,joint='curve')
 for end in [pts[0],pts[-1]]:draw.ellipse((end[0]-1,end[1]-1,end[0]+1,end[1]+1),fill=(99,92,77,int(alpha*.6)))
 im.alpha_composite(layer)
# Cleft strokes follow the two inset stations, with interruptions along their lengths.
stroke([(-18.28,.23),(-18.13,.30),(-18.20,.39)],3,157)
stroke([(-18.05,.43),(-17.88,.49),(-17.86,.67)],2,163)
stroke([(-12.80,.24),(-12.57,.36),(-12.60,.44)],3,143)
stroke([(-12.46,.49),(-12.40,.60),(-12.61,.73)],2,143)
# Only the exposed shoulder lips receive horizontal strokes; none span the entire coast.
stroke([(-16.75,.578),(-16.1,.583),(-15.6,.578)],3,146)
stroke([(-15.0,.579),(-14.25,.581),(-13.75,.572)],2,123)
# Local joint tips stay on a face; they do not cross the UV transition onto rock tops.
stroke([(-20.75,.45),(-20.39,.475),(-19.75,.47)],2,118)
stroke([(-16.1,.30),(-15.88,.36),(-15.93,.425)],2,106)
stroke([(-14.8,.75),(-14.64,.79),(-14.22,.8)],2,111)
stroke([(-9.23,.32),(-9.0,.39),(-9.04,.465)],2,113)
stroke([(-10.67,.73),(-10.29,.762),(-9.81,.75)],2,114)
# Sparse short dry-brush groups on the broad mineral faces, aligned with the
# neighboring joint direction. Deliberate clusters, no full-surface speckle map.
for cx,cy,sgn in [(-20.2,.35,1),(-19.8,.67,1),(-16.05,.34,-1),(-15.1,.72,-1),(-10.2,.36,1),(-8.65,.68,1)]:
 for i in range(6):
  x=cx+(i%3)*.14;y=cy+(i//3)*.044;length=.13+.045*(i%3)
  poly([(x,y),(x+length,y+.004*sgn),(x+length*.9,y+.010),(x-.014,y+.013)],(220,195,158,35 if i%2 else 48))
rgba=np.asarray(im).copy()
# Alpha stores an opaque material blend, not transparency. Turf follows the
# original world's grass painting along an uneven crown edge.
reach=.006+.008*np.exp(-((xx-u(-18.1))/.040)**2)+.009*np.exp(-((xx-u(-12.4))/.046)**2)
reach+=.006*(.5+.5*np.sin(xx*68+yy*37))
grass=1-np.clip((yy-reach)/.018,0,1)
rgba[:,:,3]=(grass*255).astype('uint8')
Image.fromarray(rgba,'RGBA').save(A/'junction_paint.png')
(A/'SOURCE.md').write_text('# Coast junction sample\n\nGeometry and UV editing: Blender MCP, `tools/blender/refine_coast_junction.py`. Five locally authored original coastal modules are clipped into the sample while preserving UV0; a new recessed core and crown connect them to the turf. No Wandering Sword geometry, UV, or texture is used.\n\nThe five relief meshes retain the self-painted plus Poly Haven CC0-derived pigments documented in `../original_coastal_rock/SOURCE.md`; this sample is not claimed to have all textures painted from scratch. Their contact UVs and AO are newly baked in the current assembly.\n\nThe new crown/core pigment texture alone is drawn by `tools/paint_coast_junction.py`. Its alpha stores the grass/material blend, not transparency. The original painted grass is shared at the thin upper seam. The main island blend contains the corresponding edited land and archived baseline.\n',encoding='utf8')
print('JUNCTION_PAINT',im.size)
