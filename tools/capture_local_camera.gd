extends SceneTree
const OUT="res://artifacts/local-camera-review/"
const STEP=1.0/24.0
var island:Node3D
var failures:Array[String]=[]
var shots:Array[Dictionary]=[]
var ticks=0
var maximum_camera_step=0.0
var minimum_actor_screen_margin=10000.0
func _initialize():call_deferred("run")
func run():
	root.size=Vector2i(1280,720);root.content_scale_size=Vector2i(1280,720)
	island=load("res://scenes/layered_island.tscn").instantiate();root.add_child(island);current_scene=island
	island.manual_control=false;island.hud.hide()
	for i in 12:await process_frame
	await shot("beach")
	for row in [["stair_bottom","stair_top",.5,"stairs"],["bridge_left","bridge_right",.5,"bridge"],["bridge_right","cave_mouth",.65,"cave_approach"],["cave_mouth","cave_end",1.,"cave_end"],["forest_step1","forest_mid",.7,"forest_mid"],["forest_landing","forest_end",1.,"forest_end"]]:
		island.set_route_sample(row[0],row[1],row[2]);island.facing="right" if row[3] in ["bridge","cave_approach"] else "up"
		island._update_actor(false,0.,true)
		for i in 3:await process_frame
		await shot(row[3])
	island.reset_actor()
	await walk(["stair_bottom","stair_top","junction","bridge_left","bridge_right","cave_mouth","cave_end","cave_mouth","bridge_right","bridge_left","junction","forest_turn","forest_step1","forest_mid","forest_step2","forest_landing","forest_end","forest_landing","forest_step2","forest_mid","forest_step1","forest_turn","junction","stair_top","stair_bottom","beach"])
	var size_before:float=island.camera.size
	var event=InputEventKey.new();event.physical_keycode=KEY_F5;event.pressed=true;island._unhandled_key_input(event)
	if not island.camera_locked or absf(island.camera.size-size_before)>.00001:failures.append("F5 changed local view size")
	island._unhandled_key_input(event)
	var before_stop:Vector3=island.hero.position
	for i in 48:island.advance_input(Vector2.ZERO,STEP);await process_frame
	if island.hero.position.distance_to(before_stop)>.001:failures.append("Idle drift")
	var report={"shots":shots,"movement_ticks":ticks,"max_camera_center_step_in_reference_pixels":maximum_camera_step,"minimum_actor_screen_margin":minimum_actor_screen_margin,"failures":failures,"video_recorded":false}
	var f=FileAccess.open(OUT+"local-camera-check.json",FileAccess.WRITE);f.store_string(JSON.stringify(report,"  "))
	print("LOCAL_CAMERA_CHECK "+JSON.stringify({"ticks":ticks,"max_camera_step":maximum_camera_step,"actor_margin":minimum_actor_screen_margin,"failures":failures}));quit(0 if failures.is_empty() else 1)
func walk(route:Array):
	for target:String in route:
		var guard=0
		while island.current_anchor!=target or not island.destination.is_empty():
			guard+=1
			if guard>900:failures.append("Could not reach "+target);return
			var direction=(island.camera.unproject_position(island.anchors[target])-island.camera.unproject_position(island.anchors[island.current_anchor])).normalized()
			island.advance_input(direction,STEP)
			if island.last_ground.is_empty() and not "Missing support" in failures:failures.append("Missing support")
			var before:Vector2=island.camera_focus
			await process_frame
			maximum_camera_step=maxf(maximum_camera_step,island.camera_focus.distance_to(before))
			var actor:Vector2=island.camera.unproject_position(island.hero.position+Vector3(0,.85,0))
			var margin=minf(minf(actor.x,1280.-actor.x),minf(actor.y,720.-actor.y))
			minimum_actor_screen_margin=minf(minimum_actor_screen_margin,margin)
			if margin<32. and not "Actor left safe frame" in failures:failures.append("Actor left safe frame")
			ticks+=1
func shot(label:String):
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_jpg(OUT+"local-"+label+".jpg",.86)
	var foot:Vector2=island.camera.unproject_position(island.hero.position)
	var head:Vector2=island.camera.unproject_position(island.hero.position+Vector3(0,1.9,0))
	shots.append({"label":label,"foot":[foot.x,foot.y],"projected_1_9m_height":foot.distance_to(head),"focus":[island.camera_focus.x,island.camera_focus.y],"reference_view_height":1536./island.local_zoom,"camera_position":[island.camera.position.x,island.camera.position.y,island.camera.position.z]})
