extends SceneTree
const OUT="res://artifacts/forest-wind-mist-review/"
func _initialize():call_deferred("run")
func run():
	var args=OS.get_cmdline_user_args();var prefix="pass1" if args.is_empty() else str(args[0])
	root.size=Vector2i(1280,720);root.content_scale_size=Vector2i(1280,720)
	var island=load("res://scenes/layered_island.tscn").instantiate();root.add_child(island);current_scene=island
	island.manual_control=false;island.hud.hide();island.set_process(false)
	for path in ["layered_left.gdshader","layered_forest_surface.gdshader","forest_role_leaf.gdshader","forest_depth_paint.gdshader","forest_depth_solid.gdshader","forest_layer_mist.gdshader","forest_local_air.gdshader","layered_sea.gdshader","beach_sand.gdshader","beach_swash.gdshader","layered_distance.gdshader","layered_cloudsea.gdshader"]:
		var shader=load("res://shaders/"+path) as Shader;shader.code=shader.code.replace("TIME","8.0")
	var mist_nodes=island.get_node("World").find_children("Forest_Mist_*","MeshInstance3D",true,false)
	var env:Environment
	for child in island.get_children():
		if child is WorldEnvironment:env=child.environment
	var report=[]
	for shot in [["forest_west_gate","forest_west_light",.8,"clearing"],["forest_west_light","forest_west_mid",.8,"middle"],["forest_end","forest_west_entry",.45,"connection"],["forest_west_shade","forest_west_end",1.0,"end"],["forest_west_entry","forest_west_gate",.6,"gate"],["forest_step2","forest_landing",.6,"old_forest"],["beach","stair_bottom",.0,"beach"],["bridge_left","bridge_right",.5,"bridge"]]:
		island.set_route_sample(shot[0],shot[1],shot[2]);island.facing="right";island.facing_left=true;island._update_actor(false,0.,true);island._update_occluders(2.0);island.hero.pause();island.hero.frame=0
		var variants=["current","no_mist","no_far_dof","no_volume","no_both_dof","raw_layers"] if shot[3]=="middle" else ["current"]
		for variant in variants:
			for n in mist_nodes:n.visible=variant not in ["no_mist","raw_layers"]
			island.camera.attributes.dof_blur_far_enabled=variant not in ["no_far_dof","no_both_dof","raw_layers"]
			var forest_view=shot[3] not in ["beach","bridge"]
			island.camera.attributes.dof_blur_near_enabled=not forest_view and variant not in ["no_both_dof","raw_layers"]
			env.volumetric_fog_enabled=variant not in ["no_volume","raw_layers"]
			for i in 28:await process_frame
			await RenderingServer.frame_post_draw
			var path=OUT+prefix+"-"+shot[3]+"-"+variant
			assert(root.get_texture().get_image().save_jpg(path+".jpg",.94)==OK)
			assert(root.get_texture().get_image().save_png(path+".png")==OK)
			report.append({"view":shot[3],"variant":variant,"camera":str(island.camera.position),"sea_opacity":island.sea_material.get_shader_parameter("scene_opacity"),"support":not island.last_ground.is_empty(),"mist_meshes":mist_nodes.size(),"dof_far_distance":island.camera.attributes.dof_blur_far_distance})
	var f=FileAccess.open(OUT+prefix+"-shots.json",FileAccess.WRITE);f.store_string(JSON.stringify(report,"  "))
	print("FOREST_WIND_MIST_CAPTURE_DONE");quit()
