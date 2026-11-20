extends SceneTree
## Uses the normal controller and imported support; generates no geometry.
const OUT="res://artifacts/forest-rocky-terminus-rework/"
func _initialize():call_deferred("run")
func shortest_path(island:Node3D,start:String,goal:String)->Array:
	var queue=[start];var previous={start:""}
	while not queue.is_empty():
		var a=queue.pop_front()
		if a==goal:break
		for b in island.neighbors[a]:
			if not previous.has(b):previous[b]=a;queue.append(b)
	assert(previous.has(goal))
	var path=[goal]
	while path[0]!=start:path.push_front(previous[path[0]])
	return path
func run()->void:
	root.size=Vector2i(1280,720);root.content_scale_size=Vector2i(1280,720)
	var frame_dir=OUT+"review-motion-frames/";DirAccess.make_dir_recursive_absolute(frame_dir)
	var island=load("res://scenes/layered_island.tscn").instantiate();root.add_child(island);current_scene=island
	island.manual_control=false;island.hud.hide();island.set_process(false);island.reset_actor("forest_west_mid")
	for warmup in 8:await process_frame
	var stages=[["forest_west_mid",72],["cape_center",144],["cape_shore_end",72],["forest_west_mid",72]]
	var stage=0;var wait_ticks=0;var tick=0;var frames=0;var failures=[];var samples=[];var seen={};var path=[]
	var key=InputEventKey.new();key.physical_keycode=KEY_F5;key.pressed=true
	var lock_transform:Transform3D;var lock_fov=0.0;var locked_hold=false
	var life=island.get_node("World").find_child("CapeFireLight",true,false) as OmniLight3D
	var light_min=INF;var light_max=0.0
	while stage<stages.size() and tick<1200:
		var target:String=stages[stage][0];var input=Vector2.ZERO
		if island.current_anchor==target and island.destination.is_empty():
			if stage==1 and wait_ticks==0:
				island._unhandled_key_input(key);lock_transform=island.camera.transform;lock_fov=island.camera.fov;locked_hold=true
			wait_ticks+=1
			if wait_ticks>=int(stages[stage][1]):
				if locked_hold:island._unhandled_key_input(key);locked_hold=false
				stage+=1;wait_ticks=0;path=[]
		else:
			if island.destination.is_empty():
				path=shortest_path(island,island.current_anchor,target)
				if path.size()>1:input=(island.camera.unproject_position(island.anchors[path[1]])-island.camera.unproject_position(island.anchors[path[0]])).normalized()
			else:input=(island.camera.unproject_position(island.anchors[island.destination])-island.camera.unproject_position(island.anchors[island.current_anchor])).normalized()
		island.advance_input(input,1.0/24.0);island._update_camera(1.0/24.0);island._update_occluders(1.0/24.0)
		await process_frame
		if island.last_ground.is_empty():failures.append({"tick":tick,"error":"missing imported floor"})
		elif absf(island.hero.position.y-float(island.last_ground.height)-.014)>.003:failures.append({"tick":tick,"error":"unsupported feet"})
		if locked_hold and (not island.camera.transform.is_equal_approx(lock_transform) or not is_equal_approx(island.camera.fov,lock_fov)):failures.append({"tick":tick,"error":"locked camera moved"})
		if island.hero.material_override!=island.hero_lighting.material:failures.append({"tick":tick,"error":"lost hero lighting"})
		if island.hero_lighting.material.get_shader_parameter("mirror_sign")!=(-1.0 if island.hero.flip_h else 1.0):failures.append({"tick":tick,"error":"mirrored normal mismatch"})
		if life:light_min=minf(light_min,life.light_energy);light_max=maxf(light_max,life.light_energy)
		seen[island.current_anchor]=true
		if tick%2==0:
			RenderingServer.force_draw(false)
			var im=root.get_texture().get_image();im.resize(960,540,Image.INTERPOLATE_LANCZOS)
			assert(im.save_jpg(frame_dir+"frame-%04d.jpg"%frames,.94)==OK);frames+=1
		if tick%48==0:
			print("ROCKY_TERMINUS_MOTION ",tick," stage=",stage," anchor=",island.current_anchor)
			samples.append({"tick":tick,"stage":stage,"anchor":island.current_anchor,"camera":str(island.camera.position),"fov":island.camera.fov,"actor":str(island.hero.position),"sea_opacity":island.sea_material.get_shader_parameter("scene_opacity"),"cape_palette":island.sea_material.get_shader_parameter("cape_palette"),"fire_energy":life.light_energy if life else -1})
		tick+=1
	if stage!=stages.size():failures.append({"error":"route did not complete","stage":stage})
	var reset_key=InputEventKey.new();reset_key.physical_keycode=KEY_R;reset_key.pressed=true;island._unhandled_key_input(reset_key)
	var reset_anchor=island.current_anchor
	var file=FileAccess.open(OUT+"review-motion-check.json",FileAccess.WRITE)
	file.store_string(JSON.stringify({"engine_fps":24,"capture_fps":12,"frames":frames,"duration_seconds":float(tick)/24.0,"stages":stages,"stages_completed":stage,"move_speed":island.MOVE_SPEED,"anchors_seen":seen.keys(),"reset_anchor":reset_anchor,"fire_energy_min":light_min,"fire_energy_max":light_max,"samples":samples,"failures":failures},"  "))
	print("ROCKY_TERMINUS_MOTION_DONE ",frames," frames, failures=",failures.size());quit(0 if failures.is_empty() else 1)
