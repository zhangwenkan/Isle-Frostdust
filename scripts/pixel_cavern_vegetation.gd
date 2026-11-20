extends Node
## Runtime wind / footprint uniforms only. All plant meshes are Blender assets.
const SURFACE := preload("res://shaders/pixel_cavern_vegetation.gdshader")
const DEPTH := preload("res://shaders/pixel_cavern_vegetation_depth.gdshader")
const TRAIL_COUNT := 12
const RECOVERY_SECONDS := 1.5
const STAMP_INTERVAL := 0.12
var preview: Node
var materials: Array[ShaderMaterial] = []
var grass_materials: Array[ShaderMaterial] = []
var _material_ids: Dictionary = {}
var _trail_positions := PackedVector3Array()
var _trail_ages := PackedFloat32Array()
var _trail_cursor := 0
var _last_stamp := Vector3.ZERO
var _last_hero := Vector3.ZERO
var _movement_direction := Vector2.RIGHT
var _stamp_elapsed := 0.0
var _uniform_elapsed := 0.0
var _step_side := 1.0
var _has_hero_position := false
var _time_override := -1.0
var _wind_strength := 1.0

func setup(scene: Node) -> void:
	preview = scene
	_trail_positions.resize(TRAIL_COUNT)
	_trail_ages.resize(TRAIL_COUNT)
	_trail_ages.fill(RECOVERY_SECONDS)
	_collect_materials(preview.world)
	_push_uniforms()
	print("CAVERN_VEGETATION_READY materials=",materials.size()," grass_passes=",grass_materials.size()," footprint_recovery=",RECOVERY_SECONDS)

func _collect_materials(node: Node) -> void:
	if node is MeshInstance3D:
		var instance := node as MeshInstance3D
		_register_material(instance.material_override)
		if instance.mesh:
			for i in instance.mesh.get_surface_count():
				_register_material(instance.get_surface_override_material(i))
				_register_material(instance.mesh.surface_get_material(i))
	for child in node.get_children(): _collect_materials(child)

func _register_material(material: Material) -> void:
	if not material is ShaderMaterial: return
	var shader_material := material as ShaderMaterial
	if shader_material.shader != SURFACE and shader_material.shader != DEPTH: return
	var identity := shader_material.get_instance_id()
	if _material_ids.has(identity): return
	_material_ids[identity] = true
	materials.append(shader_material)
	shader_material.set_shader_parameter("vegetation_time",_time_override)
	shader_material.set_shader_parameter("wind_strength",_wind_strength)
	var kind: Variant = shader_material.get_shader_parameter("wind_kind")
	if kind != null and float(kind) > 0.5 and float(kind) < 1.5:
		grass_materials.append(shader_material)

func set_time_override(seconds: float = -1.0) -> void:
	# A nonnegative value freezes wind for same-frame diagnostic comparisons.
	_time_override = seconds
	for material in materials: material.set_shader_parameter("vegetation_time",seconds)

func set_wind_strength(strength: float) -> void:
	_wind_strength = maxf(strength,0.0)
	for material in materials: material.set_shader_parameter("wind_strength",_wind_strength)

func clear_trail() -> void:
	_trail_ages.fill(RECOVERY_SECONDS)
	_has_hero_position = false
	_push_uniforms()

func _process(delta: float) -> void:
	if not is_instance_valid(preview) or not is_instance_valid(preview.hero): return
	for i in TRAIL_COUNT: _trail_ages[i] = minf(_trail_ages[i] + delta,RECOVERY_SECONDS)
	var current: Vector3 = preview.hero.global_position
	if not _has_hero_position:
		_last_hero = current
		_last_stamp = current
		_has_hero_position = true
	var difference := current - _last_hero
	var planar := Vector2(difference.x,difference.z)
	if planar.length() > 0.001: _movement_direction = planar.normalized()
	_stamp_elapsed += delta
	# Review teleports must not leave a streak between unrelated viewpoints.
	if difference.length() > 2.0:
		_trail_ages.fill(RECOVERY_SECONDS)
		_last_stamp = current
		_stamp_elapsed = 0.0
	elif _stamp_elapsed >= STAMP_INTERVAL and current.distance_to(_last_stamp) > 0.10:
		var side := Vector3(-_movement_direction.y,0,_movement_direction.x) * _step_side * 0.065
		_trail_positions[_trail_cursor] = current + side
		_trail_ages[_trail_cursor] = 0.0
		_trail_cursor = (_trail_cursor + 1) % TRAIL_COUNT
		_step_side *= -1.0
		_last_stamp = current
		_stamp_elapsed = 0.0
	_last_hero = current
	_uniform_elapsed += delta
	# Wind uses engine TIME. Only nearby grass needs changing interaction data.
	if _uniform_elapsed >= 1.0/30.0:
		_uniform_elapsed = 0.0
		_push_uniforms()

func _push_uniforms() -> void:
	var points := PackedVector4Array()
	points.resize(TRAIL_COUNT)
	for i in TRAIL_COUNT:
		var remaining := 1.0 - smoothstep(0.0,RECOVERY_SECONDS,_trail_ages[i])
		var position := _trail_positions[i]
		points[i] = Vector4(position.x,position.y,position.z,remaining)
	var current := Vector4.ZERO
	if is_instance_valid(preview) and is_instance_valid(preview.hero):
		var position: Vector3 = preview.hero.global_position
		current = Vector4(position.x,position.y,position.z,1.0)
	for material in grass_materials:
		material.set_shader_parameter("hero_position",current)
		material.set_shader_parameter("movement_direction",_movement_direction)
		material.set_shader_parameter("trample_points",points)
