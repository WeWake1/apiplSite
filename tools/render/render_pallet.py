"""Studio renders (+ optional web 3D model) of one pallet from tools/render/recipes.json.

Geometry comes from pallets.py: every board and block is placed exactly where the
official drawing (EPAL / CP) or the reference range puts it. The only edge treatments are
the ones the drawings call for:
  * 45 deg vertical corner chamfers, cut through every component that reaches the corner
  * EPAL "chamfered lower edge boards": upper outer edge, only between the blocks,
    with curved run-outs (disc cutter profile)
  * GMA stringer notches with rounded corners
No other bevels, no random jitter.

Run (one pallet per Blender process):
  Blender --background --factory-startup --python tools/render/render_pallet.py -- \
      --recipe cp3 --name cp3-type-pallet-1140x1140 --out out/ [--brand tools/render/brand.json]
      [--views 1,2,3,4,5] [--res 1600] [--samples 128] [--glb public/models/x.glb]
"""
import argparse
import json
import math
import os
import random
import sys

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
MM = 0.001

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
ap = argparse.ArgumentParser()
ap.add_argument("--recipe", required=True)
ap.add_argument("--name", help="output base name (defaults to recipe id)")
ap.add_argument("--recipes", default=os.path.join(HERE, "recipes.json"))
ap.add_argument("--brand", default=os.path.join(HERE, "brand.json"))
ap.add_argument("--out", default=os.path.join(HERE, "out"))
ap.add_argument("--views", default="1,2,3,4,5")
ap.add_argument("--res", type=int, default=1600)
ap.add_argument("--samples", type=int, default=128)
ap.add_argument("--textures", default=os.path.join(HERE, "textures"))
ap.add_argument("--glb", default="", help="also export a web GLB model to this path")
ap.add_argument("--blend", action="store_true")
ap.add_argument("--detail-index", type=int, default=0, help="view 9: which marking to frame (0 = first)")
args = ap.parse_args(argv)

RECIPES = json.load(open(args.recipes))
R = RECIPES[args.recipe]
BRAND = json.load(open(args.brand))
NAME = args.name or args.recipe
random.seed(sum(ord(c) for c in NAME))

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene


def srgb(hexstr):
    h = hexstr.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(((x + 0.055) / 1.055) ** 2.4 if x > 0.04045 else x / 12.92 for x in c)


def out_of_type(node, kind):
    return next(o for o in node.outputs if o.type == kind)


# ================================================================ materials (Cycles)
WOODS = {
    "pine": dict(tex="Wood096", grain="v", tile=0.95, sat=1.75, hue=(0.503, 0.511), val=(1.02, 1.12),
                 contrast=-0.25, rough=(0.55, 0.85), knot=(0.22, 0.42), knot_tone="#C99E68"),
    "hard": dict(tex="Wood060", grain="u", tile=0.8, sat=1.0, hue=(0.497, 0.505), val=(0.92, 1.08),
                 contrast=-0.05, rough=(0.6, 0.9), knot=(0.03, 0.08), knot_tone="#5A3A26"),
}


