extends SceneTree
## Static previews and short functional checks only; no video recording.

var output_directory := "res://artifacts/pixel-dialogue-review/"
var island: Node3D
var reports: Array = []

func _initialize() -> void:
	for argument in OS.get_cmdline_user_args():
		if argument.begins_with("--dialogue-output="):
			output_directory = argument.trim_prefix("--dialogue-output=").trim_suffix("/") + "/"
	DirAccess.make_dir_recursive_absolute(output_directory)
	call_deferred("run")

func settle(frames: int = 8) -> void:
	for i in frames:
		await process_frame
	await RenderingServer.frame_post_draw

func key(code: Key) -> void:
	for pressed in [true, false]:
		var event := InputEventKey.new()
		event.keycode = code
		event.physical_keycode = code
		event.pressed = pressed
		Input.parse_input_event(event)

func click_at(point: Vector2) -> void:
	for pressed in [true, false]:
		var event := InputEventMouseButton.new()
		event.button_index = MOUSE_BUTTON_LEFT
		event.position = point
		event.pressed = pressed
		Input.parse_input_event(event)

func shot(label: String) -> void:
	var dialogue: CanvasLayer = island.opening.dialogue
	var card: Rect2 = dialogue.card.get_global_rect()
	assert(absf(card.get_center().x - dialogue.screen.size.x * 0.5) < 1.0)
	assert(absf(card.end.y - dialogue.screen.size.y + 12.0) < 1.0)
	assert(dialogue.body.get_content_height() <= dialogue.body.size.y)
	assert(dialogue.portrait.get_global_rect().position.y >= 0.0)
	assert(dialogue.card.find_children("*", "Label", true, false).size() == 1)
	var button: TextureButton = dialogue.advance_button
	assert(button.texture_normal.resource_path.ends_with("cloud_advance.png"))
	var font: Font = dialogue.body.get_theme_font("normal_font")
	var speaker_font: Font = dialogue.speaker.get_theme_font("font")
	var base_font: Font = font.base_font if font is FontVariation else font
	for character in dialogue.body.text:
		if character != "\n":
			assert(font.has_char(character.unicode_at(0)))
	for character in dialogue.speaker.text:
		assert(speaker_font.has_char(character.unicode_at(0)))
	reports.append({"shot": label, "card": str(card), "viewport": str(dialogue.screen.size),
		"body_content_height": dialogue.body.get_content_height(), "body_space": dialogue.body.size.y,
		"font": font.get_font_name(), "font_source": font.resource_path,
		"speaker_font":speaker_font.get_font_name(),
		"embolden":font.variation_embolden if font is FontVariation else 0.0,
		"antialiasing": base_font.antialiasing,
		"oversampling": base_font.oversampling})
	assert(root.get_texture().get_image().save_png(output_directory + label + ".png") == OK)
	print("PIXEL_DIALOGUE_SHOT ", label)

func run() -> void:
	root.content_scale_size = Vector2i(1280, 720)
	root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	root.size = Vector2i(1280, 720)
	island = load("res://scenes/island.tscn").instantiate()
	root.add_child(island)
	current_scene = island
	await island.opening.dialogue.dialogue_started
	var dialogue: CanvasLayer = island.opening.dialogue
	await settle(40)
	assert(dialogue.is_dialogue_active())
	assert(island.opening.is_input_locked())
	shot("page-1-1280x720")
	click_at(dialogue.advance_button.get_global_rect().get_center())
	await settle(40)
	assert(dialogue._page == 1)
	shot("page-2-1280x720")
	# Use actual canvas scaling, including the project's expand aspect.
	root.size = Vector2i(1024, 768)
	await settle()
	shot("layout-1024x768")
	root.size = Vector2i(1920, 1080)
	await settle()
	shot("layout-1920x1080")
	root.size = Vector2i(960, 540)
	await settle()
	shot("layout-960x540")
	root.size = Vector2i(1280, 720)
	await settle()
	key(KEY_ENTER)
	await settle()
	assert(not dialogue.is_dialogue_active())
	assert(not island.opening.is_input_locked())
	assert(island.hud.visible)
	key(KEY_R)
	await island.opening.dialogue.dialogue_started
	await settle(8)
	# fixed-fps advances game time faster than the wall-clock opening guard.
	while Time.get_ticks_msec() < dialogue._accept_after_msec:
		await process_frame
	assert(dialogue._page == 0)
	# Clicking the paper during typewriter reveal first completes that page.
	click_at(dialogue.body.get_global_rect().get_center())
	await settle(2)
	assert(dialogue.body.visible_characters == dialogue.body.get_total_character_count())
	assert(dialogue._page == 0)
	key(KEY_SPACE)
	await settle(40)
	assert(dialogue._page == 1)
	key(KEY_SPACE)
	await settle()
	assert(not island.opening.is_input_locked())
	var report := {"static_only": true, "mouse_icon_page": true, "keyboard_finish": true,
		"paper_click_complete_text": true, "replay": true, "player_unlock": true, "layouts": reports}
	var file := FileAccess.open(output_directory + "verification.json", FileAccess.WRITE)
	file.store_string(JSON.stringify(report, "  "))
	print("PIXEL_DIALOGUE_VERIFIED ", JSON.stringify(report))
	quit(0)
