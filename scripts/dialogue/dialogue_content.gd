extends Resource
## Text and portrait only. Trigger timing belongs to the scene director.

@export var dialogue_id: StringName
@export var speaker_name := ""
@export var portrait: Texture2D
@export_multiline var original_text := ""
@export var pages: PackedStringArray = PackedStringArray()
