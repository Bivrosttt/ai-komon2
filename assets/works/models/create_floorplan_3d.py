import bpy
import math
import os
from mathutils import Vector


ROOT = os.path.dirname(os.path.abspath(__file__))
BLEND_PATH = os.path.join(ROOT, "floorplan-furnished.blend")
RENDER_PATH = os.path.join(ROOT, "floorplan-furnished.png")
TOP_RENDER_PATH = os.path.join(ROOT, "floorplan-furnished-top.png")
GLB_PATH = os.path.join(ROOT, "floorplan-furnished.glb")


def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for datablocks in (bpy.data.meshes, bpy.data.curves, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        for datablock in list(datablocks):
            if datablock.users == 0:
                datablocks.remove(datablock)


def mat(name, color, roughness=0.55, metallic=0.0, alpha=1.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color = (*color, alpha)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Alpha"].default_value = alpha
    if alpha < 1:
        m.surface_render_method = "DITHERED"
    return m


def collection(name):
    c = bpy.data.collections.get(name) or bpy.data.collections.new(name)
    if c.name not in bpy.context.scene.collection.children:
        bpy.context.scene.collection.children.link(c)
    return c


def move_to_collection(obj, coll):
    for old in list(obj.users_collection):
        old.objects.unlink(obj)
    coll.objects.link(obj)


def box(name, loc, scale, material, coll, bevel=0.03, rotation=0.0):
    bpy.ops.mesh.primitive_cube_add(location=loc, rotation=(0, 0, rotation))
    o = bpy.context.object
    o.name = name
    o.scale = (scale[0] / 2, scale[1] / 2, scale[2] / 2)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if material:
        o.data.materials.append(material)
    if bevel:
        mod = o.modifiers.new("Soft edges", "BEVEL")
        mod.width = bevel
        mod.segments = 2
    move_to_collection(o, coll)
    return o


def cylinder(name, loc, radius, depth, material, coll, vertices=32):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc)
    o = bpy.context.object
    o.name = name
    if material:
        o.data.materials.append(material)
    mod = o.modifiers.new("Soft edges", "BEVEL")
    mod.width = min(0.03, radius * 0.15)
    mod.segments = 2
    move_to_collection(o, coll)
    return o


def wall_x(name, x1, x2, y, h=1.65, t=0.14, z=None):
    z = h / 2 + 0.08 if z is None else z
    return box(name, ((x1 + x2) / 2, y, z), (x2 - x1, t, h), WALL, ARCH, 0.025)


def wall_y(name, x, y1, y2, h=1.65, t=0.14, z=None):
    z = h / 2 + 0.08 if z is None else z
    return box(name, (x, (y1 + y2) / 2, z), (t, y2 - y1, h), WALL, ARCH, 0.025)


def floor_zone(name, x1, x2, y1, y2, material):
    return box(name, ((x1 + x2) / 2, (y1 + y2) / 2, 0.035), (x2 - x1, y2 - y1, 0.07), material, FLOORS, 0.0)


def window_x(name, x1, x2, y, sill=0.65):
    cx = (x1 + x2) / 2
    width = x2 - x1
    box(name + "_glass", (cx, y, sill + 0.72), (width, 0.035, 1.35), GLASS, ARCH, 0.005)
    for x in (x1, cx, x2):
        box(name + "_frame", (x, y, sill + 0.72), (0.045, 0.07, 1.46), FRAME, ARCH, 0.005)
    for z in (sill, sill + 1.44):
        box(name + "_frame", (cx, y, z), (width + 0.05, 0.07, 0.05), FRAME, ARCH, 0.005)


def window_y(name, x, y1, y2, sill=0.65):
    cy = (y1 + y2) / 2
    width = y2 - y1
    box(name + "_glass", (x, cy, sill + 0.72), (0.035, width, 1.35), GLASS, ARCH, 0.005)
    for y in (y1, cy, y2):
        box(name + "_frame", (x, y, sill + 0.72), (0.07, 0.045, 1.46), FRAME, ARCH, 0.005)
    for z in (sill, sill + 1.44):
        box(name + "_frame", (x, cy, z), (0.07, width + 0.05, 0.05), FRAME, ARCH, 0.005)


def door(name, x, y, width=0.78, along="x", angle=0.0):
    # An open door leaf makes circulation and room entrances readable from above.
    if along == "x":
        o = box(name, (x, y, 1.05), (width, 0.045, 2.02), DOOR, ARCH, 0.02, angle)
    else:
        o = box(name, (x, y, 1.05), (0.045, width, 2.02), DOOR, ARCH, 0.02, angle)
    return o


def rug(name, x, y, sx, sy, material, rot=0):
    return box(name, (x, y, 0.105), (sx, sy, 0.035), material, FURNITURE, 0.04, rot)


def table(name, x, y, sx, sy, h=0.74, rot=0, top_mat=None):
    top_mat = top_mat or WOOD
    top = box(name + "_top", (x, y, h), (sx, sy, 0.08), top_mat, FURNITURE, 0.05, rot)
    c, s = math.cos(rot), math.sin(rot)
    for dx in (-sx * 0.38, sx * 0.38):
        for dy in (-sy * 0.34, sy * 0.34):
            rx, ry = dx * c - dy * s, dx * s + dy * c
            box(name + "_leg", (x + rx, y + ry, h / 2), (0.07, 0.07, h), DARK, FURNITURE, 0.015)
    return top


def chair(name, x, y, rot=0, material=None):
    material = material or BLUE
    box(name + "_seat", (x, y, 0.48), (0.48, 0.48, 0.10), material, FURNITURE, 0.07, rot)
    c, s = math.cos(rot), math.sin(rot)
    back_dx, back_dy = 0, 0.21
    rx, ry = back_dx * c - back_dy * s, back_dx * s + back_dy * c
    box(name + "_back", (x + rx, y + ry, 0.78), (0.46, 0.08, 0.58), material, FURNITURE, 0.06, rot)
    for dx, dy in ((-0.18, -0.18), (0.18, -0.18), (-0.18, 0.18), (0.18, 0.18)):
        rx, ry = dx * c - dy * s, dx * s + dy * c
        box(name + "_leg", (x + rx, y + ry, 0.24), (0.045, 0.045, 0.45), DARK, FURNITURE, 0.01)


def bed(name, x, y, sx=1.4, sy=2.0, rot=0, accent=None):
    accent = accent or BLUE
    box(name + "_base", (x, y, 0.30), (sx, sy, 0.36), WOOD_DARK, FURNITURE, 0.08, rot)
    box(name + "_mattress", (x, y, 0.54), (sx - 0.08, sy - 0.10, 0.24), LINEN, FURNITURE, 0.10, rot)
    c, s = math.cos(rot), math.sin(rot)
    # Headboard and pillows are offset along local +Y.
    hx, hy = -0.0 * s + (sy / 2 - 0.07) * -s, (sy / 2 - 0.07) * c
    box(name + "_head", (x + hx, y + hy, 0.78), (sx, 0.10, 0.95), WOOD_DARK, FURNITURE, 0.05, rot)
    for px in (-sx * 0.25, sx * 0.25):
        rx, ry = px * c - (sy * 0.28) * s, px * s + (sy * 0.28) * c
        box(name + "_pillow", (x + rx, y + ry, 0.72), (sx * 0.37, 0.42, 0.16), LINEN_LIGHT, FURNITURE, 0.10, rot)
    rx, ry = -(sy * 0.15) * s, (sy * 0.15) * c
    box(name + "_throw", (x - rx, y - ry, 0.70), (sx - 0.12, sy * 0.52, 0.07), accent, FURNITURE, 0.04, rot)


def futon(name, x, y, sx=1.40, sy=2.05, rot=0, accent=None):
    """Japanese floor bedding without a raised frame or headboard."""
    accent = accent or GREEN
    box(name + "_shikibuton", (x, y, 0.16), (sx, sy, 0.22), LINEN_LIGHT, FURNITURE, 0.12, rot)
    c, s = math.cos(rot), math.sin(rot)
    px, py = -(sy * 0.31) * s, (sy * 0.31) * c
    box(name + "_pillow", (x + px, y + py, 0.32), (sx * 0.64, 0.40, 0.16), LINEN, FURNITURE, 0.10, rot)
    bx, by = (sy * 0.17) * s, -(sy * 0.17) * c
    box(name + "_kakebuton", (x + bx, y + by, 0.34), (sx - 0.10, sy * 0.58, 0.18), accent, FURNITURE, 0.12, rot)


def sofa(name, x, y, sx=2.45, sy=0.92, rot=0, material=None):
    material = material or SOFA
    box(name + "_base", (x, y, 0.30), (sx, sy, 0.34), material, FURNITURE, 0.12, rot)
    c, s = math.cos(rot), math.sin(rot)
    bx, by = -(sy * 0.35) * s, (sy * 0.35) * c
    box(name + "_back", (x + bx, y + by, 0.72), (sx, 0.20, 0.75), material, FURNITURE, 0.10, rot)
    for side in (-1, 1):
        ax, ay = side * (sx * 0.46) * c, side * (sx * 0.46) * s
        box(name + "_arm", (x + ax, y + ay, 0.52), (0.20, sy, 0.56), material, FURNITURE, 0.09, rot)
    for side, cm in ((-0.5, OCHRE), (0.5, GREEN)):
        px, py = side * 0.62 * c - 0.1 * s, side * 0.62 * s + 0.1 * c
        box(name + "_cushion", (x + px, y + py, 0.70), (0.52, 0.16, 0.45), cm, FURNITURE, 0.09, rot)


def cabinet(name, x, y, sx, sy, h, material=None, rot=0):
    return box(name, (x, y, h / 2 + 0.08), (sx, sy, h), material or CABINET, FURNITURE, 0.035, rot)


def plant(name, x, y, scale=1.0):
    cylinder(name + "_pot", (x, y, 0.18 * scale), 0.18 * scale, 0.36 * scale, TERRACOTTA, DECOR, 24)
    cylinder(name + "_stem", (x, y, 0.57 * scale), 0.035 * scale, 0.55 * scale, STEM, DECOR, 12)
    for i, (dx, dy, z, r) in enumerate(((0.0, 0.0, 0.85, 0.25), (0.18, 0.02, 0.72, 0.18), (-0.13, 0.08, 0.66, 0.17), (0.05, -0.12, 0.60, 0.16))):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=r * scale, location=(x + dx * scale, y + dy * scale, z * scale))
        o = bpy.context.object
        o.name = name + "_leaf_" + str(i)
        o.scale.z = 1.4
        o.data.materials.append(LEAF)
        move_to_collection(o, DECOR)


