extends "res://tools/capture_cloud_water.gd"
## Targeted regression checks, with a few diagnostic stills and no video capture.
const OUT := "res://artifacts/hd2d-upright-review/"
var failures: Array[String]=[]
var report: Dictionary={}

func check(ok: bool,label: String) -> void:
	if not ok:
		failures.append(label)
		push_error(label)

func pose(animation: StringName,frame: int,mirror: bool,snap := false) -> void:
	island.hero.animation=animation
	island.hero.frame=frame
	island.hero.flip_h=mirror
	island.hero.pause()
	island.hero_presentation.update(1.0/60.0,snap)
	island._update_ground_contact()

func image_difference(a: Image,b: Image) -> int:
	var count:=0
	for y in a.get_height():
		for x in a.get_width():
			var ca:=a.get_pixel(x,y)
			var cb:=b.get_pixel(x,y)
			if maxf(absf(ca.r-cb.r),maxf(absf(ca.g-cb.g),absf(ca.b-cb.b)))>.10:count+=1
	return count

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
	set_time(1.0)
	var presenter: RefCounted=island.hero_presentation
	var expected_basis: Basis=island.camera.basis
	var max_angle_error:=0.0
	var max_height_change:=0.0
	var minimum_clearance:=INF
	var maximum_lift:=0.0
	var max_idle_gap:=0.0
	var contact_cases:=0
	var gaps: Array=[]
	for x in [-15.2,-13.0,-11.0,-6.8,0.0,4.1,4.3,5.2,7.8,9.5,12.1,14.4,14.7,20.0,23.7]:
		for offset in [-.5,0.0,.5]:
			island.hero_x=x
			island.hero_path_offset=offset
			island._position_hero()
			island._update_camera(0,true)
			pose(&"idle_right",0,false,true)
			var standing_height: float=island.hero.position.y+presenter.lift
			max_angle_error=maxf(max_angle_error,expected_basis.get_rotation_quaternion().angle_to(island.camera.basis.get_rotation_quaternion()))
			for animation in [&"idle_right",&"idle_up",&"idle_down",&"walk_right",&"walk_up",&"walk_down"]:
				for mirror in [false,true] if animation in [&"idle_right",&"walk_right"] else [false]:
					for frame in island.hero.sprite_frames.get_frame_count(animation):
						pose(animation,frame,mirror)
						check(is_zero_approx(presenter.roll),"No slope roll")
						max_height_change=maxf(max_height_change,absf(island.hero.position.y+presenter.lift-standing_height))
						maximum_lift=maxf(maximum_lift,absf(presenter.lift))
						var frame_gap:=INF
						for point: Array in presenter.last_frame_data.sole:
							var px: float=(point[0]-256)*island.hero.pixel_size*(-1 if mirror else 1)
							var py: float=(724-point[1])*island.hero.pixel_size
							py=presenter.grounded_local_y(px,py)
							var world: Vector3=island.hero.position+island.hero.basis.x*px+island.hero.basis.y*py+Vector3.UP*presenter.lift
							var clearance: float=world.y-float(presenter.ground(world.x,world.z).height)
							frame_gap=minf(frame_gap,clearance)
							minimum_clearance=minf(minimum_clearance,clearance)
							contact_cases+=1
						if str(animation).begins_with("idle_"):
							max_idle_gap=maxf(max_idle_gap,frame_gap)
							if frame_gap>.06:gaps.append({"x":x,"offset":offset,"animation":str(animation),"mirror":mirror,"gap_m":frame_gap})
	check(rad_to_deg(max_angle_error)<.05,"Exploration viewing direction stays fixed along route")
	check(max_height_change<.00001,"All directions and animation frames share standing height")
	check(minimum_clearance>=-.005,"Shoe outlines do not visibly intersect imported terrain and bridge")
	check(max_idle_gap<.035,"Idle shoes stay within 3.5cm of the surface")
	report["contact"]={"queries":contact_cases,"minimum_clearance_m":minimum_clearance,"maximum_abs_lift_m":maximum_lift,"maximum_idle_gap_m":max_idle_gap,"larger_gaps":gaps,"max_change_on_turn_or_frame_m":max_height_change,"max_camera_angle_error_degrees":rad_to_deg(max_angle_error)}
	print("UPRIGHT_CONTACT ",JSON.stringify(report.contact))
	# Compare the first rendered state after a change against the settled same state.
	# This catches a color-atlas/UV/normal mismatch that transform checks cannot see.
	position(5.2)
	pose(&"idle_right",0,false,true)
	await settle(12)
	var states: Array=[
		["walk_right",15,false],["walk_right",16,false],["walk_down",23,false],
		["idle_right",0,true],["walk_up",28,false],["walk_right",25,true],
		["idle_down",0,false],["idle_up",0,false],["idle_right",0,false]]
	var render_checks: Array=[]
	for i in states.size():
		var state: Array=states[i]
		pose(StringName(state[0]),state[1],state[2])
		await process_frame
		await RenderingServer.frame_post_draw
		var foot: Vector2=island.camera.unproject_position(island.hero.position+Vector3.UP*presenter.lift)
		var rect:=Rect2i(int(foot.x)-90,int(foot.y)-225,180,250)
		var first: Image=root.get_texture().get_image().get_region(rect)
		await settle(3)
		await RenderingServer.frame_post_draw
		var settled: Image=root.get_texture().get_image().get_region(rect)
		var changed:=image_difference(first,settled)
		render_checks.append({"state":state,"pixels_changed_above_10pct":changed})
		if changed>40:
			first.save_png(OUT+"turn-%02d-first.png"%i)
			settled.save_png(OUT+"turn-%02d-settled.png"%i)
		check(changed<=40,"Turn/atlas transition %d has no one-frame image mismatch"%i)
	report["render_changes"]=render_checks
	print("UPRIGHT_RENDER ",JSON.stringify(render_checks))
	# Real movement and rapid input changes, without recording frames.
	position(-15.2)
	var min_head_margin:=INF
	for i in 680:
		island._move_hero(Vector2.RIGHT,1.0/60.0)
		island._update_camera(1.0/60.0)
		island._update_ground_contact()
		var head: Vector2=island.camera.unproject_position(island.hero.position+Vector3.UP*presenter.lift+island.hero.basis.y*2.5)
		min_head_margin=minf(min_head_margin,minf(head.x,minf(1280-head.x,head.y)))
		if i%12==0:await process_frame
	check(island.hero_x>23.6,"Traversal reaches east endpoint")
	check(min_head_margin>12,"Head remains within frame")
	position(5.2)
	for i in 80:
		var move: Vector2=[Vector2.LEFT,Vector2.RIGHT,Vector2.UP,Vector2.DOWN][i%4]
		island._move_hero(move,1.0/60.0)
		island._update_camera(1.0/60.0)
		check(is_zero_approx(presenter.roll),"Rapid input keeps actor upright")
		if i%4==0:await process_frame
	report["movement"]={"traversal_steps":680,"rapid_direction_changes":80,"minimum_head_margin_px":min_head_margin}
	# Exercise the actual opening, dialogue release and R replay.
	island.skip_opening=false
	island.opening.enabled=true
	var replay:=InputEventKey.new()
	replay.keycode=KEY_R
	replay.pressed=true
	island._unhandled_key_input(replay)
	island.set_process(true)
	var opening_basis: Basis=island.camera.basis
	var opening_position: Vector3=island.hero.position
	await create_timer(4.7).timeout
	check(island.opening.phase==island.opening.Phase.DIALOGUE,"Opening finishes into dialogue")
	check(island.camera.basis.is_equal_approx(opening_basis),"Opening and dialogue keep their high shot")
	check(island.hero.position.is_equal_approx(opening_position),"Opening root is not grounded per action frame")
	island.opening.dialogue.advance()
	await process_frame
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png(OUT+"after-dialogue.png")
	for i in 5:island.opening.dialogue.advance()
	check(not island.opening.is_input_locked(),"Dialogue releases control")
	var last_camera: Basis=island.camera.basis
	var max_release_step:=0.0
	island.set_process(false)
	for i in 240:
		island._update_camera(1.0/60.0)
		max_release_step=maxf(max_release_step,last_camera.get_rotation_quaternion().angle_to(island.camera.basis.get_rotation_quaternion()))
		last_camera=island.camera.basis
	check(island.cape_opening<.001,"Cape returns to exploration view after dialogue")
	check(rad_to_deg(max_release_step)<2.0,"Dialogue camera blends without a one-frame cut")
	report["opening"]={"high_shot_preserved":true,"max_camera_step_degrees":rad_to_deg(max_release_step),"remaining_blend":island.cape_opening}
	check(is_equal_approx(island.hero.pixel_size,island.HERO_PIXEL_SIZE) and island.hero.offset==island.HERO_SPRITE_OFFSET,"Original sprite scale and anchor remain intact")
	report["passed"]=failures.is_empty()
	report["failures"]=failures
	report["video_recorded"]=false
	var file:=FileAccess.open(OUT+"verification.json",FileAccess.WRITE)
	file.store_string(JSON.stringify(report,"  "))
	print("UPRIGHT_VERIFY ","PASS" if failures.is_empty() else "FAIL")
	quit(0 if failures.is_empty() else 1)
