extends Node3D
## Blender-authored assets only. Godot handles rendering and gameplay, never mesh generation.

@export_group("Gameplay Camera")
@export_range(18.0, 50.0, 0.5) var gameplay_fov := 23.14
@export var camera_offset := Vector3(2.27, 7.22, 22.18)
@export_range(0.0, 3.0, 0.1) var camera_look_ahead := 1.2
@export_range(1.0, 12.0, 0.5) var camera_follow_speed := 5.0

@export_group("Coastal Daylight")
@export_range(7.0, 17.0, 0.1) var daylight_hour := 11.2
@export_range(0.0, 1.0, 0.01) var cloud_cover := 0.12
var atmosphere: Node

var camera: Camera3D
var hero: AnimatedSprite3D
var hud: CanvasLayer
var lens: ShaderMaterial
var capture_path := ""
var capture_frames := 0
const HERO_START_X := -24.2
const HERO_END_X := 34.0
var hero_x := HERO_START_X
var hero_path_offset := 0.0
var hero_facing := Vector2.RIGHT
const HERO_SPEED := 3.6
const HERO_VISUAL_SCALE := 0.75
const HERO_PIXEL_SIZE := 0.0037 * HERO_VISUAL_SCALE
const HERO_SPRITE_OFFSET := Vector2(0, 340)
# The authored walking strip stays level with _height within +/-0.58 m.
# Keep the actor inside it and inside the bridge's rope rails.
const HERO_PATH_HALF_WIDTH := 0.55
var clock_time := 0.0
var coastal_life: Node3D
var status_label: Label
var camera_focus := Vector3.ZERO
var camera_facing := 1.0
var camera_opening := 0.0
var cape_opening := 0.0
var contact_shadow: MeshInstance3D
var material_cache: Dictionary = {}
var foliage_materials: Dictionary = {}
var lens_surface: MeshInstance3D
var capture_lens_enabled := true
var capture_hide_hud := false
var camera_effects: CameraAttributesPractical
var background_comparison: Node
var opening: Node
var skip_opening := false
var hero_presentation: RefCounted


func _ready() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--capture="):
			capture_path = arg.trim_prefix("--capture=")
		if arg.begins_with("--hero-x="):
			hero_x = clampf(float(arg.trim_prefix("--hero-x=")), HERO_START_X, HERO_END_X)
		if arg == "--no-lens":
			capture_lens_enabled = false
		if arg == "--hide-hud":
			capture_hide_hud = true
		if arg == "--skip-opening":
			skip_opening = true
		if arg.begins_with("--day-hour="):
			daylight_hour = float(arg.trim_prefix("--day-hour="))
		if arg.begins_with("--cloud-cover="):
			cloud_cover = float(arg.trim_prefix("--cloud-cover="))
	_setup_environment()
	_configure_asset($World3D)
	preload("res://scripts/forest_spring.gd").add_pool_fill($World3D/EastSpring)
	var pixel_forest=preload("res://scripts/pixel_bamboo_forest.gd").new()
	pixel_forest.name="PixelBambooAtmosphere"
	add_child(pixel_forest)
	pixel_forest.configure()
	_build_hero()
	hero_presentation = preload("res://scripts/hero_presentation.gd").new()
	hero_presentation.configure(self)
	_position_hero()
	coastal_life = preload("res://scripts/coastal_life.gd").new()
	coastal_life.name = "CoastalLife"
	add_child(coastal_life)
	coastal_life.configure()
	coastal_life.bind_underwater($World3D)
	_build_presentation()
	get_viewport().size_changed.connect(_fit_camera)
	_fit_camera()
	_update_camera(0.0, true)
	opening = preload("res://scripts/opening_rest.gd").new()
	opening.name = "OpeningRest"
	add_child(opening)
	opening.configure(self, not skip_opening and capture_path.is_empty() and is_equal_approx(hero_x, HERO_START_X))
	_update_camera(0.0, true)
	_update_ground_contact()
	print("Blender island ready: imported terrain, rocks, bridge, trees, foliage and seabirds.")