def toilet(name, x, y, rot=0):
    box(name + "_tank", (x, y + 0.28, 0.48), (0.55, 0.28, 0.72), PORCELAIN, FIXTURES, 0.10, rot)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, location=(x, y - 0.05, 0.32), scale=(0.34, 0.48, 0.22), rotation=(0, 0, rot))
    o = bpy.context.object
    o.name = name + "_bowl"
    o.data.materials.append(PORCELAIN)
    move_to_collection(o, FIXTURES)


def add_label(body, x, y, size=0.32):
    bpy.ops.object.text_add(location=(x, y, 0.095))
    o = bpy.context.object
    o.name = "Label_" + body
    o.data.body = body
    o.data.align_x = "CENTER"
    o.data.align_y = "CENTER"
    o.data.size = size
    o.data.extrude = 0.006
    o.data.materials.append(LABEL)
    move_to_collection(o, LABELS)
    return o


clear_scene()

ARCH = collection("01 Architecture")
FLOORS = collection("02 Room Floors")
FURNITURE = collection("03 Furniture")
FIXTURES = collection("04 Kitchen Bath Fixtures")
DECOR = collection("05 Decor and Plants")
LABELS = collection("06 Room Labels")
LIGHTS = collection("07 Lighting")

WALL = mat("Warm white walls", (0.91, 0.88, 0.82), 0.78)
FRAME = mat("Window frames", (0.08, 0.10, 0.11), 0.35, 0.15)
GLASS = mat("Window glass", (0.33, 0.67, 0.78), 0.12, 0.05, 0.30)
DOOR = mat("Oak doors", (0.50, 0.29, 0.14), 0.48)
WOOD = mat("Oak", (0.56, 0.34, 0.17), 0.48)
WOOD_DARK = mat("Walnut", (0.20, 0.10, 0.055), 0.48)
DARK = mat("Charcoal metal", (0.055, 0.065, 0.072), 0.28, 0.45)
CABINET = mat("Kitchen cabinetry", (0.78, 0.75, 0.69), 0.42)
COUNTER = mat("Stone counter", (0.87, 0.86, 0.82), 0.24)
PORCELAIN = mat("White porcelain", (0.94, 0.96, 0.97), 0.18)
METAL = mat("Brushed steel", (0.42, 0.46, 0.48), 0.20, 0.65)
LINEN = mat("Warm linen", (0.86, 0.80, 0.71), 0.82)
LINEN_LIGHT = mat("Pillows", (0.97, 0.96, 0.92), 0.88)
SOFA = mat("Sage sofa", (0.34, 0.43, 0.34), 0.86)
BLUE = mat("Dusty blue", (0.25, 0.42, 0.55), 0.78)
GREEN = mat("Deep green", (0.12, 0.30, 0.20), 0.78)
OCHRE = mat("Ochre", (0.78, 0.42, 0.10), 0.72)
PINK = mat("Muted rose", (0.63, 0.33, 0.32), 0.82)
RUG_BLUE = mat("Blue rug", (0.16, 0.32, 0.42), 0.92)
RUG_WARM = mat("Warm rug", (0.72, 0.57, 0.38), 0.92)
TERRACOTTA = mat("Terracotta", (0.54, 0.22, 0.10), 0.80)
STEM = mat("Plant stems", (0.12, 0.22, 0.08), 0.78)
LEAF = mat("Plant leaves", (0.13, 0.34, 0.15), 0.86)
LABEL = mat("Room label", (0.16, 0.13, 0.10), 0.75)
BALCONY = mat("Balcony concrete", (0.50, 0.52, 0.52), 0.88)
RAIL = mat("Balcony railing", (0.13, 0.15, 0.16), 0.30, 0.35)
FLOOR_LDK = mat("LDK oak floor", (0.72, 0.55, 0.33), 0.72)
FLOOR_BED = mat("Bedroom floor", (0.66, 0.49, 0.31), 0.72)
FLOOR_HALL = mat("Hall floor", (0.78, 0.66, 0.48), 0.74)
FLOOR_WET = mat("Wet room tile", (0.54, 0.70, 0.73), 0.62)
FLOOR_ENTRY = mat("Entry tile", (0.42, 0.44, 0.44), 0.72)

