extends SceneTree
var island:Node3D
func _initialize()->void:call_deferred("run")
func run()->void:
	island=load("res://scenes/island.tscn").instantiate();root.add_child(island)
	island.set_process(false);island.opening.set_process(false);island.skip_opening=true
	island.opening.enabled=false;island.opening.dialogue.cancel_dialogue();island.opening.phase=island.opening.Phase.COMPLETE
	var gaps=[];var worst_step:=0.0;var previous:=0.0;var count:=0
	for i in 1001:
		var x:=lerpf(22.0,34.0,i/1000.0)
		for dz in [-.55,0.0,.55]:
			var hit=island.hero_presentation.surface.sample(x,island._path_z(x)+dz)
			if hit.is_empty():gaps.append([x,dz])
			else:
				if dz==0.0 and i>0:worst_step=maxf(worst_step,absf(hit.height-previous))
				if dz==0.0:previous=hit.height
			count+=1
	island.hero_x=23.7;island.hero_path_offset=0;island._position_hero()
	for i in 230:island._move_hero(Vector2.RIGHT,1.0/60.0)
	var endpoint:float=island.hero_x
	for i in 180:island._move_hero(Vector2.LEFT,1.0/60.0)
	var result={"samples":count,"gaps":gaps,"max_height_step_over_12mm":worst_step,"right_stop":endpoint,"returned_x":island.hero_x,"surface_names":island.hero_presentation.surface.surface_names}
	FileAccess.open("res://artifacts/east-spring-review/runtime-verification.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "))
	print("SPRING_VERIFICATION ",JSON.stringify(result))
	quit(0 if gaps.is_empty() and absf(endpoint-34.0)<.001 and worst_step<.15 else 1)
