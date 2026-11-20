extends Node
## Imported Blender environment with separate, sharp character rendering.
const ASSET := "res://assets/pixel_cavern_coast/pixel_cavern_coast.glb"
const REVIEW := "res://artifacts/pixel-cavern-coast-review"
const SURFACE := preload("res://shaders/pixel_cavern_surface.gdshader")
const EDGES := preload("res://shaders/pixel_cavern_outline.gdshader")
const WATER := preload("res://shaders/pixel_cavern_water.gdshader")
const SKY := preload("res://shaders/pixel_cavern_sky.gdshader")
const MIST := preload("res://shaders/pixel_cavern_mist.gdshader")
const DEPTH := preload("res://shaders/pixel_cavern_depth.gdshader")
const MOUNTAIN := preload("res://shaders/pixel_cavern_mountains.gdshader")
const INTERIOR := preload("res://shaders/pixel_cavern_interior.gdshader")
const PLAYER := preload("res://scripts/pixel_cavern_player.gd")
const VEGETATION := preload("res://scripts/pixel_cavern_vegetation.gd")
const PLANT_SURFACE := preload("res://shaders/pixel_cavern_vegetation.gdshader")
const PLANT_DEPTH := preload("res://shaders/pixel_cavern_vegetation_depth.gdshader")
var low_view: SubViewport
var hero_view: SubViewport
var camera: Camera3D
var hero_camera: Camera3D
var world: Node3D
var frames := 0
var capture := false
var motion := false
var motion_frame := 0
var hero: Sprite3D
var hero_shadow: Sprite3D
var player: Node
var vegetation: Node

func _ready() -> void:
	DisplayServer.window_set_title("孤屿霜尘 · 竹林吊桥山洞 · 三维像素样区")
	capture = "--capture-cavern" in OS.get_cmdline_user_args()
	motion = "--motion-cavern" in OS.get_cmdline_user_args()
	DirAccess.make_dir_recursive_absolute(REVIEW)
	var holder := SubViewportContainer.new()
	holder.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	holder.stretch = true
	holder.stretch_shrink = 2
	holder.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	add_child(holder)
	low_view = SubViewport.new()
	low_view.size = Vector2i(640,480)
	low_view.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	low_view.msaa_3d = Viewport.MSAA_DISABLED
	low_view.use_taa = false
	holder.add_child(low_view)
	world = Node3D.new()
	low_view.add_child(world)
	_setup_light_and_air()
	var model := load(ASSET).instantiate() as Node3D
	world.add_child(model)
	_materials(model)
	camera = Camera3D.new()
	world.add_child(camera)
	camera.fov = 40
	camera.near = .1
	camera.far = 400
	camera.cull_mask = 1
	camera.current = true
	_character_pass(model)
	vegetation = VEGETATION.new()
	add_child(vegetation)
	vegetation.setup(self)
	if capture or motion:
		_view(1)
	else:
		player = PLAYER.new()
		add_child(player)
		player.setup(self, model)
		_sync()
	if motion:
		DirAccess.make_dir_recursive_absolute(REVIEW+"/motion")
	print("PIXEL_CAVERN_READY imported=",ASSET," low=",low_view.size," hero=",hero_view.size," old_scene_assets=0")

func _setup_light_and_air() -> void:
	var we := WorldEnvironment.new()
	var env := Environment.new()
	var sky := Sky.new()
	var sky_mat := ShaderMaterial.new()
	sky_mat.shader = SKY
	sky.sky_material = sky_mat
	env.sky = sky
	env.background_mode = Environment.BG_SKY
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color("96b6c2")
	env.ambient_light_energy = .42
	env.tonemap_mode = Environment.TONE_MAPPER_LINEAR
	env.ssao_enabled = true
	env.ssao_radius = .65
	env.ssao_intensity = .40
	env.fog_enabled = true
	env.fog_light_color = Color("b9c9be")
	env.fog_density = .0008
	env.fog_sky_affect = .12
	env.volumetric_fog_enabled = true
	env.volumetric_fog_density = .00035
	env.volumetric_fog_albedo = Color("b7c8bd")
	env.volumetric_fog_length = 145
	we.environment = env
	world.add_child(we)
	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-46,-43,0)
	sun.light_color = Color("fff0d7")
	sun.light_energy = 1.08
	sun.light_angular_distance = 1.2
	sun.shadow_enabled = true
	sun.shadow_bias = .045
	sun.shadow_normal_bias = .65
	sun.directional_shadow_max_distance = 90
	world.add_child(sun)
	var mist_positions := [Vector3(0,5,-27),Vector3(-17,8,-43),Vector3(22,7,-52),Vector3(0,9,-73)]
	var mist_sizes := [Vector3(43,18,24),Vector3(51,19,25),Vector3(48,19,26),Vector3(110,22,38)]
	for i in 4:
		var fog := FogVolume.new()
		fog.shape = RenderingServer.FOG_VOLUME_SHAPE_ELLIPSOID
		fog.size = mist_sizes[i]
		fog.position = mist_positions[i]
		var material := ShaderMaterial.new()
		material.shader = MIST
		material.set_shader_parameter("strength",.18 if i==0 else .19)
		material.set_shader_parameter("fog_tint",Color("c4d1cc"))
		fog.material = material
		world.add_child(fog)

