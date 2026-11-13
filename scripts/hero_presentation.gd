extends RefCounted
## Upright sprite with a stable root and a small lower-leg contact warp.

const WALK_PITCH := deg_to_rad(8.0)
const CONTACT_SPAN := .70
const CONTACT_SAMPLES := 65
const LEG_BLEND_HEIGHT := .72
const MAX_FOOT_OFFSET := .34

var island: Node3D
var actor: AnimatedSprite3D
var surface = preload("res://scripts/hero_surface_sampler.gd").new()
var material: ShaderMaterial
var contacts: Dictionary
var normal_atlases: Dictionary = {}
var surface_atlases: Dictionary = {}
var current_key := ""
var lift := 0.0
var target_lift := 0.0
var foot_center := 0.0
var contact_point := Vector3.ZERO
var pitch := 0.0
var roll := 0.0
var view_alignment_roll := 0.0
var last_position := Vector3(INF,INF,INF)
var last_frame_data: Dictionary = {}
var shoe_shadows: Array[MeshInstance3D]=[]
var contact_curve := PackedFloat32Array()
var support_position := Vector3(INF,INF,INF)
var support_basis := Basis.IDENTITY
var support_height := 0.0

func configure(scene: Node3D) -> void:
	island=scene
	actor=island.hero
	surface.configure(island.get_node("World3D"))
	contacts=JSON.parse_string(FileAccess.get_file_as_string("res://assets/characters/volume_support/contacts.json"))
	contact_curve.resize(CONTACT_SAMPLES)
	for direction in ["right","up","down"]:
		for suffix in ["00","01","idle"]:
			var key: String=direction+"_"+suffix
			normal_atlases[key]=load("res://assets/characters/volume_support/"+key+"_normal.png")
		# Standing references have individually authored head/limb/cloth directions.
		normal_atlases[direction+"_idle"]=load("res://assets/characters/standing_surface/"+direction+"_idle_normal.png")
		surface_atlases[direction+"_idle"]=load("res://assets/characters/standing_surface/"+direction+"_idle_surface.png")
	material=ShaderMaterial.new()
	material.shader=preload("res://shaders/hero_volume.gdshader")
	material.set_shader_parameter("sprite_pixel_size",actor.pixel_size)
	material.set_shader_parameter("leg_blend_height",LEG_BLEND_HEIGHT*island.HERO_VISUAL_SCALE)
	material.set_shader_parameter("sprite_offset",actor.offset)
	material.set_shader_parameter("foot_curve",contact_curve)
	actor.material_override=material
	actor.billboard=BaseMaterial3D.BILLBOARD_DISABLED
	actor.extra_cull_margin=.4
	actor.frame_changed.connect(_sync_texture)
	actor.animation_changed.connect(_sync_texture)
	actor.sprite_frames_changed.connect(_sync_texture)
	# Reuse the existing Blender-authored contact disk; these are scene instances.
	for i in 2:
		var shoe:=MeshInstance3D.new()
		shoe.name="SoleContact%d"%i
		shoe.mesh=island.contact_shadow.mesh
		shoe.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		var mat:=ShaderMaterial.new()
		mat.shader=preload("res://shaders/hero_ground_contact.gdshader")
		mat.set_shader_parameter("strength",.36)
		mat.set_shader_parameter("sole_contact",.20)
		shoe.material_override=mat
		island.add_child(shoe)
		shoe_shadows.append(shoe)
	_sync_texture()

func _sync_texture() -> void:
	if not actor.sprite_frames.has_animation(actor.animation):return
	if actor.frame>=actor.sprite_frames.get_frame_count(actor.animation):return
	var texture: Texture2D=actor.sprite_frames.get_frame_texture(actor.animation,actor.frame)
	if texture==null:return
	var base: Texture2D=texture.atlas if texture is AtlasTexture else texture
	material.set_shader_parameter("color_atlas",base)
	var region: Rect2=texture.region if texture is AtlasTexture else Rect2(Vector2.ZERO,texture.get_size())
	material.set_shader_parameter("frame_uv_rect",Vector4(region.position.x/base.get_width(),region.position.y/base.get_height(),region.size.x/base.get_width(),region.size.y/base.get_height()))
	material.set_shader_parameter("frame_size",region.size)
	var key:=base.resource_path.get_file().get_basename()
	var supported: bool = base.resource_path.contains("/green_three_walk/") and normal_atlases.has(key)
	material.set_shader_parameter("has_volume",supported)
	if supported:material.set_shader_parameter("volume_atlas",normal_atlases[key])
	material.set_shader_parameter("has_surface",supported and surface_atlases.has(key))
	if supported and surface_atlases.has(key):material.set_shader_parameter("surface_atlas",surface_atlases[key])
	current_key=str(actor.animation)+":"+str(actor.frame)
	last_frame_data={}
	if contacts.has(str(actor.animation)) and actor.frame < contacts[str(actor.animation)].size():
		last_frame_data=contacts[str(actor.animation)][actor.frame]

