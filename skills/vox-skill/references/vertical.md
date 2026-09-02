# Vertical / TikTok (1080×1920)

Same visual system, different frame. Scaffold with `--vertical` and the
composition is 1080×1920 at 30fps.

```bash
scripts/scaffold.sh ~/Desktop/my-film MyFilmSequence --vertical
```

## What actually changes

The layer model, the palette, the red marker stroke and the motion rules are
identical. Four things are not.

### 1. The frame is 44% narrower

At 1920 wide you can put three portraits in a row. At 1080 you cannot: each gets
about 340px and the faces stop reading. **Rows become stacks, or become
sequences.** Three founders in landscape is one shot; in vertical it is either a
vertical column of three or three consecutive beats each holding one portrait.
Prefer the sequence — one subject at a time is the format's native grammar.

Type does not scale with the frame. Because the frame is narrower, headline
sizes go *up* relative to width, not down. A 46px kicker at 1920 becomes ~64px
at 1080 or it reads as fine print on a phone.

### 2. There are three dead zones

The platform draws its own interface over your video. Content that lands there
is covered.

| Zone | Reserve |
|---|---|
| Top | 180px — status bar, "Following / For You" |
| Bottom | 420px — caption, username, music ticker |
| Right | 150px — like, comment, share, spinning disc |

That leaves roughly 930 × 1320 of usable frame, offset upward and left. Compose
inside it. `useLayout()` returns these as `safe`, and the composition's centre of
attention should be `safe.cy`, which sits above the geometric centre.

The foreground band still anchors the bottom of the composition, but it now sits
*above* the bottom dead zone rather than at the frame edge, or it reads as part
of the platform's own chrome.

### 3. Captions are not optional

Most of the audience has the sound off. A vertical cut without burned captions
is a silent film. Generate them from the same word boundaries that drive
everything else:

```bash
python3 scripts/captions.py            # writes src/shared/captions.ts
```

Then render `<Captions />` from `shared/system` at `zIndex 40`. It shows two to
four words at a time, snapped to word boundaries, in Arial Black over a soft ink
plate, positioned just above the bottom dead zone.

Do not caption the whole sentence at once. Short groups that change on the beat
are what holds the eye.

### 4. The first second carries the whole video

Landscape gives you a title card and a slow build. Vertical does not: the viewer
decides in about a second. Open on the strongest image with the hook already
burned in as a caption. Move the reveal earlier than feels right.

## Reusing a landscape film

Every scene takes position props, so a lot survives. The mechanical part is:

- Halve the x offsets, or set them to 0 and stack instead.
- Move `bottom` values up by the bottom dead zone.
- Raise type by roughly 1.4×.
- Re-time nothing. The cues come from `vo/timing.json` and are aspect-independent.

The part that does not survive is any shot built as a row. Rebuild those as a
stack or split them across beats.

## Thumbnail

`pick_thumbnail.py` works on either aspect. On vertical, pass `--grid 5` — a 7×7
grid on a tall frame puts too many cells inside the dead zones and biases the
score toward frames with content behind the platform's own interface.
