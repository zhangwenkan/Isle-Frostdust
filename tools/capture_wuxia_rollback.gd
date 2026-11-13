extends "res://tools/capture_coastal_water.gd"

func save_view(label: String) -> void:
	assert(island.find_child("Wuxia_Tingchao_Waymarker", true, false) == null)
	assert(island.find_child("Wuxia_Tingchao_Inscription", true, false) == null)
	await settle(8)
	await RenderingServer.frame_post_draw
	var path := "res://artifacts/wuxia-style-review/rollback/restored-" + label + ".png"
	assert(root.get_texture().get_image().save_png(path) == OK)
	print("ROLLBACK_CAPTURE ", label, " no marker; current speed=", island.HERO_SPEED)
