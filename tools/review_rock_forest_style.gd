extends SceneTree
var out="res://artifacts/rock-forest-style-review/"
func _initialize():call_deferred("run")
func capture(file:String)->void:
	for frame in 28:await process_frame
	RenderingServer.force_draw(false)
	assert(root.get_texture().get_image().save_png(out+file+".png")==OK)
func run()->void:
	if "--style-before" in OS.get_cmdline_user_args():out+="before/"
	Engine.time_scale=0.0
	root.size=Vector2i(1280,720);root.content_scale_size=Vector2i(1280,720)
	root.content_scale_mode=Window.CONTENT_SCALE_MODE_VIEWPORT;root.content_scale_aspect=Window.CONTENT_SCALE_ASPECT_KEEP
	var island=load("res://scenes/layered_island.tscn").instantiate();root.add_child(island);current_scene=island
	if not "--style-before" in OS.get_cmdline_user_args():
		var rock_count=0
		for obj in island.get_node("World").find_children("*","MeshInstance3D",true,false):
			assert(not str(obj.name).begins_with("Cape_Strict_Rock_Near_"))
			for index in obj.mesh.get_surface_count():
				var mat=obj.get_surface_override_material(index) as ShaderMaterial
				if mat and mat.shader.resource_path=="res://shaders/rock_forest_wash.gdshader":
					assert(mat in island.forest_light_materials)
					assert(mat.get_shader_parameter("painting")!=null and mat.get_shader_parameter("normal_paint")!=null)
					rock_count+=1
		assert(rock_count==2)
	island.manual_control=false;island.hud.hide();island.set_process(false);island.hero.pause()
	for mat in island.forest_light_materials:mat.set_shader_parameter("forest_light_time_override",0.0)
	var views=[]
	for shot in [["forest_cape_approach","forest_cape_exit",.75,"approach"],["cape_entry","cape_center",.9,"camp"],["cape_stair_top","cape_stair_bottom",.48,"stairs"],["cape_stair_bottom","cape_sand",.5,"sand"]]:
		island.set_route_sample(shot[0],shot[1],shot[2]);island.facing="right";island.facing_left=false;island._update_actor(false,0.0,true);island.hero.pause();island.hero.frame=0
		island._update_occluders(0.0);await capture("game-"+shot[3])
		views.append({"view":shot[3],"actor":str(island.hero.position),"ground":island.last_ground,"camera":str(island.camera.position),"fov":island.camera.fov})
	var file=FileAccess.open(out+"game-check.json",FileAccess.WRITE);file.store_string(JSON.stringify({"integration":island.get_meta("tripo_rock_integrated",false),"views":views,"scope":"Four static game positions; shader time frozen at zero for matched comparison, no continuous movement audit."},"  "))
	print("ROCK_FOREST_STYLE_STATIC_COMPLETE");quit()
