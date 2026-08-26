"""Kinetic overlay primitives for vox-style beats.

Each builder renders a PNG sequence with a transparent background, which
`composite()` lays over a finished beat clip with ffmpeg. All local, no API cost.

Primitives
  counter()        a number ticking up fast to a target, with easing
  typewriter()     characters typing on with a blinking caret (short phrases only)
  circle_word()    a hand-drawn ellipse stroking on around a word
  marker_highlight() a highlighter pen sweeping behind a word
  life_grid()      a grid of boxes filling in and colour-coding by category

Every primitive takes `step_fps` (default 12): graphic motion is quantized to 12fps
steps inside a smooth 30fps edit, which is what makes it read as built rather than
rendered. Pass step_fps=None for smooth motion.
"""
from pathlib import Path
import math, os, subprocess

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ED = Path.home() / ".claude/skills/editorial-carousel/references"
FIG = str(ED / "fonts/Figtree.ttf")
ANTON = str(ED / "fonts/Anton.ttf")


RED = (214, 40, 34)          # house accent - red, not orange
INK = (22, 22, 24)
HILITE = (255, 214, 64)


def anchor_box(element_png, centre, scale=1.0, pad=0):
    """Where an element ACTUALLY sits on the canvas.

    Annotations must be anchored to a measured element, never to hand-typed pixels -
    that is what makes a circle or a highlight miss its target. Returns (x, y, w, h)
    of the element's opaque content, in canvas coordinates.
    """
    im = Image.open(element_png).convert("RGBA")
    bb = im.split()[3].getbbox() or (0, 0, im.width, im.height)
    w, h = (bb[2] - bb[0]) * scale, (bb[3] - bb[1]) * scale
    ox = (bb[0] - im.width / 2 + (bb[2] - bb[0]) / 2) * scale
    oy = (bb[1] - im.height / 2 + (bb[3] - bb[1]) / 2) * scale
    cx, cy = centre[0] + ox, centre[1] + oy
    return (cx - w / 2 - pad, cy - h / 2 - pad, w + pad * 2, h + pad * 2)


def stack_zones(canvas=(1080, 1920), top=0.16, bottom=0.74, gap=28):
    """Non-overlapping horizontal bands. Place each element in its own zone so text can
    never land on top of a figure - the most common and most obvious layout failure."""
    W, H = canvas
    y0, y1 = H * top, H * bottom
    def zones(n):
        band = (y1 - y0 - gap * (n - 1)) / n
        return [(W / 2, y0 + i * (band + gap) + band / 2, band) for i in range(n)]
    return zones


def _font(path, size, var=None):
    f = ImageFont.truetype(path, size)
    if var:
        try: f.set_variation_by_name(var)
        except Exception: pass
    return f


