extends SceneTree
func _initialize():call_deferred("run")
func run():
 var s=load("res://scenes/layered_island.tscn").instantiate();root.add_child(s);s.set_process(false)
 for n in s.get_node("World").find_children("*","MeshInstance3D",true,false):
  if "Stair" in str(n.name) or "stair" in str(n.name):print(n.get_path()," ",n.get_aabb()," ",n.global_transform)
 quit()