func _kind(name: String) -> float:
	if name.begins_with("Bamboo_Leaves") or name.begins_with("Foliage_"): return 2.0
	if name.begins_with("Bamboo_"): return 3.0
	if name.begins_with("Plant_"): return 4.0
	if name.begins_with("Grass_"): return 1.0
	if name.begins_with("Mountain_"): return 5.0
	if name.begins_with("Wood_") or name.begins_with("Plank_") or name.begins_with("Rope_") or name.begins_with("Root_"): return 6.0
	return 0.0

func _wind_kind(label: String) -> float:
	if label.begins_with("Shadow_BambooMass_"): return 5.0
	if label.begins_with("Shadow_CanopyMass_"): return 2.0
	if label.begins_with("LiveGrass_"): return 1.0
	if label.begins_with("LiveCanopy_"): return 2.0
	if label.begins_with("LiveTreeBranch_") or label.begins_with("Bamboo_Stem_") or label.begins_with("Bamboo_Branches_"): return 3.0
	if label.begins_with("LiveVine"): return 4.0
	if label.begins_with("LiveBambooLeaf_"): return 5.0
	if label.begins_with("Plant_Fern_") or label.begins_with("Plant_Edge_Shrub_") or label.begins_with("Plant_Foreground_") or label.begins_with("Plant_Cliff_Creeper_"): return 6.0
	return 0.0

func _plant_color(original: StandardMaterial3D) -> Color:
	if not original: return Color("668c71")
	# Adjacent leaves share a restrained palette; volume comes from clump normals.
	var label := original.resource_name
	if label.begins_with("PCC_leaf_lit"): return Color("77966e")
	if label.begins_with("PCC_leaf_dark"): return Color("416a5b")
	if label.begins_with("PCC_leaf"): return Color("62876d")
	if label.begins_with("PCC_fern"): return Color("60846b")
	if label.begins_with("PCC_bamboo_light"): return Color("8e9d70")
	if label.begins_with("PCC_bamboo_dark"): return Color("416856")
	if label.begins_with("PCC_bamboo_node"): return Color("92a17b")
	if label.begins_with("PCC_bamboo"): return Color("6b8863")
	return original.albedo_color

func _materials(node: Node) -> void:
	for child in node.get_children(): _materials(child)
	if not node is MeshInstance3D: return
	var mi := node as MeshInstance3D
	if String(mi.name).begins_with("Render_"):
		var edge := ShaderMaterial.new()
		edge.shader = EDGES
		edge.render_priority = 100
		mi.material_override = edge
		mi.extra_cull_margin = 16384
		mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		return
	var kind := _kind(mi.name)
	var wind_kind := _wind_kind(mi.name)
	for i in mi.mesh.get_surface_count():
		var original := mi.mesh.surface_get_material(i) as StandardMaterial3D
		var mat := ShaderMaterial.new()
		if wind_kind > 0.0:
			mat.shader = PLANT_SURFACE
			mat.set_shader_parameter("wind_kind",wind_kind)
			mat.set_shader_parameter("base_color",_plant_color(original))
		elif String(mi.name).begins_with("Water_"):
			mat.shader = WATER
			mat.render_priority = 0
		elif String(mi.name).begins_with("Mountain_"):
			mat.shader = MOUNTAIN
			if original: mat.set_shader_parameter("base_color",original.albedo_color)
		elif String(mi.name).begins_with("CaveInterior_") or String(mi.name).begins_with("Step_Cave") or String(mi.name).begins_with("Rock_Cave_Buried"):
			mat.shader = INTERIOR
			mat.set_shader_parameter("stone_steps",String(mi.name).begins_with("Step_"))
		else:
			mat.shader = SURFACE
			mat.set_shader_parameter("kind",kind)
			if original: mat.set_shader_parameter("base_color",original.albedo_color)
		mi.set_surface_override_material(i,mat)
	if wind_kind == 1.0 or String(mi.name).begins_with("LiveBambooLeaf_") or String(mi.name).begins_with("LiveCanopy_"):
		# Blender-authored crown masses cast the shared, moving shadow instead.
		mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	mi.extra_cull_margin = .7 if wind_kind > 0.0 else 0.0
	if kind==4.0 or kind==5.0 or String(mi.name).begins_with("Water_"):
		mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	if String(mi.name).begins_with("Foliage_"):
		mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	if String(mi.name).begins_with("Shadow_"):
		mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_SHADOWS_ONLY

