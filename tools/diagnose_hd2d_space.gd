extends SceneTree
## Temporary runtime camera comparisons. Never saves camera/scene/model changes.
const OUT="res://artifacts/hd2d-space-diagnosis/"
var island:Node3D
var report={"locations":[]}
func _initialize():call_deferred("run")
func body_pixels()->float:
	return island.camera.unproject_position(island.hero.global_position).distance_to(island.camera.unproject_position(island.hero.global_position+Vector3.UP*1.6))
func setup_camera(focus:Vector3,pitch:float,fov:float,distance:float):
	var rad=deg_to_rad(pitch)
	island.camera.set_perspective(fov,.15,800.)
	island.camera.position=focus+Vector3(0,sin(rad),cos(rad))*distance
	island.camera.look_at(focus)
func camera_info()->Dictionary:
	var cam:Camera3D=island.camera
	var normal=(island.get_node("World") as Node3D).global_basis.y.normalized()
	return {"vertical_fov":cam.fov,"horizontal_fov":rad_to_deg(2.*atan(tan(deg_to_rad(cam.fov*.5))*16./9.)),"world_pitch":rad_to_deg(asin(absf(cam.global_basis.z.y))),"angle_above_nominal_ground":rad_to_deg(asin(absf(cam.global_basis.z.dot(normal)))),"world_ground_tilt":rad_to_deg(acos(clampf(normal.dot(Vector3.UP),-1,1))),"distance_to_focus":cam.position.distance_to(island.camera_focus_world),"body_1_6m_pixels":body_pixels(),"camera":cam.position,"focus":island.camera_focus_world,"hero":island.hero.position,"camera_attributes":str(cam.attributes)}
func run():
	root.size=Vector2i(1280,720);root.content_scale_size=Vector2i(1280,720)
	island=load("res://scenes/layered_island.tscn").instantiate();root.add_child(island);current_scene=island
	island.manual_control=false;island.hud.hide();island.set_process(false)
	for child in island.get_children():
		if child is WorldEnvironment:
			report["environment"]={"ambient_energy":child.environment.ambient_light_energy,"fog":child.environment.fog_enabled,"volumetric_fog":child.environment.volumetric_fog_enabled,"glow":child.environment.glow_enabled,"world_camera_attributes":str(child.camera_attributes)}
	report["hero"]={"billboard":island.hero.billboard,"shaded":island.hero.shaded,"shadow":island.hero.cast_shadow}
	for location in [["beach","stair_bottom",0.,"beach"],["forest_step1","forest_mid",.7,"forest"]]:
		island.camera.attributes=null
		island.set_route_sample(location[0],location[1],location[2]);island.hero.stop()
		var target=body_pixels();var focus:Vector3=island.camera_focus_world;var base_pitch=float(camera_info().world_pitch)
		var baseline=camera_info();var variants=[]
		for row in [["A-current",base_pitch,16.3,false],["B-lower",15.,16.3,false],["C-wider",base_pitch,23.140917,false],["D-lower-wider",15.,23.140917,false],["E-current-dof",base_pitch,16.3,true]]:
			island.camera.attributes=null
			var lo=10.;var hi=85.
			for i in 20:
				var distance=(lo+hi)*.5;setup_camera(focus,row[1],row[2],distance)
				if body_pixels()>target:lo=distance
				else:hi=distance
			if row[3]:
				var attributes=CameraAttributesPractical.new();var d=(lo+hi)*.5
				attributes.dof_blur_near_enabled=true;attributes.dof_blur_near_distance=d-3.;attributes.dof_blur_near_transition=6.
				attributes.dof_blur_far_enabled=true;attributes.dof_blur_far_distance=d+6.;attributes.dof_blur_far_transition=18.;attributes.dof_blur_amount=.12
				island.camera.attributes=attributes
			island._update_occluders(1.)
			var info=camera_info();info["label"]=row[0]
			# Same metric feature near the actor and at +/-3 m nominal ground depth.
			var point:Vector3=island.hero.position+Vector3.UP*.2
			var direction:Vector3=(island.get_node("World") as Node3D).global_basis.z.normalized()
			var sizes=[]
			for depth in [-3.,0.,3.]:
				var p=point+direction*depth
				sizes.append(island.camera.unproject_position(p).distance_to(island.camera.unproject_position(p+Vector3.RIGHT)))
			info["one_meter_width_at_depth_minus3_zero_plus3"]=sizes
			for i in 4:await process_frame
			await RenderingServer.frame_post_draw
			root.get_texture().get_image().save_jpg(OUT+str(location[3])+"-"+str(row[0])+".jpg",.85)
			variants.append(info)
		report.locations.append({"name":location[3],"baseline":baseline,"variants":variants})
	var f=FileAccess.open(OUT+"runtime-camera-audit.json",FileAccess.WRITE);f.store_string(JSON.stringify(report,"  "))
	print("HD2D_SPACE_DIAGNOSIS "+JSON.stringify({"baseline":report.locations[0].baseline,"environment":report.environment,"hero":report.hero}));quit()
