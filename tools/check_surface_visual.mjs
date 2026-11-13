import {spawn} from 'node:child_process';
import {mkdtemp,readFile,writeFile} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join,resolve} from 'node:path';
import {pathToFileURL} from 'node:url';

const profile=await mkdtemp(join(tmpdir(),'island-surface-preview-'));
const preview=resolve('artifacts/surface-review/interaction-preview.html');
const chrome=spawn('C:/Program Files/Google/Chrome/Application/chrome.exe',[
  '--headless=new','--disable-gpu','--no-first-run','--remote-debugging-port=0',
  '--disable-site-isolation-trials','--disable-features=IsolateOrigins,site-per-process',
  '--user-data-dir='+profile,'--window-size=800,1000',pathToFileURL(preview).href
],{windowsHide:true,stdio:'ignore'});
const pause=ms=>new Promise(r=>setTimeout(r,ms));
let socket;
try {
  let port;
  for(let i=0;i<100;i++){
    try{port=(await readFile(join(profile,'DevToolsActivePort'),'utf8')).split('\n')[0];break}catch{await pause(100)}
  }
  if(!port)throw Error('Chrome did not start');
  const targets=await (await fetch(`http://127.0.0.1:${port}/json/list`)).json();
  const tab=targets.find(t=>t.type==='page');
  socket=new WebSocket(tab.webSocketDebuggerUrl);
  await new Promise((r,j)=>{socket.onopen=r;socket.onerror=j});
  let next=0;const pending=new Map(),contexts=new Set(),errors=[];
  socket.onmessage=e=>{
    const m=JSON.parse(e.data);
    if(m.id){const task=pending.get(m.id);pending.delete(m.id);m.error?task.reject(m.error):task.resolve(m.result)}
    if(m.method==='Runtime.executionContextCreated')contexts.add(m.params.context.id);
    if(m.method==='Runtime.executionContextDestroyed')contexts.delete(m.params.executionContextId);
    if(m.method==='Runtime.executionContextsCleared')contexts.clear();
    if(m.method==='Runtime.exceptionThrown')errors.push(m.params.exceptionDetails.text);
  };
  const call=(method,params={})=>new Promise((resolve,reject)=>{const id=++next;pending.set(id,{resolve,reject});socket.send(JSON.stringify({id,method,params}))});
  await call('Runtime.enable');await call('Page.enable');
  let context;
  for(let i=0;i<120;i++){
    for(const id of contexts){
      const r=await call('Runtime.evaluate',{contextId:id,expression:"!!document.getElementById('island-surface-after')?.complete && !!document.getElementById('island-surface-after')?.naturalWidth",returnByValue:true}).catch(()=>({}));
      if(r.result?.value){context=id;break}
    }
    if(context)break;
    await pause(250);
  }
  if(!context){
    for(const id of contexts)console.log(await call('Runtime.evaluate',{contextId:id,expression:"({url:location.href,text:document.body?.innerText.slice(0,500),images:document.images.length})",returnByValue:true}).catch(()=>({})));
    throw Error('Comparison images did not load');
  }
  const evaluate=async expression=>{
    const r=await call('Runtime.evaluate',{contextId:context,expression,returnByValue:true,awaitPromise:true});
    if(r.exceptionDetails)throw Error(JSON.stringify(r.exceptionDetails));
    return r.result.value;
  };
  const results=[];
  for(const view of ['overview','rock','grass','bark','wood']){
    await evaluate(`document.getElementById('island-surface-view').value='${view}';document.getElementById('island-surface-view').dispatchEvent(new Event('change'));`);
    await pause(80);
    results.push(await evaluate(`(() => {const s=document.getElementById('island-surface-slider');s.value=72;s.dispatchEvent(new Event('input'));const a=document.getElementById('island-surface-after');return {view:document.getElementById('island-surface-view').value,loaded:a.complete&&a.naturalWidth>0,clip:document.getElementById('island-surface-before').style.clipPath,overflow:document.body.scrollWidth>innerWidth}})()`));
  }
  if(results.some(r=>!r.loaded||r.clip!=='inset(0px 28% 0px 0px)'||r.overflow))throw Error(JSON.stringify(results));
  await evaluate("document.getElementById('island-surface-view').value='overview';document.getElementById('island-surface-view').dispatchEvent(new Event('change'));document.getElementById('island-surface-slider').value=50;document.getElementById('island-surface-slider').dispatchEvent(new Event('input'));");
  await pause(100);
  const shot=await call('Page.captureScreenshot',{format:'png'});
  await writeFile('artifacts/surface-review/interaction-check.png',Buffer.from(shot.data,'base64'));
  await call('Emulation.setDeviceMetricsOverride',{width:360,height:900,deviceScaleFactor:1,mobile:false});
  await pause(100);
  const narrow=await evaluate('({overflow:document.body.scrollWidth>innerWidth,width:innerWidth})');
  if(narrow.overflow)throw Error('Narrow layout overflow');
  const report={views:results,narrow,errors};
  await writeFile('artifacts/surface-review/interaction-check.json',JSON.stringify(report,null,2));
  console.log(JSON.stringify(report));
} finally {
  socket?.close();chrome.kill();
}
