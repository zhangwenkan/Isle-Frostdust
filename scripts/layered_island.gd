extends Node3D
## Painted layers over Blender-authored relief, walk surfaces, bridge and cave.
const PAINT=preload("res://shaders/layered_paint.gdshader")
const DISTANCE=preload("res://shaders/layered_distance.gdshader")
const CLOUD=preload("res://shaders/layered_cloudsea.gdshader")
var layout:Dictionary
var anchors:Dictionary={}
var neighbors:Dictionary={}
var surface=preload("res://scripts/layered_surface.gd").new()
var camera:Camera3D
var hero:AnimatedSprite3D
var contact:MeshInstance3D
var hud:CanvasLayer
var location_label:Label
var current_anchor="beach"
var destination=""
var edge_t=0.0
var facing="right"
var facing_left=false
var elapsed=0.0
var camera_locked=false
var camera_focus=Vector2.ZERO
var camera_focus_world=Vector3.ZERO
var camera_lead=Vector2.ZERO
var local_zoom=2.5
var manual_control=true
var base_camera:Vector3
var base_target:Vector3
var birds:Array[Dictionary]=[]
var last_ground:Dictionary={}
var contact_mesh:Mesh
var bamboo_occluders:Array[MeshInstance3D]=[]

func v3(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])

func _ready()->void:
	layout=JSON.parse_string(FileAccess.get_file_as_string("res://assets/layered_island/layout.json"))
	for key:String in layout.anchors:
		anchors[key]=$World.to_global(v3(layout.anchors[key]));neighbors[key]=[]
	for edge:Array in layout.edges:
		neighbors[edge[0]].append(edge[1]);neighbors[edge[1]].append(edge[0])
	base_camera=$World.to_global(v3(layout.camera.position));base_target=$World.to_global(v3(layout.camera.target))
	local_zoom=float(layout.camera.get("local_zoom",2.5))
	_configure_art($World)
	surface.configure($World)
	_build_environment()
	_build_hero()
	_build_hud()
	_build_birds()
	reset_actor()
	print("LAYERED_ISLAND_READY surfaces=%d triangles=%d"%[surface.surfaces.size(),surface.triangle_count])

func _paint(tex:String,plant=false,tint=Color.WHITE)->ShaderMaterial:
	var m=ShaderMaterial.new();m.shader=PAINT
	m.set_shader_parameter("painting",load("res://assets/layered_island/textures/"+tex+".png"))
	m.set_shader_parameter("tint",tint)
	m.set_shader_parameter("wind_strength",0.11 if plant else 0.0)
	m.set_shader_parameter("author_world_to_local",$World.global_transform.affine_inverse())
	return m

