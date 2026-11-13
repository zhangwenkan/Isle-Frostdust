extends RefCounted
## Shared colored brush materials across the island. Mesh authoring stays in Blender MCP.
static func apply_surface(instance: MeshInstance3D, surface: int, source: StandardMaterial3D) -> bool:
	var title := source.resource_name
	var material: ShaderMaterial
	if title == "ShallowCape_Stone":
		material=ShaderMaterial.new()
		material.shader=preload("res://shaders/shallow_cape_rock.gdshader")
		material.set_shader_parameter("stone_paint",source.albedo_texture)
		material.set_shader_parameter("contact_shading",preload("res://assets/shallow_cape/slab_contact.png"))
	elif title == "Junction_Coast_Painted":
		material=ShaderMaterial.new()
		material.shader=preload("res://shaders/junction_coastal_rock.gdshader")
		material.set_shader_parameter("mineral_paint",source.albedo_texture)
		material.set_shader_parameter("contact_shading",preload("res://assets/coast_junction/junction_contact.png"))
		material.set_shader_parameter("brush_color",preload("res://assets/colored_ink_sample/ground_brush_color.png"))
		material.set_shader_parameter("cape_turf",preload("res://assets/west_cape/cape_turf.png"))
		material.set_shader_parameter("east_brush",preload("res://assets/full_island_ink/east_ground.png"))
	elif title.begins_with("Junction_Relief_"):
		material=ShaderMaterial.new()
		material.shader=preload("res://shaders/junction_coastal_relief.gdshader")
		material.set_shader_parameter("mineral_paint",source.albedo_texture)
		material.set_shader_parameter("top_surface",title.begins_with("Junction_Relief_Top"))
		material.set_shader_parameter("contact_shading",preload("res://assets/coast_junction/junction_contact.png"))
	elif title == "Integrated_Coast_Painted":
		material=ShaderMaterial.new()
		material.shader=preload("res://shaders/integrated_coastal_rock.gdshader")
		material.set_shader_parameter("coastal_paint",preload("res://assets/original_coastal_rock/integrated_coast_paint.png"))
		material.set_shader_parameter("coastal_contact",preload("res://assets/original_coastal_rock/integrated_coast_contact.png"))
		material.set_shader_parameter("brush_color",preload("res://assets/colored_ink_sample/ground_brush_color.png"))
		material.set_shader_parameter("cape_turf",preload("res://assets/west_cape/cape_turf.png"))
		material.set_shader_parameter("east_brush",preload("res://assets/full_island_ink/east_ground.png"))
	elif title == "Original_Coast_Recess":
		material=ShaderMaterial.new()
		material.shader=preload("res://shaders/original_coastal_recess.gdshader")
	elif title.begins_with("Original_Coast_Stone_"):
		material=ShaderMaterial.new()
		material.shader=preload("res://shaders/original_coastal_rock.gdshader")
		material.set_shader_parameter("mineral_paint",source.albedo_texture)
		material.set_shader_parameter("top_surface",title.begins_with("Original_Coast_Stone_Top"))
		material.set_shader_parameter("contact_shading",preload("res://assets/original_coastal_rock/fitted_coast_contact.png"))
	elif title == "Coastal_Strata_Painted":
		material=ShaderMaterial.new()
		material.shader=preload("res://shaders/coastal_strata.gdshader")
		material.set_shader_parameter("strata_color",source.albedo_texture)
	elif title == "Forest_Light_Shaft":
		material=ShaderMaterial.new()
		material.shader=preload("res://shaders/forest_light_shaft.gdshader")
		material.set_shader_parameter("phase",float(instance.get_meta("extras",{}).get("shaft_phase",0.0)))
		instance.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	elif title.begins_with("FineBamboo_") or title.begins_with("DepthFineBamboo_"):
		var authored: Dictionary = instance.get_meta("extras",{})
		var variant: String = title.trim_prefix("DepthFineBamboo_").trim_prefix("FineBamboo_")
		var atlas_folder: String = "bamboo_depth" if title.begins_with("DepthFineBamboo_") else "bamboo_fine"
		material = ShaderMaterial.new()
		material.shader = preload("res://shaders/fine_bamboo.gdshader")
		if bool(authored.get("foreground_foliage",false)):
			var foreground_shader:=Shader.new()
			foreground_shader.code=material.shader.code.replace("render_mode cull_disabled", "render_mode depth_prepass_alpha,cull_disabled").replace("ALPHA_SCISSOR_THRESHOLD=.36;", "vec3 view_right=INV_VIEW_MATRIX[0].xyz; float side=abs(dot(world_position-actor_position,view_right)); float near_actor=(1.0-smoothstep(.38,.85,side))*(1.0-smoothstep(1.9,2.6,world_position.y-actor_position.y)); ALPHA*=1.0-near_actor*.94;")
			material.shader=foreground_shader
			instance.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		material.set_shader_parameter("fine_color",load("res://assets/"+atlas_folder+"/"+variant+"_color.png"))
		material.set_shader_parameter("surface_directions",load("res://assets/"+atlas_folder+"/"+variant+"_normal.png"))
		material.set_shader_parameter("forest_depth",float(authored.get("pixel_bamboo_layer",0)))
		material.set_shader_parameter("pigment_variation",float(authored.get("pigment_variation",1.0)))
		instance.extra_cull_margin = .4
	elif title.begins_with("PixelBamboo_"):
		var authored: Dictionary = instance.get_meta("extras",{})
		material = ShaderMaterial.new()
		material.shader = preload("res://shaders/pixel_bamboo.gdshader")
		material.set_shader_parameter("pixel_atlas",source.albedo_texture)
		material.set_shader_parameter("forest_depth",float(authored.get("pixel_bamboo_layer",0)))
		material.set_shader_parameter("pigment_variation",float(authored.get("pigment_variation",1.0)))
		instance.extra_cull_margin = .4
	elif title in ["Forest_Backwall_Moss","Forest_Backwall_Rock"]:
		material=ShaderMaterial.new()
		material.shader=preload("res://shaders/forest_backwall.gdshader")
		material.set_shader_parameter("floor_paint",preload("res://assets/pixel_bamboo_west/forest_floor.png"))
		material.set_shader_parameter("cliff_paint",preload("res://assets/full_island_ink/cliff_wash.png"))
		material.set_shader_parameter("is_side",title=="Forest_Backwall_Rock")
	elif title == "PixelForest_Ground":
		material = ShaderMaterial.new()
		material.shader = preload("res://shaders/pixel_forest_ground.gdshader")
		material.set_shader_parameter("floor_paint",source.albedo_texture)
		material.set_shader_parameter("edge_paint",preload("res://assets/colored_ink_sample/ground_brush_color.png"))
		material.set_shader_parameter("cape_turf",preload("res://assets/west_cape/cape_turf.png"))
	elif title.begins_with("InkBridge_"):
		material = ShaderMaterial.new()
		material.shader = preload("res://shaders/ink_bridge.gdshader")
		material.set_shader_parameter("brush_color",source.albedo_texture)
		material.set_shader_parameter("is_rope",title in ["InkBridge_Rope","InkBridge_Binding"])
		material.set_shader_parameter("is_binding",title == "InkBridge_Binding")
		material.set_shader_parameter("is_end",title == "InkBridge_End")
	elif title.begins_with("ForestValley_"):
		material = ShaderMaterial.new()
		if title == "ForestValley_Fall" or title == "ForestValley_Foam":
			material.shader = preload("res://shaders/forest_waterfall.gdshader")
			material.set_shader_parameter("is_foam",title == "ForestValley_Foam")
			instance.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		elif title == "ForestValley_Stream":
			material.shader = preload("res://shaders/forest_creek.gdshader")
			instance.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		else:
			material.shader = preload("res://shaders/forest_valley.gdshader")
			material.set_shader_parameter("is_turf",title == "ForestValley_Turf")
			material.set_shader_parameter("is_valley",str(instance.name) in ["ForestVisibility_Opposite_Rock_Slope","ForestVisibility_Near_Bank"])
			material.set_shader_parameter("turf_paint",preload("res://assets/full_island_ink/valley_turf.png"))
			material.set_shader_parameter("cliff_paint",preload("res://assets/full_island_ink/cliff_wash.png"))
			material.set_shader_parameter("depth_haze",float(instance.get_meta("forest_visibility_layer",0))*.04)
	elif title.begins_with("InkValley_"):
		material = ShaderMaterial.new()
		material.shader = preload("res://shaders/ink_valley.gdshader")
		material.set_shader_parameter("is_turf",title == "InkValley_Turf")
		material.set_shader_parameter("is_patch",title == "InkValley_Rock")
		material.set_shader_parameter("turf_paint",preload("res://assets/colored_ink_sample/ground_brush_color.png"))
		material.set_shader_parameter("depth_haze",float(instance.get_meta("valley_depth_layer",0))*.12)
	elif title == "Coast_Ground":
		material = ShaderMaterial.new()
		material.shader = preload("res://shaders/ink_sample_ground.gdshader")
		material.set_shader_parameter("original_color",source.albedo_texture)
		material.set_shader_parameter("original_normal",source.normal_texture)
		material.set_shader_parameter("brush_color",preload("res://assets/colored_ink_sample/ground_brush_color.png"))
		material.set_shader_parameter("cape_turf",preload("res://assets/west_cape/cape_turf.png"))
		material.set_shader_parameter("east_brush",preload("res://assets/full_island_ink/east_ground.png"))
		material.set_shader_parameter("coastal_edge_enabled",str(instance.name)=="Fish_West_Continuous_Land")
		material.set_shader_parameter("coastal_edge_paint",preload("res://assets/original_coastal_rock/integrated_coast_paint.png"))
		material.set_shader_parameter("junction_edge_paint",preload("res://assets/coast_junction/junction_paint.png"))
		material.set_shader_parameter("shallow_cape_surface",preload("res://assets/shallow_cape/cape_surface.png"))
	elif title in ["Coast_Sculpted_Bedrock","InkIsland_Rock_Wash"]:
		material = ShaderMaterial.new()
		material.shader = preload("res://shaders/ink_island_bedrock.gdshader")
		material.set_shader_parameter("cliff_paint",preload("res://assets/full_island_ink/cliff_wash.png"))
		material.set_shader_parameter("use_vertex_wash",title == "Coast_Sculpted_Bedrock")
	elif title.begins_with("InkCampfire_"):
		material = ShaderMaterial.new()
		material.shader = preload("res://shaders/ink_campfire.gdshader")
		material.set_shader_parameter("use_texture",source.albedo_texture != null)
		if source.albedo_texture != null:
			material.set_shader_parameter("brush_color",source.albedo_texture)
	elif title == "ForestRock_Moss":
		material = ShaderMaterial.new()
		material.shader = preload("res://shaders/forest_rock.gdshader")
		material.set_shader_parameter("brush_color",source.albedo_texture)
	elif title.begins_with("InkSample_Rock_"):
		material = ShaderMaterial.new()
		material.shader = preload("res://shaders/ink_sample_rock.gdshader")
		material.set_shader_parameter("brush_color",source.albedo_texture)
	elif title in ["InkSample_Bamboo_Stem","InkSample_Bamboo_Leaf","InkSample_Grass"]:
		material = ShaderMaterial.new()
		material.shader = preload("res://shaders/ink_sample_bamboo.gdshader")
		material.set_shader_parameter("is_leaf",title == "InkSample_Bamboo_Leaf")
		material.set_shader_parameter("is_grass",title == "InkSample_Grass")
		if str(instance.name).begins_with("ValleyDepth_"):
			material.set_shader_parameter("depth_haze",float(instance.get_meta("valley_depth_layer",0))*.14)
		elif instance.has_meta("forest_visibility_layer"):
			material.set_shader_parameter("depth_haze",float(instance.get_meta("forest_visibility_layer",0))*.11)
	else:
		return false
	instance.set_surface_override_material(surface,material)
	return true
