extends RefCounted
## Blender components, ordinary lighting, localized plant and spring-water motion.
static func configure(instance:MeshInstance3D)->void:
	var title:=str(instance.name)
	if title in ["ForestSpring_Pool","ForestSpring_Falling_Water","ForestSpring_Channel_Water"]:
		var water:=ShaderMaterial.new()
		water.shader=preload("res://shaders/forest_spring_water.gdshader")
		water.set_shader_parameter("component",0 if title=="ForestSpring_Pool" else (1 if title=="ForestSpring_Falling_Water" else 2))
		instance.material_override=water
		instance.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		return
	for surface in instance.mesh.get_surface_count():
		var imported:=instance.mesh.surface_get_material(surface) as StandardMaterial3D
		if imported==null:continue
		if imported.resource_name.begins_with("FS_Flower_"):
			var flower:=imported.duplicate() as StandardMaterial3D
			flower.cull_mode=BaseMaterial3D.CULL_DISABLED
			flower.roughness=1.0
			instance.set_surface_override_material(surface,flower)
			continue
		var component: int={"FS_Floor":0,"FS_Stone":1,"FS_Bark":2,"FS_Leaf":3,"FS_Grass":4,"FS_Moss":4}.get(imported.resource_name,1)
		var mat:=ShaderMaterial.new()
		mat.shader=preload("res://shaders/forest_spring_surface.gdshader")
		mat.set_shader_parameter("component_paint",imported.albedo_texture)
		mat.set_shader_parameter("component",component)
		instance.set_surface_override_material(surface,mat)

static func path_z(x:float)->float:
	var t:=smoothstep(24.2,29.0,x)
	return lerpf(.4+sin(24.2*.25)*.44,2.1,t)-.7*smoothstep(29.0,34.0,x)

static func add_pool_fill(parent:Node3D)->void:
	var fill:=SpotLight3D.new()
	fill.name="SpringCanopyOpeningLight"
	parent.add_child(fill)
	fill.position=Vector3(34.2,4.8,1.8)
	fill.look_at(Vector3(35.2,1.0,-2.2))
	fill.light_color=Color("e0d7ac")
	fill.light_energy=2.3
	fill.light_specular=.25
	fill.spot_range=10.0
	fill.spot_angle=55.0
	fill.spot_angle_attenuation=1.6
	fill.shadow_enabled=true
