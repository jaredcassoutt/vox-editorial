---
name: vox-skill
description: Use when building a narrated, voiceover-synced motion-graphics explainer or B-roll film in Remotion — paper-texture collage, cut-out subjects with an offset red marker stroke, code-drawn charts, newspapers, documents and typewriter reveals. Horizontal 1920x1080 by default, vertical 1080x1920 for TikTok, Reels and Shorts on request. Triggers on "make a vox style video", "vox editorial video", "b-roll sequence", "Remotion explainer", "documentary motion graphics about X", "turn this script into a video", "make a TikTok explainer". Not for hard-sell product ads (use fastcut-ad).
---

# Remotion paper B-roll

One topic in, one 1920×1080 narrated film out, built as React. The register is
editorial documentary: it holds attention by being genuinely interesting, not by
shouting.

Everything animates because code moves it. There is no After Effects step, no
timeline to drag. You direct the film by writing components and tuning props.

## Pick the right skill first

| You want | Use |
|---|---|
| Horizontal 1920×1080, React/Remotion, code-drawn charts and newspapers | **this skill** |
| Vertical 1080×1920 for TikTok, Reels or Shorts | **this skill**, `--vertical` — see `references/vertical.md` |
| Any narrated explainer where the pipeline choice is open | `explainer-studio` |
| Fast-cut product ad with sound design | `fastcut-ad` |

## What decides quality, in order

1. **The fact you build on.** One genuinely surprising, checkable reversal. Without it the film has no reason to exist and no craft rescues it.
2. **The narration.** It is the clock and the spine. Every cut is timed to a spoken word.
3. **Depth.** Whether the frame has three layers moving against each other.
4. **Everything else.**

Spend effort in that order.

## The pipeline

Ten phases. Do not start phase N+1 before phase N produces its artifact.

### 1. Find the reversal, write the beats

Find the thing that turns out to be the opposite of what a viewer assumes. Not a
statistic, a contradiction.

Write **8 to 12 beats, one idea per line**. The script IS the timeline. A beat is
one sentence or one clause that can carry one image.

**The hook is beat 1 and it withholds the subject.** No proper nouns in it: no
country, no person, no institution, no year. It states something that cannot be
right. The final beat answers that exact question. Test a draft with two
questions. Can the viewer name the subject from the hook? If yes, rewrite. Does
the last line pay the debt the hook created? If not, one of the two is wrong.

Write the beats into `script.json`:

```json
{"topic": "...", "beats": [{"id": 1, "narration": "This university is older than the state it stands in."}]}
```

### 2. Voice first, then timing

The voiceover is generated **before** any animation, because its duration decides
every frame count.

```bash
python3 -m venv .venv && ./.venv/bin/pip install -q edge-tts
./.venv/bin/python ~/.claude/skills/vox-skill/scripts/gen_vo.py
```

This writes `vo/beat_NN.mp3`, one joined `public/audio/vo.mp3`, and
`vo/timing.json` holding per-beat start, end, duration, frame windows and
word-level boundaries. Every duration downstream is read from that file. Never
guess a frame count.

Voice defaults to `en-GB-RyanNeural` at `+4%`. Override with `VOICE=` and
`RATE=`. Worth auditioning before you commit, because re-voicing after the film
is built is only cheap if you did step 3:

| Voice | Register |
|---|---|
| `en-US-AndrewMultilingualNeural` | newer HD model, warm and confident. The best default. |
| `en-US-ChristopherNeural` | tagged "reliable, authority". The classic narrator. |
| `en-GB-RyanNeural` / `en-GB-ThomasNeural` | British, drier |
| `en-US-SteffanNeural` | closest to a straight news read |

**The voice model matters less than the mastering.** See phase 6.

### 3. Make the timings derived, not typed

Hand-tuning frame numbers against a waveform works exactly once. Change the
voice, the rate or one word and every number is wrong.

