extends SceneTree
func _initialize():call_deferred("run")
func run():
	root.size=Vector2i(1280,720);root.content_scale_size=Vector2i(1280,720)
	var island=load("res://scenes/layered_island.tscn").instantiate();root.add_child(island)
	island.manual_control=false;island.set_process(false)
	island.set_route_sample("forest_west_light","forest_west_mid",.8)
	var world=island.get_node("World")
	for row in island.layout.forest_extension.layer_roles.painted_layers+island.layout.forest_extension.layer_roles.mist_layers:
		var center=island.v3(row.center)
		for height in [center.z,center.z-5.0,center.z-10.0,center.z-15.0]:
			var p=world.to_global(Vector3(center.x,height,-center.y))
			print(row.name," z=",height," screen=",island.camera.unproject_position(p)," distance=",-island.camera.to_local(p).z)
	quit()
