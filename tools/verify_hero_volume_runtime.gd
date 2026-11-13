extends SceneTree
## Opening, dialogue, turns, bridge traversal and replay. Stills only.
const OUT := "res://artifacts/hero-volume-review/"
var island: Node3D
var errors: Array[String]=[]

func _initialize() -> void:call_deferred("run")
func check(ok: bool,label: String) -> void:
	if not ok:
		errors.append(label)
		push_error(label)
func run() -> void:
	root.size=Vector2i(1280,720)
	island=load("res://scenes/island.tscn").instantiate()
	root.add_child(island)
	current_scene=island
	check(island.opening.is_input_locked(),"Opening starts normally")
	var camera_start: Vector3=island.camera.position
	var life_start: float=island.coastal_life.elapsed
	await create_timer(4.8).timeout
	check(island.opening.phase==island.opening.Phase.DIALOGUE,"Real opening completes into dialogue")
	check(island.camera.position.distance_to(camera_start)<.005,"Opening camera remains stable")
	check(island.coastal_life.elapsed>life_start+4.0,"Environment remains alive during opening")
	var dialogue: CanvasLayer=island.opening.dialogue
	dialogue.advance()
	await process_frame
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png(OUT+"final-dialogue.png")
	for i in 5:dialogue.advance()
	check(not island.opening.is_input_locked(),"Dialogue releases control")
	island.set_process(false)
	var min_margin:=INF
	var frame_updates:=0
	var previous_frame: int=island.hero.frame
	# Exercise real movement without saving a video or frame sequence.
	for i in 330:
		island._move_hero(Vector2.RIGHT,1.0/30.0)
		island._update_camera(1.0/30.0)
		island._update_ground_contact()
		var actor: AnimatedSprite3D=island.hero
		if actor.frame!=previous_frame:frame_updates+=1
		previous_frame=actor.frame
		var head: Vector3=actor.position+actor.basis.y*2.45+Vector3.UP*island.hero_presentation.lift
		var screen: Vector2=island.camera.unproject_position(head)
		min_margin=minf(min_margin,minf(screen.x,minf(1280-screen.x,screen.y)))
		if i%3==0:await process_frame
	check(island.hero_x>23.6,"Crosses full bridge and reaches eastern endpoint")
	check(min_margin>12,"Character head remains in camera throughout traversal")
	check(frame_updates>10,"Walking frames keep advancing")
	for direction in [Vector2.LEFT,Vector2.UP,Vector2.DOWN,Vector2.ZERO]:
		island._move_hero(direction,.1)
		island._update_camera(.1)
		await process_frame
	check(not island.hero.is_playing(),"Stopping pauses only character movement")
	var event:=InputEventKey.new()
	event.keycode=KEY_R
	event.pressed=true
	island._unhandled_key_input(event)
	island._update_camera(0,true)
	check(island.hero.animation==&"rest_rise_right" and island.opening.is_input_locked(),"R replays original opening")
	check(island.hero_presentation.lift==0,"Replay clears walking correction")
	island.set_process(true)
	await create_timer(.15).timeout
	check(island.hero.frame>0,"Replayed action advances")
	var file:=FileAccess.open(OUT+"runtime-verification.json",FileAccess.WRITE)
	file.store_string(JSON.stringify({"passed":errors.is_empty(),"errors":errors,"opening_seconds":4.8,"traversal_steps":330,"min_head_screen_margin_px":min_margin,"walking_frame_changes":frame_updates,"replay":true,"video_recorded":false},"  "))
	print("HERO_RUNTIME_", "PASS" if errors.is_empty() else "FAIL")
	quit(0 if errors.is_empty() else 1)
