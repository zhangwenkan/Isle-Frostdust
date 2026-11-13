extends CanvasLayer
## Standalone UI: starts only through start_dialogue(), never on scene entry.
## The caller owns player input locking; environment animation keeps running.

const DialogueContent = preload("res://scripts/dialogue/dialogue_content.gd")
const DESIGN_SIZE := Vector2(1240, 259)
const PORTRAIT_RISE := 292.0

signal dialogue_started(dialogue_id: StringName)
signal dialogue_finished(dialogue_id: StringName)
signal page_changed(page_index: int, page_count: int)

@export var content: DialogueContent
@export_range(0.0, 90.0, 1.0) var characters_per_second := 30.0

@onready var screen: Control = $Screen
@onready var card: Control = $Screen/Card
@onready var portrait: TextureRect = $Screen/Card/Portrait
@onready var speaker: Label = $Screen/Card/Nameplate/Speaker
@onready var body: RichTextLabel = $Screen/Card/Body
@onready var advance_button: TextureButton = $Screen/Card/Advance

var _current: DialogueContent
var _page := 0
var _revealed := 0.0
var _character_count := 0
var _active := false
var _accept_after_msec := 0


func _ready() -> void:
	screen.hide()
	set_process(false)
	set_process_unhandled_input(false)
	screen.resized.connect(_fit_card)
	card.gui_input.connect(_on_card_gui_input)
	advance_button.pressed.connect(advance)
	_fit_card()
	if content != null:
		speaker.text = content.speaker_name
		portrait.texture = content.portrait


func is_dialogue_active() -> bool:
	return _active


func cancel_dialogue() -> void:
	# Scene reset cancels without emitting normal story completion.
	_active = false
	_current = null
	screen.hide()
	set_process(false)
	set_process_unhandled_input(false)


func start_dialogue(next_content: DialogueContent = null) -> bool:
	# A rejected call leaves an existing conversation intact.
	if not is_node_ready() or _active:
		return false
	var selected: DialogueContent = next_content if next_content != null else content
	if selected == null or selected.pages.is_empty():
		return false
	_current = selected
	_page = 0
	_active = true
	speaker.text = _current.speaker_name
	portrait.texture = _current.portrait
	screen.show()
	_fit_card()
	_show_page()
	# Avoid consuming the same confirm press that opened the dialogue.
	_accept_after_msec = Time.get_ticks_msec() + 150
	set_process(true)
	set_process_unhandled_input(true)
	dialogue_started.emit(_current.dialogue_id)
	return true


func advance() -> void:
	if not _active or Time.get_ticks_msec() < _accept_after_msec:
		return
	if body.visible_characters < _character_count:
		_revealed = float(_character_count)
		body.visible_characters = _character_count
		_update_advance()
		return
	if _page + 1 < _current.pages.size():
		_page += 1
		_show_page()
		return
	var finished_id := _current.dialogue_id
	_active = false
	screen.hide()
	set_process(false)
	set_process_unhandled_input(false)
	_current = null
	dialogue_finished.emit(finished_id)


func _show_page() -> void:
	body.text = _current.pages[_page]
	_character_count = body.get_total_character_count()
	_revealed = float(_character_count) if characters_per_second <= 0.0 else 0.0
	body.visible_characters = int(_revealed)
	_update_advance()
	page_changed.emit(_page, _current.pages.size())


func _process(delta: float) -> void:
	if not _active or body.visible_characters >= _character_count:
		return
	_revealed = minf(float(_character_count), _revealed + delta * characters_per_second)
	body.visible_characters = int(_revealed)
	if body.visible_characters >= _character_count:
		_update_advance()


func _update_advance() -> void:
	var revealing := body.visible_characters < _character_count
	advance_button.modulate.a = 0.6 if revealing else 1.0


func _unhandled_input(event: InputEvent) -> void:
	if not _active:
		return
	if event.is_action_pressed("ui_accept") and not event.is_echo():
		get_viewport().set_input_as_handled()
		advance()


func _on_card_gui_input(event: InputEvent) -> void:
	if event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT and event.pressed:
		card.accept_event()
		advance()


func _fit_card() -> void:
	# Scale the composition together so portrait, plaque and border stay aligned.
	var fit_scale := minf(1.0, minf((screen.size.x - 40.0) / DESIGN_SIZE.x,
		(screen.size.y - 32.0) / (DESIGN_SIZE.y + PORTRAIT_RISE)))
	fit_scale = maxf(0.1, fit_scale)
	card.size = DESIGN_SIZE
	card.scale = Vector2.ONE * fit_scale
	card.position = Vector2((screen.size.x - DESIGN_SIZE.x * fit_scale) * 0.5,
		screen.size.y - DESIGN_SIZE.y * fit_scale - 12.0)
