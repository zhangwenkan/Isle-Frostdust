extends SceneTree
const OUT="res://artifacts/spatial-foundation-review/"
var island:Node3D
var mask:ShaderMaterial
func _initialize():call_deferred("run")
func run():
	root.size=Vector2i(1280,720);root.content_scale_size=Vector2i(1280,720)
	island=load("res://scenes/layered_island.tscn").instantiate();root.add_child(island);current_scene=island
	island.manual_control=false;island.camera_locked=true;island.hud.hide();island.set_process(false)
	for node in island.get_node("World").find_children("*","MeshInstance3D",true,false):
		if node.material_override is ShaderMaterial and node.material_override.shader==island.PAINT:node.material_override.set_shader_parameter("wind_strength",0.0)
	var normal=Shader.new();normal.code="shader_type spatial;render_mode unshaded,cull_disabled;uniform sampler2D painting:filter_linear_mipmap;void fragment(){ALBEDO=vec3(1,0,1);ALPHA=texture(painting,UV).a;ALPHA_SCISSOR_THRESHOLD=.3;}"
	var through=Shader.new();through.code=normal.code.replace("unshaded,cull_disabled","unshaded,cull_disabled,depth_test_disabled")
	mask=ShaderMaterial.new();mask.shader=normal
	island.hero.billboard=BaseMaterial3D.BILLBOARD_DISABLED;island.hero.material_override=mask
	var result=[]
	for row in [["junction","bridge_left",.6],["bridge_left","bridge_right",1.0],["bridge_right","cave_mouth",.5],["cave_mouth","cave_end",1.0],["forest_step1","forest_mid",1.0],["forest_landing","forest_end",1.0]]:
		island.set_route_sample(row[0],row[1],row[2]);island.hero.stop();island._update_occluders(2.)
		mask.set_shader_parameter("painting",island.hero.sprite_frames.get_frame_texture("idle_right",0))
		mask.shader=through;var full=await count_mask()
		mask.shader=normal;var base=await count_mask()
		var blockers={}
		if base<float(full)*.88:
			for name in ["Cave_Outer_Relief","Cave_Inner_Relief","Land_Relief","Bamboo_Back","Bamboo_Middle_Left","Bamboo_Middle_Deep","Bamboo_Front_Left","Bamboo_Bridge","Vine_Left","Vine_Right"]:
				var node=island.get_node("World").find_child(name,true,false)
				if not node:continue
				node.hide();var visible=await count_mask();node.show()
				if visible>base+5:blockers[name]=visible-base
		var fades={}
		for plant in island.bamboo_occluders:
			if plant.transparency>.1:fades[str(plant.name)]=plant.transparency
		result.append({"edge":[row[0],row[1]],"t":row[2],"visible":base,"full":full,"blockers":blockers,"faded_clumps":fades})
	var f=FileAccess.open(OUT+"visibility-check.json",FileAccess.WRITE);f.store_string(JSON.stringify(result,"  "))
	print("VISIBILITY_CHECK "+JSON.stringify(result));quit()
func count_mask()->int:
	for i in 2:await process_frame
	await RenderingServer.frame_post_draw
	var im=root.get_texture().get_image()
	var foot=island.camera.unproject_position(island.hero.position)
	var n=0
	for y in range(maxi(0,int(foot.y)-180),mini(720,int(foot.y)+20)):
		for x in range(maxi(0,int(foot.x)-60),mini(1280,int(foot.x)+60)):
			var c=im.get_pixel(x,y)
			if c.r>.9 and c.b>.9 and c.g<.1:n+=1
	return n