func _setup_environment() -> void:
	atmosphere = preload("res://scripts/island_atmosphere.gd").new()
	atmosphere.name = "CoastalDaylight"
	add_child(atmosphere)
	atmosphere.configure(daylight_hour, cloud_cover)
	camera = Camera3D.new()
	camera.name = "GameplayCamera"
	camera.far = 2000
	add_child(camera)
	camera.current = true
	camera_effects = CameraAttributesPractical.new()
	camera_effects.dof_blur_far_enabled = capture_lens_enabled
	camera_effects.dof_blur_far_distance = 55.0
	camera_effects.dof_blur_far_transition = 180.0
	camera_effects.dof_blur_near_enabled = capture_lens_enabled
	camera_effects.dof_blur_near_distance = 11.6
	camera_effects.dof_blur_near_transition = 3.6
	camera_effects.dof_blur_amount = 0.025
	camera.attributes = camera_effects


func _configure_asset(node: Node) -> void:
	if node is MeshInstance3D:
		var instance := node as MeshInstance3D
		var title := str(instance.name)
		if title.begins_with("ForestSpring_"):
			preload("res://scripts/forest_spring.gd").configure(instance)
		elif title == "HD2D_Lens_Surface":
			lens_surface = instance
			instance.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		elif title == "Open_Sea":
			var water := ShaderMaterial.new()
			water.shader = load("res://shaders/fish_water.gdshader")
			atmosphere.configure_water(water)
			instance.material_override = water
			instance.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		elif "Foam" in title:
			var foam := ShaderMaterial.new()
			foam.shader = load("res://shaders/island_foam.gdshader")
			instance.material_override = foam
			instance.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		elif title == "ContactShadow":
			contact_shadow = instance
			var shadow := ShaderMaterial.new()
			shadow.shader = preload("res://shaders/hero_ground_contact.gdshader")
			instance.material_override = shadow
			instance.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		elif title.begins_with("Cliff_Fern_"):
			var fern := ShaderMaterial.new()
			fern.shader = load("res://shaders/cliff_fern.gdshader")
			instance.material_override = fern
		elif title.begins_with("Fish_Underwater_Kelp"):
			var kelp := ShaderMaterial.new()
			kelp.shader = load("res://shaders/underwater_kelp.gdshader")
			instance.material_override = kelp
		else:
			var foliage := "Needle" in title or "Leaves" in title or "Fronds" in title or "Grass_Patch" in title or "Grass_Transition" in title
			for surface in instance.mesh.get_surface_count():
				var imported := instance.mesh.surface_get_material(surface) as StandardMaterial3D
				if imported == null:
					continue
				if preload("res://scripts/colored_ink_sample.gd").apply_surface(instance,surface,imported):
					continue
				if imported.resource_name in ["Depth_Bamboo_Stem", "Depth_Bamboo_Canopy"]:
					if not foliage_materials.has(imported):
						var bamboo := ShaderMaterial.new()
						bamboo.shader = load("res://shaders/depth_bamboo.gdshader")
						bamboo.set_shader_parameter("is_leaf", imported.resource_name == "Depth_Bamboo_Canopy")
						foliage_materials[imported] = bamboo
					instance.set_surface_override_material(surface, foliage_materials[imported])
					continue
				if imported.resource_name == "Depth_Mountain":
					var mountain := ShaderMaterial.new()
					mountain.shader = load("res://shaders/depth_mountain.gdshader")
					instance.set_surface_override_material(surface, mountain)
					continue
				if imported.resource_name == "Coast_Palm" or imported.resource_name == "Coast_Grass":
					if not foliage_materials.has(imported):
						var coast_plant := ShaderMaterial.new()
						if imported.resource_name == "Coast_Palm":
							coast_plant.shader = load("res://shaders/coast_palm.gdshader")
							coast_plant.set_shader_parameter("albedo_texture", imported.albedo_texture)
							coast_plant.set_shader_parameter("normal_texture", imported.normal_texture)
						else:
							coast_plant.shader = load("res://shaders/coast_grass.gdshader")
							coast_plant.set_shader_parameter("ground_atlas", load("res://assets/island_blender/palm_study/Island_Ground_Study.png"))
						foliage_materials[imported] = coast_plant
					instance.set_surface_override_material(surface, foliage_materials[imported])
					continue
				if imported.resource_name in ["Fish_Leaves", "Fish_Grass"]:
					if not foliage_materials.has(imported):
						var fish_leaf := ShaderMaterial.new()
						fish_leaf.shader = load("res://shaders/fish_foliage.gdshader")
						fish_leaf.set_shader_parameter("albedo_texture", imported.albedo_texture)
						fish_leaf.set_shader_parameter("base_color", imported.albedo_color)
						fish_leaf.set_shader_parameter("is_grass", imported.resource_name == "Fish_Grass")
						fish_leaf.set_shader_parameter("amplitude", 0.025 if imported.resource_name == "Fish_Grass" else 0.045)
						foliage_materials[imported] = fish_leaf
					instance.set_surface_override_material(surface, foliage_materials[imported])
					continue
				if foliage:
					if not foliage_materials.has(imported):
						var leaf := ShaderMaterial.new()
						leaf.shader = load("res://shaders/island_mesh_foliage.gdshader")
						leaf.set_shader_parameter("base_color",imported.albedo_color)
						leaf.set_shader_parameter("use_texture",imported.albedo_texture != null)
						if imported.albedo_texture:
							leaf.set_shader_parameter("albedo_texture",imported.albedo_texture)
						foliage_materials[imported] = leaf
					instance.set_surface_override_material(surface,foliage_materials[imported])
					continue
				if not material_cache.has(imported):
					var mat := imported.duplicate() as StandardMaterial3D
					mat.texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST
					mat.cull_mode = BaseMaterial3D.CULL_DISABLED
					mat.roughness = 0.95
					if imported.resource_name.begins_with("Fish_"):
						mat.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS_ANISOTROPIC
						mat.roughness = imported.roughness
					if imported.resource_name.begins_with("Fish_Rock_"):
						mat.albedo_color = Color(0.78, 0.82, 0.80)
						mat.metallic_specular = 0.18
						mat.normal_scale = 1.0
					if imported.resource_name.begins_with("Coast_"):
						mat.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS_ANISOTROPIC
						mat.metallic_specular = 0.12
					if imported.resource_name == "Coast_Ground":
						mat.vertex_color_use_as_albedo = false
						mat.albedo_color = Color(0.78, 0.82, 0.79)
						mat.normal_scale = 0.38
						mat.roughness = 1.0
					material_cache[imported] = mat
				instance.set_surface_override_material(surface,material_cache[imported])
			if title.begins_with("Hazy_Islet"):
				var haze := StandardMaterial3D.new()
				haze.albedo_color = Color("83b1b3")
				haze.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
				instance.material_override = haze
	for child in node.get_children():
		_configure_asset(child)