# Apartment footprint is approximately 10m x 13m. It is inferred from room areas
# (23 jo LDK, 6-7 jo bedrooms) because the source plan contains no dimensions.
floor_zone("LDK lower", 0.15, 4.65, 0.15, 4.55, FLOOR_LDK)
floor_zone("LDK kitchen dining", 0.15, 5.35, 4.55, 8.45, FLOOR_LDK)
floor_zone("Bedroom NW 6.7 jo", 0.15, 3.55, 8.55, 12.85, FLOOR_BED)
floor_zone("WIC", 3.65, 5.15, 9.65, 12.85, FLOOR_HALL)
floor_zone("Central hall", 5.45, 6.70, 4.65, 12.85, FLOOR_HALL)
floor_zone("Service room 6 jo", 6.82, 9.85, 8.55, 12.85, FLOOR_BED)
floor_zone("Washroom", 6.82, 9.85, 6.55, 8.40, FLOOR_WET)
floor_zone("Bathroom", 7.20, 9.85, 4.70, 6.42, FLOOR_WET)
floor_zone("Toilet", 5.25, 6.65, 5.05, 6.42, FLOOR_WET)
floor_zone("Bedroom South 7.1 jo", 4.75, 7.45, 0.15, 4.48, FLOOR_BED)
floor_zone("Kids room 6.4 jo", 7.55, 9.85, 0.15, 4.48, FLOOR_BED)
floor_zone("Entrance", 5.35, 6.70, 11.55, 12.85, FLOOR_ENTRY)

