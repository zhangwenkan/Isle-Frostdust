extends SceneTree
const OUT := "res://artifacts/shallow-cape-review/"
var island:Node3D
func _initialize()->void:call_deferred("run")
func run()->void:
	root.size=Vector2i(1280,720)
	island=load("res://scenes/island.tscn").instantiate();root.add_child(island);current_scene=island
	island.set_process(false);island.opening.set_process(false);island.hud.hide();island.hero.pause()
	assert(not island.opening.is_input_locked())
	var samples:=0
	var max_step:=0.0
	var last_y:float=island.hero.position.y
	for direction in [Vector2.RIGHT,Vector2.ZERO,Vector2.LEFT]:
		for i in (175 if direction!=Vector2.ZERO else 20):
			island._move_hero(direction,1.0/60.0);island._update_camera(1.0/60.0);island._update_ground_contact()
			island.hero.pause()
			var p:Vector3=island.hero.position
			var hit:Dictionary=island.hero_presentation.surface.sample(p.x,p.z)
			assert(not hit.is_empty())
			assert(absf(p.y-float(hit.height)-.04)<.002)
			max_step=maxf(max_step,absf(p.y-last_y));last_y=p.y;samples+=1
	assert(absf(island.hero_x-island.HERO_START_X)<.01)
	assert(max_step<.06)
	island.opening.enabled=true;island.skip_opening=false;island.opening.start()
	for frame in [0,30,55,80,102]:
		island.opening._begin_rising();island.hero.pause();island.hero.frame=frame;island._update_camera(0,true)
		await process_frame;await RenderingServer.frame_post_draw
		root.get_texture().get_image().save_png(OUT+"verified-rise-%03d.png"%frame)
		assert(island.opening.is_input_locked())
	island.opening._on_animation_finished()
	for i in 100:island.opening._process(1.0/60.0);island._update_camera(1.0/60.0)
	assert(island.opening.phase==island.opening.Phase.DIALOGUE)
	await process_frame;await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png(OUT+"verified-dialogue.png")
	island.opening.dialogue.cancel_dialogue();island.opening._finish()
	for i in 120:island.opening._process(1.0/60.0);island._update_camera(1.0/60.0)
	assert(not island.opening.is_input_locked())
	island.opening.start();island._update_camera(0,true)
	assert(island.camera.global_basis.z.dot(Vector3.UP)>.999999)
	assert(island.hero.frame==0 and not island.hero.is_playing())
	FileAccess.open(OUT+"walk-opening-verification.json",FileAccess.WRITE).store_string(JSON.stringify({"steps":samples,"ground_support":true,"returned_to_start":true,"max_height_step_m":max_step,"opening_sampled_frames":[0,30,55,80,102],"dialogue_and_unlock":true,"overhead_replay":true,"continuous_video_recorded":false},"  "))
	print("SHALLOW_CAPE_WALK_OPENING_VERIFIED")
	quit(0)
