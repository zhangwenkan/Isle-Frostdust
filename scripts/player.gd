extends CharacterBody2D

@export var move_speed := 160.0

var facing := Vector2.DOWN
var movement_bounds := Rect2(16, 96, 608, 232)

func set_movement_bounds(bounds: Rect2) -> void:
	movement_bounds = bounds
	_clamp_to_bounds()

func _clamp_to_bounds() -> void:
	# 保留完整角色的空间；占位像素角色在场景中放大为两倍。
	var padding := Vector2(7, 12) * scale
	position.x = clampf(position.x, movement_bounds.position.x + padding.x, movement_bounds.end.x - padding.x)
	position.y = clampf(position.y, movement_bounds.position.y + padding.y, movement_bounds.end.y - padding.y)

func _physics_process(_delta: float) -> void:
	var input_vector := Input.get_vector("move_left", "move_right", "move_up", "move_down")
	velocity = input_vector * move_speed

	if input_vector.length_squared() > 0.0:
		facing = input_vector

	move_and_slide()
	_clamp_to_bounds()
	queue_redraw()

func _draw() -> void:
	# 所有尺寸都对齐整数像素，后续替换 Sprite2D 时可直接保留碰撞体。
	draw_rect(Rect2(-7, 6, 14, 3), Color(0.03, 0.07, 0.09, 0.45))
	draw_rect(Rect2(-5, -8, 10, 8), Color("d5a36a"))
	draw_rect(Rect2(-6, -9, 12, 3), Color("251b24"))
	draw_rect(Rect2(-7, -7, 3, 5), Color("251b24"))
	draw_rect(Rect2(-5, 0, 10, 9), Color("31566a"))
	draw_rect(Rect2(-6, 1, 12, 3), Color("c64d46"))
	draw_rect(Rect2(-5, 9, 4, 3), Color("171c2c"))
	draw_rect(Rect2(1, 9, 4, 3), Color("171c2c"))

	# 用一个亮色像素提示朝向，方便验证输入是否生效。
	var look := facing.normalized() * 5.0
	draw_rect(Rect2(look.x - 1.0, look.y - 1.0, 2.0, 2.0), Color("f4d58d"))