func _height(x: float, z: float) -> float:
	if x>=27.1:return 1.28
	if x <= 2.8:return 1.86-2.31*(1.0-smoothstep(-23.0,-16.0,x))
	var authored := _source_height(preload("res://scripts/cape_layout.gd").source_x(x),z)
	# Match the Blender-authored lower western walking terrace. The cape and
	# bridge joints fade to their existing elevations; no geometry is generated.
	var weight := smoothstep(-15.1,-12.2,x)*(1.0-smoothstep(.5,4.0,x))
	return lerpf(1.86,authored-maxf(0.0,authored-1.5)*.40*weight,smoothstep(2.8,4.1,x))

func _source_height(x: float, z: float) -> float:
	if x > 10:
		return 1.15 + sin(x*0.37)*0.18 + maxf(0, -z)*0.16
	var slope := 1.65 + (4.5-x)*0.127
	var undulation := sin(x*0.39)*0.16 + cos(z*1.3+x*0.21)*0.10
	var original := slope + undulation + maxf(0, -z-0.3)*0.23
	if x < -12.5:
		var across := 1.0-smoothstep(1.10,3.1,absf(z-_source_path_z(x)))
		var extent := smoothstep(-24.65,-23.1,x)*(1.0-smoothstep(-13.3,-12.5,x))
		var protect := smoothstep(.88,1.30,Vector2(x+23.0,z+.06).length())
		var start_z := .4+sin(-20.7*.25)*.44
		var start_y := 1.65+(4.5+20.7)*.127+sin(-20.7*.39)*.16+cos(start_z*1.3-20.7*.21)*.10
		var route_z := _source_path_z(x)
		var route_y := 1.65+(4.5-x)*.127+sin(x*.39)*.16+cos(route_z*1.3+x*.21)*.10+maxf(0.0,-route_z-.3)*.23
		var deck := lerpf(start_y,route_y,smoothstep(-18.5,-12.5,x))
		return lerpf(original,deck,across*extent*protect)
	return original


