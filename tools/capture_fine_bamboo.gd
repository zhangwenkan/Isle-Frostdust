extends "res://tools/capture_pixel_bamboo.gd"
func pixel_shot(label: String) -> void:
	island._update_ground_contact()
	await settle(24)
	await RenderingServer.frame_post_draw
	assert(root.get_texture().get_image().save_png("res://artifacts/bamboo-fine-atlas-review/"+phase+"-"+label+".png")==OK)
	print("FINE_BAMBOO_SHOT ",phase," ",label)
