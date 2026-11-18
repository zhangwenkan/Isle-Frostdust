extends SceneTree
const OUT="res://artifacts/forest-valley-enclosure-review/"
var island:Node3D
var env:Environment
func _initialize():call_deferred("run")
func run():
	var args=OS.get_cmdline_user_args();var prefix="pass1" if args.is_empty() else str(args[0])
	root.size=Vector2i(1280,720);root.content_scale_size=Vector2i(1280,720)
	island=load("res://scenes/layered_island.tscn").instantiate();root.add_child(island);current_scene=island
	island.manual_control=false;island.hud.hide();island.set_process(false)
	for child in island.get_children():
		if child is WorldEnvironment:env=child.environment
	for path in ["layered_left.gdshader","forest_local_air.gdshader","layered_sea.gdshader","beach_sand.gdshader","beach_swash.gdshader","layered_distance.gdshader","layered_cloudsea.gdshader"]:
		var shader=load("res://shaders/"+path) as Shader;shader.code=shader.code.replace("TIME","8.0")
	var backgrounds=[]
	for node in island.get_node("World").find_children("*","MeshInstance3D",true,false):
		if node.name in ["WALK_Left_Beach","Beach_Swash_Film"]:node.material_override.set_shader_parameter("shoreline_time_override",8.0)
		if node.name in ["Sea_Surface","Sky_Painting"] or str(node.name).begins_with("Cloud_Sea") or str(node.name).begins_with("Mountain_"):backgrounds.append(node)
	var report=[]
	for shot in [["forest_west_gate","forest_west_light",.8,"clearing"],["forest_west_light","forest_west_mid",.8,"middle"],["forest_end","forest_west_entry",.45,"connection"],["forest_west_shade","forest_west_end",1.0,"end"],["forest_west_entry","forest_west_gate",.6,"gate"],["forest_step2","forest_landing",.6,"old_forest"],["beach","stair_bottom",.0,"beach"],["bridge_left","bridge_right",.5,"bridge"]]:
		island.set_route_sample(shot[0],shot[1],shot[2]);island.facing="right";island.facing_left=true;island._update_actor(false,0.,true);island._update_occluders(2.0);island.hero.pause();island.hero.frame=0
		var variants=["current","no_sea_sky"] if shot[3] in ["clearing","middle","connection","end","gate"] else ["current"]
		if shot[3]=="clearing":variants.append("no_volume")
		for variant in variants:
			for node in backgrounds:node.visible=variant!="no_sea_sky"
			env.volumetric_fog_enabled=variant!="no_volume"
			for i in 36:await process_frame
			await RenderingServer.frame_post_draw
			var path=OUT+prefix+"-"+shot[3]+"-"+variant
			assert(root.get_texture().get_image().save_jpg(path+".jpg",.94)==OK)
			assert(root.get_texture().get_image().save_png(path+".png")==OK)
			report.append({"view":shot[3],"variant":variant,"camera":str(island.camera.position),"world":str(island.get_node("World").global_transform),"far_dof":island.camera.attributes.dof_blur_far_enabled,"far_transition":island.camera.attributes.dof_blur_far_transition})
	var f=FileAccess.open(OUT+"shots.json",FileAccess.WRITE);f.store_string(JSON.stringify(report,"  "))
	print("VALLEY_FOREST_CAPTURE_DONE");quit()
