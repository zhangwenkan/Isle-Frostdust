extends RefCounted
## Rendering integration for the original Sumiro environment recipes.
## Geometry is imported from the Blender MCP-authored master GLB.

var cache: Dictionary = {}
var noise: ImageTexture3D
var sun_direction := Vector3(0.3,0.8,0.5).normalized()

func _noise() -> ImageTexture3D:
	if noise == null:
		var atlas := (load("res://assets/sumiro/ink_noise_slices.png") as Texture2D).get_image()
		atlas.convert(Image.FORMAT_L8)
		var slices: Array[Image] = []
		for z in 64:
			slices.append(atlas.get_region(Rect2i(0,z*64,64,64)))
		noise = ImageTexture3D.new()
		assert(noise.create(Image.FORMAT_L8,64,64,64,false,slices) == OK)
	return noise

func configure(instance: MeshInstance3D) -> bool:
	var handled := false
	for surface in instance.mesh.get_surface_count():
		var imported := instance.mesh.surface_get_material(surface) as StandardMaterial3D
		if imported == null or not imported.resource_name.begins_with("Sumiro_"):
			continue
		handled = true
		var key := imported.resource_name
		if cache.has(key):
			instance.set_surface_override_material(surface,cache[key])
			continue
		var mat := ShaderMaterial.new()
		if key.begins_with("Sumiro_Hill_"):
			mat.shader = preload("res://shaders/sumiro_hill.gdshader")
			mat.render_priority = 10
			mat.set_shader_parameter("painting",imported.albedo_texture)
			instance.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		else:
			mat.shader = preload("res://shaders/sumiro_ink.gdshader")
			mat.set_shader_parameter("tInkNoise",_noise())
			mat.set_shader_parameter("uSunDir",sun_direction)
			mat.set_shader_parameter("uInkBold",0.35)
			mat.set_shader_parameter("has_map",imported.albedo_texture != null)
			if imported.albedo_texture != null:
				mat.set_shader_parameter("look_map",imported.albedo_texture)
			mat.set_shader_parameter("base_color",Vector3(imported.albedo_color.r,imported.albedo_color.g,imported.albedo_color.b))
			if "Path" in key or "Cliff_Base" in key:
				mat.set_shader_parameter("use_paint",false)
				mat.set_shader_parameter("base_ground",true)
				mat.set_shader_parameter("ground_project",true)
				mat.set_shader_parameter("uRampBias",0.20)
				mat.set_shader_parameter("uRampScale",0.8)
				mat.set_shader_parameter("uSkyFill",0.5)
				mat.set_shader_parameter("uCavityK",0.5)
				mat.set_shader_parameter("uDryDirect",0.0)
				mat.set_shader_parameter("uStainAmt",0.14)
				mat.set_shader_parameter("uStainFreq",0.34)
				mat.set_shader_parameter("uGrainAmp",0.03)
				mat.set_shader_parameter("uBrushAmt",0.08)
				mat.set_shader_parameter("uStep",0.2)
			elif "Pine" in key or "Bridge" in key or "Grass" in key:
				mat.set_shader_parameter("use_paint",false)
				mat.set_shader_parameter("uUseRamp",0.0)
				mat.set_shader_parameter("uLookMap",0.0)
				mat.set_shader_parameter("uFacetAmt",0.0)
				mat.set_shader_parameter("uInkBold",0.0)
				mat.set_shader_parameter("uSkyFill",0.45)
				mat.set_shader_parameter("uGrainAmp",0.04)
				mat.set_shader_parameter("uWashWarp",0.1)
				if "Grass" in key:
					mat.set_shader_parameter("grass",true)
					mat.set_shader_parameter("uShadeTint",Vector3(.9,.9,.9))
				if "Needles" in key:
					mat.set_shader_parameter("foliage",true)
					mat.set_shader_parameter("uShadeTint",Vector3(.82,.84,.84))
					mat.set_shader_parameter("uWrap",0.8)
					mat.set_shader_parameter("uSkyFill",0.5)
				elif "Root" in key:
					mat.set_shader_parameter("uShadeTint",Vector3(.8,.8,.8))
				elif "Bridge" in key:
					mat.set_shader_parameter("uShadeTint",Vector3(.62,.60,.58))
			if "Face" in key:
				mat.set_shader_parameter("uWrap",0.35)
				mat.set_shader_parameter("uSkyFill",0.6)
				mat.set_shader_parameter("uCavityK",0.5)
			if "Lobe" in key:
				mat.set_shader_parameter("uWrap",0.3)
				mat.set_shader_parameter("uSkyFill",0.55)
				mat.set_shader_parameter("uCavityK",0.45)
		cache[key] = mat
		instance.set_surface_override_material(surface,mat)
	return handled
