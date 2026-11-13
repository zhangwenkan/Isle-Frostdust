extends SceneTree
## Real imported materials, camera movement, and lens behavior at 1440p.
var island: Node3D
const OUTPUT := "res://artifacts/surface-review/"
const TARGETS := ["rock", "rock_light", "wet_rock", "grass", "moss", "bark", "wood"]

func _initialize() -> void:
	call_deferred("run_review")

func settle(frames: int) -> void:
	for i in frames:
		await process_frame

func capture(label: String) -> void:
	await RenderingServer.frame_post_draw
	assert(root.get_texture().get_image().save_png(OUTPUT+label+".png") == OK)

func run_review() -> void:
	island = load("res://scenes/island.tscn").instantiate()
	root.add_child(island)
	current_scene = island
	island.hud.visible = false
	await settle(40)
	var checked: Dictionary = {}
	for imported in island.material_cache:
		if imported.resource_name not in TARGETS:
			continue
		var applied: StandardMaterial3D = island.material_cache[imported]
		assert(applied.albedo_texture != null)
		assert(applied.texture_filter == BaseMaterial3D.TEXTURE_FILTER_NEAREST_WITH_MIPMAPS)
		var picture: Image = applied.albedo_texture.get_image()
		assert(picture.has_mipmaps(), "Missing mipmaps: "+imported.resource_name)
		checked[imported.resource_name] = str(picture.get_size())
	assert(checked.size() == TARGETS.size(), "Surface material was lost in GLB import")
	print("MATERIALS_PASS ",JSON.stringify(checked))
	var event := InputEventKey.new()
	event.pressed = true
	event.keycode = KEY_F
	island._unhandled_key_input(event)
	assert(not island.camera_effects.dof_blur_far_enabled)
	await settle(10)
	await capture("after-no-lens")
	island._unhandled_key_input(event)
	assert(island.camera_effects.dof_blur_far_enabled)
	var start_x: float = island.hero_x
	Input.action_press("move_right")
	for frame in 90:
		await process_frame
		if frame%15 == 0:
			await capture("motion-%03d"%frame)
	Input.action_release("move_right")
	assert(island.hero_x > start_x+0.3)
	assert(island.camera.position.x > -5.6)
	print("MOTION_PASS hero_x=",island.hero_x," camera_x=",island.camera.position.x)
	print("PASS: 7 imported surface materials, mipmaps, real movement, camera follow, lens toggle.")
	quit(0)