def wood_material(name, kind="pine", tint=1.0):
    spec = WOODS[kind]
    prefix = os.path.join(args.textures, spec["tex"], spec["tex"] + "_2K-JPG_")
    tile = spec["tile"]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    n, l = m.node_tree.nodes, m.node_tree.links
    n.clear()
    out = n.new("ShaderNodeOutputMaterial")
    bsdf = n.new("ShaderNodeBsdfPrincipled")
    l.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    tc = n.new("ShaderNodeTexCoord")
    oi = n.new("ShaderNodeObjectInfo")
    sep = n.new("ShaderNodeSeparateXYZ")
    l.new(tc.outputs["Object"], sep.inputs[0])
    nsep = n.new("ShaderNodeSeparateXYZ")
    l.new(tc.outputs["Normal"], nsep.inputs[0])
    r2m = n.new("ShaderNodeMath"); r2m.operation = "MULTIPLY"
    l.new(oi.outputs["Random"], r2m.inputs[0]); r2m.inputs[1].default_value = 17.31
    r2 = n.new("ShaderNodeMath"); r2.operation = "FRACT"
    l.new(r2m.outputs[0], r2.inputs[0])

    def uv(across, along):
        ua = n.new("ShaderNodeMath"); ua.operation = "MULTIPLY_ADD"
        l.new(across, ua.inputs[0]); ua.inputs[1].default_value = 1.0 / tile
        l.new(oi.outputs["Random"], ua.inputs[2])
        vb = n.new("ShaderNodeMath"); vb.operation = "MULTIPLY_ADD"
        l.new(along, vb.inputs[0]); vb.inputs[1].default_value = 1.0 / tile
        l.new(r2.outputs[0], vb.inputs[2])
        cmb = n.new("ShaderNodeCombineXYZ")
        if spec["grain"] == "v":
            l.new(ua.outputs[0], cmb.inputs[0]); l.new(vb.outputs[0], cmb.inputs[1])
        else:
            l.new(vb.outputs[0], cmb.inputs[0]); l.new(ua.outputs[0], cmb.inputs[1])
        return cmb.outputs[0]

    uv_top = uv(sep.outputs["Y"], sep.outputs["X"])
    uv_side = uv(sep.outputs["Z"], sep.outputs["X"])
    absz = n.new("ShaderNodeMath"); absz.operation = "ABSOLUTE"
    l.new(nsep.outputs["Z"], absz.inputs[0])
    absx = n.new("ShaderNodeMath"); absx.operation = "ABSOLUTE"
    l.new(nsep.outputs["X"], absx.inputs[0])
    is_top = n.new("ShaderNodeMath"); is_top.operation = "GREATER_THAN"
    l.new(absz.outputs[0], is_top.inputs[0]); is_top.inputs[1].default_value = 0.5
    is_end = n.new("ShaderNodeMath"); is_end.operation = "GREATER_THAN"
    l.new(absx.outputs[0], is_end.inputs[0]); is_end.inputs[1].default_value = 0.6
    uvmix = n.new("ShaderNodeMix"); uvmix.data_type = "VECTOR"
    l.new(is_top.outputs[0], uvmix.inputs["Factor"])
    l.new(uv_side, uvmix.inputs[4]); l.new(uv_top, uvmix.inputs[5])

    def img(kind_, colorspace):
        t = n.new("ShaderNodeTexImage")
        t.image = bpy.data.images.load(prefix + kind_ + ".jpg", check_existing=True)
        t.image.colorspace_settings.name = colorspace
        t.interpolation = "Cubic"
        l.new(out_of_type(uvmix, "VECTOR"), t.inputs["Vector"])
        return t

    col = img("Color", "sRGB")
    rough = img("Roughness", "Non-Color")
    disp = img("Displacement", "Non-Color")
    soft = n.new("ShaderNodeBrightContrast")
    soft.inputs["Contrast"].default_value = spec["contrast"]
    soft.inputs["Bright"].default_value = 0.02
    l.new(col.outputs["Color"], soft.inputs["Color"])
    hsv = n.new("ShaderNodeHueSaturation")
    hsv.inputs["Saturation"].default_value = spec["sat"]
    hmap = n.new("ShaderNodeMapRange")
    hmap.inputs["To Min"].default_value, hmap.inputs["To Max"].default_value = spec["hue"]
    l.new(oi.outputs["Random"], hmap.inputs["Value"])
    l.new(hmap.outputs[0], hsv.inputs["Hue"])
    vmap = n.new("ShaderNodeMapRange")
    vmap.inputs["To Min"].default_value = spec["val"][0] * tint
    vmap.inputs["To Max"].default_value = spec["val"][1] * tint
    l.new(r2.outputs[0], vmap.inputs["Value"])
    l.new(vmap.outputs[0], hsv.inputs["Value"])
    l.new(soft.outputs["Color"], hsv.inputs["Color"])
    lum = n.new("ShaderNodeRGBToBW")
    l.new(col.outputs["Color"], lum.inputs["Color"])
    kmask = n.new("ShaderNodeMapRange")
    kmask.inputs["From Min"].default_value, kmask.inputs["From Max"].default_value = spec["knot"]
    kmask.inputs["To Min"].default_value, kmask.inputs["To Max"].default_value = 0.7, 0.0
    l.new(lum.outputs["Val"], kmask.inputs["Value"])
    deknot = n.new("ShaderNodeMix"); deknot.data_type = "RGBA"
    l.new(kmask.outputs[0], deknot.inputs["Factor"])
    l.new(hsv.outputs["Color"], deknot.inputs[6])
    deknot.inputs[7].default_value = (*srgb(spec["knot_tone"]), 1)
    base = out_of_type(deknot, "RGBA")
    endc = n.new("ShaderNodeVectorMath"); endc.operation = "ADD"
    l.new(tc.outputs["Object"], endc.inputs[0]); endc.inputs[1].default_value = (0, 0.11, 0.07)
    ring = n.new("ShaderNodeTexWave"); ring.wave_type = "RINGS"; ring.rings_direction = "X"
    ring.inputs["Scale"].default_value = 70
    ring.inputs["Distortion"].default_value = 2.0
    l.new(endc.outputs[0], ring.inputs["Vector"])
    rr = n.new("ShaderNodeValToRGB")
    rr.color_ramp.elements[0].color = (0.78, 0.66, 0.52, 1)
    rr.color_ramp.elements[1].color = (0.92, 0.86, 0.78, 1)
    l.new(ring.outputs["Fac"], rr.inputs["Fac"])
    ring_col = n.new("ShaderNodeMix"); ring_col.data_type = "RGBA"; ring_col.blend_type = "MULTIPLY"
    ring_col.inputs["Factor"].default_value = 1.0
    l.new(base, ring_col.inputs[6]); l.new(rr.outputs["Color"], ring_col.inputs[7])
    final = n.new("ShaderNodeMix"); final.data_type = "RGBA"
    l.new(is_end.outputs[0], final.inputs["Factor"])
    l.new(base, final.inputs[6])
    l.new(out_of_type(ring_col, "RGBA"), final.inputs[7])
    l.new(out_of_type(final, "RGBA"), bsdf.inputs["Base Color"])
    rmap = n.new("ShaderNodeMapRange")
    rmap.inputs["To Min"].default_value, rmap.inputs["To Max"].default_value = spec["rough"]
    l.new(rough.outputs["Color"], rmap.inputs["Value"])
    l.new(rmap.outputs[0], bsdf.inputs["Roughness"])
    bsdf.inputs["Specular IOR Level"].default_value = 0.3
    bump = n.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.25
    bump.inputs["Distance"].default_value = 0.0005
    l.new(disp.outputs["Color"], bump.inputs["Height"])
    l.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return m


def plain_material(name, hexcol, metallic=0.0, roughness=0.5):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*srgb(hexcol), 1)
    b.inputs["Metallic"].default_value = metallic
    b.inputs["Roughness"].default_value = roughness
    return m