func _configure_art(node:Node)->void:
	if node is MeshInstance3D:
		var name_text=str(node.name)
		node.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		if name_text=="WALK_Left_Beach" and layout.has("beach_swatch"):
			var m=ShaderMaterial.new();m.shader=preload("res://shaders/beach_sand.gdshader")
			m.set_shader_parameter("sand_map",load("res://assets/layered_island/beach_swatch/sand_albedo.png"))
			node.material_override=m;node.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_ON
		elif name_text=="Beach_Swash_Film":
			var m=ShaderMaterial.new();m.shader=preload("res://shaders/beach_swash.gdshader");m.render_priority=-55
			node.material_override=m
		elif name_text.begins_with("Left_") or name_text.begins_with("WALK_Left_") or name_text.begins_with("Forest_") or name_text.begins_with("WALK_Forest_"):
			_configure_left_material(node)
		elif name_text.begins_with("Space_") or name_text.begins_with("WALK_Space_"):
			_configure_spatial_material(node)
		elif name_text=="Hero_Contact_Disk":contact_mesh=node.mesh;node.hide()
		elif name_text=="SUPPORT_Bridge":node.hide()
		elif name_text=="Sea_Surface":
			var m=ShaderMaterial.new();m.shader=preload("res://shaders/layered_sea.gdshader");m.render_priority=-60;node.material_override=m
			m.set_shader_parameter("author_world_to_local",$World.global_transform.affine_inverse())
			m.set_shader_parameter("swash_enabled",layout.has("beach_swatch"))
			var coast=PackedVector2Array()
			for p:Array in layout.get("shoreline",[]):
				coast.append(Vector2(p[0],p[1]))
			if coast.size()==32:m.set_shader_parameter("shoreline",coast)
		elif name_text.begins_with("Cloud_Sea"):
			var m=ShaderMaterial.new();m.shader=CLOUD
			m.set_shader_parameter("phase",2.3 if name_text.ends_with("Back") else 0.0)
			m.set_shader_parameter("density",.22 if name_text.ends_with("Back") else .15)
			m.render_priority=-50
			node.material_override=m
		elif name_text.begins_with("Mountain_") or name_text=="Sky_Painting":
			var key="sky" if name_text=="Sky_Painting" else name_text.to_lower()
			var m=ShaderMaterial.new();m.shader=DISTANCE;m.set_shader_parameter("painting",load("res://assets/layered_island/textures/"+key+".png"));m.set_shader_parameter("sky",key=="sky")
			m.render_priority={"sky":-120,"mountain_far":-110,"mountain_middle":-100,"mountain_near":-90}[key]
			node.material_override=m
		elif name_text.begins_with("WALK_Route_"):
			if name_text in layout.get("spatial_sample",{}).get("hidden_route_surfaces",[]):node.hide()
			var index=int(name_text.trim_prefix("WALK_Route_"))
			node.material_override=_paint("cave_inner" if index==6 else ("cave_outer" if index==5 else "land"))
			node.material_override.set_shader_parameter("project_from_author_camera",true)
		elif name_text.begins_with("Bridge_"):
			for i in node.mesh.get_surface_count():
				var original=node.mesh.surface_get_material(i) as StandardMaterial3D
				if original:
					var m=original.duplicate() as StandardMaterial3D
					m.transparency=BaseMaterial3D.TRANSPARENCY_DISABLED
					m.cull_mode=BaseMaterial3D.CULL_DISABLED
					m.roughness=.93;m.texture_filter=BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
					node.set_surface_override_material(i,m)
			node.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_ON
		else:
			var map={"WALK_Land":"land","WALK_Front_Stairs":"land","Cave_Outer_Relief":"cave_outer","WALK_Cave_Interior":"cave_inner","Bamboo_Back":"bamboo_back","Bamboo_Middle_Left":"bamboo_middle","Bamboo_Middle_Deep":"bamboo_middle","Bamboo_Front_Left":"bamboo_front","Bamboo_Bridge":"bamboo_bridge","Bamboo_Left_Extension":"bamboo_middle","Trees_Cave_Back":"trees_back","Vine_Left":"vine_left","Vine_Right":"vine_right","Foreground_Bottom":"foreground_bottom","Foreground_Right_Rock":"foreground_right_rock","Foreground_Right_Leaves":"foreground_right_leaves"}
			map["Land_Relief"]="land";map["Cave_Inner_Relief"]="cave_inner"
			map["Land_Left_Extension"]="land";map["Trees_Right_Extension"]="trees_back"
			if map.has(name_text):
				var plant=name_text.begins_with("Bamboo") or name_text.begins_with("Vine") or name_text.begins_with("Trees") or name_text.ends_with("Leaves")
				var tint=Color(.84,.86,.79) if name_text=="Trees_Cave_Back" else Color.WHITE
				var m=_paint(map[name_text],plant,tint)
				m.set_shader_parameter("project_from_author_camera",name_text in ["Land_Relief","Cave_Outer_Relief","Cave_Inner_Relief","WALK_Front_Stairs","WALK_Land","WALK_Cave_Interior"])
				if name_text.begins_with("WALK_Land"):m.set_shader_parameter("shade_motion",.018)
				node.material_override=m
	for child in node.get_children():_configure_art(child)

