"""Parametrisches Gehaeuse fuer Waveshare 7.5" e-Paper + e-Paper ESP32 Driver Board.

Aufruf:  python3 -I build_case.py <ausgabeordner>
Benoetigt: trimesh, manifold3d, shapely, numpy

Koordinaten: x = Laenge, y = Tiefe (Front = -y), z = Hoehe. Koerper-Unterseite z=0,
Bodenplatte liegt darunter (z = -COVER_T .. 0).
"""
import sys
import numpy as np
import trimesh
from shapely.geometry import box as sbox, Point

# ---------------- Parameter (mm) ----------------
PANEL_W, PANEL_H, PANEL_T = 170.2, 111.2, 1.18   # 7.5" Rohpanel (Waveshare)
PL_BACK, PL_POCKET, PL_SIDE = 2.0, 1.3, 1.2      # Rueckplatte: Rueckwand, Taschentiefe, Seitenwand
PL_LIP, PL_LIP_T, PL_UP = 1.8, 1.0, 1.2          # Haltelippe oben: Ueberdeckung, Dicke, Ueberstand
PL_BOTTOM_GAP = 2.5                              # Rueckplatte endet so weit ueber Panel-Unterkante (FPC)
PLATE_W = PANEL_W + 0.4 + 2 * PL_SIDE            # Breite Rueckplatte
SLOT_CLR_X = 0.8                                 # Spiel Rueckplatte im Schlitz
SLOT_T = PL_BACK + PL_POCKET + 0.6               # Schlitzdicke (Rueckplatte + Panel + Spiel)
SLOT_DEPTH = 8.0                                 # Einstecktiefe entlang der Panelachse
TILT = 15.0                                      # Neigung nach hinten (Grad)

BOARD_X, BOARD_Y = 48.25, 29.46                  # ESP32 Driver Board (Waveshare)
BOARD_CLR = 0.5                                  # Spiel Platinentasche
PAD_H = 2.5                                      # Abstandshoehe Platine ueber Boden
USB_W, USB_H = 13.0, 8.0                         # USB-C Durchbruch (Stecker mit Huelle)

L, W, H = 180.0, 45.0, 20.0                      # Aussenmasse Koerper
WALL = 1.6
TOP_T = 3.0                                      # Deckenstaerke
CORNER_R = 4.0
COVER_T = 2.4
SLOT_Y_TOP = -14.5                               # Schlitzmitte auf Oberseite
WINDOW_X = 150.0                                 # Durchfuehrung FPC/FFC

SCREW_PILOT, SCREW_CLEAR, POST_D = 2.6, 3.4, 7.0  # M3 Blechschraube
POSTS = [(-60, -17.0), (60, -17.0), (-70, 17.4), (0, 17.4)]


def rrect(x0, y0, x1, y1, r):
    return sbox(x0 + r, y0 + r, x1 - r, y1 - r).buffer(r, resolution=24)


def extrude(poly, z0, z1):
    m = trimesh.creation.extrude_polygon(poly, z1 - z0)
    m.apply_translation([0, 0, z0])
    return m


