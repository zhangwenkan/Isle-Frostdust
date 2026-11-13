extends SceneTree
## Render-independent checks of actual imported surface contact and action boundaries.
const OUT := "res://artifacts/hero-volume-review/"
var island: Node3D
var checks: Array[String]=[]
var worst_clearance:=INF
var largest_lift:=0.0
var max_frame_step:=0.0
var query_count:=0
var fallback_count:=0
var extremes: Array=[]
var failures: Array[String]=[]

func _initialize() -> void:call_deferred("run")
func check(ok: bool,label: String) -> void:
	if not ok:
		push_error(label)
		failures.append(label)
	else:checks.append(label)

func run() -> void:
	island=load("res://scenes/island.tscn").instantiate()
	root.add_child(island)
	current_scene=island
	island.set_process(false)
	island.hero.pause()
	var presenter: RefCounted=island.hero_presentation
	check(presenter.surface.surface_names.size()==41,"Samples two imported islands and all 39 individual bridge planks")
	var positions: Array=[-15.2,-13.0,-11.0,-6.8,0.0,4.1,4.3,5.2,7.8,9.5,12.1,14.4,14.7,20.0,23.7]
	if "--quick" in OS.get_cmdline_user_args():positions=[-13.0,4.3,14.4]
	for x in positions:
		for offset in [-.5,0.0,.5]:
			island.hero_x=x
			island.hero_path_offset=offset
			island._position_hero()
			island._update_camera(0.0,true)
			for animation in [&"walk_right",&"walk_up",&"walk_down",&"idle_right",&"idle_up",&"idle_down"]:
				island.hero.animation=animation
				for mirror in [false,true] if animation in [&"walk_right",&"idle_right"] else [false]:
					island.hero.flip_h=mirror
					var last_lift:=0.0
					for f in island.hero.sprite_frames.get_frame_count(animation):
						island.hero.frame=f
						presenter.update(1.0/24.0,true)
						if absf(presenter.lift)>largest_lift:
							largest_lift=absf(presenter.lift)
							extremes.append({"x":x,"offset":offset,"animation":str(animation),"mirror":mirror,"frame":f,"lift":presenter.lift})
						if f>0:max_frame_step=maxf(max_frame_step,absf(presenter.lift-last_lift))
						last_lift=presenter.lift
						for point: Array in presenter.last_frame_data.sole:
							var px: float=(point[0]-256)*island.hero.pixel_size*(-1 if mirror else 1)
							var py: float=(724-point[1])*island.hero.pixel_size
							var world: Vector3=island.hero.position+island.hero.basis.x*px+island.hero.basis.y*py+Vector3.UP*presenter.lift
							var hit: Dictionary=presenter.ground(world.x,world.z)
							query_count+=1
							if hit.surface=="fallback":fallback_count+=1
							worst_clearance=minf(worst_clearance,world.y-float(hit.height))
	check(worst_clearance>=.007,"All tested shoe outlines clear imported terrain/bridge triangles")
	check(fallback_count==0,"No formula fallback along tested walking footprints")
	print("CONTACT_EXTREMES ",JSON.stringify(extremes))
	print("CONTACT_STEP ",max_frame_step)
	check(largest_lift<.18,"Ground correction remains below 18cm, without resizing frames")
	# Actual loop advances; turn direction also mirrors lighting, preserving resource/scale.
	island.hero_x=-6.8
	island.hero_path_offset=0
	island._position_hero()
	island._move_hero(Vector2.LEFT,.1)
	island._update_camera(.1)
	check(island.hero.flip_h and presenter.material.get_shader_parameter("mirror_sign")==-1.0,"Left turn mirrors normals together with frame")
	island._move_hero(Vector2.UP,.1)
	island._update_camera(.1)
	check(not island.hero.flip_h and island.hero.animation==&"walk_up","Depth movement clears mirror and selects back frames")
	await create_timer(.16).timeout
	check(island.hero.frame>0,"Animation advances in running scene")
	var walk_frames: SpriteFrames=island.hero.sprite_frames
	island.hero_x=island.HERO_START_X
	island.hero_path_offset=0
	island._position_hero()
	island._update_camera(0,true)
	var fixed_root: Vector3=island.hero.position
	island.hero.sprite_frames=island.opening.REST_FRAMES
	island.hero.animation=&"rest_rise_right"
	island.hero.pause()
	for f in 103:
		island.hero.frame=f
		presenter.update(1.0/24,true)
		check(presenter.lift==0 and island.hero.position==fixed_root,"Opening frame %d retains original displacement"%f)
	var end_basis: Basis=island.hero.basis
	island.hero.sprite_frames=walk_frames
	island.hero.animation=&"idle_right"
	presenter.update(0,true)
	check(end_basis.is_equal_approx(island.hero.basis),"Rise and idle have identical presentation orientation at handoff")
	check(is_equal_approx(island.hero.pixel_size,island.HERO_PIXEL_SIZE) and island.hero.offset==island.HERO_SPRITE_OFFSET,"Native frame scale and anchor retained")
	var started:=Time.get_ticks_usec()
	for i in 120:presenter.update(1.0/60.0)
	var update_us: float=(Time.get_ticks_usec()-started)/120.0
	var report_name: String="verification-renderer.json" if "--quick" in OS.get_cmdline_user_args() else "verification.json"
	var file:=FileAccess.open(OUT+report_name,FileAccess.WRITE)
	file.store_string(JSON.stringify({"passed":failures.is_empty(),"checks":checks,"failures":failures,"foot_queries":query_count,"formula_fallbacks":fallback_count,"minimum_clearance_m":worst_clearance,"maximum_abs_correction_m":largest_lift,"maximum_raw_frame_correction_step_m":max_frame_step,"average_idle_update_us":update_us,"static_review_only":true},"  "))
	print("HERO_VOLUME_", "PASS" if failures.is_empty() else "FAIL", " ",query_count," sole probes; minimum=",worst_clearance," lift=",largest_lift," step=",max_frame_step," update_us=",update_us)
	quit(0 if failures.is_empty() else 1)
