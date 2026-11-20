extends Node3D
## Painted layers over Blender-authored relief, walk surfaces, bridge and cave.
const PAINT=preload("res://shaders/layered_paint.gdshader")
const DISTANCE=preload("res://shaders/layered_distance.gdshader")
const CLOUD=preload("res://shaders/layered_cloudsea.gdshader")
const MOVE_SPEED=7.0
var layout:Dictionary
var anchors:Dictionary={}
var neighbors:Dictionary={}
var surface=preload("res://scripts/layered_surface.gd").new()
var camera:Camera3D
var hero:AnimatedSprite3D
var hero_lighting=preload("res://scripts/hero_forest_lighting.gd").new()
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
var coastal_backdrops:Array[ShaderMaterial]=[]
var forest_paintings:Array[ShaderMaterial]=[]
var forest_light_materials:Array[ShaderMaterial]=[]
var sea_material:ShaderMaterial
var cape_backdrops:Array[ShaderMaterial]=[]
var cape_islets:Array[MeshInstance3D]=[]
var cape_sky_material:ShaderMaterial
var scene_environment:Environment

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
	preload("res://scripts/coast_structure_integration.gd").new().configure(self)
	surface.configure($World)
	_build_environment()
	_bind_forest_light_field()
	_build_hero()
	if layout.has("reference_cape"):
		var life=preload("res://scripts/reference_cape_life.gd").new();$World.add_child(life);life.configure(self)
	_build_hud()
	_build_birds()
	reset_actor("forest_west_mid")
	if "--tripo-rock-preview" in OS.get_cmdline_user_args():reset_actor("cape_center")
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
		if name_text.begins_with("Forest_Strict_"):
			_configure_strict_material(node)
		elif name_text.begins_with("Cape_") or name_text.begins_with("WALK_Cape_"):
			_configure_cape_material(node)
		elif name_text.begins_with("Forest_Paint_"):
			var key=name_text.trim_prefix("Forest_Paint_")
			var files={"Near":"forest_shapes_near","Middle":"forest_shapes_middle","Depth":"forest_depth"}
			var m=ShaderMaterial.new();m.shader=preload("res://shaders/forest_depth_solid.gdshader") if key=="Depth" else preload("res://shaders/forest_depth_paint.gdshader")
			m.set_shader_parameter("painting",load("res://assets/layered_island/forest_layers/"+files[key]+".png"))
			m.set_shader_parameter("layer",{"Near":0.0,"Middle":1.0,"Depth":2.0}[key])
			m.set_shader_parameter("author_world_to_local",$World.global_transform.affine_inverse())
			m.render_priority={"Near":-70,"Middle":-75,"Depth":-80}[key]
			m.set_shader_parameter("terminus_edge_enabled",layout.get("reference_cape",{}).has("rocky_terminus"))
			node.material_override=m;forest_paintings.append(m)
		elif name_text.begins_with("Forest_Mist_"):
			var key=name_text.trim_prefix("Forest_Mist_")
			var m=ShaderMaterial.new();m.shader=preload("res://shaders/forest_layer_mist.gdshader")
			m.set_shader_parameter("layer",{"Front":0.0,"Middle":1.0,"Far":2.0}[key])
			m.set_shader_parameter("fog_color",Color({"Front":"8fa580","Middle":"a7b69a","Far":"b8c3a9"}[key]).srgb_to_linear())
			m.set_shader_parameter("author_world_to_local",$World.global_transform.affine_inverse())
			m.render_priority={"Front":-67,"Middle":-72,"Far":-77}[key]
			m.set_shader_parameter("terminus_edge_enabled",layout.get("reference_cape",{}).has("rocky_terminus"))
			node.material_override=m;forest_paintings.append(m)
		elif name_text.begins_with("Forest_Sunray_"):
			var data:Dictionary={}
			for row in layout.forest_extension.layer_roles.get("sunray_layers",[]):
				if row.name==name_text:data=row;break
			var m=ShaderMaterial.new();m.shader=preload("res://shaders/forest_sunray_veil.gdshader")
			m.set_shader_parameter("author_world_to_local",$World.global_transform.affine_inverse())
			m.set_shader_parameter("layer",float(data.get("layer",0.0)))
			m.set_shader_parameter("veil_strength",float(data.get("strength",.14)))
			m.render_priority=-69-int(data.get("layer",0))*5
			node.material_override=m;forest_paintings.append(m)
		elif name_text=="WALK_Left_Beach" and layout.has("beach_swatch"):
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
			sea_material=m
			if layout.has("reference_cape"):
				m.set_shader_parameter("cape_enabled",true)
				if layout.reference_cape.has("rocky_terminus"):
					m.set_shader_parameter("cape_region",Vector2(-61.0,-54.0))
					m.set_shader_parameter("cape_reflection_x",-85.2)
				var cape_coast=PackedVector2Array()
				for point:Array in layout.reference_cape.shoreline:cape_coast.append(Vector2(point[0],point[1]))
				m.set_shader_parameter("cape_shoreline",cape_coast)
			m.set_shader_parameter("author_world_to_local",$World.global_transform.affine_inverse())
			m.set_shader_parameter("swash_enabled",layout.has("beach_swatch"))
			if layout.has("forest_extension"):
				var mask_data=JSON.parse_string(FileAccess.get_file_as_string("res://assets/layered_island/forest_extension/forest_water_mask.json"))
				var bounds:Array=mask_data.bounds
				m.set_shader_parameter("forest_land_mask_enabled",true)
				m.set_shader_parameter("forest_land_mask",load("res://assets/layered_island/forest_extension/forest_water_mask.png"))
				m.set_shader_parameter("forest_land_bounds",Vector4(bounds[0],bounds[1],bounds[2],bounds[3]))
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
		if name_text.begins_with("Cloud_Sea") or name_text.begins_with("Mountain_") or name_text=="Sky_Painting":coastal_backdrops.append(node.material_override)
	for child in node.get_children():_configure_art(child)

