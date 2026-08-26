# Real subject cutouts (Stage 3.5)

Anything SPECIFIC — a named person, a real place, a real object — should be a **real
photograph**, cut out and given a white sticker border, not an AI illustration of it.
Generated "a politician at a podium" is generic; the actual photo of the actual moment
is the thing that makes the film feel researched.

## 1. Source a real, licensed image

Use Wikimedia Commons (`_tools/commons.py` pattern: `search()` -> filter to CC0 / public
domain / CC BY -> `fetch()`). US federal government photos (White House, VOA, Congress)
are public domain and are usually the best option for American political subjects.
Record what you used and its licence in `photos/credits.json`.

## 2. Lift the subject with Vision (macOS)

`_tools/subject_cutout.swift` — a CLI port of Apple's subject-lift, the same API the
Barrier app uses in `barrier_swiftui/Helpers/SubjectExtractor.swift`:

```
VNGenerateForegroundInstanceMaskRequest
  -> results.first
  -> pick the most prominent instance when allInstances.count > 1
  -> generateMaskedImage(ofInstances:from:croppedToInstancesExtent: true)
  -> transparent PNG
```

```bash
swiftc -O subject_cutout.swift -o subject_cutout
./subject_cutout photos/obama_2004.png cutouts/obama_2004.png
```

## 3. Sticker treatment

`_tools/sticker.py` — dilate the alpha into a white silhouette, add a soft drop shadow.

**Two bugs that will bite you, both already fixed in the script:**
- The Vision cutout is cropped tight to the subject, so you MUST paste the alpha onto a
  larger padded canvas BEFORE dilating, or the border is clipped off at the edges and
  nothing appears to change no matter how large you set `border`.
- `ImageFilter.MaxFilter` does not dilate reliably at large kernel sizes. Use
  blur-then-threshold instead — it also rounds the corners, which is what a real
  die-cut sticker edge looks like.

Default `border=52` at ~1400px. Thinner than ~40 reads as a cheap masking job.

## 4. CRITICAL: the video model will not animate real people

Image-to-video **fails on identifiable public figures** — a deepfake guardrail. In testing,
every beat containing a photo of Obama failed while the identical call on a campaign sign
succeeded. Do not try to work around it. Instead:

1. Generate the keyframe as a **people-free background** with deliberate empty negative
   space ("ABSOLUTELY NO PEOPLE... leave empty space in the centre").
2. Animate that background with the video model.
3. Composite the sticker locally in ffmpeg with its own push-in, so the photo only
   translates and scales as a rigid sticker and the face can never warp:

```
[N:v]scale=w='W0*(1+GROW*t)':h='H0*(1+GROW*t)':eval=frame,format=rgba[s]
[base][s]overlay=x='CX-w/2':y='CY-h/2'
```

See `STICKERS` and `build_sticker_beat()` in the project's assembler for a working map of
beat id -> [(sticker, x_frac, y_frac, height_frac, grow_per_sec, greyscale)].
