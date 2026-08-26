"""Key the magenta field and cut each object into its own free sprite.

Because the model only ever drew the subjects - spaced apart on flat magenta -
this is exact: no ground fringe, no negative space mistaken for an object, no
guessing which blob is real. Each sprite comes out with true alpha and can be
placed anywhere on any depth plane.
"""
import os, sys
import numpy as np
from PIL import Image, ImageFilter

sys.path.insert(0, os.path.expanduser("~/.claude/skills/vox-explainer/references"))
from auto_elements import _components


def sprites(sheet_path, want, out_dir, min_frac=0.004):
    im = Image.open(sheet_path).convert("RGB")
    W, H = im.size
    s = im.resize((W // 3, H // 3), Image.LANCZOS)
    a = np.asarray(s).astype(np.int16)
    # The field is magenta but NOT a uniform magenta - it comes back with a wash
    # across it. So sample the key colour from the border instead of assuming a
    # fixed value, and cut on distance to that colour.
    bd = np.concatenate([a[0], a[-1], a[:, 0], a[:, 1]])
    key_col = np.median(bd, axis=0)
    dist = np.abs(a - key_col).sum(axis=2)
    g_ = a[..., 1]
    magenta_ish = (a[..., 0] > g_ + 25) & (a[..., 2] > g_ + 25)
    obj = (dist > 110) & ~magenta_ish
    m = Image.fromarray((obj * 255).astype(np.uint8))
    m = m.filter(ImageFilter.MedianFilter(5)).filter(ImageFilter.MaxFilter(3))
    obj = np.asarray(m) > 127

    lab, comps = _components(obj, int(obj.size * min_frac))
    comps.sort(key=lambda c: -c[5])
    os.makedirs(out_dir, exist_ok=True)
    out = []
    for i, c in enumerate(comps[:want]):
        pm = np.asarray(Image.fromarray(((lab == c[0]) * 255).astype(np.uint8))
                        .filter(ImageFilter.MaxFilter(5))) > 127
        ys, xs = np.nonzero(pm)
        x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
        X0, Y0 = max(0, x0 * 3 - 6), max(0, y0 * 3 - 6)
        X1, Y1 = min(W, (x1 + 1) * 3 + 6), min(H, (y1 + 1) * 3 + 6)
        piece = im.crop((X0, Y0, X1, Y1)).convert("RGBA")
        al = Image.fromarray((pm[y0:y1 + 1, x0:x1 + 1] * 255).astype(np.uint8))
        al = al.resize(piece.size, Image.BILINEAR).filter(ImageFilter.GaussianBlur(1.5))
        # Pull the alpha WELL inside the silhouette. The key leaves a magenta halo
        # in the outermost pixels of the white sticker border, and a pink rim around
        # every object is the single most obvious tell that something was cut out.
        # The border is thick, so losing a few pixels of it costs nothing.
        al = al.point(lambda v: 0 if v < 150 else 255)
        for _ in range(3):
            al = al.filter(ImageFilter.MinFilter(5))
        al = al.filter(ImageFilter.GaussianBlur(1.2))
        piece.putalpha(al)
        # and neutralise any magenta that still survives inside the remaining rim
        arr = np.asarray(piece).astype(np.int16)
        rgb, a4 = arr[..., :3], arr[..., 3]
        pink = (rgb[..., 0] > rgb[..., 1] + 30) & (rgb[..., 2] > rgb[..., 1] + 30) & (a4 > 0)
        arr[..., :3][pink] = 252
        piece = Image.fromarray(arr.astype(np.uint8), "RGBA")
        p = os.path.join(out_dir, f"s{i:02d}.png")
        piece.save(p)
        out.append(p)
    return out


if __name__ == "__main__":
    import json
    jobs = {j["id"]: j for j in json.load(open("sheets/jobs.json"))}
    for bid in sorted(jobs):
        sp = f"sheets/sheet_{bid:02d}.png"
        if not os.path.exists(sp):
            print(f"beat {bid:2d}: sheet missing"); continue
        got = sprites(sp, jobs[bid]["n"], f"sprites/b{bid:02d}")
        sizes = [Image.open(p).size for p in got]
        print(f"beat {bid:2d}: {len(got)}/{jobs[bid]['n']} sprites {sizes}")
