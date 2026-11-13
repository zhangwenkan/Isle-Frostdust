extends Node
## Two background studies over the restored coast. Only imported geometry is assembled here.

const LABELS := ["原版天空与群山", "米黄天空·夕阳红"]
var mode := 0
var island: Node3D
var original_mountains: Array[MeshInstance3D] = []
var ink_mountains: Node3D
var button: Button
var original_sky: ShaderMaterial
var comparison_sky: ShaderMaterial

func configure(owner_island: Node3D, ui: Control) -> void:
	island = owner_island
	_find_originals(island.get_node("World3D"))
	assert(original_mountains.size() == 14)
	ink_mountains = preload("res://assets/background_comparison/ink_mountains.glb").instantiate()
	ink_mountains.name = "ComparisonInkMountains"
	island.add_child(ink_mountains)
	_configure_ink(ink_mountains)
	original_sky = island.atmosphere.sky_cloud_material
	comparison_sky = original_sky.duplicate() as ShaderMaterial
	comparison_sky.shader = preload("res://shaders/comparison_sky.gdshader")
	for parameter in ["sky_top_color", "sky_horizon_color", "ground_bottom_color", "ground_horizon_color", "sky_curve", "ground_curve", "cloud_cover"]:
		comparison_sky.set_shader_parameter(parameter, original_sky.get_shader_parameter(parameter))
	button = Button.new()
	button.name = "BackgroundComparisonButton"
	button.focus_mode = Control.FOCUS_NONE
	button.custom_minimum_size = Vector2(360,46)
	button.add_theme_font_override("font",island.status_label.get_theme_font("font"))
	button.add_theme_font_size_override("font_size",18)
	button.add_theme_color_override("font_color",Color("f5efe1"))
	for state in ["normal","hover","pressed"]:
		var style := StyleBoxFlat.new()
		style.bg_color = Color("243e43") if state == "normal" else Color("3c5659")
		style.bg_color.a = .94
		style.set_corner_radius_all(5)
		style.set_border_width_all(1)
		style.border_color = Color("89968f")
		button.add_theme_stylebox_override(state,style)
	ui.add_child(button)
	button.set_anchors_and_offsets_preset(Control.PRESET_TOP_RIGHT)
	button.offset_left = -396
	button.offset_right = -36
	button.offset_top = 94
	button.offset_bottom = 140
	button.tooltip_text = "点击或按 F6 切换背景\n1 原版天空与群山\n2 米黄天空·夕阳红"
	button.pressed.connect(cycle)
	set_mode(0)

func _find_originals(node: Node) -> void:
	if node is MeshInstance3D and str(node.name).begins_with("Mist_Ridge_"):
		original_mountains.append(node)
	for child in node.get_children():
		_find_originals(child)

func _configure_ink(node: Node) -> void:
	if node is MeshInstance3D:
		var mesh := node as MeshInstance3D
		mesh.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		for index in mesh.mesh.get_surface_count():
			var source := mesh.mesh.surface_get_material(index) as StandardMaterial3D
			var material := ShaderMaterial.new()
			material.shader = preload("res://shaders/comparison_ink_hills.gdshader")
			material.set_shader_parameter("painting",source.albedo_texture)
			# Paint far rows first. Keep the sea's refraction/depth buffer untouched.
			var center := mesh.global_transform * mesh.get_aabb().get_center()
			material.render_priority = 10 + clampi(int((250.0+center.z)/10.0),0,20)
			mesh.set_surface_override_material(index,material)
	for child in node.get_children():
		_configure_ink(child)

func cycle() -> void:
	set_mode((mode + 1) % LABELS.size())

func set_mode(index: int) -> void:
	mode = posmod(index,LABELS.size())
	var painted := mode == 1
	for mountain in original_mountains:
		mountain.visible = not painted
	ink_mountains.visible = painted
	var atmosphere = island.atmosphere
	var cloud_color: Color = Color("d5dfe0").lerp(Color("c7d1d5"),atmosphere.clouds)
	var sea_mist_color: Color = Color("a0c3cc").lerp(Color("a7bec7"),atmosphere.clouds)
	if painted:
		atmosphere.environment.sky.sky_material = comparison_sky
		atmosphere.sky_cloud_material = comparison_sky
		cloud_color = Color("c8baa2")
		sea_mist_color = Color("99b6bd")
	else:
		atmosphere.environment.sky.sky_material = original_sky
		atmosphere.sky_cloud_material = original_sky
	atmosphere.mountain_cloud_material.set_shader_parameter("cloud_color",cloud_color)
	atmosphere.mountain_cloud_material.set_shader_parameter("sea_mist_color",sea_mist_color)
	atmosphere.mountain_cloud_material.set_shader_parameter("sunset_blend",1.0 if painted else 0.0)
	for water in atmosphere.water_materials:
		water.set_shader_parameter("sunset_haze",1.0 if painted else 0.0)
	button.text = "背景 %d/%d · %s  ›" % [mode+1,LABELS.size(),LABELS[mode]]
	print("BACKGROUND_MODE ",mode," ",LABELS[mode])

func _unhandled_key_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo and event.keycode == KEY_F6:
		cycle()
		get_viewport().set_input_as_handled()
