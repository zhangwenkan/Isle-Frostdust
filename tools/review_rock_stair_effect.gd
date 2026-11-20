extends SceneTree
const OUT="res://artifacts/rock-stair-composition-review/"
func _initialize():call_deferred("run")
func capture(name:String)->void:
	for frame in 14:await process_frame
	RenderingServer.force_draw(false)
	assert(root.get_texture().get_image().save_png(OUT+name+".png")==OK)
func run()->void:
	root.size=Vector2i(1280,720);root.content_scale_size=Vector2i(1280,720)
	var island=load("res://scenes/layered_island.tscn").instantiate();root.add_child(island);current_scene=island
	island.manual_control=false;island.hud.hide();island.set_process(false);island.hero.pause()
	for mat in island.forest_light_materials:
		mat.set_shader_parameter("wind_time_override",8.0);mat.set_shader_parameter("forest_light_time_override",10.0)
	var views=[]
	for shot in [["forest_cape_approach","forest_cape_exit",.68,"approach"],["cape_entry","cape_center",.85,"camp"],["cape_stair_top","cape_stair_bottom",.56,"stairs"],["cape_stair_bottom","cape_sand",.8,"sand"]]:
		island.set_route_sample(shot[0],shot[1],shot[2]);island.facing="right";island.facing_left=false;island._update_actor(false,0.0,true);island.hero.pause();island.hero.frame=0
		island._update_occluders(0.0);await capture("review-"+shot[3])
		views.append({"name":shot[3],"camera":str(island.camera.position),"fov":island.camera.fov})
		if shot[3]=="stairs" and "--diagnose-roof" in OS.get_cmdline_user_args():
			var ground=island.get_node("World").find_child("WALK_Forest_Ground",true,false)
			var core=island.get_node("World").find_child("Cape_Terminus_Bedrock",true,false)
			ground.hide();await capture("diagnostic-without-ground");ground.show()
			core.hide();await capture("diagnostic-without-core");core.show()
		if shot[3]=="stairs" and "--pick-wing" in OS.get_cmdline_user_args():
			var picks=[]
			for pixel in [Vector2(950,425),Vector2(965,430),Vector2(980,440),Vector2(990,450)]:
				var origin=island.camera.project_ray_origin(pixel);var ray=island.camera.project_ray_normal(pixel)
				var closest=INF;var best={}
				for key in ["WALK_Forest_Ground","Cape_Terminus_Bedrock","Cape_Strict_Rock_Near_Lower","Cape_Strict_Rock_Near_Seam"]:
					var obj=island.get_node("World").find_child(key,true,false) as MeshInstance3D
					var tris=obj.mesh.get_faces()
					for i in range(0,tris.size(),3):
						var a=obj.to_global(tris[i]);var b=obj.to_global(tris[i+1]);var c=obj.to_global(tris[i+2])
						var hit=Geometry3D.ray_intersects_triangle(origin,ray,a,b,c)
						if hit!=null and origin.distance_to(hit)<closest:
							closest=origin.distance_to(hit);var local=island.get_node("World").to_local(hit)
							best={"object":key,"author_hit":[local.x,-local.z,local.y],"triangle":i/3}
				picks.append({"pixel":str(pixel),"hit":best})
			var pickfile=FileAccess.open(OUT+"wing-picks.json",FileAccess.WRITE);pickfile.store_string(JSON.stringify(picks,"  "))
	island.set_route_sample("cape_entry","cape_center",.85);island._update_actor(false,0.0,true)
	var target=island.get_node("World").to_global(Vector3(-60.5,5.2,-10.0))
	island.camera.position=target+island.get_node("World").global_basis*Vector3(0,12.4,34.1);island.camera.fov=42;island.camera.look_at(target)
	await capture("review-overview")
	var file=FileAccess.open(OUT+"effect-captures.json",FileAccess.WRITE)
	file.store_string(JSON.stringify({"views":views,"revision":island.layout.revision,"scope":"Static effect captures only. No passage audit or continuous walking test."},"  "))
	print("ROCK_STAIR_EFFECT_CAPTURED");quit()