func _update_contact_curve(right: Vector3,up: Vector3) -> void:
	if actor.position.is_equal_approx(support_position) and actor.basis.is_equal_approx(support_basis):
		return
	support_height=float(ground(actor.position.x,actor.position.z).height)+.008
	var anchor:=Vector3(actor.position.x,support_height,actor.position.z)
	var step:=2.0*CONTACT_SPAN/float(CONTACT_SAMPLES-1)
	for i in CONTACT_SAMPLES:
		var point:=anchor+right*(-CONTACT_SPAN+step*i)
		var offset:=0.0
		# Intersect the existing sprite plane with the imported walkable surface.
		for iteration in 2:
			var probe:=point+up*offset
			offset=(float(ground(probe.x,probe.z).height)+.008-point.y)/up.y
		var probe:=point+up*offset
		# Span one sample interval so smaller shoes cannot fall between edge probes.
		for side in [-1.0,-.5,.5,1.0]:
			var adjacent: Vector3=probe+right*(step*side)
			offset=maxf(offset,(float(ground(adjacent.x,adjacent.z).height)+.008-point.y)/up.y)
		contact_curve[i]=clampf(offset,-MAX_FOOT_OFFSET,MAX_FOOT_OFFSET)
	support_position=actor.position
	support_basis=actor.basis
	material.set_shader_parameter("foot_curve",contact_curve)

func foot_offset(local_x: float) -> float:
	var index:=clampf((local_x+CONTACT_SPAN)/(2.0*CONTACT_SPAN)*(CONTACT_SAMPLES-1),0.0,CONTACT_SAMPLES-1.0)
	var a:=mini(int(index),CONTACT_SAMPLES-2)
	return lerpf(contact_curve[a],contact_curve[a+1],index-a)

func grounded_local_y(local_x: float,local_y: float) -> float:
	return local_y+foot_offset(local_x)*clampf(1.0-local_y/(LEG_BLEND_HEIGHT*island.HERO_VISUAL_SCALE),0.0,1.0)

func ground(x: float,z: float) -> Dictionary:
	var hit: Dictionary=surface.sample(x,z)
	if not hit.is_empty():return hit
	# Only a fallback outside the traversable imported surfaces.
	var y: float=island._height(x,z)
	if x>4.2 and x<14.5:y=island._bridge_y(x)+.045
	return {"height":y,"normal":Vector3.UP,"surface":"fallback","gap":false}

