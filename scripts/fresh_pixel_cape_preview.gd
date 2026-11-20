extends Node
## New asset preview. This controller imports Blender geometry; it makes no meshes.
const ASSET := "res://assets/fresh_pixel_cape/fresh_pixel_cape.glb"
const SURFACE := preload("res://shaders/fresh_cape_surface.gdshader")
const WATER := preload("res://shaders/fresh_cape_water.gdshader")
const EDGES := preload("res://shaders/fresh_cape_edges.gdshader")
const OCCLUSION := preload("res://shaders/fresh_cape_occlusion.gdshader")
const REVIEW := "res://artifacts/cape-stone-steps-clarity-review"
var low_view: SubViewport
var camera: Camera3D
var hero_view: SubViewport
var hero_camera: Camera3D
var hero: Sprite3D
var occlusion_mode := false
var frame_count := 0
var capture_mode := false
var world: Node3D
var motion_mode := false
var motion_index := 0
var motion_origin := Vector3(-.6,9.0,16.6)
var pixel_step := .02

func _ready() -> void:
	capture_mode = "--capture-fresh-cape" in OS.get_cmdline_user_args()
	motion_mode = "--capture-cape-motion" in OS.get_cmdline_user_args()
	occlusion_mode = "--check-cape-occlusion" in OS.get_cmdline_user_args()
	DisplayServer.window_set_title("孤屿霜尘 · 全新岛角像素样区")
	var holder := SubViewportContainer.new()
	holder.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	holder.stretch = true
	holder.stretch_shrink = 2
	holder.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	add_child(holder)
	low_view = SubViewport.new()
	low_view.size = Vector2i(640,360)
	low_view.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	low_view.msaa_3d = Viewport.MSAA_DISABLED
	low_view.use_taa = false
	holder.add_child(low_view)
	world = Node3D.new()
	low_view.add_child(world)
	var env_node := WorldEnvironment.new()
	var env := Environment.new()
	env.background_mode = Environment.BG_COLOR
	env.background_color = Color("648e91")
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color("a0b9c9")
	env.ambient_light_energy = .30
	env.tonemap_mode = Environment.TONE_MAPPER_LINEAR
	env.ssao_enabled = true
	env.ssao_radius = .70
	env.ssao_intensity = .65
	env_node.environment = env
	world.add_child(env_node)
	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-48,-34,0)
	sun.light_color = Color("fff2d7")
	sun.light_energy = 1.05
	sun.shadow_enabled = true
	sun.shadow_bias = .18
	sun.shadow_normal_bias = 1.15
	sun.directional_shadow_max_distance = 40
	world.add_child(sun)
	var model := load(ASSET).instantiate() as Node3D
	world.add_child(model)
	_apply_materials(model)
	camera = Camera3D.new()
	world.add_child(camera)
	camera.position = Vector3(3,12.0,24)
	camera.look_at(Vector3(-1.8,3.1,0),Vector3.UP)
	camera.fov = 34
	camera.near = .1
	camera.far = 450
	camera.current = true
	camera.cull_mask = 1
	_create_character_pass(model)
	if motion_mode:
		_set_view(3)
		pixel_step = 2.0 * camera.global_position.distance_to(Vector3(-3.4,3,0)) * tan(deg_to_rad(camera.fov)*.5) / 360.0
		DirAccess.make_dir_recursive_absolute(REVIEW+"/motion")
	hero = Sprite3D.new()
	hero.texture = load("res://assets/characters/green_three_walk/right_idle.png")
	hero.pixel_size = 1.8 / 675.0
	hero.offset = Vector2(0,340)
	hero.position = Vector3(-2.7,3.17,1.15)
	hero.billboard = BaseMaterial3D.BILLBOARD_FIXED_Y
	hero.layers = 2
	hero.alpha_cut = SpriteBase3D.ALPHA_CUT_DISABLED
	hero.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
	hero.shaded = false
	hero.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	world.add_child(hero)
	var hero_shadow := Sprite3D.new()
	hero_shadow.texture = hero.texture
	hero_shadow.pixel_size = hero.pixel_size
	hero_shadow.offset = hero.offset
	hero_shadow.billboard = hero.billboard
	hero_shadow.alpha_cut = SpriteBase3D.ALPHA_CUT_DISCARD
	hero_shadow.alpha_scissor_threshold = .35
	hero_shadow.layers = 1
	hero_shadow.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_SHADOWS_ONLY
	hero.add_child(hero_shadow)
	_sync_character_camera()
	print("FRESH_CAPE_READY imported=", ASSET, " triangles=", _triangles(model), " old_assets_loaded=0")
	print("HERO_PASS full_resolution=",hero_view.size," world_shared=true depth_occlusion=true")

