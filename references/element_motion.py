"""Element-level motion collage — animate the PIECES of a poster, not the whole flat image.

Local keyframe engine. The video model is not used at all:
frames are drawn locally with Pillow, so nothing is content-filtered, everything is exact
and reproducible, and it costs nothing.

Two stages:
  1. cut the poster into pieces  (use Vision subject-lift from real-subject-cutouts.md for
     figures, and plain crops for text blocks / strips)
  2. animate the pieces with Layer keyframes, then render

Key lesson carried over: elements REST AT THEIR ORIGINAL POSITIONS on the poster, and the
poster itself is the backdrop, so the assembled frame reconstructs the original composition.
Scatter pieces into a new arrangement and it stops looking like the source.
"""
import math, subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter


# ───────────────────────────── easings ─────────────────────────────
def _lin(t): return t
def _in(t): return t * t
def _out(t): return 1 - (1 - t) ** 3
def _smooth(t): return t * t * (3 - 2 * t)
def _back(t, s=1.70158): return 1 + (s + 1) * (t - 1) ** 3 + s * (t - 1) ** 2
def _bounce(t):
    n, d = 7.5625, 2.75
    if t < 1 / d: return n * t * t
    if t < 2 / d: t -= 1.5 / d; return n * t * t + .75
    if t < 2.5 / d: t -= 2.25 / d; return n * t * t + .9375
    t -= 2.625 / d; return n * t * t + .984375

EASE = {"linear": _lin, "in": _in, "out": _out, "smooth": _smooth,
        "back": _back, "bounce": _bounce}


class Layer:
    """One collage piece.

    keys: [dict(t=seconds, x=, y=, s=1.0, r=0, a=1.0, e="smooth"), ...]
          x/y are the CENTRE in canvas pixels. Values interpolate between keys using the
          easing named on the LATER key.
    sway/pulse: tiny idle motion so a settled piece is never dead-still.
    """

    def __init__(self, img, keys, sway=0.0, pulse=0.0, shadow=0):
        self.img = Image.open(img).convert("RGBA") if isinstance(img, (str, Path)) else img
        self.keys = sorted(keys, key=lambda k: k["t"])
        self.sway, self.pulse, self.shadow = sway, pulse, shadow

    def state(self, t):
        ks = self.keys
        if t <= ks[0]["t"]: cur = dict(ks[0])
        elif t >= ks[-1]["t"]: cur = dict(ks[-1])
        else:
            for i in range(len(ks) - 1):
                a, b = ks[i], ks[i + 1]
                if a["t"] <= t <= b["t"]:
                    u = (t - a["t"]) / max(1e-6, b["t"] - a["t"])
                    u = EASE.get(b.get("e", "smooth"), _smooth)(u)
                    cur = {k: a.get(k, 0) + (b.get(k, a.get(k, 0)) - a.get(k, 0)) * u
                           for k in ("x", "y", "s", "r", "a")}
                    cur["t"] = t
                    break
        cur.setdefault("s", 1.0); cur.setdefault("r", 0); cur.setdefault("a", 1.0)
        if self.sway:
            cur["x"] += math.sin(t * 1.7) * self.sway
            cur["y"] += math.cos(t * 1.3) * self.sway * .6
        if self.pulse:
            cur["s"] *= 1 + math.sin(t * 2.1) * self.pulse
        return cur

    def draw(self, canvas, t):
        st = self.state(t)
        if st["a"] <= 0.01 or st["s"] <= 0.01: return
        w = max(1, int(self.img.width * st["s"]))
        h = max(1, int(self.img.height * st["s"]))
        im = self.img.resize((w, h), Image.LANCZOS)
        if st["r"]: im = im.rotate(st["r"], expand=True, resample=Image.BICUBIC)
        if st["a"] < 1:
            al = im.split()[3].point(lambda v: int(v * st["a"])); im.putalpha(al)
        pos = (int(st["x"] - im.width / 2), int(st["y"] - im.height / 2))
        if self.shadow:
            sh = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
            sh.paste(Image.new("RGBA", im.size, (0, 0, 0, 120)),
                     (pos[0] + self.shadow, pos[1] + self.shadow), im.split()[3])
            canvas.alpha_composite(sh.filter(ImageFilter.GaussianBlur(self.shadow * .8)))
        canvas.alpha_composite(im, pos)


