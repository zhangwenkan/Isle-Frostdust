extends SceneTree
const OUT="res://artifacts/hero-forest-light-review/"
func _initialize():call_deferred("run")
func capture(viewport:SubViewport,path:String)->void:
	await process_frame
	RenderingServer.force_draw(false)
	assert(viewport.get_texture().get_image().save_png(OUT+path)==OK)
func run()->void:
	DirAccess.make_dir_recursive_absolute(OUT+"frame-check")
	var island=load("res://scenes/layered_island.tscn").instantiate();root.add_child(island);current_scene=island
	island.set_process(false);island.hero.pause();island.hud.hide()
	var actor:AnimatedSprite3D=island.hero
	var viewport=SubViewport.new();viewport.size=Vector2i(256,256);viewport.own_world_3d=true;viewport.transparent_bg=true;viewport.render_target_update_mode=SubViewport.UPDATE_ALWAYS;root.add_child(viewport)
	actor.reparent(viewport);actor.position=Vector3.ZERO
	var camera=Camera3D.new();viewport.add_child(camera);camera.position=Vector3(0,1.16,5);camera.look_at(Vector3(0,1.16,0));camera.projection=Camera3D.PROJECTION_ORTHOGONAL;camera.size=2.8;camera.current=true
	var env=WorldEnvironment.new();env.environment=Environment.new();env.environment.ambient_light_source=Environment.AMBIENT_SOURCE_DISABLED;env.environment.tonemap_mode=Environment.TONE_MAPPER_LINEAR;viewport.add_child(env)
	for warmup in 8:await process_frame
	var mat:ShaderMaterial=island.hero_lighting.material
	mat.set_shader_parameter("review_mode",1)
	var failures=[];var samples=[];var visited={};var count=0
	for animation in actor.sprite_frames.get_animation_names():
		actor.play(animation);actor.pause()
		for index in actor.sprite_frames.get_frame_count(animation):
			actor.frame=index
			var tex=actor.sprite_frames.get_frame_texture(animation,index)
			var base:Texture2D=tex.atlas if tex is AtlasTexture else tex
			if mat.get_shader_parameter("color_atlas")!=base:failures.append("Color atlas mismatch %s:%d"%[animation,index])
			if not bool(mat.get_shader_parameter("has_volume")):failures.append("Missing normal atlas %s:%d"%[animation,index])
			visited[island.hero_lighting.current_source]=true
			count+=1
			# First and last regions of each sheet, in both facing directions.
			var previous=actor.sprite_frames.get_frame_texture(animation,maxi(0,index-1))
			var next=actor.sprite_frames.get_frame_texture(animation,mini(index+1,actor.sprite_frames.get_frame_count(animation)-1))
			var first=index==0 or (previous is AtlasTexture and previous.atlas!=base)
			var last=index==actor.sprite_frames.get_frame_count(animation)-1 or (next is AtlasTexture and next.atlas!=base)
			if not first and not last:continue
			for mirrored in [false,true]:
				actor.flip_h=mirrored;island.hero_lighting.update()
				var key="%s-%02d-%s"%[animation,index,"left" if mirrored else "right"]
				actor.material_override=null;actor.shaded=false
				await capture(viewport,"frame-check/"+key+"-original.png")
				actor.material_override=mat;actor.shaded=true
				await capture(viewport,"frame-check/"+key+"-shader.png")
				samples.append(key)
		print("HERO_FRAME_CHECK ",animation)
	var file=FileAccess.open(OUT+"frame-bindings.json",FileAccess.WRITE)
	file.store_string(JSON.stringify({"frames_checked":count,"atlases_visited":visited.keys(),"render_pairs":samples,"failures":failures},"  "))
	print("HERO_FRAME_CHECK_DONE ",count);quit(0 if failures.is_empty() else 1)