func update(delta: float,snap := false) -> void:
	if current_key!=str(actor.animation)+":"+str(actor.frame):_sync_texture()
	var resting:=actor.animation==&"rest_rise_right"
	var camera: Camera3D=island.camera
	var right:=camera.global_basis.x
	right.y=0.0
	right=right.normalized()
	var back:=right.cross(Vector3.UP).normalized()
	var camera_pitch:=asin(clampf(camera.global_basis.z.y,-1,1))
	# Standing artwork keeps the same upright support in the opening and walk.
	# Only the lying/rising sheet eases from a camera-facing presentation.
	pitch=WALK_PITCH
	if resting:pitch=lerpf(camera_pitch,pitch,smoothstep(60.0,102.0,float(actor.frame)+actor.frame_progress))
	var up:=Vector3.UP*cos(pitch)-back*sin(pitch)
	var front:=right.cross(up).normalized()
	roll=0.0
	# An off-centre perspective shot projects a world-upright card diagonally.
	# Align its screen vertical while keeping the feet as the rotation anchor.
	# This is camera compensation, not ground-slope following or frame scaling.
	var camera_position:=camera.to_local(actor.global_position)
	var depth:=maxf(.1,-camera_position.z)
	var vertical_dx:=camera.global_basis.x.dot(up)*depth+camera_position.x*camera.global_basis.z.dot(up)
	var horizontal_dx:=camera.global_basis.x.dot(right)*depth+camera_position.x*camera.global_basis.z.dot(right)
	var standing_weight:=smoothstep(60.0,102.0,float(actor.frame)+actor.frame_progress) if resting else 1.0
	view_alignment_roll=atan2(vertical_dx,horizontal_dx)*island.cape_opening*standing_weight
	var aligned_right:=right*cos(view_alignment_roll)+up*sin(view_alignment_roll)
	up=up*cos(view_alignment_roll)-right*sin(view_alignment_roll)
	right=aligned_right
	actor.basis=Basis(right,up,front)
	material.set_shader_parameter("mirror_sign",-1.0 if actor.flip_h else 1.0)
	material.set_shader_parameter("sprite_tint",actor.modulate)
	target_lift=0.0
	var weighted_x:=0.0
	var total_weight:=0.0
	if not resting and not last_frame_data.is_empty():
		_update_contact_curve(right,up)
		target_lift=support_height-actor.position.y
		for foot: Dictionary in last_frame_data.feet:
			var weight:=exp(-(724.0-float(foot.y))/8.0)
			weighted_x+=(float(foot.x)-256.0)*actor.pixel_size*(-1.0 if actor.flip_h else 1.0)*weight
			total_weight+=weight
	var foot_target:=weighted_x/maxf(total_weight,.001)
	var teleported:=last_position.distance_to(actor.position)>1.0
	if resting:
		# No sole locking or frame-by-frame normalisation of the opening action.
		lift=0.0
		foot_center=0.0
	elif snap or teleported:
		lift=target_lift
		foot_center=foot_target
	else:
		# Raise immediately to prevent clipping; ease a descending correction.
		lift=maxf(target_lift,lerpf(lift,target_lift,1.0-exp(-18.0*delta)))
		foot_center=lerpf(foot_center,foot_target,1.0-exp(-16.0*delta))
	material.set_shader_parameter("ground_lift",lift)
	contact_point=actor.position+right*foot_center
	contact_point.y=float(ground(contact_point.x,contact_point.z).height)+.012
	for i in 2:
		var shoe:=shoe_shadows[i]
		shoe.visible=not resting and last_frame_data.get("feet",[]).size()>i
		if not shoe.visible:continue
		var foot: Dictionary=last_frame_data.feet[i]
		var px: float=(float(foot.x)-256.0)*actor.pixel_size*(-1 if actor.flip_h else 1)
		var py: float=(724.0-float(foot.y))*actor.pixel_size
		py=grounded_local_y(px,py)
		var point:=actor.position+right*px+up*py+Vector3.UP*lift
		var hit:=ground(point.x,point.z)
		var separation:=maxf(0.0,point.y-float(hit.height))
		point.y=float(hit.height)+.018
		var normal: Vector3=hit.normal
		var along: Vector3=(right-normal*normal.dot(right)).normalized()
		# Compact per-shoe support avoids a broad dark oval between the feet.
		var width:=clampf(float(foot.width)*actor.pixel_size*1.12,.17*island.HERO_VISUAL_SCALE,.34*island.HERO_VISUAL_SCALE)
		var size:=Vector3(width/.66,1,.50*island.HERO_VISUAL_SCALE)
		shoe.global_transform=Transform3D(Basis(along,normal,along.cross(normal)).scaled_local(size),point)
		var mat:=shoe.material_override as ShaderMaterial
		var contact:=exp(-separation*16.0)
		mat.set_shader_parameter("strength",.43*contact)
		mat.set_shader_parameter("sole_contact",.43*contact)
	last_position=actor.position

func debug_state() -> Dictionary:
	var shoe_data: Array=[]
	for shoe in shoe_shadows:
		shoe_data.append({"visible":shoe.visible,"point":str(shoe.position),"screen":str(island.camera.unproject_position(shoe.position)),"strength":shoe.material_override.get_shader_parameter("strength")})
	var screen_up:Vector2=island.camera.unproject_position(actor.position+actor.basis.y*1.5)-island.camera.unproject_position(actor.position)
	return {"pitch_degrees":rad_to_deg(pitch),"slope_roll_degrees":rad_to_deg(roll),"view_alignment_degrees":rad_to_deg(view_alignment_roll),"screen_vertical_drift_px":screen_up.x,"lift_m":lift,"target_lift_m":target_lift,
		"contact":str(contact_point),"surface":ground(actor.position.x,actor.position.z).surface,
		"triangle_count":surface.triangle_count,"normal_key":current_key,"shoe_shadows":shoe_data}