func _configure_cape_material(node:MeshInstance3D)->void:
	var key=str(node.name)
	var continuity=layout.get("reference_cape",{}).has("forest_continuity") and key in ["WALK_Cape_Neck","Cape_Connection_Shoulder","WALK_Cape_Platform","Cape_Neck_Rockside","Cape_Connection_Closed_Skirt"]
	continuity=continuity or key.begins_with("Cape_Terminus_")
	if key=="Cape_Sky_Backdrop":
		node.hide();return
	if key=="WALK_Cape_Sand":
		var mat=ShaderMaterial.new();mat.shader=preload("res://shaders/beach_sand.gdshader")
		mat.set_shader_parameter("sand_map",load("res://assets/layered_island/strict_coast/sand.png" if layout.reference_cape.has("strict_reference") else "res://assets/layered_island/reference_cape/sand_unique.png"))
		node.material_override=mat;node.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_ON;return
	if key=="Cape_Swash_Film":
		var mat=ShaderMaterial.new();mat.shader=preload("res://shaders/beach_swash.gdshader");mat.render_priority=-55
		node.material_override=mat;return
	if key.begins_with("Cape_Flame_") or key.begins_with("Cape_Smoke_") or key.begins_with("Cape_Ember_"):
		var mat=ShaderMaterial.new()
		mat.shader=preload("res://shaders/reference_cape_flame.gdshader") if key.begins_with("Cape_Flame_") else (preload("res://shaders/reference_cape_smoke.gdshader") if key.begins_with("Cape_Smoke_") else preload("res://shaders/reference_cape_ember.gdshader"))
		mat.set_shader_parameter("phase",float(key.get_slice("_",2).to_int())*1.71)
		node.material_override=mat;return
	var distant=key.begins_with("Cape_Distant_Islet_")
	if distant:cape_islets.append(node)
	if node.mesh.get_surface_count()>0:
		var first=node.mesh.surface_get_material(0) as StandardMaterial3D
		if first and str(first.resource_name).begins_with("StrictCoast_") and not distant:
			_configure_strict_material(node);return
	for i in node.mesh.get_surface_count():
		var original=node.mesh.surface_get_material(i) as StandardMaterial3D
		if not original:continue
		var mat=ShaderMaterial.new();mat.shader=preload("res://shaders/reference_cape_islet.gdshader") if distant else preload("res://shaders/reference_cape_surface.gdshader")
		if distant and layout.reference_cape.has("strict_reference"):mat.shader=preload("res://shaders/strict_coast_islet.gdshader")
		if continuity:mat.shader=preload("res://shaders/cape_forest_surface.gdshader")
		var relief_paint=str(original.resource_name).begins_with("ForestCoast_")
		mat.set_shader_parameter("painting",original.albedo_texture)
		if not distant:
			mat.set_shader_parameter("use_texture",original.albedo_texture!=null)
			mat.set_shader_parameter("tint",original.albedo_color)
			mat.set_shader_parameter("neck",key in ["WALK_Cape_Neck","Cape_Connection_Shoulder"])
			mat.set_shader_parameter("grass",key=="Cape_Shore_Grass")
			mat.set_shader_parameter("author_world_to_local",$World.global_transform.affine_inverse())
			mat.set_shader_parameter("forest_ground",load("res://assets/layered_island/left_finish_textures/ground_unique.png"))
			if continuity and not relief_paint:_bind_continuity_floor(mat)
		node.set_surface_override_material(i,mat)
	node.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_ON

