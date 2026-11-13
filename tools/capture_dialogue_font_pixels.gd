extends SceneTree
## Temporary runtime font comparisons; the scene file is not overridden.

const OUT := "res://artifacts/pixel-dialogue-font-review/"
const I_YAN := OUT + "candidates/i-yan.ttf"
var island: Node3D
var reports: Array = []

func _initialize() -> void:
	if not FileAccess.file_exists(I_YAN):
		print("Historical font candidates were removed after the final selection. See artifacts/dialogue-four-font-review/selected/.")
		quit(0)
		return
	call_deferred("run")

func settle(frames: int = 6) -> void:
	for i in frames:
		await process_frame
	await RenderingServer.frame_post_draw

func show_font(path: String, pixel: bool, stem: String, ink_weight: float = 0.0) -> void:
	var font := FontFile.new()
	font.data = FileAccess.get_file_as_bytes(path)
	font.allow_system_fallback = false
	font.antialiasing = TextServer.FONT_ANTIALIASING_NONE if pixel else TextServer.FONT_ANTIALIASING_GRAY
	font.oversampling = 1.0 if pixel else 0.0
	font.subpixel_positioning = TextServer.SUBPIXEL_POSITIONING_DISABLED
	font.hinting = TextServer.HINTING_NONE
	var dialogue: CanvasLayer = island.opening.dialogue
	for text in dialogue.content.pages:
		for character in text:
			if character == "\n": continue
			assert(font.has_char(character.unicode_at(0)))
	dialogue.screen.theme = dialogue.screen.theme.duplicate()
	if ink_weight > 0.0:
		var ink_font := FontVariation.new()
		ink_font.base_font = font
		ink_font.variation_embolden = ink_weight
		dialogue.screen.theme.default_font = ink_font
	else:
		dialogue.screen.theme.default_font = font
	dialogue.body.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST if pixel else CanvasItem.TEXTURE_FILTER_LINEAR
	dialogue.speaker.texture_filter = dialogue.body.texture_filter
	await settle()
	assert(dialogue.body.get_content_height() <= dialogue.body.size.y)
	assert(root.get_texture().get_image().save_png(OUT + stem + ".png") == OK)
	reports.append({"file":stem,"font":font.get_font_name(),"pixel":pixel,"font_size":32,
		"oversampling":font.oversampling,"antialiasing":font.antialiasing,"ink_weight":ink_weight,"body_height":dialogue.body.get_content_height()})
	print("FONT_PREVIEW ",stem)

func run() -> void:
	root.content_scale_size = Vector2i(1280,720)
	root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	root.size = Vector2i(1280,720)
	island = load("res://scenes/island.tscn").instantiate()
	root.add_child(island)
	current_scene = island
	await island.opening.dialogue.dialogue_started
	await settle(40)
	await show_font(I_YAN,false,"i-yan-smooth")
	await show_font(I_YAN,true,"i-yan-pixel")
	var variant := OUT + "candidates/huiwen-variant/DyslexicKaiMono-Regular.ttf"
	if FileAccess.file_exists(variant):
		await show_font(variant,false,"huiwen-smooth")
		await show_font(variant,true,"huiwen-pixel")
		await show_font(variant,true,"huiwen-pixel-ink",0.5)
	var file := FileAccess.open(OUT + "pixel-render-verification.json",FileAccess.WRITE)
	file.store_string(JSON.stringify(reports,"  "))
	quit(0)
