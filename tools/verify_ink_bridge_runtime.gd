extends SceneTree
func _initialize() -> void:
	call_deferred("run")
func run() -> void:
	var island=load("res://scenes/island.tscn").instantiate();island.skip_opening=true
	root.add_child(island);island.set_process(false)
	await process_frame
	var sampler=preload("res://scripts/hero_surface_sampler.gd").new()
	sampler.configure(island)
	var count:=0
	var min_height:=INF
	var max_height:=-INF
	var seam_hits:=0
	for i in 421:
		var x:=lerpf(4.15,14.65,i/420.0)
		for z in [-.20,.25,.70]:
			var sample:Dictionary=sampler.sample(x,z)
			assert(not sample.is_empty(),str(Vector2(x,z)))
			assert(is_finite(sample.height))
			assert(sample.height>.65 and sample.height<2.1,str(Vector2(x,z))+" "+str(sample))
			min_height=minf(min_height,sample.height);max_height=maxf(max_height,sample.height)
			if sample.gap:seam_hits+=1
			count+=1
	var surfaces:=0;var objects:=0
	for node in island.find_children("Bridge_*","MeshInstance3D",true,false):
		objects+=1
		for surface in node.mesh.get_surface_count():
			var material=node.get_active_material(surface) as ShaderMaterial
			assert(material!=null,str(node.name))
			assert(material.shader.resource_path=="res://shaders/ink_bridge.gdshader",str(node.name))
			assert(material.get_shader_parameter("brush_color")!=null)
			surfaces+=1
	assert(objects==42)
	var seam:Dictionary=sampler.sample(4.85,.25)
	assert(str(seam.surface).begins_with("Bridge_Plank_") and seam.height>1.5)
	var max_lift:=0.0
	var min_actor_y:=INF
	for i in 421:
		island.hero_x=lerpf(4.15,14.65,i/420.0)
		island.hero_path_offset=0
		island._position_hero()
		island._update_camera(1.0/60.0,true)
		island.hero.animation=&"walk_right"
		island.hero.frame=i%island.hero.sprite_frames.get_frame_count(&"walk_right")
		island.hero.pause()
		island.hero_presentation.update(1.0/60.0,true)
		var presentation:RefCounted=island.hero_presentation
		max_lift=maxf(max_lift,absf(presentation.lift))
		min_actor_y=minf(min_actor_y,island.hero.position.y+presentation.lift)
	assert(max_lift<.20 and min_actor_y>.65)
	var data={"imported_bridge_meshes":objects,"bound_surfaces":surfaces,"walk_samples":count,"height_range":[min_height,max_height],"narrow_board_seam_samples":seam_hits,"all_walk_samples_have_deck_support":true,"seam_regression":seam,"actor_route_samples":421,"maximum_abs_actor_lift_m":max_lift,"minimum_actor_support_y":min_actor_y,"method":"Imported scene, existing foot presenter and surface sampler across the full bridge. No video."}
	var file:=FileAccess.open("res://artifacts/ink-bridge-review/runtime-verification.json",FileAccess.WRITE)
	file.store_string(JSON.stringify(data,"  "))
	print("INK_BRIDGE_RUNTIME_OK ",data)
	await process_frame
	await RenderingServer.frame_post_draw
	quit(0)
