extends RefCounted
## Read-only vertical queries on Blender's imported triangles. No mesh creation.

const CELL := .25
var buckets: Dictionary = {}
var surface_names: Array[String] = []
var triangle_count := 0

func configure(node: Node) -> void:
	if node is MeshInstance3D:
		var title := str(node.name)
		var plank := title.begins_with("Bridge_Plank_") and title.trim_prefix("Bridge_Plank_").is_valid_int()
		if title in ["Fish_West_Continuous_Land","Fish_East_Continuous_Land","ForestSpring_Ground"] or plank:
			surface_names.append(title)
			var faces: PackedVector3Array = node.mesh.get_faces()
			for i in range(0,faces.size(),3):
				var a: Vector3 = node.global_transform*faces[i]
				var b: Vector3 = node.global_transform*faces[i+1]
				var c: Vector3 = node.global_transform*faces[i+2]
				var normal := (b-a).cross(c-a).normalized()
				if absf(normal.y)<.25:continue
				if normal.y<0:normal=-normal
				var den := (b.z-c.z)*(a.x-c.x)+(c.x-b.x)*(a.z-c.z)
				if absf(den)<.000001:continue
				var tri := {"a":a,"b":b,"c":c,"den":den,"normal":normal,"name":title}
				triangle_count+=1
				for x in range(floori(minf(a.x,minf(b.x,c.x))/CELL),floori(maxf(a.x,maxf(b.x,c.x))/CELL)+1):
					for z in range(floori(minf(a.z,minf(b.z,c.z))/CELL),floori(maxf(a.z,maxf(b.z,c.z))/CELL)+1):
						var key:=Vector2i(x,z)
						if not buckets.has(key):buckets[key]=[]
						buckets[key].append(tri)
	for child in node.get_children():configure(child)

func exact(x: float,z: float) -> Dictionary:
	var result: Dictionary = {}
	var highest := -INF
	for tri: Dictionary in buckets.get(Vector2i(floori(x/CELL),floori(z/CELL)),[]):
		var a: Vector3=tri.a
		var b: Vector3=tri.b
		var c: Vector3=tri.c
		var u: float=((b.z-c.z)*(x-c.x)+(c.x-b.x)*(z-c.z))/tri.den
		var v: float=((c.z-a.z)*(x-c.x)+(a.x-c.x)*(z-c.z))/tri.den
		if u<-.0001 or v<-.0001 or u+v>1.0001:continue
		var y:=u*a.y+v*b.y+(1-u-v)*c.y
		if y>highest:
			highest=y
			result={"height":y,"normal":tri.normal,"surface":tri.name,"gap":false}
	return result

func sample(x: float,z: float) -> Dictionary:
	var hit:=exact(x,z)
	if not hit.is_empty() and (x<=4.0 or x>=14.8 or str(hit.surface).begins_with("Bridge_Plank_")):return hit
	# A shoe bridges a narrow board seam; never raycast down to the sea floor.
	# The closed island mesh can return its buried base through a seam, so a
	# nonempty terrain hit must still be checked against the adjacent deck.
	if x>4.0 and x<14.8:
		var used_adjacent:=false
		for dx in [-.045,.045,-.085,.085]:
			var adjacent:=exact(x+dx,z)
			if adjacent.is_empty():continue
			if not str(adjacent.surface).begins_with("Bridge_Plank_"):continue
			if hit.is_empty() or adjacent.height>hit.height:
				hit=adjacent
				used_adjacent=true
		if used_adjacent:hit["gap"]=true
	return hit