Write `cues.json` naming the **word** each element lands on, then generate a
timing module from it:

```bash
python3 ~/.claude/skills/vox-skill/scripts/sync_timing.py --check   # inspect
python3 ~/.claude/skills/vox-skill/scripts/sync_timing.py           # write src/shared/timing.ts
```

Scenes import `D` for their lengths and `CUE` for every start frame. Re-voicing
is then three commands and a render, not an afternoon. `--check` also
bounds-checks every cue against its scene length.

### 4. Map beats to scenes

**Fewer scenes than beats.** Two or three beats often share one held image, and a
scene that holds while narration continues reads as confidence. Seven scenes for
ten beats is a good ratio.

A scene's duration is the sum of its beats' frame windows, taken from
`vo/timing.json`. Write the mapping down before writing any component.

### 5. Produce the assets

Three asset classes, in order of preference.

**Code-drawn (best).** Newspapers, charts, documents, maps, ledgers, typewriter
text, striking-through lists. No files, no keying, infinitely tunable, and they
animate natively. Reach for this first. See `references/scene-patterns.md`.

**Transparent PNG cut-outs.** Subject lifting runs locally through Vision, free
and offline:

```bash
swiftc -O ~/.claude/skills/vox-skill/scripts/cutout.swift -o /tmp/cutout
/tmp/cutout raw/portrait.jpg public/scene-04/portrait.png
python3 ~/.claude/skills/vox-skill/scripts/halftone.py public/scene-04/portrait.png
```

`halftone.py` applies the paper treatment: desaturate, raise contrast, dot
screen, warm the ink. It makes a modern photo sit on 19th-century paper.

If Vision finds no subject, fall back to PIL: flood-fill from the four corners at
tolerance ~55, then keep only the largest connected opaque component so interior
fills such as collars survive. Never seed the flood-fill from mid-edges, it leaks
into a wide subject.

**Transparent video.** Transcode to VP9 with alpha, then `<OffthreadVideo transparent />`:

```bash
ffmpeg -i in.mov -c:v libvpx-vp9 -pix_fmt yuva420p -vf scale=1920:-2 -b:v 0 -crf 32 out.webm
```

Keep the paper background under 5 MB at exactly 1920×1080. A 28 MB background
makes Studio drop frames, and dropped frames drag the audio out of sync while you
tune.

### 6. Build scenes on the locked visual system

Decide the system once, then every scene is a variation on it. Full palette,
type scale and motion rules in `references/visual-system.md`. The three
non-negotiables:

**Every scene is three layers.**

1. **Background** — the same paper texture in every scene, full-cover, `zIndex 0`, with a soft-light wash over it. It never changes. That continuity is what makes seven scenes read as one film.
2. **Midground** — the subject, dropped in as a cut-out, each with an offset red marker stroke.
3. **Foreground** — something that occludes the subject's lower body and anchors the shot.

A scene missing the foreground looks like a slide. The occlusion is what creates
depth.

**The red marker stroke** is the signature. Render a solid-colour silhouette of
the cut-out behind the image, offset a few pixels, mostly horizontally so it
reads on one side:

```tsx
<div aria-hidden style={{
  ...sameBoxAsImg,
  backgroundColor: "#E04329",
  maskImage: `url(${assetUrl})`,      WebkitMaskImage: `url(${assetUrl})`,
  maskSize: "100% 100%",              WebkitMaskSize: "100% 100%",
  maskRepeat: "no-repeat",            WebkitMaskRepeat: "no-repeat",
  transform: `translate(calc(-50% + ${strokeX}px), ${rise + strokeY}px)`,
}}/>
<Img src={assetUrl} style={{ ...sameBoxAsImg, transform: `translate(-50%, ${rise}px)` }} />
```

`strokeX` around ±26, `strokeY` around 8. Mirror the sign so subjects on the left
of frame stroke left and subjects on the right stroke right.

