extends SceneTree
## Matching cameras and frozen animation make material comparisons reproducible.
var island: Node3D
var phase := "before"
var frozen_shaders: Dictionary = {}

func _initialize() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--phase="):
			phase = arg.trim_prefix("--phase=")
	call_deferred("run_capture")

func freeze_material(mat: Material) -> void:
	if not mat is ShaderMaterial:
		return
	var shader_material := mat as ShaderMaterial
	var source: Shader = shader_material.shader
	if source == null:
		return
	if not frozen_shaders.has(source):
		var frozen := source.duplicate() as Shader
		var expression := RegEx.new()
		expression.compile("\\bTIME\\b")
		frozen.code = expression.sub(source.code,"1.0",true)
		frozen_shaders[source] = frozen
		frozen_shaders[frozen] = frozen
	shader_material.shader = frozen_shaders[source]

func freeze_shaders(node: Node) -> void:
	if node is MeshInstance3D:
		freeze_material(node.material_override)
		for surface in node.mesh.get_surface_count():
			freeze_material(node.get_surface_override_material(surface))
	for child in node.get_children():
		freeze_shaders(child)

func settle(frames: int) -> void:
	for i in frames:
		await process_frame

func capture_view(label: String, x: float) -> void:
	island.hero_x = x
	island._position_hero()
	island._update_camera(0.0,true)
	await settle(30)
	await RenderingServer.frame_post_draw
	var picture := root.get_texture().get_image()
	var path := "res://artifacts/fish-style-review/"+phase+"-"+label+".png"
	assert(picture.save_png(path) == OK)
	print("SURFACE_CAPTURE ",phase," ",label," size=",picture.get_size()," camera=",island.camera.global_transform)

func run_capture() -> void:
	island = load("res://scenes/island.tscn").instantiate()
	root.add_child(island)
	current_scene = island
	island.set_process(false)
	island.hero.pause()
	island.hero.frame = 0
	island.hero.flip_h = false
	island.hud.visible = false
	freeze_shaders(island)
	await settle(50)
	await capture_view("midshot",-6.8)
	await capture_view("bridge",5.5)
	await capture_view("cliff",-17.0)
	await capture_view("east",20.0)
	quit(0)
