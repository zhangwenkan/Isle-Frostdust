"""Refresh final local artwork in the existing Blender source via MCP."""
exec(compile(open('D:/自己做着玩的/孤屿霜尘/tools/blender/left_finish_common.py',encoding='utf-8').read(),'left_finish_common.py','exec'))
assert 'study_framing_correction' in LAYOUT['forest_extension']['layer_roles']
refreshed=[]
for im in bpy.data.images:
    if '/forest_layers/' in bpy.path.abspath(im.filepath).replace('\\','/'):
        im.reload();im.pack();refreshed.append(im.name)
(ROOT/'artifacts/forest-wind-mist-review/packed-paint.json').write_text(json.dumps({'images':refreshed,'changes_geometry_or_uv':False},indent=2),encoding='utf-8')
export('study-dark-forest-local-mist')
