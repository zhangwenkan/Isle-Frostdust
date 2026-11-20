extends SceneTree
func _initialize():call_deferred("run")
func run()->void:
	root.size=Vector2i(1280,720)
	var island=load("res://scenes/layered_island.tscn").instantiate();root.add_child(island);current_scene=island
	island.manual_control=false;island.hud.hide();island.set_process(false)
	island.set_route_sample("cape_neck","cape_entry",.45)
	var colors={"Cape_Cliff_Plane_00":Color.RED,"Cape_Cliff_Plane_01":Color.ORANGE,"Cape_Cliff_Plane_02":Color.BLUE,"Cape_Cliff_Plane_03":Color.MAGENTA,"Cape_Tip_Continuous_Bedrock":Color.CYAN,"Forest_Near_Closed_Skirt":Color.YELLOW}
	for node in island.get_node("World").find_children("*","MeshInstance3D",true,false):
		if colors.has(str(node.name)):
			var mat=StandardMaterial3D.new();mat.shading_mode=BaseMaterial3D.SHADING_MODE_UNSHADED;mat.albedo_color=colors[str(node.name)];mat.cull_mode=BaseMaterial3D.CULL_DISABLED;node.material_override=mat
	for frame in 8:await process_frame
	RenderingServer.force_draw(false);root.get_texture().get_image().save_png("res://artifacts/forest-tip-extension-review/rock-source-debug.png");quit()
