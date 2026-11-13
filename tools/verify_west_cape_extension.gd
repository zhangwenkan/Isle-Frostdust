extends "res://tools/capture_background_comparison.gd"
const OUT := "res://artifacts/west-cape-extension-review/"
var failures:Array[String]=[]
func check(ok:bool,label:String)->void:
	if not ok:failures.append(label);push_error(label)
func pose(animation:StringName,frame:int,mirror:bool)->void:
	island.hero.animation=animation;island.hero.frame=frame;island.hero.flip_h=mirror
	island.hero.pause();island.hero_presentation.update(0,true)
func key(code:Key)->void:
	var e:=InputEventKey.new();e.keycode=code;e.pressed=true
	island._unhandled_key_input(e)
func run_capture()->void:
	root.size=Vector2i(1280,720)
	island=load("res://scenes/island.tscn").instantiate()
	root.add_child(island);current_scene=island
	island.set_process(false);island.hero.pause();island.opening.set_process(false)
	var presenter:RefCounted=island.hero_presentation
	var minimum:=INF;var fallback:=0;var queries:=0;var max_idle_gap:=0.0
	for x in [-24.2,-22.0,-20.0,-18.0,-16.0,-15.2,-14.0,-11.0,-9.0,-6.8,-2.5,0.0,2.8,3.2,3.7,4.1,4.3,5.2,7.8,14.4,14.7,21.0]:
		for offset in [-.55,0.0,.55]:
			island.hero_x=x;island.hero_path_offset=offset
			island._position_hero();island._update_camera(0,true)
			for animation in [&"idle_right",&"idle_up",&"idle_down",&"walk_right",&"walk_up",&"walk_down"]:
				for mirror in [false,true] if animation in [&"idle_right",&"walk_right"] else [false]:
					for frame in island.hero.sprite_frames.get_frame_count(animation):
						pose(animation,frame,mirror)
						var frame_gap:=INF
						for point:Array in presenter.last_frame_data.sole:
							var px:float=(point[0]-256)*island.hero.pixel_size*(-1 if mirror else 1)
							var py:float=presenter.grounded_local_y(px,(724-point[1])*island.hero.pixel_size)
							var world:Vector3=island.hero.position+island.hero.basis.x*px+island.hero.basis.y*py+Vector3.UP*presenter.lift
							var hit:Dictionary=presenter.ground(world.x,world.z)
							var clearance:float=world.y-float(hit.height)
							minimum=minf(minimum,clearance);frame_gap=minf(frame_gap,clearance)
							if hit.surface=="fallback":fallback+=1
							queries+=1
						if str(animation).begins_with("idle_"):max_idle_gap=maxf(max_idle_gap,frame_gap)
	check(minimum>=-.005,"Sole outline clears imported ground")
	check(fallback==0,"All tested feet have actual imported support")
	check(max_idle_gap<.035,"Standing soles remain near ground")
	var min_height:=INF;var max_height:=-INF;var max_step:=0.0;var previous:=0.0
	for i in 581:
		var x:float=-24.2+29.0*i/580.0
		var h:Dictionary=presenter.surface.sample(x,.25)
		check(not h.is_empty(),"Continuous path support at "+str(x))
		if x<=2.8:min_height=minf(min_height,h.height);max_height=maxf(max_height,h.height)
		if i>0:max_step=maxf(max_step,absf(h.height-previous))
		previous=h.height
	check(max_height-min_height<.01,"West road is level")
	check(max_step<.13,"Bridge approach has no abrupt terrain step")
	island.opening.enabled=true;island.skip_opening=false
	key(KEY_R);island.hero.pause()
	var start:Vector3=island.hero.position
	island._move_hero(Vector2.RIGHT,1.0)
	check(island.hero.position==start,"Rising locks movement")
	var min_margin:=INF
	for frame in 103:
		island.hero.frame=frame;island.hero_presentation.update(0,true)
		var tex:Texture2D=island.hero.sprite_frames.get_frame_texture(island.hero.animation,frame)
		var used:Rect2i=tex.get_image().get_used_rect()
		for pixel in [Vector2(used.position),Vector2(used.end.x,used.position.y),Vector2(used.end),Vector2(used.position.x,used.end.y)]:
			var px:float=(pixel.x-tex.get_width()*.5+island.hero.offset.x)*island.hero.pixel_size
			var py:float=(tex.get_height()*.5-pixel.y+island.hero.offset.y)*island.hero.pixel_size
			var screen:Vector2=island.camera.unproject_position(island.hero.global_position+island.hero.basis.x*px+island.hero.basis.y*py)
			min_margin=minf(min_margin,minf(minf(screen.x,1280-screen.x),minf(screen.y,720-screen.y)))
	check(min_margin>8.0,"All opening poses remain inside screen")
	island.opening._on_animation_finished()
	for i in 86:
		island._move_hero(Vector2.RIGHT,1.0/60.0);island._update_camera(1.0/60.0);island.opening._process(1.0/60.0)
	check(island.hero.position==start,"Dialogue reframing locks movement")
	check(island.opening.dialogue.is_dialogue_active(),"Dialogue starts after reframing")
	var foot:Vector2=island.camera.unproject_position(island.hero.position)
	check(foot.y<445,"Actor stays above bottom dialogue frame")
	island.opening.dialogue.cancel_dialogue();island.opening._on_dialogue_finished(&"an_lixing_after_rest")
	for i in 108:
		island._move_hero(Vector2.RIGHT,1.0/60.0);island._update_camera(1.0/60.0);island.opening._process(1.0/60.0)
	check(island.hero.position==start,"Return camera finishes before movement")
	island._update_camera(1.0/60.0);island.opening._process(1.0/60.0)
	check(not island.opening.is_input_locked(),"Movement unlocks after transition")
	check(island.cape_opening<.001,"Cape view fully returned")
	island._move_hero(Vector2.RIGHT,.2)
	check(island.hero_x>island.HERO_START_X+.5,"Walking works after opening")
	key(KEY_R);island.hero.pause()
	check(island.opening.phase==island.opening.Phase.RISING,"R restarts opening")
	key(KEY_R);island.hero.pause()
	check(island.hero.frame==0,"Replay resets first frame")
	var report:Dictionary={"passed":failures.is_empty(),"failures":failures,"sole_queries":queries,"min_sole_clearance_m":minimum,"max_idle_gap_m":max_idle_gap,"surface_fallbacks":fallback,"west_road_height_range_m":[min_height,max_height],"max_approach_step_per_5cm_m":max_step,"opening_min_screen_margin_px":min_margin,"dialogue_foot_screen":str(foot),"opening_locks_and_replay":true,"static_only_no_video":true}
	FileAccess.open(OUT+"runtime-verification.json",FileAccess.WRITE).store_string(JSON.stringify(report,"  "))
	print("ENCLOSURE_RUNTIME ",JSON.stringify(report))
	quit(0 if failures.is_empty() else 1)
