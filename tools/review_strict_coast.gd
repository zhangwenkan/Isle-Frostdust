extends SceneTree
const OUT="res://artifacts/strict-forest-coast-review/"
func _initialize():call_deferred("run")
func capture(name:String)->void:
	for frame in 12:await process_frame
	RenderingServer.force_draw(false)
	assert(root.get_texture().get_image().save_png(OUT+name+".png")==OK)
func run()->void:
	var args=OS.get_cmdline_user_args();var prefix="pass1" if args.is_empty() else str(args[0])
	root.size=Vector2i(1280,720);root.content_scale_size=Vector2i(1280,720)
	var island=load("res://scenes/layered_island.tscn").instantiate();root.add_child(island);current_scene=island
	island.manual_control=false;island.hud.hide();island.set_process(false);island.hero.pause()
	for mat in island.forest_light_materials:mat.set_shader_parameter("wind_time_override",8.0);mat.set_shader_parameter("forest_light_time_override",10.0)
	var report=[]
	for shot in [["forest_west_mid","forest_west_light",0.0,"forest"],["forest_cape_approach","forest_cape_exit",.68,"approach"],["cape_neck","cape_entry",.45,"mouth"],["cape_entry","cape_center",.85,"camp"],["cape_center","cape_stair_top",.92,"stair-top"],["cape_stair_top","cape_stair_bottom",.56,"stairs"],["cape_stair_bottom","cape_sand",.8,"sand"]]:
		island.set_route_sample(shot[0],shot[1],shot[2]);island.facing="right";island.facing_left=false;island._update_actor(false,0.0,true);island.hero.pause();island.hero.frame=0
		island._update_occluders(0.0);await capture(prefix+"-"+shot[3])
		report.append({"name":shot[3],"camera":str(island.camera.position),"fov":island.camera.fov,"support":island.last_ground})
	island.set_route_sample("cape_entry","cape_center",.85);island._update_actor(false,0.0,true)
	var target=island.get_node("World").to_global(Vector3(-60.5,5.2,-10.0))
	island.camera.position=target+island.get_node("World").global_basis*Vector3(0,12.4,34.1);island.camera.fov=42;island.camera.look_at(target)
	await capture(prefix+"-overview")
	var failures=[];var samples=0
	for edge:Array in island.layout.edges:
		for i in 81:
			var p:Vector3=(island.anchors[edge[0]] as Vector3).lerp(island.anchors[edge[1]],float(i)/80.0)
			var hit:Dictionary=island.surface.sample(p);samples+=1
			if hit.is_empty():failures.append({"edge":edge,"sample":i,"error":"missing floor"})
	var file=FileAccess.open(OUT+prefix+"-static-check.json",FileAccess.WRITE)
	file.store_string(JSON.stringify({"views":report,"bindings":island.forest_light_materials.size(),"route_samples":samples,"failures":failures},"  "))
	print("STRICT_COAST_STATIC_DONE ",prefix," failures=",failures.size());quit(0 if failures.is_empty() else 1)
