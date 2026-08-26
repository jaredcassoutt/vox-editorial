#!/usr/bin/env python3
"""Reusable component library - look here BEFORE generating anything.

Model-generated sprites cost real credits, and most films need the same handful of
objects: a pointing hand, a phone, a page card, a crowd. Every sprite a build
produces is filed here with tags, so the next film pays nothing for it.

Two rules for the pipeline:
  1. Before generating a subject sprite, call `find()`. Only generate the misses.
  2. After extracting new sprites, call `add()` for any that are generic enough to
     come up again. An object tied to one specific film (a named person's portrait,
     a one-off diagram) does NOT belong here.

The locally-drawn elements - confetti, tape, torn banners, newsprint clippings,
paper grounds - are NOT cached as images. They are drawn by `paper.py` in a couple
of milliseconds, seeded, so caching them would only freeze variety that costs
nothing to regenerate. Cache what is expensive, draw what is cheap.

    from library import find, add, ensure
    hit = find(["hand", "pointing"])          # -> path or None
    paths = ensure([{"id": "smartphone", "tags": [...], "prompt": "..."}], gen_fn)
"""
import json
import os
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "manifest.json"


def _load():
    if MANIFEST.exists():
        return json.loads(MANIFEST.read_text())
    return {"components": []}


def _save(man):
    man["components"].sort(key=lambda c: c["id"])
    MANIFEST.write_text(json.dumps(man, indent=1))


def all_components(kind=None):
    comps = _load()["components"]
    return [c for c in comps if kind is None or c.get("kind") == kind]


def find(tags, kind="sprite", min_score=0.5):
    """Best component matching these tags, or None. Scored by tag overlap."""
    want = {t.lower() for t in tags}
    best, best_score = None, 0.0
    for c in all_components(kind):
        have = {t.lower() for t in c.get("tags", [])} | {c["id"].replace("-", " ")}
        hits = sum(1 for w in want if any(w in h or h in w for h in have))
        score = hits / max(1, len(want))
        if score > best_score:
            best, best_score = c, score
    if best and best_score >= min_score:
        return str(ROOT / best["file"])
    return None


def add(path, cid, tags, kind="sprite", style=None, source=None, origin=None,
        overwrite=False):
    """File a component. Returns its path in the library."""
    man = _load()
    existing = next((c for c in man["components"] if c["id"] == cid), None)
    if existing and not overwrite:
        return str(ROOT / existing["file"])
    sub = "sprites" if kind == "sprite" else kind
    (ROOT / sub).mkdir(parents=True, exist_ok=True)
    dst = ROOT / sub / f"{cid}{Path(path).suffix}"
    shutil.copy(path, dst)
    try:
        from PIL import Image
        size = list(Image.open(dst).size)
    except Exception:
        size = None
    rec = {"id": cid, "kind": kind, "file": f"{sub}/{dst.name}", "tags": tags,
           "size": size, "style": style, "source": source, "from": origin}
    man["components"] = [c for c in man["components"] if c["id"] != cid] + [rec]
    _save(man)
    return str(dst)


def ensure(specs, generate):
    """Resolve a list of sprite specs, generating only what the library lacks.

    Each spec: {"id", "tags", "prompt"}. `generate(missing_specs)` must return
    {id: local_path}. Everything it returns is filed for next time.
    """
    resolved, missing = {}, []
    for sp in specs:
        hit = find(sp["tags"] + [sp["id"].replace("-", " ")])
        if hit:
            resolved[sp["id"]] = hit
        else:
            missing.append(sp)
    if missing:
        made = generate(missing) or {}
        for sp in missing:
            p = made.get(sp["id"])
            if p and os.path.exists(p):
                resolved[sp["id"]] = add(p, sp["id"], sp["tags"],
                                         source="generated", origin=sp.get("origin"))
    return resolved, [sp["id"] for sp in missing]


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        print(find(sys.argv[1:]) or "no match")
    else:
        for c in all_components():
            print(f"{c['id']:24s} {', '.join(c.get('tags', [])[:6])}")
