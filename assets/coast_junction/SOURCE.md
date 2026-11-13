# Coast junction sample

Geometry and UV editing: Blender MCP, `tools/blender/refine_coast_junction.py`. Five locally authored original coastal modules are clipped into the sample while preserving UV0; a new recessed core and crown connect them to the turf. No Wandering Sword geometry, UV, or texture is used.

The five relief meshes retain the self-painted plus Poly Haven CC0-derived pigments documented in `../original_coastal_rock/SOURCE.md`; this sample is not claimed to have all textures painted from scratch. Their contact UVs and AO are newly baked in the current assembly.

The new crown/core pigment texture alone is drawn by `tools/paint_coast_junction.py`. Its alpha stores the grass/material blend, not transparency. The original painted grass is shared at the thin upper seam. The main island blend contains the corresponding edited land and archived baseline.