func _path_z(x: float) -> float:
	if x>24.2:return preload("res://scripts/forest_spring.gd").path_z(x)
	if x <= 4.5:return .25
	return _source_path_z(preload("res://scripts/cape_layout.gd").source_x(x))

func _source_path_z(x: float) -> float:
	if x >= 4.5 and x <= 14:
		return 0.25
	# Match the flat cape route to the opening camera's screen-right direction.
	# The same profile is authored into Blender terrain and the grass/road painting.
	if x < -12.5:
		var start_z := .4+sin(-20.7*.25)*.44
		if x <= -18.5:
			return start_z-(x+20.7)*5.0/9.0
		var t := (x+18.5)/6.0
		var a := start_z-(-18.5+20.7)*5.0/9.0
		var b := .4+sin(-12.5*.25)*.44
		return (2*t*t*t-3*t*t+1)*a+(t*t*t-2*t*t+t)*6.0*(-5.0/9.0)+(-2*t*t*t+3*t*t)*b+(t*t*t-t*t)*6.0*.11*cos(-12.5*.25)
	return 0.4 + sin(x*0.25)*0.44


func _bridge_y(x: float) -> float:
	var f := clampf((x-4.2)/10.3,0,1)
	return lerpf(_height(4.2,0.25),_height(14.5,0.25),f)-sin(f*PI)*0.48


func _build_hero() -> void:
	hero = AnimatedSprite3D.new()
	hero.name = "WanderingSwordsman"
	hero.sprite_frames = preload("res://assets/characters/green_three_walk/swordsman_walk.tres")
	# All views share a 512x768 canvas and foot bottom edge y=724.
	hero.pixel_size = HERO_PIXEL_SIZE
	hero.offset = HERO_SPRITE_OFFSET
	hero.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	hero.texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST
	hero.alpha_cut = SpriteBase3D.ALPHA_CUT_DISCARD
	hero.shaded = true
	hero.modulate = Color(0.92,0.98,0.91)
	hero.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON
	hero.animation = "idle_right"
	add_child(hero)
	_position_hero()
	if is_instance_valid(contact_shadow):
		contact_shadow.reparent(hero)
		contact_shadow.position = Vector3(0,0.01,0)
	hero.frame_changed.connect(_update_ground_contact)
	hero.animation_changed.connect(_update_ground_contact)
	_update_ground_contact()


