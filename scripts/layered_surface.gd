extends RefCounted
## Reads the triangles authored in Blender; does not construct mesh geometry.
const CELL=0.5
var buckets:Dictionary={}
var triangle_count=0
var surfaces:Array[String]=[]
func configure(node:Node)->void:
	if node is MeshInstance3D and (str(node.name).begins_with("WALK_") or str(node.name)=="SUPPORT_Bridge"):
		surfaces.append(str(node.name))
		var faces:PackedVector3Array=node.mesh.get_faces()
		var priority=4 if node.name=="SUPPORT_Bridge" else 3
		for i in range(0,faces.size(),3):
			var a:Vector3=node.global_transform*faces[i]
			var b:Vector3=node.global_transform*faces[i+1]
			var c:Vector3=node.global_transform*faces[i+2]
			var den=(b.z-c.z)*(a.x-c.x)+(c.x-b.x)*(a.z-c.z)
			if absf(den)<0.000001:continue
			var tri={"a":a,"b":b,"c":c,"den":den,"priority":priority,"surface":str(node.name)}
			triangle_count+=1
			for x in range(floori(minf(a.x,minf(b.x,c.x))/CELL),floori(maxf(a.x,maxf(b.x,c.x))/CELL)+1):
				for z in range(floori(minf(a.z,minf(b.z,c.z))/CELL),floori(maxf(a.z,maxf(b.z,c.z))/CELL)+1):
					var key=Vector2i(x,z)
					if not buckets.has(key):buckets[key]=[]
					buckets[key].append(tri)
	for child in node.get_children():configure(child)
func sample(pos:Vector3)->Dictionary:
	var result:Dictionary={}
	var best_priority=0
	var highest=-INF
	for tri:Dictionary in buckets.get(Vector2i(floori(pos.x/CELL),floori(pos.z/CELL)),[]):
		var a:Vector3=tri.a;var b:Vector3=tri.b;var c:Vector3=tri.c
		var u=((b.z-c.z)*(pos.x-c.x)+(c.x-b.x)*(pos.z-c.z))/tri.den
		var v=((c.z-a.z)*(pos.x-c.x)+(a.x-c.x)*(pos.z-c.z))/tri.den
		if u<-.0001 or v<-.0001 or u+v>1.0001:continue
		var y:float=u*a.y+v*b.y+(1.-u-v)*c.y
		if tri.priority>best_priority or (tri.priority==best_priority and y>highest):
			best_priority=tri.priority;highest=y;result={"height":y,"surface":tri.surface}
	return result
