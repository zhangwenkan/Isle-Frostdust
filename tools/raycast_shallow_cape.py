"""Identify a visible triangle in an exported GLB without modifying any geometry."""
import json,struct,hashlib
import numpy as np
from pathlib import Path
R=Path(__file__).resolve().parents[1]
src=(R/'tools/verify_original_coast_assets.py').read_text(encoding='utf8');exec(src[src.index('def read(path):'):src.index('old=read(')])
doc,nodes,meshes,arr=read(R/'assets/island_blender/nameless_island.glb')
eye=np.array([-26.,3.3,18.5]);target=np.array([-26.,.35,0]);f=(target-eye);f/=np.linalg.norm(f);right=np.cross(f,[0,1,0]);right/=np.linalg.norm(right);up=np.cross(right,f)
for pixel in [(859,371),(870,361),(862,382)]:
 dx=(pixel[0]/1280*2-1)*np.tan(np.deg2rad(20))*1280/720;dy=(1-pixel[1]/720*2)*np.tan(np.deg2rad(20));direction=f+right*dx+up*dy;direction/=np.linalg.norm(direction)
 hits=[]
 for name,n in nodes.items():
  if name in ['Open_Sea','HD2D_Lens_Surface']:continue
  if name.startswith(('PixelBamboo','Mist_','Bridge','Gull')):continue
  for p in doc['meshes'][n['mesh']]['primitives']:
   v=arr(p['attributes']['POSITION']).astype(float)
   if 'matrix' in n:
    m=np.array(n['matrix']).reshape(4,4).T;v=(np.column_stack((v,np.ones(len(v))))@m.T)[:,:3]
   else:
    v*=np.array(n.get('scale',[1,1,1]));v+=np.array(n.get('translation',[0,0,0]))
   idx=arr(p['indices']).reshape(-1,3);a=v[idx[:,0]];e1=v[idx[:,1]]-a;e2=v[idx[:,2]]-a;h=np.cross(direction,e2);det=(e1*h).sum(1);valid=abs(det)>1e-9;inv=np.divide(1,det,out=np.zeros_like(det),where=valid);ss=eye-a;u=inv*(ss*h).sum(1);q=np.cross(ss,e1);vv=inv*(q*direction).sum(1);t=inv*(e2*q).sum(1);ok=valid&(u>=0)&(vv>=0)&(u+vv<=1)&(t>0)
   if ok.any():
    ti=np.where(ok)[0][np.argmin(t[ok])];hits.append((float(t[ti]),name,list(eye+direction*t[ti]),v[idx[ti]].tolist()))
 print(pixel,sorted(hits)[:2])
