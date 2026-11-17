extends SceneTree
const OUT="res://artifacts/spatial-foundation-review/"
var island:Node3D
var prefix="review"
func _initialize():call_deferred("run")
func run():
	root.size=Vector2i(1280,720);root.content_scale_size=Vector2i(1280,720)
	if not OS.get_cmdline_user_args().is_empty():prefix=OS.get_cmdline_user_args()[0]
	island=load("res://scenes/layered_island.tscn").instantiate();root.add_child(island);current_scene=island
	island.manual_control=false;island.hud.hide()
	for i in 12:await process_frame
	var shots=[]
	for row in [["beach","stair_bottom",0.,"beach"],["stair_bottom","stair_top",.5,"stairs"],["junction","bridge_left",.5,"platform"],["bridge_left","bridge_right",.5,"bridge"],["cave_mouth","cave_end",1.,"cave"],["forest_step1","forest_mid",.7,"forest_mid"],["forest_landing","forest_end",1.,"forest_end"]]:
		island.set_route_sample(row[0],row[1],row[2]);island.facing="up" if row[3] in ["stairs","forest_mid","forest_end"] else "right";island._update_actor(false,0.,true)
		island._update_occluders(2.)
		for i in 3:await process_frame
		await RenderingServer.frame_post_draw
		root.get_texture().get_image().save_jpg(OUT+prefix+"-"+row[3]+".jpg",.84)
		shots.append({"label":row[3],"position":island.hero.position,"foot":island.camera.unproject_position(island.hero.position),"ground":island.last_ground,"camera":island.camera.position})
	var f=FileAccess.open(OUT+prefix+"-shots.json",FileAccess.WRITE);f.store_string(JSON.stringify(shots,"  "))
	print("SPATIAL_SHOTS_DONE");quit()
