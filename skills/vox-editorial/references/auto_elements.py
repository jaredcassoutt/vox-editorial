#!/usr/bin/env python3
"""
Automatic element decomposition — split a collage keyframe into INDEPENDENT layers.

The local engine animates a keyframe's pieces
separately, but it needs a hand-authored elements_spec.json with a bbox per element.
This finds the pieces automatically: the collage ground is a flat-ish paper field, and
the elements are the high-contrast shapes sitting on it, so a saliency mask plus
connected components recovers them without any hand-placement.

The pieces rest at their ORIGINAL positions over the original poster as backdrop, exactly
as the skill's own note prescribes, so a frame at rest reconstructs the source poster.

Usage: python3 auto_elements.py <project_dir> [max_elements]
"""
import json, os, sys
import numpy as np
from PIL import Image, ImageFilter


def _components(mask, min_px):
    """Label 4-connected components with an iterative flood fill (no scipy needed)."""
    h, w = mask.shape
    lab = np.zeros((h, w), np.int32)
    cur = 0
    out = []
    for sy in range(0, h, 2):
        for sx in range(0, w, 2):
            if not mask[sy, sx] or lab[sy, sx]:
                continue
            cur += 1
            stack = [(sy, sx)]
            lab[sy, sx] = cur
            ys, xs = [], []
            while stack:
                y, x = stack.pop()
                ys.append(y); xs.append(x)
                for dy, dx in ((1,0),(-1,0),(0,1),(0,-1)):
                    ny, nx = y+dy, x+dx
                    if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not lab[ny, nx]:
                        lab[ny, nx] = cur
                        stack.append((ny, nx))
            if len(ys) >= min_px:
                out.append((cur, min(xs), min(ys), max(xs), max(ys), len(ys)))
    return lab, out


def decompose(card_path, out_dir, max_elements=7, feather=3):
    im = Image.open(card_path).convert("RGB")
    W, H = im.size
    small = im.resize((W // 3, H // 3), Image.LANCZOS)
    a = np.asarray(small).astype(np.int16)

    # the paper ground is the modal colour; elements are what differs from it
    flat = a.reshape(-1, 3)
    ground = np.median(flat, axis=0)
    dist = np.abs(a - ground).sum(axis=2)

    # plus local contrast, which catches dark type on a light ground
    g = np.asarray(small.convert("L").filter(ImageFilter.FIND_EDGES)).astype(np.int16)
    score = dist + g * 2

    thr = np.percentile(score, 72)
    mask = score > thr
    m = Image.fromarray((mask * 255).astype(np.uint8))
    m = m.filter(ImageFilter.MaxFilter(7)).filter(ImageFilter.MinFilter(5))
    mask = np.asarray(m) > 127

    min_px = int(mask.size * 0.004)
    _, comps = _components(mask, min_px)
    comps.sort(key=lambda c: -c[5])
    comps = comps[:max_elements]

    os.makedirs(out_dir, exist_ok=True)
    els = []
    for i, (_, x0, y0, x1, y1, area) in enumerate(comps):
        # back to full-res coords with a little margin
        X0, Y0 = max(0, x0 * 3 - 12), max(0, y0 * 3 - 12)
        X1, Y1 = min(W, x1 * 3 + 12), min(H, y1 * 3 + 12)
        if X1 - X0 < 40 or Y1 - Y0 < 40:
            continue
        piece = im.crop((X0, Y0, X1, Y1)).convert("RGBA")
        # soft-edged alpha so the moving copy doesn't show a hard rectangle seam
        al = Image.new("L", piece.size, 0)
        from PIL import ImageDraw
        ImageDraw.Draw(al).rounded_rectangle(
            [4, 4, piece.width - 5, piece.height - 5],
            radius=max(6, min(piece.width, piece.height) // 12), fill=255)
        piece.putalpha(al.filter(ImageFilter.GaussianBlur(feather)))
        name = f"el{i:02d}"
        piece.save(os.path.join(out_dir, f"{name}.png"))
        els.append({"name": name, "bbox": [X0, Y0, X1, Y1],
                    "centre": [(X0 + X1) / 2, (Y0 + Y1) / 2],
                    "area": int(area), "size": [piece.width, piece.height]})
    return els


def run(proj, max_elements=7):
    doc = json.load(open(os.path.join(proj, "beats.json")))
    for b in doc["beats"]:
        for sh in b.get("shots", [{"id": "a"}]):
            key = f"{b['id']}{sh.get('id','a')}"
            kf = sh.get("keyframe_path") or os.path.join(proj, "keyframes", f"kf_{key}.jpg")
            if not os.path.exists(kf):
                print(f"[{key}] no keyframe, skipped"); continue
            od = os.path.join(proj, "elements", key)
            els = decompose(kf, od, max_elements)
            sh["elements"] = els
            sh["elements_dir"] = od
            print(f"[{key}] {len(els)} independent layers")
    json.dump(doc, open(os.path.join(proj, "beats.json"), "w"), indent=1, ensure_ascii=False)
    print("updated beats.json")


if __name__ == "__main__":
    proj = sys.argv[1] if len(sys.argv) > 1 else "out/tang-30s"
    run(os.path.abspath(proj), int(sys.argv[2]) if len(sys.argv) > 2 else 7)
