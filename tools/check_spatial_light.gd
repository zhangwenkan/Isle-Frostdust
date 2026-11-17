extends SceneTree
const OUT="res://artifacts/spatial-foundation-review/"
var island:Node3D
func _initialize():call_deferred("run")
func run():
	root.size=Vector2i(1280,720);root.content_scale_size=Vector2i(1280,720)
	island=load("res://scenes/layered_island.tscn").instantiate();root.add_child(island);current_scene=island;island.manual_control=false;island.set_process(false);island.hud.hide()
	island.reset_actor();island.hero.stop()
	for node in island.get_node("World").find_children("*","MeshInstance3D",true,false):
		if node.material_override is ShaderMaterial:node.material_override.set_shader_parameter("wind_strength",0.0)
		for i in node.get_surface_override_material_count():
			var m=node.get_surface_override_material(i)
			if m is ShaderMaterial:m.set_shader_parameter("wind_strength",0.0)
	await shot("light-shaded-shadow")
	island.hero.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	await shot("light-shaded-no-shadow")
	island.hero.shaded=false
	await shot("light-unshaded-no-shadow")
	print("LIGHT_COMPARISON_SAVED");quit()
func shot(name:String):
	for i in 5:await process_frame
	await RenderingServer.frame_post_draw
	var im=root.get_texture().get_image()
	var foot:Vector2=island.camera.unproject_position(island.hero.position)
	im.get_region(Rect2i(Vector2i(int(foot.x)-140,int(foot.y)-180),Vector2i(280,270))).save_png(OUT+name+".png")
