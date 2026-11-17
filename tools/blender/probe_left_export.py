import bpy
print([(p.identifier, str(p.default)) for p in bpy.ops.export_scene.gltf.get_rna_type().properties if 'color' in p.identifier])
