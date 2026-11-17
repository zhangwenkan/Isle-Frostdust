extends SceneTree
var island:Node3D
const OUT="res://artifacts/layered-island-build/"
var prefix="pass4"
func _initialize()->void:call_deferred("run")
func run()->void:
	root.size=Vector2i(1280,720);root.content_scale_size=Vector2i(1280,720)
	island=load("res://scenes/layered_island.tscn").instantiate();root.add_child(island);current_scene=island
	island.manual_control=false;island.camera_locked=true
	for i in 30:await process_frame
	island.hud.hide()
	await shot(prefix+"-beach")
	for row:Array in [["stair_bottom","stair_top",.6,"stairs"],["bridge_left","bridge_right",.5,"bridge"],["cave_mouth","cave_end",.65,"cave"],["forest_turn","forest_mid",.7,"forest"]]:
		island.set_route_sample(row[0],row[1],row[2]);island.facing="up" if row[3] in ["stairs","forest","cave"] else "right"
		island._update_actor(false,.1,true)
		for i in 4:await process_frame
		await shot(prefix+"-"+row[3])
	var misses=[];var max_jump=0.;var samples=0;var edge_results=[]
	for edge:Array in island.layout.edges:
		var previous_y=0.;var edge_jump=0.
		for i in 81:
			var p:Vector3=(island.anchors[edge[0]] as Vector3).lerp(island.anchors[edge[1]],float(i)/80.)
			var hit:Dictionary=island.surface.sample(p)
			samples+=1
			if hit.is_empty():misses.append({"edge":edge,"t":float(i)/80.})
			else:
				if i>0:
					max_jump=maxf(max_jump,absf(float(hit.height)-previous_y));edge_jump=maxf(edge_jump,absf(float(hit.height)-previous_y))
				previous_y=hit.height
		edge_results.append({"edge":edge,"max_jump":edge_jump})
	var f=FileAccess.open(OUT+prefix+"-support.json",FileAccess.WRITE);f.store_string(JSON.stringify({"samples":samples,"misses":misses,"max_sample_height_jump":max_jump,"surfaces":island.surface.surfaces,"edges":edge_results},"  "))
	print("LAYERED_CAPTURE_COMPLETE samples=%d misses=%d"%[samples,misses.size()]);quit()
func shot(name:String)->void:
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png(OUT+name+".png")
