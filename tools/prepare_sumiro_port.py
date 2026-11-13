"""Extract inspected Sumiro material GLSL; adapt syntax, not the visual recipe."""
from pathlib import Path
import re,json,shutil,hashlib
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'artifacts/sumiro-style-review/source'
OUT=ROOT/'assets/sumiro'
OUT.mkdir(exist_ok=True)
for folder in ['env_cliff','env_pines','backdrop']:
    for f in (SRC/'assets'/folder).rglob('*'):
        if f.suffix not in ['.png','.jpg','.webp']:continue
        dest=OUT/f.relative_to(SRC/'assets');dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(f,dest)

# Source noise lattice is exactly xorshift32 seeded with 49734321.
t=49734321;data=bytearray()
for i in range(64**3):
    t^=(t<<13)&0xffffffff;t&=0xffffffff;t^=t>>17;t^=(t<<5)&0xffffffff;t&=0xffffffff;data.append(t&255)
Image.frombytes('L',(64,4096),bytes(data)).save(OUT/'ink_noise_slices.png')

s=(SRC/'ink_material-UyOP6egx.js').read_text()
templates=re.findall(r'`([\s\S]*?)`',s)
noise=next(t for t in templates if 'float vnoise(vec3 p)' in t)
surface=next(t for t in templates if 'vec3 inkSurface(' in t)
# Remove the unused snow chapter; preserve chapter-one stone/wood/pine algorithms.
lines=surface.splitlines();out=[];levels=[];active=True
for line in lines:
    if '#ifdef INK_SNOW' in line:levels.append(active);active=False;continue
    if line.strip()=='#else' and levels:active=levels[-1] and not active;continue
    if line.strip()=='#endif' and levels:active=levels.pop();continue
    if active:out.append(line)
