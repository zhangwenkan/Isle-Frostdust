extends SceneTree
func _initialize():call_deferred("run")
func run():
	var island=load("res://scenes/layered_island.tscn").instantiate();root.add_child(island)
	var report=[]
	for node in island.get_node("World").find_children("*","MeshInstance3D",true,false):
		if not str(node.name).begins_with("Cape_Strict_Rock") and not str(node.name).begins_with("Forest_Strict_Leaves_00"):continue
		for i in node.mesh.get_surface_count():
			var original=node.mesh.surface_get_material(i) as StandardMaterial3D
			var m=node.get_surface_override_material(i) as ShaderMaterial
			report.append({"node":str(node.name),"surface":i,"original":original.resource_name,"texture":str(original.albedo_texture),"shader":m.shader.resource_path if m else "none","use_texture":m.get_shader_parameter("use_texture") if m else null,"sampler":str(m.get_shader_parameter("painting")) if m else "none"})
	var f=FileAccess.open("res://artifacts/strict-forest-coast-review/materials.json",FileAccess.WRITE);f.store_string(JSON.stringify(report,"  "));print(JSON.stringify(report.slice(0,4)));quit()