func _update_ground_contact() -> void:
	if not is_instance_valid(contact_shadow):
		return
	var lying := 0.0
	if hero.animation == &"rest_rise_right":
		lying=1.0-smoothstep(22.0,68.0,float(hero.frame)+hero.frame_progress)
	# A broad soft contact under the resting body contracts as weight reaches feet.
	# Scale the existing contact shape with the character, preserving the foot anchor.
	var right := camera.global_basis.x
	right.y=0.0
	right=right.normalized()
	var forward := Vector3(-right.z,0,right.x)
	var center := hero.global_position+right*(-.20*lying*HERO_VISUAL_SCALE)+forward*(.17*lying*HERO_VISUAL_SCALE)
	center.y=_height(center.x,center.z)+.016
	if hero_x>4.2 and hero_x<14.5:center.y=_bridge_y(hero_x)+.096
	var dx:=(_height(center.x+.08,center.z)-_height(center.x-.08,center.z))/.16
	var dz:=(_height(center.x,center.z+.08)-_height(center.x,center.z-.08))/.16
	var up:=Vector3(-dx,1.0,-dz).normalized()
	if hero_x>4.2 and hero_x<14.5:up=Vector3.UP
	if hero_presentation != null and hero.animation != &"rest_rise_right":
		center=hero_presentation.contact_point
		up=hero_presentation.ground(center.x,center.z).normal
	var contact_material := contact_shadow.material_override as ShaderMaterial
	contact_material.set_shader_parameter("sole_contact",.35 if hero_presentation != null and lying<.01 else 0.0)
	right=(right-up*right.dot(up)).normalized()
	var back:=right.cross(up).normalized()
	var shape:=Vector3(lerpf(.86,3.55,lying)*HERO_VISUAL_SCALE,1.0,lerpf(.85,1.85,lying)*HERO_VISUAL_SCALE)
	contact_shadow.global_transform=Transform3D(Basis(right,up,back).scaled_local(shape),center)


func _position_hero() -> void:
	var path_center := _path_z(hero_x)
	# The old route bends near the landings. Narrow its usable depth before
	# entering the bridge so the new axis cannot carry the feet past the rails.
	var bridge_weight := smoothstep(3.2, 4.2, hero_x) * (1.0 - smoothstep(14.5, 15.5, hero_x))
	var rear_limit := lerpf(-HERO_PATH_HALF_WIDTH, maxf(-HERO_PATH_HALF_WIDTH, -0.30 - path_center), bridge_weight)
	var front_limit := lerpf(HERO_PATH_HALF_WIDTH, minf(HERO_PATH_HALF_WIDTH, 0.80 - path_center), bridge_weight)
	hero_path_offset = clampf(hero_path_offset, rear_limit, front_limit)
	var z := path_center + hero_path_offset
	var y := _height(hero_x,z)
	if hero_x > 4.2 and hero_x < 14.5:
		y = _bridge_y(hero_x)+0.08
	if hero_presentation != null:
		y=hero_presentation.ground(hero_x,z).height
	hero.position = Vector3(hero_x,y+0.04,z)


func _set_hero_animation(animation: StringName, walking: bool) -> void:
	if walking:
		hero.play(animation)
	else:
		hero.animation = animation
		hero.pause()


func _move_hero(input_vector: Vector2, delta: float) -> void:
	if is_instance_valid(opening) and opening.is_input_locked():
		return
	var move := input_vector.limit_length()
	var previous_position := hero.position
	if not move.is_zero_approx():
		# A diagonal uses its dominant axis, with horizontal winning exact ties.
		if absf(move.y) > absf(move.x):
			hero_facing = Vector2(0, signf(move.y))
		else:
			hero_facing = Vector2(signf(move.x), 0)
		camera_facing = hero_facing.x
		hero_x = clampf(hero_x + move.x * delta * HERO_SPEED, HERO_START_X, HERO_END_X)
		hero_path_offset += move.y * delta * HERO_SPEED
		_position_hero()
	var walking := not hero.position.is_equal_approx(previous_position)
	hero.flip_h = hero_facing.x < 0.0
	if not is_zero_approx(hero_facing.y):
		var suffix := "up" if hero_facing.y < 0.0 else "down"
		_set_hero_animation(StringName(("walk_" if walking else "idle_") + suffix), walking)
	else:
		_set_hero_animation(&"walk_right" if walking else &"idle_right", walking)


