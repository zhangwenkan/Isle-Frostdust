"""Read existing Blender GLB floors into a water coverage mask; no mesh edits."""
import hashlib
import json
import struct
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'assets/layered_island/layered_island.glb'
OUT = ROOT / 'assets/layered_island/forest_extension'
data = SOURCE.read_bytes()
length, kind = struct.unpack_from('<II', data, 12)
doc = json.loads(data[20:20 + length])
names_in_asset = {node.get('name') for node in doc['nodes']}
NAMES = {'WALK_Forest_Ground'} | ({'Forest_Valley_Ground','Forest_Back_Ground'} & names_in_asset)
offset = 20 + length
length, kind = struct.unpack_from('<II', data, offset)
binary = data[offset + 8:offset + 8 + length]

def accessor(index):
    a = doc['accessors'][index]
    view = doc['bufferViews'][a['bufferView']]
    components = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4}[a['type']]
    dtype = np.dtype({5121: '<u1', 5123: '<u2', 5125: '<u4', 5126: '<f4'}[a['componentType']])
    return np.ndarray((a['count'], components), dtype=dtype, buffer=binary,
                      offset=view.get('byteOffset', 0) + a.get('byteOffset', 0),
                      strides=(view.get('byteStride', dtype.itemsize * components), dtype.itemsize)).copy()

def transform(node):
    if 'matrix' in node:
        return np.array(node['matrix'], dtype=float).reshape((4, 4), order='F')
    x, y, z, w = node.get('rotation', [0, 0, 0, 1])
    rotation = np.array([[1-2*(y*y+z*z), 2*(x*y-z*w), 2*(x*z+y*w)],
                         [2*(x*y+z*w), 1-2*(x*x+z*z), 2*(y*z-x*w)],
                         [2*(x*z-y*w), 2*(y*z+x*w), 1-2*(x*x+y*y)]])
    result = np.eye(4)
    result[:3, :3] = rotation @ np.diag(node.get('scale', [1, 1, 1]))
    result[:3, 3] = node.get('translation', [0, 0, 0])
    return result

parents = {child: i for i, node in enumerate(doc['nodes']) for child in node.get('children', [])}
def accumulated(index):
    matrix = transform(doc['nodes'][index])
    return accumulated(parents[index]) @ matrix if index in parents else matrix

surfaces = []
for i, node in enumerate(doc['nodes']):
    if node.get('name') not in NAMES:
        continue
    for primitive in doc['meshes'][node['mesh']]['primitives']:
        vertices = accessor(primitive['attributes']['POSITION'])
        points = np.c_[vertices, np.ones(len(vertices))] @ accumulated(i).T
        indices = accessor(primitive['indices']).reshape((-1, 3))
        surfaces.append((node['name'], points[:, [0, 2]], indices))
assert {name for name, _, _ in surfaces} == NAMES
points = np.concatenate([p for _, p, _ in surfaces])
lower = points.min(axis=0) - 1.0
upper = points.max(axis=0) + 1.0
size = (1024, 576)
mask = Image.new('L', size, 0)
draw = ImageDraw.Draw(mask)
for _, points, indices in surfaces:
    pixels = (points - lower) / (upper - lower) * np.array(size)
    for triangle in indices:
        draw.polygon([tuple(pixels[j]) for j in triangle], fill=255)
OUT.mkdir(parents=True, exist_ok=True)
mask.save(OUT / 'forest_water_mask.png')
metadata = {'source': str(SOURCE.relative_to(ROOT)),
            'source_sha256': hashlib.sha256(data).hexdigest(),
            'floors': sorted(NAMES), 'bounds': [*lower.tolist(), *(upper-lower).tolist()],
            'size': size, 'triangles_read': sum(len(t) for _, _, t in surfaces),
            'purpose': 'Exclude the physical ocean from the existing inland forest valley. White is dry land.',
            'changes_geometry_or_uv': False}
(OUT / 'forest_water_mask.json').write_text(json.dumps(metadata, indent=2), encoding='utf-8')
print(json.dumps(metadata))
