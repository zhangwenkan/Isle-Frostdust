extends SceneTree
## Rendered material/pose integration checks only; no video recording.
const OUT := "res://artifacts/hero-standing-light-review/"
var failures: Array[String]=[]
var checks:=0
var island: Node3D

func _initialize() -> void:call_deferred("run")
func check(ok:bool,label:String) -> void:
	checks+=1
	if not ok:
		failures.append(label)
		push_error(label)

func run() -> void:
	root.size=Vector2i(1280,720)
	island=load("res://scenes/island.tscn").instantiate()
	island.skip_opening=true
	root.add_child(island)
	current_scene=island
	island.set_process(false)
	island.hud.hide()
	island.hero_x=-6.8
	island._position_hero()
	island._update_camera(0,true)
	var presenter: RefCounted=island.hero_presentation
	var material: ShaderMaterial=presenter.material
	var standing_root:=Vector3.ZERO
	for direction in ["down","right","up"]:
		island.hero.animation=StringName("idle_"+direction)
		island.hero.pause()
		presenter.update(0,true)
		island._update_ground_contact()
		await process_frame
		await RenderingServer.frame_post_draw
		check(material.get_shader_parameter("has_volume"),direction+" has normals")
		check(material.get_shader_parameter("has_surface"),direction+" has standing surface")
		var normal: Texture2D=material.get_shader_parameter("volume_atlas")
		check(normal.resource_path.ends_with("standing_surface/"+direction+"_idle_normal.png"),direction+" correct region map")
		var point: Vector3=island.hero.position+Vector3.UP*presenter.lift
		if direction=="down":standing_root=point
		else:check(point.distance_to(standing_root)<.0001,direction+" root unchanged on direction switch")
		check(absf(presenter.roll)<.00001,direction+" remains upright")
	for direction in ["right","up","down"]:
		island.hero.animation=StringName("walk_"+direction)
		for frame in island.hero.sprite_frames.get_frame_count(island.hero.animation):
			island.hero.frame=frame
			presenter.update(0,true)
			check(not material.get_shader_parameter("has_surface"),"walking does not sample a standing ink mask")
			var normal: Texture2D=material.get_shader_parameter("volume_atlas")
			check(normal.resource_path.contains("volume_support/"),"walking retains existing matching frame map")
		await process_frame
		await RenderingServer.frame_post_draw
	island.hero.animation=&"idle_right"
	island.hero.flip_h=true
	presenter.update(0,true)
	check(material.get_shader_parameter("mirror_sign")==-1.0,"mirrored normal sign")
	var frames: SpriteFrames=island.hero.sprite_frames
	island.hero.sprite_frames=island.opening.REST_FRAMES
	island.hero.animation=&"rest_rise_right"
	island.hero.frame=102
	presenter.update(0,true)
	check(not material.get_shader_parameter("has_volume"),"opening retains unsupported-pose lighting branch")
	check(not material.get_shader_parameter("has_surface"),"opening has no standing mask")
	check(presenter.lift==0.0,"opening keeps original displacement")
	await process_frame
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png(OUT+"final-opening-last-frame.png")
	island.hero.sprite_frames=frames
	island.hero.animation=&"idle_down"
	island.hero.flip_h=false
	presenter.update(0,true)
	check(material.get_shader_parameter("has_surface"),"standing map restored after opening")
	var file:=FileAccess.open(OUT+"runtime-verification.json",FileAccess.WRITE)
	file.store_string(JSON.stringify({"passed":failures.is_empty(),"checks":checks,"failures":failures,"standing_directions":3,"existing_walk_frames_checked":79,"opening_last_frame":102,"video_recorded":false},"  "))
	print("STANDING_CHECKS ",checks," PASS=",failures.is_empty())
	quit(0 if failures.is_empty() else 1)
