extends Node
## Owns the cape opening; never pauses the tree or alters frame alignment.

enum Phase { INACTIVE, ESTABLISHING, RISING, DIALOGUE_REFRAME, DIALOGUE, TRANSITION, COMPLETE }

const REST_FRAMES = preload("res://assets/characters/rest_rise_right/color_matched/rest_rise_color_matched.tres")
const DIALOGUE_SCENE = preload("res://scenes/ui/an_lixing_dialogue.tscn")
const REST_ANIMATION := &"rest_rise_right"
const INTRO_HOLD := 1.8
const INTRO_DURATION := 7.2
const TITLE_FONT = preload("res://assets/ui/fonts/cubic_11/Cubic_11.ttf")

var phase := Phase.INACTIVE
var enabled := true
var island: Node3D
var dialogue: CanvasLayer
var _walking_frames: SpriteFrames
var _restore_hud := true
var transition_elapsed := 0.0
var intro_elapsed := 0.0
var title_layer: CanvasLayer
var title_group: VBoxContainer


func configure(scene: Node3D, play_on_entry: bool) -> void:
	island = scene
	enabled = play_on_entry
	_walking_frames = island.hero.sprite_frames
	dialogue = DIALOGUE_SCENE.instantiate()
	add_child(dialogue)
	dialogue.dialogue_finished.connect(_on_dialogue_finished)
	island.hero.animation_finished.connect(_on_animation_finished)
	_build_title()
	# Advance before the island camera so a phase boundary uses the same frame.
	process_priority = -10
	if enabled:
		start()


func is_input_locked() -> bool:
	return phase in [Phase.ESTABLISHING,Phase.RISING,Phase.DIALOGUE_REFRAME,Phase.DIALOGUE,Phase.TRANSITION]

func is_cape_shot() -> bool:
	return phase in [Phase.ESTABLISHING,Phase.RISING,Phase.DIALOGUE_REFRAME,Phase.DIALOGUE]

func descent_progress() -> float:
	return smoothstep(INTRO_HOLD, INTRO_DURATION, intro_elapsed)

func _build_title() -> void:
	title_layer = CanvasLayer.new()
	title_layer.name = "IslandIntroduction"
	title_layer.layer = 15
	add_child(title_layer)
	var center := CenterContainer.new()
	center.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	center.mouse_filter = Control.MOUSE_FILTER_IGNORE
	title_layer.add_child(center)
	title_group = VBoxContainer.new()
	title_group.mouse_filter = Control.MOUSE_FILTER_IGNORE
	title_group.add_theme_constant_override("separation", 18)
	center.add_child(title_group)
	for item in [["無人岛",48], ["大雍 · 景宁十七年",24]]:
		var label := Label.new()
		label.text = item[0]
		label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		label.mouse_filter = Control.MOUSE_FILTER_IGNORE
		label.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
		label.add_theme_font_override("font", TITLE_FONT)
		label.add_theme_font_size_override("font_size", item[1])
		label.add_theme_color_override("font_color", Color("f3f1da"))
		label.add_theme_color_override("font_shadow_color", Color(.015,.09,.12,.65))
		label.add_theme_constant_override("shadow_offset_x", 2)
		label.add_theme_constant_override("shadow_offset_y", 3)
		title_group.add_child(label)
	title_layer.hide()

func _update_title() -> void:
	title_group.modulate.a = smoothstep(.55,1.45,intro_elapsed) * (1.0-smoothstep(4.2,5.35,intro_elapsed))

func _process(delta: float) -> void:
	if phase == Phase.ESTABLISHING:
		intro_elapsed = minf(intro_elapsed + delta, INTRO_DURATION)
		_update_title()
		if intro_elapsed >= INTRO_DURATION:
			_begin_rising()
	if phase == Phase.DIALOGUE_REFRAME:
		transition_elapsed += delta
		if transition_elapsed >= 1.4:
			phase = Phase.DIALOGUE
			if not dialogue.start_dialogue():
				push_error("Opening dialogue could not start.")
				_finish()
	if phase == Phase.TRANSITION:
		transition_elapsed += delta
		if transition_elapsed >= 1.8:
			phase = Phase.COMPLETE
			island.hud.visible = _restore_hud


func start() -> void:
	if not enabled:
		return
	if not is_input_locked():
		_restore_hud = island.hud.visible
	dialogue.cancel_dialogue()
	phase = Phase.ESTABLISHING
	intro_elapsed = 0.0
	transition_elapsed = 0.0
	island.hud.hide()
	island.hero.stop()
	island.hero.sprite_frames = REST_FRAMES
	island.hero.flip_h = false
	island.hero.animation = REST_ANIMATION
	island.hero.set_frame_and_progress(0,0.0)
	title_layer.show()
	_update_title()

func _begin_rising() -> void:
	title_layer.hide()
	phase = Phase.RISING
	island.hero.play(REST_ANIMATION)
	island.hero.set_frame_and_progress(0,0.0)


func _on_animation_finished() -> void:
	if phase != Phase.RISING or island.hero.animation != REST_ANIMATION:
		return
	island.hero.sprite_frames = _walking_frames
	island._set_hero_animation(&"idle_right", false)
	island.hero.frame = 0
	phase = Phase.DIALOGUE_REFRAME
	transition_elapsed = 0.0


func _on_dialogue_finished(dialogue_id: StringName) -> void:
	if phase == Phase.DIALOGUE and dialogue_id == &"an_lixing_after_rest":
		_finish()


func _finish() -> void:
	phase = Phase.TRANSITION
	transition_elapsed = 0.0
