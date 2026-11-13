extends "res://tools/capture_coastal_water.gd"

const REVIEW := "res://artifacts/cloud-water-review/"

func freeze_material(material: ShaderMaterial, shader_type: String) -> void:
	var shader := material.shader.duplicate() as Shader
	var expression := RegEx.new()
	expression.compile("\\bTIME\\b")
	shader.code = expression.sub(shader.code, "review_time", true)
	shader.code = shader.code.replace("shader_type " + shader_type + ";", "shader_type " + shader_type + ";\nuniform float review_time = 1.0;")
	material.shader = shader
	controlled_materials.append(material)

func save_view(label: String) -> void:
	await settle(24)
	await RenderingServer.frame_post_draw
	assert(root.get_texture().get_image().save_png(REVIEW + phase + "-" + label + ".png") == OK)
	print("CLOUD_CAPTURE ", label)

func record_cloud_motion() -> void:
	position(7.8)
	var folder := REVIEW + "motion-frames"
	DirAccess.make_dir_recursive_absolute(folder)
	for frame in 540:
		set_time(frame / 30.0)
		await settle(2)
		await RenderingServer.frame_post_draw
		assert(root.get_texture().get_image().save_jpg(folder + "/%04d.jpg" % frame, 0.92) == OK)
		if frame % 120 == 0:
			print("CLOUD_MOTION ", frame)
	var output := FileAccess.open(REVIEW + "motion-verification.json", FileAccess.WRITE)
	output.store_string(JSON.stringify({"frames":540,"fps":30,"duration_seconds":18,"size":str(root.size),"camera":"Fixed gameplay bridge view","time_scale":1.0,"renderer":"Vulkan Forward+"}, "  "))
	print("CLOUD_MOTION_COMPLETE")

func run_capture() -> void:
	island = load("res://scenes/island.tscn").instantiate()
	root.add_child(island)
	current_scene = island
	island.set_process(false)
	island.hero.pause()
	island.hero.frame = 0
	island.hud.visible = false
	control_time(island)
	freeze_material(island.atmosphere.mountain_cloud_material, "fog")
	freeze_material(island.atmosphere.sky_cloud_material, "sky")
	set_time(1.0)
	await settle(40)
	if "--movie" in OS.get_cmdline_user_args():
		await record_cloud_motion()
		quit(0)
		return
	for point in [{"label":"midshot","x":-6.8},{"label":"bridge","x":7.8},{"label":"east","x":20.0}]:
		position(point.x)
		await save_view(point.label)
	position(7.8)
	set_time(19.0)
	await save_view("bridge-later")
	set_time(1.0)
	island.camera_effects.dof_blur_near_enabled = false
	island.camera_effects.dof_blur_far_enabled = false
	island.camera.position = Vector3(4.0,13.0,-35.0)
	island.camera.look_at(Vector3(4.0,8.0,-110.0))
	await save_view("horizon-detail")
	island.camera.position = Vector3(7.8,4.0,13.0)
	island.camera.look_at(Vector3(7.8,1.5,-50.0))
	await save_view("low-angle")
	position(7.8)
	island.camera_effects.dof_blur_near_enabled = true
	island.camera_effects.dof_blur_far_enabled = true
	island.atmosphere.apply(10.5,0.9)
	await save_view("overcast")
	island.atmosphere.apply(14.5,0.22)
	await save_view("afternoon")
	quit(0)
