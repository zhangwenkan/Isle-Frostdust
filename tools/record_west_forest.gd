extends SceneTree
const OUT="res://artifacts/bamboo-west-extension-review/"
var island:Node3D
var route=["stair_bottom","stair_top","junction","forest_turn","forest_step1","forest_mid","forest_step2","forest_landing","forest_end","forest_west_entry","forest_west_gate","forest_west_light","forest_west_mid","forest_west_shade","forest_west_end","forest_west_shade","forest_west_mid","forest_west_light","forest_west_gate","forest_west_entry","forest_end","forest_landing","forest_step2","forest_mid","forest_step1","forest_turn","junction","stair_top","stair_bottom","beach"]
var tick=0
var route_index=0
var pause_ticks=48
var positions=[]
func _initialize():call_deferred("start")
func start():
	root.size=Vector2i(1280,720);root.content_scale_size=Vector2i(1280,720)
	island=load("res://scenes/layered_island.tscn").instantiate();root.add_child(island);current_scene=island;island.manual_control=false;island.hud.hide()
	process_frame.connect(step)
func step():
	if not island:return
	tick+=1
	if pause_ticks>0:
		pause_ticks-=1;island.advance_input(Vector2.ZERO,1./24.)
	elif route_index<route.size():
		var target:String=route[route_index]
		if island.current_anchor==target and island.destination.is_empty():
			route_index+=1
			if target in ["junction","forest_west_entry","forest_west_light","forest_west_end","beach"]:pause_ticks=60
		else:
			var dir=(island.camera.unproject_position(island.anchors[target])-island.camera.unproject_position(island.anchors[island.current_anchor])).normalized()
			island.advance_input(dir,1./24.)
	else:
		var f=FileAccess.open(OUT+"motion-frame-log.json",FileAccess.WRITE);f.store_string(JSON.stringify({"fps":24,"frame_count":tick,"samples":positions},"  "));print("FOREST_MOTION_DONE frames="+str(tick));quit()
	if tick%24==0:positions.append({"frame":tick,"actor":island.hero.position,"camera":island.camera.position,"anchor":island.current_anchor,"destination":island.destination})
	if tick>3000:push_error("Motion route timeout");quit(1)
