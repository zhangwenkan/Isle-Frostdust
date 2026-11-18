extends SceneTree
const OUT="res://artifacts/forest-air-review/"
var island:Node3D
var env:Environment
var air_materials:Array=[]
var args:Array=[]

func _initialize():call_deferred("run")

func run():
	DirAccess.make_dir_recursive_absolute(OUT)
	root.size=Vector2i(1280,720);root.content_scale_size=Vector2i(1280,720)
	args=OS.get_cmdline_user_args()
	var prefix="diagnosis" if args.is_empty() else str(args[0])
	if prefix=="before":
		for filename in ["layered_left.gdshader","forest_local_air.gdshader","layered_sea.gdshader"]:
			(load("res://shaders/"+filename) as Shader).code=FileAccess.get_file_as_string(OUT+"before/"+filename)
	island=load("res://scenes/layered_island.tscn").instantiate()
	if prefix=="before":
		var baseline=GDScript.new();baseline.source_code=FileAccess.get_file_as_string(OUT+"before/layered_island.gd")
		assert(baseline.reload()==OK);island.set_script(baseline)
	root.add_child(island);current_scene=island
	island.manual_control=false;island.hud.hide();island.set_process(false)
	for child in island.get_children():
		if child is WorldEnvironment:env=child.environment
	collect_materials(island.get_node("World"))
	for node in island.get_node("World").find_children("*","MeshInstance3D",true,false):
		if node.name in ["WALK_Left_Beach","Beach_Swash_Film"]:
			node.material_override.set_shader_parameter("shoreline_time_override",8.0)
	# Freeze only runtime shader resources; source files remain untouched.
	for path in ["res://shaders/layered_left.gdshader","res://shaders/forest_local_air.gdshader","res://shaders/layered_sea.gdshader","res://shaders/beach_sand.gdshader","res://shaders/beach_swash.gdshader","res://shaders/layered_distance.gdshader","res://shaders/layered_cloudsea.gdshader"]:
		var shader=load(path) as Shader
		shader.code=shader.code.replace("TIME","8.0")
	var variants=["original","no_far_dof","no_volume","no_material_air","no_volume_or_material_air"] if prefix=="diagnosis" else ["current"]
	if prefix=="background":variants=["current","no_sea","no_cloudsea","no_sky","no_mountains"]
	if prefix=="verification":variants=["current","no_far_dof","no_water_mask"]
	var backgrounds=[]
	for node in island.get_node("World").find_children("*","MeshInstance3D",true,false):
		if node.name=="Sea_Surface" or node.name=="Sky_Painting" or str(node.name).begins_with("Cloud_Sea") or str(node.name).begins_with("Mountain_"):
			backgrounds.append(node)
	var report=[]
	var shots=[["forest_west_gate","forest_west_light",.8,"clearing"],["forest_west_light","forest_west_mid",.8,"middle"],["forest_end","forest_west_entry",.45,"connection"]]
	if prefix in ["verification","before"]:shots.append_array([["forest_west_shade","forest_west_end",1.0,"end"],["beach","stair_bottom",.0,"beach"],["bridge_left","bridge_right",.5,"bridge"]])
	for shot in shots:
		if prefix=="background" and shot[3]!="clearing":continue
		island.set_route_sample(shot[0],shot[1],shot[2]);island.facing="right";island.facing_left=true;island._update_actor(false,0.,true);island._update_occluders(2.)
		island.hero.pause();island.hero.frame=0
		for variant in variants:
			for node in backgrounds:
				node.visible=not ((variant=="no_sea" and node.name=="Sea_Surface") or (variant=="no_cloudsea" and str(node.name).begins_with("Cloud_Sea")) or (variant=="no_sky" and node.name=="Sky_Painting") or (variant=="no_mountains" and str(node.name).begins_with("Mountain_")))
			env.volumetric_fog_enabled=variant not in ["no_volume","no_volume_or_material_air"]
			island.camera.attributes.dof_blur_far_enabled=variant!="no_far_dof"
			if prefix!="before":
				for node in backgrounds:
					if node.name=="Sea_Surface":node.material_override.set_shader_parameter("forest_land_mask_enabled",variant!="no_water_mask")
			for row in air_materials:row[0].set_shader_parameter("forest_air",0.0 if variant in ["no_material_air","no_volume_or_material_air"] else row[1])
			for i in 36:
				await process_frame
			await RenderingServer.frame_post_draw
			var path=OUT+prefix+"-"+shot[3]+"-"+variant+".jpg"
			assert(root.get_texture().get_image().save_jpg(path,.94)==OK)
			if prefix in ["verification","before"]:assert(root.get_texture().get_image().save_png(path.replace(".jpg",".png"))==OK)
			report.append({"file":path,"view":shot[3],"variant":variant,"camera":str(island.camera.position),"far_dof":island.camera.attributes.dof_blur_far_enabled,"volume":env.volumetric_fog_enabled,"far_distance":island.camera.attributes.dof_blur_far_distance,"far_transition":island.camera.attributes.dof_blur_far_transition,"blur_amount":island.camera.attributes.dof_blur_amount,"sea_probes":sea_probes()})
	var f=FileAccess.open(OUT+prefix+"-shots.json",FileAccess.WRITE);f.store_string(JSON.stringify(report,"  "))
	print("FOREST_AIR_CAPTURE_DONE "+prefix);quit()

func sea_probes()->Array:
	var sea=island.get_node("World").find_child("Sea_Surface",true,false) as MeshInstance3D
	var center=sea.to_global(sea.mesh.get_aabb().get_center())
	var plane=Plane(sea.global_basis.y.normalized(),center)
	var result=[]
	for pixel in [Vector2(640,180),Vector2(640,210),Vector2(640,240),Vector2(320,210)]:
		var hit=plane.intersects_ray(island.camera.project_ray_origin(pixel),island.camera.project_ray_normal(pixel))
		if hit!=null:
			result.append({"pixel":str(pixel),"authored":str(island.get_node("World").to_local(hit)),"view_depth":-(island.camera.global_transform.affine_inverse()*hit).z})
	return result

func collect_materials(node:Node):
	if node is MeshInstance3D:
		for i in node.mesh.get_surface_count():
			var m=node.get_surface_override_material(i)
			if m is ShaderMaterial and m.shader.resource_path=="res://shaders/layered_left.gdshader":
				air_materials.append([m,m.get_shader_parameter("forest_air")])
	for child in node.get_children():collect_materials(child)