# Balcony and porch slabs.
floor_zone("West balcony", -1.15, -0.08, 0.10, 8.35, BALCONY)
floor_zone("North balcony", 0.0, 5.10, 13.05, 14.05, BALCONY)
floor_zone("South balcony", 0.85, 9.95, -1.15, -0.08, BALCONY)
floor_zone("Entrance porch", 5.20, 10.0, 13.05, 14.05, BALCONY)

# Exterior shell. Balcony-facing sides are broken around the large sliding
# windows shown in the source plan instead of being modeled as solid walls.
wall_x("Outer south LDK left pier", 0.0, 0.65, 0.0, 1.15)
wall_x("Outer south LDK right pier", 4.25, 4.72, 0.0, 1.15)
wall_x("Outer south center piers A", 4.72, 5.15, 0.0, 1.15)
wall_x("Outer south center piers B", 7.15, 7.75, 0.0, 1.15)
wall_x("Outer south east pier", 9.55, 10.0, 0.0, 1.15)
wall_x("Outer north NW left pier", 0.0, 0.65, 13.0, 2.55)
wall_x("Outer north NW right pier", 2.95, 5.2, 13.0, 2.55)
wall_x("Outer north service left pier", 5.2, 7.20, 13.0, 2.55)
wall_x("Outer north service right pier", 9.55, 10.0, 13.0, 2.55)
wall_y("Outer west LDK lower pier", 0.0, 0.0, 2.20, 1.15)
wall_y("Outer west LDK upper pier", 0.0, 6.60, 9.50, 1.15)
wall_y("Outer west NW upper pier", 0.0, 11.80, 13.0, 1.15)
wall_y("Outer east", 10.0, 0.0, 13.0, 2.55)