func _build_presentation() -> void:
	lens = ShaderMaterial.new()
	lens.shader = load("res://shaders/island_depth_lens.gdshader")
	lens.render_priority = 127
	lens.set_shader_parameter("enabled",capture_lens_enabled)
	if is_instance_valid(lens_surface):
		lens_surface.reparent(camera)
		lens_surface.transform = Transform3D.IDENTITY
		lens_surface.position.z = -1.0
		lens_surface.extra_cull_margin = 16000.0
		lens_surface.material_override = lens
		# Native camera DOF includes refractive water. A second screen-copy lens
		# would sample the opaque buffer again and erase the water's refraction.
		lens_surface.visible = false
	hud = CanvasLayer.new()
	hud.name = "SceneTitles"
	hud.layer = 5
	hud.visible = not capture_hide_hud
	add_child(hud)
	var root := Control.new()
	root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	hud.add_child(root)
	var title := _label("孤 屿 霜 尘",44,Color("f4f4d7"))
	title.position = Vector2(48,38)
	root.add_child(title)
	var subtitle := _label("东 海  ·  无 名 屿",20,Color("e0eee0"))
	subtitle.position = Vector2(52,104)
	root.add_child(subtitle)
	var line := ColorRect.new()
	line.color = Color(0.91,0.91,0.70,0.7)
	line.position = Vector2(52,148)
	line.size = Vector2(84,2)
	root.add_child(line)
	var day_part := "巳 时" if daylight_hour < 11.0 else ("午 时" if daylight_hour < 13.0 else "午 后")
	var sky_state := "多 云" if cloud_cover >= 0.55 else "海 风"
	var time_label := _label(day_part + "  /  " + sky_state,20,Color("e7efda"))
	time_label.set_anchors_and_offsets_preset(Control.PRESET_TOP_RIGHT)
	time_label.position = Vector2(-194,54)
	root.add_child(time_label)
	status_label = _label("临海绝径   ·   西行至此，已无去路",20,Color("e6ead7"))
	status_label.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_LEFT)
	status_label.position = Vector2(52,-90)
	root.add_child(status_label)
	var hint := _label("WASD / 方向键  行走       TAB  隐藏界面       F  景深       R  重播开场",18,Color("c9e2d6"))
	hint.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_LEFT)
	hint.position = Vector2(52,-54)
	root.add_child(hint)
	background_comparison = preload("res://scripts/background_comparison.gd").new()
	background_comparison.name = "BackgroundComparison"
	add_child(background_comparison)
	background_comparison.configure(self,root)


func _label(text: String, size: int, color: Color) -> Label:
	var label := Label.new()
	label.text = text
	label.add_theme_font_size_override("font_size",size)
	label.add_theme_color_override("font_color",color)
	label.add_theme_color_override("font_shadow_color",Color(0.03,0.17,0.19,0.45))
	label.add_theme_constant_override("shadow_offset_x",2)
	label.add_theme_constant_override("shadow_offset_y",2)
	var font := SystemFont.new()
	font.font_names = PackedStringArray(["Microsoft YaHei", "Noto Sans CJK SC"])
	label.add_theme_font_override("font",font)
	label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return label


func _fit_camera() -> void:
	# Preserve the character's screen height; narrow screens show less of the coast.
	camera.keep_aspect = Camera3D.KEEP_HEIGHT
	camera.fov = gameplay_fov


