extends Node3D
## Animates Blender-authored assets. Paths and joints contain no generated geometry.

const GULL := preload("res://assets/island_blender/coastal_gull.glb")
const LEAF := preload("res://assets/island_blender/breeze_leaf.glb")
# Separate paths let the flock open out in depth instead of keeping a ruler-straight row.
const FLOCK_ROUTES := [
	[Vector3(-2.3,5.5,-3.5), Vector3(6.0,5.7,4.0), Vector3(22.0,4.8,-14.0), Vector3(43.0,3.5,-86.0)],
	[Vector3(-1.0,5.9,-5.1), Vector3(8.0,7.0,-6.0), Vector3(12.0,4.4,-32.0), Vector3(24.0,3.3,-100.0)],
	[Vector3(-3.0,5.1,-3.9), Vector3(3.0,5.9,-0.5), Vector3(25.0,3.7,-23.0), Vector3(52.0,2.8,-93.0)],
	[Vector3(-0.4,5.4,-6.7), Vector3(5.0,6.2,-8.0), Vector3(16.0,5.2,-30.0), Vector3(34.0,4.0,-109.0)],
	[Vector3(-1.9,6.1,-4.8), Vector3(9.0,6.4,-2.0), Vector3(29.0,4.0,-19.0), Vector3(61.0,3.0,-89.0)]
]
const FLOCK_DELAYS := [0.0, 0.23, 0.57, 0.94, 1.28]
const FLOCK_DURATIONS := [14.6, 17.2, 15.4, 18.0, 16.1]
var elapsed := 0.0
var flock_started := -1000.0
var flock_count := 0
var flock_armed := true
var last_hero_x := -6.8
var gulls: Array[Dictionary] = []
var leaves: Array[Dictionary] = []
var enabled := true
var swimmers: Array[Dictionary] = []

func bind_underwater(world: Node3D) -> void:
	for i in 4:
		var fish := world.find_child("Fish_Underwater_Swimmer_%02d" % i,true,false) as Node3D
		if fish:
			swimmers.append({"node":fish,"origin":fish.position,"tail":fish.find_child("*Tail",true,false),"phase":float(i)*1.9})

func configure() -> void:
	for i in 8:
		var bird := GULL.instantiate() as Node3D
		bird.name = "LivingGull_%02d" % i
		add_child(bird)
		bird.scale = Vector3.ONE * (0.86 + float(i % 3) * 0.09)
		gulls.append({"node":bird, "left":bird.find_child("Wing_L",true,false), "right":bird.find_child("Wing_R",true,false), "tip_left":bird.find_child("Tip_L",true,false), "tip_right":bird.find_child("Tip_R",true,false), "phase":float(i)*1.73, "meshes":bird.find_children("*","MeshInstance3D",true,false)})
		assert(gulls[-1].left != null and gulls[-1].tip_right != null)
	for i in 8:
		var leaf := LEAF.instantiate() as Node3D
		leaf.name = "DriftingLeaf_%02d" % i
		add_child(leaf)
		leaves.append({"node":leaf,"meshes":leaf.find_children("*","MeshInstance3D",true,false)})
	advance(0.0, -6.8)

func _flight_pose(index: int, p: Vector3, ahead: Vector3, bank: float, energy: float) -> void:
	var data: Dictionary = gulls[index]
	var bird: Node3D = data.node
	var direction := (ahead-p).normalized()
	if direction.length_squared() < 0.5:
		direction = Vector3.FORWARD
	var orientation := Basis.looking_at(direction, Vector3.UP)
	var size := 0.86 + float(index % 3) * 0.09
	bird.transform = Transform3D(orientation * Basis(Vector3.FORWARD, bank), p).scaled_local(Vector3.ONE * size)
	var phase: float = elapsed * (7.2 + float(index % 3) * 0.45) + data.phase
	var stroke := sin(phase)
	var flap := stroke * energy
	data.left.rotation.z = -(0.09 + flap * 0.67)
	data.right.rotation.z = 0.09 + flap * 0.67
	data.tip_left.rotation.z = -(0.11 + sin(phase-0.50) * energy * 0.31)
	data.tip_right.rotation.z = 0.11 + sin(phase-0.50) * energy * 0.31

func _ambient_position(index: int, time: float) -> Vector3:
	var angle := time * (0.15 + float(index)*0.019) + float(index)*2.1
	return Vector3(4.0 + cos(angle)*(20.0+float(index)*5.0), 6.6+float(index)*0.55+sin(angle*2.0)*0.85, -20.0-float(index)*13.0+sin(angle)*(10.0+float(index)*3.0))