func _configure_left_material(node:MeshInstance3D)->void:
	var bamboo=str(node.name).begins_with("Left_Bamboo") or str(node.name).begins_with("Forest_Bamboo")
	var grass=str(node.name).begins_with("Left_Grass") or str(node.name).begins_with("Forest_Grass")
	var depth_band="old"
	for grove:Dictionary in layout.get("forest_extension",{}).get("groves",[]):
		if grove.name==str(node.name):depth_band=grove.band;break
	if bamboo:bamboo_occluders.append(node)
	for i in node.mesh.get_surface_count():
		var original=node.mesh.surface_get_material(i) as StandardMaterial3D
		if not original:continue
		var m=ShaderMaterial.new();m.shader=preload("res://shaders/layered_left.gdshader")
		m.set_shader_parameter("use_texture",original.albedo_texture!=null)
		m.set_shader_parameter("painting",original.albedo_texture)
		m.set_shader_parameter("tint",Color.WHITE if original.albedo_texture else original.albedo_color)
		m.set_shader_parameter("wind_strength",.16 if bamboo else (.06 if grass else 0.0))
		m.set_shader_parameter("vertex_tint",bamboo or grass)
		m.set_shader_parameter("foliage",str(original.resource_name).begins_with("LF_leaf"))
		m.set_shader_parameter("actor_clearance",bamboo)
		m.set_shader_parameter("grove_tint",Color("a6b2a1") if depth_band=="far" else (Color("bac4ac") if depth_band=="deep" else (Color("b1b8a0") if depth_band=="front" else Color.WHITE)))
		if str(node.name)=="Forest_Grass_Understory":m.set_shader_parameter("grove_tint",Color(.63,.77,.53))
		m.set_shader_parameter("forest_air",.46 if depth_band=="backdrop" else (.27 if depth_band=="far" else (.10 if depth_band=="deep" else 0.0)))
		m.set_shader_parameter("sand",str(node.name)=="WALK_Left_Beach")
		m.set_shader_parameter("author_world_to_local",$World.global_transform.affine_inverse())
		node.set_surface_override_material(i,m)
		node.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_DOUBLE_SIDED if bamboo or grass else GeometryInstance3D.SHADOW_CASTING_SETTING_ON

func _configure_spatial_material(node:MeshInstance3D)->void:
	var plant=str(node.name).begins_with("Space_Bamboo")
	var grass=str(node.name).begins_with("Space_Grass")
	if plant:bamboo_occluders.append(node)
	for i in node.mesh.get_surface_count():
		var original=node.mesh.surface_get_material(i) as StandardMaterial3D
		if not original:continue
		var m=ShaderMaterial.new();m.shader=preload("res://shaders/layered_spatial.gdshader")
		m.set_shader_parameter("use_texture",original.albedo_texture!=null)
		m.set_shader_parameter("painting",original.albedo_texture)
		m.set_shader_parameter("tint",Color.WHITE if original.albedo_texture else original.albedo_color)
		if str(node.name)=="Space_Cave_Lining":
			m.set_shader_parameter("use_texture",true)
			m.set_shader_parameter("painting",load("res://assets/layered_island/spatial_textures/rock.png"))
			m.set_shader_parameter("tint",Color(.12,.15,.16))
		m.set_shader_parameter("cutout",plant)
		m.set_shader_parameter("wind_strength",.13 if plant else (.045 if grass else 0.0))
		m.set_shader_parameter("author_world_to_local",$World.global_transform.affine_inverse())
		if str(node.name)=="WALK_Space_Ground":
			m.set_shader_parameter("ground_path",true)
			m.set_shader_parameter("path_painting",load("res://assets/layered_island/spatial_textures/path.png"))
		node.set_surface_override_material(i,m)
	node.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_DOUBLE_SIDED if plant or grass else GeometryInstance3D.SHADOW_CASTING_SETTING_ON

