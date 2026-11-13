extends "res://tools/capture_cloud_water.gd"
func run_capture()->void:
	root.size=Vector2i(1280,720)
	island=load("res://scenes/island.tscn").instantiate();root.add_child(island);current_scene=island
	island.set_process(false);island.opening.set_process(false);island.hero.pause();island.hud.hide()
	island.opening.enabled=true;island.opening.start();island.opening.intro_elapsed=1.8;island._update_camera(0,true)
	var water:ShaderMaterial=island.atmosphere.water_materials[0]
	var original:String=water.shader.code
	for variant in ["normal","flat","no-bottom","no-specular","no-caustic"]:
		var code:=original
		if variant=="flat":code=code.replace("vec3 world_normal = normalize(vec3(slope.x, 1.0, slope.y));","slope=vec2(0.0); vec3 world_normal=vec3(0.0,1.0,0.0);")
		if variant=="no-bottom":code=code.replace("transmission *= bottom_visibility;","transmission=vec3(0.0);")
		if variant=="no-specular":code=code.replace("SPECULAR*=1.0-distant_haze;","SPECULAR=0.0;")
		if variant=="no-caustic":code=code.replace("caustic * 0.16","caustic * 0.0")
		var test:=Shader.new();test.code=code;water.shader=test
		await settle(12);await RenderingServer.frame_post_draw
		root.get_texture().get_image().save_png("res://artifacts/coast-unification-review/water-diagnostic-"+variant+".png")
	quit(0)
