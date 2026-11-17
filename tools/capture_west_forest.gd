extends SceneTree
const OUT="res://artifacts/bamboo-west-extension-review/"
var island:Node3D
var prefix="review"
func _initialize():call_deferred("run")
func run():
	root.size=Vector2i(1280,720);root.content_scale_size=Vector2i(1280,720)
	if not OS.get_cmdline_user_args().is_empty():prefix=OS.get_cmdline_user_args()[0]
	island=load("res://scenes/layered_island.tscn").instantiate();root.add_child(island);current_scene=island
	island.manual_control=false;island.hud.hide()
	for i in 16:await process_frame
	var shots=[]
	for row in [["beach","stair_bottom",0.,"beach"],["junction","bridge_left",.3,"platform"],["forest_step1","forest_mid",.7,"old_forest"],["forest_end","forest_west_entry",.45,"connection"],["forest_west_entry","forest_west_gate",.8,"gate"],["forest_west_gate","forest_west_light",.8,"clearing"],["forest_west_light","forest_west_mid",.8,"middle"],["forest_west_shade","forest_west_end",.7,"end"]]:
		island.set_route_sample(row[0],row[1],row[2]);island.facing="up" if row[3]=="old_forest" else "right";island.facing_left=true;island._update_actor(false,0.,true)
		island._update_occluders(2.)
		for i in 10:await process_frame
		await RenderingServer.frame_post_draw
		root.get_texture().get_image().save_jpg(OUT+prefix+"-"+row[3]+".jpg",.87)
		shots.append({"label":row[3],"actor":island.hero.position,"ground":island.last_ground,"camera":island.camera.position})
	var f=FileAccess.open(OUT+prefix+"-shots.json",FileAccess.WRITE);f.store_string(JSON.stringify(shots,"  "))
	print("FOREST_SHOTS_DONE");quit()