# ───────────────────────── entrance helpers ─────────────────────────
def pop_settle(t0, x, y, dur=0.5, from_scale=1.35):
    """Focus-pop in place. Opaque, no off-screen travel, so it never ghosts on a backdrop."""
    return [dict(t=t0, x=x, y=y, s=from_scale, a=0),
            dict(t=t0 + 0.10, x=x, y=y, s=from_scale * .98, a=1, e="out"),
            dict(t=t0 + dur, x=x, y=y, s=1.0, a=1, e="out")]

def fly_in(t0, x, y, W, H, frm="left", dur=0.6, spin=0):
    off = {"left": (-W * .5, y), "right": (W * 1.5, y),
           "top": (x, -H * .4), "bottom": (x, H * 1.4)}[frm]
    return [dict(t=t0, x=off[0], y=off[1], s=1.0, r=spin, a=1),
            dict(t=t0 + dur, x=x, y=y, s=1.0, r=0, a=1, e="back")]

def slap(t0, x, y, dur=0.34, from_scale=1.35):
    """Snap in from slightly enlarged. Softer than the old 1.9x stomp."""
    return [dict(t=t0, x=x, y=y, s=from_scale, a=0),
            dict(t=t0 + dur, x=x, y=y, s=1.0, a=1, e="out")]

def drop(t0, x, y, H, dur=0.7):
    return [dict(t=t0, x=x, y=-H * .2, s=1.0, a=1),
            dict(t=t0 + dur, x=x, y=y, s=1.0, a=1, e="bounce")]


# ───────────────────────────── camera ─────────────────────────────
def cam(t, zoom_per_s=0.012, shake_at=(), shake_amp=5, decay=9.0):
    """Slow push plus a SUBTLE impact shake.

    Restraint rule: shake is a punctuation mark, not a default. Use it on at most one
    entrance per beat - the payoff - and leave every other entrance unshaken. A film where
    everything stomps reads as noise.
    """
    z = 1 + zoom_per_s * t
    dx = dy = 0.0
    for st in shake_at:
        d = t - st
        if 0 <= d < 1.2:
            k = math.exp(-decay * d)
            dx += math.sin(d * 46) * shake_amp * k
            dy += math.cos(d * 39) * shake_amp * k
    return z, dx, dy


# ───────────────────────────── render ─────────────────────────────
def render(out_path, layers, dur, fps=30, size=(1080, 1920), backdrop=None,
           camera=True, shake_at=(), bg=(18, 18, 20)):
    """Draw every frame locally and pipe rawvideo into ffmpeg."""
    W, H = size
    over = 1.18                                   # overscan so camera moves never reveal edges
    CW, CH = int(W * over), int(H * over)
    back = None
    if backdrop:
        b = Image.open(backdrop).convert("RGBA")
        s = max(CW / b.width, CH / b.height)
        b = b.resize((int(b.width * s), int(b.height * s)), Image.LANCZOS)
        back = b.crop(((b.width - CW) // 2, (b.height - CH) // 2,
                       (b.width - CW) // 2 + CW, (b.height - CH) // 2 + CH))
    n = int(dur * fps)
    p = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
         "-s", f"{W}x{H}", "-r", str(fps), "-i", "-", "-an",
         "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
         str(out_path)], stdin=subprocess.PIPE)
    for i in range(n):
        t = i / fps
        canvas = Image.new("RGBA", (CW, CH), bg + (255,))
        if back is not None: canvas.alpha_composite(back)
        # layers are positioned in FINAL canvas space; offset into the overscan canvas
        ox, oy = (CW - W) // 2, (CH - H) // 2
        sub = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
        for L in layers:
            st = L.state(t)
            st = dict(st); st["x"] += ox; st["y"] += oy
            tmp = Layer(L.img, [dict(st, t=0)], shadow=L.shadow)
            tmp.draw(sub, 0)
        canvas.alpha_composite(sub)
        if camera:
            z, dx, dy = cam(t, shake_at=shake_at)
            cw, ch = int(CW / z), int(CH / z)
            x0 = int((CW - cw) / 2 + dx); y0 = int((CH - ch) / 2 + dy)
            x0 = max(0, min(CW - cw, x0)); y0 = max(0, min(CH - ch, y0))
            canvas = canvas.crop((x0, y0, x0 + cw, y0 + ch)).resize((W, H), Image.LANCZOS)
        else:
            canvas = canvas.crop((ox, oy, ox + W, oy + H))
        p.stdin.write(canvas.convert("RGB").tobytes())
    p.stdin.close(); p.wait()
    return out_path
