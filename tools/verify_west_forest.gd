extends SceneTree
const OUT="res://artifacts/bamboo-west-extension-review/"
const STEP=1.0/24.0
var island:Node3D
var failures:Array[String]=[]
var samples=[]
var ticks=0
var max_step=0.0
var max_camera_step=0.0
var min_margin=10000.0
var previous_heading=Vector2.ZERO
func _initialize():call_deferred("run")
func direction(a:String,b:String)->Vector2:return (island.camera.unproject_position(island.anchors[b])-island.camera.unproject_position(island.anchors[a])).normalized()
func run():
	root.size=Vector2i(1280,720);root.content_scale_size=Vector2i(1280,720)
	island=load("res://scenes/layered_island.tscn").instantiate();root.add_child(island);current_scene=island
	island.manual_control=false;island.set_process(false);island.hud.hide()
	walk(["stair_bottom","stair_top","junction","forest_turn","forest_step1","forest_mid","forest_step2","forest_landing","forest_end","forest_west_entry","forest_west_gate","forest_west_light","forest_west_mid","forest_west_shade","forest_west_end"])
	var still:Vector3=island.hero.position
	for i in 48:tick(Vector2.ZERO)
	if island.hero.position.distance_to(still)>.001:failures.append("Idle drift")
	walk(["forest_west_shade","forest_west_mid","forest_west_light","forest_west_gate","forest_west_entry","forest_end","forest_landing","forest_step2","forest_mid","forest_step1","forest_turn","junction","bridge_left","bridge_right","cave_mouth","cave_end","cave_mouth","bridge_right","bridge_left","junction","stair_top","stair_bottom","beach"])
	# Horizontal left input must enter and continue through the new segment.
	island.set_route_sample("forest_end","forest_west_entry",0.);island.destination=""
	for i in 12:tick(Vector2.LEFT)
	if island.destination!="forest_west_entry":failures.append("Left input did not enter west extension")
	var before:Vector3=island.hero.position;tick(Vector2.RIGHT)
	if island.destination!="forest_end" or island.hero.position.distance_to(before)>.15:failures.append("West path reversal")
	var event=InputEventKey.new();event.physical_keycode=KEY_F5;event.pressed=true;island._unhandled_key_input(event)
	var locked:Transform3D=island.camera.transform
	for i in 24:tick(Vector2.LEFT)
	if not island.camera.transform.is_equal_approx(locked):failures.append("F5 lock moved")
	island._unhandled_key_input(event)
	event.physical_keycode=KEY_R;island._unhandled_key_input(event)
	if island.current_anchor!="beach":failures.append("Reset failed")
	var support=[]
	for edge:Array in island.layout.forest_extension.new_edges:
		for i in 101:
			island.set_route_sample(edge[0],edge[1],float(i)/100.)
			var h=Vector3(island.hero.position)
			for dx in [-.13,0.,.13]:
				var sample:Dictionary=island.surface.sample(h+Vector3(dx,0,0))
				if sample.is_empty():failures.append("Sole unsupported "+str(edge))
			if i%20==0:support.append({"edge":edge,"t":float(i)/100.,"actor":h,"surface":island.last_ground})
	var normal:Vector3=island.get_node("World").global_basis.y.normalized()
	var report={"movement_ticks":ticks,"max_height_step":max_step,"max_camera_step":max_camera_step,"minimum_frame_margin":min_margin,"ground_angle_degrees":rad_to_deg(asin(absf(island.camera.global_basis.z.dot(normal)))),"vertical_fov":island.camera.fov,"support_samples":support,"route_samples":samples,"failures":failures}
	var f=FileAccess.open(OUT+"movement-check.json",FileAccess.WRITE);f.store_string(JSON.stringify(report,"  "))
	print("FOREST_MOVEMENT "+JSON.stringify({"ticks":ticks,"max_height_step":max_step,"failures":failures}));quit(0 if failures.is_empty() else 1)
func walk(route:Array):
	for target:String in route:
		var guard=0
		while island.current_anchor!=target or not island.destination.is_empty():
			guard+=1
			if guard>1100:failures.append("Route timeout "+target);return
			tick(direction(island.current_anchor,target))
func tick(input:Vector2):
	var before:Vector3=island.hero.position;var camera_before:Vector3=island.camera.position
	island.advance_input(input,STEP);island._update_camera(STEP);island._update_occluders(STEP)
	if island.last_ground.is_empty() and not "Missing support" in failures:failures.append("Missing support")
	var dh=absf(island.hero.position.y-before.y)
	if dh>.28 and not ("Abrupt step "+island.current_anchor) in failures:failures.append("Abrupt step "+island.current_anchor)
	max_step=maxf(max_step,dh);max_camera_step=maxf(max_camera_step,island.camera.position.distance_to(camera_before))
	if island.hero.position.distance_to(before)>.001 and island.destination.is_empty() and str(island.hero.animation).begins_with("idle"):failures.append("Idle arrival flash")
	var pixel:Vector2=island.camera.unproject_position(island.hero.position+Vector3.UP*.9)
	min_margin=minf(min_margin,minf(minf(pixel.x,1280-pixel.x),minf(pixel.y,720-pixel.y)))
	if min_margin<32 and not "Actor outside safe frame" in failures:failures.append("Actor outside safe frame")
	ticks+=1
	if ticks%24==0:samples.append({"tick":ticks,"anchor":island.current_anchor,"destination":island.destination,"actor":island.hero.position,"camera":island.camera.position})