func _bind_continuity_floor(mat:ShaderMaterial)->void:
	mat.set_shader_parameter("continuity_enabled",true)
	if layout.get("reference_cape",{}).has("rocky_terminus"):
		mat.set_shader_parameter("continuity_floor",load("res://assets/layered_island/strict_coast/floor.png" if layout.reference_cape.has("strict_reference") else "res://assets/layered_island/rocky_terminus/floor.png"))
		mat.set_shader_parameter("continuity_bounds",Vector4(-68.0,4.0,18.0,31.0))
		return
	var tip=layout.get("reference_cape",{}).has("forest_tip_extension")
	mat.set_shader_parameter("continuity_floor",load("res://assets/layered_island/forest_tip_extension/tip_floor.png" if tip else "res://assets/layered_island/cape_forest_transition/continuity_floor.png"))
	mat.set_shader_parameter("continuity_bounds",Vector4(-84.0,-5.0,34.0,40.0) if tip else Vector4(-74.0,-5.0,24.0,33.0))

func _configure_strict_material(node:MeshInstance3D)->void:
	var key=str(node.name)
	var bamboo=key.begins_with("Forest_Strict_Bamboo_") or key.begins_with("Forest_Strict_Leaves_") or key.begins_with("Forest_Strict_Low_")
	if bamboo:bamboo_occluders.append(node)
	for i in node.mesh.get_surface_count():
		var original=node.mesh.surface_get_material(i) as StandardMaterial3D
		if not original:continue
		var mat=ShaderMaterial.new();mat.shader=preload("res://shaders/strict_coast_surface.gdshader")
		mat.set_shader_parameter("painting",original.albedo_texture)
		mat.set_shader_parameter("use_texture",original.albedo_texture!=null)
		mat.set_shader_parameter("normal_paint",original.normal_texture)
		mat.set_shader_parameter("use_normal",original.normal_texture!=null)
		mat.set_shader_parameter("tint",original.albedo_color)
		mat.set_shader_parameter("bamboo",bamboo)
		mat.set_shader_parameter("leaf_surface",str(original.resource_name)=="StrictCoast_leaf")
		mat.set_shader_parameter("grass",key.begins_with("Forest_Strict_") and not bamboo)
		mat.set_shader_parameter("author_world_to_local",$World.global_transform.affine_inverse())
		if bamboo:_bind_bamboo_wind(mat,key)
		node.set_surface_override_material(i,mat)
	node.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_DOUBLE_SIDED if bamboo else GeometryInstance3D.SHADOW_CASTING_SETTING_ON

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
		if str(original.resource_name).begins_with("ForestRole_Leaf_"):
			var leaf_material=ShaderMaterial.new();leaf_material.shader=preload("res://shaders/forest_role_leaf.gdshader")
			leaf_material.set_shader_parameter("painting",original.albedo_texture)
			leaf_material.set_shader_parameter("author_world_to_local",$World.global_transform.affine_inverse())
			leaf_material.set_shader_parameter("foreground",depth_band=="role_front")
			_bind_bamboo_wind(leaf_material,str(node.name))
			node.set_surface_override_material(i,leaf_material)
			node.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_DOUBLE_SIDED
			continue
		var forest_surface=layout.get("forest_extension",{}).has("layer_roles") and (str(node.name).begins_with("Forest_") or str(node.name).begins_with("WALK_Forest_"))
		var m=ShaderMaterial.new();m.shader=preload("res://shaders/layered_forest_surface.gdshader") if forest_surface else preload("res://shaders/layered_left.gdshader")
		if forest_surface:m.set_shader_parameter("role_lighting",true)
		if forest_surface and (layout.get("reference_cape",{}).has("forest_continuity") or layout.get("reference_cape",{}).has("forest_tip_extension")) and str(node.name) in ["WALK_Forest_Ground","WALK_Forest_NearSlope"]:_bind_continuity_floor(m)
		m.set_shader_parameter("use_texture",original.albedo_texture!=null)
		m.set_shader_parameter("painting",original.albedo_texture)
		m.set_shader_parameter("tint",Color.WHITE if original.albedo_texture else original.albedo_color)
		m.set_shader_parameter("wind_strength",.16 if bamboo else (.06 if grass else 0.0))
		if forest_surface and bamboo:_bind_bamboo_wind(m,str(node.name),true)
		m.set_shader_parameter("vertex_tint",bamboo or grass)
		m.set_shader_parameter("foliage",str(original.resource_name).begins_with("LF_leaf"))
		m.set_shader_parameter("actor_clearance",bamboo)
		m.set_shader_parameter("grove_tint",Color("a6b2a1") if depth_band=="far" else (Color("bac4ac") if depth_band=="deep" else (Color("b1b8a0") if depth_band=="front" else Color.WHITE)))
		if depth_band.begins_with("valley_"):m.set_shader_parameter("grove_tint",Color("b6c2a8") if depth_band=="valley_far" else Color("c1ccb4"))
		if str(node.name)=="Forest_Grass_Understory":m.set_shader_parameter("grove_tint",Color(.63,.77,.53))
		# A continuous optical-distance fade supplies the air perspective in the
		# shader. Band values only make a small allowance for the deepest groves.
		m.set_shader_parameter("forest_air",.035 if depth_band=="backdrop" else (.020 if depth_band=="far" else (.008 if depth_band=="deep" else 0.0)))
		if depth_band.begins_with("valley_"):m.set_shader_parameter("forest_air",.035 if depth_band=="valley_far" else .015)
		if not layout.get("forest_extension",{}).has("layer_roles"):
			if depth_band.begins_with("valley_") or str(node.name)=="Forest_Valley_Ground":m.set_shader_parameter("valley_air_strength",.72 if depth_band=="valley_far" else .62)
			elif layout.get("forest_extension",{}).has("valley_enclosed") and depth_band in ["deep","far"]:m.set_shader_parameter("valley_air_strength",.60 if depth_band=="far" else .36)
		if depth_band=="role_front":m.set_shader_parameter("grove_tint",Color(.66,.73,.55))
		m.set_shader_parameter("sand",str(node.name)=="WALK_Left_Beach")
		m.set_shader_parameter("author_world_to_local",$World.global_transform.affine_inverse())
		node.set_surface_override_material(i,m)
		node.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_DOUBLE_SIDED if bamboo or grass else GeometryInstance3D.SHADOW_CASTING_SETTING_ON

