"""Lift the white-bordered cutouts off a vibrant keyframe.

Every object in this style carries a thick WHITE sticker border, so the reliable
signal is the rim - not colour banding, which on these frames happily returns the
negative space between objects and calls it six layers.

Three things the plain rim pass needed:

* ADAPTIVE SPLITTING. Several white cutouts touching (three stacked page cards,
  a banner overlapping a card) fill as one blob. Erode until the bridges snap,
  label, then grow each label back inside the original mask.
* A DARK-POLARITY PASS. Not every element is white-on-colour: beat 8's headline
  numeral is black type on cream. The same fill runs on the dark end of the
  histogram and the results are pooled.
* VALIDITY FILTERS, because a wrong lift looks far worse than no lift. A piece
  must fill >=30% of its own bounding box (kills halftone slivers) and must be
  mostly NOT the ground colour (kills negative space). Beats where fewer than two
  pieces survive keep a camera move only.
"""
import json, os
import numpy as np
from PIL import Image, ImageFilter

from rims import _fill_holes, _b, SC
import sys
sys.path.insert(0, os.path.expanduser("~/.claude/skills/vox-explainer/references"))
from auto_elements import _components

MAXFRAC, MINFILL, MINDIST = 0.55, 0.30, 55


def _blobs(mask, min_frac=0.004):
    """Split a mask into pieces, eroding just enough to snap the bridges."""
    best = None
    for er in (5, 9, 13, 19, 25):
        core = np.asarray(_b(mask).filter(ImageFilter.MinFilter(er))) > 127
        lab, comps = _components(core, int(mask.size * min_frac))
        if not comps:
            break
        tot = sum(c[5] for c in comps)
        top = max(c[5] for c in comps) / max(1, tot)
        if best is None or len(comps) > best[3]:
            best = (lab, comps, er, len(comps))
        if len(comps) >= 3 and top < 0.55:
            best = (lab, comps, er, len(comps))
            break
    if not best:
        return []
    lab, comps, er, _ = best
    out = []
    for c in sorted(comps, key=lambda c: -c[5])[:8]:
        grown = np.asarray(_b(lab == c[0]).filter(ImageFilter.MaxFilter(er + 4))) > 127
        pm = grown & mask
        if pm.sum() > 300:
            out.append(pm)
    return out


def lift(bid, want=6, feather=3):
    kf = f"frames/keyframe_{bid:02d}.png"
    eldir = f"elements/b{bid:02d}"
    os.makedirs(eldir, exist_ok=True)
    for f in os.listdir(eldir):
        os.remove(os.path.join(eldir, f))

    im = Image.open(kf).convert("RGB")
    W, H = im.size
    small = im.resize((W // SC, H // SC), Image.LANCZOS)
    L = np.asarray(small.convert("L")).astype(np.int16)
    ground = np.median(np.asarray(small).reshape(-1, 3), axis=0)

    masks = []
    for label, m in (("bright", L >= max(198, int(np.percentile(L, 86)))),
                     ("dark", L <= min(72, int(np.percentile(L, 12))))):
        m = np.asarray(_b(m).filter(ImageFilter.MaxFilter(9))) > 127
        m = _fill_holes(m)
        m = np.asarray(_b(m).filter(ImageFilter.MinFilter(7))) > 127
        if m.mean() > 0.005:
            masks += _blobs(m)

    A = W * H
    cand = []
    for pm in masks:
        ys, xs = np.nonzero(pm)
        x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
        bw, bh = (x1 - x0 + 1) * SC, (y1 - y0 + 1) * SC
        if bw * bh > MAXFRAC * A or bw < 90 or bh < 90:
            continue
        box = pm[y0:y1 + 1, x0:x1 + 1]
        if box.mean() < MINFILL:
            continue
        px = np.asarray(small).astype(np.int16)[y0:y1 + 1, x0:x1 + 1][box]
        if len(px) < 400 or np.abs(px - ground).sum(axis=1).mean() < MINDIST:
            continue
        cand.append((int(pm.sum()), pm, x0, x1, y0, y1))

    cand.sort(key=lambda c: -c[0])
    keep = []
    for c in cand:
        if any((c[1] & k[1]).sum() / max(1, min(c[0], k[0])) > 0.5 for k in keep):
            continue
        keep.append(c)
        if len(keep) >= want:
            break

    els = []
    for i, (area, pm, x0, x1, y0, y1) in enumerate(keep):
        X0, Y0 = max(0, x0 * SC - 8), max(0, y0 * SC - 8)
        X1, Y1 = min(W, (x1 + 1) * SC + 8), min(H, (y1 + 1) * SC + 8)
        piece = im.crop((X0, Y0, X1, Y1)).convert("RGBA")
        al = _b(pm[y0:y1 + 1, x0:x1 + 1]).resize(piece.size, Image.BILINEAR)
        piece.putalpha(al.filter(ImageFilter.GaussianBlur(feather)))
        name = f"el{i:02d}"
        piece.save(os.path.join(eldir, name + ".png"))
        els.append({"name": name, "bbox": [int(X0), int(Y0), int(X1), int(Y1)],
                    "centre": [(X0 + X1) / 2, (Y0 + Y1) / 2],
                    "area": int(area) * SC * SC, "size": [piece.width, piece.height]})
    return els


if __name__ == "__main__":
    d = json.load(open("script.json"))
    durs = {b["id"]: b["duration"] for b in json.load(open("audio/vo_durations.json"))["beats"]}
    out = {"beats": []}
    for b in d["beats"]:
        els = lift(b["id"])
        print(f"beat {b['id']:2d}: {len(els) if len(els)>=2 else 0} moving pieces"
              f"{'' if len(els)>=2 else '  (camera only)'}")
        out["beats"].append(dict(id=b["id"], kf=f"frames/keyframe_{b['id']:02d}.png",
                                 eldir=f"elements/b{b['id']:02d}",
                                 elements=els if len(els) >= 2 else [],
                                 dur=durs[b["id"]]))
    json.dump(out, open("beats.json", "w"), indent=1)
