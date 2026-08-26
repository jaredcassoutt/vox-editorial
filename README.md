# vox-editorial

**A Claude Code skill that turns one researched topic into a finished vertical explainer
film** — script, narration, cut-paper artwork, multiplane animation, captions and a music
bed, assembled locally with ffmpeg.

Editorial register: it holds attention by being genuinely interesting, not by selling.

---

## It made a video about me, which I am definitely not being weird about 😂

I pointed it at my own Twitter account and let it read my Highlights. It came back with a
better summary of what I've been building than I'd have written myself, and then made a
film out of it. Shameless self-promotion, but in my defence it was the machine's idea.

![a film about JC Builds](docs/jc-builds.gif)

*Full film: [`docs/jc-builds.mp4`](docs/jc-builds.mp4) · 49s · that's me, [@jc_builds](https://twitter.com/jc_builds) 👋*

The opening line never says who it's about:

> *"Turn on airplane mode and every AI app on your phone stops working. His keep going."*

That's the skill's hook rule at work — withhold the subject, open on a premise the viewer
can verify from their own pocket, then break it and don't settle the debt until the final
line. The question it owes is *how is that possible*, and the closing beat answers exactly
that.

It found the through-line on its own, too: almost every "AI app" is a thin wrapper around
someone else's server, and I keep shipping the opposite. The 4,096-token model planning a
trip with no API calls, the coding agent that writes Swift on-device and repairs its own
errors, the photo library matched against 164 landmarks. I didn't feed it any of that.

---

## And here's one that isn't about me

![Tokyo](docs/tokyo.gif)

*Full film: [`docs/tokyo.mp4`](docs/tokyo.mp4) · 29s*

> Tokyo started as a fishing village called Edo. By 1720 it had a million people — the
> largest city on earth, bigger than London, bigger than Paris. And almost all of it was
> built of wood and paper. It burned down roughly every twenty years. Each time, they
> rebuilt it. You are walking on the fourth or fifth version of the same city.

![stills from other films in the series](docs/stills.jpg)

---

## The one idea this is built on

**Generate elements, not posters.**

Most collage pipelines generate a finished composition per beat and then animate pieces
of it. It looks flat every single time — and the reason isn't the motion. The original
composition is still sitting underneath, so a "moving" element is sliding over an
identical copy of itself. Nothing can move *behind* anything, because there is no behind.

So here the image model never draws a composition. It draws the **subjects only**, spaced
apart on a flat magenta field, which is keyed to true alpha. The ground, the confetti, the
tape, the newsprint and the headline are all drawn locally. The scene is then assembled
onto an empty sheet across depth planes:

```
0.05  ground              barely moves
0.20  clippings, tape
0.40  rear confetti
0.60  secondary subject
0.80  primary subject
1.00  front confetti      largest, fastest
1.15  headline            nearest the lens
```

Depth drives three things at once: parallax rate against the camera, drift amplitude, and
draw order. That differential is what the eye reads as space. Every layer also carries its
own entrance, drift, breath and rotation phase, so no two elements ever move together. A
typical beat runs **28–36 independent layers**.

---

## What it costs

Almost nothing, by design.

| stage | cost |
| --- | --- |
| research + script | free |
| narration | **free** — Edge neural TTS, no API key |
| subject sprites | the only real spend, and the bundled library covers most films |
| grounds, banners, confetti, tape, newsprint, numerals | **free** — drawn locally |
| animation, captions, mixing, mastering | **free** — local Python + ffmpeg |
| every rebuild after the first | **free** |

The bundled `library/` ships 18 tagged, alpha-keyed sprites. Check it before generating
anything: **cache what is expensive, draw what is cheap.**

---

## Quick start

Requirements: `ffmpeg`, `ffprobe`, Python 3.10+ with `pillow` and `numpy`.

Free narration:

```bash
uv venv ~/.local/tts-venv --python 3.12
source ~/.local/tts-venv/bin/activate && uv pip install edge-tts
```

Drop the folder into `~/.claude/skills/` and ask for an explainer about anything. The
skill handles research → script → narration → artwork → animation → assembly.

---

## Things it learned the hard way

Each of these was a visible defect in a real cut before it became a rule.

- **A continuation cut must not replay its effect.** Split one narration line across two
  shots and the second must render the *settled* state, or the reveal runs twice.
- **Lock wide headline banners.** Let a decomposer split a headline into pieces that drift
  independently and the layout appears to fall apart.
- **Measure text the way you draw it.** Per-letter colouring loses kerning, so a line
  measured with `textlength(whole_string)` overruns the paper it sits on.
- **The ground never fades in**, or the beat opens on black.
- **Master to −14 LUFS.** Platforms normalise, so a quiet master gets pushed up along with
  its noise floor.
- **Verify sourced imagery is on-topic.** Image search returns confidently wrong results —
  a building in the wrong country, a stamp *of* a thing instead of the thing.
- **Grade with numbers, not vibes.** Length, seconds-per-cut, audio peak and RMS,
  near-silent windows. Each catches something the eye misses.

---

## Licence

MIT. Forked from [vox-explainer-skill](https://github.com/CK42BB/vox-explainer-skill) by
Kingsley, also MIT — see [`NOTICE`](NOTICE) for exactly what's inherited and what's new.
The short version: the premise is theirs, the artwork inversion and everything downstream
of it is mine.