func _build_environment()->void:
	var env=Environment.new();env.background_mode=Environment.BG_COLOR;env.background_color=Color("a1b0b2")
	env.ambient_light_source=Environment.AMBIENT_SOURCE_COLOR;env.ambient_light_color=Color("c4cfbd");env.ambient_light_energy=.39
	env.ssao_enabled=true;env.ssao_radius=.65;env.ssao_intensity=1.1
	env.tonemap_mode=Environment.TONE_MAPPER_LINEAR
	if layout.has("forest_extension"):
		env.volumetric_fog_enabled=true;env.volumetric_fog_density=0.0
		env.volumetric_fog_length=85.;env.volumetric_fog_detail_spread=1.6
		env.volumetric_fog_ambient_inject=.35;env.volumetric_fog_sky_affect=0.0
	var world=WorldEnvironment.new();world.environment=env;add_child(world)
	var sun=DirectionalLight3D.new();sun.name="CoastalSun";sun.rotation_degrees=Vector3(-41,-38,0);sun.light_color=Color("fff0ce");sun.light_energy=1.08;sun.shadow_enabled=true;sun.directional_shadow_max_distance=80;sun.shadow_bias=.018;sun.shadow_normal_bias=.23;sun.light_angular_distance=.8;add_child(sun)
	camera=Camera3D.new();camera.name="SceneCamera";camera.position=base_camera;camera.fov=32;camera.near=.15;camera.far=800;add_child(camera);camera.look_at(base_target);camera.current=true
	if layout.has("forest_extension"):
		var attributes=CameraAttributesPractical.new()
		attributes.dof_blur_near_enabled=true;attributes.dof_blur_near_distance=28.0;attributes.dof_blur_near_transition=5.0
		attributes.dof_blur_far_enabled=true;attributes.dof_blur_far_distance=40.0;attributes.dof_blur_far_transition=21.0;attributes.dof_blur_amount=.12
		camera.attributes=attributes
		_build_forest_atmosphere()

func _build_forest_atmosphere()->void:
	# Real local volumes sit between the authored groves, with open intervals.
	# The ocean and foreground remain outside these volumes.
	for row in [[Vector3(-28,6.0,-22),Vector3(29,7,7),.052],[Vector3(-22,5.7,-30),Vector3(39,10,9),.072],[Vector3(-6.8,7.0,-18.5),Vector3(12,7,10),.038]]:
		var fog=FogVolume.new();fog.name="ForestAir";fog.size=row[1]
		var mat=ShaderMaterial.new();mat.shader=preload("res://shaders/forest_local_air.gdshader");mat.set_shader_parameter("density",row[2]);fog.material=mat
		$World.add_child(fog);fog.position=row[0]

func _build_hero()->void:
	hero=AnimatedSprite3D.new();hero.name="XiaoYe"
	# Local mip levels preserve thin linework at the current projected size.
	var frames=preload("res://assets/characters/green_three_walk/swordsman_walk.tres").duplicate() as SpriteFrames
	var filtered:Dictionary={}
	for animation in frames.get_animation_names():
		for i in frames.get_frame_count(animation):
			var tex=frames.get_frame_texture(animation,i)
			var base=tex.atlas if tex is AtlasTexture else tex
			if not filtered.has(base.resource_path):
				var img=base.get_image();img.generate_mipmaps()
				filtered[base.resource_path]=ImageTexture.create_from_image(img)
			var replacement:Texture2D=filtered[base.resource_path]
			if tex is AtlasTexture:
				var atlas=tex.duplicate() as AtlasTexture;atlas.atlas=replacement;replacement=atlas
			frames.set_frame(animation,i,replacement,frames.get_frame_duration(animation,i))
	hero.sprite_frames=frames
	hero.pixel_size=.0032;hero.offset=Vector2(0,340)
	hero.billboard=BaseMaterial3D.BILLBOARD_FIXED_Y
	hero.texture_filter=BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
	hero.alpha_cut=SpriteBase3D.ALPHA_CUT_DISCARD;hero.alpha_scissor_threshold=.3;hero.shaded=true
	hero.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_DOUBLE_SIDED;add_child(hero)
	contact=MeshInstance3D.new();contact.mesh=contact_mesh;contact.name="FootContact"
	var m=ShaderMaterial.new();m.shader=preload("res://shaders/hero_ground_contact.gdshader");m.set_shader_parameter("strength",.19);m.set_shader_parameter("sole_contact",.06)
	contact.material_override=m;contact.scale=Vector3(.55,1,.36);add_child(contact)

func _build_hud()->void:
	hud=CanvasLayer.new();hud.name="Controls";add_child(hud)
	var font=load("res://assets/ui/fonts/cubic_11/Cubic_11.ttf")
	var label=Label.new();label.text="無人岛\nWASD / 方向键 行走   ·   岔路按对应方向\nR 回到沙滩   ·   Tab 隐藏界面   ·   F5 锁定 / 跟随镜头";label.position=Vector2(24,20)
	label.add_theme_font_override("font",font);label.add_theme_font_size_override("font_size",16);label.add_theme_color_override("font_color",Color("eee5ce"));label.add_theme_color_override("font_shadow_color",Color("192b2c"));label.add_theme_constant_override("shadow_offset_x",1);label.add_theme_constant_override("shadow_offset_y",2);hud.add_child(label)
	location_label=Label.new();location_label.position=Vector2(24,92);location_label.add_theme_font_override("font",font);location_label.add_theme_font_size_override("font_size",16);hud.add_child(location_label)