**Elements arrive, they do not fade.** `spring()` a rise from ~390px with
`{damping: 18, mass: 0.75, stiffness: 110}`, crossed with a 16-frame opacity
ramp. Charts and signatures draw on via `interpolate()` over `strokeDashoffset`.
Stagger entrances so no two elements land on the same frame.

**Every scene takes a zod schema with tuned props.** Position, scale and
start/end frame for every element. That is what makes the film adjustable in
Studio instead of a recompile per nudge.

### 7. Score and master the audio

**Judge the bed by what a laptop speaker reproduces, not by its spectrum plot.**

A real documentary cue measures at 93% of its energy below 250 Hz. Copying that
target literally produces a bed that is *silent* on every speaker without a
woofer, because phones and laptops roll off hard below ~200 Hz. Ask how loud the
music is **above 250 Hz** relative to speech above 250 Hz. That single number
decides whether anyone hears it.

    # speech passage vs a gap between lines, both high-passed
    ffmpeg -ss <speech> -t 1.5 -i mix.wav -af "highpass=f=250,volumedetect" -f null /dev/null
    ffmpeg -ss <gap>   -t 0.3 -i mix.wav -af "highpass=f=250,volumedetect" -f null /dev/null

| Separation above 250 Hz | Verdict |
|---|---|
| 30 dB or more | inaudible; the listener will say "there's no music" |
| 18-22 dB | present and unobtrusive. The target. |
| under 8 dB | crowding the narration |

`score.py` prints this as a small-speaker penalty plus the audible level at four
points through the piece, so a silent stretch shows up before you render.

```bash
python3 ~/.claude/skills/vox-skill/scripts/score.py music/bed.wav --seconds <SEQ_SECONDS>
bash   ~/.claude/skills/vox-skill/scripts/mix_audio.sh \
       public/audio/vo.mp3 music/bed.wav /tmp/mix.wav -20
```

`score.py` prints its own spectral balance against those targets. Cut the bed to
the **sequence** length, not the voice length, so it carries the closing hold.

The bed is set with a `music_db` offset and then sidechain-ducked a further
~6 dB while the voice speaks, so it swells back in the gaps rather than sitting
flat. **-18 to -22 dB is the textbook figure and it assumes a full-range mix.**
For a sub-heavy bed it lands 30+ dB down where it counts. Set the offset from
the measured separation above, not from the convention. Around -12 dB is typical
once the bed carries real midrange.

**Watch the arrangement curves on a short film.** They are fractions of the whole
piece, so a part that reaches full at 0.20 is absent for the first thirteen
seconds of a 65-second cut. An opening of pure sub-bass drone reads as "there is
no music", and that is the part everyone judges. Keep a floor under the musical
parts from the start.

`mix_audio.sh` also masters the narration, and that is most of the distance
between "text to speech" and "documentary narration":

| Move | Why |
|---|---|
| high-pass 85 Hz | rumble the voice never uses |
| -2 dB @ 350 Hz | the boxiness every neural TTS has |
| +2.5 dB @ 3 kHz | presence; it is what makes consonants land |
| -3 dB @ 6.8 kHz | de-ess; TTS sibilance is harsher than a real mouth |
| 3:1 compression | quiet clauses sit level with loud ones |
| loudnorm -16 LUFS | sensible on phones and laptops |

Point the composition at the mixed file rather than the raw VO.

### 8. QC on stills before you render

**Render one still per scene and look at them on a contact sheet before
committing to a full render.** A 70-second film is a 10-minute render; a still is
seconds. Every collision, wrap and mis-scale shows up here.

```bash
for f in 200 541 695 1056; do
  npx remotion still src/index.ts <SequenceId> out/qc/f$f.png --frame=$f --log=error
done
ffmpeg -y -i out/qc/f200.png -i out/qc/f541.png -i out/qc/f695.png -i out/qc/f1056.png \
  -filter_complex "[0:v]scale=720:-1[a];[1:v]scale=720:-1[b];[2:v]scale=720:-1[c];[3:v]scale=720:-1[d];\
[a][b]hstack[t];[c][d]hstack[u];[t][u]vstack" out/qc/sheet.png
```