# Main partitions, intentionally split at doors.
wall_x("LDK north A", 0.0, 3.55, 8.50)
wall_x("LDK north B", 4.35, 5.40, 8.50)
wall_y("NW bed WIC A", 3.60, 8.50, 10.05)
wall_y("NW bed WIC B", 3.60, 10.88, 13.0)
wall_y("LDK hall lower", 4.70, 0.0, 3.48)
wall_y("LDK hall upper", 5.40, 4.30, 8.50)
wall_y("Hall west A", 5.25, 8.50, 10.25)
wall_y("Hall west B", 5.25, 11.08, 13.0)
wall_y("Hall east upper A", 6.72, 8.50, 10.25)
wall_y("Hall east upper B", 6.72, 11.08, 13.0)
wall_x("Service south A", 6.72, 7.22, 8.50)
wall_x("Service south B", 8.05, 10.0, 8.50)
wall_x("Wash bath", 6.72, 10.0, 6.48)
wall_y("Bath corridor A", 6.90, 4.55, 5.12)
wall_y("Bath corridor B", 6.90, 5.92, 8.50)
wall_x("South rooms north A", 4.70, 5.72, 4.55)
wall_x("South rooms north B", 6.55, 7.95, 4.55)
wall_x("South rooms north C", 8.75, 10.0, 4.55)
wall_y("South bedroom divide A", 7.50, 0.0, 3.50)
wall_y("South bedroom divide B", 7.50, 4.30, 4.55)
wall_x("Toilet north", 5.22, 6.90, 6.48)
wall_y("Toilet west", 5.22, 4.55, 6.48)

# Windows and readable open doors.
window_x("LDK south window", 0.65, 4.25, 0.00, 0.25)
window_y("LDK west window", 0.00, 2.2, 6.6, 0.45)
window_x("NW bedroom window", 0.65, 2.95, 13.00, 0.55)
window_y("NW bedroom side", 0.00, 9.5, 11.8, 0.55)
window_x("South bedroom window", 5.15, 7.15, 0.00, 0.35)
window_x("Kids room window", 7.75, 9.55, 0.00, 0.55)
window_x("Service room window", 7.20, 9.55, 13.00, 0.55)
door("Bedroom NW door", 3.98, 8.53, 0.78, "x", math.radians(50))
door("LDK hall door", 5.38, 3.88, 0.78, "x", math.radians(42))
door("South bedroom door", 6.12, 4.56, 0.78, "x", math.radians(-42))
door("Kids room door", 8.35, 4.56, 0.78, "x", math.radians(42))
door("Service door", 7.62, 8.52, 0.78, "x", math.radians(-45))
door("Bath door", 6.92, 5.52, 0.78, "y", math.radians(45))
door("Entrance door", 5.95, 13.00, 0.88, "x", math.radians(-50))

# Balcony railings.
for y in (0.25, 2.25, 4.25, 6.25, 8.15):
    box("West rail post", (-1.12, y, 0.58), (0.05, 0.05, 1.10), RAIL, ARCH, 0.005)
box("West rail top", (-1.12, 4.20, 1.08), (0.07, 8.05, 0.08), RAIL, ARCH, 0.01)
for x in (0.9, 3.1, 5.3, 7.5, 9.7):
    box("South rail post", (x, -1.10, 0.58), (0.05, 0.05, 1.10), RAIL, ARCH, 0.005)
