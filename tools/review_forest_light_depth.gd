extends SceneTree
const OUT="res://artifacts/forest-light-depth-review/"
func _initialize():call_deferred("run")
func capture(path):
	for tick in 20:await process_frame
	assert(root.get_texture().get_image().save_jpg(OUT+path+".jpg",.95)==OK)
	assert(root.get_texture().get_image().save_png(OUT+path+".png")==OK)
func run():
	var args=OS.get_cmdline_user_args();var prefix="pass1" if args.is_empty() else str(args[0])
	root.size=Vector2i(1280,720);root.content_scale_size=Vector2i(1280,720)
	var island=load("res://scenes/layered_island.tscn").instantiate();root.add_child(island);current_scene=island
	island.manual_control=false;island.hud.hide();island.set_process(false);island.hero.pause()
	for path in ["layered_forest_surface.gdshader","forest_role_leaf.gdshader","forest_depth_paint.gdshader","forest_depth_solid.gdshader","forest_layer_mist.gdshader","forest_local_air.gdshader","forest_sunray_veil.gdshader","layered_left.gdshader","layered_sea.gdshader","beach_sand.gdshader","beach_swash.gdshader","layered_distance.gdshader","layered_cloudsea.gdshader"]:
		var shader=load("res://shaders/"+path) as Shader;shader.code=shader.code.replace("TIME","8.0")
	var rays=island.get_node("World").find_children("Forest_Sunray_*","MeshInstance3D",true,false)
	var report=[];var bindings=[]
	for mat in island.forest_light_materials:
		bindings.append({"shader":mat.shader.resource_path,"ray":str(mat.get_shader_parameter("forest_ray_direction"))})
	for shot in [["forest_west_light","forest_west_mid",.8,"middle"],["forest_west_gate","forest_west_light",.8,"clearing"],["forest_west_entry","forest_west_gate",.6,"gate"],["forest_west_shade","forest_west_end",1.0,"end"],["forest_end","forest_west_entry",.45,"connection"],["beach","stair_bottom",.0,"beach"],["bridge_left","bridge_right",.5,"bridge"]]:
		island.set_route_sample(shot[0],shot[1],shot[2]);island.facing="right";island.facing_left=true;island._update_actor(false,0.,true);island._update_occluders(2.0);island.hero.pause();island.hero.frame=0
		for time in ([0.0,5.0,10.0,15.0] if shot[3] in ["middle","clearing"] else [5.0]):
			for mat in island.forest_light_materials:mat.set_shader_parameter("forest_light_time_override",time);mat.set_shader_parameter("forest_light_strength",1.0)
			for ray in rays:ray.visible=true
			await capture(prefix+"-"+shot[3]+"-t%02d"%time)
			report.append({"view":shot[3],"light_time":time,"camera":str(island.camera.global_position),"sea":island.sea_material.get_shader_parameter("scene_opacity"),"supported":not island.last_ground.is_empty()})
		if shot[3]=="middle":
			for mat in island.forest_light_materials:mat.set_shader_parameter("forest_light_time_override",5.0)
			for ray in rays:ray.visible=false
			await capture(prefix+"-middle-no-rays")
			for mat in island.forest_light_materials:mat.set_shader_parameter("forest_light_strength",0.0)
			await capture(prefix+"-middle-no-shared-field")
	var file=FileAccess.open(OUT+prefix+"-shots.json",FileAccess.WRITE)
	file.store_string(JSON.stringify({"views":report,"ray_carriers":rays.size(),"bound_materials":bindings},"  "))
	print("FOREST_LIGHT_DEPTH_CAPTURE_DONE materials=",bindings.size()," rays=",rays.size());quit()
