extends "res://tools/capture_pixel_bamboo.gd"
func pixel_shot(label: String) -> void:
	island._update_ground_contact()
	await settle(28)
	await RenderingServer.frame_post_draw
	assert(root.get_texture().get_image().save_png("res://artifacts/forest-rock-root-review/"+phase+"-"+label+".png")==OK)
	print("FOREST_ROOT_SHOT ",phase," ",label)