box("South rail top", (5.30, -1.10, 1.08), (8.85, 0.07, 0.08), RAIL, ARCH, 0.01)
for x in (0.1, 1.75, 3.4, 5.0):
    box("North rail post", (x, 14.00, 0.58), (0.05, 0.05, 1.10), RAIL, ARCH, 0.005)
box("North rail top", (2.55, 14.00, 1.08), (4.95, 0.07, 0.08), RAIL, ARCH, 0.01)

# LDK: lounge, TV, dining for six, and peninsula kitchen.
rug("Living rug", 2.55, 2.70, 3.35, 2.45, RUG_BLUE)
# The balcony sides are glazed, so the 75-inch TV is mounted on the solid
# corridor-side wall. A 75-inch 16:9 panel is approximately 1.66m x 0.93m.
sofa("Living sofa facing TV", 1.75, 2.70, 2.65, 0.98, math.pi / 2, SOFA)
table("Coffee table", 2.95, 2.70, 0.68, 1.22, 0.40, 0, WOOD)
cabinet("Wall-side TV console", 4.48, 2.70, 0.30, 1.92, 0.46, WOOD_DARK)
tv = box("75-inch wall-mounted TV", (4.61, 2.70, 1.25), (0.075, 1.66, 0.94), DARK, FURNITURE, 0.045)
tv["screen_diagonal_inches"] = 75
box("TV soundbar", (4.54, 2.70, 0.76), (0.10, 1.05, 0.10), DARK, FURNITURE, 0.025)
plant("Living plant", 4.25, 1.25, 0.82)
# Rotate the dining group 90 degrees: table runs north-south and chairs sit
# on its left/right sides, matching the requested reverse orientation.
table("Dining table", 2.25, 6.58, 0.95, 2.10, 0.75, 0, WOOD)
for i, (x, y, r) in enumerate(((1.43, 5.86, math.pi / 2), (1.43, 6.58, math.pi / 2), (1.43, 7.30, math.pi / 2), (3.07, 5.86, -math.pi / 2), (3.07, 6.58, -math.pi / 2), (3.07, 7.30, -math.pi / 2))):
    chair("Dining chair " + str(i + 1), x, y, r, BLUE if i % 2 else GREEN)

# Kitchen back counter and island/peninsula.
cabinet("Kitchen back cabinets", 4.55, 7.86, 1.55, 0.55, 0.88, CABINET)
box("Kitchen back counter", (4.55, 7.86, 0.94), (1.64, 0.63, 0.08), COUNTER, FIXTURES, 0.025)
cabinet("Kitchen peninsula", 4.45, 6.63, 0.62, 2.10, 0.88, CABINET)
box("Kitchen peninsula counter", (4.45, 6.63, 0.94), (0.72, 2.18, 0.08), COUNTER, FIXTURES, 0.025)
box("Induction hob", (4.52, 7.90, 0.995), (0.54, 0.36, 0.025), DARK, FIXTURES, 0.01)
box("Sink", (4.45, 6.20, 0.985), (0.42, 0.54, 0.045), METAL, FIXTURES, 0.02)
for y in (6.15, 7.05):
    cylinder("Counter stool", (3.78, y, 0.45), 0.25, 0.10, OCHRE, FURNITURE, 24)
    cylinder("Counter stool leg", (3.78, y, 0.23), 0.055, 0.44, DARK, FURNITURE, 16)

# Bedrooms: beds, desks, storage.
rug("NW bedroom rug", 1.95, 10.62, 2.45, 2.80, RUG_WARM)
bed("NW queen bed", 1.75, 10.72, 1.55, 2.05, 0, BLUE)
cabinet("NW bedside", 2.82, 11.18, 0.48, 0.44, 0.48, WOOD)
table("NW desk", 2.55, 9.15, 1.25, 0.55, 0.72, 0, WOOD)
chair("NW desk chair", 2.55, 9.83, math.pi, OCHRE)

futon("7.1 jo floor futon", 6.10, 1.50, 1.42, 2.08, 0, GREEN)
table("7.1 jo low table", 6.15, 3.25, 1.05, 0.55, 0.36, 0, WOOD)
cabinet("7.1 jo wardrobe", 4.98, 2.55, 0.38, 1.28, 1.70, CABINET)
plant("7.1 jo plant", 6.98, 3.75, 0.52)

