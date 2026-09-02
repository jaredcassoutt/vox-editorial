"""Generate the voiceover and the timing map that drives every frame count.

Reads   script.json   {"topic": str, "beats": [{"id": int, "narration": str}, ...]}
Writes  vo/beat_NN.mp3          one file per beat
        public/audio/vo.mp3     the joined narration with inter-beat gaps
        vo/timing.json          per-beat start/end/duration + frame windows + word boundaries

Nothing downstream may guess a duration. Read it from vo/timing.json.

    python3 -m venv .venv && ./.venv/bin/pip install -q edge-tts
    ./.venv/bin/python gen_vo.py                 # defaults
    VOICE=en-US-AndrewNeural RATE=+8% ./.venv/bin/python gen_vo.py

Env:
    VOICE  default en-GB-RyanNeural   (British documentary register)
    RATE   default +4%
    GAP    default 0.42              seconds of silence between beats
    FPS    default 30
"""

import asyncio
import json
import os
import subprocess
from pathlib import Path

import edge_tts

VOICE = os.environ.get("VOICE", "en-GB-RyanNeural")
RATE = os.environ.get("RATE", "+4%")
GAP = float(os.environ.get("GAP", "0.42"))
FPS = int(os.environ.get("FPS", "30"))

ROOT = Path.cwd()
VO_DIR = ROOT / "vo"
AUDIO_DIR = ROOT / "public" / "audio"


def duration_of(path: Path) -> float:
    out = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(path)]
    )
    return float(out.decode().strip())


async def synth(beat: dict) -> list[dict]:
    """Synthesise one beat, returning its word boundaries."""
    try:
        comm = edge_tts.Communicate(beat["narration"], VOICE, rate=RATE,
                                    boundary="WordBoundary")
    except TypeError:  # older/newer edge-tts without the boundary kwarg
        comm = edge_tts.Communicate(beat["narration"], VOICE, rate=RATE)

    words: list[dict] = []
    path = VO_DIR / f"beat_{beat['id']:02d}.mp3"
    with open(path, "wb") as f:
        async for chunk in comm.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                words.append({
                    "w": chunk["text"],
                    "t": chunk["offset"] / 1e7,
                    "d": chunk["duration"] / 1e7,
                })
    return words


def join_with_gaps(paths: list[Path], out: Path) -> None:
    """Concatenate the beats, separated by GAP seconds of silence."""
    silence = VO_DIR / "_gap.mp3"
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-f", "lavfi",
         "-i", f"anullsrc=r=24000:cl=mono", "-t", str(GAP),
         "-c:a", "libmp3lame", "-q:a", "6", str(silence)],
        check=True,
    )
    listing = VO_DIR / "_concat.txt"
    lines = []
    for i, p in enumerate(paths):
        if i:
            lines.append(f"file '{silence.resolve()}'")
        lines.append(f"file '{p.resolve()}'")
    listing.write_text("\n".join(lines) + "\n")
    out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
         "-i", str(listing), "-c:a", "libmp3lame", "-q:a", "2", str(out)],
        check=True,
    )


async def main() -> None:
    VO_DIR.mkdir(exist_ok=True)
    script = json.loads((ROOT / "script.json").read_text())
    beats = script["beats"]

    timing: dict[str, dict] = {}
    paths: list[Path] = []
    cursor = 0.0

    for beat in beats:
        words = await synth(beat)
        path = VO_DIR / f"beat_{beat['id']:02d}.mp3"
        dur = duration_of(path)
        start, end = cursor, cursor + dur
        timing[str(beat["id"])] = {
            "narration": beat["narration"],
            "start": round(start, 3),
            "end": round(end, 3),
            "duration": round(dur, 3),
            "startFrame": round(start * FPS),
            "endFrame": round(end * FPS),
            "frames": round(dur * FPS),
            "words": words,
        }
        paths.append(path)
        cursor = end + GAP
        print(f"  beat {beat['id']:>2}  {dur:5.2f}s  {len(words):>3} words  "
              f"{start:6.2f}-{end:6.2f}  |  {beat['narration'][:58]}")

    join_with_gaps(paths, AUDIO_DIR / "vo.mp3")
    total = duration_of(AUDIO_DIR / "vo.mp3")

    payload = {
        "voice": VOICE, "rate": RATE, "gap": GAP, "fps": FPS,
        "totalDuration": round(total, 3),
        "totalFrames": round(total * FPS),
        "beats": timing,
    }
    (VO_DIR / "timing.json").write_text(json.dumps(payload, indent=1))
    print(f"\n  TOTAL {total:.2f}s  =  {round(total * FPS)} frames @ {FPS}fps")
    print(f"  wrote vo/timing.json and public/audio/vo.mp3")


if __name__ == "__main__":
    asyncio.run(main())