func _update_camera(delta: float, snap := false) -> void:
	# The high cape angle belongs to the opening/dialogue, not a stretch of the walk.
	var opening_shot := not skip_opening and is_equal_approx(hero_x,HERO_START_X)
	if is_instance_valid(opening):opening_shot=opening.is_cape_shot()
	var cape_target := 1.0 if opening_shot else 0.0
	cape_opening = cape_target if snap else lerpf(cape_opening,cape_target,1.0-exp(-2.2*delta))
	if is_instance_valid(opening) and opening.phase == opening.Phase.TRANSITION:
		cape_opening = 1.0-smoothstep(0.0,1.8,opening.transition_elapsed)
	var desired := hero.position+Vector3(camera_facing*camera_look_ahead,1.0,0.0)
	var grove_weight := smoothstep(-14.8,-12.8,hero_x)*(1.0-smoothstep(-.8,5.0,hero_x))
	desired += Vector3(.35,.25,0)*grove_weight
	desired.x = clampf(desired.x,HERO_START_X-.8,HERO_END_X+1.2)
	var spring_weight := smoothstep(24.5,28.5,hero_x)
	desired=desired.lerp(hero.position+Vector3(.8,2.85,-.8),spring_weight)
	# Frame the cape from higher above, keeping the whole actor above the
	# bottom dialogue and to the right of its shoulder portrait.
	var cape_focus := hero.position+Vector3(-4.0,-.15,-1.5)
	if is_instance_valid(opening) and opening.phase in [opening.Phase.DIALOGUE_REFRAME,opening.Phase.DIALOGUE]:
		var dialogue_frame := 1.0 if opening.phase == opening.Phase.DIALOGUE else smoothstep(0.0,1.4,opening.transition_elapsed)
		cape_focus += Vector3(0,-.8,4.0)*dialogue_frame
	elif is_instance_valid(opening) and opening.phase == opening.Phase.TRANSITION:
		cape_focus += Vector3(0,-.8,4.0)
	desired = desired.lerp(cape_focus,cape_opening)
	if snap or (is_instance_valid(opening) and opening.is_input_locked()):
		camera_focus = desired
	else:
		camera_focus.x = lerpf(camera_focus.x,desired.x,1.0-exp(-camera_follow_speed*delta))
		var vertical_weight := 1.0-exp(-3.0*delta)
		camera_focus.y = lerpf(camera_focus.y,desired.y,vertical_weight)
		camera_focus.z = lerpf(camera_focus.z,desired.z,vertical_weight)
	var open_target := smoothstep(1.0,7.0,hero_x)*(1.0-smoothstep(13.0,19.5,hero_x))
	camera_opening = open_target if snap else lerpf(camera_opening,open_target,1.0-exp(-1.4*delta))
	# Dolly on a single viewing axis: no regional orbit or change of exploration pitch.
	var valley_weight := grove_weight
	var forest_camera := 1.0-smoothstep(-1.0,5.0,hero_x)
	var framed_offset := Vector3(1.35,4.3,13.2).lerp(Vector3(camera_offset.x,5.6,camera_offset.z),forest_camera)*(1.0+.055*camera_opening-.035*valley_weight)
	# A modest elevated opening keeps the bent cape readable without a top-down
	# view of side-view artwork. The viewing direction stays close to the walk.
	framed_offset = framed_offset.lerp(Vector3(.8,6.6,14.5),cape_opening)
	camera.fov = lerpf(lerpf(38.0,gameplay_fov,forest_camera),38.5,cape_opening)
	camera.position = camera_focus+framed_offset
	camera.look_at(camera_focus)
	var intro_view := 0.0
	if is_instance_valid(opening) and opening.phase == opening.Phase.ESTABLISHING:
		var descent: float = opening.descent_progress()
		var end_offset := Vector3(.8,6.6,14.5)
		var yaw := atan2(end_offset.x,end_offset.z)
		var pitch := lerpf(PI*.5,asin(end_offset.y/end_offset.length()),descent)
		var distance := lerpf(35.0,end_offset.length(),descent)
		var target := Vector3(-32.0,1.0,1.8).lerp(cape_focus,descent)
		# Explicit basis avoids look_at's singular up vector at exactly 90 degrees.
		camera.basis = Basis.from_euler(Vector3(-pitch,yaw,0.0))
		camera.position = target + camera.basis.z*distance
		camera.fov = lerpf(42.0,36.5,descent)
		intro_view = 1.0-descent
	# Near turf falls out of focus in the groves; the open bridge view keeps
	# the shallows legible. Focus changes follow the same continuous opening.
	camera_effects.dof_blur_near_distance = lerpf(lerpf(11.6,10.0,camera_opening),19.5,forest_camera)
	var actor_depth := -camera.to_local(hero.global_position).z
	camera_effects.dof_blur_near_distance = lerpf(camera_effects.dof_blur_near_distance,actor_depth-1.6,valley_weight)
	camera_effects.dof_blur_near_distance = lerpf(camera_effects.dof_blur_near_distance,actor_depth-1.15,cape_opening)
	camera_effects.dof_blur_near_transition = lerpf(3.6,1.6,cape_opening)
	camera_effects.dof_blur_far_distance = lerpf(lerpf(55.0,actor_depth+6.0,valley_weight),actor_depth+5.0,cape_opening)
	camera_effects.dof_blur_far_transition = lerpf(lerpf(180.0,18.0,valley_weight),10.0,cape_opening)
	camera_effects.dof_blur_amount = lerpf(lerpf(.025,.065,valley_weight),.055,cape_opening)
	camera_effects.dof_blur_amount *= pow(1.0-intro_view,3.0)
	atmosphere.set_cape_opening(cape_opening)
	for water: ShaderMaterial in atmosphere.water_materials:
		water.set_shader_parameter("overhead_intro",intro_view)
	hero.modulate = Color(.92,.98,.91).lerp(Color(.97,.99,.95),cape_opening)
	if hero_presentation != null:
		hero_presentation.update(delta,snap)
	if lens:
		lens.set_shader_parameter("focus_distance",camera_offset.length())