func _character_pass(model: Node3D) -> void:
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
	holder.add_child(hero_view)
	hero_camera = Camera3D.new()
	hero_camera.cull_mask = 2|4
	hero_camera.current = true
	hero_view.add_child(hero_camera)
	_depth_proxies(model)
	hero = Sprite3D.new()
	hero.texture = load("res://assets/characters/green_three_walk/right_idle.png")
	hero.pixel_size = 1.8/675.0
	hero.offset = Vector2(0,340)
	hero.position = Vector3(-4.7,4.51,.3)
	hero.billboard = BaseMaterial3D.BILLBOARD_FIXED_Y
	hero.layers = 2
	hero.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
	hero.shaded = false
	hero.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	world.add_child(hero)
	var shadow := Sprite3D.new()
	hero_shadow = shadow
	shadow.texture = hero.texture
	shadow.pixel_size = hero.pixel_size
	shadow.offset = hero.offset
	shadow.billboard = hero.billboard
	shadow.alpha_cut = SpriteBase3D.ALPHA_CUT_DISCARD
	shadow.layers = 1
	shadow.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_SHADOWS_ONLY
	hero.add_child(shadow)

func _depth_proxies(node: Node) -> void:
	for child in node.get_children(): _depth_proxies(child)
	if not node is MeshInstance3D: return
	var src := node as MeshInstance3D
	if String(src.name).begins_with("Render_") or String(src.name).begins_with("Water_") or String(src.name).begins_with("Shadow_") or String(src.name).begins_with("Mountain_"): return
	var proxy := MeshInstance3D.new()
	proxy.mesh = src.mesh
	proxy.layers = 4
	proxy.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	var mat := ShaderMaterial.new()
	var wind_kind := _wind_kind(src.name)
	mat.shader = PLANT_DEPTH if wind_kind > 0.0 else DEPTH
	mat.render_priority = -128
	if wind_kind > 0.0: mat.set_shader_parameter("wind_kind",wind_kind)
	else: mat.set_shader_parameter("kind",_kind(src.name))
	proxy.extra_cull_margin = .7
	proxy.material_override = mat
	src.add_child(proxy)

func _sync() -> void:
	hero_camera.global_transform = camera.global_transform
	hero_camera.fov = camera.fov
	hero_camera.near = camera.near
	hero_camera.far = camera.far

func _view(index: int) -> void:
	if player: player.follow = false
	if index==1:
		camera.position=Vector3(6.8,15.8,31.5)
		camera.look_at(Vector3(-.6,5.8,-.6),Vector3.UP)
		camera.fov=43
	elif index==2:
		camera.position=Vector3(2.0,12.2,20)
		camera.look_at(Vector3(-7.6,4.5,-.8),Vector3.UP)
		camera.fov=39
	else:
		camera.position=Vector3(15.9,12.2,17.3)
		camera.look_at(Vector3(9.9,6.5,-3.7),Vector3.UP)
		camera.fov=42
	_sync()

func _process(_delta:float) -> void:
	frames+=1
	if player: player.update_camera(_delta)
	_sync()
	if capture and frames in [35,55,75]:
		await RenderingServer.frame_post_draw
		var label := "overview" if frames==35 else "bamboo-stairs" if frames==55 else "bridge-cavern"
		get_viewport().get_texture().get_image().save_png(REVIEW+"/game-"+label+".png")
		if frames==35: _view(2)
		elif frames==55: _view(3)
		else:
			print("PIXEL_CAVERN_CAPTURED three_views=true")
			get_tree().quit()
	if motion and frames>35 and frames%4==0:
		await RenderingServer.frame_post_draw
		get_viewport().get_texture().get_image().save_png(REVIEW+"/motion/%03d.png"%motion_frame)
		motion_frame+=1
		if motion_frame==24:
			print("PIXEL_CAVERN_MOTION_CAPTURED frames=24")
			get_tree().quit()
		else:
			camera.position=Vector3(6.8,15.8,31.5)+camera.basis.x*sin(float(motion_frame)/23*TAU)*.45

func _unhandled_key_input(event:InputEvent) -> void:
	if event.is_action_pressed("ui_cancel"): get_tree().quit()
	if event is InputEventKey and event.pressed:
		if event.echo: return
		if player and event.keycode==KEY_F:
			player.follow = true
			player.snap_camera()
		if player and event.keycode==KEY_TAB: player.hud.visible = not player.hud.visible
		if event.keycode==KEY_1: _view(1)
		if event.keycode==KEY_2: _view(2)
		if event.keycode==KEY_3: _view(3)
