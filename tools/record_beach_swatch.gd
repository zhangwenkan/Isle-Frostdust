extends SceneTree
const OUT="res://artifacts/beach-swash-review/"
var island:Node3D
var tick=0
var samples=[]
func _initialize():call_deferred("start")
func start():
	root.size=Vector2i(1280,720);root.content_scale_size=Vector2i(1280,720)
	island=load("res://scenes/layered_island.tscn").instantiate();root.add_child(island);current_scene=island
	island.manual_control=false;island.hud.hide()
	process_frame.connect(step)
func step():
	if not island:return
	tick+=1
	# First two tides use a stationary camera. Then walk to the lower stairs,
	# stop and return, keeping the same active near-shore water.
	if tick<=384:island.advance_input(Vector2.ZERO,1./24.)
	elif tick<=432:
		var dir=(island.camera.unproject_position(island.anchors.stair_bottom)-island.camera.unproject_position(island.anchors.beach)).normalized()
		island.advance_input(dir,1./24.)
	elif tick<=480:island.advance_input(Vector2.ZERO,1./24.)
	elif tick<=544:
		var dir=(island.camera.unproject_position(island.anchors.beach)-island.camera.unproject_position(island.anchors.stair_bottom)).normalized()
		island.advance_input(dir,1./24.)
	else:island.advance_input(Vector2.ZERO,1./24.)
	if tick%24==0:samples.append({"frame":tick,"actor":island.hero.position,"camera":island.camera.position,"anchor":island.current_anchor})
	if tick>=624:
		var f=FileAccess.open(OUT+"motion-frame-log.json",FileAccess.WRITE);f.store_string(JSON.stringify({"fps":24,"logic_frames":tick,"samples":samples},"  "))
		print("BEACH_MOTION_DONE "+str(tick));quit()
