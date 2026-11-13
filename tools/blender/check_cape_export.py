import bpy,json
print('EXPORT_PROPS',[p.identifier for p in bpy.ops.export_scene.gltf.get_rna_type().properties if 'scene' in p.identifier or 'select' in p.identifier])
print('CURRENT',bpy.context.scene.name,'FILE',bpy.data.filepath)
