extends "res://tools/capture_cloud_water.gd"
const OUT := "res://artifacts/full-island-ink-review/"

func shot(label: String) -> void:
	island._update_ground_contact()
	await settle(18)
	await RenderingServer.frame_post_draw
	assert(root.get_texture().get_image().save_png(OUT+phase+"-"+label+".png")==OK)
	print("INK_STATIC ",phase," ",label)

func run_capture() -> void:
	root.size=Vector2i(1280,720)
	island=load("res://scenes/island.tscn").instantiate()
	island.skip_opening=true
	root.add_child(island);current_scene=island
	island.set_process(false);island.hero.pause();island.hud.hide()
	island.hero.animation=&"idle_right";island.hero.flip_h=false
	control_time(island)
	freeze_material(island.atmosphere.mountain_cloud_material,"fog")
	freeze_material(island.background_comparison.original_sky,"sky")
	freeze_material(island.background_comparison.comparison_sky,"sky")
	set_time(1.0)
	for mode in [0,1]:
		island.background_comparison.set_mode(mode)
		for point in [{"x":-15.2,"label":"cape"},{"x":-10.2,"label":"west"},{"x":-6.8,"label":"valley"},{"x":1.5,"label":"waterfall"},{"x":9.5,"label":"bridge"},{"x":17.0,"label":"east-entry"},{"x":23.0,"label":"east-end"}]:
			position(point.x)
			await shot(("original-" if mode==0 else "sunset-")+point.label)
	island.background_comparison.set_mode(0)
	island.camera_effects.dof_blur_near_enabled=false
	island.camera_effects.dof_blur_far_enabled=false
	position(20.0)
	await shot("east-no-dof")
	island.camera.position=Vector3(18,9.5,11)
	island.camera.look_at(Vector3(20,.6,0))
	await shot("east-detail")
	position(-6.8)
	await shot("valley-no-dof")
	var rows:Array=[]
	for node in island.find_children("*","MeshInstance3D",true,false):
		for surface in node.mesh.get_surface_count():
			var material=node.get_active_material(surface)
			rows.append({"object":str(node.name),"surface":surface,"shader":material.shader.resource_path if material is ShaderMaterial else "standard","material":node.mesh.surface_get_material(surface).resource_name if node.mesh.surface_get_material(surface) else ""})
	var f:=FileAccess.open(OUT+phase+"-materials.json",FileAccess.WRITE)
	f.store_string(JSON.stringify(rows,"  "))
	quit(0)
