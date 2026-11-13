extends Node3D
## Local atmosphere only. All bamboo and ground geometry comes from Blender.
var daylight: Node
var openings: Array[SpotLight3D] = []
var targets: Array[Vector3] = []
var foreground_materials:Array[ShaderMaterial]=[]
func configure() -> void:
	var haze:=FogVolume.new()
	haze.name="BambooInteriorMist"
	haze.shape=RenderingServer.FOG_VOLUME_SHAPE_BOX
	haze.size=Vector3(30,14,14)
	haze.position=Vector3(-9,8.5,-7.5)
	var material:=ShaderMaterial.new()
	material.shader=preload("res://shaders/pixel_forest_mist.gdshader")
	haze.material=material
	add_child(haze)
	daylight=get_parent().atmosphere
	for mesh in get_parent().find_children("ForestForeground_*","MeshInstance3D",true,false):
		var mat:ShaderMaterial=mesh.get_active_material(0)
		if mat:foreground_materials.append(mat)
	# Local shafts through canopy gaps use the existing sun direction. These
	# illuminate real surfaces and cast alpha-cutout culm/leaf shadows.
	for target in [Vector3(-12.8,1.86,.1),Vector3(-7.0,1.86,-.5),Vector3(-1.5,1.86,-.2),Vector3(-10,3.0,-5.3),Vector3(-3.5,6.1,-8.0)]:
		var light:=SpotLight3D.new()
		light.name="CanopyOpening%d"%openings.size()
		light.spot_range=34.0
		light.spot_angle=15.0 if openings.size()<3 else 12.0
		light.spot_angle_attenuation=1.4
		light.spot_attenuation=.55
		light.light_specular=0.0
		light.light_volumetric_fog_energy=1.3
		light.shadow_enabled=true
		light.shadow_bias=.025
		light.shadow_normal_bias=.12
		add_child(light)
		openings.append(light);targets.append(target)
	_update_sun_openings()

func _update_sun_openings() -> void:
	for i in openings.size():
		var light:SpotLight3D=openings[i]
		light.position=targets[i]+Vector3(-7.0,12.0,-4.0)
		light.look_at(targets[i])
		light.light_color=daylight.sun.light_color.lerp(Color("e4dfb2"),.30)
		light.light_energy=daylight.sun.light_energy*(2.0 if i<3 else 1.6)*(1.0-daylight.clouds*.85)

func _process(_delta:float) -> void:
	_update_sun_openings()
	var actor:AnimatedSprite3D=get_parent().hero
	if actor:
		for mat in foreground_materials:mat.set_shader_parameter("actor_position",actor.global_position)
