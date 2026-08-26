"""Local paper-element factory - every piece is its own RGBA sprite.

Nothing here is baked into a background. The ground is generated blank, and the
confetti, tape, clippings and title banner are each returned as separate
transparent layers so the compositor can put them on different depth planes and
move them independently.

Drawing these locally rather than generating them also means the title text is
exactly right every time, and there is an unlimited supply of confetti.
"""
import math, random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

FONTS = Path.home() / ".claude/skills/editorial-carousel/references/fonts"
ANTON = str(FONTS / "Anton.ttf")
FIGTREE = str(FONTS / "Figtree.ttf")

PALETTE = [(232, 76, 61), (247, 176, 44), (58, 96, 191), (32, 160, 138),
           (233, 96, 140), (124, 88, 176), (241, 130, 62)]
WHITE = (255, 255, 255, 255)


def grain(im, amount=9, seed=0):
    """Matte paper tooth. Without it every flat fill reads as digital."""
    rnd = random.Random(seed)
    w, h = im.size
    n = Image.new("L", (w // 2, h // 2))
    n.putdata([128 + rnd.randint(-amount, amount) for _ in range(n.width * n.height)])
    n = n.resize((w, h), Image.BILINEAR).filter(ImageFilter.GaussianBlur(0.4))
    a = im.convert("RGB").split()
    out = []
    for ch in a:
        out.append(Image.blend(ch, Image.composite(ch, ch, n), 0.0))
    base = im.convert("RGBA")
    ov = Image.merge("RGBA", (n, n, n, Image.new("L", (w, h), 26)))
    return Image.alpha_composite(base, ov)


def ground(size, colour, seed=0):
    """A blank sheet of coloured paper. Nothing on it."""
    im = Image.new("RGBA", size, colour + (255,))
    im = grain(im, 10, seed)
    d = ImageDraw.Draw(im)
    rnd = random.Random(seed + 7)
    for _ in range(140):                       # faint fibre flecks
        x, y = rnd.randrange(size[0]), rnd.randrange(size[1])
        v = rnd.randint(-14, 14)
        c = tuple(max(0, min(255, ch + v)) for ch in colour)
        d.ellipse([x, y, x + rnd.randint(2, 6), y + rnd.randint(2, 5)], fill=c + (60,))
    return im


def _torn_mask(size, seed=0, amp=None, sides=("top", "bottom")):
    """A rectangle whose chosen sides are ripped rather than cut."""
    w, h = size
    amp = amp or max(6, h // 22)
    rnd = random.Random(seed)
    m = Image.new("L", size, 0)
    d = ImageDraw.Draw(m)
    def edge(n, base, horizontal=True):
        pts = []
        step = (w if horizontal else h) / n
        for i in range(n + 1):
            j = i * step
            off = rnd.randint(-amp, amp) + rnd.choice([0, 0, amp // 2])
            pts.append((j, base + off) if horizontal else (base + off, j))
        return pts
    top = edge(26, 0) if "top" in sides else [(0, 0), (w, 0)]
    bot = edge(26, h) if "bottom" in sides else [(w, h), (0, h)]
    d.polygon(top + list(reversed(bot)) if "bottom" in sides else top + bot, fill=255)
    return m.filter(ImageFilter.GaussianBlur(0.6))


def sticker(layer, border=14, shadow=True, blur=3):
    """Thick white sticker rim plus a soft real paper drop shadow."""
    pad = border + (26 if shadow else 0)
    big = Image.new("RGBA", (layer.width + pad * 2, layer.height + pad * 2), (0, 0, 0, 0))
    al = layer.split()[3]
    rim = al.filter(ImageFilter.MaxFilter(3))
    for _ in range(max(1, border // 2)):
        rim = rim.filter(ImageFilter.MaxFilter(3))
    rim = rim.point(lambda v: 255 if v > 90 else 0)
    out = Image.new("RGBA", big.size, (0, 0, 0, 0))
    if shadow:
        sh = Image.new("RGBA", big.size, (0, 0, 0, 0))
        sh.paste((40, 30, 15, 105), (pad + 7, pad + 11), rim)
        out = Image.alpha_composite(out, sh.filter(ImageFilter.GaussianBlur(blur * 3)))
    white = Image.new("RGBA", big.size, (0, 0, 0, 0))
    white.paste(WHITE, (pad, pad), rim)
    out = Image.alpha_composite(out, white)
    out.alpha_composite(layer, (pad, pad))
    return out.crop(out.getbbox())


def banner(text, width, colours=None, seed=0, size=None, tape=True):
    """Torn white paper strip with big condensed all-caps set INTO it."""
    colours = colours or PALETTE
    size = size or int(width * 0.135)
    f = ImageFont.truetype(ANTON, size)
    tmp = ImageDraw.Draw(Image.new("RGB", (8, 8)))

    def drawn_width(font):
        return sum(tmp.textlength(ch, font=font) for ch in text)

    while drawn_width(f) > width * 0.76 and size > 24:
        size -= 4
        f = ImageFont.truetype(ANTON, size)
    tw = drawn_width(f)
    h = int(size * 2.05)
    strip = Image.new("RGBA", (width, h), (0, 0, 0, 0))
    paper = Image.new("RGBA", (width, h), (253, 252, 248, 255))
    paper = grain(paper, 7, seed)
    strip.paste(paper, (0, 0), _torn_mask((width, h), seed))
    d = ImageDraw.Draw(strip)
    x = (width - tw) / 2
    y = (h - size * 1.24) / 2
    rnd = random.Random(seed + 3)
    for i, ch in enumerate(text):
        c = colours[i % len(colours)] if len(colours) > 1 else colours[0]
        d.text((x, y + rnd.randint(-2, 2)), ch, font=f, fill=c + (255,))
        x += d.textlength(ch, font=f)
    if tape:
        for corner in (0, 1):
            t = tape_strip(int(width * 0.17), int(h * 0.42), rnd.choice([-28, 24]), seed + corner)
            strip.alpha_composite(t, (-14 if corner == 0 else width - t.width + 14,
                                      -12 if corner == 0 else h - t.height + 10))
    return strip


def tape_strip(w, h, angle=0, seed=0, dots=True):
    """Halftone-dot washi tape."""
    im = Image.new("RGBA", (w, h), (250, 246, 232, 232))
    d = ImageDraw.Draw(im)
    if dots:
        step = max(6, h // 7)
        for y in range(step // 2, h, step):
            for x in range(step // 2 + (step // 2 if (y // step) % 2 else 0), w, step):
                d.ellipse([x - step * 0.22, y - step * 0.22, x + step * 0.22, y + step * 0.22],
                          fill=(46, 42, 38, 210))
    rnd = random.Random(seed)
    m = Image.new("L", (w, h), 255)
    md = ImageDraw.Draw(m)
    for x in range(0, w, 5):                  # nibbled tape ends
        md.rectangle([x, 0, x + 5, rnd.randint(0, 3)], fill=0)
        md.rectangle([x, h - rnd.randint(0, 3), x + 5, h], fill=0)
    im.putalpha(Image.composite(im.split()[3], Image.new("L", (w, h), 0), m))
    return im.rotate(angle, expand=True, resample=Image.BICUBIC)


def clipping(w, h, seed=0):
    """A torn newspaper scrap carrying fine printed body text."""
    rnd = random.Random(seed)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    paper = Image.new("RGBA", (w, h), (240, 236, 224, 255))
    paper = grain(paper, 8, seed)
    im.paste(paper, (0, 0), _torn_mask((w, h), seed, sides=("top", "bottom")))
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype(FIGTREE, max(7, h // 26))
    y = h * 0.12
    while y < h * 0.9:
        x = w * 0.08
        while x < w * 0.9:
            wlen = rnd.randint(14, 46)
            d.rectangle([x, y, min(x + wlen, w * 0.92), y + max(2, h // 90)],
                        fill=(64, 60, 56, 220))
            x += wlen + rnd.randint(6, 12)
        y += max(6, h / 22)
    return im


def confetti(kind, colour, s, seed=0, border=True):
    """One geometric paper accent - its own sprite, never a group."""
    pad = 10
    im = Image.new("RGBA", (s + pad * 2, s + pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = colour + (255,)
    if kind == "triangle":
        d.polygon([(pad, pad + s), (pad + s / 2, pad), (pad + s, pad + s)], fill=c)
    elif kind == "shard":
        d.polygon([(pad, pad), (pad + s * 0.62, pad + s * 0.16), (pad + s * 0.3, pad + s)], fill=c)
    elif kind == "square":
        d.rectangle([pad, pad, pad + s * 0.8, pad + s * 0.8], fill=c)
    elif kind == "ring":
        d.ellipse([pad, pad, pad + s, pad + s], outline=c, width=max(3, s // 5))
    elif kind == "dot":
        d.ellipse([pad, pad, pad + s * 0.7, pad + s * 0.7], fill=c)
    else:                                     # zigzag - flat and wide, not a letter
        n, step = 5, s / 5
        pts = [(pad + i * step, pad + (0 if i % 2 else s * 0.34)) for i in range(n + 1)]
        d.line(pts, fill=c, width=max(4, s // 6), joint="curve")
    im = im.crop(im.getbbox() or (0, 0, s, s))
    return sticker(im, border=max(3, s // 12), shadow=True, blur=1) if border else im


def word_sprite(text, size, colour=(28, 26, 24), seed=0):
    """A single big word or numeral as its own white-bordered paper cutout."""
    f = ImageFont.truetype(ANTON, size)
    tmp = ImageDraw.Draw(Image.new("RGB", (8, 8)))
    w = int(tmp.textlength(text, font=f)) + size // 3
    im = Image.new("RGBA", (w, int(size * 1.35)), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((size // 6, 0), text, font=f, fill=colour + (255,))
    im = im.crop(im.getbbox())
    return sticker(im, border=max(8, size // 14), shadow=True, blur=3)
