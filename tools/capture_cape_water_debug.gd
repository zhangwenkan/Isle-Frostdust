extends "res://tools/capture_shallow_cape.gd"
func run_capture()->void:
	root.size=Vector2i(1280,720)
	island=load("res://scenes/island.tscn").instantiate();root.add_child(island);current_scene=island
	island.set_process(false);island.opening.set_process(false);island.hero.pause();island.hud.hide();control_time(island);set_time(2.0)
	position(-24.2)
	island.camera_effects.dof_blur_near_enabled=false;island.camera_effects.dof_blur_far_enabled=false
	island.camera.position=Vector3(-26,3.3,18.5);island.camera.look_at(Vector3(-26,.35,0));island.camera.fov=40
	var bed:Node3D=island.get_node("World3D").find_child("Fish_Seabed",true,false)
	var water:Node3D=island.get_node("World3D").find_child("Open_Sea",true,false)
	bed.hide();await picture("debug-no-bed")
	bed.show();water.hide();await picture("debug-no-water")
	quit(0)
