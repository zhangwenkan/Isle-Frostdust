extends "res://tools/capture_cloud_water.gd"
## Static comparison only. Use the same scene, poses and environment time in both passes.
const OUT := "res://artifacts/hd2d-upright-review/"
var rows: Array=[]

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
	for point in [{"x":-15.2,"label":"cape"},{"x":-6.8,"label":"grove"},{"x":5.2,"label":"bridge-entry"},{"x":9.5,"label":"bridge-middle"},{"x":20.0,"label":"east"}]:
		for direction in ["right","down"] if point.label=="bridge-entry" else ["right"]:
			island.hero.animation=StringName("idle_"+direction)
			island.hero.flip_h=false
			position(point.x)
			island._update_ground_contact()
			await settle(10)
			await RenderingServer.frame_post_draw
			root.get_texture().get_image().save_png(OUT+phase+"-"+point.label+"-"+direction+".png")
			var presenter: RefCounted=island.hero_presentation
			var foot: Vector3=island.hero.position+Vector3.UP*presenter.lift
			var screen_foot: Vector2=island.camera.unproject_position(foot)
			var screen_head: Vector2=island.camera.unproject_position(foot+island.hero.basis.y*2.45)
			rows.append({"label":point.label,"direction":direction,"pitch":rad_to_deg(asin(island.camera.global_basis.z.y)),"yaw":rad_to_deg(atan2(island.camera.global_basis.z.x,island.camera.global_basis.z.z)),"fov":island.camera.fov,"foot":str(screen_foot),"head":str(screen_head),"roll_screen":rad_to_deg(atan2(screen_head.x-screen_foot.x,screen_foot.y-screen_head.y)),"presenter":presenter.debug_state()})
			print("UPRIGHT_STATIC ",phase," ",point.label," ",direction)
	var file:=FileAccess.open(OUT+phase+"-poses.json",FileAccess.WRITE)
	file.store_string(JSON.stringify(rows,"  "))
	quit(0)
