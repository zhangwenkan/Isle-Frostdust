extends RefCounted
## Light the existing animated artwork without changing its geometry or frames.
var actor:AnimatedSprite3D
var material:ShaderMaterial
var source_keys:Dictionary={}
var normal_atlases:Dictionary={}
var current_source=""

func configure(scene:Node3D,keys:Dictionary)->void:
	actor=scene.hero
	source_keys=keys
	for key:String in source_keys.values():
		if normal_atlases.has(key):continue
		var path="res://assets/characters/volume_support/"+key+"_normal.png"
		if key.ends_with("_idle"):path="res://assets/characters/standing_surface/"+key+"_normal.png"
		if not ResourceLoader.exists(path):continue
		var image=(load(path) as Texture2D).get_image()
		image.generate_mipmaps()
		normal_atlases[key]=ImageTexture.create_from_image(image)
	material=ShaderMaterial.new()
	material.shader=preload("res://shaders/hero_forest_light.gdshader")
	material.set_shader_parameter("author_world_to_local",scene.get_node("World").global_transform.affine_inverse())
	actor.material_override=material
	actor.frame_changed.connect(_sync_texture)
	actor.animation_changed.connect(_sync_texture)
	actor.sprite_frames_changed.connect(_sync_texture)
	var sun=scene.get_node("CoastalSun") as DirectionalLight3D
	var ray:Vector3=(scene.get_node("World").global_basis.inverse()*(-sun.global_basis.z)).normalized()
	scene._register_forest_light_material(material,ray)
	_sync_texture()
	update()

func _sync_texture()->void:
	if not actor.sprite_frames.has_animation(actor.animation):return
	if actor.frame>=actor.sprite_frames.get_frame_count(actor.animation):return
	var texture=actor.sprite_frames.get_frame_texture(actor.animation,actor.frame)
	if texture==null:return
	var base:Texture2D=texture.atlas if texture is AtlasTexture else texture
	material.set_shader_parameter("color_atlas",base)
	current_source=str(source_keys.get(base.get_instance_id(),""))
	material.set_shader_parameter("has_volume",normal_atlases.has(current_source))
	if normal_atlases.has(current_source):material.set_shader_parameter("volume_atlas",normal_atlases[current_source])

func update()->void:
	material.set_shader_parameter("mirror_sign",-1.0 if actor.flip_h else 1.0)
	material.set_shader_parameter("sprite_tint",actor.modulate)
