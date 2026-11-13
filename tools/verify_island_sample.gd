extends SceneTree
## Visual and input smoke check; uses the actual imported scene, camera and movement.

var island: Node3D
const OUTPUT := "res://artifacts/hd2d-sample/"

func _initialize() -> void:
	call_deferred("run_review")

func settle(frames: int) -> void:
	for i in frames:
		await process_frame

func capture(name: String) -> void:
	await RenderingServer.frame_post_draw
	var result := root.get_texture().get_image().save_png(OUTPUT+name+".png")
	assert(result == OK, "Capture failed: "+name)
	print("CAPTURE ",name," hero=",island.hero.position," camera=",island.camera.position)

func place(x: float) -> void:
	island.hero_x = x
	island._position_hero()
	island._update_camera(0.0,true)
	await settle(30)

func toggle_lens() -> void:
	var event := InputEventKey.new()
	event.pressed = true
	event.keycode = KEY_F
	island._unhandled_key_input(event)

func run_review() -> void:
	island = load("res://scenes/island.tscn").instantiate()
	root.add_child(island)
	current_scene = island
	island.hud.visible = false
	await settle(80)
	assert(is_instance_valid(island.lens_surface),"Blender lens surface missing")
	await capture("sample-midshot")
	toggle_lens()
	await settle(5)
	assert(not island.camera_effects.dof_blur_far_enabled)
	await capture("sample-no-lens")
	toggle_lens()
	await place(2.0)
	await capture("sample-bridgehead")
	await place(8.0)
	await capture("sample-bridge")
	await place(-17.0)
	await capture("sample-cliff")
	await place(-6.8)
	var before: float = island.hero_x
	Input.action_press("move_right")
	for frame in 100:
		await process_frame
		if frame%20 == 0:
			await capture("motion-%03d"%frame)
	Input.action_release("move_right")
	assert(island.hero_x > before+1.0,"D input did not move the protagonist")
	assert(island.camera.position.x > -5.6,"Camera did not follow")
	await settle(15)
	await capture("sample-walking")
	print("PASS: imported scene, Vulkan rendering, lens toggle, five locations, movement and camera follow.")
	quit(0)
