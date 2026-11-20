extends SceneTree
const BASE="res://artifacts/coast-structure-recovery/"
var before=false
func _initialize():call_deferred("run")
func vec(v:Array)->Vector3:return Vector3(v[0],v[1],v[2])
func arr(v:Vector3)->Array:return [v.x,v.y,v.z]
func run():
	before="--weight-before" in OS.get_cmdline_user_args()
	Engine.time_scale=0.0;root.size=Vector2i(1280,720);root.content_scale_size=Vector2i(1280,720);root.content_scale_mode=Window.CONTENT_SCALE_MODE_VIEWPORT;root.content_scale_aspect=Window.CONTENT_SCALE_ASPECT_KEEP
	var island=load("res://scenes/layered_island.tscn").instantiate();root.add_child(island);current_scene=island
	island.manual_control=false;island.hud.hide();island.set_process(false);island.hero.pause()
	for mat in island.forest_light_materials:mat.set_shader_parameter("forest_light_time_override",0.0)
	var records=[];var camera_records=[]
	if not before:camera_records=JSON.parse_string(FileAccess.get_file_as_string("res://artifacts/rock-cape-weight-review/before/frames.json"))
	var index=0
	for shot in [["forest_cape_approach","forest_cape_exit",.75,"approach"],["cape_entry","cape_center",.9,"camp"],["cape_stair_top","cape_stair_bottom",.48,"stairs"],["cape_stair_bottom","cape_sand",.5,"sand"],["cape_stair_top","cape_stair_bottom",.84,"lower-close"]]:
		island.set_route_sample(shot[0],shot[1],shot[2]);island.facing="right";island.facing_left=false;island._update_actor(false,0.0,true);island.hero.pause();island.hero.frame=0;island._update_occluders(0.0)
		if shot[3]=="lower-close":island.camera.fov=22.0
		if not before:
			island.camera.position=vec(camera_records[index].camera);island.camera.rotation=vec(camera_records[index].rotation);island.camera.fov=camera_records[index].fov
		for frame in 24:await process_frame
		RenderingServer.force_draw(false)
		assert(root.get_texture().get_image().save_png(BASE+("before/" if before else "")+"game-"+shot[3]+".png")==OK)
		records.append({"shot":shot[3],"camera":arr(island.camera.position),"rotation":arr(island.camera.rotation),"fov":island.camera.fov,"actor":arr(island.hero.position),"ground":island.last_ground});index+=1
	var file=FileAccess.open(BASE+("before/" if before else "")+"frames.json",FileAccess.WRITE);file.store_string(JSON.stringify(records,"  "))
	print("ROCK_CAPE_WEIGHT_STATIC_COMPLETE");quit()