func _create_character_pass(model: Node3D) -> void:
	var holder := SubViewportContainer.new()
	holder.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	holder.stretch = true
	holder.mouse_filter = Control.MOUSE_FILTER_IGNORE
	holder.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
	add_child(holder)
	hero_view = SubViewport.new()
	hero_view.size = get_viewport().get_visible_rect().size
	hero_view.transparent_bg = true
	hero_view.world_3d = low_view.world_3d
	hero_view.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	hero_view.msaa_3d = Viewport.MSAA_DISABLED
	holder.add_child(hero_view)
	hero_camera = Camera3D.new()
	hero_camera.cull_mask = 2 | 4
	hero_view.add_child(hero_camera)
	hero_camera.current = true
	_add_depth_proxies(model)

func _add_depth_proxies(node: Node) -> void:
	# Reuse imported Blender meshes. No geometry is generated here.
	for child in node.get_children(): _add_depth_proxies(child)
	if not node is MeshInstance3D: return
	var source := node as MeshInstance3D
	if "Fresh_Render_Overlay" in source.name or "Sea_Surface" in source.name or "Shadow_Proxy" in source.name: return
	var proxy := MeshInstance3D.new()
	proxy.name = "CharacterDepth_"+source.name
	proxy.mesh = source.mesh
	proxy.layers = 4
	proxy.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	var mat := ShaderMaterial.new()
	mat.shader = OCCLUSION
	mat.render_priority = -128
	var kind := 0.0
	if "Bamboo" in source.name: kind = 2.0
	if "Grass_Clump" in source.name or "Grass_Patch_Blades" in source.name: kind = 3.0
	mat.set_shader_parameter("surface_kind",kind)
	mat.set_shader_parameter("wind_amount",.018 if kind>1.5 else 0.0)
	proxy.material_override = mat
	source.add_child(proxy)

func _sync_character_camera() -> void:
	hero_camera.global_transform = camera.global_transform
	hero_camera.fov = camera.fov
	hero_camera.near = camera.near
	hero_camera.far = camera.far

func _apply_materials(node: Node) -> void:
	if node is MeshInstance3D:
		var mi := node as MeshInstance3D
		if "Fresh_Render_Overlay" in mi.name:
			mi.extra_cull_margin = 16384
			mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
			var overlay := ShaderMaterial.new()
			overlay.shader = EDGES
			overlay.render_priority = 100
			mi.material_override = overlay
			return
		for i in mi.mesh.get_surface_count():
			var original := mi.mesh.surface_get_material(i) as StandardMaterial3D
			var shader_mat := ShaderMaterial.new()
			if "Sea_Surface" in mi.name:
				shader_mat.shader = WATER
			else:
				shader_mat.shader = SURFACE
				if original: shader_mat.set_shader_parameter("base_color", original.albedo_color)
				var kind := 0.0
				if "Grass_Surface" in mi.name or "Grass_Patch" in mi.name: kind = 1.0
				if "Bamboo" in mi.name: kind = 2.0
				if "Grass_Clump" in mi.name or "Grass_Patch_Blades" in mi.name: kind = 3.0
				shader_mat.set_shader_parameter("surface_kind",kind)
				shader_mat.set_shader_parameter("wind_amount",0.018 if kind>1.5 else 0.0)
			mi.set_surface_override_material(i,shader_mat)
		if "Grass_Patch" in mi.name:
			mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		if "Bamboo_Leaf_Cluster" in mi.name or "Bamboo_Leaf_Core" in mi.name:
			mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		if "Bamboo_Shadow_Proxy" in mi.name:
			mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_SHADOWS_ONLY
	for child in node.get_children(): _apply_materials(child)

