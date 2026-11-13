extends SceneTree
const OUT := "res://artifacts/full-island-ink-review/runtime-verification.json"
var rows:Array=[]
var counts:Dictionary={}
func _initialize() -> void:
	call_deferred("run")
func run() -> void:
	var island=load("res://scenes/island.tscn").instantiate()
	island.skip_opening=true
	root.add_child(island)
	island.set_process(false)
	for node in island.find_children("*","MeshInstance3D",true,false):
		for surface in node.mesh.get_surface_count():
			var source=node.mesh.surface_get_material(surface) as StandardMaterial3D
			if source==null:continue
			var title=source.resource_name
			var expected=""
			if title=="Coast_Ground":expected="ink_sample_ground.gdshader"
			elif title in ["Coast_Sculpted_Bedrock","InkIsland_Rock_Wash"]:expected="ink_island_bedrock.gdshader"
			elif title.begins_with("InkSample_Rock_"):expected="ink_sample_rock.gdshader"
			elif title in ["InkSample_Grass","InkSample_Bamboo_Leaf","InkSample_Bamboo_Stem"]:expected="ink_sample_bamboo.gdshader"
			elif title in ["ForestValley_Turf","ForestValley_Rock"]:expected="forest_valley.gdshader"
			assert(title not in ["Coast_Grass","Depth_Bamboo_Stem","Depth_Bamboo_Canopy"])
			assert(not title.begins_with("Fish_Rock_"))
			if expected.is_empty():continue
			var material=node.get_active_material(surface) as ShaderMaterial
			assert(material!=null, str(node.name)+" "+title)
			assert(material.shader.resource_path.ends_with(expected),str(node.name)+" "+material.shader.resource_path)
			counts[expected]=counts.get(expected,0)+1
			rows.append({"object":str(node.name),"source_material":title,"shader":material.shader.resource_path})
	assert(counts.get("ink_sample_ground.gdshader",0)==2)
	assert(counts.get("ink_island_bedrock.gdshader",0)==9)
	assert(counts.get("ink_sample_rock.gdshader",0)==5)
	var f:=FileAccess.open(OUT,FileAccess.WRITE)
	f.store_string(JSON.stringify({"counts":counts,"surfaces":rows,"obsolete_terrestrial_materials":0,"validation":"Real imported scene and runtime material bindings; headless, no video."},"  "))
	print("FULL_INK_RUNTIME_OK ",counts)
	quit(0)