def stamp_material(name, path):
    """Burnt-in / printed marking decal: PNG alpha (x wear noise) drives a dark ink."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    n, l = m.node_tree.nodes, m.node_tree.links
    b = n["Principled BSDF"]
    t = n.new("ShaderNodeTexImage")
    t.image = bpy.data.images.load(path, check_existing=True)
    t.interpolation = "Cubic"
    l.new(t.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.88
    noise = n.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 260.0
    noise.inputs["Detail"].default_value = 4.0
    ramp = n.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.30
    ramp.color_ramp.elements[0].color = (0.55, 0.55, 0.55, 1)
    ramp.color_ramp.elements[1].position = 0.62
    l.new(noise.outputs["Fac"], ramp.inputs["Fac"])
    mul = n.new("ShaderNodeMath"); mul.operation = "MULTIPLY"
    l.new(t.outputs["Alpha"], mul.inputs[0])
    l.new(out_of_type(ramp, "RGBA"), mul.inputs[1])
    mul2 = n.new("ShaderNodeMath"); mul2.operation = "MULTIPLY"
    l.new(mul.outputs[0], mul2.inputs[0]); mul2.inputs[1].default_value = 0.93
    l.new(mul2.outputs[0], b.inputs["Alpha"])
    return m


MATS = {
    "pine": wood_material("pine", "pine"),
    "hard": wood_material("hard", "hard"),
    "block": wood_material("block_pine", "pine", tint=0.96),
    "block_hard": wood_material("block_hard", "hard", tint=0.97),
}
NAIL = plain_material("nail", "#5E5E5A", metallic=0.8, roughness=0.45)
STEEL = plain_material("galvanised", "#B6BABD", metallic=1.0, roughness=0.32)

ROOT = bpy.data.objects.new("pallet", None)
scene.collection.objects.link(ROOT)
OBJECTS = []   # (object, kind) for every renderable pallet object


def link(ob, kind, parent=None):
    scene.collection.objects.link(ob)
    ob.parent = parent or ROOT
    OBJECTS.append((ob, kind))
    return ob


# ================================================================ geometry
def frame_of(p):
    """Local frame: local X = grain (length), local Y across, local Z up from z0."""
    x0, x1 = p["x"]; y0, y1 = p["y"]; z0, z1 = p["z"]
    if p["grain"] == "x":
        lx, ly, rot = x1 - x0, y1 - y0, 0.0
    else:
        lx, ly, rot = y1 - y0, x1 - x0, 90.0
    c = Vector(((x0 + x1) / 2, (y0 + y1) / 2, z0))
    M = Matrix.Translation(c * MM) @ Matrix.Rotation(math.radians(rot), 4, "Z")
    return lx, ly, z1 - z0, c, rot, M


def chamfer_profile(lx, openings_local, D, off=12.0, run=42.0):
    """Sampled (s, depth) along the board for the EPAL lower-edge-board chamfer.
    Full depth D between the run-outs; run-outs follow the arc of a disc cutter."""
    pts = {round(-lx / 2, 4): 0.0, round(lx / 2, 4): 0.0}
    for a, b in openings_local:
        s0, s3 = a + off, b - off
        run_ = run if s3 - s0 >= 2 * run + 10 else max(10.0, (s3 - s0 - 10) / 2)
        Rr = (run_ * run_ + D * D) / (2 * D)
        s1, s2 = s0 + run_, s3 - run_
        for k in range(15):
            u = run_ * (1 - k / 14)
            d = max(math.sqrt(max(Rr * Rr - u * u, 0)) - (Rr - D), 0.0)
            for s in (s1 - u, s2 + u):
                key = round(s, 4)
                pts[key] = max(pts.get(key, 0.0), d)
    return sorted(pts.items())


def mesh_box(bm, lx, ly, lz):
    vs = {}
    for sx in (-1, 1):
        for sy in (-1, 1):
            for sz in (0, 1):
                vs[(sx, sy, sz)] = bm.verts.new((sx * lx / 2 * MM, sy * ly / 2 * MM, sz * lz * MM))
    quads = [((-1, -1, 0), (-1, 1, 0), (1, 1, 0), (1, -1, 0)), ((-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1)),
             ((-1, -1, 0), (1, -1, 0), (1, -1, 1), (-1, -1, 1)), ((-1, 1, 0), (-1, 1, 1), (1, 1, 1), (1, 1, 0)),
             ((-1, -1, 0), (-1, -1, 1), (-1, 1, 1), (-1, 1, 0)), ((1, -1, 0), (1, 1, 0), (1, 1, 1), (1, -1, 1))]
    for q in quads:
        bm.faces.new([vs[k] for k in q])


def mesh_chamfer_board(bm, lx, ly, lz, sgn, profile):
    """Board along local X whose upper edge on side sgn*Y is chamfered by depth d(s)."""
    secs = []
    w2 = ly / 2
    for s, d in profile:
        d = max(d, 0.05)
        ring = [(-w2, 0.0), (w2, 0.0), (w2, lz - d), (w2 - d, lz), (-w2, lz)]
        if sgn < 0:
            ring = [(-y, z) for y, z in ring][::-1]
        secs.append([bm.verts.new((s * MM, y * MM, z * MM)) for y, z in ring])
    k = len(secs[0])
    for i in range(len(secs) - 1):
        a, b = secs[i], secs[i + 1]
        for j in range(k):
            bm.faces.new([a[j], a[(j + 1) % k], b[(j + 1) % k], b[j]])
    bm.faces.new(secs[0][::-1])
    bm.faces.new(secs[-1])


def mesh_notched(bm, lx, ly, lz, notches_local):
    """Stringer along local X with notches cut from the underside (rounded top corners)."""
    prof = [(-lx / 2, 0.0)]
    for c, length, depth, r in sorted(notches_local):
        xl, xr = c - length / 2, c + length / 2
        prof.append((xl, 0.0))
        if depth - r > 0.5:
            prof.append((xl, depth - r))
        for k in range(1, 9):
            a = math.pi - k * (math.pi / 2) / 8
            prof.append((xl + r + r * math.cos(a), depth - r + r * math.sin(a)))
        for k in range(0, 8):
            a = math.pi / 2 - k * (math.pi / 2) / 8
            prof.append((xr - r + r * math.cos(a), depth - r + r * math.sin(a)))
        if depth - r > 0.5:
            prof.append((xr, depth - r))
        prof.append((xr, 0.0))
    prof += [(lx / 2, 0.0), (lx / 2, lz), (-lx / 2, lz)]
    front = [bm.verts.new((x * MM, -ly / 2 * MM, z * MM)) for x, z in prof]
    back = [bm.verts.new((x * MM, ly / 2 * MM, z * MM)) for x, z in prof]
    bm.faces.new(front)
    bm.faces.new(back[::-1])
    k = len(prof)
    for i in range(k):
        j = (i + 1) % k
        bm.faces.new([front[i], back[i], back[j], front[j]])


def corner_planes(p, recipe):
    """World cut planes (point, normal) of every corner chamfer that reaches this part."""
    planes = []
    for reg in recipe["corners"]:
        if p["z"][0] < reg["z"][0] - 0.01 or p["z"][1] > reg["z"][1] + 0.01:
            continue
        c = reg["c"]
        for sx in (-1, 1):
            for sy in (-1, 1):
                X = reg["x"][1] if sx > 0 else reg["x"][0]
                Y = reg["y"][1] if sy > 0 else reg["y"][0]
                nrm = Vector((sx, sy, 0)).normalized()
                pt = Vector((X - sx * c, Y, 0))
                reach = max(nrm.dot(Vector((x, y, 0)) - pt) for x in p["x"] for y in p["y"])
                if reach > 0.01:
                    planes.append((pt, nrm))
    return planes


def build_part(p, recipe, z_offset=0.0):
    lx, ly, lz, c, rot, M = frame_of(p)
    M = Matrix.Translation((0, 0, z_offset * MM)) @ M
    bm = bmesh.new()
    if "edge_chamfer" in p:
        ec = p["edge_chamfer"]
        if p["grain"] == "x":
            sgn = 1 if ec["side"] == "+y" else -1
            ops = [[a - c.x, b - c.x] for a, b in ec["openings"]]
        else:
            sgn = -1 if ec["side"] == "+x" else 1
            ops = [[a - c.y, b - c.y] for a, b in ec["openings"]]
        mesh_chamfer_board(bm, lx, ly, lz, sgn, chamfer_profile(lx, ops, ec["depth"]))
    elif "notches" in p:
        off = c.x if p["grain"] == "x" else c.y
        mesh_notched(bm, lx, ly, lz, [(nt["center"] - off, nt["length"], nt["depth"], nt["radius"]) for nt in p["notches"]])
    else:
        mesh_box(bm, lx, ly, lz)
    Minv = M.inverted()
    for pt, nrm in corner_planes(p, recipe):
        co = Minv @ ((pt + Vector((0, 0, z_offset))) * MM)
        no = (Minv.to_3x3() @ nrm).normalized()
        geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
        bmesh.ops.bisect_plane(bm, geom=geom, dist=1e-7, plane_co=co, plane_no=no, clear_outer=True)
        bnd = [e for e in bm.edges if e.is_boundary]
        if bnd:
            bmesh.ops.holes_fill(bm, edges=bnd, sides=0)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    big = [f for f in bm.faces if len(f.verts) > 4]
    if big:
        bmesh.ops.triangulate(bm, faces=big, quad_method="BEAUTY", ngon_method="EAR_CLIP")
    me = bpy.data.meshes.new(p["name"])
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(p["name"], me)
    ob.matrix_world = M
    hard = recipe["_wood"] == "hard"
    if p.get("wood") == "block":
        mat = MATS["block_hard"] if hard else MATS["block"]
    else:
        mat = MATS["hard"] if p.get("wood") == "hard" else MATS["pine"]
    ob.data.materials.append(mat)
    ob["grain_kind"] = "hard" if (p.get("wood") == "hard" or (p.get("wood") == "block" and hard)) else "pine"
    return link(ob, "wood")


def nail_head(x, y, z, down=False):
    me = bpy.data.meshes.get("nail_head")
    if me is None:
        bm = bmesh.new()
        bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=3.6 * MM, radius2=3.2 * MM, depth=0.7 * MM)
        me = bpy.data.meshes.new("nail_head")
        bm.to_mesh(me)
        bm.free()
        me.materials.append(NAIL)
    ob = bpy.data.objects.new("nail", me)
    ob.location = (x * MM, y * MM, (z + (-0.15 if down else 0.15)) * MM)
    if down:
        ob.rotation_euler.x = math.pi
    return link(ob, "nail")


def overlap(a, b):
    x0, x1 = max(a["x"][0], b["x"][0]), min(a["x"][1], b["x"][1])
    y0, y1 = max(a["y"][0], b["y"][0]), min(a["y"][1], b["y"][1])
    return (x0, x1, y0, y1) if x1 - x0 > 5 and y1 - y0 > 5 else None


def place_nails(parts, z_offset=0.0):
    """Nails where top deck boards cross the members below, and on the floor layer
    where it meets the member above (seen in the underside view)."""
    for p in parts:
        floor = p["role"] == "bottom" and p["z"][0] < 0.01
        if p["role"] != "top" and not floor:
            continue
        for q in parts:
            if q is p:
                continue
            touching = abs(q["z"][1] - p["z"][0]) < 0.01 if p["role"] == "top" else abs(q["z"][0] - p["z"][1]) < 0.01
            if not touching:
                continue
            ov = overlap(p, q)
            if not ov:
                continue
            x0, x1, y0, y1 = ov
            across = (y1 - y0) if p["grain"] == "x" else (x1 - x0)
            along = (x1 - x0) if p["grain"] == "x" else (y1 - y0)
            na = 3 if across >= 130 else 2 if across >= 85 else 1
            nl = 2 if along >= 120 else 1
            for i in range(na):
                fa = (i + 1) / (na + 1)
                for j in range(nl):
                    fl = (j + 1) / (nl + 1)
                    shift = 0.06 if (na > 1 and nl > 1 and i % 2) else 0.0
                    if p["grain"] == "x":
                        x, y = x0 + (fl + shift) * (x1 - x0), y0 + fa * (y1 - y0)
                    else:
                        x, y = x0 + fa * (x1 - x0), y0 + (fl + shift) * (y1 - y0)
                    if floor:
                        nail_head(x, y, z_offset, down=True)
                    else:
                        nail_head(x, y, p["z"][1] + z_offset)


# ================================================================ markings
STAMP_ASPECT = {"ippc": 340 / 150, "epal": 2.0, "epal2": 336 / 150, "epal3": 336 / 150, "cp": 2.0}
_stamp_mats = {}


def stamp_file(mark):
    if mark == "ippc":
        ip = BRAND["ippc"]
        return os.path.join(HERE, "stamps", f"ippc_{ip['country']}-{ip['code']}_{ip['treatment']}.png")
    return os.path.join(HERE, "stamps", f"{mark}.png")


def decal(mark, centre, normal, face_w, face_h):
    """Flat marking on a vertical face (centre in mm, world)."""
    if mark not in _stamp_mats:
        _stamp_mats[mark] = stamp_material("stamp_" + mark, stamp_file(mark))
    asp = STAMP_ASPECT["cp" if mark.startswith("cp") else mark]
    w = min(face_w * 0.80, face_h * 0.66 * asp)
    h = w / asp
    n = Vector(normal).normalized()
    up = Vector((0, 0, 1))
    right = up.cross(n).normalized()
    c = Vector(centre) + n * 0.35
    corners = [c - right * w / 2 - up * h / 2, c + right * w / 2 - up * h / 2,
               c + right * w / 2 + up * h / 2, c - right * w / 2 + up * h / 2]
    me = bpy.data.meshes.new("decal")
    me.from_pydata([tuple(v * MM) for v in corners], [], [(0, 1, 2, 3)])
    uvl = me.uv_layers.new(name="UVMap")
    for loop, uvv in zip(me.loops, [(0, 0), (1, 0), (1, 1), (0, 1)]):
        uvl.data[loop.index].uv = uvv
    me.materials.append(_stamp_mats[mark])
    return link(bpy.data.objects.new("decal_" + mark, me), "decal")


def marks_for(recipe):
    m = BRAND.get("marks", {})
    rid = recipe["id"]
    if rid in m:
        return m[rid]
    if rid.startswith("cp") and "cp*" in m:
        return {k: (f"cp{rid[2:]}" if v == "cp" else v) for k, v in m["cp*"].items()}
    return m.get("default", {"L": "ippc"})


def place_marks(recipe, z_offset=0.0, marks=None):
    marks = marks if marks is not None else marks_for(recipe)
    if not marks:
        return
    parts = recipe["parts"]
    axis = recipe.get("stamp_axis", "y")
    L, W = recipe["dims"][0], recipe["dims"][1]
    c_leg = max([reg["c"] for reg in recipe["corners"] if reg["z"][0] <= 30] or [0])
    blocks = [p for p in parts if p["role"] == "block"]
    stringers = [p for p in parts if p["role"] == "stringer"]
    for face in (-1, 1):
        if blocks:
            if axis == "y":
                edge = min(b["y"][0] for b in blocks) if face < 0 else max(b["y"][1] for b in blocks)
                row = [b for b in blocks if abs((b["y"][0] if face < 0 else b["y"][1]) - edge) < 0.5]
                row.sort(key=lambda b: b["x"][0] * (1 if face < 0 else -1))      # viewer's left -> right
            else:
                edge = min(b["x"][0] for b in blocks) if face < 0 else max(b["x"][1] for b in blocks)
                row = [b for b in blocks if abs((b["x"][0] if face < 0 else b["x"][1]) - edge) < 0.5]
                row.sort(key=lambda b: -b["y"][0] * (1 if face < 0 else -1))
            slots = {"L": row[0], "R": row[-1], "C": row[len(row) // 2]}
            for slot, mark in marks.items():
                b = slots.get(slot)
                if b is None:
                    continue
                if axis == "y":
                    a0, a1, lim = b["x"][0], b["x"][1], L / 2
                else:
                    a0, a1, lim = b["y"][0], b["y"][1], W / 2
                # a corner chamfer shortens the flat face of corner blocks
                at_edge = abs(edge) >= (W / 2 if axis == "y" else L / 2) - 0.5
                if at_edge and c_leg and a0 <= -lim + 0.5:
                    a0 += c_leg
                if at_edge and c_leg and a1 >= lim - 0.5:
                    a1 -= c_leg
                mid = (a0 + a1) / 2
                zc = (b["z"][0] + b["z"][1]) / 2 + z_offset
                centre = (mid, edge, zc) if axis == "y" else (edge, mid, zc)
                normal = (0, face, 0) if axis == "y" else (face, 0, 0)
                decal(mark, centre, normal, a1 - a0, b["z"][1] - b["z"][0])
        elif stringers:
            edge = min(s["x"][0] for s in stringers) if face < 0 else max(s["x"][1] for s in stringers)
            s = next(s for s in stringers if abs((s["x"][0] if face < 0 else s["x"][1]) - edge) < 0.5)
            ys = {"L": W / 2 - W / 6, "C": 0.0, "R": -W / 2 + W / 6}
            for slot, mark in marks.items():
                if slot not in ys:
                    continue
                y = ys[slot] * (1 if face < 0 else -1)
                for nt in s.get("notches", []):   # keep clear of notches
                    lo, hi = nt["center"] - nt["length"] / 2 - 10, nt["center"] + nt["length"] / 2 + 10
                    if lo < y < hi:
                        y = (hi + W / 2) / 2 if y > 0 else (lo - W / 2) / 2
                centre = (edge, y, (s["z"][0] + s["z"][1]) / 2 + z_offset)
                decal(mark, centre, (face, 0, 0), min(220, W / 3), s["z"][1] - s["z"][0])


# ================================================================ build
def prep(recipe):
    recipe["_wood"] = "hard" if any(p.get("wood") == "hard" for p in recipe["parts"]) else "pine"
    return recipe


def build_recipe(recipe, z_offset=0.0, marks=None):
    prep(recipe)
    for p in recipe["parts"]:
        build_part(p, recipe, z_offset)
    place_nails(recipe["parts"], z_offset)
    place_marks(recipe, z_offset, marks)


def hinge(x, y, sx, sy, z0, h):
    """Galvanised corner hinge: one leaf on each board face + knuckle at the corner."""
    leaf, t = 105.0, 2.0
    for along in ("x", "y"):
        bm = bmesh.new()
        if along == "x":
            cx, cy, wx, wy = x - sx * leaf / 2, y + sy * t / 2, leaf, t
        else:
            cx, cy, wx, wy = x + sx * t / 2, y - sy * leaf / 2, t, leaf
        mesh_box(bm, wx, wy, h)
        me = bpy.data.meshes.new("hinge")
        bm.to_mesh(me)
        bm.free()
        me.materials.append(STEEL)
        ob = bpy.data.objects.new("hinge", me)
        ob.location = (cx * MM, cy * MM, z0 * MM)
        link(ob, "steel")
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=12, radius1=5 * MM, radius2=5 * MM, depth=h * MM)
    me = bpy.data.meshes.new("knuckle")
    bm.to_mesh(me)
    bm.free()
    me.materials.append(STEEL)
    ob = bpy.data.objects.new("knuckle", me)
    ob.location = ((x + sx * 3) * MM, (y + sy * 3) * MM, (z0 + h / 2) * MM)
    link(ob, "steel")


def build_collar(stack=1, on_pallet=True):
    base_h = 0.0
    if on_pallet:
        base = RECIPES[R["meta"]["base"]]
        build_recipe(base, 0.0, marks=marks_for(base))
        base_h = base["dims"][2]
    H = R["dims"][2]
    prep(R)
    for k in range(stack):
        z = base_h + k * H
        for p in R["parts"]:
            build_part(p, R, z)
        for sx in (-1, 1):
            for sy in (-1, 1):
                hinge(sx * 600, sy * 400, sx, sy, z + 22, H - 44)
        decal("ippc", (-420, -400, z + H / 2), (0, -1, 0), 200, H * 0.55)
    return base_h + stack * H


def clear_pallet():
    for ob, _ in list(OBJECTS):
        bpy.data.objects.remove(ob, do_unlink=True)
    OBJECTS.clear()


# ================================================================ studio
bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 0, 0))
ground = bpy.context.active_object
ground.data.materials.append(plain_material("floor", "#F2F2F2", roughness=0.9))
ground.data.materials[0].node_tree.nodes["Principled BSDF"].inputs["Specular IOR Level"].default_value = 0.1
world = bpy.data.worlds.new("studio")
scene.world = world
world.use_nodes = True
wbg = world.node_tree.nodes["Background"]
wbg.inputs["Color"].default_value = (*srgb("#F4F4F4"), 1)
wbg.inputs["Strength"].default_value = 0.6


def area(name, loc, size, power, look_at=(0, 0, 0.07)):
    ld = bpy.data.lights.new(name, "AREA")
    ld.size = size
    ld.energy = power
    ob = bpy.data.objects.new(name, ld)
    scene.collection.objects.link(ob)
    ob.location = loc
    ob.rotation_euler = (Vector(look_at) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()


area("key", (-2.2, -2.6, 3.4), 3.5, 300)
area("fill", (3.0, -1.6, 1.8), 3.0, 66)
area("rim", (0.8, 3.2, 2.4), 2.5, 105)
cam_data = bpy.data.cameras.new("cam")
cam_data.lens = 75
cam_data.sensor_width = 36
cam = bpy.data.objects.new("cam", cam_data)
scene.collection.objects.link(cam)
scene.camera = cam
RES_X, RES_Y = args.res, args.res * 3 // 4
scene.render.resolution_x, scene.render.resolution_y = RES_X, RES_Y
CAM_AZ = -38.0


def frame(local_corners, elev, margin):
    bpy.context.view_layer.update()
    corners = [ROOT.matrix_world @ c for c in local_corners]
    centre = sum(corners, Vector()) / len(corners)
    az, el = math.radians(CAM_AZ), math.radians(elev)
    direction = Vector((math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el)))
    half_w = (cam_data.sensor_width / 2) / cam_data.lens
    half_h = half_w * RES_Y / RES_X
    cam_data.shift_x = cam_data.shift_y = 0

    def project(dist):
        cam.location = centre + direction * dist
        cam.rotation_euler = (-direction).to_track_quat("-Z", "Y").to_euler()
        bpy.context.view_layer.update()
        inv = cam.matrix_world.inverted()
        pts = [(p.x / -p.z, p.y / -p.z) for p in (inv @ c for c in corners)]
        return [p[0] for p in pts], [p[1] for p in pts]

    lo, hi = 0.3, 40.0
    for _ in range(60):
        mid = (lo + hi) / 2
        xs, ys = project(mid)
        if (max(xs) - min(xs)) <= 2 * half_w * margin and (max(ys) - min(ys)) <= 2 * half_h * margin:
            hi = mid
        else:
            lo = mid
    xs, ys = project(hi)
    cam_data.shift_x = ((max(xs) + min(xs)) / 2) / (2 * half_w)
    cam_data.shift_y = ((max(ys) + min(ys)) / 2) / (2 * half_w)


VIEWS = {
    1: dict(rot=0, el=27, margin=0.80),
    2: dict(rot=-76, el=27, margin=0.80),
    3: dict(rot=24, el=6, margin=0.86),
    4: dict(rot=-8, el=62, margin=0.78),
    5: dict(rot=0, el=30, margin=0.80, flip=True),
    9: dict(el=9, margin=0.92, detail=True),   # close-up of the first marking; only when asked for (--views 9)
}
COLLAR_VIEWS = {
    1: dict(rot=0, el=27, margin=0.78, stack=1, pallet=True),
    2: dict(rot=-76, el=24, margin=0.78, stack=3, pallet=True),
    3: dict(rot=0, el=27, margin=0.78, stack=1, pallet=False),
    4: dict(rot=-8, el=58, margin=0.78, stack=1, pallet=True),
}

scene.render.engine = "CYCLES"
cy = scene.cycles
prefs = bpy.context.preferences.addons["cycles"].preferences
prefs.compute_device_type = "METAL"
prefs.refresh_devices()
for d in prefs.devices:
    d.use = d.type == "METAL"   # GPU only; adding the CPU slows Metal down a lot
cy.device = "GPU"
cy.use_denoising = True
cy.max_bounces = 8
scene.render.film_transparent = False
scene.view_settings.view_transform = "Standard"
scene.render.image_settings.file_format = "OPEN_EXR"
scene.render.image_settings.color_depth = "32"


def render_linear(path, samples, scale=1.0):
    cy.samples = samples
    scene.render.resolution_percentage = int(scale * 100)
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
    img = bpy.data.images.load(path)
    a = np.array(img.pixels[:], dtype=np.float32).reshape(img.size[1], img.size[0], 4)[..., :3]
    bpy.data.images.remove(img)
    os.remove(path)
    scene.render.resolution_percentage = 100
    return a


def upsample(a, h, w):
    h0, w0 = a.shape[:2]
    yi = np.linspace(0, h0 - 1, h)
    xi = np.linspace(0, w0 - 1, w)
    tmp = np.stack([np.interp(yi, np.arange(h0), a[:, x]) for x in range(w0)], axis=1)
    return np.stack([np.interp(xi, np.arange(w0), tmp[y]) for y in range(h)], axis=0)


def save_png(lin, path):
    out = np.clip(lin, 0, 1)
    s = np.where(out <= 0.0031308, out * 12.92, 1.055 * np.power(out, 1 / 2.4) - 0.055)
    h, w = s.shape[:2]
    rgba = np.concatenate([s, np.ones((h, w, 1))], axis=2).astype(np.float32)
    im = bpy.data.images.new("out", w, h, alpha=False, float_buffer=False)
    im.pixels.foreach_set(rgba.ravel())
    im.filepath_raw = path
    im.file_format = "PNG"
    im.save()
    bpy.data.images.remove(im)


# ================================================================ web GLB export
def save_rgb(a, path, q=84):
    h, w = a.shape[:2]
    rgba = np.concatenate([a, np.ones((h, w, 1), np.float32)], axis=2).astype(np.float32)
    im = bpy.data.images.new("tex", w, h, alpha=False)
    im.pixels.foreach_set(rgba.ravel())
    im.filepath_raw = path
    im.file_format = "JPEG"
    scene.render.image_settings.quality = q
    im.save()
    bpy.data.images.remove(im)


def bake_web_textures():
    """1K side-grain albedo per wood (graded like the render shader) + procedural end grain."""
    outdir = os.path.join(args.textures, "web")
    os.makedirs(outdir, exist_ok=True)
    made = {}
    for kind, spec in WOODS.items():
        side = os.path.join(outdir, f"{kind}_side.jpg")
        end = os.path.join(outdir, f"{kind}_end.jpg")
        if not os.path.exists(side):
            src = bpy.data.images.load(os.path.join(args.textures, spec["tex"], spec["tex"] + "_2K-JPG_Color.jpg"))
            w, h = src.size
            a = np.array(src.pixels[:], dtype=np.float32).reshape(h, w, 4)[..., :3]
            bpy.data.images.remove(src)
            a = a.reshape(h // 2, 2, w // 2, 2, 3).mean(axis=(1, 3))
            if spec["grain"] == "u":
                a = np.ascontiguousarray(np.transpose(a, (1, 0, 2)))
            lum = a @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)
            a = (a - 0.5) * (1 + spec["contrast"]) + 0.52
            mean = a.mean(axis=2, keepdims=True)
            a = mean + (a - mean) * spec["sat"]
            a = a * (spec["val"][0] + spec["val"][1]) / 2
            k0, k1 = spec["knot"]
            km = np.clip((k1 - lum) / (k1 - k0), 0, 1)[..., None] * 0.7
            tone = np.array([int(spec["knot_tone"][i:i + 2], 16) / 255 for i in (1, 3, 5)], dtype=np.float32)
            save_rgb(np.clip(a * (1 - km) + tone * km, 0, 1), side)
        if not os.path.exists(end):
            n = 512
            yy, xx = np.mgrid[0:n, 0:n].astype(np.float32) / n
            r = np.hypot(xx - 0.35, yy - 0.82) * 38 + 0.6 * np.sin(xx * 9) * np.cos(yy * 7)
            ring = 0.5 + 0.5 * np.sin(r * 2 * np.pi) ** 3
            light = np.array([0.86, 0.72, 0.52] if kind == "pine" else [0.42, 0.28, 0.18], dtype=np.float32)
            save_rgb((light * 0.82 + light * 0.18 * ring[..., None]).astype(np.float32), end)
        made[kind] = (side, end)
    return made


def web_material(name, path):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    n, l = m.node_tree.nodes, m.node_tree.links
    b = n["Principled BSDF"]
    t = n.new("ShaderNodeTexImage")
    t.image = bpy.data.images.load(path, check_existing=True)
    l.new(t.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.78
    b.inputs["Specular IOR Level"].default_value = 0.25
    return m


def export_glb(path):
    tex = bake_web_textures()
    wmats = {k: (web_material(f"{k}_side", s), web_material(f"{k}_end", e)) for k, (s, e) in tex.items()}
    clean = {}
    ROOT.rotation_euler = (0, 0, 0)
    ROOT.location = (0, 0, 0)
    bpy.context.view_layer.update()
    obs = [ob for ob, _ in OBJECTS]
    for ob in obs:
        mw = ob.matrix_world.copy()
        ob.parent = None
        ob.matrix_world = mw
    bpy.ops.object.select_all(action="DESELECT")
    for ob in obs:
        ob.hide_render = False
        ob.select_set(True)
    bpy.context.view_layer.objects.active = obs[0]
    bpy.ops.object.make_single_user(object=True, obdata=True)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    for ob, kind in OBJECTS:
        me = ob.data
        if kind == "wood":
            gk = ob.get("grain_kind", "pine")
            tile = WOODS[gk]["tile"]
            me.materials.clear()
            me.materials.append(wmats[gk][0])
            me.materials.append(wmats[gk][1])
            uvl = me.uv_layers.new(name="UVMap")
            # transforms are applied: recover the grain axis from the object's name-free geometry
            xs = [v.co.x for v in me.vertices]; ys = [v.co.y for v in me.vertices]
            along_x = (max(xs) - min(xs)) >= (max(ys) - min(ys)) if ob.get("grain_axis") is None else ob["grain_axis"] == "x"
            ru, rv = random.random(), random.random()
            for poly in me.polygons:
                n = poly.normal
                gx, gy = (abs(n.x), abs(n.y)) if along_x else (abs(n.y), abs(n.x))   # along / across grain
                nz = abs(n.z)
                end_face = gx > gy and gx > nz and gx > 0.6
                poly.material_index = 1 if end_face else 0
                for li in poly.loop_indices:
                    co = me.vertices[me.loops[li].vertex_index].co
                    a_ = co.x if along_x else co.y
                    c_ = co.y if along_x else co.x
                    if end_face:
                        u, v = c_ / 0.18 + ru, co.z / 0.18 + rv
                    elif nz >= gy:
                        u, v = c_ / tile + ru, a_ / tile + rv
                    else:
                        u, v = co.z / tile + ru, a_ / tile + rv
                    uvl.data[li].uv = (u, v)
        elif kind == "decal":
            src = me.materials[0]
            img = next(nd.image for nd in src.node_tree.nodes if nd.type == "TEX_IMAGE")
            if img.name not in clean:
                cm = bpy.data.materials.new("mark_" + img.name)
                cm.use_nodes = True
                n, l = cm.node_tree.nodes, cm.node_tree.links
                b = n["Principled BSDF"]
                t = n.new("ShaderNodeTexImage")
                t.image = img
                l.new(t.outputs["Color"], b.inputs["Base Color"])
                l.new(t.outputs["Alpha"], b.inputs["Alpha"])
                b.inputs["Roughness"].default_value = 0.9
                clean[img.name] = cm
            me.materials[0] = clean[img.name]
            nrm = me.polygons[0].normal.copy()
            for v in me.vertices:      # web viewers need a little more offset against z-fighting
                v.co += nrm * 0.0006
    bpy.ops.object.join()
    joined = bpy.context.view_layer.objects.active
    joined.name = NAME
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    bpy.ops.export_scene.gltf(filepath=path, export_format="GLB", use_selection=True, export_apply=True,
                              export_yup=True, export_image_format="WEBP", export_image_quality=80,
                              export_cameras=False, export_lights=False, export_extras=False,
                              export_materials="EXPORT", export_normals=True, export_texcoords=True)
    print("WROTE", path, os.path.getsize(path) // 1024, "KB")


# ================================================================ render views
BG_LIN = srgb("#F2F2F2")[0]
os.makedirs(args.out, exist_ok=True)
prep(R)
is_collar = bool(R["parts"]) and all(p["role"] == "collar" for p in R["parts"])
views = COLLAR_VIEWS if is_collar else VIEWS
wanted = [int(v) for v in args.views.split(",") if v and int(v) in views]
built = None
H = R["dims"][2]
LX, WY = R["dims"][0], R["dims"][1]
for v in wanted:
    cfg = views[v]
    key = (cfg.get("stack", 1), cfg.get("pallet", True)) if is_collar else "pallet"
    if key != built:
        clear_pallet()
        if is_collar:
            H = build_collar(stack=key[0], on_pallet=key[1])
            LX, WY = R["dims"][0] + 12, R["dims"][1] + 12
        else:
            build_recipe(R)
        built = key
    if cfg.get("detail"):
        # frame the corner around the first marking, turned to face the camera ~18 degrees off-axis
        decals = [ob for ob, kind in OBJECTS if kind == "decal"]
        dec = decals[min(args.detail_index, len(decals) - 1)] if decals else None
        if dec is None:
            print("SKIP view", v, "(no markings)")
            continue
        pts = [q.co for q in dec.data.vertices]
        c = sum(pts, Vector()) / len(pts)
        n = dec.data.polygons[0].normal
        t = Vector((-n.y, n.x, 0)).normalized()
        half = max(max((q - c).dot(t) for q in pts) * 2.5, H * MM * 0.75)
        local = [Vector((p.x, p.y, z * MM)) for s in (-1, 1) for d in (0.0, 0.18)
                 for p in [c + t * s * half - n * d] for z in (0, H)]
        az = math.radians(CAM_AZ)
        rot = math.degrees(math.atan2(-math.cos(az), math.sin(az)) - math.atan2(n.y, n.x)) + 18
        ROOT.rotation_euler = (0, 0, math.radians(rot))
        ROOT.location = (0, 0, 0)
    else:
        local = [Vector((sx * LX / 2 * MM, sy * WY / 2 * MM, z * MM)) for sx in (-1, 1) for sy in (-1, 1) for z in (0, H)]
        ROOT.rotation_euler = (math.pi if cfg.get("flip") else 0, 0, math.radians(cfg["rot"]))
        ROOT.location = (0, 0, H * MM if cfg.get("flip") else 0)
    frame(local, cfg["el"], cfg["margin"])
    base = os.path.join(args.out, f"{NAME}-{v}")
    for ob, _ in OBJECTS:
        ob.hide_render = False
    beauty = render_linear(base + "_b.exr", args.samples)
    for ob, _ in OBJECTS:
        ob.hide_render = True
    plate = render_linear(base + "_p.exr", 24, scale=1.0 if cfg["el"] < 15 else 0.25)
    lum = upsample(plate.mean(axis=2), beauty.shape[0], beauty.shape[1])[..., None]
    save_png(beauty / np.maximum(lum, 1e-4) * BG_LIN, base + ".png")
    print("WROTE", base + ".png")

if args.glb:
    clear_pallet()
    if is_collar:
        build_collar(stack=1, on_pallet=True)
    else:
        build_recipe(R)
    for ob, kind in OBJECTS:
        if kind == "wood":
            pass
    export_glb(args.glb)

if args.blend:
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(args.out, NAME + ".blend"))
