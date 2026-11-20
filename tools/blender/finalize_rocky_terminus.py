"""Finalize the shared cliff folds and the actual descending stair metadata."""
exec(compile(open('D:/自己做着玩的/孤屿霜尘/tools/blender/left_finish_common.py',encoding='utf8').read(),'left_finish_common.py','exec'))
rc=LAYOUT['reference_cape'];data=rc['rocky_terminus'];assert data.get('polish') and not data.get('finalized')
COL=bpy.data.collections[data['collection']];MATS['side']=[m for m in bpy.data.materials if m.name.startswith('RC_cape_side')][-1]
border=[Vector(p) for p in data['outline']];middle=[];low=[]
for i,p in enumerate(border):
    prev=border[max(0,i-1)];nxt=border[min(len(border)-1,i+1)];d=nxt-prev;n=Vector((d.y,-d.x,0)).normalized()
    # Shared unequal corner offsets produce ledges without disconnected rocks.
    offset=.28+.13*math.sin(i*1.7)
    middle.append(Vector((p.x+n.x*offset,p.y+n.y*offset,p.z*(.43+.04*math.sin(i)))))
    low.append(Vector((p.x+n.x*(offset+.11),p.y+n.y*(offset+.11),-.65)))
b=Mesh('Cape_Terminus_Bedrock_Folds')
for i,(p,q) in enumerate(zip(border,border[1:])):
    if p.y>8.7 and q.y>8.7 and p.x<-64 and q.x>-63:continue
    b.part([p,q,middle[i+1],middle[i]],[(0,1,2,3)],'side')
    b.part([middle[i],middle[i+1],low[i+1],low[i]],[(0,1,2,3)],'side')
new=b.build();old=SCENE.objects['Cape_Terminus_Bedrock'];old.data=new.data;bpy.data.objects.remove(new,do_unlink=True)
rc['stairs']['top']=LAYOUT['anchors']['cape_stair_top'];rc['stairs']['bottom']=LAYOUT['anchors']['cape_stair_bottom'];rc['stairs']['steps']=30
data['finalized']={'shared_unequal_cliff_folds':True,'single_stair_metadata_updated':True,'art_status':'awaiting user evaluation'}
export('forest-rocky-terminus-review')
