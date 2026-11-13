extends "res://tools/capture_cloud_water.gd"
## Identical static pose/camera/time comparison; never records a video.
const OUT := "res://artifacts/hero-standing-light-review/"
var rows: Array=[]

func shot(label:String) -> void:
	island.hero_presentation.update(0,true)
	island._update_ground_contact()
	await settle(24)
	await RenderingServer.frame_post_draw
	assert(root.get_texture().get_image().save_png(OUT+phase+"-"+label+".png")==OK)
	var p: Vector3=island.hero.position+Vector3.UP*island.hero_presentation.lift
	rows.append({"label":label,"hero":str(p),"foot_screen":str(island.camera.unproject_position(p)),"head_screen":str(island.camera.unproject_position(p+island.hero.basis.y*2.45)),"camera":str(island.camera.transform),"sun_direction":str(island.atmosphere.sun.global_basis.z),"presentation":island.hero_presentation.debug_state()})
	print("STANDING_STATIC ",phase," ",label)

func run_capture() -> void:
	root.size=Vector2i(1280,720)
	island=load("res://scenes/island.tscn").instantiate()
	island.skip_opening=true
	root.add_child(island)
	current_scene=island
	island.set_process(false)
	island.hero.pause()
	island.hud.hide()
	control_time(island)
	freeze_material(island.atmosphere.mountain_cloud_material,"fog")
	freeze_material(island.background_comparison.original_sky,"sky")
	freeze_material(island.background_comparison.comparison_sky,"sky")
	set_time(1.0)
	island.hero.animation=&"idle_down"
	position(-6.8)
	await shot("grove-front")
	# A closer inspection view keeps the exploration viewing direction intact.
	var focus: Vector3=island.hero.position+Vector3.UP*1.28
	island.camera.position=focus+island.camera.global_basis.z*7.8
	island.camera_effects.dof_blur_near_enabled=false
	island.camera_effects.dof_blur_far_enabled=false
	await shot("front-detail")
	if "--surface-variants" in OS.get_cmdline_user_args():
		for wrap in [.85,1.10,1.40]:
			island.hero_presentation.material.set_shader_parameter("light_wrap",wrap)
			await shot("wrap-%03d"%int(wrap*100))
		island.hero_presentation.material.set_shader_parameter("light_wrap",1.10)
		island.hero_presentation.material.set_shader_parameter("normal_strength",1.5)
		await shot("wrap-strong-form")
		print("CONTACT_MESH ",island.contact_shadow.mesh.get_aabb())
		quit(0)
		return
	if "--light-diagnose" in OS.get_cmdline_user_args():
		island.hero.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		await shot("no-self-cast")
		island.hero.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_ON
		island.atmosphere.sun.shadow_normal_bias=.05
		await shot("low-bias")
		island.atmosphere.sun.rotation_degrees=Vector3(-42,-25,0)
		await shot("frontlight")
		var diagnostic: Shader=island.hero_presentation.material.shader.duplicate()
		diagnostic.code=diagnostic.code.replace("ROUGHNESS=1.0;","ROUGHNESS=1.0; ALBEDO=vec3(0.0); EMISSION=n*.5+.5;")
		island.hero_presentation.material.shader=diagnostic
		await shot("normal-map")
		print("NORMAL_BINDING ",island.hero_presentation.material.get_shader_parameter("volume_atlas")," ",island.hero_presentation.material.get_shader_parameter("has_volume"))
		quit(0)
		return
	if phase=="probe":
		for share in [.55,.75,.90,1.0]:
			island.hero_presentation.material.set_shader_parameter("light_share",share)
			await shot("share-%02d"%int(share*100))
		island.hero_presentation.material.set_shader_parameter("light_share",.32)
		island.hero.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		await shot("no-cast")
		island.hero.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_ON
		for s in island.hero_presentation.shoe_shadows:s.hide()
		island.contact_shadow.hide()
		await shot("no-body-contact")
	else:
		for direction in ["right","up"]:
			island.hero.animation=StringName("idle_"+direction)
			await shot(direction+"-detail")
		island.hero.animation=&"idle_down"
		island.atmosphere.apply(11.2,.9)
		await shot("front-overcast")
		island.atmosphere.apply(11.2,.12)
		island.background_comparison.set_mode(1)
		await shot("front-sunset")
		island.background_comparison.set_mode(0)
		island.camera_effects.dof_blur_near_enabled=true
		island.camera_effects.dof_blur_far_enabled=true
		position(9.5)
		await shot("bridge-front")
		if "--extended" in OS.get_cmdline_user_args():
			for x in [-11.5,-9.0,-3.0,20.0]:
				position(x)
				await shot("position-%s"%str(x).replace(".","_"))
			position(-6.8)
			island.camera.position=island.hero.position+Vector3.UP*1.28+island.camera.global_basis.z*7.8
			island.camera_effects.dof_blur_near_enabled=false
			island.camera_effects.dof_blur_far_enabled=false
			island.atmosphere.sun.light_energy=0
			await shot("sky-only")
			island.atmosphere.apply(11.2,.12)
			# Same world sun settings except azimuth, for a surface-response diagnostic.
			island.atmosphere.sun.rotation_degrees=Vector3(-42,-35,0)
			await shot("test-light-left")
			island.atmosphere.sun.rotation_degrees=Vector3(-42,35,0)
			await shot("test-light-right")
			island.atmosphere.apply(11.2,.12)
			var original_frames: SpriteFrames=island.hero.sprite_frames
			island.hero.sprite_frames=island.opening.REST_FRAMES
			island.hero.animation=&"rest_rise_right"
			island.hero.frame=102
			await shot("opening-last-frame")
			island.hero.sprite_frames=original_frames
			island.hero.animation=&"walk_right"
			island.hero.frame=7
			await shot("existing-walk-smoke")
	var file:=FileAccess.open(OUT+phase+"-poses.json",FileAccess.WRITE)
	file.store_string(JSON.stringify(rows,"  "))
	quit(0)