func _process(delta: float) -> void:
	clock_time += delta
	var move := Input.get_vector("move_left", "move_right", "move_up", "move_down")
	var arrows := Vector2(
		float(Input.is_key_pressed(KEY_RIGHT)) - float(Input.is_key_pressed(KEY_LEFT)),
		float(Input.is_key_pressed(KEY_DOWN)) - float(Input.is_key_pressed(KEY_UP)))
	_move_hero((move + arrows).limit_length(), delta)
	_update_camera(delta)
	_update_ground_contact()
	coastal_life.advance(delta,hero_x)
	if not capture_path.is_empty():
		capture_frames += 1
		if capture_frames == 70:
			await RenderingServer.frame_post_draw
			var err := get_viewport().get_texture().get_image().save_png(capture_path)
			print("Island capture: ",capture_path," result=",err)
			print("Preview average FPS: ",snappedf(capture_frames/maxf(clock_time,0.001),0.1))
			get_tree().quit(err)


func _unhandled_key_input(event: InputEvent) -> void:
	if not event is InputEventKey or not event.pressed or event.echo:
		return
	match event.keycode:
		KEY_TAB:
			if not opening.is_input_locked():
				hud.visible = not hud.visible
		KEY_F:
			var enabled := not bool(lens.get_shader_parameter("enabled"))
			lens.set_shader_parameter("enabled",enabled)
			camera_effects.dof_blur_far_enabled = enabled
			camera_effects.dof_blur_near_enabled = enabled
		KEY_R:
			hero_x = HERO_START_X
			hero_path_offset = 0.0
			hero_facing = Vector2.RIGHT
			hero.flip_h = false
			if opening.enabled:
				opening.start()
			else:
				_set_hero_animation(&"idle_right", false)
				hero.frame = 0
			camera_facing = 1.0
			_position_hero()
			_update_camera(0.0, true)
