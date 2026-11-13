extends "res://tools/capture_wuxia_dialogue.gd"

var layout_reports: Array = []


func settle(frames: int = 8) -> void:
	for i in frames:
		await process_frame
	await RenderingServer.frame_post_draw


func run() -> void:
	root.content_scale_size = Vector2i(1280, 720)
	root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	root.size = Vector2i(1280, 720)
	island = load("res://scenes/island.tscn").instantiate()
	root.add_child(island)
	current_scene = island
	await island.opening.dialogue.dialogue_started
	await settle(40)
	var dialogue: CanvasLayer = island.opening.dialogue
	var sword: TextureButton = dialogue.advance_button
	layout_reports.append(verify_dialogue_layout())
	# This override only lives in the review process; no candidate is committed.
	for choice in ["A", "B", "C", "D", "E", "F"]:
		var image := Image.load_from_file(OUT + "icon-candidates/prepared/" + choice + "-button.png")
		assert(image != null)
		var texture := ImageTexture.create_from_image(image)
		sword.texture_normal = texture
		sword.texture_hover = texture
		sword.texture_pressed = texture
		sword.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
		await settle()
		shot("choice-" + choice)
	# Verify changed TextureButton click path plus keyboard and recovery.
	click_continue()
	await settle(36)
	assert(dialogue._page == 1)
	shot("traditional-page-2")
	layout_reports.append(verify_dialogue_layout())
	key(KEY_ENTER)
	await settle()
	assert(not dialogue.is_dialogue_active())
	assert(not island.opening.is_input_locked())
	key(KEY_R)
	await island.opening.dialogue.dialogue_started
	await settle(40)
	# Preserve original font/portrait proportions when the UI scale changes.
	root.content_scale_size = Vector2i(1024, 768)
	root.size = Vector2i(1024, 768)
	await settle()
	layout_reports.append(verify_dialogue_layout())
	shot("layout-1024x768")
	var file := FileAccess.open(OUT + "traditional-layout-verification.json", FileAccess.WRITE)
	file.store_string(JSON.stringify({"candidates":6,"production_icon_selected":false,"mouse_and_keyboard":true,"reports":layout_reports}, "  "))
	print("TRADITIONAL_UI_VERIFIED ", JSON.stringify(layout_reports))
	quit(0)