surface='\n'.join(out)
defaults={'uSunDir':'vec3(0.3,0.8,0.5)','uShadowMul':'vec3(0.42,0.47,0.55)','uWrap':'.5','uSkyFill':'.8','uWashFreq':'.7','uWashWarp':'.03','uCavityK':'.3','uDryAmt':'.85','uDryFreq':'1.6','uGrainAmp':'.07','uGrainFreq':'7.0','uBlotchAmp':'.02','uBlotchFreq':'9.0','uStreakAmp':'.01','uUseRamp':'1.0','uLookMap':'1.0','uFlat':'0.0','uRampBias':'0.0','uRampScale':'1.0','uPoolAmt':'1.0','uStep':'0.0','uBrushEdge':'.05','uHueAmt':'.15','uFacetAmt':'0.0','uFacetFreq':'1.1','uFacetStretch':'.42','uCrackAmt':'0.0','uCrackW':'1.6','uCrackGate':'.62','uFacetBevel':'.2','uBrushAmt':'.02','uBrushLean':'.24','uPitAmt':'0.0','uScumble':'0.0','uStainAmt':'0.0','uStainFreq':'.5','uSpeckAmt':'0.0','uPxScale':'1.0','uPxToRad':str(__import__('math').tan(__import__('math').radians(20))/352),'uGouge':'0.0','uNoiseFrame':'mat3(1.0)','uTint':'vec3(1.012,1.0,.975)','uShadeTint':'vec3(.56,.56,.58)','uDryCol':'vec3(.552,.546,.486)','uPoolCol':'vec3(.024,.031,.034)','uPoolDeep':'vec3(.0075,.0103,.0116)','uInkLine':'vec3(.0044,.004,.003)','uLineWeight':'1.0','uLitClean':'.6','uZones':'0.0','uZoneA':'.38','uZoneB':'.68','uZoneWander':'1.0','uZoneSoft':'.15','uZoneVals':'vec3(.2,.52,.92)','uDryDirect':'1.0','uPoolTear':'.35','uCoolDark':'.12','uInkBold':'1.0','uBoldMat':'1.0','uInkShape':'1.0'}
surface=re.sub(r'uniform (float|vec3|mat3)\s+(\w+);',lambda m:f'uniform {m[1]} {m[2]} = {defaults.get(m[2],"0.0")};',surface)
surface=surface.replace('cameraPosition','ink_camera').replace('float flat_', 'float flat_')
surface=surface.replace('const vec3 RAMP[RAMP_N] = vec3[RAMP_N](', 'const vec3 RAMP[RAMP_N] = {').replace('vec3(203.0, 202.0, 193.0) / 255.0\n);','vec3(203.0, 202.0, 193.0) / 255.0\n};')
noise=noise.replace('uniform highp sampler3D tInkNoise;','uniform sampler3D tInkNoise : filter_linear, repeat_enable;')
header='''// Adapted from Sumiro's publicly served ink_material-UyOP6egx.js (2026-11-07).
// Upstream provenance and licence status: assets/sumiro/PROVENANCE.md.
shader_type spatial;
render_mode unshaded, cull_disabled, fog_disabled;
uniform sampler2D look_map : filter_linear_mipmap_anisotropic, repeat_enable;
uniform bool has_map = true;
uniform bool use_paint = true;
uniform bool foliage = false;
uniform bool grass = false;
uniform bool ground_project = false;
uniform bool base_ground = false;
uniform vec3 base_color = vec3(1.0);
uniform float material_scale = 1.0;
uniform float alpha_cut = 0.0;
uniform float wash_amount = 0.0;
uniform vec3 wash_color = vec3(.6,.56,.47);
varying vec3 ink_world;
varying vec3 ink_normal;
varying vec3 ink_camera;
varying float leaf_weight;
void vertex(){
    ink_camera = CAMERA_POSITION_WORLD;
    vec3 p = (MODEL_MATRIX * vec4(VERTEX,1.0)).xyz;
    if(foliage){
        float ph = p.x*1.3+p.z*.9+p.y*.7;
        float w = sin(TIME*.9+ph)+.5*sin(TIME*1.7+ph*2.1);
        VERTEX.xz += vec2(.018,.012)*w*UV2.x;
    }
    if(grass){
        float ph=p.x*1.1+p.z*.8;
        VERTEX.xz+=vec2(.035,.018)*(sin(TIME*1.1+ph)*.6+sin(TIME*2.3+ph*1.7)*.25)*UV2.x;
    }
    ink_world = (MODEL_MATRIX * vec4(VERTEX,1.0)).xyz;
    ink_normal = normalize(MODEL_NORMAL_MATRIX * NORMAL);
}
'''
# A display-referred NPR palette must be brought back through Godot's ACES output.
# This leaves the water's original physical shading and its tone mapper untouched.
tail='''
vec3 display_to_scene(vec3 c){
    vec3 y = mix(c/12.92,pow((c+.055)/1.055,vec3(2.4)),step(vec3(.04045),c));
    vec3 a = 2.51-2.43*y;
    vec3 b = .03-.59*y;
    return max((-b+sqrt(b*b+4.0*a*.14*y))/(2.0*a),vec3(0.0));
}
void fragment(){
    vec2 uv = UV;
    if(ground_project){
        float path_z=.4+sin(ink_world.x*.25)*.44;
        uv=vec2(clamp((ink_world.z-path_z+5.0)/10.0,.025,.975),(ink_world.x+21.0)/48.0);
    }
    vec4 tex = has_map ? texture(look_map,uv) : vec4(base_color,1.0);
    if(foliage){
        vec2 dx=dFdx(uv)*2048.0,dy=dFdy(uv)*2048.0;
        float lod=.5*log2(max(max(dot(dx,dx),dot(dy,dy)),.000001));
        if(tex.a<mix(.42,.1,smoothstep(2.0,5.5,lod))){
            if(texture(look_map,uv,2.4).a<.42)discard;
            tex.rgb=vec3(.075,.085,.078);
        }
    }else if(tex.a<alpha_cut){discard;}
    vec4 paint = use_paint ? COLOR : vec4(1.0,0.0,0.0,1.0);
    if(!use_paint&&!base_ground)tex.rgb*=COLOR.rgb;
    if(base_ground)paint=vec4(1.0,0.0,0.0,1.0);
    vec3 col=inkSurface(ink_world*material_scale,normalize(ink_normal),tex.rgb,paint,1.0);
    col=mix(col,wash_color,wash_amount);
    ALBEDO=display_to_scene(clamp(col,vec3(0.0),vec3(.96)));
}
'''
(ROOT/'shaders/sumiro_ink.gdshader').write_text(header+noise+surface+tail,encoding='utf8')
print('Ported chapter-one ink surface:',len(surface),'characters')

files=[]
for f in SRC.rglob('*'):
    if f.is_file() and f.suffix in ['.js','.glb','.png','.jpg','.webp','.json']:
        files.append({'file':str(f.relative_to(SRC)).replace('\\','/'),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'bytes':f.stat().st_size})
(OUT/'source_manifest.json').write_text(json.dumps(files,indent=2),encoding='utf8')
(OUT/'PROVENANCE.md').write_text('''# Sumiro local style study

Source: https://xikhar.github.io/sumiro/ by xikhar. Retrieved 2026-11-07.
The website's actually served bundled JavaScript and GLB/image assets were inspected and saved in `artifacts/sumiro-style-review/source/`.

Models, look maps, pine atlas, hill paintings and sky masks originate in Sumiro. The chapter-one surface algorithm is adapted to Godot from `ink_material-UyOP6egx.js`; presets come from `materials-CGuChJ0C.js` and `constants-BjlLV5tN.js`. Pine construction and wind come from `env_pines-CRDalYfK.js` and `cards-D1AvNuWX.js`; sky and hills from `backdrop-eS84m0Yx.js`.

No public source-repository licence has been verified: the repository API returned 404 and the served bundles contain no project licence grant. These local evaluation copies are not represented as original work or as cleared for redistribution. Confirm permission/licence before distributing the adapted assets/code. No publication or external distribution is part of this pass.

Godot integration and coastline fitting are local adaptations. All model importing, adaptation and assembly occur inside Blender through Blender MCP. SHA-256 hashes are recorded in source_manifest.json.
''',encoding='utf8')