# The far 6.4-jo room is a child's room: single bed, study desk, toy storage,
# and a bright play rug. Its floor area remains smaller than the adjacent 7.1-jo room.
rug("Kids play rug", 8.65, 2.18, 1.55, 2.70, RUG_WARM)
bed("Kids single bed", 9.05, 1.45, 1.02, 2.02, 0, OCHRE)
table("Kids study desk", 8.35, 3.48, 1.18, 0.52, 0.70, 0, WOOD)
chair("Kids study chair", 8.35, 4.02, math.pi, BLUE)
cabinet("Kids toy storage", 9.60, 3.48, 0.34, 1.25, 0.78, OCHRE)
for i, cm in enumerate((BLUE, GREEN, PINK)):
    box("Kids storage bin " + str(i + 1), (9.42, 3.12 + i * 0.36, 0.50), (0.14, 0.27, 0.22), cm, DECOR, 0.035)

# The upper-right 6-jo room is a dedicated home office near the entrance.
rug("Office rug", 8.30, 10.62, 2.05, 2.55, RUG_BLUE)
table("Office main desk", 8.28, 11.92, 1.86, 0.68, 0.74, 0, WOOD)
chair("Office task chair placeholder", 8.28, 11.05, math.pi, DARK)
for i, x in enumerate((7.90, 8.66)):
    box("Office monitor " + str(i + 1), (x, 11.67, 1.34), (0.66, 0.07, 0.40), DARK, FURNITURE, 0.035)
    box("Office monitor stand " + str(i + 1), (x, 11.72, 1.05), (0.07, 0.07, 0.35), METAL, FURNITURE, 0.015)
cabinet("Office shelving", 9.63, 10.60, 0.42, 1.60, 1.75, WOOD_DARK)
cabinet("Office printer cabinet", 7.10, 9.35, 0.48, 1.05, 0.78, CABINET)
box("Office printer", (7.10, 9.35, 0.90), (0.42, 0.62, 0.20), PORCELAIN, FURNITURE, 0.055)
plant("Office plant", 7.10, 12.15, 0.65)

# Walk-in closet and hallway storage.
cabinet("WIC left storage", 3.82, 11.35, 0.35, 2.55, 1.95, CABINET)
cabinet("WIC right storage", 4.98, 11.35, 0.35, 2.55, 1.95, CABINET)
cabinet("Hall storage", 5.52, 9.02, 0.42, 1.10, 1.85, CABINET)

# Wet areas and sanitary fixtures.
cabinet("Vanity", 7.45, 7.92, 1.10, 0.52, 0.82, CABINET)
box("Vanity basin", (7.45, 7.92, 0.91), (0.65, 0.36, 0.14), PORCELAIN, FIXTURES, 0.07)
box("Vanity mirror", (7.45, 8.25, 1.63), (1.00, 0.045, 0.95), GLASS, FIXTURES, 0.025)
cylinder("Washer", (9.25, 7.65, 0.45), 0.39, 0.82, PORCELAIN, FIXTURES, 32)
cylinder("Washer door", (9.25, 7.22, 0.46), 0.24, 0.06, DARK, FIXTURES, 32)
box("Bathtub", (8.70, 5.36, 1.00), (2.00, 0.86, 0.72), PORCELAIN, FIXTURES, 0.16)
box("Bathtub inner", (8.70, 5.36, 1.22), (1.62, 0.56, 0.34), GLASS, FIXTURES, 0.16)
box("Shower screen", (7.57, 5.36, 1.26), (0.04, 0.92, 1.65), GLASS, FIXTURES, 0.02)
toilet("Main toilet", 5.95, 5.60, 0)

# Entry bench, console and balcony plants.
cabinet("Entry shoe cabinet", 6.38, 12.18, 0.42, 1.05, 1.05, WOOD)
box("Entry bench", (5.75, 11.73, 0.42), (0.95, 0.42, 0.42), BLUE, FURNITURE, 0.08)
for i, (x, y, s) in enumerate(((-0.62, 1.0, 0.55), (-0.62, 7.45, 0.70), (1.35, -0.60, 0.68), (4.45, -0.60, 0.55), (8.85, -0.60, 0.72), (1.05, 13.53, 0.62), (4.25, 13.53, 0.55))):
    plant("Balcony plant " + str(i + 1), x, y, s)

