"""Reuse the existing in-game motion check for the new integrated coast."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]
s=(root/'tools/review_reference_cape_motion.gd').read_text(encoding='utf8')
s=s.replace('res://artifacts/reference-cape-review/','res://artifacts/forest-rocky-terminus-review/')
s=s.replace('var stages=[["forest_west_mid",48],["cape_center",96],["cape_shore_end",96],["forest_west_mid",72]]','var stages=[["forest_west_mid",72],["cape_center",144],["cape_shore_end",72],["forest_west_mid",72]]')
s=s.replace('REFERENCE_CAPE_MOTION','ROCKY_TERMINUS_MOTION')
(root/'tools/review_rocky_terminus_motion.gd').write_text(s,encoding='utf8')
print('Prepared the integrated motion check')