func _bind_bamboo_wind(mat:ShaderMaterial,node_name:String,body=false)->void:
	var bindings:Dictionary=layout.get("forest_extension",{}).get("layer_roles",{}).get("wind_bindings",{})
	if not bindings.has(node_name):return
	var data:Dictionary=bindings[node_name]
	mat.set_shader_parameter("bamboo_root",v3(data.root))
	mat.set_shader_parameter("bamboo_height",data.height)
	mat.set_shader_parameter("wind_seed",data.seed)
	mat.set_shader_parameter("wind_strength",data.amplitude)
	if body:mat.set_shader_parameter("coherent_bamboo",true)

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
	scene_environment=env
	if layout.has("reference_cape"):
		cape_sky_material=ShaderMaterial.new();cape_sky_material.shader=preload("res://shaders/reference_cape_sky_environment.gdshader")
		if layout.reference_cape.has("strict_reference"):
			cape_sky_material.set_shader_parameter("sun_direction",($World.global_basis*Vector3(-.47,.12,-.87)).normalized())
		var sky=Sky.new();sky.sky_material=cape_sky_material;env.sky=sky
	env.ambient_light_source=Environment.AMBIENT_SOURCE_COLOR;env.ambient_light_color=Color("c4cfbd");env.ambient_light_energy=.39
	env.ssao_enabled=true;env.ssao_radius=.65;env.ssao_intensity=1.1
	env.tonemap_mode=Environment.TONE_MAPPER_LINEAR
	if layout.has("forest_extension"):
		env.volumetric_fog_enabled=true;env.volumetric_fog_density=0.0
		env.volumetric_fog_length=155.0 if layout.get("forest_extension",{}).has("valley_enclosed") else 85.0;env.volumetric_fog_detail_spread=1.6
		env.volumetric_fog_ambient_inject=.35;env.volumetric_fog_sky_affect=0.0
	var world=WorldEnvironment.new();world.environment=env;add_child(world)
	var sun=DirectionalLight3D.new();sun.name="CoastalSun";sun.rotation_degrees=Vector3(-41,-38,0);sun.light_color=Color("fff0ce");sun.light_energy=1.08;sun.shadow_enabled=true;sun.directional_shadow_max_distance=80;sun.shadow_bias=.065;sun.shadow_normal_bias=.55;sun.light_angular_distance=.8;add_child(sun)
	camera=Camera3D.new();camera.name="SceneCamera";camera.position=base_camera;camera.fov=32;camera.near=.15;camera.far=800;add_child(camera);camera.look_at(base_target);camera.current=true
	if layout.has("forest_extension"):
		var attributes=CameraAttributesPractical.new()
		attributes.dof_blur_near_enabled=true;attributes.dof_blur_near_distance=28.0;attributes.dof_blur_near_transition=5.0
		if layout.get("forest_extension",{}).has("layer_roles"):attributes.dof_blur_near_distance=31.0
		attributes.dof_blur_far_enabled=true;attributes.dof_blur_far_distance=40.0;attributes.dof_blur_far_transition=38.0;attributes.dof_blur_amount=.12
		if layout.get("forest_extension",{}).get("layer_roles",{}).has("wind_bindings"):
			attributes.dof_blur_near_distance=29.5;attributes.dof_blur_near_transition=5.5
			attributes.dof_blur_far_distance=47.0;attributes.dof_blur_far_transition=40.0;attributes.dof_blur_amount=.095
		camera.attributes=attributes
		_build_forest_atmosphere()
		if layout.get("forest_extension",{}).has("layer_roles"):_build_forest_light_openings()

