extends "res://tools/capture_cloud_water.gd"
## Identical still cameras/frames before and after. No video recording.

const OUT := "res://artifacts/hero-volume-review/"
var report: Array = []

func run_capture() -> void:
	root.size = Vector2i(1280,720)
	island = load("res://scenes/island.tscn").instantiate()
	root.add_child(island)
	current_scene = island
	island.set_process(false)
	island.hero.pause()
	island.hud.hide()
	control_time(island)
	freeze_material(island.atmosphere.mountain_cloud_material,"fog")
	freeze_material(island.background_comparison.original_sky,"sky")
	freeze_material(island.background_comparison.comparison_sky,"sky")
	set_time(1.0)
	if phase=="diagnose":
		island.hero.animation=&"walk_right"
		island.hero.frame=7
		position(-15.2)
		await shot("shadow")
		island.hero.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		await shot("contact-only")
		island.hero.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_ON
		island.atmosphere.sun.shadow_normal_bias=.1
		await shot("bias")
		island.hero.flip_h=true
		island.hero.frame=23
		island.hero_path_offset=-.5
		island.hero_x=-13.0
		island._position_hero()
		island._update_camera(0,true)
		await shot("steep")
		var diag:=FileAccess.open(OUT+phase+"-views.json",FileAccess.WRITE)
		diag.store_string(JSON.stringify(report,"  "))
		quit(0)
		return
	for p in [{"x":-15.2,"label":"cape"},{"x":-6.8,"label":"slope"},{"x":7.8,"label":"bridge"},{"x":20.0,"label":"east"}]:
		island.hero.animation = &"idle_right"
		island.hero.flip_h = false
		position(p.x)
		await shot(p.label+"-idle")
		island.hero.animation = &"walk_right"
		island.hero.frame = 7
		island.hero.pause()
		await shot(p.label+"-stride")
		if p.label == "cape":
			island.hero.animation = &"walk_down"
			island.hero.frame = 5
			await shot("cape-front")
		if p.label=="slope":
			island.hero.flip_h=true
			await shot("slope-left")
			island.hero.flip_h=false
			island.hero.animation=&"walk_up"
			island.hero.frame=12
			await shot("slope-back")
	island.background_comparison.set_mode(1)
	island.hero.animation = &"idle_right"
	position(7.8)
	await shot("sunset-bridge")
	if phase != "before":
		island.background_comparison.set_mode(0)
		position(-15.2)
		var frames: SpriteFrames = island.hero.sprite_frames
		island.hero.sprite_frames = island.opening.REST_FRAMES
		island.hero.animation = &"rest_rise_right"
		for f in [0,50,90,102]:
			island.hero.frame=f
			await shot("rest-%03d"%f)
		island.hero.sprite_frames=frames
		island.hero.animation=&"idle_right"
		island.opening.dialogue.characters_per_second=0.0
		island.opening.dialogue.start_dialogue()
		await shot("dialogue")
		island.opening.dialogue.cancel_dialogue()
		island.hero.animation=&"walk_right"
		island.hero.frame=23
		island.hero.flip_h=true
		island.hero_x=-13.0
		island.hero_path_offset=-.5
		island._position_hero()
		island._update_camera(0,true)
		await shot("steep-slope")
	var file:=FileAccess.open(OUT+phase+"-views.json",FileAccess.WRITE)
	file.store_string(JSON.stringify(report,"  "))
	quit(0)

func shot(label: String) -> void:
	if island.get("hero_presentation") != null:
		island.hero_presentation.update(0.0,true)
	island._update_ground_contact()
	await settle(18)
	await RenderingServer.frame_post_draw
	assert(root.get_texture().get_image().save_png(OUT+phase+"-"+label+".png")==OK)
	var entry: Dictionary={"label":label,"hero":str(island.hero.position),"camera":str(island.camera.transform),"frame":island.hero.frame,"animation":str(island.hero.animation)}
	if island.get("hero_presentation") != null:
		entry["presentation"]=island.hero_presentation.debug_state()
	report.append(entry)
	print("HERO_VOLUME_SHOT ",phase," ",label)
