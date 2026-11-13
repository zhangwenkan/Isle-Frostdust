"""Prepare supplied image maps. Geometry and UVs are authored only in Blender MCP."""
from pathlib import Path
import json,shutil,hashlib
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
REF=Path('D:/steam/steamapps/common/I Just Wanted to Fish Demo/analysis/exported_all')
OUT=ROOT/'assets/island_blender/palm_study';OUT.mkdir(exist_ok=True)
records=[]
def record(src,dst,method):
    records.append({'source':str(src),'output':dst.name,'method':method,'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest()})
def normal(src):
    a=np.array(Image.open(src).convert('RGBA'),dtype=np.float32)/255
    # Unity DXT5nm / RG-or-AG: tangent X is stored in A*R, tangent Y in G.
    x=a[:,:,0]*a[:,:,3]*2-1;y=a[:,:,1]*2-1
    z=np.sqrt(np.maximum(0,1-x*x-y*y))
    return np.stack([x*.5+.5,y*.5+.5,z*.5+.5],axis=-1)
for src in [REF/'textures/T_Palm_Normal_501.png']+list((REF/'textures').glob('T_Rock_[ABCD]_Normal_*.png')):
    dst=OUT/(src.stem+'_OpenGL.png');a=normal(src)
    Image.fromarray(np.round(a*255).astype('uint8')).save(dst)
    record(src,dst,'Decode Unity AG-packed tangent normal to RGB OpenGL normal; no invented surface detail')
src=REF/'textures/T_Palm_Albedo_399.png';dst=OUT/src.name;shutil.copy2(src,dst);record(src,dst,'Unmodified reference UV atlas')
src=REF/'textures/T_Terrain_Albedo_Demo_542.png';original=Image.open(src).convert('RGB')
crop=(0,0,1400,760);size=(2048,768)
grass=np.array(original.crop(crop).resize(size,Image.Resampling.LANCZOS),dtype=np.float32)/255
luma=(grass*np.array([.2126,.7152,.0722])).sum(axis=2,keepdims=True)
grass=(luma+(grass-luma)*.80)*np.array([.88,.90,.98])
u=np.linspace(0,1,size[0]);v=np.linspace(0,1,size[1]);x=-20+u[None,:]*48;z=-7+v[:,None]*12
pz=np.where((x>=4.5)&(x<=14),.25,.4+np.sin(x*.25)*.44)
variation=np.clip((luma[:,:,0]-.42)*.7,-.12,.12)
distance=np.abs(z-pz)
t=np.clip((distance-(.40+variation))/(.30+variation*.3),0,1)
path=(1-t*t*(3-2*t))[:,:,None]
sand=np.array(original.crop((500,2800,1700,3400)).resize(size,Image.Resampling.LANCZOS),dtype=np.float32)/255
sand_luma=(sand*np.array([.2126,.7152,.0722])).sum(axis=2,keepdims=True)
sand=np.array([.65,.59,.44])[None,None,:]*(.92+.16*sand_luma)
paint=np.clip(grass*(1-path)+sand*path,0,1)
dst=OUT/'Island_Ground_Study.png';Image.fromarray(np.round(paint*255).astype('uint8')).save(dst)
record(src,dst,'Reuse grass crop (0,0,1400,760) once across island bounds; match existing path with softened irregular edges; restrained saturation')
srcn=REF/'textures/T_Terrain_Normal_Demo_436.png'
n=normal(srcn);n=Image.fromarray(np.round(n*255).astype('uint8')).crop(crop).resize(size,Image.Resampling.LANCZOS)
n=np.array(n,dtype=np.float32)/255;n=n*(1-path*.9)+np.array([.5,.5,1])[None,None,:]*(path*.9)
dst=OUT/'Island_Ground_Normal.png';Image.fromarray(np.round(np.clip(n,0,1)*255).astype('uint8')).save(dst)
record(srcn,dst,'Decode matching Unity normal crop; flatten on path; same mapping as ground color')
(OUT/'source_manifest.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
print('Prepared',len(records),'reference-derived maps, including decoded Unity normals.')