func _build_birds()->void:
	for i in 2:
		var b=preload("res://assets/island_blender/coastal_gull.glb").instantiate() as Node3D
		b.name="DistantGull%d"%i;b.scale=Vector3.ONE*.7;add_child(b)
		birds.append({"node":b,"left":b.find_child("Wing_L",true,false),"right":b.find_child("Wing_R",true,false),"phase":float(i)*1.4})

func reset_actor()->void:
	current_anchor="beach";destination="";edge_t=0.;hero.position=anchors.beach;facing="right";facing_left=false;_update_actor(false,0.,true)
	camera_lead=Vector2.ZERO;_update_camera(0.,true)

func _unhandled_key_input(event:InputEvent)->void:
	if event is InputEventKey and event.pressed and not event.echo:
		if event.physical_keycode==KEY_R:reset_actor()
		elif event.physical_keycode==KEY_TAB:hud.visible=not hud.visible
		elif event.physical_keycode==KEY_F5:camera_locked=not camera_locked

func _input_vector()->Vector2:
	var v=Input.get_vector("move_left","move_right","move_up","move_down")
	if Input.is_physical_key_pressed(KEY_LEFT):v.x-=1
	if Input.is_physical_key_pressed(KEY_RIGHT):v.x+=1
	if Input.is_physical_key_pressed(KEY_UP):v.y-=1
	if Input.is_physical_key_pressed(KEY_DOWN):v.y+=1
	return v.limit_length()

func _process(delta:float)->void:
	elapsed+=delta
	if manual_control:advance_input(_input_vector(),delta)
	_update_camera(delta)
	_update_occluders(delta)
	for data:Dictionary in birds:
		var t=fmod(elapsed+data.phase*2.,42.)
		data.node.visible=t<18.
		var f=t/18.;data.node.position=Vector3(lerpf(-18.,22.,f),9.+sin(f*PI)*3.+data.phase,lerpf(-23.,-53.,f)-sin(f*PI)*10.)
		data.node.rotation=Vector3(.03*sin(t),-1.2+f*.7,.18*sin(f*PI))
		var flap=sin(t*5.2+data.phase)*.48*(1.-smoothstep(5.,8.,t))
		if data.left:data.left.rotation.z=flap
		if data.right:data.right.rotation.z=-flap

func _update_occluders(delta:float)->void:
	# Only foreground clumps crossing the camera-to-character line soften.
	# Depth, roots and shadows remain in place throughout the transition.
	var focus=hero.global_position+Vector3(0,1.0,0)
	var ray=focus-camera.global_position
	for bamboo in bamboo_occluders:
		if str(bamboo.name).begins_with("Left_Bamboo") or str(bamboo.name).begins_with("Forest_Bamboo"):
			for i in bamboo.mesh.get_surface_count():
				var mat=bamboo.get_surface_override_material(i) as ShaderMaterial
				if mat:
					mat.set_shader_parameter("actor_focus",focus)
					mat.set_shader_parameter("viewer_position",camera.global_position)
			continue
		var bounds=bamboo.get_aabb();var center=bamboo.to_global(bounds.get_center())
		var t=clampf((center.z-camera.global_position.z)/ray.z,0.0,1.0)
		var nearest=camera.global_position+ray*t
		var radius=maxf(.7,bounds.size.x*.38)
		var blocks=t<.99 and center.z>focus.z+.25 and absf(center.x-nearest.x)<radius and nearest.y>center.y-bounds.size.y*.52 and nearest.y<center.y+bounds.size.y*.52
		bamboo.transparency=lerpf(bamboo.transparency,.86 if blocks else 0.0,1.-exp(-5.*delta))

func _reference_pixel(point:Vector3)->Vector2:
	var forward=(base_target-base_camera).normalized()
	var up=Vector3.RIGHT.cross(forward).normalized()
	var q=point-base_camera;var depth=q.dot(forward)
	var half=tan(deg_to_rad(32.)*.5)
	return Vector2(1024.+q.x/depth/(half*4./3.)*1024.,768.-q.dot(up)/depth/half*768.)

