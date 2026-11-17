extends SceneTree
## Exercise the playable route graph and save only selected visual checkpoints.
const OUT="res://artifacts/layered-island-build/"
const STEP=1.0/24.0
var island:Node3D
var failures:Array[String]=[]
var checkpoints:Array[Dictionary]=[]
var ticks=0
var misses=0
var max_step=0.0
var idle_arrivals=0
var captured:Dictionary={}

func _initialize()->void:call_deferred("run")

func check(ok:bool,message:String)->void:
	if not ok:failures.append(message)

func run()->void:
	root.size=Vector2i(1280,720);root.content_scale_size=Vector2i(1280,720)
	island=load("res://scenes/layered_island.tscn").instantiate();root.add_child(island);current_scene=island
	island.manual_control=false;island.camera_locked=false;island.hud.hide()
	for i in 20:await process_frame
	await shot("beach")
	await walk(["stair_bottom","stair_top","junction","bridge_left"])
	# Reverse before reaching the other bank, then continue forward again.
	var dir=direction("bridge_left","bridge_right")
	for i in 40:
		island.advance_input(dir,STEP);await process_frame
	var before=island.hero.position
	island.advance_input(-dir,STEP)
	check(island.destination=="bridge_left","Bridge mid-edge reversal failed")
	check(island.hero.position.distance_to(before)<0.16,"Bridge reversal teleported actor")
	island.advance_input(dir,STEP)
	check(island.destination=="bridge_right","Bridge forward resume failed")
	await finish_edge("bridge_right")
	await shot("bridge_exit")
	await walk(["cave_mouth","cave_end"])
	await shot("cave_end")
	var stopped:Vector3=island.hero.position
	for i in 48:
		island.advance_input(Vector2.ZERO,STEP);await process_frame
	check(island.hero.position.distance_to(stopped)<0.001,"Idle actor drifted")
	await walk(["cave_mouth","bridge_right","bridge_left","junction","forest_turn","forest_step1","forest_mid","forest_step2","forest_landing","forest_end"])
	await shot("forest_end")
	await walk(["forest_landing","forest_step2","forest_mid","forest_step1","forest_turn","junction","stair_top","stair_bottom","beach"])
	await shot("return_beach")
	# Real input mappings, branch choice, and user-facing shortcuts.
	Input.action_press("move_up");check(island._input_vector().y<-.9,"W/up action mapping failed");Input.action_release("move_up")
	island.current_anchor="junction";island.destination="";island.edge_t=0.0;island.hero.position=island.anchors.junction
	island.advance_input(Vector2.RIGHT,STEP);check(island.destination=="bridge_left","Right at fork did not select bridge")
	island.current_anchor="junction";island.destination="";island.edge_t=0.0;island.hero.position=island.anchors.junction
	island.advance_input(Vector2.UP,STEP);check(island.destination=="forest_turn","Up at fork did not select forest")
	for key in [KEY_TAB,KEY_F5,KEY_R]:
		var event=InputEventKey.new();event.physical_keycode=key;event.pressed=true;island._unhandled_key_input(event)
	check(island.hud.visible,"Tab did not show HUD")
	check(island.camera_locked,"F5 did not lock local camera")
	check(island.current_anchor=="beach" and island.destination.is_empty(),"R did not reset to beach")
	island.hud.hide()
	# Compare the same camera and idle pose several seconds apart for environment motion.
	island.camera.position=island.base_camera;island.camera.look_at(island.base_target);island.camera.fov=32.0
	for i in 48:await process_frame
	await shot("idle_a")
	for i in 144:await process_frame
	await shot("idle_b")
	var report={"ticks":ticks,"route_misses":misses,"max_tick_height_change":max_step,"idle_animation_on_arrival":idle_arrivals,"failures":failures,"checkpoints":checkpoints,"recorded_video":false}
	check(idle_arrivals==0,"Walking animation interrupted at route node")
	var file=FileAccess.open(OUT+"playable-check.json",FileAccess.WRITE);file.store_string(JSON.stringify(report,"  "))
	print("PLAYABLE_CHECK "+JSON.stringify({"ticks":ticks,"misses":misses,"failures":failures,"idle_arrivals":idle_arrivals}))
	quit(0 if failures.is_empty() and misses==0 else 1)

func direction(a:String,b:String)->Vector2:
	return (island.camera.unproject_position(island.anchors[b])-island.camera.unproject_position(island.anchors[a])).normalized()

func walk(route:Array)->void:
	for target:String in route:await finish_edge(target)

func finish_edge(target:String)->void:
	var count=0
	while island.current_anchor!=target or not island.destination.is_empty():
		if count>1200:
			failures.append("Timed out reaching "+target);return
		var start:Vector3=island.hero.position
		var input=direction(island.current_anchor,target)
		island.advance_input(input,STEP)
		var label=""
		if target=="stair_top":label="stairs"
		elif target=="bridge_right":label="bridge"
		elif target=="forest_mid":label="forest_mid"
		if not label.is_empty() and not captured.has(label) and island.edge_t>.45 and island.edge_t<.6:
			captured[label]=true;await shot(label,false)
		if island.last_ground.is_empty():misses+=1
		max_step=maxf(max_step,absf(island.hero.position.y-start.y))
		if island.hero.position.distance_to(start)>.001 and str(island.hero.animation).begins_with("idle_"):idle_arrivals+=1
		var screen:Vector2=island.camera.unproject_position(island.hero.position+Vector3(0,.8,0))
		if screen.x<0 or screen.x>1280 or screen.y<0 or screen.y>720:
			if not "Actor left camera frame" in failures:failures.append("Actor left camera frame")
		ticks+=1;count+=1
		await process_frame

func shot(label:String,stop=true)->void:
	if stop:island.advance_input(Vector2.ZERO,STEP)
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_jpg(OUT+"review-"+label+".jpg",.86)
	var p:Vector2=island.camera.unproject_position(island.hero.position)
	checkpoints.append({"label":label,"foot_screen":[p.x,p.y],"actor_position":[island.hero.position.x,island.hero.position.y,island.hero.position.z],"animation":str(island.hero.animation)})
