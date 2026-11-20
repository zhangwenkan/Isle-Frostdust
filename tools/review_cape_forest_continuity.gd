extends SceneTree
const OUT="res://artifacts/cape-forest-continuity-review/"
func _initialize():call_deferred("run")
func capture(name:String)->void:
	for frame in 8:await process_frame
	RenderingServer.force_draw(false)
	assert(root.get_texture().get_image().save_png(OUT+name+".png")==OK)
func run()->void:
	var args=OS.get_cmdline_user_args();var prefix="pass1" if args.is_empty() else str(args[0])
	root.size=Vector2i(1280,720);root.content_scale_size=Vector2i(1280,720)
	var island=load("res://scenes/layered_island.tscn").instantiate();root.add_child(island);current_scene=island
	island.manual_control=false;island.hud.hide();island.set_process(false);island.hero.pause()
	for mat in island.forest_light_materials:mat.set_shader_parameter("wind_time_override",8.0);mat.set_shader_parameter("forest_light_time_override",10.0)
	var report=[]
	for shot in [["forest_west_mid","forest_west_light",0.0,"forest"],["forest_cape_approach","forest_cape_exit",.65,"exit"],["forest_cape_exit","cape_neck",.1,"mouth"],["cape_neck","cape_entry",.45,"neck"],["cape_entry","cape_center",.75,"platform"],["cape_center","cape_stair_top",.98,"stair-top"],["cape_stair_top","cape_stair_bottom",.56,"stairs"],["cape_stair_bottom","cape_sand",.8,"sand"]]:
		island.set_route_sample(shot[0],shot[1],shot[2]);island.facing="right";island.facing_left=false;island._update_actor(false,0.0,true);island.hero.pause();island.hero.frame=0
		await capture(prefix+"-"+shot[3])
		var author=island.get_node("World").to_local(island.hero.position)
		report.append({"name":shot[3],"author":str(author),"camera":str(island.camera.position),"fov":island.camera.fov,"support":island.last_ground})
	var file=FileAccess.open(OUT+prefix+"-static-check.json",FileAccess.WRITE);file.store_string(JSON.stringify({"views":report,"bindings":island.forest_light_materials.size()},"  "))
	print("CAPE_CONTINUITY_STATIC_DONE ",prefix);quit()
