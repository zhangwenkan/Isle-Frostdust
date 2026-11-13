extends SceneTree

const OUT := "res://artifacts/overhead-opening-review/"
var island: Node3D

func _initialize() -> void:
	call_deferred("run")

func run() -> void:
	root.content_scale_size = Vector2i(1280,720)
	root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	root.size = Vector2i(1280,720)
	island = load("res://scenes/island.tscn").instantiate()
	root.add_child(island)
	current_scene = island
	island.opening.set_process(false)
	island.set_process(false)
	island.hero.pause()
	for t in [0.0,1.8,3.6,5.4,7.2]:
		island.opening.intro_elapsed = t
		island.opening._update_title()
		island._update_camera(0,true)
		island._update_ground_contact()
		for i in 12: await process_frame
		await RenderingServer.frame_post_draw
		assert(root.get_texture().get_image().save_png(OUT+"preview-%03d.png"%int(t*10)) == OK)
		print("INTRO_SAMPLE ",t," position ",island.camera.position," pitch ",island.camera.rotation_degrees.x)
	island.opening._begin_rising()
	island.hero.pause()
	for frame in [0,38,65,102]:
		island.hero.frame = frame
		island._update_camera(0,true)
		island._update_ground_contact()
		for i in 12: await process_frame
		await RenderingServer.frame_post_draw
		assert(root.get_texture().get_image().save_png(OUT+"rise-%03d.png"%frame) == OK)
	quit(0)