func _triangles(node: Node) -> int:
	if String(node.name).begins_with("CharacterDepth_"): return 0
	var count := 0
	if node is MeshInstance3D:
		for s in node.mesh.get_surface_count():
			count += int(node.mesh.surface_get_array_index_len(s)/3)
	for child in node.get_children(): count += _triangles(child)
	return count

func _process(_delta: float) -> void:
	frame_count += 1
	_sync_character_camera()
	if motion_mode and frame_count > 25 and frame_count % 3 == 0:
		await RenderingServer.frame_post_draw
		get_viewport().get_texture().get_image().save_png(REVIEW+"/motion/%03d.png" % motion_index)
		motion_index += 1
		if motion_index >= 48:
			print("FRESH_CAPE_MOTION_CAPTURED frames=48 perspective=true anchor_snap=true")
			get_tree().quit()
			return
		var offset := sin(float(motion_index)/47.0*TAU)*.65
		# Stabilize the focus depth on the pixel grid while retaining perspective.
		# Other depths keep their natural perspective disparity.
		camera.position = motion_origin + camera.basis.x * snappedf(offset,pixel_step)
	if capture_mode and frame_count == 25:
		await RenderingServer.frame_post_draw
		var directory := REVIEW
		DirAccess.make_dir_recursive_absolute(directory)
		low_view.get_texture().get_image().save_png(directory+"/game-native-640.png")
		get_viewport().get_texture().get_image().save_png(directory+"/game-color-overview.png")
		camera.position = Vector3(5.8,8.2,14.5)
		camera.look_at(Vector3(2.0,1.8,1.6),Vector3.UP)
	if capture_mode and frame_count == 40:
		await RenderingServer.frame_post_draw
		get_viewport().get_texture().get_image().save_png(REVIEW+"/game-stairs-detail.png")
		camera.position = Vector3(-.6,9.0,16.6)
		camera.look_at(Vector3(-3.4,3.0,0.0),Vector3.UP)
	if capture_mode and frame_count == 55:
		await RenderingServer.frame_post_draw
		get_viewport().get_texture().get_image().save_png(REVIEW+"/game-character-detail.png")
		hero_view.get_texture().get_image().save_png(REVIEW+"/character-transparent-pass.png")
		print("FRESH_CAPE_CAPTURED overview_stairs_character")
		get_tree().quit()
	if occlusion_mode and frame_count == 25:
		_set_view(3)
		hero.position = Vector3(-3.4,1.4,1.9)
	if occlusion_mode and frame_count == 40:
		await RenderingServer.frame_post_draw
		get_viewport().get_texture().get_image().save_png(REVIEW+"/occlusion-buried.png")
		hero_view.get_texture().get_image().save_png(REVIEW+"/occlusion-buried-alpha.png")
		hero.position = Vector3(-3.4,2.25,1.9)
	if occlusion_mode and frame_count == 55:
		await RenderingServer.frame_post_draw
		get_viewport().get_texture().get_image().save_png(REVIEW+"/occlusion-partial.png")
		hero_view.get_texture().get_image().save_png(REVIEW+"/occlusion-partial-alpha.png")
		print("HERO_OCCLUSION_CAPTURED buried_and_partial")
		get_tree().quit()

func _unhandled_key_input(event: InputEvent) -> void:
	if event.is_action_pressed("ui_cancel"): get_tree().quit()
	if event is InputEventKey and event.pressed:
		if event.keycode == KEY_1: _set_view(1)
		if event.keycode == KEY_2: _set_view(2)
		if event.keycode == KEY_3: _set_view(3)

func _set_view(index: int) -> void:
	if index == 1:
		camera.position = Vector3(3,12,24)
		camera.look_at(Vector3(-1.8,3.1,0),Vector3.UP)
	elif index == 2:
		camera.position = Vector3(5.8,8.2,14.5)
		camera.look_at(Vector3(2,1.8,1.6),Vector3.UP)
	else:
		camera.position = motion_origin
		camera.look_at(Vector3(-3.4,3,0),Vector3.UP)
