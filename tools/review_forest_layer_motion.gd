extends SceneTree
const OUT="res://artifacts/forest-layer-role-review/"
var island:Node3D
func _initialize():call_deferred("run")
func run():
	DirAccess.make_dir_recursive_absolute(OUT+"motion-frames")
	root.size=Vector2i(1280,720);root.content_scale_size=Vector2i(1280,720)
	island=load("res://scenes/layered_island.tscn").instantiate();root.add_child(island);current_scene=island
	island.manual_control=false;island.hud.hide();island.set_route_sample("forest_end","forest_west_entry",.0)
	var report=[];var max_camera_step=0.0;var max_height_step=0.0;var failures=[]
	var previous_height:float=island.hero.position.y
	for tick in 912:
		var input=Vector2.ZERO
		if tick>=24 and tick<384:input=Vector2.LEFT
		if tick>=456 and tick<816:input=Vector2.RIGHT
		var before:Vector3=island.camera.position
		island.advance_input(input,1.0/24.0)
		await process_frame
		max_camera_step=maxf(max_camera_step,island.camera.position.distance_to(before))
		max_height_step=maxf(max_height_step,absf(island.hero.position.y-previous_height));previous_height=island.hero.position.y
		if island.last_ground.is_empty() and failures.is_empty():failures.append("Missing support")
		if tick%2==0:
			await RenderingServer.frame_post_draw
			var im=root.get_texture().get_image();im.resize(960,540,Image.INTERPOLATE_LANCZOS)
			assert(im.save_jpg(OUT+"motion-frames/frame-%04d.jpg"%(tick/2),.93)==OK)
		if tick%24==0:report.append({"frame":tick,"input":str(input),"camera":str(island.camera.position),"actor":str(island.hero.position),"anchor":island.current_anchor,"sea_opacity":island.sea_material.get_shader_parameter("scene_opacity")})
	var event=InputEventKey.new();event.physical_keycode=KEY_F5;event.pressed=true;island._unhandled_key_input(event)
	var locked:Transform3D=island.camera.transform
	var locked_opacity=float(island.sea_material.get_shader_parameter("scene_opacity"))
	var locked_forest=float(island.forest_paintings[0].get_shader_parameter("opacity"))
	for i in 48:island.advance_input(Vector2.LEFT,1.0/24.0);await process_frame
	if not island.camera.transform.is_equal_approx(locked):failures.append("F5 camera lock changed")
	if not is_equal_approx(locked_opacity,float(island.sea_material.get_shader_parameter("scene_opacity"))):failures.append("F5 sea context followed actor")
	if not is_equal_approx(locked_forest,float(island.forest_paintings[0].get_shader_parameter("opacity"))):failures.append("F5 forest context followed actor")
	island._unhandled_key_input(event)
	var f=FileAccess.open(OUT+"motion-check.json",FileAccess.WRITE)
	f.store_string(JSON.stringify({"engine_fps":24,"capture_fps":12,"engine_frames":912,"duration_seconds":38,"max_camera_step":max_camera_step,"max_height_step":max_height_step,"failures":failures,"samples":report},"  "))
	print("FOREST_LAYER_MOTION_DONE");quit(0 if failures.is_empty() else 1)
