extends Node
## Movement and camera only; all visible geometry comes from the Blender GLB.
const WALK_FRAMES := preload("res://assets/characters/green_three_walk/swordsman_walk.tres")
const SPEED := 2.55
const MAX_STEP := 0.32
const FOOT_CLEARANCE := 0.012
const CAMERA_OFFSET := Vector3(2.4, 5.2, 13.6)
var scene: Node
var velocity := Vector2.ZERO
var facing := "right"
var flipped := false
var animation_clock := 0.0
var follow := true
var camera_anchor := Vector3.ZERO
var camera_lead := Vector3.ZERO
var camera_offset := CAMERA_OFFSET
var body_shape := CapsuleShape3D.new()
var ground_count := 0
var blocker_count := 0
var ready_for_physics := false
var hud: Label

func setup(preview: Node, model: Node3D) -> void:
	scene = preview
	body_shape.radius = 0.16
	body_shape.height = 1.55
	_add_imported_collisions(model)
	_hud()
	snap_camera()
	print("CAVERN_PLAYER_SETUP ground=", ground_count, " blockers=", blocker_count)

func _add_imported_collisions(node: Node) -> void:
	# Visit original children before adding collision children.
	for child in node.get_children(): _add_imported_collisions(child)
	if not node is MeshInstance3D: return
	var mesh_node := node as MeshInstance3D
	if mesh_node.layers != 1: return # Character occlusion proxies are render-only.
	var label := String(mesh_node.name)
	var floor_mesh := label.begins_with("Path_") or label.begins_with("Step_") or label.begins_with("Plank_Bridge_") or label in ["Grass_Left_Terrace", "Grass_Right_Terrace", "Grass_Upper_Forest", "Sand_Cove", "Sand_Wet_Edge"]
	var blocker_mesh := label.begins_with("Rock_Cliff_") or label.begins_with("Rock_Cave_") or label.begins_with("Bamboo_Stem_") or label.begins_with("Wood_Tree_") or label.begins_with("LiveTreeBranch_") or label.begins_with("Wood_Bridge_Post_") or label.begins_with("CaveInterior_")
	if label.contains("Buried"): blocker_mesh = false
	if not floor_mesh and not blocker_mesh: return
	var body := StaticBody3D.new()
	body.name = "ImportedCollision"
	body.collision_layer = 1 if floor_mesh else 2
	body.collision_mask = 0
	var shape := CollisionShape3D.new()
	shape.shape = mesh_node.mesh.create_trimesh_shape()
	body.add_child(shape)
	mesh_node.add_child(body)
	if floor_mesh: ground_count += 1
	else: blocker_count += 1

func _floor_at(point: Vector3) -> Dictionary:
	var query := PhysicsRayQueryParameters3D.create(point + Vector3.UP * MAX_STEP, point - Vector3.UP * (MAX_STEP + .10), 1)
	var hit: Dictionary = scene.world.get_world_3d().direct_space_state.intersect_ray(query)
	if not hit.is_empty() and hit.normal.y < .55: return {}
	return hit

func _foot_floor(point: Vector3) -> Dictionary:
	var center := _floor_at(point)
	if not center.is_empty(): return center
	# A foot can straddle an authored seam only with support on BOTH sides.
	# This spans board gaps and the 11 cm stair-top joint, but never a cliff edge.
	for offset in [Vector3(.13,0,0), Vector3(0,0,.13)]:
		var a := _floor_at(point + offset)
		var b := _floor_at(point - offset)
		if not a.is_empty() and not b.is_empty():
			return a if a.position.y > b.position.y else b
	return {}

func supported_floor(point: Vector3) -> Dictionary:
	var center := _foot_floor(point)
	if center.is_empty(): return {}
	# Do not allow the body center to walk over cliffs, water, or a stair side.
	var supported := 0
	for offset in [Vector3(.13,0,0), Vector3(-.13,0,0), Vector3(0,0,.13), Vector3(0,0,-.13)]:
		if not _foot_floor(point + offset).is_empty(): supported += 1
	if supported < 3: return {}
	return center

func _can_stand(point: Vector3) -> bool:
	var query := PhysicsShapeQueryParameters3D.new()
	query.shape = body_shape
	query.transform = Transform3D(Basis.IDENTITY, point + Vector3(0,.91,0))
	query.collision_mask = 2
	query.margin = .015
	return scene.world.get_world_3d().direct_space_state.intersect_shape(query,1).is_empty()

func _try_move(offset: Vector3) -> bool:
	if offset.length_squared() < .0000001: return false
	var candidate: Vector3 = scene.hero.position + offset
	var hit := supported_floor(candidate)
	if hit.is_empty(): return false
	candidate.y = hit.position.y + FOOT_CLEARANCE
	if not _can_stand(candidate): return false
	scene.hero.position = candidate
	return true

