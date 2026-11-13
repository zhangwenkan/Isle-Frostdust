extends "res://tools/capture_four_dialogue_fonts.gd"
## Normal and synthesized bold KaiTi, without changing the production theme.

func run_capture() -> void:
	var ink_weight := 0.65
	var output_stem := "06-kaiti-bold-pixel"
	for argument in OS.get_cmdline_user_args():
		if argument == "--medium":
			ink_weight = 0.325
			output_stem = "07-kaiti-medium-pixel"
	root.content_scale_size = Vector2i(1280,720)
	root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	root.size = Vector2i(1280,720)
	island = load("res://scenes/island.tscn").instantiate()
	root.add_child(island)
	current_scene = island
	await island.opening.dialogue.dialogue_started
	await settle(40)
	island.process_mode = Node.PROCESS_MODE_DISABLED
	island.hero.pause()
	control_time(island)
	freeze_material(island.atmosphere.mountain_cloud_material,"fog")
	freeze_material(island.background_comparison.original_sky,"sky")
	freeze_material(island.background_comparison.comparison_sky,"sky")
	set_time(6.0)
	await settle(30)
	var base := load_font("C:/Windows/Fonts/simkai.ttf",true)
	if ink_weight == 0.65:
		await capture_font(base,true,"楷体原字重＋固定像素","05-kaiti-normal-weight")
	var bold := FontVariation.new()
	bold.base_font = base
	bold.variation_embolden = ink_weight
	var dialogue: CanvasLayer = island.opening.dialogue
	dialogue.screen.theme.default_font = bold
	dialogue.body.add_theme_font_override("normal_font", bold)
	await settle(10)
	await RenderingServer.frame_post_draw
	assert(dialogue.body.get_content_height() <= dialogue.body.size.y)
	assert(root.get_texture().get_image().save_png(FONT_REVIEW + output_stem + ".png") == OK)
	var file := FileAccess.open(FONT_REVIEW + output_stem + "-verification.json",FileAccess.WRITE)
	file.store_string(JSON.stringify({"font":"KaiTi","variation_embolden":ink_weight,
		"fixed_pixel":true,"body_size":32,"speaker_size":30,
		"body_height":dialogue.body.get_content_height(),"body_space":dialogue.body.size.y,
		"production_unchanged":true,"static_only":true},"  "))
	print("KAITI_BOLD_CAPTURED")
	quit(0)
