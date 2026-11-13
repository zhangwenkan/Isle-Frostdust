extends "res://tools/capture_pixel_dialogue.gd"
## Static UI and camera review. Reuses the existing dialogue input checks.

func _initialize() -> void:
	output_directory = "res://artifacts/bottom-dialogue-review/"
	DirAccess.make_dir_recursive_absolute(output_directory)
	call_deferred("run")

func actor_screen_rect() -> Rect2:
	var sprite: AnimatedSprite3D = island.hero
	var texture := sprite.sprite_frames.get_frame_texture(sprite.animation, sprite.frame)
	var used := texture.get_image().get_used_rect()
	var texture_size := Vector2(texture.get_size())
	var points := [Vector2(used.position), Vector2(used.end.x, used.position.y),
		Vector2(used.end), Vector2(used.position.x, used.end.y)]
	var bounds := Rect2()
	for index in points.size():
		var pixel: Vector2 = points[index]
		var local_x := (pixel.x - texture_size.x * 0.5 + sprite.offset.x) * sprite.pixel_size
		var local_y := (texture_size.y * 0.5 - pixel.y + sprite.offset.y) * sprite.pixel_size
		if sprite.flip_h:
			local_x = -local_x
		var world: Vector3 = sprite.global_position + island.camera.global_basis.x * local_x + island.camera.global_basis.y * local_y
		var point: Vector2 = island.camera.unproject_position(world)
		bounds = Rect2(point, Vector2.ZERO) if index == 0 else bounds.expand(point)
	return bounds

func shot(label: String) -> void:
	var dialogue: CanvasLayer = island.opening.dialogue
	var actor := actor_screen_rect()
	var frame: Rect2 = dialogue.card.get_global_rect()
	var portrait: Rect2 = dialogue.portrait.get_global_rect()
	print("ACTOR_UI_BOUNDS ", label, " actor=", actor, " card=", frame, " portrait=", portrait)
	assert(not actor.intersects(frame), "Dialogue covers map actor")
	assert(not actor.intersects(portrait), "Portrait covers map actor")
	assert(Rect2(Vector2.ZERO, dialogue.screen.size).encloses(actor), "Map actor outside screen")
	super.shot(label)
	reports[-1]["actor_bounds"] = str(actor)
	reports[-1]["actor_frame_clearance"] = frame.position.y - actor.end.y
	reports[-1]["actor_portrait_overlap"] = false
	reports[-1]["camera_position"] = str(island.camera.position)
	reports[-1]["camera_focus"] = str(island.camera_focus)
