extends SceneTree
const OUT="res://artifacts/beach-swash-review/"
func _initialize():call_deferred("run")
func run():
	var world=load("res://assets/layered_island/layered_island.glb").instantiate();root.add_child(world)
	var report={};var failed=false
	for name in ["WALK_Left_Beach","Beach_Swash_Film"]:
		var node=world.find_child(name,true,false) as MeshInstance3D
		var arrays=node.mesh.surface_get_arrays(0)
		var points:PackedVector3Array=arrays[Mesh.ARRAY_VERTEX]
		var field:PackedVector2Array=arrays[Mesh.ARRAY_TEX_UV2]
		var min_d=100.;var max_d=-100.;var inland=0;var offshore=0;var wrong=0
		for i in points.size():
			min_d=minf(min_d,field[i].y);max_d=maxf(max_d,field[i].y)
			if field[i].y< -1.2:
				inland+=1
				if points[i].y< -.16:wrong+=1
			if field[i].y>.8:
				offshore+=1
				if points[i].y> -.14:wrong+=1
		report[name]={"signed_distance_range":[min_d,max_d],"inland_vertices":inland,"offshore_vertices":offshore,"wrong_side_vertices":wrong}
		if wrong>0 or inland==0 or offshore==0:failed=true
	var f=FileAccess.open(OUT+"imported-shore-field.json",FileAccess.WRITE);f.store_string(JSON.stringify(report,"  "))
	print("BEACH_IMPORTED_FIELD "+JSON.stringify(report));quit(1 if failed else 0)
