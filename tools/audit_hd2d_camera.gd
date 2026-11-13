extends SceneTree
## Read-only camera/presentation measurements for the public-reference study.
func _initialize() -> void:call_deferred("run")
func run() -> void:
	var island: Node3D=load("res://scenes/island.tscn").instantiate()
	island.skip_opening = true
	root.add_child(island)
	island.set_process(false)
	island.hero.animation = &"idle_right"
	island.hero.frame = 0
	island.hero.pause()
	var rows: Array=[]
	for item in [{"label":"cape","x":-15.2},{"label":"transition","x":-14.0},{"label":"grove","x":-6.8},{"label":"landing","x":3.0},{"label":"bridge","x":9.5},{"label":"east","x":20.0}]:
		island.hero_x=item.x
		island.hero_path_offset=0
		island._position_hero()
		island._update_camera(0,true)
		var camera: Camera3D=island.camera
		var row: Dictionary={"label":item.label,"x":item.x,"projection":"perspective","fov":camera.fov,
			"pitch_degrees":rad_to_deg(asin(camera.global_basis.z.y)),
			"yaw_degrees":rad_to_deg(atan2(camera.global_basis.z.x,camera.global_basis.z.z)),
			"distance_to_hero":camera.position.distance_to(island.hero.position),
			"sprite_pitch_degrees":rad_to_deg(island.hero_presentation.pitch),
			"sprite_roll_degrees":rad_to_deg(island.hero_presentation.roll)}
		rows.append(row)
	var file:=FileAccess.open("res://artifacts/hd2d-character-camera-study/current-camera.json",FileAccess.WRITE)
	file.store_string(JSON.stringify(rows,"  "))
	print(JSON.stringify(rows,"  "))
	quit(0)
