extends Node
## Shared daytime lighting: solar angle, sky illumination and cloud cover.
## This controls the current coastal scene; it is not a rain or weather scheduler.

var environment: Environment
var sky_material: ProceduralSkyMaterial
var sky_cloud_material: ShaderMaterial
var sun: DirectionalLight3D
var hour := 10.5
var clouds := 0.22
var water_materials: Array[ShaderMaterial] = []
var mountain_cloud_material: ShaderMaterial
var cape_opening := 0.0
var base_sun_rotation := Vector3.ZERO
var base_sun_color := Color.WHITE
var base_sun_energy := 1.0
var base_ambient_energy := 0.5

func configure(day_hour: float, cloud_cover: float) -> void:
	environment = Environment.new()
	environment.background_mode = Environment.BG_SKY
	var sky := Sky.new()
	sky_material = ProceduralSkyMaterial.new()
	sky_cloud_material = ShaderMaterial.new()
	sky_cloud_material.shader = preload("res://shaders/coastal_moving_sky.gdshader")
	sky.sky_material = sky_cloud_material
	sky.radiance_size = Sky.RADIANCE_SIZE_256
	sky.process_mode = Sky.PROCESS_MODE_REALTIME
	environment.sky = sky
	environment.ambient_light_source = Environment.AMBIENT_SOURCE_SKY
	environment.ambient_light_sky_contribution = 1.0
	environment.reflected_light_source = Environment.REFLECTION_SOURCE_SKY
	environment.tonemap_mode = Environment.TONE_MAPPER_ACES
	environment.tonemap_exposure = 1.0
	environment.glow_enabled = false
	environment.fog_enabled = true
	environment.fog_density = 0.0008
	environment.fog_light_color = Color("b7d4d8")
	environment.fog_light_energy = 0.8
	environment.fog_sun_scatter = 0.08
	environment.fog_sky_affect = 0.0
	environment.volumetric_fog_enabled = true
	environment.volumetric_fog_density = 0.0
	environment.volumetric_fog_length = 260.0
	environment.volumetric_fog_detail_spread = 1.0
	environment.volumetric_fog_ambient_inject = 0.7
	environment.volumetric_fog_temporal_reprojection_enabled = true
	var cloud_bank := FogVolume.new()
	cloud_bank.name = "MountainCloudSea"
	cloud_bank.shape = RenderingServer.FOG_VOLUME_SHAPE_BOX
	cloud_bank.size = Vector3(420.0, 40.0, 300.0)
	cloud_bank.position = Vector3(0.0, 0.0, -130.0)
	mountain_cloud_material = ShaderMaterial.new()
	mountain_cloud_material.shader = preload("res://shaders/mountain_cloud_bank.gdshader")
	cloud_bank.material = mountain_cloud_material
	add_child(cloud_bank)
	environment.ssao_enabled = true
	environment.ssao_radius = 0.65
	environment.ssao_intensity = 0.45
	environment.ssao_power = 1.0
	environment.ssao_light_affect = 0.12
	environment.ssil_enabled = true
	environment.ssil_radius = 2.0
	environment.ssil_intensity = 0.35
	environment.ssil_sharpness = 0.6
	var world := WorldEnvironment.new()
	world.name = "CoastalSky"
	world.environment = environment
	add_child(world)
	sun = DirectionalLight3D.new()
	sun.name = "CoastalSun"
	sun.shadow_enabled = true
	sun.light_specular = 0.45
	sun.directional_shadow_mode = DirectionalLight3D.SHADOW_PARALLEL_4_SPLITS
	sun.directional_shadow_max_distance = 58.0
	sun.directional_shadow_blend_splits = true
	sun.shadow_bias = 0.06
	sun.shadow_normal_bias = 0.65
	add_child(sun)
	apply(day_hour, cloud_cover)

