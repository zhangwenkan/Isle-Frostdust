using System;
using System.IO;
using System.Text;
using System.Collections;
using System.Collections.Generic;
using System.Globalization;
using BepInEx;
using UnityEngine;
using UnityEngine.Animations;
using UnityEngine.Playables;

[Serializable] public class MotionClipPlan { public string animation; public float start; public float duration; public float speed; public float clip_in; }
[Serializable] public class MotionPlan { public string id; public string name; public float duration; public MotionClipPlan[] clips; }
[Serializable] public class PreviewPlan { public string output; public MotionPlan[] motions; }

[BepInPlugin("local.gulong.complex.preview", "Complex Martial Reference Preview", "1.0.0")]
public sealed class ComplexMartialPreview : BaseUnityPlugin {
    PreviewPlan plan;
    MotionClipPlan C(string animation,float start,float duration){return new MotionClipPlan{animation=animation,start=start,duration=duration,speed=1,clip_in=0};}
    MotionPlan M(string id,string name,float duration,params MotionClipPlan[] clips){return new MotionPlan{id=id,name=name,duration=duration,clips=clips};}
    void FallbackPlan(){
        plan=new PreviewPlan{output=Path.Combine(Paths.GameRootPath,"original-render"),motions=new MotionPlan[]{
            M("gl_skill_empty_014","踏月留香",2.566667f,C("gl_skill_empty_014a",0,.4f),C("gl_skill_empty_014b",.4f,1.2f),C("gl_skill_empty_014c",1.566667f,1)),
            M("gl_skill_empty_039","天落金鹏",2.933333f,C("gl_skill_empty_039a",0,1.266667f),C("gl_skill_empty_039b",1.266667f,.5f),C("gl_skill_empty_039c",1.766667f,1.166667f)),
            M("gl_skill_empty_088","孤形吊影",2.866667f,C("gl_skill_empty_088a",0,.6f),C("gl_skill_empty_088b",.6f,.466667f),C("gl_skill_empty_088c",1.066667f,1.8f)),
            M("gl_skill_empty_040","凤舞九天",3.266667f,C("gl_skill_empty_040",0,3.266667f)),
            M("gl_skill_single_083","摸爬滚打剑",2.4f,C("gl_skill_single_083a",0,.833333f),C("gl_skill_single_083b",.833333f,.466667f),C("gl_skill_single_083c",1.3f,1.1f))
        }};
    }
    void Awake() {
        plan=JsonUtility.FromJson<PreviewPlan>(File.ReadAllText(Path.Combine(Paths.GameRootPath,"preview-plan.json")));
        if(plan==null || plan.motions==null)FallbackPlan();
        Directory.CreateDirectory(plan.output); Application.runInBackground=true; StartCoroutine(Begin());
    }
    IEnumerator Begin() {
        yield return null; yield return null;
        IEnumerator e=Export();
        while(true) {
            bool more=false;
            try {more=e.MoveNext();} catch(Exception ex) {File.WriteAllText(Path.Combine(plan.output,"ERROR.txt"),ex.ToString());Logger.LogError(ex);Application.Quit();yield break;}
            if(!more)break; yield return e.Current;
        }
        File.WriteAllText(Path.Combine(plan.output,"DONE.txt"),"Reference body-animation sampling complete."); Application.Quit();
    }
    string F(float v){return v.ToString("F6",CultureInfo.InvariantCulture);}
    string V(Vector3 p){return F(p.x)+","+F(p.y)+","+F(p.z);}
    void Pose(float time, MotionPlan motion, AnimationMixerPlayable mixer, AnimationClipPlayable[] clips, PlayableGraph graph) {
        float total=0;
        for(int j=0;j<clips.Length;j++) {
            MotionClipPlan cp=motion.clips[j];
            float w=(time>=cp.start-.00001f && time<=cp.start+cp.duration+.00001f)?1:0;
            if(j>0 && time<cp.start)w=0;
            if(j+1<clips.Length && time>=motion.clips[j+1].start) {
                float overlap=cp.start+cp.duration-motion.clips[j+1].start;
                w=overlap>.00001f?Mathf.Clamp01((cp.start+cp.duration-time)/overlap):0;
            }
            if(j>0) {
                float overlap=motion.clips[j-1].start+motion.clips[j-1].duration-cp.start;
                if(overlap>.00001f && time<cp.start+overlap)w*=Mathf.Clamp01((time-cp.start)/overlap);
            }
            if(j==clips.Length-1 && time>=cp.start+cp.duration)w=1;
            clips[j].SetTime(Mathf.Clamp(time-cp.start,0,cp.duration)*cp.speed+cp.clip_in);
            mixer.SetInputWeight(j,w); total+=w;
        }
        if(total>0)for(int j=0;j<clips.Length;j++)mixer.SetInputWeight(j,mixer.GetInputWeight(j)/total);
        graph.Evaluate(0);
    }
    IEnumerator Export() {
        foreach(Camera c in FindObjectsOfType<Camera>())c.enabled=false;
        foreach(AudioListener a in FindObjectsOfType<AudioListener>())a.enabled=false;
        Physics.autoSimulation=false; QualitySettings.shadows=ShadowQuality.Disable;
        RenderSettings.ambientMode=UnityEngine.Rendering.AmbientMode.Flat;
        RenderSettings.ambientLight=new Color(.72f,.72f,.75f);RenderSettings.fog=false;
        AssetBundle bundle=AssetBundle.LoadFromFile(@"D:\古龙风云录\gulong\AssetBundles\character");
        if(bundle==null)throw new Exception("character bundle missing");
        GameObject prefab=bundle.LoadAsset<GameObject>("assets/character/b/ba026/prefab/ba026.prefab");
        Light key=new GameObject("Key").AddComponent<Light>();key.type=LightType.Directional;key.intensity=1;key.transform.rotation=Quaternion.Euler(40,-30,0);
        Light fill=new GameObject("Fill").AddComponent<Light>();fill.type=LightType.Directional;fill.intensity=.45f;fill.transform.rotation=Quaternion.Euler(20,140,0);
        Camera cam=new GameObject("DiagnosticCamera").AddComponent<Camera>();cam.enabled=false;cam.orthographic=true;
        cam.nearClipPlane=.01f;cam.farClipPlane=100;cam.clearFlags=CameraClearFlags.SolidColor;cam.backgroundColor=new Color(.12f,.15f,.19f,1);
        cam.allowHDR=false;cam.allowMSAA=true;
        RenderTexture rt=new RenderTexture(768,768,24,RenderTextureFormat.ARGB32);rt.antiAliasing=4;rt.Create();cam.targetTexture=rt;
        Texture2D tex=new Texture2D(768,768,TextureFormat.RGB24,false);
        HumanBodyBones[] bones={HumanBodyBones.Hips,HumanBodyBones.Head,HumanBodyBones.RightHand,HumanBodyBones.LeftHand,HumanBodyBones.RightFoot,HumanBodyBones.LeftFoot,HumanBodyBones.RightUpperLeg,HumanBodyBones.LeftUpperLeg};
        Logger.LogInfo("Plan output="+plan.output+" motions="+(plan.motions==null?"NULL":plan.motions.Length.ToString()));
        foreach(MotionPlan motion in plan.motions) {
            Logger.LogInfo("Motion "+motion.id+" clips="+motion.clips.Length);
            string output=Path.Combine(plan.output,motion.id);Directory.CreateDirectory(output);
            GameObject model=Instantiate(prefab);model.transform.position=Vector3.zero;model.transform.rotation=Quaternion.identity;
            foreach(MonoBehaviour b in model.GetComponentsInChildren<MonoBehaviour>(true))if(b!=null)b.enabled=false;
            Animator animator=model.GetComponentInChildren<Animator>(true);animator.enabled=true;animator.runtimeAnimatorController=null;
            Logger.LogInfo("Animator found; avatar="+(animator.avatar!=null));
            animator.cullingMode=AnimatorCullingMode.AlwaysAnimate;animator.applyRootMotion=false;animator.Rebind();
            foreach(SkinnedMeshRenderer sk in model.GetComponentsInChildren<SkinnedMeshRenderer>(true))sk.updateWhenOffscreen=true;
            PlayableGraph graph=PlayableGraph.Create(motion.id);graph.SetTimeUpdateMode(DirectorUpdateMode.Manual);
            AnimationMixerPlayable mixer=AnimationMixerPlayable.Create(graph,motion.clips.Length);
            AnimationPlayableOutput apo=AnimationPlayableOutput.Create(graph,"Body",animator);apo.SetSourcePlayable(mixer);
            AnimationClipPlayable[] clips=new AnimationClipPlayable[motion.clips.Length];
            StringBuilder meta=new StringBuilder("Model ba026 / Chen Yu; original clips on original Avatar; no game displacement/VFX/cloth/physics.\n");
            for(int j=0;j<clips.Length;j++) {
                string clipName=motion.clips[j].animation;
                AnimationClip source=bundle.LoadAsset<AnimationClip>("assets/character/all_action/animation/"+clipName+".anim");
                if(source==null)throw new Exception("Missing clip "+clipName);
                clips[j]=AnimationClipPlayable.Create(graph,source);clips[j].SetApplyFootIK(false);
                graph.Connect(clips[j],0,mixer,j);
                meta.AppendLine(clipName+" length="+source.length+" rate="+source.frameRate+" human="+source.isHumanMotion);
            }
            graph.Play();int count=Mathf.RoundToInt(motion.duration*30)+1;
            Bounds all=new Bounds();bool started=false;
            StringBuilder csv=new StringBuilder("frame,time");foreach(HumanBodyBones bone in bones)csv.Append(","+bone+"_x,"+bone+"_y,"+bone+"_z");csv.AppendLine();
            for(int i=0;i<count;i++) {
                float t=Mathf.Min(i/30f,motion.duration);Pose(t,motion,mixer,clips,graph);yield return null;
                csv.Append(i+","+F(t));
                foreach(HumanBodyBones bone in bones) {
                    Transform bt=animator.GetBoneTransform(bone);
                    if(bt==null)throw new Exception("Missing bone "+bone+" for "+motion.id);
                    Vector3 v=bt.position;csv.Append(","+V(v));
                    if(!started){all=new Bounds(v,Vector3.zero);started=true;}else all.Encapsulate(v);
                }
                csv.AppendLine();
            }
            // One fixed framing for the entire motion, including the highest/lowest sampled pose.
            Vector3 target=all.center;float radius=Mathf.Max(all.size.y,Mathf.Sqrt(all.size.x*all.size.x+all.size.z*all.size.z));
            cam.orthographicSize=radius*.5f+.55f;
            string[] views={"side","three-quarter"};foreach(string view in views)Directory.CreateDirectory(Path.Combine(output,view));
            for(int i=0;i<count;i++) {
                Pose(Mathf.Min(i/30f,motion.duration),motion,mixer,clips,graph);yield return null;
                for(int v=0;v<views.Length;v++) {
                    Vector3 dir=v==0?new Vector3(1,0,0):new Vector3(1,.1f,.7f).normalized;
                    cam.transform.position=target+dir*12;cam.transform.LookAt(target);cam.Render();RenderTexture.active=rt;
                    tex.ReadPixels(new Rect(0,0,768,768),0,0);tex.Apply();
                    File.WriteAllBytes(Path.Combine(output,views[v],String.Format("frame_{0:D3}.png",i)),ImageConversion.EncodeToPNG(tex));
                }
            }
            File.WriteAllText(Path.Combine(output,"bones.csv"),csv.ToString());
            meta.AppendLine("frames="+count+" duration="+motion.duration+" orthoSize="+cam.orthographicSize+" cameraTarget="+target);
            File.WriteAllText(Path.Combine(output,"metadata.txt"),meta.ToString());
            graph.Destroy();Destroy(model);yield return null;
        }
        RenderTexture.active=null;cam.targetTexture=null;rt.Release();
    }
}
