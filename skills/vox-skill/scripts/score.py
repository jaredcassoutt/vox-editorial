"""Synthesise a tense-documentary music bed that stays out of the narration's way.

Measured against a reference documentary cue, the genre's defining property is
spectral, not melodic: **93% of its energy sits below 250 Hz, and only ~13% falls
inside the vocal band (200 Hz - 4 kHz)**. It is a low drone, not a song turned
down. Build to that and the mix works before you touch a fader.

Interest has to come from arrangement over time, never from volume or from
adding midrange. The bed is sectioned: bare drone, then a pulse, then a
recurring motif, the pad filter opening as it builds, stripped back at the end.

    pip install numpy
    python3 score.py out.wav --seconds 70.3
    python3 score.py out.wav --seconds 70.3 --key D --bpm 68 --motif 0.9

Options:
    --seconds F   length (default 60)
    --bpm N       tempo (default 72; the genre lives at 60-80)
    --key K       root note letter, A-G, optional # or b (default A). Natural minor.
    --motif F     0..1, the recurring cello figure (default 0.7). The main source
                  of interest. At 0 you get a flat drone bed.
    --pulse F     0..1, rhythmic movement (default 0.7)
    --bright F    0..1, sparse bell on top (default 0.45). Above ~0.8 it starts
                  competing with the voice.
    --build F     0..1, how much the bed swells across its length (default 0.55)
    --seed N      changes bell placement and detuning (default 7)
    --sr N        sample rate (default 44100)

Writes a 16-bit stereo WAV. See mix_audio.sh for the mastering and the duck.
"""

import sys
import wave

import numpy as np

NOTES = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}

# Eight chords rather than four: the second half turns to VII and back, which is
# what stops a four-chord loop announcing itself on the third pass.
PROGRESSION = [
    (0, "min"), (8, "maj"), (5, "min"), (7, "min"),
    (0, "min"), (10, "maj"), (8, "maj"), (7, "min"),
]
TRIAD = {"min": (0, 3, 7), "maj": (0, 4, 7)}

# The motif: (beat within the two-bar chord, semitones above that chord's root).
# A fixed intervallic shape that transposes with the harmony, which is what makes
# it read as a theme rather than as arpeggio filler. 15 is rewritten to the
# chord's own third.
MOTIF = [(0.0, 12), (1.5, 19), (3.0, 15), (4.5, 12), (6.0, 17)]


def hz(semitones_from_a1: float) -> float:
    """A1 = 55 Hz is the anchor: the drone's root octave."""
    return 55.0 * 2 ** (semitones_from_a1 / 12)


def lp(x: np.ndarray, cutoff: float, sr: int, stages: int = 4) -> np.ndarray:
    """Cascaded one-pole low-pass, done in the frequency domain so it's instant."""
    n = 1 << (len(x) - 1).bit_length()
    X = np.fft.rfft(x, n)
    f = np.fft.rfftfreq(n, 1 / sr)
    H = 1.0 / (1.0 + (f / cutoff) ** 2) ** (stages / 2)
    return np.fft.irfft(X * H, n)[: len(x)]


def bp(x: np.ndarray, lo: float, hi: float, sr: int) -> np.ndarray:
    n = 1 << (len(x) - 1).bit_length()
    X = np.fft.rfft(x, n)
    f = np.fft.rfftfreq(n, 1 / sr)
    H = (1.0 / (1.0 + (f / hi) ** 2)) * (1.0 - 1.0 / (1.0 + (f / lo) ** 2))
    return np.fft.irfft(X * H, n)[: len(x)]


def seg_env(n: int, attack: float, decay: float, sr: int) -> np.ndarray:
    a = max(1, int(attack * sr))
    e = np.ones(n)
    e[:a] = np.linspace(0, 1, a)
    tail = min(max(1, int(decay * sr)), n)
    e[-tail:] *= np.linspace(1, 0, tail) ** 1.6
    return e


