extends SceneTree
const OUT="res://artifacts/left-finish-review/"
const STEP=1.0/24.0
var island:Node3D
var failures:Array[String]=[]
var ticks=0
var max_step=0.0
var idle_arrivals=0
var min_margin=10000.0
var max_camera_step=0.0
var first_camera:Vector3
var max_camera_distance=0.0
func _initialize():call_deferred("run")
func run():
	root.size=Vector2i(1280,720);root.content_scale_size=Vector2i(1280,720)
	island=load("res://scenes/layered_island.tscn").instantiate();root.add_child(island);current_scene=island
	island.manual_control=false;island.set_process(false);island.hud.hide()
	first_camera=island.camera.position
	walk(["stair_bottom","stair_top","junction","bridge_left"])
	for i in 24:tick(direction("bridge_left","bridge_right"))
	var previous:Vector3=island.hero.position
	tick(-direction("bridge_left","bridge_right"))
	if island.destination!="bridge_left" or island.hero.position.distance_to(previous)>.15:failures.append("Mid-bridge reversal")
	tick(direction("bridge_left","bridge_right"))
	walk(["bridge_right","cave_mouth","cave_end","cave_mouth","bridge_right","bridge_left","junction","forest_turn","forest_step1","forest_mid","forest_step2","forest_landing","forest_end","forest_landing","forest_step2","forest_mid","forest_step1","forest_turn","junction","stair_top","stair_bottom","beach"])
	var stopped:Vector3=island.hero.position
	for i in 48:tick(Vector2.ZERO)
	if island.hero.position.distance_to(stopped)>.001:failures.append("Idle drift")
	var event=InputEventKey.new();event.physical_keycode=KEY_F5;event.pressed=true;island._unhandled_key_input(event)
	var locked:Transform3D=island.camera.transform
	for i in 24:tick(direction("beach","stair_bottom"))
	if not island.camera.transform.is_equal_approx(locked):failures.append("F5 lock moved")
	island._unhandled_key_input(event)
	for i in 24:tick(Vector2.ZERO)
	if island.camera.transform.is_equal_approx(locked):failures.append("F5 resume failed")
	for key in [KEY_TAB,KEY_R]:event.physical_keycode=key;island._unhandled_key_input(event)
	if not island.hud.visible or island.current_anchor!="beach":failures.append("Tab or R failed")
	Input.action_press("move_up")
	if island._input_vector().y>-.9:failures.append("Up input mapping")
	Input.action_release("move_up")
	for row in [[Vector2.RIGHT,"bridge_left"],[Vector2.UP,"forest_turn"]]:
		island.set_route_sample("junction","bridge_left",0.);island.destination="";island.advance_input(row[0],STEP)
		if island.destination!=row[1]:failures.append("Fork input "+row[1])
	# Compare projected parallax for a 1 m physical camera translation.
	island.reset_actor()
	var near_point=island.anchors.beach+Vector3(-3,0,-2)
	var far_point=Vector3(-8,12,-90)
	var near_before=island.camera.unproject_position(near_point)
	var far_before=island.camera.unproject_position(far_point)
	island.camera.position.x+=1.0
	var parallax={"near_pixels":absf(island.camera.unproject_position(near_point).x-near_before.x),"far_pixels":absf(island.camera.unproject_position(far_point).x-far_before.x)}
	if parallax.near_pixels<=parallax.far_pixels*1.5:failures.append("Missing differential parallax")
	if idle_arrivals>0:failures.append("Arrival animation idle flashes")
	var report={"movement_ticks":ticks,"max_height_step":max_step,"idle_arrivals":idle_arrivals,"minimum_actor_frame_margin":min_margin,"max_camera_step_meters":max_camera_step,"camera_travel_from_start_meters":max_camera_distance,"parallax":parallax,"saved_world_transform":island.get_node("World").transform,"failures":failures}
	var file=FileAccess.open(OUT+"movement-check.json",FileAccess.WRITE);file.store_string(JSON.stringify(report,"  "))
	print("SPATIAL_MOVEMENT "+JSON.stringify(report));quit(0 if failures.is_empty() else 1)
func direction(a:String,b:String)->Vector2:return (island.camera.unproject_position(island.anchors[b])-island.camera.unproject_position(island.anchors[a])).normalized()
func walk(route:Array):
	for target:String in route:
		var guard=0
		while island.current_anchor!=target or not island.destination.is_empty():
			guard+=1
			if guard>900:failures.append("Route timeout "+target);return
			tick(direction(island.current_anchor,target))
func tick(input:Vector2):
	var before:Vector3=island.hero.position;var camera_before:Vector3=island.camera.position
	island.advance_input(input,STEP);island._update_camera(STEP);island._update_occluders(STEP)
	if island.last_ground.is_empty() and not "Missing support" in failures:failures.append("Missing support")
	if absf(island.hero.position.y-before.y)>.26:failures.append("Abrupt height jump at "+island.current_anchor+" to "+island.destination)
	max_step=maxf(max_step,absf(island.hero.position.y-before.y))
	if island.hero.position.distance_to(before)>.001 and island.destination.is_empty() and str(island.hero.animation).begins_with("idle"):idle_arrivals+=1
	var screen:Vector2=island.camera.unproject_position(island.hero.position+Vector3(0,.9,0))
	min_margin=minf(min_margin,minf(minf(screen.x,1280-screen.x),minf(screen.y,720-screen.y)))
	if min_margin<32 and not "Actor outside safe frame" in failures:failures.append("Actor outside safe frame")
	max_camera_step=maxf(max_camera_step,island.camera.position.distance_to(camera_before));max_camera_distance=maxf(max_camera_distance,island.camera.position.distance_to(first_camera));ticks+=1
