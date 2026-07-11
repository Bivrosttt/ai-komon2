"""Build the browser walkthrough GLB from the editable furnished Blender file.

The main Blender file is a dollhouse/cutaway presentation model. This exporter
temporarily restores full-height partitions and adds a ceiling so a 1.6 m POV
camera reads as an interior instead of looking over the walls.
"""

import os

import bpy


ROOT = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(ROOT, "floorplan-furnished.blend")
OUTPUT = os.path.join(ROOT, "floorplan-walkthrough.glb")

bpy.ops.wm.open_mainfile(filepath=SOURCE)

wall_prefixes = (
    "Outer ",
    "LDK north",
    "NW bed WIC",
    "LDK hall",
    "Hall west",
    "Hall east",
    "Service south",
    "Wash bath",
    "Bath corridor",
    "South rooms north",
    "South bedroom divide",
    "Toilet north",
    "Toilet west",
)

for obj in bpy.data.objects:
    if obj.type != "MESH" or not obj.name.startswith(wall_prefixes):
        continue
    obj.dimensions.z = 2.55
    obj.location.z = 1.36

# Close the apartment volume for a believable first-person interior. Lighting
# in the web viewer is non-shadow-casting, so the ceiling does not make the
# rooms unnaturally dark.
bpy.ops.mesh.primitive_cube_add(location=(5.0, 6.5, 2.68))
ceiling = bpy.context.object
ceiling.name = "Walkthrough Ceiling"
ceiling.scale = (5.0, 6.5, 0.06)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
wall_material = bpy.data.materials.get("Warm white walls")
if wall_material:
    ceiling.data.materials.append(wall_material)

# The large studio backdrop is useful for the isometric render but unnecessary
# inside the apartment and increases ray-cast work in the browser.
backdrop = bpy.data.objects.get("Backdrop")
if backdrop:
    backdrop.hide_render = True
    backdrop.hide_viewport = True

bpy.context.scene["walkthrough_eye_height_m"] = 1.60
bpy.context.scene["walkthrough_bounds"] = "x:0.2..9.8, y:0.2..12.8"

bpy.ops.export_scene.gltf(
    filepath=OUTPUT,
    export_format="GLB",
    export_apply=True,
    export_cameras=False,
    export_lights=False,
    export_yup=True,
    use_visible=True,
)

print("WALKTHROUGH:", OUTPUT)
