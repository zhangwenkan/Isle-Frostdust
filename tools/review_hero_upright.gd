extends "res://tools/capture_cloud_water.gd"
## Reproduce the reported bridge poses and measure rapid direction changes.
const OUT := "res://artifacts/hero-upright-review/"
var report: Array=[]

func run_capture() -> void:
	root.size=Vector2i(1280,720)
	island=load("res://scenes/island.tscn").instantiate()
	root.add_child(island)
	current_scene=island
	island.set_process(false)
	island.hero.pause()
	island.hud.hide()
	control_time(island)
	freeze_material(island.atmosphere.mountain_cloud_material,"fog")
	freeze_material(island.background_comparison.original_sky,"sky")
	set_time(1)
	for p in [{"x":5.2,"label":"bridge-entry"},{"x":9.5,"label":"bridge-middle"},{"x":13.6,"label":"bridge-exit"},{"x":-13.0,"label":"steep"},{"x":-15.2,"label":"cape"}]:
		island.hero.animation=&"idle_right"
		island.hero.flip_h=false
		position(p.x)
		for direction in ["right","down","up","left"]:
			island.hero.animation=StringName("idle_"+("right" if direction=="left" else direction))
			island.hero.flip_h=direction=="left"
			island.hero_presentation.update(0,true)
			island._update_ground_contact()
			await settle(5)
			await RenderingServer.frame_post_draw
			root.get_texture().get_image().save_png(OUT+phase+"-"+p.label+"-"+direction+".png")
			var a: Vector2=island.camera.unproject_position(island.hero.position+Vector3.UP*island.hero_presentation.lift)
			var b: Vector2=island.camera.unproject_position(island.hero.position+island.hero.basis.y*2.0+Vector3.UP*island.hero_presentation.lift)
			report.append({"label":p.label,"direction":direction,"tilt_degrees":rad_to_deg(atan2(b.x-a.x,a.y-b.y)),"lift":island.hero_presentation.lift,"position":str(island.hero.position)})
		print("UPRIGHT_SHOTS ",phase," ",p.label)
	var file:=FileAccess.open(OUT+phase+"-poses.json",FileAccess.WRITE)
	file.store_string(JSON.stringify(report,"  "))
	quit(0)
