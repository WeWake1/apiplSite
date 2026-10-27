"""Exact component lists for every pallet we render.

Sources
  EPAL 1/2/3 ......... EPAL product sheets PB 07/2020 (+ EPAL 2/3 sheets 2023), vector-measured
  CP1-CP9 ............ EPAL CP product sheets PB CP 07/2022 (CP4: design drawing ed. 6),
                       vector-measured from the drawings; board/block counts cross-checked
  PW / HW / GMA / collar  No public standard. Built to match the published reference
                       range (overall L x W x H, board count, layout) measured from the
                       reference images.

Coordinates (mm): origin = centre of the pallet footprint on the floor, z up.
X is the direction the TOP deck boards run; Y runs across them.

Every component is an axis-aligned prism:
  {"name", "role", "x": [a, b], "y": [a, b], "z": [a, b], "grain": "x" | "y", "wood"}
optional features:
  "edge_chamfer": {"side": "+y"|"-y"|"+x"|"-x", "depth": mm, "openings": [[a, b], ...]}
        45 deg chamfer on the upper outer edge, ONLY inside the openings between blocks,
        with curved run-outs (EPAL "chamfered lower edge boards").
  "notches": [{"center": c, "length": l, "depth": d, "radius": r}]   cut from the underside
Pallet-level:
  "corners": [{"c": leg, "x": [..], "y": [..], "z": [..]}]  45 deg vertical corner chamfer that
        cuts EVERY component inside that z range which reaches the corner.

Run this file directly to print a validation table (dimensions, counts) and write recipes.json.
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


# ---------------------------------------------------------------- helpers
def runs(start, widths, gaps):
    """Consecutive [a, b] spans: widths with gaps between them (gap 0 = butted boards)."""
    if isinstance(gaps, (int, float)):
        gaps = [gaps] * (len(widths) - 1)
    assert len(gaps) == len(widths) - 1, (widths, gaps)
    out, c = [], start
    for i, w in enumerate(widths):
        out.append([round(c, 3), round(c + w, 3)])
        c += w + (gaps[i] if i < len(gaps) else 0)
    return out


def centred(total, widths, gaps):
    """Like runs() but centred on 0 over `total` (checks the fit).
    gaps: number, or list of numbers / "a" (auto: equal gaps solved so the deck fits exactly)."""
    if isinstance(gaps, (int, float)):
        gaps = [gaps] * (len(widths) - 1)
    if "a" in gaps:
        fixed = sum(g for g in gaps if g != "a")
        auto = (total - sum(widths) - fixed) / gaps.count("a")
        gaps = [auto if g == "a" else g for g in gaps]
    span = sum(widths) + sum(gaps)
    assert abs(span - total) < 0.6, f"layout {span} != {total}"
    return runs(-total / 2, widths, gaps)


def even_gaps(total, widths):
    g = (total - sum(widths)) / (len(widths) - 1)
    return centred(total, widths, g)


def flush3(total, w_outer, w_centre=None):
    """Three members: flush with both edges and centred."""
    w_centre = w_outer if w_centre is None else w_centre
    h = total / 2
    return [[-h, -h + w_outer], [-w_centre / 2, w_centre / 2], [h - w_outer, h]]


def inset3(total, inset, w):
    """Three members of width w, outer ones `inset` from the edges, one centred."""
    h = total / 2
    return [[-h + inset, -h + inset + w], [-w / 2, w / 2], [h - inset - w, h - inset]]


class P:
    """Pallet under construction."""

    def __init__(self, pid, L, W, H, wood="pine"):
        self.pid, self.L, self.W, self.H, self.wood = pid, L, W, H, wood
        self.parts, self.corners, self.meta = [], [], {}
        self.stamp_axis = "y"  # faces that carry the markings: normal +-y (default) or +-x

    def add(self, role, x, y, z, grain, name=None, **feat):
        d = {"name": name or f"{role}{len([p for p in self.parts if p['role'] == role]) + 1}",
             "role": role, "x": [round(v, 3) for v in x], "y": [round(v, 3) for v in y],
             "z": [round(v, 3) for v in z], "grain": grain,
             "wood": feat.pop("wood", "block" if role in ("block",) else self.wood)}
        d.update(feat)
        self.parts.append(d)
        return d

    def boards_x(self, role, ys, z, x=None, **feat):
        """Boards running along X, one per [y0, y1] span."""
        x = x or [-self.L / 2, self.L / 2]
        return [self.add(role, x, y, z, "x", **feat) for y in ys]

    def boards_y(self, role, xs, z, y=None, **feat):
        y = y or [-self.W / 2, self.W / 2]
        return [self.add(role, x, y, z, "y", **feat) for x in xs]

    def blocks(self, xs, ys, z):
        for x in xs:
            for y in ys:
                self.add("block", x, y, z, "y")

    def corner(self, c, z=None, x=None, y=None):
        self.corners.append({"c": c, "x": x or [-self.L / 2, self.L / 2], "y": y or [-self.W / 2, self.W / 2],
                             "z": z or [0, self.H]})

    def openings(self, members):
        """Gaps between consecutive [a, b] members along an axis (block faces)."""
        m = sorted(members)
        return [[m[i][1], m[i + 1][0]] for i in range(len(m) - 1)]

    def done(self, **meta):
        self.meta.update(meta)
        return {"id": self.pid, "dims": [self.L, self.W, self.H], "parts": self.parts,
                "corners": self.corners, "stamp_axis": self.stamp_axis, "meta": self.meta}


# ---------------------------------------------------------------- EPAL
def epal1():
    p = P("epal1", 1200, 800, 144)
    top = centred(800, [145, 100, 145, 100, 145], [42, 40.5, 40.5, 42])   # "287 +-3" = 145+42+100
    cols = flush3(1200, 145)                                           # blocks / cross boards along X
    rows = [[-400, -300], [-72.5, 72.5], [300, 400]]                   # 100 | 145 | 100
    p.boards_x("bottom", rows[:1], [0, 22], edge_chamfer={"side": "-y", "depth": 11, "openings": p.openings(cols)})
    p.boards_x("bottom", rows[1:2], [0, 22])
    p.boards_x("bottom", rows[2:], [0, 22], edge_chamfer={"side": "+y", "depth": 11, "openings": p.openings(cols)})
    p.blocks(cols, rows, [22, 100])
    p.boards_y("cross", cols, [100, 122])
    p.boards_x("top", top, [122, 144])
    p.corner(17)
    return p.done(official={"boards": 11, "blocks": 9, "nails": 78})


def epal2():
    # Top boards run along the 1000 side, so X = 1000 here.
    p = P("epal2", 1000, 1200, 162)
    p.stamp_axis = "x"   # the 1200 mm long sides
    top = centred(1200, [145, 100, 100, 100, 100, 100, 100, 100, 145], [0, 35, 35, 35, 35, 35, 35, 0])
    xrows = flush3(1000, 100)                       # stringers & block rows (along X positions)
    ycols = [[-600, -455], [-50, 50], [455, 600]]   # block columns along Y (145 | 100 | 145)
    # single-layer perimeter base: 2 end boards along X + 3 boards along Y between them
    xo = p.openings(xrows)
    p.boards_x("bottom", [[-600, -500]], [0, 22], x=[-500, 500], edge_chamfer={"side": "-y", "depth": 11, "openings": xo})
    p.boards_x("bottom", [[500, 600]], [0, 22], x=[-500, 500], edge_chamfer={"side": "+y", "depth": 11, "openings": xo})
    yo = [[-455, -50], [50, 455]]
    p.boards_y("bottom", [xrows[0]], [0, 22], y=[-500, 500], edge_chamfer={"side": "-x", "depth": 11, "openings": yo})
    p.boards_y("bottom", [xrows[1]], [0, 22], y=[-500, 500])
    p.boards_y("bottom", [xrows[2]], [0, 22], y=[-500, 500], edge_chamfer={"side": "+x", "depth": 11, "openings": yo})
    p.blocks(xrows, ycols, [22, 117])
    p.boards_y("cross", xrows, [117, 142])          # stringer boards 25 thick, 1200 long
    p.boards_x("top", top, [142, 162])
    p.corner(24)
    return p.done(official={"boards": 17, "blocks": 9, "nails": 133})


def epal3():
    p = P("epal3", 1200, 1000, 144)
    top = centred(1000, [145, 100, 100, 145, 100, 100, 145], [0, 41.25, 41.25, 41.25, 41.25, 0])
    cols = flush3(1200, 145)
    rows = flush3(1000, 145)
    p.boards_x("bottom", rows[:1], [0, 22], edge_chamfer={"side": "-y", "depth": 11, "openings": p.openings(cols)})
    p.boards_x("bottom", rows[1:2], [0, 22])
    p.boards_x("bottom", rows[2:], [0, 22], edge_chamfer={"side": "+y", "depth": 11, "openings": p.openings(cols)})
    p.blocks(cols, rows, [22, 100])
    p.boards_y("cross", cols, [100, 122])
    p.boards_x("top", top, [122, 144])
    p.corner(24)
    return p.done(official={"boards": 13, "blocks": 9, "nails": 84})


# ---------------------------------------------------------------- CP (top 18, stringer 22, block 80, bottom 18)
def cp_simple(pid, L, W, top_w, block_y, bottom_w, stringer_inset=40, block_inset=50, block_x=80,
              stringer_w=100, chamfer=20, official=None):
    """CP1/2/3/5: 3 stringer boards along Y, 9 blocks, 3 bottom boards along X, 138 high."""
    p = P(pid, L, W, 138)
    top = even_gaps(W, top_w)
    if stringer_inset == 0:
        sx = flush3(L, stringer_w)
        bx = flush3(L, block_x)
    else:
        sx = inset3(L, stringer_inset, stringer_w)
        bx = inset3(L, block_inset, block_x)
    by = flush3(W, block_y[0], block_y[1])
    bottom = flush3(W, bottom_w[0], bottom_w[1])
    p.boards_x("bottom", bottom, [0, 18])
    p.blocks(bx, by, [18, 98])
    p.boards_y("cross", sx, [98, 120])
    p.boards_x("top", top, [120, 138])
    if chamfer:
        p.corner(chamfer)
    return p.done(official=official or {})


def cp1():
    return cp_simple("cp1", 1200, 1000, [100, 80, 80, 80, 100, 80, 80, 80, 100], (135, 135), (135, 135),
                     official={"boards": 15, "blocks": 9, "nails": 81})


def cp2():
    return cp_simple("cp2", 1200, 800, [100, 80, 80, 100, 80, 80, 100], (100, 100), (100, 100),
                     official={"boards": 13, "blocks": 9, "nails": 60})


def cp3():
    return cp_simple("cp3", 1140, 1140, [120, 80, 80, 80, 120, 80, 80, 80, 120], (135, 135), (135, 135),
                     official={"boards": 15, "blocks": 9, "nails": 81})


def cp5():
    return cp_simple("cp5", 1140, 760, [100, 80, 80, 100, 80, 80, 100], (80, 80), (80, 100),
                     stringer_inset=0, block_x=100, chamfer=0,
                     official={"boards": 13, "blocks": 9, "nails": 60})


def cp4():
    # 1300 x 1100 deck overhanging a 1200 x 1000 base by 50 mm all round
    p = P("cp4", 1300, 1100, 138)
    top = even_gaps(1100, [120, 80, 80, 80, 120, 80, 80, 80, 120])
    sx = inset3(1200, 40, 100)          # relative to the 1200 base
    bx = inset3(1200, 50, 80)
    by = flush3(1000, 120)
    p.boards_x("bottom", by, [0, 18], x=[-600, 600])
    p.blocks(bx, by, [18, 98])
    p.boards_y("cross", sx, [98, 120])  # 1100 long, full deck width
    p.boards_x("top", top, [120, 138])
    p.corner(20, z=[120, 138])
    p.corner(20, z=[0, 18], x=[-600, 600], y=[-500, 500])
    return p.done(official={"boards": 15, "blocks": 9})


def cp_two_layer(pid, L, W, top_w, top_g, stringers, block_x, block_y, upper, lower, corner_z, official):
    """CP6-CP9: two-layer base (upper along X under the blocks, lower along Y), 156 high."""
    p = P(pid, L, W, 156)
    top = centred(W, top_w, top_g)
    for x, y in lower["at"]:
        p.add("bottom", x, y, [0, 18], "y")
    for x, y in upper["at"]:
        p.add("bottom", x, y, [18, 36], "x")
    p.blocks(block_x, block_y, [36, 116])
    p.boards_y("cross", stringers, [116, 138])
    p.boards_x("top", top, [138, 156])
    for z in corner_z:
        p.corner(20, z=z)
    return p, top, official


def cp6():
    xs_b = [[-450, -370], [-40, 40], [370, 450]]
    ys_b = [[-550, -450], [-50, 50], [450, 550]]
    p, top, off = cp_two_layer(
        "cp6", 1000, 1200, [100, 80, 80, 80, 80, 100, 80, 80, 80, 80, 100], [0, 32.5, 32.5, 32.5, 32.5, 32.5, 32.5, 32.5, 32.5, 0],
        [[-500, -375], [-50, 50], [375, 500]], xs_b, ys_b,
        upper={"at": [([-450, 450], y) for y in ys_b]},
        lower={"at": [(x, [-550, 550]) for x in [[-450, -350], [-50, 50], [350, 450]]]},
        corner_z=[[116, 156]], official={"boards": 20, "blocks": 9, "nails": 84})
    return p.done(official=off)


def cp7():
    xs_b = [[-500, -420], [-40, 40], [420, 500]]
    ys_b = [[-600, -500], [-50, 50], [500, 600]]
    p, top, off = cp_two_layer(
        "cp7", 1100, 1300, [100, 100, 80, 80, 80, 100, 80, 80, 80, 100, 100], [0, 40, 40, 40, 40, 40, 40, 40, 40, 0],
        [[-550, -425], [-50, 50], [425, 550]], xs_b, ys_b,
        upper={"at": [([-500, 500], y) for y in ys_b]},
        lower={"at": [(x, [-600, 600]) for x in [[-500, -420], [-370, -290], [-40, 40], [290, 370], [420, 500]]]},
        corner_z=[[116, 156]], official={"boards": 22, "blocks": 9, "nails": 96})
    return p.done(official=off)


def cp8():
    # container pallet with a bottom outlet: centre deck board split, 4 stringers, 12 blocks
    xs_b = [[-550, -470], [-230, -150], [150, 230], [470, 550]]
    ys_b = [[-550, -450], [-50, 50], [450, 550]]
    p = P("cp8", 1140, 1140, 156)
    for x in [[-570, -470], [-250, -150], [150, 250], [470, 570]]:
        p.add("bottom", x, [-570, 570], [0, 18], "y")
    for y in ys_b:
        p.add("bottom", [-570, 570], y, [18, 36], "x")
    p.blocks(xs_b, ys_b, [36, 116])
    p.boards_y("cross", xs_b, [116, 138])
    top = centred(1140, [120, 80, 80, 80, 100, 80, 80, 80, 120], [34, 28, 0, 98, 98, 0, 28, 34])
    for i, y in enumerate(top):
        if i == 4:   # split centre board -> 300 mm outlet opening between the middle stringers
            p.add("top", [-570, -150], y, [138, 156], "x")
            p.add("top", [150, 570], y, [138, 156], "x")
        else:
            p.add("top", [-570, 570], y, [138, 156], "x")
    p.corner(20)
    return p.done(official={"boards": 28, "blocks": 12, "nails": 116})


def cp9():
    xs_b = [[-550, -470], [-40, 40], [470, 550]]
    ys_b = [[-550, -450], [-50, 50], [450, 550]]
    p, top, off = cp_two_layer(
        "cp9", 1140, 1140, [120, 80, 80, 80, 120, 80, 80, 80, 120], 37.5, xs_b, xs_b, ys_b,
        upper={"at": [([-570, 570], y) for y in ys_b]},
        lower={"at": [(x, [-570, 570]) for x in [[-570, -470], [-50, 50], [470, 570]]]},
        corner_z=[[0, 156]], official={"boards": 24, "blocks": 9, "nails": 102})
    return p.done(official=off)


# ---------------------------------------------------------------- pinewood (reference range)
def block_simple(pid, L, W, H, top_w, top_g, cross_x, block_y, t=(20, 20, 70, 20), bottom="rows",
                 wood="pine", chamfer_bottom=0, bottom_extra=None):
    """Block pallet: bottom (rows along X | perimeter) -> blocks -> cross boards along Y -> top along X.
    t = (top, cross, block, bottom) thickness/heights."""
    tt, tc, tb, tbot = t
    p = P(pid, L, W, H, wood)
    zb = 0
    layers = []
    if bottom_extra:  # lower full-deck layer under everything
        ys = bottom_extra["boards"]
        for x in ys:
            p.add("bottom", x, [-W / 2, W / 2], [0, bottom_extra["t"]], "y")
        zb = bottom_extra["t"]
    if bottom == "rows":
        for y in block_y:
            feat = {}
            if chamfer_bottom and (y[0] <= -W / 2 + 0.01 or y[1] >= W / 2 - 0.01):
                feat["edge_chamfer"] = {"side": "-y" if y[0] < 0 else "+y", "depth": chamfer_bottom,
                                        "openings": p.openings(cross_x)}
            p.add("bottom", [-L / 2, L / 2], y, [zb, zb + tbot], "x", **feat)
    elif bottom == "perimeter":
        # 2 end boards along Y at the X ends (under the outer block columns), 3 boards along X between
        xe = cross_x
        for x in (xe[0], xe[2]):
            feat = {}
            if chamfer_bottom:
                feat["edge_chamfer"] = {"side": "-x" if x[0] < 0 else "+x", "depth": chamfer_bottom,
                                        "openings": p.openings(block_y)}
            p.add("bottom", x, [-W / 2, W / 2], [zb, zb + tbot], "y", **feat)
        for y in block_y:
            feat = {}
            if chamfer_bottom and (y[0] <= -W / 2 + 0.01 or y[1] >= W / 2 - 0.01):
                feat["edge_chamfer"] = {"side": "-y" if y[0] < 0 else "+y", "depth": chamfer_bottom,
                                        "openings": [[xe[0][1], xe[1][0]], [xe[1][1], xe[2][0]]]}
            p.add("bottom", [xe[0][1], xe[2][0]], y, [zb, zb + tbot], "x", **feat)
    z = zb + tbot
    p.blocks(cross_x, block_y, [z, z + tb])
    z += tb
    p.boards_y("cross", cross_x, [z, z + tc])
    z += tc
    p.boards_x("top", centred(W, top_w, top_g), [z, z + tt])
    z += tt
    assert abs(z - H) < 0.01, (pid, z, H)
    return p


def pw01():
    p = block_simple("pw01", 1200, 800, 130, [120, 100, 100, 100, 120], [57, 73, 73, 57],
                     flush3(1200, 100), flush3(800, 100))
    return p.done()


def pw02():
    p = block_simple("pw02", 1000, 1200, 130, [100] * 9, 37.5,
                     flush3(1000, 120, 100), flush3(1200, 120, 100), bottom="perimeter")
    p.stamp_axis = "x"
    return p.done()


def pw03():
    p = block_simple("pw03", 1120, 1120, 130, [120, 90, 90, 90, 90, 90, 120], [60, 77.5, 77.5, 77.5, 77.5, 60],
                     flush3(1120, 90), flush3(1120, 90))
    return p.done()


def pw04():
    lower = centred(1120, [120, 90, 90, 90, 90, 90, 120], [57.5, 78.75, 78.75, 78.75, 78.75, 57.5])
    p = block_simple("pw04", 1120, 1120, 150, [120, 90, 90, 90, 90, 90, 120], [60, 77.5, 77.5, 77.5, 77.5, 60],
                     flush3(1120, 90), flush3(1120, 90), bottom_extra={"t": 20, "boards": lower})
    return p.done()


def pw07():
    p = block_simple("pw07", 1000, 1000, 146, [110, 97, 97, 97, 97, 97, 97, 97, 110], 12.625,
                     flush3(1000, 110, 95), flush3(1000, 110, 95), t=(22, 22, 80, 22), bottom="perimeter")
    return p.done()


def pw08():
    p = block_simple("pw08", 1100, 1100, 146, [127, 100, 97, 97, 97, 97, 97, 100, 127], [0, "a", "a", "a", "a", "a", "a", 0],
                     flush3(1100, 120, 97), flush3(1100, 120, 97), t=(22, 22, 80, 22), bottom="perimeter",
                     chamfer_bottom=11)
    return p.done()


def skid(pid, L, W, H, top_w, top_g, runners, t_top, wood="pine", bottom=None, t_bottom=0):
    """Stringer / skid pallet: optional bottom boards along X -> runners along Y -> top along X."""
    p = P(pid, L, W, H, wood)
    p.stamp_axis = "x"   # outer stringer faces
    z = 0
    if bottom:
        for y in bottom:
            p.add("bottom", [-L / 2, L / 2], y, [0, t_bottom], "x")
        z = t_bottom
    for x in runners:
        p.add("stringer", x, [-W / 2, W / 2], [z, H - t_top], "y")
    p.boards_x("top", centred(W, top_w, top_g), [H - t_top, H])
    return p


def pw05():
    return skid("pw05", 1100, 1100, 130, [155, 127, 127, 127, 127, 127, 155], 25.833,
                flush3(1100, 100), 22).done()


def pw06():
    runners = [[-570, -495], [-107.5, -67.5], [67.5, 107.5], [495, 570]]
    return skid("pw06", 1140, 1140, 130, [110] * 9, 18.75, runners, 22,
                bottom=centred(1140, [110, 110, 110], 405), t_bottom=20).done()


# ---------------------------------------------------------------- hardwood (reference range)
def hw01():
    p = block_simple("hw01", 1000, 1200, 161, [97, 97, 100, 100, 100, 100, 100, 100, 97, 97],
                     [0, "a", "a", "a", "a", "a", "a", "a", 0], flush3(1000, 120, 100),
                     flush3(1200, 120, 100), t=(22, 22, 95, 22), wood="hard", bottom="perimeter")
    p.stamp_axis = "x"
    return p.done()


def hw02():
    p = block_simple("hw02", 1200, 1000, 161, [103, 103, 104, 116, 116, 104, 103, 103], [0, 33, 41, 0, 41, 33, 0],
                     flush3(1200, 150, 120), flush3(1000, 120, 100), t=(22, 22, 95, 22), wood="hard",
                     chamfer_bottom=11)
    return p.done()


def hw03():
    return skid("hw03", 1200, 1200, 144, [105] * 9, 31.875, flush3(1200, 100), 22, wood="hard",
                bottom=centred(1200, [120, 120, 120], 420), t_bottom=22).done()


def hw04():
    runners = [[-600, -500], [-100, -20], [20, 100], [500, 600]]
    return skid("hw04", 1200, 1235, 122, [120] * 10, 3.889, runners, 25, wood="hard").done()


def hw05():
    p = block_simple("hw05", 1275, 1275, 161, [104, 104, 105, 105, 123, 123, 105, 105, 104, 104],
                     [0, "a", "a", "a", 0, "a", "a", "a", 0], flush3(1275, 150, 120), flush3(1275, 150, 120),
                     t=(22, 22, 95, 22), wood="hard", bottom="perimeter", chamfer_bottom=11)
    p.corner(20)
    return p.done()


def hw06():
    runners = [[-600, -520], [-91.5, -31.5], [31.5, 91.5], [520, 600]]
    return skid("hw06", 1200, 1200, 144, [135, 126, 140, 139.5, 139.5, 140, 126, 135], ["a", "a", 0, "a", 0, "a", "a"],
                runners, 22, wood="hard",
                bottom=centred(1200, [135, 126, 140, 139.5, 139.5, 140, 126, 135], ["a", "a", 0, "a", 0, "a", "a"]),
                t_bottom=22).done()


# ---------------------------------------------------------------- GMA 48 x 40 in
def gma():
    # top boards along the 40" (1016) side, three notched stringers along the 48" (1220) side
    p = P("gma", 1016, 1220, 132)
    p.stamp_axis = "x"
    for y in ([-610, -450], [-50, 50], [450, 610]):
        p.add("bottom", [-508, 508], y, [0, 18], "x")
    notches = [{"center": -305, "length": 230, "depth": 38, "radius": 32},
               {"center": 305, "length": 230, "depth": 38, "radius": 32}]
    for x in ([-508, -470], [-19, 19], [470, 508]):
        p.add("stringer", x, [-610, 610], [18, 114], "y", notches=notches)
    p.boards_x("top", centred(1220, [160, 100, 100, 100, 100, 100, 160], [55, 72.5, 72.5, 72.5, 72.5, 55]), [114, 132])
    return p.done(official={"boards": 10, "stringers": 3})


# ---------------------------------------------------------------- pallet collar (on a Euro-size base)
def collar():
    p = P("collar", 1200, 800, 195)
    t = 20
    p.add("collar", [-600, 600], [-400, -400 + t], [0, 195], "x")
    p.add("collar", [-600, 600], [400 - t, 400], [0, 195], "x")
    p.add("collar", [-600, -600 + t], [-400 + t, 400 - t], [0, 195], "y")  # short boards between the long ones
    p.add("collar", [600 - t, 600], [-400 + t, 400 - t], [0, 195], "y")
    return p.done(base="epal1", hinges=True)


ALL = [epal1, epal2, epal3, cp1, cp2, cp3, cp4, cp5, cp6, cp7, cp8, cp9,
       pw01, pw02, pw03, pw04, pw05, pw06, pw07, pw08, hw01, hw02, hw03, hw04, hw05, hw06, gma, collar]


def bbox(parts):
    return [min(p["x"][0] for p in parts), max(p["x"][1] for p in parts),
            min(p["y"][0] for p in parts), max(p["y"][1] for p in parts),
            min(p["z"][0] for p in parts), max(p["z"][1] for p in parts)]


def check(r):
    """Overlap & extent sanity checks; returns list of problems."""
    probs = []
    L, W, H = r["dims"]
    b = bbox(r["parts"])
    if abs((b[1] - b[0]) - L) > 0.5 or abs((b[3] - b[2]) - W) > 0.5 or abs(b[5] - H) > 0.5 or abs(b[4]) > 0.01:
        probs.append(f"extent {b} != {L}x{W}x{H}")
    parts = r["parts"]
    for i, a in enumerate(parts):
        for c in parts[i + 1:]:
            ox = min(a["x"][1], c["x"][1]) - max(a["x"][0], c["x"][0])
            oy = min(a["y"][1], c["y"][1]) - max(a["y"][0], c["y"][0])
            oz = min(a["z"][1], c["z"][1]) - max(a["z"][0], c["z"][0])
            if ox > 0.5 and oy > 0.5 and oz > 0.5:
                probs.append(f"overlap {a['name']} / {c['name']} ({ox:.0f}x{oy:.0f}x{oz:.0f})")
    # every board/block must rest on something (except the floor layer)
    for a in parts:
        if a["z"][0] < 0.01:
            continue
        support = any(abs(c["z"][1] - a["z"][0]) < 0.01 and
                      min(a["x"][1], c["x"][1]) - max(a["x"][0], c["x"][0]) > 0.5 and
                      min(a["y"][1], c["y"][1]) - max(a["y"][0], c["y"][0]) > 0.5 for c in parts)
        if not support and a["role"] != "collar":
            probs.append(f"{a['name']} floats at z={a['z'][0]}")
    return probs


def table(recipes):
    rows = []
    for r in recipes:
        roles = {}
        for p in r["parts"]:
            roles[p["role"]] = roles.get(p["role"], 0) + 1
        boards = sum(v for k, v in roles.items() if k in ("top", "cross", "bottom"))
        off = r["meta"].get("official", {})
        rows.append((r["id"], "x".join(str(round(v)) for v in r["dims"]), roles.get("top", 0), roles.get("cross", 0),
                     roles.get("stringer", 0), roles.get("block", 0), roles.get("bottom", 0), boards,
                     off.get("boards", "-"), off.get("blocks", "-"), len(r["corners"]),
                     sum(1 for p in r["parts"] if "edge_chamfer" in p), "; ".join(check(r)) or "ok"))
    hdr = ("pallet", "LxWxH", "top", "cross", "string", "blocks", "bottom", "boards", "off.brd", "off.blk", "corner", "edgeChf", "checks")
    w = [max(len(str(x[i])) for x in rows + [hdr]) for i in range(len(hdr))]
    print("  ".join(h.ljust(w[i]) for i, h in enumerate(hdr)))
    for row in rows:
        print("  ".join(str(v).ljust(w[i]) for i, v in enumerate(row)))


if __name__ == "__main__":
    recipes = [f() for f in ALL]
    table(recipes)
    out = os.path.join(HERE, "recipes.json")
    with open(out, "w") as fh:
        json.dump({r["id"]: r for r in recipes}, fh, indent=1)
    print("wrote", out)