func _physics_process(delta: float) -> void:
	if not scene or scene.capture or scene.motion: return
	if not ready_for_physics:
		var hit := supported_floor(scene.hero.position)
		if hit.is_empty(): return
		scene.hero.position.y = hit.position.y + FOOT_CLEARANCE
		ready_for_physics = true
		snap_camera()
	var input := Vector2(
		Input.get_action_strength("move_right") + Input.get_action_strength("ui_right") - Input.get_action_strength("move_left") - Input.get_action_strength("ui_left"),
		Input.get_action_strength("move_down") + Input.get_action_strength("ui_down") - Input.get_action_strength("move_up") - Input.get_action_strength("ui_up")
	).limit_length()
	velocity = velocity.move_toward(input * SPEED, (20.0 if input == Vector2.ZERO else 14.0) * delta)
	var before: Vector3 = scene.hero.position
	# Substeps keep ledge checks valid even on a slow frame.
	var travel := Vector3(velocity.x,0,velocity.y) * delta
	var pieces := maxi(1, ceili(travel.length() / .035))
	travel /= pieces
	for i in pieces:
		if not _try_move(travel):
			_try_move(Vector3(travel.x,0,0))
			_try_move(Vector3(0,0,travel.z))
	var moved: Vector3 = scene.hero.position - before
	var planar_speed := Vector2(moved.x,moved.z).length() / maxf(delta,.001)
	_animate(moved, planar_speed, delta)
	if planar_speed > .05 and not follow:
		follow = true
		snap_camera()

func _animate(moved: Vector3, actual_speed: float, delta: float) -> void:
	var walking := actual_speed > .05
	if walking:
		if absf(moved.x) >= absf(moved.z) * .75:
			facing = "right"
			flipped = moved.x < 0
		else:
			facing = "up" if moved.z < 0 else "down"
			flipped = false
		animation_clock += delta * clampf(actual_speed / SPEED, .35, 1.0)
	else: animation_clock = 0.0
	var anim := StringName(("walk_" if walking else "idle_") + facing)
	var index := int(animation_clock * WALK_FRAMES.get_animation_speed(anim)) % WALK_FRAMES.get_frame_count(anim)
	scene.hero.texture = WALK_FRAMES.get_frame_texture(anim,index)
	scene.hero.flip_h = flipped
	scene.hero_shadow.texture = scene.hero.texture
	scene.hero_shadow.flip_h = flipped

func snap_camera() -> void:
	camera_anchor = scene.hero.position + Vector3(0,1.15,0)
	camera_lead = Vector3.ZERO
	update_camera(0.0, true)

func update_camera(delta: float, snap := false) -> void:
	if not follow: return
	var target: Vector3 = scene.hero.position + Vector3(0,1.15,0)
	var blend := 1.0 if snap else 1.0 - exp(-5.5 * delta)
	# Foot height follows individual treads; camera elevation eases across risers.
	camera_anchor = camera_anchor.lerp(target,blend)
	var look_ahead := Vector3(velocity.x/SPEED*.65,0,velocity.y/SPEED*.30)
	camera_lead = camera_lead.lerp(look_ahead,blend)
	# Lower toward the mouth when entering; the exterior overhead view sees roof.
	var cave_weight := smoothstep(-2.5,-6.4,scene.hero.position.z) * smoothstep(9.5,10.6,scene.hero.position.x)
	var desired_offset := CAMERA_OFFSET.lerp(Vector3(.35,1.25,13.8),cave_weight)
	camera_offset = camera_offset.lerp(desired_offset,blend)
	scene.camera.position = camera_anchor + camera_lead + camera_offset
	scene.camera.look_at(camera_anchor + camera_lead,Vector3.UP)
	scene.camera.fov = 38.0

func _hud() -> void:
	var layer := CanvasLayer.new()
	add_child(layer)
	hud = Label.new()
	hud.text = "WASD / 方向键 移动    F 跟随人物    1–3 查看场景    Tab 隐藏提示"
	hud.position = Vector2(22,18)
	hud.add_theme_font_size_override("font_size",18)
	hud.add_theme_color_override("font_color",Color("eee9d8"))
	hud.add_theme_color_override("font_shadow_color",Color(0.08,.12,.10,.9))
	hud.add_theme_constant_override("shadow_offset_x",1)
	hud.add_theme_constant_override("shadow_offset_y",2)
	hud.mouse_filter = Control.MOUSE_FILTER_IGNORE
	layer.add_child(hud)
