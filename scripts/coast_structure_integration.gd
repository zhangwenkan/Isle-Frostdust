extends RefCounted
## Assemble the Blender-authored continuous cape and recovered stone flight.
const ASSET="res://assets/layered_island/coast_recovery/coast_structure.glb"
const FIT="res://assets/layered_island/coast_recovery/assembly.json"

func configure(island:Node3D)->void:
	var world:Node3D=island.get_node("World")
	var fit:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(FIT))
	var addon=(load(ASSET) as PackedScene).instantiate() as Node3D
	addon.name="CoastStructureRecovery"
	var retired:Array=fit.replace.duplicate()
	retired.append_array(fit.retire_extra)
	retired.append_array(island.layout.reference_cape.cliff_masses)
	for obj in world.find_children("*","MeshInstance3D",true,false):
		if str(obj.name) in retired or str(obj.name).begins_with("Cape_Strict_Moss_"):
			obj.get_parent().remove_child(obj);obj.queue_free()
	world.add_child(addon)
	for obj in addon.find_children("*","MeshInstance3D",true,false):
		obj.name=str(obj.name).trim_prefix("Recovery_")
		island._configure_art(obj)
		if str(obj.name)=="WALK_Forest_Ground":
			for index in obj.mesh.get_surface_count():
				var ground=obj.get_surface_override_material(index) as ShaderMaterial
				if ground:
					ground.set_shader_parameter("continuity_floor",load("res://assets/layered_island/coast_recovery/cape_floor.png"))
					ground.set_shader_parameter("continuity_bounds",Vector4(-72.5,4.0,23.0,31.0))
		for index in obj.mesh.get_surface_count():
			var original=obj.mesh.surface_get_material(index) as StandardMaterial3D
			if not original or not original.resource_name.begins_with("Recovery_"):continue
			var mat=ShaderMaterial.new();mat.shader=preload("res://shaders/rock_forest_wash.gdshader")
			mat.set_shader_parameter("painting",original.albedo_texture)
			mat.set_shader_parameter("normal_paint",original.normal_texture)
			mat.set_shader_parameter("use_texture",original.albedo_texture!=null)
			mat.set_shader_parameter("use_normal",original.normal_texture!=null)
			mat.set_shader_parameter("tint",original.albedo_color)
			mat.set_shader_parameter("stone_step",str(obj.name)=="WALK_Cape_Stairs")
			mat.set_shader_parameter("author_world_to_local",world.global_transform.affine_inverse())
			obj.set_surface_override_material(index,mat)
	var old_fire:Vector3=island.v3(island.layout.reference_cape.fire_center)
	var new_fire:Vector3=island.v3(fit.fire_center)
	for key:String in fit.anchors:
		island.layout.anchors[key]=fit.anchors[key]
		island.anchors[key]=world.to_global(island.v3(fit.anchors[key]))
	island.layout.reference_cape.fire_center=fit.fire_center
	for obj in world.find_children("Cape_*","MeshInstance3D",true,false):
		if str(obj.name).begins_with("Cape_Flame_") or str(obj.name).begins_with("Cape_Smoke_") or str(obj.name).begins_with("Cape_Ember_"):
			obj.position+=new_fire-old_fire;obj.set_meta("fire_origin_offset",obj.position)
	var shoreline=PackedVector2Array()
	for p:Array in fit.shoreline:shoreline.append(Vector2(p[0],p[1]))
	island.sea_material.set_shader_parameter("cape_shoreline",shoreline)
	island.set_meta("coast_structure_recovery",true)
	print("COAST_STRUCTURE_RECOVERY ",fit.revision)