func _build_forest_light_openings()->void:
	# Broad light pools relate the walking band to the slope and foliage behind it.
	for row in [[Vector3(-25.8,18,-23),Vector3(-27.8,6,-14),1.65],[Vector3(-44.8,17,-23),Vector3(-42.5,6,-13.5),1.0]]:
		var light=SpotLight3D.new();light.name="ForestOpeningLight"
		light.light_color=Color("f8edbf");light.light_energy=row[2]
		light.spot_range=23.0;light.spot_angle=30.0;light.spot_angle_attenuation=1.4
		light.shadow_enabled=true;light.shadow_bias=.025;light.shadow_normal_bias=.08
		$World.add_child(light);light.position=row[0];light.look_at($World.to_global(row[1]))

func _register_forest_light_material(mat:ShaderMaterial,ray:Vector3)->void:
	if not mat or not mat.shader or mat in forest_light_materials:return
	var shared=false
	for parameter in mat.shader.get_shader_uniform_list():
		if parameter.name=="forest_ray_direction":shared=true;break
	if not shared:return
	mat.set_shader_parameter("forest_ray_direction",ray)
	mat.set_shader_parameter("forest_sun_tint",Color("fff0ce").srgb_to_linear())
	mat.set_shader_parameter("forest_light_strength",1.0)
	forest_light_materials.append(mat)

func _bind_forest_light_field()->void:
	var sun=get_node("CoastalSun") as DirectionalLight3D
	var ray:Vector3=($World.global_basis.inverse()*(-sun.global_basis.z)).normalized()
	for node in $World.find_children("*","MeshInstance3D",true,false):
		_register_forest_light_material(node.material_override as ShaderMaterial,ray)
		for index in node.mesh.get_surface_count():
			_register_forest_light_material(node.get_surface_override_material(index) as ShaderMaterial,ray)
	for node in $World.find_children("*","FogVolume",true,false):
		_register_forest_light_material(node.material as ShaderMaterial,ray)

