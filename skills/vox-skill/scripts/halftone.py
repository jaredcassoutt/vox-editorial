"""Give a transparent cut-out the paper treatment so it sits on the texture.

Two modes:
  halftone  clustered-dot screen, ink on paper. The default. Reads as newsprint.
  duotone   smooth two-tone ramp, no dots. Use when the source is small or the
            subject is a building/object where dots destroy the silhouette.

Alpha is preserved exactly, so the red marker stroke still masks correctly.

    pip install Pillow
    python3 halftone.py cut.png                    # in place, halftone
    python3 halftone.py cut.png out.png --duotone
    python3 halftone.py cut.png out.png --cell 7 --contrast 1.45

Options:
    --duotone         smooth ramp instead of dots
    --cell N          dot cell size in px (default 6). Bigger = coarser.
    --contrast F      pre-screen contrast (default 1.35)
    --gamma F         pre-screen gamma; BELOW 1 lightens, above 1 darkens (default 0.95)
    --size N          resize long edge to N before screening, up OR down (default 900)
    --ink #RRGGBB     dark tone  (default #1A1A1A)
    --paper #RRGGBB   light tone (default #F7F5F1)

Sizing: aim for an on-screen dot pitch near 3px. A subject displayed 500px wide
from a 900px asset is scaled 0.55, so --cell 6 lands at ~3.3px. Upscale small
archive scans to 900 rather than screening them at native size.

The light tone is near-white, NOT the paper colour. The cut-out has to sit a
shade brighter than the texture behind it or the silhouette disappears.
"""

import sys
from PIL import Image, ImageChops, ImageEnhance, ImageOps

CLUSTERED_8 = [
    [24, 10, 12, 26, 35, 47, 49, 37],
    [8,  0,  2,  14, 45, 59, 61, 51],
    [22, 6,  4,  16, 43, 57, 63, 53],
    [30, 20, 18, 28, 33, 41, 55, 39],
    [34, 46, 48, 36, 25, 11, 13, 27],
    [44, 58, 60, 50, 9,  1,  3,  15],
    [42, 56, 62, 52, 23, 7,  5,  17],
    [32, 40, 54, 38, 31, 21, 19, 29],
]


def _hex(s: str) -> tuple[int, int, int]:
    s = s.lstrip("#")
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


def _screen(gray: Image.Image, cell: int) -> Image.Image:
    """Threshold against a tiled clustered-dot matrix scaled to `cell`.

    Clustered-dot (not ordered/Bayer) is what makes this read as newsprint:
    ink pools into growing round dots instead of scattering into noise.
    """
    w, h = gray.size
    m = Image.new("L", (8, 8))
    m.putdata([int((v + 0.5) * 255 / 64) for row in CLUSTERED_8 for v in row])
    tile = m.resize((cell, cell), Image.NEAREST)
    mask = Image.new("L", (w + cell, h + cell))
    for y in range(0, h + cell, cell):
        for x in range(0, w + cell, cell):
            mask.paste(tile, (x, y))
    mask = mask.crop((0, 0, w, h))
    # gray > mask, done in C: subtract clamps at 0, so any positive is "lighter".
    return ImageChops.subtract(gray, mask).point(lambda v: 255 if v > 0 else 0)


def treat(src, dst=None, *, duotone=False, cell=6, contrast=1.35, gamma=0.95,
          size=900, ink="#1A1A1A", paper="#F7F5F1"):
    dst = dst or src
    im = Image.open(src).convert("RGBA")
    # Resize to `size` on the long edge, UP or down. Upscaling a small archive
    # scan before screening is the point: the dot grid hides the softness.
    if size and max(im.size) != size:
        s = size / max(im.size)
        im = im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))),
                       Image.LANCZOS)
    alpha = im.split()[3]

    gray = ImageOps.grayscale(im)
    gray = ImageOps.autocontrast(gray, cutoff=2)
    gray = ImageEnhance.Contrast(gray).enhance(contrast)
    if gamma != 1.0:
        lut = [min(255, int((i / 255) ** gamma * 255)) for i in range(256)]
        gray = gray.point(lut)

    tone = gray if duotone else _screen(gray, cell)
    body = ImageOps.colorize(tone, black=_hex(ink), white=_hex(paper)).convert("RGBA")
    body.putalpha(alpha)
    body.save(dst)
    return body.size


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        print(__doc__)
        raise SystemExit(2)
    src = a[0]
    dst = a[1] if len(a) > 1 and not a[1].startswith("--") else src
    flags = {a[i]: a[i + 1] for i in range(len(a)) if a[i].startswith("--") and i + 1 < len(a)}
    print(treat(
        src, dst,
        duotone="--duotone" in a,
        cell=int(flags.get("--cell", 6)),
        contrast=float(flags.get("--contrast", 1.35)),
        gamma=float(flags.get("--gamma", 0.95)),
        size=int(flags.get("--size", 900)),
        ink=flags.get("--ink", "#1A1A1A"),
        paper=flags.get("--paper", "#F7F5F1"),
    ))