func apply(day_hour: float, cloud_cover: float) -> void:
	hour = clampf(day_hour, 7.0, 17.0)
	clouds = clampf(cloud_cover, 0.0, 1.0)
	var elevation := sin((hour - 6.0) / 12.0 * PI) * 42.0
	var daylight := smoothstep(8.0, 40.0, elevation)
	sun.rotation_degrees = Vector3(-elevation, -162.0 + (hour - 10.5) * 12.0, 0.0)
	sun.light_color = Color("eacbac").lerp(Color("fff3df"), daylight).lerp(Color("e8ece9"), clouds * 0.7)
	sun.light_energy = lerpf(1.15, 1.75, daylight) * lerpf(1.0, 0.30, clouds)
	sun.light_angular_distance = lerpf(1.3, 3.0, clouds)
	sun.shadow_opacity = lerpf(0.92, 0.65, clouds)
	sky_material.sky_top_color = Color("629cb8").lerp(Color("99a9b3"), clouds)
	sky_material.sky_horizon_color = Color("b7d4d8").lerp(Color("becbce"), clouds)
	sky_material.ground_bottom_color = Color("526965").lerp(Color("727d7b"), clouds)
	sky_material.ground_horizon_color = sky_material.sky_horizon_color
	sky_material.sky_curve = 0.28
	sky_material.ground_curve = 0.22
	sky_material.sky_energy_multiplier = 1.0
	sky_material.ground_energy_multiplier = 1.0
	for parameter in ["sky_top_color", "sky_horizon_color", "ground_bottom_color", "ground_horizon_color", "sky_curve", "ground_curve"]:
		sky_cloud_material.set_shader_parameter(parameter, sky_material.get(parameter))
	sky_cloud_material.set_shader_parameter("cloud_cover",lerpf(.44,.82,clouds))
	environment.ambient_light_energy = lerpf(0.48, 0.65, clouds)
	base_sun_rotation = sun.rotation_degrees
	base_sun_color = sun.light_color
	base_sun_energy = sun.light_energy
	base_ambient_energy = environment.ambient_light_energy
	environment.fog_light_color = sky_material.sky_horizon_color
	mountain_cloud_material.set_shader_parameter("cloud_color", Color("d5dfe0").lerp(Color("c7d1d5"), clouds))
	mountain_cloud_material.set_shader_parameter("sea_mist_color", Color("a0c3cc").lerp(Color("a7bec7"), clouds))
	mountain_cloud_material.set_shader_parameter("cloud_density", lerpf(0.065, 0.085, clouds))
	for material in water_materials:
		_update_water(material)
	set_cape_opening(cape_opening)

func set_cape_opening(weight: float) -> void:
	cape_opening = clampf(weight,0.0,1.0)
	# Keep one late-morning sun direction while the player travels inland.
	sun.rotation_degrees = base_sun_rotation
	sun.light_color = base_sun_color
	sun.light_energy = base_sun_energy*lerpf(1.0,1.08,cape_opening)
	environment.ambient_light_energy = base_ambient_energy*lerpf(1.0,1.08,cape_opening)
	environment.fog_density = lerpf(.0008,.00025,cape_opening)
	mountain_cloud_material.set_shader_parameter("cape_opening",cape_opening)
	for material in water_materials:
		material.set_shader_parameter("cape_opening",cape_opening)
		material.set_shader_parameter("sun_elevation_sine",sun.global_basis.z.y)

func configure_water(material: ShaderMaterial) -> void:
	if material not in water_materials:
		water_materials.append(material)
	material.set_shader_parameter("wave_slopes", preload("res://assets/water/coastal_wave_slopes.png"))
	_update_water(material)

func _update_water(material: ShaderMaterial) -> void:
	material.set_shader_parameter("sun_elevation_sine", sun.global_basis.z.y)
	material.set_shader_parameter("reflected_horizon", sky_material.sky_horizon_color)
	material.set_shader_parameter("reflected_zenith", sky_material.sky_top_color)
	material.set_shader_parameter("deep_color", Color("197b8b").lerp(Color("376775"), clouds * 0.65))
	material.set_shader_parameter("shallow_color", Color("38b4a0").lerp(Color("619e98"), clouds * 0.65))
	material.set_shader_parameter("wave_strength", lerpf(0.32, 0.40, clouds))