func _build_forest_atmosphere()->void:
	# Rounded, staggered pockets fade in all three dimensions. The box only
	# bounds shader evaluation; it does not supply a visible horizontal rim.
	var pockets=[[Vector3(-38,4.8,-27),Vector3(17,10,17),.025],[Vector3(-24,7.0,-32),Vector3(19,13,19),.032],[Vector3(-12,5.4,-26),Vector3(15,11,16),.023],[Vector3(-5.8,6.7,-19),Vector3(11,9,12),.018]]
	if layout.get("forest_extension",{}).has("layer_roles"):
		pockets=[[Vector3(-27,6.6,-28),Vector3(20,12,13),.026],[Vector3(-47,5.0,-35),Vector3(24,13,17),.022],[Vector3(-12,7.5,-30),Vector3(16,13,14),.020]]
	elif layout.get("forest_extension",{}).has("valley_enclosed"):
		pockets.append_array([[Vector3(-47,6.4,-45),Vector3(38,20,28),.085],[Vector3(-28,9.0,-64),Vector3(37,24,31),.068],[Vector3(-67,11.0,-74),Vector3(47,26,33),.074],[Vector3(-7,8.0,-50),Vector3(32,23,30),.075]])
		pockets.append_array([[Vector3(-39,6.0,-32),Vector3(28,17,23),.070],[Vector3(-18,7.0,-36),Vector3(29,18,24),.080],[Vector3(-60,6.0,-35),Vector3(31,18,27),.075]])
	for row in pockets:
		var fog=FogVolume.new();fog.name="ForestAir";fog.size=row[1]
		var mat=ShaderMaterial.new();mat.shader=preload("res://shaders/forest_local_air.gdshader")
		mat.set_shader_parameter("density",row[2]);mat.set_shader_parameter("pocket_center",row[0]);mat.set_shader_parameter("pocket_half_size",row[1]*.5)
		mat.set_shader_parameter("author_world_to_local",$World.global_transform.affine_inverse());fog.material=mat
		$World.add_child(fog);fog.position=row[0]

func _build_hero()->void:
	hero=AnimatedSprite3D.new();hero.name="XiaoYe"
	# Local mip levels preserve thin linework at the current projected size.
	var frames=preload("res://assets/characters/green_three_walk/swordsman_walk.tres").duplicate() as SpriteFrames
	var filtered:Dictionary={}
	var source_keys:Dictionary={}
	for animation in frames.get_animation_names():
		for i in frames.get_frame_count(animation):
			var tex=frames.get_frame_texture(animation,i)
			var base=tex.atlas if tex is AtlasTexture else tex
			if not filtered.has(base.resource_path):
				var img=base.get_image();img.generate_mipmaps()
				filtered[base.resource_path]=ImageTexture.create_from_image(img)
				source_keys[filtered[base.resource_path].get_instance_id()]=base.resource_path.get_file().get_basename()
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
	hero_lighting.configure(self,source_keys)
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