func _flock_position(index: int, u: float) -> Vector3:
	var lane := float(index)
	var route: Array = FLOCK_ROUTES[index]
	var start: Vector3 = route[0]
	var p := start.bezier_interpolate(route[1],route[2],route[3],u)
	p.y += sin(u*TAU*1.2+lane*0.7)*0.22*sin(u*PI)
	return p

func advance(delta: float, hero_x: float) -> void:
	if not enabled:
		return
	elapsed += delta
	for data in swimmers:
		var t: float = elapsed*0.31+data.phase
		var fish: Node3D = data.node
		fish.position = data.origin+Vector3(sin(t)*0.70,sin(t*1.3)*0.065,cos(t)*0.42)
		# The authored fish faces local -X; yaw follows its curved swimming path.
		fish.rotation.y = atan2(-sin(t)*0.42,-cos(t)*0.70)
		if data.tail:
			data.tail.rotation.y = sin(elapsed*6.3+data.phase)*0.18
	# A single approach event, followed by a long quiet interval and departure.
	if flock_armed and hero_x > -3.7 and hero_x < 1.6 and hero_x > last_hero_x + 0.001:
		flock_started = elapsed
		flock_count += 1
		flock_armed = false
	if not flock_armed and elapsed-flock_started > 55.0 and hero_x < -10.0:
		flock_armed = true
	last_hero_x = hero_x
	for i in 3:
		var p := _ambient_position(i,elapsed)
		var ahead := _ambient_position(i,elapsed+0.08)
		var cycle := 0.5+0.5*sin(elapsed*0.55+float(i)*2.4)
		var energy := lerpf(0.08,0.85,smoothstep(0.64,0.88,cycle))
		_flight_pose(i,p,ahead,sin(elapsed*0.15+float(i)*2.1)*0.28,energy)
	for j in 5:
		var index := j+3
		var bird: Node3D = gulls[index].node
		var age: float = elapsed-flock_started-FLOCK_DELAYS[j]
		var duration: float = FLOCK_DURATIONS[j]
		bird.visible = age >= 0.0 and age < duration
		if not bird.visible:
			continue
		var u := clampf(age/duration,0.0,1.0)
		var p := _flock_position(j,u)
		var ahead := _flock_position(j,minf(u+0.005,1.0))
		var energy := lerpf(1.0,0.35,smoothstep(1.5,7.0,age))
		energy *= lerpf(0.35,1.0,0.5+0.5*sin(age*1.3+float(j)))
		var later := _flock_position(j,minf(u+0.012,1.0))
		var heading := Vector3(ahead.x-p.x,0.0,ahead.z-p.z).normalized()
		var next_heading := Vector3(later.x-ahead.x,0.0,later.z-ahead.z).normalized()
		var bank := clampf(heading.signed_angle_to(next_heading,Vector3.UP)*-18.0,-0.48,0.48)
		_flight_pose(index,p,ahead,bank+0.05*sin(age+float(j)),energy)
		for part in gulls[index].meshes:
			part.transparency = smoothstep(0.84,1.0,u)
	for i in leaves.size():
		var data: Dictionary = leaves[i]
		var leaf: Node3D = data.node
		var cycle := fposmod(elapsed+float(i)*3.7,18.0+float(i)*0.8)
		leaf.visible = cycle < 8.0
		if not leaf.visible:
			continue
		var u := cycle/8.0
		var side := -7.0 if i < 4 else 18.5
		var z := 1.8 if i % 3 == 0 else -2.5
		var base_y := 3.5 if i < 4 else 1.6
		leaf.position = Vector3(side+float(i%4)*0.8+u*2.5+sin(u*TAU)*0.45,base_y+3.0-u*3.8+sin(u*TAU*1.5)*0.18,z+sin(u*PI)*1.0)
		leaf.rotation = Vector3(elapsed*1.1+float(i),sin(elapsed*0.6+float(i))*1.3,elapsed*0.7+float(i)*2.0)
		var opacity := smoothstep(0.0,0.12,u)*(1.0-smoothstep(0.80,1.0,u))
		for part in data.meshes:
			part.transparency = 1.0-opacity

func debug_state() -> Dictionary:
	var positions: Array = []
	for data in gulls:
		positions.append({"visible":data.node.visible,"position":str(data.node.position),"wing_angle":data.left.rotation.z})
	return {"elapsed":elapsed,"flock_events":flock_count,"flock_armed":flock_armed,"gulls":positions}
