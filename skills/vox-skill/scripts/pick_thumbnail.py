"""Pick the video's poster frame automatically: the busiest, most composed moment.

The first frame of a film built this way is almost always the worst possible
thumbnail — an empty paper background before anything has entered. Picking by
hand means scrubbing. This scores every candidate and takes the best.

"Interesting" is defined as **several distinct elements, spread across the
frame**, not merely a lot of ink. A shot where the dark foreground band fills the
bottom third has high coverage and no interest; a shot with three portraits, a
headline and a stamp has content in many parts of the frame. So the dominant
term is spatial spread across a grid, not raw coverage.

    pip install numpy pillow
    python3 pick_thumbnail.py out/film.mp4                    # writes out/film-thumb.png
    python3 pick_thumbnail.py out/film.mp4 poster.png --embed # also sets it as the mp4 cover
    python3 pick_thumbnail.py out/film.mp4 --report           # show the top 8 candidates

Options:
    --samples N     candidate frames to score (default 160)
    --grid N        grid used for the spread metric (default 7, so 49 cells)
    --head F        fraction of the film to ignore at the start (default 0.08)
    --tail F        fraction to ignore at the end (default 0.06)
    --embed         attach the chosen frame to the mp4 as cover art, in place
    --report        print the ranked shortlist with each frame's scores
"""

import subprocess
import sys
from pathlib import Path

import numpy as np


def probe(path: str) -> tuple[float, int, int]:
    out = subprocess.check_output([
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "format=duration:stream=width,height",
        "-of", "default=noprint_wrappers=1:nokey=1", path,
    ]).decode().split()
    w, h, dur = int(out[0]), int(out[1]), float(out[2])
    return dur, w, h


def sample_frames(path: str, n: int, t0: float, t1: float, width: int = 384):
    """Decode n evenly spaced frames as a single rawvideo stream."""
    fps = n / max(0.001, t1 - t0)
    proc = subprocess.run(
        ["ffmpeg", "-v", "error", "-ss", str(t0), "-to", str(t1), "-i", path,
         "-vf", f"fps={fps},scale={width}:-2", "-f", "rawvideo",
         "-pix_fmt", "rgb24", "-"],
        stdout=subprocess.PIPE, check=True,
    )
    buf = np.frombuffer(proc.stdout, dtype=np.uint8)
    # Height isn't known until we see the byte count; derive it.
    for h in range(2, 4000, 2):
        if len(buf) % (width * h * 3) == 0:
            frames = len(buf) // (width * h * 3)
            if frames and abs(frames - n) <= max(4, n // 8):
                return buf.reshape(frames, h, width, 3).astype(np.float32) / 255.0
    raise SystemExit("could not infer frame geometry from the decoded stream")


def score_frames(frames: np.ndarray, grid: int):
    """Return per-frame (total, spread, edges, coverage, accent)."""
    n, h, w, _ = frames.shape
    gray = frames @ np.array([0.299, 0.587, 0.114], dtype=np.float32)

    # The paper ground is whatever tone dominates the frame; ink is deviation.
    bg = np.median(gray.reshape(n, -1), axis=1)[:, None, None]
    ink = np.abs(gray - bg) > 0.085

    # Spread: how many grid cells hold real content. This is the "several
    # distinct elements" term and it carries the most weight.
    ch, cw = h // grid, w // grid
    cells = ink[:, : ch * grid, : cw * grid].reshape(n, grid, ch, grid, cw)
    cell_fill = cells.mean(axis=(2, 4))
    spread = (cell_fill > 0.10).mean(axis=(1, 2))

    # Edges: detail and legible type rather than flat blocks of tone.
    gx = np.abs(np.diff(gray, axis=2)).mean(axis=(1, 2))
    gy = np.abs(np.diff(gray, axis=1)).mean(axis=(1, 2))
    edges = gx + gy

    # Coverage, but capped: a frame that is mostly dark foreground is not busy.
    coverage = ink.mean(axis=(1, 2))
    cov_term = np.clip(coverage, 0, 0.45) / 0.45
    cov_term *= np.where(coverage > 0.72, 0.35, 1.0)  # penalise near-full frames

    # The red accent: its presence means a stamp, a strike or a reveal is on screen.
    r, g, b = frames[..., 0], frames[..., 1], frames[..., 2]
    accent = ((r > 0.45) & (r - g > 0.18) & (r - b > 0.18)).mean(axis=(1, 2))
    accent_term = np.clip(accent / 0.06, 0, 1)

    e = edges / (edges.max() + 1e-9)
    total = 0.46 * spread + 0.26 * e + 0.16 * cov_term + 0.12 * accent_term
    return total, spread, e, coverage, accent_term


def main() -> None:
    a = sys.argv[1:]
    if not a:
        print(__doc__)
        raise SystemExit(2)
    src = a[0]
    dst = a[1] if len(a) > 1 and not a[1].startswith("--") else None
    fl = {a[i]: a[i + 1] for i in range(len(a)) if a[i].startswith("--") and i + 1 < len(a)}
    n = int(fl.get("--samples", 160))
    grid = int(fl.get("--grid", 7))
    head = float(fl.get("--head", 0.08))
    tail = float(fl.get("--tail", 0.06))

    dur, W, H = probe(src)
    t0, t1 = dur * head, dur * (1 - tail)
    frames = sample_frames(src, n, t0, t1)
    total, spread, edges, coverage, accent = score_frames(frames, grid)

    order = np.argsort(-total)
    step = (t1 - t0) / len(total)
    best_t = t0 + (order[0] + 0.5) * step

    if "--report" in a:
        print(f"  {src}  {W}x{H}  {dur:.2f}s   scored {len(total)} frames "
              f"in {t0:.1f}-{t1:.1f}s\n")
        print(f"  {'time':>7}  {'score':>6}  {'spread':>6}  {'edges':>6}  {'cover':>6}  {'accent':>6}")
        for i in order[:8]:
            print(f"  {t0 + (i + 0.5) * step:7.2f}  {total[i]:6.3f}  {spread[i]:6.3f}  "
                  f"{edges[i]:6.3f}  {coverage[i]:6.3f}  {accent[i]:6.3f}")
        print()

    out = Path(dst) if dst else Path(src).with_name(Path(src).stem + "-thumb.png")
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-ss", f"{best_t:.3f}", "-i", src,
         "-frames:v", "1", str(out)],
        check=True,
    )
    print(f"  picked {best_t:.2f}s  (score {total[order[0]]:.3f}, "
          f"{spread[order[0]] * 100:.0f}% of the frame occupied)")
    print(f"  wrote {out}")

    if "--embed" in a:
        tmp = Path(src).with_suffix(".cover.mp4")
        subprocess.run(
            ["ffmpeg", "-v", "error", "-y", "-i", src, "-i", str(out),
             "-map", "0", "-map", "1", "-c", "copy", "-c:v:1", "png",
             "-disposition:v:1", "attached_pic", str(tmp)],
            check=True,
        )
        tmp.replace(src)
        print(f"  embedded as cover art in {src}")


if __name__ == "__main__":
    main()
