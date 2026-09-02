# Scene archetypes

Seven patterns that cover most editorial B-roll. Each is a starting point, not a
template to fill in. Every one assumes the shared `getEntrance` helper and the
palette from `visual-system.md`.

Reach for a **code-drawn** pattern before you go looking for an image. Charts,
newspapers, documents, maps, ledgers and lists are always better in code: they
animate natively, they tune instantly, and they never need keying.

---

## 1. Portrait row — cut-outs with the marker stroke

The workhorse. One to three subjects rise behind a foreground that crops them.

```tsx
const Portrait: React.FC<{
  asset: string; x: number; y: number; scale: number; width: number;
  startFrame: number; endFrame: number; strokeX: number; strokeY: number;
}> = ({ asset, x, y, scale, width, startFrame, endFrame, strokeX, strokeY }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { opacity, progress } = getEntrance(frame, fps, startFrame, endFrame);
  const rise = interpolate(progress, [0, 1], [390, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const url = staticFile(asset);
  const box = {
    position: "absolute" as const,
    bottom: 330 + y,
    width,
    height: 580,
    opacity,
    objectFit: "contain" as const,
    objectPosition: "center bottom",
    transformOrigin: "center bottom",
  };
  return (
    <>
      <div aria-hidden style={{
        ...box, left: 960 + x + strokeX,
        backgroundColor: "#E04329",
        maskImage: `url(${url})`,     WebkitMaskImage: `url(${url})`,
        maskRepeat: "no-repeat",      WebkitMaskRepeat: "no-repeat",
        maskSize: "100% 100%",        WebkitMaskSize: "100% 100%",
        maskPosition: "center bottom", WebkitMaskPosition: "center bottom",
        opacity: opacity * 0.95,
        transform: `translate(-50%, ${rise + strokeY}px) scale(${scale})`,
        zIndex: 11,
      }}/>
      <Img src={url} style={{
        ...box, left: 960 + x,
        transform: `translate(-50%, ${rise}px) scale(${scale})`,
        filter: "drop-shadow(0 28px 26px rgba(55,45,31,0.28))",
        zIndex: 12,
      }}/>
    </>
  );
};
```

Mirror the stroke sign by side: left subject `strokeX: -26`, right subject
`strokeX: +26`. A centre subject takes `-26`.

Nameplates under a portrait: a rotated card at `zIndex: 22`, Arial Black
uppercase 30px, ink on `#DAD9D5`, a 3px red rule above the text.

---

## 2. Newspaper page — code-drawn, no assets

A serif page on the paper, with an amber highlighter that sweeps across the
phrase that matters.

Structure: masthead (PlayfairDisplay, 96px, letterSpacing `-2`), a rule, a
metadata row (section · site · date, Montserrat 20px, uppercase, tracked `+3`),
the headline (PlayfairDisplay 78px), a deck, a byline, then two columns of body
serif at 26px with `textAlign: justify`.

The highlighter is a `<span>` with a pseudo-band behind it:

```tsx
const sweep = interpolate(frame, [hlStart, hlStart + 18], [0, 1], {
  extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.cubic),
});
<span style={{ position: "relative", display: "inline-block" }}>
  <span aria-hidden style={{
    position: "absolute", left: -6, right: -6, top: "12%", bottom: "8%",
    background: "#F5C518", transformOrigin: "left center",
    transform: `scaleX(${sweep})`, zIndex: -1,
  }}/>
  {highlightPhrase}
</span>
```

Rotate the whole page `-0.6deg`. Give it the shared drop shadow. Let the bottom
of the page run off the frame.

---

## 3. Document / charter — torn paper, seal, drawn signature

For anything official: an act, a charter, a contract, a patent.

- Card: `#EFEBE0`, rotated `1deg`, torn top and bottom edges via `clipPath`.
- Title in PlayfairDisplay small caps, tracked `+6`, with a hairline rule under it.
- Body in PTSerif 24px at `opacity: 0.75` — it reads as text without asking to be read.
- A red wax seal: a circle at `#8E2A1B` with an inner ring, scaled in on a spring.
- The signature draws on:

```tsx
const sig = interpolate(frame, [sigStart, sigEnd], [1, 0], {
  extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.inOut(Easing.cubic),
});
<svg viewBox="0 0 520 140" style={{ width: 520, overflow: "visible" }}>
  <path d={SIGNATURE_PATH} stroke="#1A1A1A" strokeWidth={5}
    strokeLinecap="round" fill="none"
    pathLength={1} strokeDasharray={1} strokeDashoffset={sig} />
</svg>
```

Write the signature path by hand as a few cubic segments. It does not need to be
a real signature, it needs to read as one at 30fps.

---

## 4. Self-drawing chart

Line, bar or area. The line draws left to right, the axis fades in first, the
final value pops as a label.

```tsx
const d = points.reduce((acc, p, i) => acc + (i ? ` L ${p.x} ${p.y}` : `M ${p.x} ${p.y}`), "");
<path d={d} stroke="#E85D24" strokeWidth={7} fill="none" strokeLinecap="round"
  pathLength={1} strokeDasharray={1} strokeDashoffset={draw} />
```

Bars grow from the baseline with `transformOrigin: "bottom"` and a staggered
`scaleY`. Put the value **on** the bar, in Arial Black, not on an axis. Drop
gridlines entirely.

---

## 5. Counter that lands on the word

A number counting up while the narration says it. The landing frame comes out of
`vo/timing.json`.

```tsx
const t = interpolate(frame, [countStart, countEnd], [0, 1], {
  extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.cubic),
});
const value = Math.round(interpolate(t, [0, 1], [from, to]));
```

Set `countEnd` to the frame the spoken number *finishes*. Landing early is
lifeless; landing late reads as a bug. Use `Montserrat` with
`fontVariantNumeric: "tabular-nums"` so digits do not jitter.

---

## 6. Strike-through list

For "all of these failed except one". Items enter staggered, then a red marker
line draws through each one in turn, leaving the survivor untouched.

```tsx
const strike = interpolate(frame, [s, s + 10], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
<div aria-hidden style={{
  position: "absolute", left: -10, right: -10, top: "52%", height: 7,
  background: "#E04329", transformOrigin: "left center",
  transform: `scaleX(${strike}) rotate(-0.8deg)`, borderRadius: 4,
}}/>
```

Fade struck items to `opacity: 0.35` a few frames after their line completes. The
survivor holds full opacity and takes a red underline instead.

---

## 7. Typewriter closer

The punchline. Text types out in SpecialElite over a vignette, timed to the two
halves of the closing line.

```tsx
const chars = Math.floor(interpolate(frame, [start, end], [0, text.length], {
  extrapolateLeft: "clamp", extrapolateRight: "clamp",
}));
const shown = text.slice(0, chars);
const caret = Math.floor(frame / 8) % 2 === 0 && chars < text.length;
```

Two sentences means two independent typewriters, each starting at its own beat.
Give the caret a solid `#E04329` block, 4px wide.

Vignette over the top:

```tsx
<AbsoluteFill aria-hidden style={{
  background: "radial-gradient(circle at 50% 50%, transparent 42%, rgba(20,16,12,0.55) 100%)",
  pointerEvents: "none", zIndex: 30,
}}/>
```
