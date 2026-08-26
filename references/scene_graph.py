"""Build each beat as a SCENE GRAPH - a list of independent layers on depth planes.

Nothing is baked. The ground is an empty sheet of coloured paper; every other
element is its own sprite with its own depth, entrance and drift phase. Depth
drives three things at once: parallax rate against the camera, drift amplitude,
and draw order. That is what makes it read as 3D space rather than a picture with
a copy of itself sliding around on top.

Planes, back to front:
  0.05  ground            (barely moves)
  0.20  newsprint clippings, tape
  0.40  back confetti
  0.60  secondary subject
  0.80  primary subject
  1.00  front confetti     (biggest, fastest)
  1.15  title banner       (nearest to camera)
"""
import random

from paper import PALETTE, banner, clipping, confetti, ground, sticker, tape_strip, word_sprite

W, H = 1080, 1920

GROUNDS = {
 1: (46, 84, 178), 2: (247, 176, 44), 3: (232, 96, 74), 4: (243, 234, 214),
 5: (46, 84, 178), 6: (247, 176, 44), 7: (232, 96, 74), 8: (243, 234, 214),
 9: (46, 84, 178), 10: (247, 176, 44),
}

TITLES = {
 1: "BUILT BY ONE MAN", 2: "2006", 3: "PAGES USED TO END", 4: "INFINITE SCROLL",
 5: "EVERY APP", 6: "IT ASKS YOU", 7: "IT NEVER ASKS", 8: "LIFETIMES",
 9: "HE REGRETS IT", 10: "PUT IT BACK",
}
TITLE_Y = {4: 0.46, 8: 0.72, 10: 0.13}          # most sit at the top; these do not

# sprite index -> (centre x, centre y, height as a fraction of frame, depth)
# sprite index -> (cx, cy, height fraction, depth). Indices are the ones the
# extractor actually produced, read off _qc/sprites.jpg - largest object first.
LAYOUT = {
 1: [(0, 0.36, 0.40, 0.34, 0.58), (1, 0.56, 0.66, 0.44, 0.86)],   # ribbon behind, hand in front
 2: [(0, 0.42, 0.58, 0.40, 0.78), (1, 0.78, 0.74, 0.17, 0.58), (2, 0.20, 0.80, 0.13, 0.62)],
 3: [(1, 0.74, 0.80, 0.19, 1.00)],                                # cards come from REPEAT
 4: [(0, 0.48, 0.56, 0.78, 0.58), (1, 0.68, 0.29, 0.23, 0.88)],
 5: [],
 6: [(0, 0.45, 0.55, 0.34, 0.78), (1, 0.63, 0.80, 0.17, 1.00)],
 7: [(0, 0.45, 0.50, 0.42, 0.58), (1, 0.58, 0.83, 0.22, 0.86)],
 8: [(0, 0.50, 0.85, 0.14, 0.58)],
 9: [(0, 0.50, 0.50, 0.42, 0.58)],
 10:[(0, 0.50, 0.70, 0.30, 0.58), (1, 0.52, 0.42, 0.26, 0.88)],
}

# a big local numeral, its own layer - the crowd beat needs the number to land
WORDS = {8: [("500,000", 0.50, 0.42, 210, (28, 26, 24), 0.80)]}

# beats that repeat one sprite into a grid: (sprite, cols, rows, x0, x1, y0, y1, height)
REPEAT = {
 5: (0, 3, 3, 0.22, 0.78, 0.36, 0.80, 0.16),
 3: (0, 1, 3, 0.50, 0.50, 0.34, 0.76, 0.185),
}

SCREEN_TINT = {5: True}                          # recolour each repeated phone's screen


def _confetti_field(rnd, n, depth_lo, depth_hi, smin, smax, clear_centre=False):
    """Scatter independent accent pieces. The front field keeps out of the middle -
    in the reference art the confetti radiates AROUND the subject, and pieces
    landing on top of a hand read as dirt on the lens."""
    out = []
    kinds = ["triangle", "shard", "zigzag", "ring", "square", "dot", "triangle", "shard"]
    for _ in range(n):
        d = rnd.uniform(depth_lo, depth_hi)
        s = int(rnd.uniform(smin, smax) * (0.7 + 0.6 * d))
        if clear_centre:
            cx = rnd.choice([rnd.uniform(0.03, 0.24), rnd.uniform(0.76, 0.97)])
            cy = rnd.uniform(0.10, 0.94)
        else:
            cx, cy = rnd.uniform(0.05, 0.95), rnd.uniform(0.06, 0.94)
        out.append(dict(img=confetti(rnd.choice(kinds), rnd.choice(PALETTE), s,
                                     seed=rnd.randrange(9999)),
                        cx=cx, cy=cy, depth=d, kind="confetti",
                        spin=rnd.uniform(-14, 14)))
    return out


