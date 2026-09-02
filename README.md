# vox

Two Claude Code skills for turning one researched topic into a finished
narrated film. Same editorial register, two different ways of building it.

| | `vox-skill` | `vox-editorial` |
|---|---|---|
| **Look** | Paper collage, halftone cut-outs, offset red marker stroke | Cut paper, saturated grounds, scissored subjects |
| **Built with** | Remotion — React that renders video | Python + ffmpeg |
| **Frame** | 1920×1080, or 1080×1920 on request | 1080×1920 |
| **Charts, documents, newspapers** | Drawn in code, animate natively | Drawn locally with PIL |
| **Sprites** | Public-domain images, lifted locally with Vision | Generated, one subject per sprite |
| **Cost** | Free. Narration, music and every rebuild are local. | Sprite generation only |

Both are editorial journalism, not advertising: they earn the next five seconds
by being genuinely interesting rather than by shouting. Both are free to run —
narration comes from Edge neural TTS and everything else happens on your machine.

---

## `skills/vox-skill` — Remotion

![the founding of Baylor University](skills/vox-skill/docs/baylor.gif)

*Full film: [`baylor-founding.mp4`](skills/vox-skill/docs/baylor-founding.mp4) · 65s · 1920×1080*

Everything in that frame except the three portraits is drawn in code: the state
outline, the flag, the charter, the wax seals, the fifteen-card grid, the stamps,
the timeline. The portraits are public-domain scans lifted with the macOS Vision
framework and screened into halftone locally.

![stills](skills/vox-skill/docs/stills.jpg)

The thing that makes it work is that **the narration is the clock**. The
voiceover is generated first, and every scene length and every animation cue is
derived from its word boundaries — so a scene starts when a word is spoken, not
when a number in a file says so. Change the voice and the whole film re-times
itself with one command.

It also ships a music generator. A real documentary cue was measured to find what
the genre actually is, spectrally, and the bed is synthesised to match and then
sidechain-ducked under the narration.

[Read the skill →](skills/vox-skill/)

---

## `skills/vox-editorial` — ffmpeg

![a film about JC Builds](skills/vox-editorial/docs/jc-builds.gif)

*Full film: [`jc-builds.mp4`](skills/vox-editorial/docs/jc-builds.mp4) · 49s*

Generates **elements, not posters**. The image model only ever draws subjects,
spaced out on a keyable field; the ground, the tape, the newsprint and the
headline are drawn locally and composed across depth planes. Depth then drives
parallax, drift and draw order at once, which is what the eye reads as space.

![Tokyo](skills/vox-editorial/docs/tokyo.gif)

[Read the skill →](skills/vox-editorial/)

---

## Install

Copy the one you want into your skills directory:

```bash
git clone https://github.com/jaredcassoutt/vox-editorial.git
cp -R vox-editorial/skills/vox-skill ~/.claude/skills/
# or
cp -R vox-editorial/skills/vox-editorial ~/.claude/skills/
```

> **Layout note.** This repo used to hold `vox-editorial` at the root. It now
> holds both skills under `skills/`. If you installed before, re-copy from the
> new path.

## Requirements

Both need `ffmpeg` and Python 3 with `numpy`, `pillow` and `edge-tts`.
`vox-skill` also needs Node and, for local subject cut-outs, macOS with Xcode
command line tools.

## Licence

MIT. See [`LICENSE`](skills/vox-editorial/LICENSE) and [`NOTICE`](skills/vox-editorial/NOTICE).
