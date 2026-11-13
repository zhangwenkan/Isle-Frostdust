extends RefCounted
## Blender-authored reconstruction; this script supplies materials and route metadata.
const NAMES=["Ground","Forest_Terrace","Masonry","Pool","Right_Canopy","Left_Trunk_Roots","Middle_Trunk_Roots","Back_Trunk","Front_Trunk_Roots","Timber_Aqueduct","Falling_Water","Pool_Rim","Reeds_West","Reeds_Centre","Reeds_Back","Reeds_Front"]
static func configure(instance:MeshInstance3D)->void:
	var mat:=ShaderMaterial.new()
	if instance.name=="Spring_Approach_Ground":
		mat.shader=preload("res://shaders/east_spring_approach.gdshader")
		mat.set_shader_parameter("old_turf",preload("res://assets/full_island_ink/east_ground.png"))
		mat.set_shader_parameter("spring_paint",preload("res://assets/east_spring/spring_paint.png"))
	else:
		mat.shader=preload("res://shaders/east_spring_paint.gdshader")
		var imported:=instance.mesh.surface_get_material(0) as StandardMaterial3D
		mat.set_shader_parameter("source_paint",imported.albedo_texture if imported!=null else preload("res://assets/east_spring/spring_paint.png"))
		mat.set_shader_parameter("component",NAMES.find(str(instance.name).trim_prefix("Spring_")))
	instance.material_override=mat
	instance.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
static func path_z(x:float)->float:
	if x<=24.2:return .4+sin(x*.25)*.44
	if x<29.0:return lerpf(.4+sin(24.2*.25)*.44,3.24,smoothstep(24.2,29.0,x))
	return lerpf(3.24,.8,smoothstep(29.0,34.0,x))
