"""Read cooked UE scene/Blueprint evidence. No scene/model edits or engine launch."""
from pathlib import Path
import hashlib, json, math, sys, collections

PROJECT=Path(__file__).resolve().parents[1]
LIB=Path('D:/Y 逸jian风yun决 v1.23.26 全DLC xg器/WanderingSword/analysis')
STUDY=LIB/'12_followup/20261109-bamboo-scene'
OUT=PROJECT/'artifacts/bamboo-atmosphere-source-study'
OUT.mkdir(exist_ok=True)
sys.path.insert(0,str(STUDY))
from inspect_bamboo import load, MAP, package

def write(name,data):
    (OUT/name).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')

scene=load(MAP)
def record(i):
    e=scene.exports[i-1]
    return dict(index=i,name=scene.resolve(i),class_name=scene.resolve(e['ClassIndex']),
                template=scene.resolve(e.get('TemplateIndex',0)),
                local_properties=scene.props(e.get('Data')),resolved_properties=scene.inherited(i))
records=[]
for i,e in enumerate(scene.exports,1):
    c=scene.resolve(e['ClassIndex'])
    if any(k in c for k in ['BP_LightBeam_C','BP_FogSheet_C','BP_JHEnvironment_JN_C',
                            'DirectionalLightComponent','SkyLightComponent','ExponentialHeightFogComponent',
                            'SpotLightComponent','JHPostProcessVolume','JHCameraBlockingVolume']):records.append(record(i))
write('scene-resolved.json',dict(source=str(LIB/'03_decoded'/(MAP+'.json.gz')),objects=records))

refs=[
 'Wandering_Sword/Content/JH/Maps/Common/LevelBass_JangNan/Map_xx_Inst.uasset',
 'Wandering_Sword/Content/JH/Core/Levels/Environment/M_YunYing.uasset',
 'Wandering_Sword/Content/JH/MapEditor/Environment/GodRay/M_GodRay_MASTER.uasset',
 'Wandering_Sword/Content/JH/MapEditor/Environment/GodRay/M_GodRay_Animated.uasset',
 'Wandering_Sword/Content/JH/MapEditor/Environment/FogSheet/Materials/M_FogSheet_Master_INST.uasset',
 'Wandering_Sword/Content/JH/MapEditor/Environment/FogSheet/Materials/M_FogSheet_Master.uasset',
]
materials=[]
for p in refs:
    a=load(p)
    materials.append(dict(package=p,source=str(LIB/'03_decoded'/(p+'.json.gz')),
       objects=[dict(name=e['ObjectName'],class_name=a.resolve(e['ClassIndex']),properties=a.props(e.get('Data')),
                     opaque_extra_base64_chars=len(e.get('Extras') or '')) for e in a.exports],
       has_editor_expression_exports=any('MaterialExpression' in a.resolve(e['ClassIndex']) for e in a.exports)))
write('material-evidence.json',materials)

blueprints=[]
def walk(v):
    if isinstance(v,dict):
        yield v
        for x in v.values():yield from walk(x)
    elif isinstance(v,list):
        for x in v:yield from walk(x)
for rel in ['GodRay/BP_LightBeam','FogSheet/BP_FogSheet']:
    pkg='Wandering_Sword/Content/JH/MapEditor/Environment/'+rel+'.uasset'
    source=LIB/'04_blueprints'/(pkg+'.readable.json')
    data=json.loads(source.read_text(encoding='utf8'));a=load(pkg)
    functions=[]
    for f in data['functions']:
        calls=[]
        for n in walk(f['statements']):
            if n.get('op') not in ['EX_FinalFunction','EX_VirtualFunction','EX_CallMath']:continue
            func=n.get('StackNode_resolved',n.get('VirtualFunctionName',''))
            if not any(s in func for s in ['ParameterValue','RandomFloat','CreateDynamicMaterial','MakeColor','Multiply_FloatFloat']):continue
            def describe(n):
                if n.get('op')=='EX_ObjectConst':return dict(object=a.resolve(n['Value']))
                if 'Value' in n and isinstance(n['Value'],(str,int,float,bool)):return n['Value']
                if n.get('op') in ['EX_InstanceVariable','EX_LocalVariable']:
                    return dict(variable=n['Variable'].get('New',{}).get('Path'),scope=n['op'])
                return n
            calls.append(dict(function=func,parameters=[describe(n) for n in n.get('Parameters',[])]))
        functions.append(dict(name=f['name'],calls=calls,statements=f['statements']))
    blueprints.append(dict(source=str(source),functions=functions))
write('blueprint-evidence.json',blueprints)

placements=json.loads((STUDY/'placements.json').read_text(encoding='utf8'))
effect_positions=[p for p in placements if any(k in p['package'] for k in ['GodRay','FogSheet'])]
write('effect-placements.json',effect_positions)

pkg='Wandering_Sword/Content/JH/Core/Characters/BP_SceneHero.uasset'
a=load(pkg);camera=[]
for i,e in enumerate(a.exports,1):
    if any(k in e['ObjectName'] for k in ['Camera','SpriteScene']):
        camera.append(dict(index=i,name=a.resolve(i),class_name=a.resolve(e['ClassIndex']),properties=a.inherited(i)))
write('camera-evidence.json',dict(source=str(LIB/'03_decoded'/(pkg+'.json.gz')),objects=camera,
     fov_comparison_at_16_9=dict(reference_resource_horizontal=40,reference_vertical=math.degrees(2*math.atan(math.tan(math.radians(20))*9/16)),
       island_vertical=38,island_horizontal=math.degrees(2*math.atan(math.tan(math.radians(19))*16/9))),
     limitation='Serialized component settings, not measured final runtime camera.'))

runtime=['assets/island_blender/nameless_island.blend','assets/island_blender/nameless_island.glb',
         'scripts/island.gd','scripts/island_atmosphere.gd','scripts/pixel_bamboo_forest.gd',
         'shaders/pixel_forest_mist.gdshader','shaders/fine_bamboo.gdshader','shaders/pixel_forest_ground.gdshader']
hashes={p:hashlib.sha256((PROJECT/p).read_bytes()).hexdigest() for p in runtime}
write('island-source-hashes.json',hashes)
for p in runtime[2:]:
    target=OUT/'current-code'/p;target.parent.mkdir(parents=True,exist_ok=True)
    target.write_bytes((PROJECT/p).read_bytes())

summary=dict(map=MAP,beam_count=sum('BP_LightBeam_C' in r['class_name'] for r in records),
             fog_sheet_count=sum('BP_FogSheet_C' in r['class_name'] for r in records),
             spot_light_count=sum('SpotLightComponent' in r['class_name'] for r in records),
             geometry_instance_count=len(placements),
             formal_scene_edited=False,reference_game_launched=False,
             current_forest_fog_has_time='TIME' in (PROJECT/'shaders/pixel_forest_mist.gdshader').read_text())
write('summary.json',summary)
print(json.dumps(summary,ensure_ascii=False))