def build(bid, sprites):
    """sprites: list of RGBA images for this beat, in OBJECTS order."""
    rnd = random.Random(bid * 977)
    g = GROUNDS[bid]
    layers = [dict(img=ground((W, H), g, seed=bid), cx=0.5, cy=0.5, depth=0.05,
                   kind="ground", spin=0)]

    for i in range(rnd.randint(2, 3)):           # newsprint, back plane
        cw = rnd.randint(190, 300)
        layers.append(dict(img=clipping(cw, int(cw * rnd.uniform(0.7, 1.3)), seed=bid * 10 + i),
                           cx=rnd.choice([rnd.uniform(0.06, 0.22), rnd.uniform(0.78, 0.94)]),
                           cy=rnd.uniform(0.14, 0.88), depth=rnd.uniform(0.18, 0.28),
                           kind="clip", spin=rnd.uniform(-8, 8)))
    for i in range(2):                           # tape, back plane
        layers.append(dict(img=tape_strip(rnd.randint(150, 230), rnd.randint(52, 76),
                                          rnd.choice([-30, -14, 18, 34]), seed=bid * 20 + i),
                           cx=rnd.uniform(0.08, 0.92), cy=rnd.uniform(0.08, 0.92),
                           depth=rnd.uniform(0.16, 0.24), kind="tape", spin=0))

    layers += _confetti_field(rnd, 11, 0.34, 0.48, 34, 60)      # behind the subject

    if bid in REPEAT:
        sp, cols, rows, x0, x1, y0, y1, hh = REPEAT[bid]
        base = sprites[sp]
        for r in range(rows):
            for c in range(cols):
                cx = x0 if cols == 1 else x0 + (x1 - x0) * c / max(1, cols - 1)
                cy = y0 if rows == 1 else y0 + (y1 - y0) * r / max(1, rows - 1)
                img = base
                if SCREEN_TINT.get(bid):
                    img = _tint_screen(base, PALETTE[(r * cols + c) % len(PALETTE)])
                layers.append(dict(img=img, cx=cx, cy=cy, h=hh,
                                   depth=0.62 + 0.06 * r + 0.02 * c, kind="obj",
                                   spin=rnd.uniform(-4, 4)))
    for sp, cx, cy, hh, dep in LAYOUT[bid]:
        if sp < len(sprites):
            layers.append(dict(img=sprites[sp], cx=cx, cy=cy, h=hh, depth=dep,
                               kind="obj", spin=rnd.uniform(-3, 3)))

    layers += _confetti_field(rnd, 10, 0.92, 1.06, 46, 80, clear_centre=True)      # in front of the subject

    for txt, cx, cy, sz, col, dep in WORDS.get(bid, []):
        layers.append(dict(img=word_sprite(txt, sz, col, seed=bid), cx=cx, cy=cy,
                           depth=dep, kind="obj", spin=rnd.uniform(-2, 2)))

    # 0.78 rather than 0.86: the title sits nearest the camera, so it grows the most
    # under the push, and a headline whose last letter walks off frame is unforgivable
    ttl = banner(TITLES[bid], int(W * 0.78), seed=bid * 5)
    layers.append(dict(img=ttl, cx=0.5, cy=TITLE_Y.get(bid, 0.13), depth=1.15,
                       kind="title", spin=0))
    return layers


def _tint_screen(phone, colour):
    """Recolour just the screen, so nine copies read as nine separate objects.

    The screen is found rather than assumed: it is the bright, low-saturation
    region inside the phone's silhouette. Filling a guessed rectangle painted over
    the phone's body too.
    """
    import numpy as np
    from PIL import Image, ImageFilter
    im = phone.copy()
    a = np.asarray(im).astype(np.int16)
    rgb, al = a[..., :3], a[..., 3]
    L = rgb.mean(axis=2)
    sat = rgb.max(axis=2) - rgb.min(axis=2)
    screen = (al > 200) & (L > 178) & (sat < 46)
    m = Image.fromarray((screen * 255).astype(np.uint8))
    m = m.filter(ImageFilter.MinFilter(5)).filter(ImageFilter.MaxFilter(3))
    screen = np.asarray(m) > 127
    if screen.sum() < 500:
        return im
    out = a.copy()
    tint = np.array(colour, dtype=np.int16)
    shade = (L[screen] / 255.0)[:, None]
    out[..., :3][screen] = (tint * (0.55 + 0.45 * shade)).astype(np.int16)
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGBA")