def ramp(u: np.ndarray, a: float, b: float) -> np.ndarray:
    """Smooth 0->1 across the normalised-time window [a, b]."""
    x = np.clip((u - a) / max(1e-6, b - a), 0, 1)
    return 0.5 - 0.5 * np.cos(np.pi * x)


def add(buf: np.ndarray, start: int, sig: np.ndarray) -> None:
    if start >= len(buf) or start < 0:
        return
    end = min(len(buf), start + len(sig))
    buf[start:end] += sig[: end - start]


def synth(seconds=60.0, bpm=72, key="A", motif=0.7, pulse=0.7, bright=0.45,
          build=0.35, sr=44100, seed=7):
    rng = np.random.default_rng(seed)
    n = int(seconds * sr)
    t = np.arange(n) / sr
    u = t / seconds  # normalised time, drives the arrangement
    root = NOTES[key[0].upper()] + (1 if key.endswith("#") else -1 if key.endswith("b") else 0)
    root -= 9

    beat = 60.0 / bpm
    bar = beat * 4
    chord_len = bar * 2

    drone = np.zeros(n)
    pad_dark = np.zeros(n)
    pad_open = np.zeros(n)
    cello = np.zeros(n)
    bell = np.zeros(n)
    sub = np.zeros(n)
    tick = np.zeros(n)
    hit = np.zeros(n)

    for c in range(int(np.ceil(seconds / chord_len))):
        deg, qual = PROGRESSION[c % len(PROGRESSION)]
        s0 = int(c * chord_len * sr)
        if s0 >= n:
            break
        s1 = min(n, int((c + 1) * chord_len * sr + 1.6 * sr))  # overlap so chords crossfade
        seg = s1 - s0
        ts = np.arange(seg) / sr
        e = seg_env(seg, 1.4, 2.2, sr)

        # Drone: root, octave and fifth in the 55-110 Hz register. Most of the track.
        for k, amp in ((0, 1.0), (12, 0.42), (7, 0.30)):
            add(drone, s0, amp * e * np.sin(2 * np.pi * hz(root + deg + k) * ts + rng.uniform(0, 6.28)))

        # Pad: the triad two octaves up, rendered twice so the filter can open
        # across the build instead of sitting at one static colour.
        chord = np.zeros(seg)
        for k in TRIAD[qual]:
            f = hz(root + deg + k + 24)
            det = rng.uniform(-0.12, 0.12)
            chord += 0.30 * e * (
                np.sin(2 * np.pi * (f + det) * ts) + 0.5 * np.sin(2 * np.pi * 2 * f * ts)
            )
        add(pad_dark, s0, chord)
        add(pad_open, s0, chord)

        # Motif: a plucked cello figure, same shape every chord, transposed.
        third = 15 if qual == "min" else 16
        for pos, iv in MOTIF:
            iv = third if iv == 15 else iv
            ns = s0 + int(pos * beat * sr)
            ln = min(int(1.5 * sr), n - ns)
            if ln <= 0:
                continue
            nt = np.arange(ln) / sr
            f = hz(root + deg + iv)
            body = (
                np.sin(2 * np.pi * f * nt)
                + 0.45 * np.sin(2 * np.pi * 2 * f * nt)
                + 0.18 * np.sin(2 * np.pi * 3 * f * nt)
            )
            add(cello, ns, np.exp(-nt * 3.1) * np.clip(nt / 0.012, 0, 1) * body)

        # Bell: one sparse chord tone, the only thing with any sparkle.
        k = TRIAD[qual][rng.integers(0, 3)]
        f = hz(root + deg + k + 36)
        bs = s0 + int(rng.uniform(0.2, 1.1) * sr)
        bl = min(int(2.6 * sr), n - bs)
        if bl > 0:
            bt = np.arange(bl) / sr
            add(bell, bs, np.exp(-bt * 2.4) * (
                np.sin(2 * np.pi * f * bt) + 0.32 * np.sin(2 * np.pi * 2.76 * f * bt)
            ))

        # A low hit on each chord change: felt, not heard.
        hl = min(int(1.2 * sr), n - s0)
        if hl > 0:
            ht = np.arange(hl) / sr
            add(hit, s0, np.exp(-ht * 4.2) * np.sin(
                2 * np.pi * hz(root + deg) * ht * (1 + 0.5 * np.exp(-ht * 16))
            ))

    # Sub pulse on every downbeat.
    for b in range(int(seconds / bar) + 1):
        s0 = int(b * bar * sr)
        ln = min(int(0.55 * sr), n - s0)
        if ln <= 0:
            break
        bt = np.arange(ln) / sr
        add(sub, s0, np.exp(-bt * 7.0) * np.sin(
            2 * np.pi * hz(root) * bt * (1 + 0.35 * np.exp(-bt * 22))
        ))

    # Eighth-note tick: motion, kept low in the spectrum so it never meets the voice.
    for i in range(int(seconds / (beat / 2)) + 1):
        s0 = int(i * (beat / 2) * sr)
        ln = min(int(0.16 * sr), n - s0)
        if ln <= 0:
            break
        bt = np.arange(ln) / sr
        strong = 1.0 if i % 2 == 0 else 0.5
        add(tick, s0, strong * np.exp(-bt * 26) * np.sin(2 * np.pi * hz(root + 24) * bt))

    air = lp(rng.standard_normal(n), 140, sr, 2)

    # Riser into the last third, then gone.
    riser = bp(rng.standard_normal(n), 180, 900, sr) * ramp(u, 0.50, 0.70) * (1 - ramp(u, 0.70, 0.78))

    # Carve for the voice.
    drone = lp(drone, 190, sr, 4)
    pad_dark = lp(pad_dark, 520, sr, 5)
    pad_open = lp(pad_open, 1250, sr, 5)
    cello = lp(cello, 1300, sr, 4)
    bell = lp(bell, 3600, sr, 2)
    sub = lp(sub, 120, sr, 3)
    tick = lp(tick, 700, sr, 3)
    hit = lp(hit, 150, sr, 3)

    def nrm(x):
        p = np.abs(x).max()
        return x / p if p > 0 else x

    # The arrangement: what is playing, and when.
    #
    # These are FRACTIONS OF THE WHOLE PIECE, so on a 65-second film a curve that
    # reaches full at 0.20 is silent for the first thirteen seconds. Bring the
    # musical parts in early and keep a floor under them: an opening that is pure
    # sub-bass drone reads as "there is no music" on any speaker without a woofer.
    g_pad = 0.45 + 0.55 * ramp(u, 0.00, 0.08)
    g_open = ramp(u, 0.10, 0.70)  # the pad's filter opening across the build
    g_cello = ramp(u, 0.05, 0.15) * (1 - 0.7 * ramp(u, 0.90, 1.00))
    g_tick = ramp(u, 0.20, 0.32) * (1 - ramp(u, 0.86, 0.96))
    g_sub = ramp(u, 0.02, 0.10)
    g_bell = 0.6 + 0.4 * ramp(u, 0.05, 0.35)

    pad = pad_dark * (1 - g_open) + pad_open * g_open

    # Weighted for AUDIBILITY, not for a spectrum plot. A bed that is 90% sub-bass
    # measures beautifully against a reference cue and is silent on a laptop.
    # The parts above 250 Hz carry the track; the drone only underpins it.
    mix = (
        0.42 * nrm(drone)
        + 0.90 * nrm(pad) * g_pad
        + motif * 0.80 * nrm(cello) * g_cello
        + bright * 0.55 * nrm(bell) * g_bell
        + 0.24 * nrm(sub) * g_sub
        + pulse * 0.26 * nrm(tick) * g_tick
        + 0.20 * nrm(hit)
        + 0.16 * nrm(riser)
        + 0.04 * nrm(air)
    )

    curve = 1 - build + build * (0.5 - 0.5 * np.cos(np.pi * np.clip(u / 0.82, 0, 1)))
    curve *= np.clip((seconds - t) / 2.6, 0, 1)
    curve *= np.clip(t / 1.1, 0, 1)
    mix *= curve

    delay = int(0.011 * sr)
    right = np.concatenate([np.zeros(delay), mix[:-delay]])
    stereo = np.stack([mix, 0.86 * mix + 0.14 * right], axis=1)

    peak = np.abs(stereo).max()
    if peak > 0:
        stereo = stereo / peak * 0.72
    return stereo


