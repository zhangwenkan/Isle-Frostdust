extends Node2D

@onready var actor: AnimatedSprite2D = $Actor
var elapsed := 0.0
var running := true
var travel := false
var speed := 128.22
var ground := 305.0
var actor_scale := 0.75
var screenshot_frames := 0
var screenshot_path := ""
var current_label: Label

func _ready() -> void:
    actor.centered = false
    actor.offset = Vector2(-128, -362)
    actor.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
    actor.scale = Vector2.ONE * actor_scale
    actor.play("walk_right")
    current_label = Label.new()
    current_label.position = Vector2(14, 8)
    current_label.add_theme_font_size_override("font_size", 13)
    add_child(current_label)
    for arg in OS.get_cmdline_user_args():
        if arg.begins_with("--capture="):
            screenshot_path = arg.trim_prefix("--capture=")
    _update_actor()

func _process(delta: float) -> void:
    if running:
        elapsed += delta
    _update_actor()
    current_label.text = "H3 walk / fixed ground / natural bob
Space: pause   Arrows: frame   M: movement   +/-: speed   R: reset
Frame %02d/%02d   Move %.0f px/s   %s" % [actor.frame + 1, actor.sprite_frames.get_frame_count("walk_right"), speed, "MOVE" if travel else "IN PLACE"]
    queue_redraw()
    if not screenshot_path.is_empty():
        screenshot_frames += 1
        if screenshot_frames == 45:
            await RenderingServer.frame_post_draw
            var err := get_viewport().get_texture().get_image().save_png(screenshot_path)
            print("Walk screenshot saved: ", err)
            get_tree().quit(err)

func _update_actor() -> void:
    var x := 320.0
    if travel:
        x = 90.0 + fposmod(elapsed * speed, 460.0)
    actor.position = Vector2(roundf(x), ground)

func _unhandled_key_input(event: InputEvent) -> void:
    if not event is InputEventKey or not event.pressed or event.echo:
        return
    match event.keycode:
        KEY_SPACE:
            running = not running
            if running: actor.play("walk_right")
            else: actor.pause()
        KEY_LEFT, KEY_RIGHT:
            running = false
            actor.pause()
            var step := 1 if event.keycode == KEY_RIGHT else -1
            actor.frame = posmod(actor.frame + step, actor.sprite_frames.get_frame_count("walk_right"))
        KEY_M:
            travel = not travel
            elapsed = 0.0
        KEY_EQUAL, KEY_PLUS, KEY_KP_ADD:
            speed += 5.0
        KEY_MINUS, KEY_KP_SUBTRACT:
            speed = maxf(0.0, speed - 5.0)
        KEY_R:
            elapsed = 0.0
            actor.frame = 0

func _draw() -> void:
    draw_rect(Rect2(0, 0, 640, 360), Color("17212e"))
    for x in range(0, 641, 24):
        draw_line(Vector2(x, 70), Vector2(x, ground), Color("263343"))
    for y in range(89, 306, 24):
        draw_line(Vector2(0, y), Vector2(640, y), Color("263343"))
    draw_line(Vector2(0, ground), Vector2(640, ground), Color("61d5a0"), 1.0)
    draw_line(actor.position + Vector2(0, 2), actor.position + Vector2(0, 14), Color("f2c778"), 1.0)