Pick each frame at the moment the scene is fullest, not its first frame. What
this pass reliably catches:

| Symptom | Cause |
|---|---|
| A stamp or label unreadable over a subject | Red on ink. Move it onto clear paper, don't restyle it. |
| Two elements touching | Absolute positions drifted. Move one, don't shrink both. |
| A tracked caption wrapping mid-phrase | Add `whiteSpace: "nowrap"`. |
| A headline breaking across lines | Same fix, plus drop 15–20% of the size. |
| Code-drawn SVG art rendering tiny | The `viewBox` is looser than the path. Bound it to the path's real extent. |
| A shape reading as the wrong object | Silhouettes need width. Narrow shoulders read as a keyhole, not a bust. |

### 9. Assemble and render

Chain the scenes with `<Series>`, one `<Series.Sequence>` per scene at the
duration from step 3.

Position props mirror each `<Composition>`'s `defaultProps`. **Timing props are
retimed in the sequence**, because a scene tuned in isolation is almost always
longer than the beat window it has to fit.

Gate the audio behind a flag so the composition renders silent by default and the
stems ship separately for mixing:

```tsx
const BAKE_AUDIO = false;   // true → VO at 1.0, music ducked to ~0.2, 24f fade in, 50f fade out
```

```bash
npx remotion studio                                              # preview and tune
npx remotion render src/index.ts <SequenceId> out/final.mp4      # render
ffmpeg -i out/final.mp4 -c:v copy -an out/video.mp4              # strip the silent track
```

**Studio can only save prop edits back to disk if** each `<Composition>`'s
`defaultProps` is an inline object literal, not an imported variable, **and** a
`.prettierrc.json` exists at the project root. Both are required. Get this wrong
and every tuning session is lost on reload.

### 10. Pick the poster frame

**Never ship the default thumbnail.** Frame zero of a film built this way is an
empty paper background before anything has entered — the single worst frame in
the file, and the one every player picks.

```bash
python3 ~/.claude/skills/vox-skill/scripts/pick_thumbnail.py \
        out/film.mp4 out/thumbnail.png --embed --report
```

It scores every candidate and takes the busiest, most composed moment.
"Interesting" is defined as **several distinct elements spread across the
frame**, not raw ink coverage — a shot where the dark foreground band fills the
bottom third has high coverage and no interest, so the dominant term is spatial
spread across a grid. Edge density, a capped coverage term and the presence of
the red accent make up the rest.

`--embed` attaches it to the mp4 as cover art. `--report` prints the shortlist so
you can take the runner-up if you prefer it. On a vertical cut pass `--grid 5`,
or the score biases toward frames whose content sits behind the platform's own
interface.

## Quick reference

| Thing | Value |
|---|---|
| Output | 1920×1080, 30fps, MP4 |
| Paper base / ink / red accent | `#DAD9D5` / `#1A1A1A` / `#E04329` |
| Headline type | Arial Black, tight tracking, uppercase |
| Serif type | PlayfairDisplay, PTSerif (newspapers, documents) |
| Typewriter type | SpecialElite (closing lines) |
| Entrance spring | `{damping: 18, mass: 0.75, stiffness: 110}` |
| Rise distance | 360–390px, from below |
| Opacity ramp | 16 frames, `Easing.out(Easing.cubic)` |
| Stroke offset | `strokeX ±26`, `strokeY 8` |
| Drop shadow | `drop-shadow(0 28px 26px rgba(55,45,31,0.28))` |
| Scaffold a project | `scripts/scaffold.sh <dir> <SequenceName>` |
| Music bed | `scripts/score.py out.wav --seconds N` |
| Master + duck | `scripts/mix_audio.sh vo.mp3 bed.wav out.wav -20` |
| Music under voice | set from measured >250 Hz separation, ~18-22 dB. Often -12 dB. |
| Music feels flat | Raise `--motif`, not the level |
| Vertical cut | `scaffold.sh <dir> <Name> --vertical`, then `references/vertical.md` |
| Captions (required on vertical) | `scripts/captions.py` then `<Captions />` |
| Poster frame | `scripts/pick_thumbnail.py out.mp4 --embed` |
| "I can't hear the music" | Measure above 250 Hz before touching the fader |
| Final loudness | -16 LUFS integrated |

