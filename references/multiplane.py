"""Render a scene graph as a multiplane shot.

A camera moves through the scene; each layer responds to it by its own DEPTH.
Near layers translate and scale more than far ones, which is the whole point -
that differential is what the eye reads as space. On top of the camera response
every layer carries its own drift, breath and rotation on its own phase, and its
own staggered entrance, so no two elements ever move together.

The ground is rendered oversized so a pan never exposes its edge.
"""
import json, math, os, subprocess, sys

from PIL import Image

FPS, W, H = 30, 1080, 1920
ENTR = ["pop", "rise", "drop", "left", "right"]


def _back(t, s=1.7):
    return 1 + (s + 1) * (t - 1) ** 3 + s * (t - 1) ** 2


def _ease(t):
    return 1 - (1 - t) ** 3


def render(layers, out, dur, idx):
    n = int(dur * FPS)
    rnd = __import__("random").Random(idx * 31 + 7)
    prepared = []
    for i, l in enumerate(layers):
        img = l["img"]
        if l["kind"] == "ground":
            img = img.resize((int(W * 1.3), int(H * 1.3)), Image.LANCZOS)
        elif "h" in l:
            target = int(H * l["h"])
            img = img.resize((max(1, int(img.width * target / img.height)), target), Image.LANCZOS)
        prepared.append(dict(l, img=img,
                             ph=rnd.uniform(0, 6.28), fq=rnd.uniform(0.5, 0.95),
                             t0=0.0 if l["kind"] in ("ground",) else
                                min(0.9, 0.04 + (1.15 - l["depth"]) * 0.45 + rnd.uniform(0, .12)),
                             ent=("pop" if l["kind"] in ("title", "ground")
                                  else ENTR[(i + idx) % len(ENTR)])))
    prepared.sort(key=lambda l: l["depth"])

    # camera: a slow push with a little lateral travel, direction alternating per beat
    sgn = 1 if idx % 2 == 0 else -1
    pr = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo",
        "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-an",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", out],
        stdin=subprocess.PIPE)
    for f in range(n):
        t = f / FPS
        u = t / max(.001, dur)
        e = _ease(min(1.0, u))
        zoom = 1 + 0.085 * e
        panx = sgn * 52 * e
        pany = -30 * e
        fr = Image.new("RGBA", (W, H), (0, 0, 0, 255))
        for l in prepared:
            lt = t - l["t0"]
            if lt < 0:
                continue
            d = l["depth"]
            ent = 1.0 if lt > 0.62 else _back(min(1.0, lt / 0.62))
            alpha = 1.0 if l["kind"] == "ground" else min(1.0, lt / 0.22)
            k = 1 - ent
            dx = dy = rot = 0.0
            if l["kind"] == "ground":
                pass
            elif l["ent"] == "rise":   dy = 190 * k * d
            elif l["ent"] == "drop":   dy = -190 * k * d
            elif l["ent"] == "left":   dx = -230 * k * d
            elif l["ent"] == "right":  dx = 230 * k * d
            else:                      rot = 5 * k

            # camera response scales with depth - this is the parallax. The title is
            # the nearest plane, so a full response walks its paper off the edge;
            # it keeps the depth (for scale and draw order) but damps the pan.
            damp = 0.35 if l["kind"] == "title" else 1.0
            cam_x = panx * d * damp
            cam_y = pany * d * damp
            zs = 1 + (zoom - 1) * (0.25 + 1.35 * d) * (0.5 if l["kind"] == "title" else 1.0)

            amp = 10 * d if l["kind"] != "ground" else 0
            drift_x = math.sin(t * l["fq"] + l["ph"]) * amp
            drift_y = math.cos(t * l["fq"] * 0.78 + l["ph"]) * amp * 0.85
            breath = 1 + math.sin(t * 1.05 + l["ph"]) * (0.010 * d)
            spin = l.get("spin", 0) * math.sin(t * 0.55 + l["ph"]) * 0.35

            img = l["img"]
            sc = zs * breath * (1.0 if l["kind"] == "ground" else (0.88 + 0.12 * ent))
            w2, h2 = max(1, int(img.width * sc)), max(1, int(img.height * sc))
            pc = img.resize((w2, h2), Image.LANCZOS)
            ang = rot + spin
            if abs(ang) > 0.05:
                pc = pc.rotate(ang, expand=True, resample=Image.BICUBIC)
                w2, h2 = pc.size
            if alpha < 1:
                pc.putalpha(pc.split()[3].point(lambda v: int(v * alpha)))
            px = l["cx"] * W + cam_x + drift_x + dx - w2 / 2
            py = l["cy"] * H + cam_y + drift_y + dy - h2 / 2
            fr.alpha_composite(pc, (int(px), int(py)))
        pr.stdin.write(fr.convert("RGB").tobytes())
    pr.stdin.close()
    pr.wait()


if __name__ == "__main__":
    import glob
    from scene import build
    durs = {b["id"]: b["duration"] for b in json.load(open("audio/vo_durations.json"))["beats"]}
    for i, bid in enumerate(range(1, 11)):
        sp = sorted(glob.glob(f"sprites/b{bid:02d}/s*.png"))
        sprites = [Image.open(p).convert("RGBA") for p in sp]
        layers = build(bid, sprites)
        dur = durs[bid] + 0.7
        render(layers, f"clips/clip_{bid:02d}.mp4", dur, i)
        kinds = {}
        for l in layers:
            kinds[l["kind"]] = kinds.get(l["kind"], 0) + 1
        print(f"beat {bid:2d}: {len(layers)} independent layers {kinds}", flush=True)
