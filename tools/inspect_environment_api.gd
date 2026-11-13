extends SceneTree
func _initialize() -> void:
	for key in ClassDB.class_get_integer_constant_list("Environment"):
		if "REFLECT" in key or "SKY" in key:
			print(key, " = ", ClassDB.class_get_integer_constant("Environment", key))
	quit()
