extends "res://tools/capture_cloud_water.gd"
## Four static game captures. Font overrides are local to this review process.

const FONT_REVIEW := "res://artifacts/dialogue-four-font-review/"
const NANO_SOURCE := "C:/Users/51440/Desktop/纳米点望宋_100font/NanoDyongWongSong.ttf"
var font_reports: Array = []

func _initialize() -> void:
	call_deferred("run_capture")

func load_font(path: String, fixed_pixel: bool) -> FontFile:
	var font := FontFile.new()
	font.data = FileAccess.get_file_as_bytes(path)
	font.allow_system_fallback = false
	if fixed_pixel:
		font.antialiasing = TextServer.FONT_ANTIALIASING_NONE
		font.oversampling = 1.0
		font.subpixel_positioning = TextServer.SUBPIXEL_POSITIONING_DISABLED
		font.hinting = TextServer.HINTING_NONE
	# Nano uses the engine's normal grayscale AA, automatic oversampling and
	# hinting defaults, without the fixed-pixel treatment used for the others.
	return font

func capture_font(font: FontFile, fixed_pixel: bool, label: String, filename: String) -> void:
	var dialogue: CanvasLayer = island.opening.dialogue
	for page in dialogue.content.pages:
		for character in page + dialogue.content.speaker_name:
			if character != "\n":
				assert(font.has_char(character.unicode_at(0)), label + ": missing " + character)
	dialogue.screen.theme = dialogue.screen.theme.duplicate()
	dialogue.screen.theme.default_font = font
	dialogue.body.add_theme_font_override("normal_font", font)
	dialogue.body.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST if fixed_pixel else CanvasItem.TEXTURE_FILTER_LINEAR
	dialogue.speaker.texture_filter = dialogue.body.texture_filter
	await settle(10)
	await RenderingServer.frame_post_draw
	assert(dialogue.body.get_content_height() <= dialogue.body.size.y)
	assert(root.get_texture().get_image().save_png(FONT_REVIEW + filename + ".png") == OK)
	font_reports.append({"label":label, "file":filename + ".png", "font":font.get_font_name(),
		"body_size":dialogue.body.get_theme_font_size("normal_font_size"),
		"speaker_size":dialogue.speaker.get_theme_font_size("font_size"),
		"antialiasing":font.antialiasing, "oversampling":font.oversampling,
		"hinting":font.hinting, "subpixel_positioning":font.subpixel_positioning,
		"fixed_pixel":fixed_pixel, "body_height":dialogue.body.get_content_height(),
		"all_dialogue_glyphs_present":true, "system_fallback":font.allow_system_fallback})
	print("FOUR_FONT_CAPTURE ", label)

func run_capture() -> void:
	DirAccess.make_dir_recursive_absolute(FONT_REVIEW)
	root.content_scale_size = Vector2i(1280,720)
	root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	root.size = Vector2i(1280,720)
	island = load("res://scenes/island.tscn").instantiate()
	root.add_child(island)
	current_scene = island
	await island.opening.dialogue.dialogue_started
	await settle(40)
	# Lock the existing gameplay camera, actor pose and environment for all four.
	island.process_mode = Node.PROCESS_MODE_DISABLED
	island.hero.pause()
	control_time(island)
	freeze_material(island.atmosphere.mountain_cloud_material,"fog")
	freeze_material(island.background_comparison.original_sky,"sky")
	freeze_material(island.background_comparison.comparison_sky,"sky")
	set_time(6.0)
	await settle(30)
	var current_font: FontFile = island.opening.dialogue.speaker.get_theme_font("font")
	assert(current_font.get_font_name() == "I.Ngaan")
	await capture_font(load_font("C:/Windows/Fonts/simsun.ttc",true),true,"宋体＋固定像素","01-simsun-fixed-pixel")
	await capture_font(load_font("C:/Windows/Fonts/simkai.ttf",true),true,"楷体＋固定像素","02-kaiti-fixed-pixel")
	await capture_font(load_font(NANO_SOURCE,false),false,"纳米点望宋（普通渲染）","03-nano-dyong-wong-song")
	await capture_font(current_font,true,"当前一點顏體＋固定像素","04-i-ngaan-current")
	var file := FileAccess.open(FONT_REVIEW + "verification.json",FileAccess.WRITE)
	file.store_string(JSON.stringify({"size":str(root.size),"production_font_unchanged":true,
		"static_only":true,"same_camera_and_text":true,"font_reports":font_reports},"  "))
	quit(0)
