extends SceneTree
const OUT="res://artifacts/tripo-game-integration-review/"
func _initialize():call_deferred("run")
func capture(file:String)->void:
	for frame in 20:await process_frame
	RenderingServer.force_draw(false)
	assert(root.get_texture().get_image().save_png(OUT+file+".png")==OK)
func run()->void:
	root.size=Vector2i(1280,720);root.content_scale_size=Vector2i(1280,720)
	var island=load("res://scenes/layered_island.tscn").instantiate();root.add_child(island);current_scene=island
	island.manual_control=false;island.hud.hide();island.set_process(false);island.hero.pause()
	var views=[]
	for shot in [["forest_cape_approach","forest_cape_exit",.75,"approach"],["cape_entry","cape_center",.9,"camp"],["cape_stair_top","cape_stair_bottom",.48,"stairs"],["cape_stair_bottom","cape_sand",.5,"sand"]]:
		island.set_route_sample(shot[0],shot[1],shot[2]);island.facing="right";island.facing_left=false;island._update_actor(false,0.0,true);island.hero.pause();island.hero.frame=0
		island._update_occluders(0.0);await capture("game-"+shot[3])
		views.append({"view":shot[3],"actor":str(island.hero.position),"ground":island.last_ground,"camera":str(island.camera.position),"fov":island.camera.fov})
	var file=FileAccess.open(OUT+"game-check.json",FileAccess.WRITE);file.store_string(JSON.stringify({"integration":island.get_meta("tripo_rock_integrated",false),"views":views,"scope":"Static in-game material and framing review, not a continuous passage audit."},"  "))
	print("TRIPO_GAME_VIEWS_COMPLETE");quit()
