from pathlib import Path
import json,os,shutil,subprocess

PROJECT=Path(__file__).resolve().parents[1]
SOURCE=PROJECT/'artifacts/gulong-acupoint-preview/runtime'
DEST=PROJECT/'artifacts/gulong-complex-martial-review'
RUNTIME=DEST/'runtime'

def main():
    if RUNTIME.exists() and (RUNTIME/'BepInEx/plugins/ComplexMartialPreview.dll').exists():
        raise FileExistsError('Existing runtime preserved')
    RUNTIME.mkdir(parents=True,exist_ok=True)
    for name in ['GuLong.exe','UnityPlayer.dll','winhttp.dll','.doorstop_version','doorstop_config.ini']:
        shutil.copy2(SOURCE/name,RUNTIME/name)
    for name in ['GuLong_Data','MonoBleedingEdge']:
        if not (RUNTIME/name).exists():
            shutil.copytree(SOURCE/name,RUNTIME/name,copy_function=os.link)
    shutil.copytree(SOURCE/'BepInEx/core',RUNTIME/'BepInEx/core',dirs_exist_ok=True)
    shutil.copytree(SOURCE/'BepInEx/config',RUNTIME/'BepInEx/config',dirs_exist_ok=True)
    (RUNTIME/'BepInEx/plugins').mkdir(exist_ok=True)
    cards=json.loads((PROJECT/'artifacts/gulong-martial-reference/reference-cards.json').read_text(encoding='utf8'))
    wanted=['gl_skill_empty_014','gl_skill_empty_039','gl_skill_empty_088','gl_skill_empty_040','gl_skill_single_083']
    motions=[]
    for card in cards:
        if card['skill']['AnimationName'] not in wanted:continue
        motions.append(dict(id=card['skill']['AnimationName'],name=card['skill']['Name'],duration=card['animation_track_end_seconds'],
            clips=[{k:c[k] for k in ['animation','start','duration','speed','clip_in']} for c in card['body_clips']]))
    plan=dict(output=str(DEST/'original-render'),motions=motions)
    (RUNTIME/'preview-plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf8')
    (DEST/'preview-plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf8')
    managed=RUNTIME/'GuLong_Data/Managed'
    refs=['UnityEngine.dll','UnityEngine.CoreModule.dll','UnityEngine.JSONSerializeModule.dll','UnityEngine.AssetBundleModule.dll','UnityEngine.AnimationModule.dll','UnityEngine.PhysicsModule.dll','UnityEngine.AudioModule.dll','UnityEngine.ImageConversionModule.dll']
    compiler=Path('C:/Program Files (x86)/Microsoft Visual Studio/2022/BuildTools/MSBuild/Current/Bin/Roslyn/csc.exe')
    args=[str(compiler),'/nologo','/target:library','/out:'+str(RUNTIME/'BepInEx/plugins/ComplexMartialPreview.dll'),'/reference:'+str(RUNTIME/'BepInEx/core/BepInEx.dll')]
    args+=['/reference:'+str(managed/r) for r in refs]
    args+=['/reference:'+str(managed/'netstandard.dll')] if (managed/'netstandard.dll').exists() else []
    args.append(str(PROJECT/'tools/ComplexMartialPreview.cs'))
    subprocess.run(args,check=True)
    print('Prepared independent original-animation diagnostic runtime')

if __name__=='__main__':main()
