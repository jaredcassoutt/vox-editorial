"""Subject sprites are generated on a keyable field, never inside a composition.

The previous build lifted objects out of a finished poster and moved them over
that same poster, so the original stayed visible underneath and the whole thing
read as flat. Here the model only ever draws the SUBJECTS, spaced out on pure
magenta, and everything else - ground, confetti, tape, clippings, title - is
drawn locally. Keying magenta gives exact alpha, so each subject becomes a真 free
sprite that can sit on its own depth plane.

Objects that repeat (a phone in a 3x3 grid, three stacked page cards) are
generated ONCE and replicated locally, which is both cheaper and makes each copy
an independent layer.
"""
SHEET = (
    "{n} separate objects arranged with LARGE EMPTY GAPS between them on a completely "
    "flat pure magenta background: {items}. Each object is a vintage-print, engraved, "
    "hand-drawn ILLUSTRATION with halftone dot shading, cut out as a paper sticker with "
    "a THICK WHITE BORDER around its silhouette. The objects must NOT touch or overlap "
    "each other and must not touch the edges of the frame. NO text, NO lettering, NO "
    "confetti, NO tape, NO other elements whatsoever - only the {n} objects on flat pure "
    "magenta. NOT photorealistic, NOT CGI, NOT a 3D render, no gradients."
)

OBJECTS = {
 1: ["a hand holding up a smartphone, seen from the side",
     "a long ribbon of blank paper curling downward like an unrolled receipt"],
 2: ["a boxy early-2000s desktop computer tower with a chunky CRT monitor",
     "a steaming coffee mug", "a small tear-off desk calendar"],
 3: ["a blank rectangular web page card with a small button shape at its lower edge",
     "a hand with the index finger extended, pointing and about to click"],
 4: ["a very long vertical strip of blank film-reel-like paper with repeated empty "
     "rectangular panels down it, curving in an S shape",
     "a hand with one finger extended, swiping downward"],
 5: ["a single smartphone seen straight on with a blank screen"],
 6: ["a blank white page card with a large bold question mark printed on it",
     "a small open hand, palm up, resting"],
 7: ["a page card whose bottom edge is ripped away into ragged trailing strips",
     "a hand reaching upward with the fingers spread"],
 8: ["a dense crowd of many tiny identical standing human figures seen from the front, "
     "packed shoulder to shoulder in a wide horizontal band"],
 9: ["an ornate empty rectangular picture frame, the inside completely blank and empty"],
 10:["a hand pressing downward with the index finger extended",
     "a blank page card with a solid horizontal bar across its top edge"],
}


def sheet_prompt(bid):
    items = OBJECTS[bid]
    return SHEET.format(n=len(items), items="; ".join(f"({i+1}) {t}" for i, t in enumerate(items)))


if __name__ == "__main__":
    import json, subprocess
    jobs = []
    for bid in sorted(OBJECTS):
        p = sheet_prompt(bid)
        r = subprocess.run(["higgsfield", "generate", "create", "nano_banana_pro",
                            "--prompt", p, "--aspect-ratio", "1:1", "--resolution", "2k",
                            "--json"], capture_output=True, text=True)
        try:
            d = json.loads(r.stdout)
            jid = d[0] if isinstance(d, list) and d and isinstance(d[0], str) else (
                  d.get("id") if isinstance(d, dict) else None)
        except Exception:
            jid = None
        print(f"beat {bid:2d}: {len(OBJECTS[bid])} objects -> {jid}", flush=True)
        jobs.append({"id": bid, "job": jid, "n": len(OBJECTS[bid]), "prompt": p})
    json.dump(jobs, open("sheets/jobs.json", "w"), indent=1)
