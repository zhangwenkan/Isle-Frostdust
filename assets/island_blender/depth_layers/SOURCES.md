# Depth composition sources

- Bamboo stems, branches and leaf geometry: authored within Blender through blender-mcp, `tools/blender/hd2d_depth_layers.py`.
- Mountain massifs: authored within Blender through blender-mcp, `tools/blender/mountain_depth_refine.py`. Three connected ranges with asymmetric divides, branching ribs and ledges; vertex colors, no image surface textures.
- Foreground cliff outcrops reuse the existing Fish rock topology, UVs and materials. Their upstream provenance is retained in `../fish_reference/SOURCES.md` and `../palm_study/source_manifest.json`.
- User composition reference: `artifacts/mountain-depth-review/reference/user-mountain-reference.png`; used to study overlapping mountains and the separation of middle and far scenery. It is not used as a game texture.
- Sky cloud cover is an original transparent panorama painted by `tools/prepare_coastal_clouds.py` and applied to Godot's existing procedural sky.
