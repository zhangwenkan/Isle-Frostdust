extends SceneTree
func _initialize():call_deferred("run")
func run():
	var island=load("res://scenes/layered_island.tscn").instantiate();root.add_child(island);current_scene=island;island.set_process(false)
	var records=[]
	for key in ["cape_center","cape_stair_top","cape_stair_bottom"]:
		var p:Vector3=island.anchors[key];var contact:Dictionary=island.surface.sample(p)
		assert(not contact.is_empty(),"Missing static anchor support: "+key)
		records.append({"anchor":key,"position":[p.x,p.y,p.z],"support":contact})
	var path="res://artifacts/rock-cape-weight-review/world-contact.json"
	FileAccess.open(path,FileAccess.WRITE).store_string(JSON.stringify(records,"  "))
	print("THREE_WORLD_ANCHORS_SUPPORTED; static only");quit()
