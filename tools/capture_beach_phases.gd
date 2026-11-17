extends SceneTree
const OUT="res://artifacts/beach-swash-review/"
var island:Node3D
func _initialize():call_deferred("run")
func run():
	root.size=Vector2i(1280,720);root.content_scale_size=Vector2i(1280,720)
	island=load("res://scenes/layered_island.tscn").instantiate();root.add_child(island);current_scene=island
	island.manual_control=false;island.hud.hide();island.set_process(false)
	island.set_route_sample("beach","stair_bottom",0.)
	island._update_occluders(1.)
	var sand=island.get_node("World").find_child("WALK_Left_Beach",true,false)
	var film=island.get_node("World").find_child("Beach_Swash_Film",true,false)
	for row in [[.3,"incoming"],[3.1,"runup"],[5.8,"backwash"]]:
		sand.material_override.set_shader_parameter("shoreline_time_override",row[0])
		film.material_override.set_shader_parameter("shoreline_time_override",row[0])
		for i in 5:await process_frame
		await RenderingServer.frame_post_draw
		root.get_texture().get_image().save_jpg(OUT+"phase-"+row[1]+".jpg",.88)
	# Inspect the actual dry substrate independently of the water overlay.
	film.hide();island.get_node("World").find_child("Sea_Surface",true,false).hide()
	for i in 3:await process_frame
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_jpg(OUT+"substrate-inspection.jpg",.88)
	print("BEACH_PHASES_DONE");quit()
