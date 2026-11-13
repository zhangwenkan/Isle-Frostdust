extends "res://tools/capture_integrated_shore.gd"
func picture(label:String)->void:
	island._update_ground_contact()
	await settle(14)
	await RenderingServer.frame_post_draw
	assert(root.get_texture().get_image().save_png("res://artifacts/coast-junction-refine-review/"+phase+"-"+label+".png")==OK)
	print("JUNCTION_SHOT ",phase," ",label)
