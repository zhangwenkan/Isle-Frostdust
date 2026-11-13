extends SceneTree
func _initialize() -> void:call_deferred("run")
func run() -> void:
	var island=load("res://scenes/island.tscn").instantiate()
	root.add_child(island)
	for layer in range(5):
		var node=island.find_child("PixelBamboo_L%d_000"%layer,true,false)
		print("PIXEL_META ",node.name," ",node.get_meta_list()," ",node.get_meta("gltf_extras",{})," material-depth=",node.get_active_material(0).get_shader_parameter("forest_depth"))
	quit()