def write_wav(path, stereo, sr):
    data = (np.clip(stereo, -1, 1) * 32767).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(data.tobytes())


def report(stereo, sr):
    x = stereo.mean(axis=1)
    N = 8192
    spec = np.zeros(N // 2 + 1)
    for i in range(0, len(x) - N, N // 2):
        spec += np.abs(np.fft.rfft(x[i : i + N] * np.hanning(N))) ** 2
    f = np.fft.rfftfreq(N, 1 / sr)
    tot = spec.sum()
    below = 100 * spec[f < 250].sum() / tot
    voice = 100 * spec[(f >= 200) & (f < 4000)].sum() / tot
    # What a laptop or phone speaker actually reproduces, in dB relative to the
    # full-band level. This is the number that decides whether anyone hears it.
    import numpy as _np
    rms_all = _np.sqrt((x ** 2).mean())
    hi = _np.fft.rfft(x)
    ff = _np.fft.rfftfreq(len(x), 1 / sr)
    hi[ff < 250] = 0
    xh = _np.fft.irfft(hi, len(x))
    rms_hi = _np.sqrt((xh ** 2).mean())
    drop = 20 * _np.log10(max(rms_hi, 1e-9) / max(rms_all, 1e-9))
    print(f"  energy below 250 Hz     : {below:5.1f}%")
    print(f"  energy in 200-4000 Hz   : {voice:5.1f}%")
    print(f"  small-speaker penalty   : {drop:5.1f} dB  (how much is lost above 250 Hz)")
    for label, frac in (("10%", 0.10), ("35%", 0.35), ("65%", 0.65), ("90%", 0.90)):
        i0 = int(len(x) * frac)
        w = x[i0 : i0 + sr * 2]
        if len(w) < 1024:
            continue
        W = _np.fft.rfft(w)
        fw = _np.fft.rfftfreq(len(w), 1 / sr)
        W[fw < 250] = 0
        lv = 20 * _np.log10(max(_np.sqrt((_np.fft.irfft(W, len(w)) ** 2).mean()), 1e-9))
        flag = "  <-- nothing audible here" if lv < -40 else ""
        print(f"  audible level at {label:>3} through : {lv:6.1f} dB{flag}")
    if drop < -14:
        print("  ! inaudible on a laptop — raise --bright/--motif, it is too sub-heavy")
    if voice > 45:
        print("  ! now crowding the voice — ease off --bright")


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        print(__doc__)
        raise SystemExit(2)
    out = a[0]
    fl = {a[i]: a[i + 1] for i in range(len(a)) if a[i].startswith("--") and i + 1 < len(a)}
    sr = int(fl.get("--sr", 44100))
    s = synth(
        seconds=float(fl.get("--seconds", 60)),
        bpm=int(fl.get("--bpm", 72)),
        key=fl.get("--key", "A"),
        motif=float(fl.get("--motif", 0.7)),
        pulse=float(fl.get("--pulse", 0.7)),
        bright=float(fl.get("--bright", 0.45)),
        build=float(fl.get("--build", 0.35)),
        seed=int(fl.get("--seed", 7)),
        sr=sr,
    )
    write_wav(out, s, sr)
    print(f"  wrote {out}  ({len(s)/sr:.1f}s)")
    report(s, sr)
