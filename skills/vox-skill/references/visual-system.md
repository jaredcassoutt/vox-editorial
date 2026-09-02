# The locked visual system

Decide all of this once, at the start. Every scene is then a variation on it
rather than a new design. Consistency is what makes seven scenes read as one
film instead of seven slides.

## Palette

| Role | Hex | Where |
|---|---|---|
| Paper base | `#DAD9D5` | the `AbsoluteFill` under the texture |
| Ink / near-black | `#1A1A1A` | headlines, numbers, rules |
| Deep ink (serif) | `#16110D` | newspaper and document body text |
| **Red marker** | `#E04329` | the signature stroke, strike-throughs, underlines |
| Orange accent | `#E85D24` | chart lines, bars |
| Orange accent 2 | `#E8741E` | second data series |
| Highlighter | `#F5C518` | amber sweep over a phrase |
| Shadow | `rgba(55, 45, 31, 0.28)` | every drop-shadow |

Do not add a colour. Four inks and a paper is the whole system. If a scene needs
emphasis, use the red, use scale, or use motion.

## Type

| Face | Use |
|---|---|
| Arial Black | headlines, big numbers, labels. Uppercase, `letterSpacing: -1` to `-3` |
| Montserrat | counters and small caps metadata |
| PlayfairDisplay | newspaper mastheads, document titles |
| PTSerif | newspaper body, article text |
| SpecialElite | typewriter reveals, closing lines |
| Bangers | comic speech bubbles |

Load through `@remotion/google-fonts`. Arial Black is a system face, no load
needed.

Sizes that work at 1920×1080: headline 150–220px, sub-headline 64–86px, label
34–44px, body serif 26–30px, metadata 20–24px.

## The layer model

Every scene, without exception:

```
zIndex  0   background.png        objectFit: cover, never changes across scenes
zIndex  2   soft-light wash       linear + radial gradient, mixBlendMode soft-light
zIndex 10   midground stroke      red silhouette, offset
zIndex 12   midground subject     the cut-out itself
zIndex 20   code-drawn overlays   charts, labels, headlines
zIndex 24   foreground            occludes the subject's lower body
zIndex 30   vignette              only on the closing scene
```

The wash, verbatim:

```tsx
<AbsoluteFill aria-hidden style={{
  background:
    "linear-gradient(180deg, rgba(255,255,255,0.06), rgba(63,54,42,0.12)), " +
    "radial-gradient(circle at 50% 72%, rgba(255,255,255,0.18), transparent 38%)",
  mixBlendMode: "soft-light",
  pointerEvents: "none",
  zIndex: 2,
}}/>
```

**The foreground is the layer people skip and it is the one that creates depth.**
It must overlap the midground subject, usually cropping them at the waist or
knee. A building facade, a desk edge, a torn paper band, a ledger, a barrel. It
enters first, before the subjects, so they appear to rise behind something that
is already there.

## Motion

**The entrance.** One helper, used by every element:

```tsx
const getEntrance = (frame: number, fps: number, startFrame: number, endFrame: number) => {
  const durationInFrames = Math.max(1, endFrame - startFrame);
  const progress = spring({
    frame: frame - startFrame,
    fps,
    config: { damping: 18, mass: 0.75, stiffness: 110 },
    durationInFrames,
  });
  const opacity = interpolate(frame, [startFrame, startFrame + 16], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
  return { opacity, progress };
};

const rise = interpolate(progress, [0, 1], [390, 0], {
  extrapolateLeft: "clamp", extrapolateRight: "clamp",
});
```

Apply as `transform: translate(-50%, ${rise}px)` with
`transformOrigin: "center bottom"`.

**Stagger.** No two elements land on the same frame. Foreground first, then the
midground subjects 20–30 frames apart, then the code-drawn label last. In a tight
beat under four seconds, compress the windows rather than dropping the stagger.

**Draw-on.** Charts, signatures, underlines and borders draw rather than appear:

```tsx
const draw = interpolate(frame, [start, end], [1, 0], {
  extrapolateLeft: "clamp", extrapolateRight: "clamp",
  easing: Easing.inOut(Easing.cubic),
});
<path d={d} stroke="#E85D24" strokeWidth={7} fill="none"
  pathLength={1} strokeDasharray={1} strokeDashoffset={draw} />
```

`pathLength={1}` normalises any path to a unit length, so one interpolation
drives every path regardless of its real length.

**Counters** land on the word. If narration says "one hundred and sixteen
dollars" at 17.4s, the counter finishes at frame `Math.round(17.4 * 30)`, not a
frame later. Read the word boundary out of `vo/timing.json`.

**Held end-states are allowed and often right.** When a scene carries two beats,
the second beat frequently plays over the finished frame with nothing new
entering. Resist filling that space.

## Micro-detail that sells the paper

- Rotate flat elements 0.4–1.2 degrees. Nothing on paper is square.
- Give every cut-out and every card the shared drop shadow.
- Let one element bleed past the frame edge. A perfectly contained composition looks like a slide.
- Torn-edge cards: a `clipPath` polygon with 12–20 slightly jittered points along one edge beats a straight edge.
- Grain: a low-opacity repeating radial-gradient at `mixBlendMode: "multiply"` over the whole frame, `opacity: 0.05`.
