extends SceneTree
func _initialize():call_deferred("run")
func run():
	root.size=Vector2i(1280,720)
	var island=load("res://scenes/layered_island.tscn").instantiate();root.add_child(island);current_scene=island
	island.manual_control=false;island.hud.hide();island.set_process(false)
	var colors={"WALK_Forest_Ground":Color.GREEN,"WALK_Forest_NearSlope":Color.BLUE,"Forest_Near_Closed_Skirt":Color.YELLOW,"WALK_Cape_Neck":Color.MAGENTA,"Cape_Connection_Shoulder":Color.ORANGE,"Cape_Connection_Closed_Skirt":Color.RED,"WALK_Cape_Platform":Color.CYAN}
	for node in island.get_node("World").find_children("*","MeshInstance3D",true,false):
		if colors.has(str(node.name)):
			var mat=StandardMaterial3D.new();mat.shading_mode=BaseMaterial3D.SHADING_MODE_UNSHADED;mat.albedo_color=colors[str(node.name)];mat.cull_mode=BaseMaterial3D.CULL_DISABLED
			node.material_override=mat
	island.set_route_sample("forest_cape_exit","cape_neck",.1)
	for tick in 8:await process_frame
	RenderingServer.force_draw(false);root.get_texture().get_image().save_png("res://artifacts/cape-forest-continuity-review/terrain-debug.png");quit()
