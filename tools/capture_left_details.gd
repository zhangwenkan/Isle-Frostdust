extends SceneTree
const OUT="res://artifacts/left-finish-review/"
var island:Node3D
func _initialize():call_deferred("run")
func run():
	root.size=Vector2i(1280,720);root.content_scale_size=Vector2i(1280,720)
	island=load("res://scenes/layered_island.tscn").instantiate();root.add_child(island);current_scene=island
	island.manual_control=false;island.hud.hide();island.set_process(false)
	for row in [["stair_bottom","stair_top",.54,"stonework"],["forest_step1","forest_mid",.55,"bamboo"]]:
		island.set_route_sample(row[0],row[1],row[2]);island._update_occluders(1.)
		island.camera.fov=11.0
		for i in 6:await process_frame
		await RenderingServer.frame_post_draw
		root.get_texture().get_image().save_jpg(OUT+"detail-"+row[3]+".jpg",.90)
	print("LEFT_DETAIL_DONE");quit()
