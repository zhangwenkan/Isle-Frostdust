extends Node3D
## Animates imported fire/smoke/ember carriers; creates no model geometry.
var fire_light:OmniLight3D
var embers:Array[MeshInstance3D]=[]
var time=0.0
func configure(island:Node3D)->void:
	var center:Vector3=island.v3(island.layout.reference_cape.fire_center)
	position=Vector3.ZERO
	fire_light=OmniLight3D.new();fire_light.name="CapeFireLight";fire_light.position=center+Vector3(0,.55,0)
	fire_light.light_color=Color("ffad57");fire_light.light_energy=1.8;fire_light.omni_range=3.5
	fire_light.shadow_enabled=true;fire_light.shadow_bias=.02;fire_light.shadow_normal_bias=.10;add_child(fire_light)
	var sunset=SpotLight3D.new();sunset.name="CapeWarmRim";sunset.position=Vector3(-94,16,-3)
	if island.layout.reference_cape.has("rocky_terminus"):sunset.position=center+Vector3(-11,9,10)
	sunset.light_color=Color("f2c895");sunset.light_energy=.85;sunset.spot_range=35;sunset.spot_angle=37
	sunset.spot_angle_attenuation=1.3;sunset.shadow_enabled=true;sunset.shadow_bias=.025;sunset.shadow_normal_bias=.10
	add_child(sunset);sunset.look_at(island.get_node("World").to_global(Vector3(-76,3.3,-8)))
	if island.layout.reference_cape.has("rocky_terminus"):sunset.look_at(island.get_node("World").to_global(center+Vector3(0,-2,1)))
	for node in island.get_node("World").find_children("Cape_Ember_*","MeshInstance3D",true,false):embers.append(node)
func _process(delta:float)->void:
	time+=delta
	if fire_light:fire_light.light_energy=1.62+.14*sin(time*8.7)+.11*sin(time*13.3+1.1)
	for i in embers.size():
		var phase=fmod(time*(.35+float(i%3)*.055)+float(i)*.173,1.0)
		embers[i].position=Vector3(embers[i].get_meta("fire_origin_offset",Vector3.ZERO))+Vector3(sin(phase*4.0+float(i))*phase*.30,phase*2.8,-phase*.18)
		embers[i].visible=phase<.83