func reset_actor(start_anchor:String="beach")->void:
	current_anchor=start_anchor;destination="";edge_t=0.;hero.position=anchors[start_anchor];facing="right";facing_left=false;_update_actor(false,0.,true)
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
	if layout.has("reference_cape"):
		var route_local:Vector3=$World.to_local(route_position)
		var opening=smoothstep(61.0,74.0,-route_local.x)
		if layout.reference_cape.has("rocky_terminus"):
			opening=smoothstep(57.0,65.0,-route_local.x)
			desired+=$World.global_basis*Vector3(-1.2,0.0,.25)*opening
		else:desired+=$World.global_basis*Vector3(-5.0,0.0,1.0)*opening
	if snap:camera_focus_world=desired
	elif not camera_locked:camera_focus_world=camera_focus_world.lerp(desired,1.-exp(-3.5*delta))
	camera_focus=_reference_pixel(camera_focus_world)
	var offset=v3(layout.camera.get("physical_offset",[0,20.5,35.14]))
	var fov=float(layout.camera.get("physical_fov",16.3))
	if layout.get("forest_extension",{}).has("near_mid_depth"):
		var p:Vector3=$World.to_local(camera_focus_world)
		var weight=smoothstep(12.0,20.0,-p.x)*smoothstep(8.0,11.0,-p.z)
		# Move the real camera closer. A wider view keeps the original actor
		# size while increasing the relative scale and motion of near objects.
		var original_distance=offset.length()
		var pitch_sine=offset.y/original_distance
		offset=offset.lerp(offset.normalized()*24.0,weight)
		var distance=offset.length()
		# Compensate the whole transition, with a fixed standing probe relative
		# to the focus. This also keeps F5's framing independent of actor motion.
		var reference_height=1.35/(original_distance+1.35*pitch_sine)+.75/(original_distance-.75*pitch_sine)
		var projected_height=1.35/(distance+1.35*pitch_sine)+.75/(distance-.75*pitch_sine)
		fov=rad_to_deg(2.0*atan(tan(deg_to_rad(fov)*.5)*projected_height/reference_height))
	if layout.has("reference_cape"):
		var focus_local:Vector3=$World.to_local(camera_focus_world)
		var opening=smoothstep(61.0,73.0,-focus_local.x)
		if layout.reference_cape.has("rocky_terminus"):opening=0.0
		offset=offset.lerp(Vector3(0.0,4.0,31.0),opening)
		fov=lerpf(fov,36.0,opening)
	camera.keep_aspect=Camera3D.KEEP_HEIGHT
	camera.set_perspective(fov,.15,800.)
	camera.position=camera_focus_world+offset
	if layout.get("reference_cape",{}).has("strict_reference"):
		var reference_focus:Vector3=$World.to_local(camera_focus_world)
		var reference_weight=smoothstep(48.0,61.0,-reference_focus.x)
		var reference_offset=$World.global_basis*Vector3(0.0,10.69,29.37)
		camera.position=camera_focus_world+offset.lerp(reference_offset,reference_weight)
		camera.fov=lerpf(fov,38.5,reference_weight)
	camera.look_at(camera_focus_world)
	_update_valley_backdrop()

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
			edge_t=minf(1.,edge_t+delta*MOVE_SPEED/a.distance_to(b))
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
	hero_lighting.update()
	if layout.has("reference_cape"):
		var actor_local:Vector3=$World.to_local(hero.position)
		hero_lighting.material.set_shader_parameter("forest_light_strength",1.0-smoothstep(61.0,68.0,-actor_local.x))
	location_label.text="竹径" if current_anchor.begins_with("forest") else ("洞口" if current_anchor.begins_with("cave") else ("吊桥" if current_anchor.begins_with("bridge") else ""))

func _update_valley_backdrop()->void:
	if not layout.get("forest_extension",{}).has("valley_enclosed"):return
	var p:Vector3=$World.to_local(camera_focus_world)
	var inside=smoothstep(7.0,13.0,-p.x)*smoothstep(6.0,11.0,-p.z)
	var cape=0.0
	if layout.has("reference_cape"):
		cape=smoothstep(57.0,65.0,-p.x) if layout.reference_cape.has("rocky_terminus") else smoothstep(61.0,71.0,-p.x)
		if not layout.reference_cape.has("rocky_terminus"):inside*=1.0-cape
	if layout.get("forest_extension",{}).get("layer_roles",{}).has("wind_bindings"):
		# Near DOF also softens the transparent forest pass. Preserve readable
		# silhouettes inside; far DOF and independent mist still supply depth.
		camera.attributes.dof_blur_near_enabled=inside<.02
		camera.attributes.dof_blur_near_distance=lerpf(29.5,18.0,cape)
		if layout.get("reference_cape",{}).has("strict_reference"):
			camera.attributes.dof_blur_far_distance=lerpf(47.0,72.0,cape)
			camera.attributes.dof_blur_far_transition=lerpf(40.0,120.0,cape)
	for mat in coastal_backdrops:mat.set_shader_parameter("opacity",(1.0-inside)*(1.0-cape))
	for mat in cape_backdrops:mat.set_shader_parameter("opacity",cape)
	for node in cape_islets:node.visible=cape>.18
	if cape_sky_material:
		cape_sky_material.set_shader_parameter("cape_amount",cape)
		scene_environment.background_mode=Environment.BG_SKY if cape>.01 else Environment.BG_COLOR
	for mat in forest_paintings:mat.set_shader_parameter("opacity",inside)
	if sea_material:
		sea_material.set_shader_parameter("scene_opacity",1.0-inside*(1.0-cape) if layout.get("reference_cape",{}).has("rocky_terminus") else 1.0-inside)
		sea_material.set_shader_parameter("cape_palette",cape)

func set_route_sample(a:String,b:String,t:float)->void:
	current_anchor=a;destination=b;edge_t=t;hero.position=(anchors[a] as Vector3).lerp(anchors[b],t);_update_actor(false,0.,true)
	camera_lead=Vector2.ZERO;_update_camera(0.,true)