def _quant(i, fps, step_fps):
    """Hold each value for several frames so graphic motion steps at step_fps."""
    if not step_fps: return i
    step = max(1, round(fps / step_fps))
    return (i // step) * step


def _ease_out(t):            # fast start, soft landing - right for counters
    return 1 - (1 - t) ** 3


def _seq(out_dir):
    p = Path(out_dir); p.mkdir(parents=True, exist_ok=True)
    for old in p.glob("*.png"): old.unlink()
    return p


# ────────────────────────────── 1. counter ──────────────────────────────
def counter(out_dir, target, dur=1.4, fps=30, size=(1080, 620), font_size=300,
            color=(255, 255, 255), accent=None, prefix="", suffix="",
            step_fps=12, comma=True, hold=0.6):
    """A number ticking up 0 -> target fast, then holding."""
    p = _seq(out_dir)
    n_anim, n_hold = int(dur * fps), int(hold * fps)
    f = _font(ANTON, font_size)
    for i in range(n_anim + n_hold):
        qi = _quant(min(i, n_anim), fps, step_fps)
        t = min(1.0, qi / max(1, n_anim))
        val = int(round(target * _ease_out(t)))
        txt = f"{prefix}{val:,}{suffix}" if comma else f"{prefix}{val}{suffix}"
        im = Image.new("RGBA", size, (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        w = d.textlength(txt, font=f)
        d.text(((size[0] - w) / 2, 40), txt, font=f,
               fill=(accent if (accent and i >= n_anim) else color) + (255,) if len(
                   (accent if (accent and i >= n_anim) else color)) == 3 else None)
        im.save(p / f"{i:04d}.png")
    return p, fps


# ──────────────────────────── 2. typewriter ────────────────────────────
def typewriter(out_dir, text, cps=22, fps=30, size=(1080, 300), font_size=84,
               color=(255, 255, 255), caret=True, step_fps=None, hold=1.0,
               align="center"):
    """Characters typing on with a blinking caret. SHORT phrases and headings only."""
    p = _seq(out_dir)
    n_type = int(len(text) / cps * fps)
    n_hold = int(hold * fps)
    f = _font(FIG, font_size, "ExtraBold")
    for i in range(n_type + n_hold):
        qi = _quant(i, fps, step_fps)
        shown = min(len(text), int(round(qi / max(1, n_type) * len(text))))
        s = text[:shown]
        im = Image.new("RGBA", size, (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        w = d.textlength(s, font=f)
        x = (size[0] - w) / 2 if align == "center" else 60
        d.text((x, 40), s, font=f, fill=color + (255,))
        if caret and (i // max(1, fps // 3)) % 2 == 0:
            cx = x + w + 8
            d.rectangle([cx, 48, cx + 10, 48 + font_size], fill=color + (235,))
        im.save(p / f"{i:04d}.png")
    return p, fps


# ─────────────────────────── 3. circle a word ──────────────────────────
def circle_word(out_dir, box, dur=0.6, fps=30, color=RED, width=9,
                step_fps=12, hold=1.2, wobble=True, canvas=(1080, 1920)):
    """Hand-drawn ellipse stroking on around `box` = (x, y, w, h) of the word."""
    p = _seq(out_dir)
    x, y, w, h = box
    cx, cy = x + w / 2, y + h / 2
    rx, ry = w * 0.62, h * 0.85
    n_anim, n_hold = int(dur * fps), int(hold * fps)
    for i in range(n_anim + n_hold):
        qi = _quant(min(i, n_anim), fps, step_fps)
        prog = min(1.0, qi / max(1, n_anim))
        im = Image.new("RGBA", canvas, (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        steps = max(2, int(prog * 74))
        pts = []
        for k in range(steps + 1):
            a = -math.pi / 2 + (k / 74) * 2 * math.pi * 1.06     # slight overshoot
            wob = (math.sin(a * 3) * 4 if wobble else 0)
            pts.append((cx + math.cos(a) * (rx + wob), cy + math.sin(a) * (ry + wob)))
        if len(pts) > 1:
            d.line(pts, fill=color + (255,), width=width, joint="curve")
        im.save(p / f"{i:04d}.png")
    return p, fps


# ──────────────────────── 4. marker highlight ──────────────────────────
def marker_highlight(out_dir, box, dur=0.45, fps=30, color=(255, 214, 64),
                     step_fps=12, hold=1.4, canvas=(1080, 1920), alpha=58):
    """A highlighter sweeping left-to-right behind a word. Composite UNDER the text."""
    p = _seq(out_dir)
    x, y, w, h = box
    n_anim, n_hold = int(dur * fps), int(hold * fps)
    for i in range(n_anim + n_hold):
        qi = _quant(min(i, n_anim), fps, step_fps)
        prog = min(1.0, qi / max(1, n_anim))
        im = Image.new("RGBA", canvas, (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        cw = int(w * prog)
        if cw > 2:
            # slightly ragged marker edges, thicker in the middle like a real nib
            top = y + h * 0.16
            d.rounded_rectangle([x, top, x + cw, top + h * 0.72],
                                radius=int(h * 0.14), fill=color + (alpha,))
            d.rounded_rectangle([x, top + h * 0.10, x + cw, top + h * 0.60],
                                radius=int(h * 0.10), fill=color + (min(255, alpha + 18),))
        im.save(p / f"{i:04d}.png")
    return p, fps


# ───────────────────────────── 5. life grid ────────────────────────────
def life_grid(out_dir, cols=40, rows=25, fps=30, canvas=(1080, 1400), pad=70,
              base=(255, 255, 255, 38), groups=None, per_frame=42, step_fps=12,
              hold=1.2, gap=4, label_font=44):
    """A grid of boxes filling in, colour-coded by group.

    groups = [(count, (r,g,b), "label"), ...] filled in order. Classic use: one box per
    week of a life (52 x 90), or per day of a year, colour-coded by how it is spent.
    """
    p = _seq(out_dir)
    total = cols * rows
    groups = groups or [(total, (201, 153, 46), "")]
    cw = (canvas[0] - pad * 2 - gap * (cols - 1)) / cols
    ch = (canvas[1] - pad * 2 - gap * (rows - 1)) / rows
    colours = []
    for count, col, _ in groups:
        colours += [col] * count
    colours = colours[:total]
    n_anim = max(1, int(math.ceil(len(colours) / per_frame)))
    for i in range(n_anim + int(hold * fps)):
        qi = _quant(min(i, n_anim), fps, step_fps)
        shown = min(len(colours), int(qi * per_frame))
        im = Image.new("RGBA", canvas, (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        for idx in range(total):
            r, c = divmod(idx, cols)
            x0 = pad + c * (cw + gap); y0 = pad + r * (ch + gap)
            fill = (colours[idx] + (255,)) if idx < shown else base
            d.rectangle([x0, y0, x0 + cw, y0 + ch], fill=fill)
        im.save(p / f"{i:04d}.png")
    return p, fps


# ───────────────────────────── compositing ─────────────────────────────
def composite(base_video, out_video, layers, fps=30):
    """layers = [(seq_dir, start_seconds, x, y), ...] laid over base_video in order."""
    inputs, fc, cur = ["-i", str(base_video)], [], "0:v"
    for i, (seq, start, x, y) in enumerate(layers):
        inputs += ["-framerate", str(fps), "-itsoffset", f"{start}", "-i",
                   str(Path(seq) / "%04d.png")]
        nxt = f"v{i}"
        fc.append(f"[{cur}][{i+1}:v]overlay=x={x}:y={y}:eof_action=pass"
                  f":enable='gte(t,{start})'[{nxt}]")
        cur = nxt
    cmd = ["ffmpeg", "-y", "-loglevel", "error"] + inputs + [
        "-filter_complex", ";".join(fc), "-map", f"[{cur}]"]
    # keep the base audio if it has any
    probe = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a",
                            "-show_entries", "stream=index", "-of", "csv=p=0",
                            str(base_video)], capture_output=True, text=True).stdout.strip()
    if probe:
        cmd += ["-map", "0:a", "-c:a", "copy"]
    cmd += ["-c:v", "libx264", "-preset", "medium", "-crf", "18",
            "-pix_fmt", "yuv420p", str(out_video)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(r.stderr[-700:])
    return out_video


# ═══════════════════════ grid-editorial style ═══════════════════════
# Light graph-paper ground, halftone cutouts with a coloured OFFSET shadow
# (not a white sticker border), bold black type, typewriter for quotes.

def grid_background(out_path, size=(1080, 1920), bg=(226, 226, 224), line=(255, 255, 255),
                    cell=118, grain=13, vignette=0.30, line_w=3):
    """The plain grid ground: soft grey paper, white graph lines, grain, corner vignette."""
    import random
    W, H = size
    im = Image.new("RGB", size, bg); d = ImageDraw.Draw(im)
    for x in range(0, W + cell, cell):
        d.line([(x, 0), (x, H)], fill=line, width=line_w)
    for y in range(0, H + cell, cell):
        d.line([(0, y), (W, y)], fill=line, width=line_w)
    # radial darkening toward the edges
    vg = Image.new("L", (W, H), 0); vd = ImageDraw.Draw(vg)
    steps = 60
    for i in range(steps):
        t = i / steps
        vd.ellipse([-W * .35 + W * .55 * t, -H * .25 + H * .45 * t,
                    W * 1.35 - W * .55 * t, H * 1.25 - H * .45 * t],
                   fill=int(255 * (1 - t) ** 2))
    vg = vg.filter(ImageFilter.GaussianBlur(90))
    dark = Image.new("RGB", size, (120, 120, 122))
    im = Image.composite(im, Image.blend(im, dark, vignette), vg)
    px = im.load()
    rnd = random.Random(7)
    for _ in range(int(W * H * grain / 1000)):
        x, y = rnd.randrange(W), rnd.randrange(H)
        v = rnd.randint(-16, 16)
        r, g, b = px[x, y]
        px[x, y] = (max(0, min(255, r + v)), max(0, min(255, g + v)), max(0, min(255, b + v)))
    im.save(out_path)
    return out_path


def offset_shadow(src, dst, colour=RED, dx=26, dy=18, halftone=True,
                  max_side=1500, grow=16):
    """The reference look: greyscale halftone cutout with a solid coloured silhouette
    offset behind it. Replaces the white sticker border for the grid-editorial style."""
    from PIL import ImageOps
    im = Image.open(src).convert("RGBA")
    im.thumbnail((max_side, max_side), Image.LANCZOS)
    a = im.split()[3].point(lambda v: 255 if v > 40 else 0)
    rgb = Image.merge("RGB", im.split()[:3])
    if halftone:
        g = ImageOps.grayscale(rgb)
        g = ImageOps.autocontrast(g, cutoff=1)
        # coarse dot screen so it reads as printed
        small = g.resize((max(1, g.width // 3), max(1, g.height // 3)), Image.NEAREST)
        g = small.resize(g.size, Image.NEAREST)
        rgb = Image.merge("RGB", (g, g, g))
    pad = max(abs(dx), abs(dy)) + grow + 20
    W, H = im.width + pad * 2, im.height + pad * 2
    sil = Image.new("L", (W, H), 0); sil.paste(a, (pad + dx, pad + dy))
    if grow:
        sil = sil.filter(ImageFilter.GaussianBlur(grow * .55)).point(lambda v: 255 if v > 30 else 0)
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    out.paste(Image.new("RGBA", (W, H), colour + (255,)), (0, 0), sil)
    body = Image.new("RGBA", im.size, (0, 0, 0, 0)); body.paste(rgb.convert("RGBA"), (0, 0), a)
    out.alpha_composite(body, (pad, pad))
    bb = out.split()[3].getbbox()
    if bb: out = out.crop(bb)
    out.save(dst)
    return out.size


# ───────────────────────── spring pop-in ─────────────────────────
def _spring(t, damping=11.0, stiffness=180.0):
    """Underdamped spring 0->1 with a visible overshoot."""
    if t <= 0: return 0.0
    import math as _m
    zeta = damping / (2 * _m.sqrt(stiffness))
    wn = _m.sqrt(stiffness)
    if zeta >= 1: return 1 - _m.exp(-wn * t) * (1 + wn * t)
    wd = wn * _m.sqrt(1 - zeta * zeta)
    return 1 - _m.exp(-zeta * wn * t) * (_m.cos(wd * t) + (zeta * wn / wd) * _m.sin(wd * t))


def spring_pop(out_dir, element_png, dur=0.9, fps=30, canvas=(1080, 1920), centre=(540, 960),
               start_scale=0.55, rise=90, step_fps=None, hold=1.0, damping=11.0):
    """Pop an element in with a spring overshoot: scales up past 1 and settles."""
    p = _seq(out_dir)
    el = Image.open(element_png).convert("RGBA")
    n_anim, n_hold = int(dur * fps), int(hold * fps)
    for i in range(n_anim + n_hold):
        qi = _quant(i, fps, step_fps)
        s = _spring(min(qi, n_anim) / fps, damping)
        sc = start_scale + (1 - start_scale) * s
        dy = rise * (1 - s)
        w, h = max(1, int(el.width * sc)), max(1, int(el.height * sc))
        im = Image.new("RGBA", canvas, (0, 0, 0, 0))
        im.alpha_composite(el.resize((w, h), Image.LANCZOS),
                           (int(centre[0] - w / 2), int(centre[1] - h / 2 + dy)))
        im.save(p / f"{i:04d}.png")
    return p, fps


# ───────────────────────── burn away ─────────────────────────
def burn_away(out_dir, element_png, dur=1.6, fps=30, canvas=None, pos=(0, 0),
              direction="up", ember=(255, 138, 24), char=(28, 22, 20), hold=0.4):
    """Burn-up effect: the element is eaten away behind a ragged glowing edge."""
    import random
    el = Image.open(element_png).convert("RGBA")
    canvas = canvas or el.size
    p = _seq(out_dir)
    W, H = el.size
    rnd = random.Random(11)
    noise = Image.new("L", (W // 6 or 1, H // 6 or 1))
    noise.putdata([rnd.randint(0, 255) for _ in range(noise.width * noise.height)])
    noise = noise.resize((W, H), Image.BICUBIC).filter(ImageFilter.GaussianBlur(7))
    grad = Image.new("L", (W, H)); gd = ImageDraw.Draw(grad)
    for y in range(H):
        v = int(255 * (1 - y / H)) if direction == "up" else int(255 * (y / H))
        gd.line([(0, y), (W, y)], fill=v)
    field = Image.blend(grad, noise, 0.42)
    n = int(dur * fps)
    for i in range(n + int(hold * fps)):
        t = min(1.0, i / max(1, n))
        thr = int(255 * t)
        keep = field.point(lambda v: 255 if v > thr else 0)
        edge = field.point(lambda v: 255 if thr < v <= thr + 26 else 0)
        glow = field.point(lambda v: 255 if thr - 14 < v <= thr + 40 else 0)
        im = Image.new("RGBA", canvas, (0, 0, 0, 0))
        body = Image.new("RGBA", el.size, (0, 0, 0, 0))
        body.paste(el, (0, 0), Image.composite(el.split()[3], Image.new("L", el.size, 0), keep))
        charl = Image.new("RGBA", el.size, char + (235,))
        body.paste(charl, (0, 0), Image.composite(el.split()[3], Image.new("L", el.size, 0), edge))
        emb = Image.new("RGBA", el.size, ember + (255,))
        gmask = Image.composite(el.split()[3], Image.new("L", el.size, 0), glow)
        emb.putalpha(gmask.filter(ImageFilter.GaussianBlur(5)))
        body.alpha_composite(emb)
        im.alpha_composite(body, pos)
        im.save(p / f"{i:04d}.png")
    return p, fps


# ──────────────────── dashed route + arrow lines ────────────────────
def _catmull(points, samples=26):
    """Smooth a polyline into a rounded trail path (Catmull-Rom)."""
    if len(points) < 3: return list(points)
    pts = [points[0]] + list(points) + [points[-1]]
    out = []
    for i in range(len(pts) - 3):
        p0, p1, p2, p3 = pts[i], pts[i+1], pts[i+2], pts[i+3]
        for s in range(samples):
            t = s / samples; t2, t3 = t*t, t*t*t
            out.append((
                0.5*((2*p1[0]) + (-p0[0]+p2[0])*t + (2*p0[0]-5*p1[0]+4*p2[0]-p3[0])*t2 + (-p0[0]+3*p1[0]-3*p2[0]+p3[0])*t3),
                0.5*((2*p1[1]) + (-p0[1]+p2[1])*t + (2*p0[1]-5*p1[1]+4*p2[1]-p3[1])*t2 + (-p0[1]+3*p1[1]-3*p2[1]+p3[1])*t3)))
    out.append(points[-1])
    return out


def dashed_route(out_dir, points, dur=1.6, fps=30, canvas=(1080, 1920), colour=RED,
                 width=8, dash=26, gap=18, step_fps=12, hold=1.2, arrow=False,
                 rounded=False):
    """Draw a line on between points.

    rounded=True smooths the polyline into a curved trail path (a travel route);
    rounded=False keeps hard editorial angles. Set dash to a huge number for a solid line.
    """
    p = _seq(out_dir)
    src = _catmull(points) if rounded and len(points) > 2 else list(points)
    # densify into a polyline we can reveal progressively
    pts = []
    for i in range(len(src) - 1):
        (x0, y0), (x1, y1) = src[i], src[i + 1]
        steps = max(2, int(math.hypot(x1 - x0, y1 - y0) / 4))
        for s in range(steps):
            u = s / steps
            pts.append((x0 + (x1 - x0) * u, y0 + (y1 - y0) * u))
    pts.append(src[-1])
    n_anim, n_hold = int(dur * fps), int(hold * fps)
    for i in range(n_anim + n_hold):
        qi = _quant(min(i, n_anim), fps, step_fps)
        prog = min(1.0, qi / max(1, n_anim))
        im = Image.new("RGBA", canvas, (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        shown = pts[:max(2, int(len(pts) * prog))]
        # walk the polyline laying dashes
        run, drawing, seg = 0.0, True, []
        for k in range(1, len(shown)):
            seg.append(shown[k - 1])
            run += math.hypot(shown[k][0] - shown[k - 1][0], shown[k][1] - shown[k - 1][1])
            if (drawing and run >= dash) or ((not drawing) and run >= gap):
                if drawing and len(seg) > 1:
                    d.line(seg, fill=colour + (255,), width=width, joint="curve")
                    for _e in (seg[0], seg[-1]):
                        d.ellipse([_e[0]-width/2, _e[1]-width/2, _e[0]+width/2, _e[1]+width/2], fill=colour+(255,))
                seg = [shown[k]]; run = 0.0; drawing = not drawing
        if drawing and len(seg) > 1:
            d.line(seg, fill=colour + (255,), width=width, joint="curve")
            for _e in (seg[0], seg[-1]):
                d.ellipse([_e[0]-width/2, _e[1]-width/2, _e[0]+width/2, _e[1]+width/2], fill=colour+(255,))
        if arrow and prog > 0.985 and len(shown) > 3:
            (ax, ay), (bx, by) = shown[-4], shown[-1]
            ang = math.atan2(by - ay, bx - ax); L = width * 4.2
            d.polygon([(bx, by),
                       (bx - L * math.cos(ang - .42), by - L * math.sin(ang - .42)),
                       (bx - L * math.cos(ang + .42), by - L * math.sin(ang + .42))],
                      fill=colour + (255,))
        im.save(p / f"{i:04d}.png")
    return p, fps


def arrow_line(out_dir, start, end, **kw):
    """A single straight line that draws on and lands an arrowhead."""
    kw.setdefault("arrow", True)
    return dashed_route(out_dir, [start, end], **kw)


def solid_line(out_dir, points, **kw):
    """Solid (undashed) connector; same signature as dashed_route."""
    kw.setdefault("dash", 10 ** 6); kw.setdefault("gap", 0)
    return dashed_route(out_dir, points, **kw)


# ═══════════════════════════ animated charts ═══════════════════════════
# Editorial, flat, no 3D, no gridlines unless asked. Values animate in with the
# same easing language as the rest of the kit.

def bar_chart(out_dir, data, dur=1.5, fps=30, canvas=(1080, 1100), colour=RED,
              base=(40, 40, 44), label_col=(28, 28, 30), step_fps=12, hold=1.4,
              pad=90, bar_gap=28, show_values=True, suffix="", horizontal=False):
    """data = [(label, value), ...] bars growing in with a soft landing."""
    p = _seq(out_dir)
    W, H = canvas
    vmax = max(v for _, v in data) or 1
    lf = _font(FIG, 40, "SemiBold"); vf = _font(ANTON, 56)
    n_anim, n_hold = int(dur * fps), int(hold * fps)
    n = len(data)
    for i in range(n_anim + n_hold):
        im = Image.new("RGBA", canvas, (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        for k, (lab, val) in enumerate(data):
            qi = _quant(max(0, min(i, n_anim) - k * 3), fps, step_fps)
            t = _ease_out(min(1.0, qi / max(1, n_anim - k * 3 or 1)))
            col = colour if k == 0 or n <= 2 else base
            if horizontal:
                bh = (H - pad * 2 - bar_gap * (n - 1)) / n
                y0 = pad + k * (bh + bar_gap)
                full = (W - pad * 2 - 240)
                d.rectangle([pad + 220, y0, pad + 220 + full * (val / vmax) * t, y0 + bh],
                            fill=col + (255,))
                d.text((pad, y0 + bh * .28), lab, font=lf, fill=label_col + (255,))
                if show_values:
                    d.text((pad + 232 + full * (val / vmax) * t, y0 + bh * .12),
                           f"{int(val*t):,}{suffix}", font=vf, fill=col + (255,))
            else:
                bw = (W - pad * 2 - bar_gap * (n - 1)) / n
                x0 = pad + k * (bw + bar_gap)
                full = H - pad * 2 - 120
                bh = full * (val / vmax) * t
                d.rectangle([x0, H - pad - 90 - bh, x0 + bw, H - pad - 90], fill=col + (255,))
                tw = d.textlength(lab, font=lf)
                d.text((x0 + bw / 2 - tw / 2, H - pad - 74), lab, font=lf, fill=label_col + (255,))
                if show_values:
                    s = f"{int(val*t):,}{suffix}"
                    sw = d.textlength(s, font=vf)
                    d.text((x0 + bw / 2 - sw / 2, H - pad - 150 - bh), s, font=vf, fill=col + (255,))
        im.save(p / f"{i:04d}.png")
    return p, fps


def line_chart(out_dir, values, dur=1.8, fps=30, canvas=(1080, 900), colour=RED,
               width=10, step_fps=12, hold=1.4, pad=90, dot=True, fill_under=False,
               axis_col=(150, 150, 152)):
    """A line drawing on left-to-right, optional dot marker riding the head."""
    p = _seq(out_dir)
    W, H = canvas
    vmin, vmax = min(values), max(values)
    span = (vmax - vmin) or 1
    pts = [(pad + (W - 2 * pad) * i / (len(values) - 1),
            H - pad - (H - 2 * pad) * (v - vmin) / span) for i, v in enumerate(values)]
    n_anim, n_hold = int(dur * fps), int(hold * fps)
    for i in range(n_anim + n_hold):
        qi = _quant(min(i, n_anim), fps, step_fps)
        prog = min(1.0, qi / max(1, n_anim))
        im = Image.new("RGBA", canvas, (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.line([(pad, H - pad), (W - pad, H - pad)], fill=axis_col + (180,), width=3)
        cut = prog * (len(pts) - 1)
        shown = pts[:int(cut) + 1]
        if cut % 1 and int(cut) + 1 < len(pts):
            a, b = pts[int(cut)], pts[int(cut) + 1]
            u = cut % 1
            shown = shown + [(a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u)]
        if len(shown) > 1:
            if fill_under:
                poly = shown + [(shown[-1][0], H - pad), (pad, H - pad)]
                d.polygon(poly, fill=colour + (46,))
            d.line(shown, fill=colour + (255,), width=width, joint="curve")
            if dot:
                x, y = shown[-1]
                d.ellipse([x - 16, y - 16, x + 16, y + 16], fill=colour + (255,))
        im.save(p / f"{i:04d}.png")
    return p, fps


def donut_chart(out_dir, pct, dur=1.3, fps=30, canvas=(1080, 1080), colour=RED,
                track=(0, 0, 0, 40), width=76, step_fps=12, hold=1.4, label=None,
                label_col=(28, 28, 30)):
    """A ring sweeping to `pct` (0-100) with the number counting up inside it."""
    p = _seq(out_dir)
    W, H = canvas
    r = min(W, H) * .34
    box = [W / 2 - r, H / 2 - r, W / 2 + r, H / 2 + r]
    nf = _font(ANTON, 170); lf = _font(FIG, 40, "SemiBold")
    n_anim, n_hold = int(dur * fps), int(hold * fps)
    for i in range(n_anim + n_hold):
        qi = _quant(min(i, n_anim), fps, step_fps)
        t = _ease_out(min(1.0, qi / max(1, n_anim)))
        im = Image.new("RGBA", canvas, (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.arc(box, 0, 360, fill=track, width=width)
        if pct * t > 0.4:
            d.arc(box, -90, -90 + 360 * (pct / 100) * t, fill=colour + (255,), width=width)
        s = f"{int(round(pct*t))}%"
        tw = d.textlength(s, font=nf)
        d.text((W / 2 - tw / 2, H / 2 - 108), s, font=nf, fill=label_col + (255,))
        if label:
            lw = d.textlength(label, font=lf)
            d.text((W / 2 - lw / 2, H / 2 + 74), label, font=lf, fill=label_col + (190,))
        im.save(p / f"{i:04d}.png")
    return p, fps


def stacked_bar(out_dir, parts, dur=1.2, fps=30, canvas=(1080, 460), step_fps=12, hold=1.6,
                pad=80, height=150, label_col=(28, 28, 30), gap=6):
    """parts = [(label, value, (r,g,b)), ...] one proportion bar filling segment by segment."""
    p = _seq(out_dir)
    W, H = canvas
    total = sum(v for _, v, _ in parts) or 1
    lf = _font(FIG, 34, "SemiBold")
    n_anim, n_hold = int(dur * fps), int(hold * fps)
    for i in range(n_anim + n_hold):
        qi = _quant(min(i, n_anim), fps, step_fps)
        prog = _ease_out(min(1.0, qi / max(1, n_anim)))
        im = Image.new("RGBA", canvas, (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        full = W - pad * 2
        x = pad
        for lab, val, col in parts:
            w = full * (val / total) * prog
            if w > 1:
                d.rectangle([x, H / 2 - height / 2, x + max(0, w - gap), H / 2 + height / 2],
                            fill=col + (255,))
            x += w
        # labels once the bar has essentially landed
        if prog > .8:
            x = pad
            for lab, val, col in parts:
                w = full * (val / total)
                if w > 90:
                    d.text((x + 12, H / 2 + height / 2 + 16), lab, font=lf,
                           fill=label_col + (int(255 * (prog - .8) / .2),))
                x += w
        im.save(p / f"{i:04d}.png")
    return p, fps
