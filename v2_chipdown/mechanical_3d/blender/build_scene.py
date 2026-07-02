# Run inside Blender: blender --background --python build_scene.py
import json
from pathlib import Path
import bpy
base = Path(__file__).resolve().parents[1]
data = json.loads((base / "models" / "glasses_assembly_model.json").read_text())
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()
for p in data["parts"]:
    bpy.ops.mesh.primitive_cube_add(size=1, location=(p["x"] + p["l"]/2, p["y"] + p["w"]/2, p["z"] + p["h"]/2))
    obj = bpy.context.object
    obj.name = p["id"] + "_" + p["ref"]
    obj.dimensions = (p["l"], p["w"], p["h"])
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
bpy.ops.wm.save_as_mainfile(filepath=str(base / "blender" / "ai_glasses_render.blend"))
