extends Node2D

const PlayerController = preload("res://scripts/player.gd")
const TILE_SIZE := 32

@onready var player: PlayerController = $World/Player
@onready var safe_area: MarginContainer = $Hud/Root/SafeArea

func _ready() -> void:
	get_viewport().size_changed.connect(_update_layout)
	_update_layout()
	player.position = player.movement_bounds.get_center()

func _update_layout() -> void:
	var view_size := get_viewport_rect().size
	player.set_movement_bounds(Rect2(16, 96, view_size.x - 32, view_size.y - 128))
	_update_safe_area()
	queue_redraw()

func _update_safe_area() -> void:
	var margins := Vector4(24, 16, 24, 16)
	if OS.get_name() == "Android":
		# 把屏幕安全区换算成逻辑坐标，避开挖孔和系统保留区域。
		var screen_safe_area := Rect2(DisplayServer.get_display_safe_area())
		if screen_safe_area.has_area():
			var viewport_safe_area := get_viewport().get_screen_transform().affine_inverse() * screen_safe_area
			var view_size := get_viewport_rect().size
			margins.x = maxf(margins.x, viewport_safe_area.position.x)
			margins.y = maxf(margins.y, viewport_safe_area.position.y)
			margins.z = maxf(margins.z, view_size.x - viewport_safe_area.end.x)
			margins.w = maxf(margins.w, view_size.y - viewport_safe_area.end.y)

	safe_area.add_theme_constant_override("margin_left", ceili(margins.x))
	safe_area.add_theme_constant_override("margin_top", ceili(margins.y))
	safe_area.add_theme_constant_override("margin_right", ceili(margins.z))
	safe_area.add_theme_constant_override("margin_bottom", ceili(margins.w))

func _draw() -> void:
	# 根据实际视口扩展占位地图，折叠切换或调整窗口后重新绘制。
	var view_size := get_viewport_rect().size
	var shore_y := roundf(view_size.y * 0.73)
	draw_rect(Rect2(Vector2.ZERO, view_size), Color("101722"))

	for x in range(0, ceili(view_size.x), TILE_SIZE):
		draw_line(Vector2(x, 96), Vector2(x, shore_y), Color("172536"), 1.0)
	for y in range(96, ceili(shore_y), TILE_SIZE):
		draw_line(Vector2(0, y), Vector2(view_size.x, y), Color("172536"), 1.0)

	# 远山顶点采用相对坐标，以适应内屏和外屏的不同长宽比。
	var mountain := PackedVector2Array([
		Vector2(0, 0.52), Vector2(0.1125, 0.37), Vector2(0.194, 0.48),
		Vector2(0.325, 0.27), Vector2(0.453, 0.46), Vector2(0.588, 0.32),
		Vector2(0.719, 0.51), Vector2(0.838, 0.39), Vector2(1, 0.53),
		Vector2(1, 0.73), Vector2(0, 0.73)
	])
	for index in mountain.size():
		mountain[index] = (mountain[index] * view_size).round()
	draw_colored_polygon(mountain, Color("1d2b3b"))

	draw_rect(Rect2(0, shore_y, view_size.x, view_size.y - shore_y), Color("182f32"))
	draw_line(Vector2(0, shore_y), Vector2(view_size.x, shore_y), Color("325552"), 1.0)
	draw_rect(Rect2(16, 96, view_size.x - 32, view_size.y - 128), Color("5d8a7a", 0.28), false, 1.0)
