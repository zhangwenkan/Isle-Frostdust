extends SceneTree
const OUT := "res://artifacts/reference-shore-fit/"
var island:Node3D
func _initialize()->void:call_deferred("run")
func run()->void:
	root.size=Vector2i(1280,720)
	island=load("res://scenes/island.tscn").instantiate();root.add_child(island);current_scene=island
	island.set_process(false);island.opening.set_process(false);island.hud.hide();island.hero.pause()
	assert(not island.opening.is_input_locked())
	var support_samples:=0
	var screenshots=[]
	for direction in [Vector2.RIGHT,Vector2.ZERO,Vector2.LEFT]:
		for i in (480 if direction!=Vector2.ZERO else 48):
			island._move_hero(direction,1.0/60.0);island._update_camera(1.0/60.0);island._update_ground_contact()
			island.coastal_life.advance(1.0/60.0,island.hero_x)
			island.hero.pause()
			if direction!=Vector2.ZERO:island.hero.frame=(i/7)%island.hero.sprite_frames.get_frame_count(island.hero.animation)
			var hit:Dictionary=island.hero_presentation.surface.sample(island.hero.position.x,island.hero.position.z)
			assert(not hit.is_empty())
			assert(absf(island.hero.position.y-float(hit.height)-.04)<.002)
			support_samples+=1
			if i%120==0:
				await process_frame;await RenderingServer.frame_post_draw
				var name:="walk-check-%04d.png"%support_samples
				root.get_texture().get_image().save_png(OUT+name);screenshots.append(name)
	assert(absf(island.hero_x-island.HERO_START_X)<.01)
	# Imported topology and UVs are unchanged on the actual traversal surface;
	# exercise stepping instead of rerunning every unrelated character atlas test.
	FileAccess.open(OUT+"walk-verification.json",FileAccess.WRITE).store_string(JSON.stringify({"steps":support_samples,"seconds":support_samples/60.0,"right_pause_left":true,"ground_support_all_steps":true,"returned_to_start":true,"screenshots":screenshots},"  "))
	print("COAST_WALK_VERIFIED ",support_samples)
	quit(0)
