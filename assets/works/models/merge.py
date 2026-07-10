import copy
import math
import pygltflib

SRC = "extracted/Models/GLB format"


def load_glb(name):
    return pygltflib.GLTF2().load(f"{SRC}/{name}.glb")


def merge_into(main, blob_holder, part, translation=(0, 0, 0), rotation_y_deg=0.0, scale=1.0, name=None):
    blob = part.binary_blob()
    offset = len(blob_holder[0])
    pad = (-offset) % 4
    if pad:
        blob_holder[0] += b"\x00" * pad
        offset = len(blob_holder[0])
    blob_holder[0] += blob

    accessor_offset = len(main.accessors)
    bufferview_offset = len(main.bufferViews)
    material_offset = len(main.materials)
    texture_offset = len(main.textures)
    image_offset = len(main.images)
    sampler_offset = len(main.samplers)
    mesh_offset = len(main.meshes)
    node_offset = len(main.nodes)

    for bv in part.bufferViews:
        nbv = copy.deepcopy(bv)
        nbv.buffer = 0
        nbv.byteOffset = (nbv.byteOffset or 0) + offset
        main.bufferViews.append(nbv)

    for acc in part.accessors:
        nacc = copy.deepcopy(acc)
        if nacc.bufferView is not None:
            nacc.bufferView += bufferview_offset
        main.accessors.append(nacc)

    for img in part.images:
        nimg = copy.deepcopy(img)
        if nimg.bufferView is not None:
            nimg.bufferView += bufferview_offset
        main.images.append(nimg)

    for smp in part.samplers:
        main.samplers.append(copy.deepcopy(smp))

    for tex in part.textures:
        ntex = copy.deepcopy(tex)
        if ntex.source is not None:
            ntex.source += image_offset
        if ntex.sampler is not None:
            ntex.sampler += sampler_offset
        main.textures.append(ntex)

    for mat in part.materials:
        nmat = copy.deepcopy(mat)
        if nmat.pbrMetallicRoughness:
            if nmat.pbrMetallicRoughness.baseColorTexture:
                nmat.pbrMetallicRoughness.baseColorTexture.index += texture_offset
            if nmat.pbrMetallicRoughness.metallicRoughnessTexture:
                nmat.pbrMetallicRoughness.metallicRoughnessTexture.index += texture_offset
        if nmat.normalTexture:
            nmat.normalTexture.index += texture_offset
        if nmat.occlusionTexture:
            nmat.occlusionTexture.index += texture_offset
        if nmat.emissiveTexture:
            nmat.emissiveTexture.index += texture_offset
        main.materials.append(nmat)

    for mesh in part.meshes:
        nmesh = copy.deepcopy(mesh)
        for prim in nmesh.primitives:
            if prim.indices is not None:
                prim.indices += accessor_offset
            if prim.material is not None:
                prim.material += material_offset
            attrs = prim.attributes
            for key in ["POSITION", "NORMAL", "TANGENT", "TEXCOORD_0", "TEXCOORD_1", "COLOR_0", "JOINTS_0", "WEIGHTS_0"]:
                val = getattr(attrs, key, None)
                if val is not None:
                    setattr(attrs, key, val + accessor_offset)
        main.meshes.append(nmesh)

    for nd in part.nodes:
        nnd = copy.deepcopy(nd)
        if nnd.mesh is not None:
            nnd.mesh += mesh_offset
        if nnd.children:
            nnd.children = [c + node_offset for c in nnd.children]
        main.nodes.append(nnd)

    part_scene = part.scenes[part.scene or 0]
    root_indices = [r + node_offset for r in part_scene.nodes]

    rad = math.radians(rotation_y_deg)
    qy = [0, math.sin(rad / 2), 0, math.cos(rad / 2)]

    wrapper = pygltflib.Node(
        name=name,
        translation=list(translation),
        rotation=qy,
        scale=[scale, scale, scale],
        children=root_indices,
    )
    main.nodes.append(wrapper)
    return len(main.nodes) - 1


def main():
    main_doc = pygltflib.GLTF2()
    main_doc.asset = pygltflib.Asset(generator="ai-komon2 works-3d merge script", version="2.0")
    main_doc.scenes = [pygltflib.Scene(nodes=[])]
    main_doc.scene = 0
    blob_holder = [b""]

    house = load_glb("building-type-p")
    tree_large = load_glb("tree-large")
    tree_small = load_glb("tree-small")
    planter = load_glb("planter")
    path_stones = load_glb("path-stones-short")

    wrappers = []
    wrappers.append(merge_into(main_doc, blob_holder, house, translation=(0, 0, 0), rotation_y_deg=0, name="house"))
    wrappers.append(merge_into(main_doc, blob_holder, tree_large, translation=(-1.05, 0, 0.78), rotation_y_deg=15, scale=1.15, name="tree1"))
    wrappers.append(merge_into(main_doc, blob_holder, tree_large, translation=(-0.95, 0, -0.85), rotation_y_deg=200, scale=0.9, name="tree2"))
    wrappers.append(merge_into(main_doc, blob_holder, tree_small, translation=(1.0, 0, -0.82), rotation_y_deg=70, scale=1.0, name="tree3"))
    wrappers.append(merge_into(main_doc, blob_holder, planter, translation=(0.42, 0, 0.56), rotation_y_deg=0, scale=1.0, name="planter1"))
    # short garden path leading away from the entrance/planter
    wrappers.append(merge_into(main_doc, blob_holder, path_stones, translation=(0.42, 0, 0.88), rotation_y_deg=0, scale=1.0, name="path1"))
    wrappers.append(merge_into(main_doc, blob_holder, path_stones, translation=(0.42, 0, 1.22), rotation_y_deg=5, scale=1.0, name="path2"))

    # global scale-up root so the diorama reads at a comfortable real-world-ish size
    root = pygltflib.Node(name="sceneRoot", scale=[3.2, 3.2, 3.2], children=wrappers)
    main_doc.nodes.append(root)
    root_index = len(main_doc.nodes) - 1
    main_doc.scenes[0].nodes = [root_index]

    # All source parts reference the same external "Textures/colormap.png" via a
    # relative URI (not embedded). Embed it once as a bufferView-backed image and
    # repoint every texture at it, so the merged .glb is fully self-contained.
    with open(f"{SRC}/Textures/colormap.png", "rb") as f:
        colormap_bytes = f.read()
    offset = len(blob_holder[0])
    pad = (-offset) % 4
    if pad:
        blob_holder[0] += b"\x00" * pad
        offset = len(blob_holder[0])
    blob_holder[0] += colormap_bytes
    colormap_bv_index = len(main_doc.bufferViews)
    main_doc.bufferViews.append(
        pygltflib.BufferView(buffer=0, byteOffset=offset, byteLength=len(colormap_bytes))
    )
    main_doc.images = [
        pygltflib.Image(name="colormap", mimeType="image/png", bufferView=colormap_bv_index, uri=None)
    ]
    for tex in main_doc.textures:
        tex.source = 0

    main_doc.buffers = [pygltflib.Buffer(byteLength=len(blob_holder[0]))]
    main_doc.set_binary_blob(blob_holder[0])

    out_path = "house-diorama.glb"
    main_doc.save(out_path)
    print("saved", out_path)


if __name__ == "__main__":
    main()