# Room labels are separate and can be hidden in Blender if a cleaner render is preferred.
add_label("LDK 23 jo", 1.20, 1.05, 0.36)
add_label("Bedroom 6.7 jo", 1.75, 12.45, 0.27)
add_label("WIC", 4.40, 9.95, 0.28)
add_label("Home Office 6 jo", 8.35, 12.55, 0.25)
add_label("Washroom", 8.20, 6.90, 0.25)
add_label("Bath", 8.25, 4.92, 0.25)
add_label("Bedroom 7.1 jo / Futon", 6.10, 0.48, 0.20)
add_label("Kids Room 6.4 jo", 8.72, 0.48, 0.21)

# Lighting and camera for an architectural dollhouse render.
world = bpy.context.scene.world or bpy.data.worlds.new("World")
bpy.context.scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.055, 0.070, 0.090, 1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.48

for name, loc, energy, size in (
    ("Key softbox", (-3.5, -2.5, 15.0), 1850, 8.0),
    ("Fill softbox", (13.5, 11.0, 11.0), 1450, 7.0),
    ("North softbox", (3.0, 18.0, 9.0), 900, 6.0),
):
    data = bpy.data.lights.new(name, "AREA")
    data.energy = energy
    data.shape = "DISK"
    data.size = size
    obj = bpy.data.objects.new(name, data)
    obj.location = loc
    LIGHTS.objects.link(obj)
    target = Vector((4.5, 6.2, 0.0))
    obj.rotation_euler = (target - obj.location).to_track_quat("-Z", "Y").to_euler()

cam_data = bpy.data.cameras.new("Architectural Camera")
cam = bpy.data.objects.new("Architectural Camera", cam_data)
bpy.context.scene.collection.objects.link(cam)
cam.location = (16.8, -18.2, 22.5)
target = Vector((4.45, 6.25, 0.25))
cam.rotation_euler = (target - cam.location).to_track_quat("-Z", "Y").to_euler()
cam_data.type = "ORTHO"
cam_data.ortho_scale = 18.5
bpy.context.scene.camera = cam

scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 1400
scene.render.resolution_y = 1200
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGBA"
scene.render.film_transparent = False
scene.render.filepath = RENDER_PATH
scene.render.image_settings.color_depth = "8"
scene.render.resolution_percentage = 100
scene.render.film_transparent = False
scene.view_settings.look = "AgX - Medium High Contrast"

# Color-managed neutral ground improves the silhouette of the balcony edges.
GROUND = mat("Backdrop", (0.035, 0.045, 0.058), 0.92)
box("Backdrop", (4.5, 6.4, -0.16), (18.0, 19.0, 0.20), GROUND, ARCH, 0.18)

# Store modeling assumptions in the file itself.
scene["source_plan"] = "CleanShot 2026-07-11 at 08.26.54@2x.png"
scene["scale_note"] = "Approximate 10m x 13m footprint inferred from Japanese jo room areas; verify with measured dimensions before construction use."
scene["ceiling_height_m"] = 2.55
scene["model_purpose"] = "Conceptual furnished 3D floor-plan visualization"

bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)
bpy.ops.render.render(write_still=True)

# A true plan-view render is useful for checking furniture orientation and
# partition placement against the supplied 2D drawing.
iso_location = cam.location.copy()
iso_rotation = cam.rotation_euler.copy()
iso_scale = cam_data.ortho_scale
iso_resolution = (scene.render.resolution_x, scene.render.resolution_y)
cam.location = (4.45, 6.35, 24.0)
cam.rotation_euler = (0.0, 0.0, 0.0)
cam_data.ortho_scale = 16.4
scene.render.resolution_x = 1200
scene.render.resolution_y = 1400
scene.render.filepath = TOP_RENDER_PATH
bpy.ops.render.render(write_still=True)
cam.location = iso_location
cam.rotation_euler = iso_rotation
cam_data.ortho_scale = iso_scale
scene.render.resolution_x, scene.render.resolution_y = iso_resolution
scene.render.filepath = RENDER_PATH

# Also export a portable GLB for web / quick-look use.
bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)
bpy.ops.export_scene.gltf(filepath=GLB_PATH, export_format="GLB", export_apply=True, export_cameras=False, export_lights=False)
print("BLEND:", BLEND_PATH)
print("RENDER:", RENDER_PATH)
print("TOP RENDER:", TOP_RENDER_PATH)
print("GLB:", GLB_PATH)