func _update_camera(delta:float,snap=false)->void:
	# Translate the observation point while preserving its viewing angle.
	# Smooth anchor heights avoid a camera bump at every physical stair riser.
	var route_position:Vector3=anchors[current_anchor]
	if not destination.is_empty():route_position=(anchors[current_anchor] as Vector3).lerp(anchors[destination],edge_t)
	var desired=route_position+Vector3(camera_lead.x/42.*.65,1.35,camera_lead.y/42.*.35)
	if snap:camera_focus_world=desired
	elif not camera_locked:camera_focus_world=camera_focus_world.lerp(desired,1.-exp(-3.5*delta))
	camera_focus=_reference_pixel(camera_focus_world)
	var offset=v3(layout.camera.get("physical_offset",[0,20.5,35.14]))
	camera.keep_aspect=Camera3D.KEEP_HEIGHT
	camera.set_perspective(float(layout.camera.get("physical_fov",16.3)),.15,800.)
	camera.position=camera_focus_world+offset
	camera.look_at(camera_focus_world)

func advance_input(input:Vector2,delta:float)->void:
	var moving=input.length()>.1
	var start_position:Vector3=hero.position
	if moving:
		if destination.is_empty():
			var best=.15
			for next:String in neighbors[current_anchor]:
				var dir=(camera.unproject_position(anchors[next])-camera.unproject_position(anchors[current_anchor])).normalized()
				var dot=input.normalized().dot(dir)
				if dot>best:best=dot;destination=next
		else:
			var dir=(camera.unproject_position(anchors[destination])-camera.unproject_position(anchors[current_anchor])).normalized()
			if input.normalized().dot(dir)<-.2:
				var old=current_anchor;current_anchor=destination;destination=old;edge_t=1.-edge_t
		if not destination.is_empty():
			var a:Vector3=anchors[current_anchor];var b:Vector3=anchors[destination]
			var screen=(camera.unproject_position(b)-camera.unproject_position(a)).normalized()
			facing="up" if screen.y<-.45 else ("down" if screen.y>.55 else "right")
			facing_left=screen.x<0. if facing=="right" else false
			edge_t=minf(1.,edge_t+delta*2.15/a.distance_to(b))
			hero.position=a.lerp(b,edge_t)
			if edge_t>=1.:current_anchor=destination;destination="";edge_t=0.
	# Arriving at a route node is still a walking frame. Only idle once the
	# input stops or there is no valid continuation at an endpoint.
	if moving and hero.position.distance_squared_to(start_position)>.0000001:
		camera_lead=camera_lead.lerp(input.normalized()*42.,1.-exp(-3.*delta))
	_update_actor(moving and hero.position.distance_squared_to(start_position)>.0000001,delta)

func _update_actor(moving:bool,delta:float,snap=false)->void:
	last_ground=surface.sample(hero.position)
	if not last_ground.is_empty():hero.position.y=float(last_ground.height)+.014
	hero.flip_h=facing_left
	var anim=StringName(("walk_" if moving else "idle_")+facing)
	if hero.animation!=anim:hero.play(anim)
	contact.position=hero.position+Vector3(0,.008,.015)
	var inside=clampf((hero.position.z-anchors.cave_mouth.z)/(anchors.cave_end.z-anchors.cave_mouth.z),0.,1.) if hero.position.x>anchors.cave_mouth.x-.15 else 0.
	var target_color=Color(.97,.97,.89).lerp(Color(.46,.58,.67),inside*.68)
	hero.modulate=target_color if snap else hero.modulate.lerp(target_color,1.-exp(-7.*delta))
	location_label.text="竹径" if current_anchor.begins_with("forest") else ("洞口" if current_anchor.begins_with("cave") else ("吊桥" if current_anchor.begins_with("bridge") else ""))

func set_route_sample(a:String,b:String,t:float)->void:
	current_anchor=a;destination=b;edge_t=t;hero.position=(anchors[a] as Vector3).lerp(anchors[b],t);_update_actor(false,0.,true)
	camera_lead=Vector2.ZERO;_update_camera(0.,true)