def cbox(x0, x1, y0, y1, z0, z1):
    return trimesh.creation.box(extents=[x1 - x0, y1 - y0, z1 - z0],
                                transform=trimesh.transformations.translation_matrix(
                                    [(x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2]))


def cyl(x, y, z0, z1, d):
    c = trimesh.creation.cylinder(radius=d / 2, height=z1 - z0, sections=48)
    c.apply_translation([x, y, (z0 + z1) / 2])
    return c


def union(*ms):
    return trimesh.boolean.union(list(ms), engine="manifold")


def diff(a, *bs):
    return trimesh.boolean.difference([a] + list(bs), engine="manifold")


def inter(a, b):
    return trimesh.boolean.intersection([a, b], engine="manifold")


def tilted_slab(width, thick, z_from, z_to):
    """Quader entlang der geneigten Panelachse. z_from/z_to = Abstand ab Oberkante (+ nach oben)."""
    s = cbox(-width / 2, width / 2, -thick / 2, thick / 2, z_from, z_to)
    rot = trimesh.transformations.rotation_matrix(np.radians(-TILT), [1, 0, 0])
    s.apply_transform(rot)
    s.apply_translation([0, SLOT_Y_TOP, H])
    return s


def build_body():
    outer = extrude(rrect(-L / 2, -W / 2, L / 2, W / 2, CORNER_R), 0, H)
    cavity = extrude(rrect(-L / 2 + WALL, -W / 2 + WALL, L / 2 - WALL, W / 2 - WALL,
                           CORNER_R - WALL), -0.01, H - TOP_T)
    shell = diff(outer, cavity)

    # Fuehrungsblock um den Schlitz (innen), bis in die Wand
    guide = tilted_slab(L, SLOT_T + 2 * WALL, -SLOT_DEPTH - 2.0, 30)
    guide = inter(guide, outer)

    # Schraubdome
    posts = [cyl(x, y, 0, H - TOP_T + 0.5, POST_D) for x, y in POSTS]

    body = union(shell, guide, *posts)

    # Schlitz fuer das Panel
    slot = tilted_slab(PLATE_W + SLOT_CLR_X, SLOT_T, -SLOT_DEPTH, 60)
    # Durchfuehrung FPC/FFC in den Innenraum
    yc = SLOT_Y_TOP - (SLOT_DEPTH) * np.tan(np.radians(TILT))
    window = cbox(-WINDOW_X / 2, WINDOW_X / 2, yc - (SLOT_T + 4) / 2, yc + (SLOT_T + 4) / 2,
                  H - SLOT_DEPTH - 3.0, H - SLOT_DEPTH + 0.5)
    # Schraubenvorbohrung
    pilots = [cyl(x, y, -0.1, 12, SCREW_PILOT) for x, y in POSTS]
    # USB-C Durchbruch in der rechten Stirnwand (Platine sitzt rechts)
    zc = PAD_H + 1.6 + 1.6                       # Mitte Buchse ueber Boden
    by_c = board_center()[1]
    usb = cbox(L / 2 - WALL - 1, L / 2 + 1, by_c - USB_W / 2, by_c + USB_W / 2,
               zc - USB_H / 2 + 1.0, zc + USB_H / 2 + 1.0)
    return diff(body, slot, window, *pilots, usb)


def board_center():
    bx = L / 2 - WALL - 0.3 - (BOARD_X + BOARD_CLR) / 2
    by = 20.4 - (BOARD_Y + BOARD_CLR) / 2
    return bx, by


def build_cover():
    plate = extrude(rrect(-L / 2, -W / 2, L / 2, W / 2, CORNER_R), -COVER_T, 0)
    bx, by = board_center()
    iw, ih = BOARD_X + BOARD_CLR, BOARD_Y + BOARD_CLR
    # Platinentasche: Rahmen mit Aussparungen in der Mitte jeder Seite
    frame_h = PAD_H + 1.2
    ring = diff(cbox(bx - iw / 2 - 1.2, bx + iw / 2 + 1.2, by - ih / 2 - 1.2, by + ih / 2 + 1.2, 0, frame_h),
                cbox(bx - iw / 2, bx + iw / 2, by - ih / 2, by + ih / 2, -0.1, frame_h + 0.1),
                cbox(bx - 8, bx + 8, by - ih / 2 - 2, by + ih / 2 + 2, PAD_H, frame_h + 0.1),
                cbox(bx - iw / 2 - 2, bx + iw / 2 + 2, by - 6, by + 6, PAD_H, frame_h + 0.1))
    pads = [cyl(bx + sx * (BOARD_X / 2 - 3), by + sy * (BOARD_Y / 2 - 3), 0, PAD_H, 5)
            for sx in (-1, 1) for sy in (-1, 1)]
    cover = union(plate, ring, *pads)
    holes = [cyl(x, y, -COVER_T - 0.1, 0.1, SCREW_CLEAR) for x, y in POSTS]
    heads = [cyl(x, y, -COVER_T - 0.1, -COVER_T + 1.3, 6.4) for x, y in POSTS]
    return diff(cover, *holes, *heads)


def plate_local():
    """Rueckplatte in Schlitzkoordinaten (x, y', z'); y' < 0 = Vorderseite, z' = 0 an Oberkante Sockel."""
    yb = SLOT_T / 2 - 0.15                       # Rueckseite der Platte
    y_pocket = yb - PL_BACK                      # Taschenboden
    z_bot = -SLOT_DEPTH + PL_BOTTOM_GAP
    z_top = PANEL_H - SLOT_DEPTH + PL_UP
    w = PLATE_W / 2
    back = cbox(-w, w, y_pocket, yb, z_bot, z_top)
    side = [cbox(w - PL_SIDE, w, y_pocket - PL_POCKET, y_pocket, z_bot, z_top),
            cbox(-w, -w + PL_SIDE, y_pocket - PL_POCKET, y_pocket, z_bot, z_top)]
    y_front = y_pocket - PL_POCKET - PL_LIP_T
    # Lippe vor dem Panel (mit 0.1 mm Luft) und Abschlusskappe ueber der Panel-Oberkante
    lip = union(cbox(-w, w, y_front, y_pocket - PANEL_T - 0.1, z_top - PL_UP - PL_LIP, z_top),
                cbox(-w, w, y_front, y_pocket, z_top - PL_UP + 0.1, z_top))
    return union(back, *side, lip), y_pocket


def build_plate():
    """Rueckplatte, Rueckseite auf dem Druckbett."""
    p, _ = plate_local()
    yb = SLOT_T / 2 - 0.15
    m = np.array([[1, 0, 0, 0], [0, 0, 1, 0], [0, -1, 0, yb], [0, 0, 0, 1]], float)
    p.apply_transform(m)
    p.apply_translation([0, -p.bounds[0][1], -p.bounds[0][2]])
    return p


def build_dummy():
    """Platzhalter fuer Panel + Rueckplatte + Board (Kollisionspruefung / Viewer)."""
    pl, y_pocket = plate_local()
    z0 = -SLOT_DEPTH
    panel = cbox(-PANEL_W / 2, PANEL_W / 2, y_pocket - PANEL_T, y_pocket, z0, z0 + PANEL_H)
    panel.apply_transform(trimesh.transformations.rotation_matrix(np.radians(-TILT), [1, 0, 0]))
    panel.apply_translation([0, SLOT_Y_TOP, H])
    plate = pl.copy()
    plate.apply_transform(trimesh.transformations.rotation_matrix(np.radians(-TILT), [1, 0, 0]))
    plate.apply_translation([0, SLOT_Y_TOP, H])
    bx, by = board_center()
    b = cbox(bx - BOARD_X / 2, bx + BOARD_X / 2, by - BOARD_Y / 2, by + BOARD_Y / 2, PAD_H, PAD_H + 1.6)
    return panel, b, plate


if __name__ == "__main__":
    out = sys.argv[1]
    body, cover = build_body(), build_cover()
    for n, m in (("body", body), ("cover", cover)):
        print(n, "watertight:", m.is_watertight, "volume cm3: %.1f" % (m.volume / 1000), m.bounds.round(1).tolist())
    body.export(f"{out}/Case_7.5_Body.stl")
    cover.apply_translation([0, 0, COVER_T])          # flach auf Druckbett
    cover.export(f"{out}/Case_7.5_BottomCover.stl")
    cover.apply_translation([0, 0, -COVER_T])
    p, b, pl = build_dummy()
    cv = lambda a, b_: (lambda x: x.volume if len(x.faces) else 0.0)(inter(a, b_))
    print("Platte/Body Kollision (mm3):", cv(pl, body), " Panel/Platte:", cv(p, pl))
    print("Panel/Body Kollision (Volumen mm3):", inter(p, body).volume if len(inter(p, body).faces) else 0.0)
    print("Board/Body Kollision (Volumen mm3):", inter(b, body).volume if len(inter(b, body).faces) else 0.0)
    print("Board/Cover Kollision (Volumen mm3):", inter(b, cover).volume if len(inter(b, cover).faces) else 0.0)
    # kombinierte 3MF (Platte mit beiden Teilen nebeneinander)
    plate = build_plate()
    print("plate watertight:", plate.is_watertight, plate.bounds.round(1).tolist())
    plate.export(f"{out}/Case_7.5_BackPlate.stl")
    c2 = cover.copy(); c2.apply_translation([0, W + 10, COVER_T])
    p2 = plate.copy(); p2.apply_translation([0, -W - 10, 0])
    sc = trimesh.Scene({"Body": body, "BottomCover": c2, "BackPlate": p2})
    sc.export(f"{out}/Case_7.5_Plate.3mf")
