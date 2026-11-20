extends RefCounted
## Assemble Blender-authored replacement meshes; creates no geometry.
const ASSET="res://assets/layered_island/tripo_replica/tripo_game_assembly.glb"
const FIT="res://assets/layered_island/tripo_replica/game_assembly.json"

func configure(island:Node3D)->void:
	var world:Node3D=island.get_node("World")
	var fit:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(FIT))
	var packed=load(ASSET) as PackedScene
	assert(packed!=null)
	var addon=packed.instantiate() as Node3D
	addon.name="TripoRockAssembly"
	var retired:Array[String]=[]
	for row:Dictionary in fit.copied_clips:retired.append(str(row.original))
	# Retire the old near shoulders as well, per the latest composition feedback.
	for key in island.layout.reference_cape.cliff_masses:retired.append(str(key))
	retired.append_array(["WALK_Cape_Stairs","Cape_Stair_Support","Cape_Strict_Paving","Cape_Timber_Seat","Cape_Timber_Endgrain"])
	for obj in world.find_children("*","MeshInstance3D",true,false):
		var key=str(obj.name)
		if key in retired or key.begins_with("Cape_Fire_Ring_") or key.begins_with("Cape_Fire_Log_") or key.begins_with("Cape_Strict_Moss_"):
			obj.get_parent().remove_child(obj);obj.queue_free()
	world.add_child(addon)
	for obj in addon.find_children("*","MeshInstance3D",true,false):
		if str(obj.name).begins_with("GameJoin_"):
			obj.name=str(obj.name).trim_prefix("GameJoin_")
			island._configure_art(obj)
		elif str(obj.name)=="Forest_Bank_Continuous_Core":
			var bank=ShaderMaterial.new();bank.shader=preload("res://shaders/forest_bank_wash.gdshader")
			bank.set_shader_parameter("painting",load("res://assets/layered_island/tripo_replica/textures_wash/forest_bank_wash.png"))
			bank.set_shader_parameter("ground_paint",load("res://assets/layered_island/tripo_replica/textures_wash/forest_floor_wash.png"))
			bank.set_shader_parameter("author_world_to_local",world.global_transform.affine_inverse())
			obj.material_override=bank
		else:
			obj.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_ON
			for i in obj.mesh.get_surface_count():
				var original=obj.mesh.surface_get_material(i) as StandardMaterial3D
				if not original:continue
				if original.resource_name.ends_with("_Stone"):
					var wash=ShaderMaterial.new();wash.shader=preload("res://shaders/rock_forest_wash.gdshader")
					wash.set_shader_parameter("painting",original.albedo_texture)
					wash.set_shader_parameter("normal_paint",original.normal_texture)
					wash.set_shader_parameter("use_texture",original.albedo_texture!=null)
					wash.set_shader_parameter("use_normal",original.normal_texture!=null)
					wash.set_shader_parameter("tint",original.albedo_color)
					wash.set_shader_parameter("stone_step",str(obj.name)=="WALK_Tripo_Stairs")
					wash.set_shader_parameter("author_world_to_local",world.global_transform.affine_inverse())
					obj.set_surface_override_material(i,wash)
					continue
				var mat=original.duplicate() as StandardMaterial3D
				mat.texture_filter=BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS_ANISOTROPIC
				# Existing animated fire replaces the sample's solid static flame.
				if "Static_Flame" in mat.resource_name:
					mat.transparency=BaseMaterial3D.TRANSPARENCY_ALPHA
					mat.albedo_color.a=0.0;mat.emission_enabled=false
				obj.set_surface_override_material(i,mat)
	# Local registered painting replaces only the cape/forest continuation map.
	for obj in world.find_children("*","MeshInstance3D",true,false):
		for index in obj.mesh.get_surface_count():
			var ground=obj.get_surface_override_material(index) as ShaderMaterial
			if ground and ground.get_shader_parameter("continuity_enabled")==true:
				ground.set_shader_parameter("continuity_floor",load("res://assets/layered_island/tripo_replica/textures_wash/forest_floor_wash.png"))
	var old_fire:Vector3=island.v3(island.layout.reference_cape.fire_center)
	var new_fire:Vector3=island.v3(fit.sample_anchors.fire_center)
	for key:String in fit.sample_anchors:
		if key=="fire_center":continue
		island.layout.anchors[key]=fit.sample_anchors[key]
		island.anchors[key]=world.to_global(island.v3(fit.sample_anchors[key]))
	island.layout.reference_cape.fire_center=fit.sample_anchors.fire_center
	for obj in world.find_children("Cape_*","MeshInstance3D",true,false):
		var key=str(obj.name)
		if key.begins_with("Cape_Flame_") or key.begins_with("Cape_Smoke_") or key.begins_with("Cape_Ember_"):
			obj.position+=new_fire-old_fire
			obj.set_meta("fire_origin_offset",obj.position)
	island.set_meta("tripo_rock_integrated",true)
	print("TRIPO_ROCK_INTEGRATED colored wash; shared forest light; continuous bank; original asset retained")