## Common mistakes

| Mistake | Fix |
|---|---|
| Guessing frame counts, then fixing sync later | Read every duration from `vo/timing.json`. The VO is the clock. |
| One scene per beat | Merge beats. A held image under continuing narration reads as confidence. |
| Background changes between scenes | It never changes. The locked texture is what unifies the film. |
| No foreground layer | Add the occluding element. Without it the shot is a slide, not a frame. |
| Sourcing an image for something code can draw | Charts, newspapers, documents, maps and lists are always better in code. |
| Everything enters on the same frame | Stagger by 20–30 frames. Simultaneous entrances read as a template. |
| Elements fading in | They spring up. Fades read as generic. |
| `defaultProps` imported from a constant | Inline the object literal or Studio silently discards your tuning. |
| Hard-coding positions instead of props | Every position, scale and frame goes in the zod schema. |
| A 28 MB paper background | Crop and resize to exactly 1920×1080, under 5 MB. |
| Typing frame numbers into scene props | Name the word in cues.json and generate them. Re-voicing must not mean re-tuning. |
| Music picked for the tune | Pick it for the spectrum. If it lives in 200-4000 Hz it fights the voice at any volume. |
| Music at one flat level | Duck it. A bed that swells in the gaps sounds mixed; a flat one sounds pasted on. |
| Shipping raw TTS | Master it. The EQ and compression chain matters more than which voice you chose. |
| Shipping the default thumbnail | Frame zero is an empty background. Run pick_thumbnail.py. |
| A vertical cut with no captions | Sound-off is the default. Burn them in. |
| A row of three subjects in vertical | 340px each. Stack them, or split across beats. |
| Rendering the film to find out how it looks | Contact-sheet the stills first. Ten minutes of render buys nothing a still won't show. |
| A subject with no public-domain likeness | Draw them as an ink form in the same box. Never borrow someone else's face. |

## Red flags

- About to write a scene component before `vo/timing.json` exists
- About to open an image generator for a chart, a document or a map
- The hook names the subject
- The last beat does not answer the question the hook asked
- A scene has two layers
- Reaching for a fade because the spring "looks bouncy" (retune damping, don't fade)
- About to run a full render without having looked at a still from every scene
- Putting an unverifiable number or quotation on screen because the layout wanted one

## Reference

- `references/visual-system.md` — palette, type, motion, the layer model in full
- `references/scene-patterns.md` — seven reusable scene archetypes with working code
- `scripts/gen_vo.py` — narration, word timings, frame windows
- `scripts/cutout.swift` — Vision subject lift to transparent PNG
- `scripts/halftone.py` — paper/halftone treatment for cut-outs
- `scripts/sync_timing.py` — cues.json + timing.json to a TypeScript timing module
- `scripts/score.py` — tense-documentary music bed, spectrally carved for the voice
- `scripts/mix_audio.sh` — narration mastering chain and sidechain duck
- `scripts/pick_thumbnail.py` — choose and embed the busiest frame as the poster
- `scripts/captions.py` — burned captions from the narration's word boundaries
- `scripts/scaffold.sh` — runnable Remotion project skeleton (`--vertical` for 9:16)
- `references/vertical.md` — what changes for TikTok, Reels and Shorts
