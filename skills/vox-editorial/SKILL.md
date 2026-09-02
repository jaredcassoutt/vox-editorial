---
name: vox-editorial
description: Build vertical editorial explainer films in a paper-collage style - a researched script, narration, cut-paper artwork animated across depth planes, burned captions and a music bed, assembled locally with ffmpeg. Use when someone wants an explainer video, a video essay, a documentary short, a narrated piece about a topic, a TikTok/Reels/Shorts explainer, or an article turned into a film. Also use for collage motion graphics, kinetic editorial typography, or animated statistic graphics.
---

# Vox editorial

One topic in, one finished vertical film out. The register is editorial journalism, not
advertising: it earns the next five seconds by being genuinely interesting rather than by
shouting. Everything below is scoped to that register only — for a hard-sell product ad
with fast cuts and sound design, use `fastcut-ad` instead.

The house style is **cut paper**. Saturated flat grounds, objects that look scissored out
and taped down, a headline set into torn stock. It suits editorial work because it reads
as made-by-hand rather than rendered, and because a paper cut-out can be animated as an
independent object.

## What decides quality, in order

1. **The fact you build on.** One genuinely surprising, checkable thing. If the topic has
   no such fact, the film has no reason to exist and no amount of craft rescues it.
2. **The narration.** It is the clock and the spine.
3. **Depth.** Whether the frame has layers that move against each other.
4. **Everything else.**

Spend your effort in that order.

---

## 1. Research and script

Find the fact first. Not a statistic — a *reversal*: the thing that turns out to be the
opposite of what the viewer assumes. Tokyo was the largest city on earth before London.
The Colosseum's missing wall was carried away by hand. Someone invented infinite scroll
and regrets it.

### The hook, and the debt it creates

**Every script opens on a hook that stays unresolved until the last line.** A hook is not
a summary and not a teaser — it is a debt the film owes the viewer, and the final line is
where it gets paid.

Two rules, and both are required. Either one alone produces a worse film than no hook.

**1. Withhold the subject.** No proper nouns in the hook: no country, no city, no person,
no year. Replace them — "this country", "the man in charge", "one developer". After the
first line the viewer must not be able to tell what the film is about. That uncertainty is
the thing keeping them there.

**2. Pose a real question.** Hiding a name is not enough. The hook has to state something
contradictory, or plainly wrong, that demands an explanation: a number that cannot be
right, a person punished for something they could not have done, a country doing the exact
opposite of what you would expect. **Then the last line of the film answers that exact
question.** If the only reveal is "it was London", the viewer feels tricked rather than
paid, and the film reads as clickbait.

Test a draft hook with two questions. *Can the viewer name the subject from it?* If yes,
rewrite. *Does the closing line answer the question the hook asked?* If not, either the
hook or the ending is wrong.

#### Worked examples

> "The man in charge was woken up and told the city was burning. He said it was nothing
> and went back to bed."

The Great Fire of London, 1666. The body runs the four days of the fire and the thirty
year rebuild. It resolves by returning to that night: the Lord Mayor refused to order
firebreaks because he did not want to pay for the demolished houses, and by the time he
was overruled, eighty percent of the city was gone. The hook asks *who was he and why did
it matter*; the ending answers it.

> "This country had more guns than all of Europe combined. Then it spent two hundred and
> fifty years pretending it never did."

Japan. The body covers the Tokugawa shogunate sealing the country. It resolves in 1853
when four American steamships arrive and the pretence collapses overnight, followed by
Japan industrialising faster than any nation in history. The hook asks *why would anyone
give that up*; the ending shows what it cost to have done it.

> "The most peaceful era in this nation's history ran entirely on hostages."

The Edo period. The body explains sankin-kotai: every lord forced to alternate years in
the capital, leaving his family behind when he left. It resolves by showing that the peace
and the hostage system were the same thing, so when one ended the other did too. The hook
asks *how can that be true*; the ending makes it make sense.

Note what all three share. The hook is a specific, checkable oddity — not a vague tease —
and the closing beat lands on the *same* oddity from the other side. The middle of the
film exists to make the answer earned rather than merely stated.

`references/hook-library.md` holds further opening patterns.

Then shape it:

```
hook        one line, subject withheld, poses a question (see above)
setup       the ordinary world the reversal will break
turn        the surprising fact, landed plainly
consequence why it changes how you see the thing
close       ANSWERS the hook's question, does not summarise
```

Beat rules that hold up:

- One beat carries one idea. Two ideas in a sentence means two beats.
- 7–10 beats for a 30–45 second film. Fewer, longer beats feel like a lecture.
- Second person is welcome. Present tense for historical narrative pulls it closer.
- Numbers beat adjectives. "Twenty seven years" lands; "a huge amount of time" does not.
- Cut every line to its shortest true form, then cut it again. Two seconds saved in the
  script is two seconds the viewer is still watching.
- **Never open a beat on an empty frame.** The primary element is on screen by ~0.1s.

`references/narrative-arcs.md` holds arc shapes and pacing presets;
`references/hook-library.md` holds opening patterns. Record the chosen arc in the script
file so a later rebuild keeps the same shape.

---

## 2. Narration

Generate one audio file **per beat**, never one long file. Beat durations are the master
clock for every timing decision downstream, and a single blob cannot be re-cut when you
rewrite one line.

Providers, best first:

| provider | cost | notes |
| --- | --- | --- |
| Edge neural TTS (`edge-tts`) | free, no key | Andrew or Brian; the default |
| Higgsfield ElevenLabs | ~0.15 credits/line | marginally better on a dramatic read |
| Kokoro (local ONNX) | free, offline | when there is no network |

Pick one voice for the whole series so separate films read as one channel. Measure every
file with `ffprobe` and write the durations out — that file is the clock.

---

## 3. Artwork: generate elements, never posters

**This is the part everyone gets wrong.** The obvious approach is to generate a finished
composition per beat and then animate pieces of it. It looks flat every time, and the
reason is not the motion — the original composition is still underneath, so a "moving"
element slides over an identical copy of itself. Nothing can move *behind* anything,
because there is no behind.

So the image model never draws a composition. It draws the **subjects only**, spaced well
apart on a flat magenta field, which is keyed to true alpha:

- `references/sprite_sheets.py` — one sheet per beat, several objects per generation
- `references/chroma_sprites.py` — keys the field and cuts each object out

The keyer samples the background colour from the border rather than assuming a fixed
magenta, pulls the alpha well inside the silhouette, and neutralises surviving fringe. A
coloured halo around a cut-out is the single clearest sign something was pasted.

**Check the library before generating anything.** `library/library.py` indexes every
sprite previous films produced, by tag. Resolve the beat's objects against it and pay only
for the misses. File the generic results afterwards — a pointing hand, a phone, a crowd —
and the next film gets them free.

**Draw the rest locally.** `library/paper.py` makes grounds, torn banners with per-letter
colour, confetti, tape, newsprint scraps and numerals. These cost nothing, so they are
drawn fresh from a seed rather than cached, and the headline text is correct by
construction instead of by hoping the model can spell.

The rule: **cache what is expensive, draw what is cheap.**

### The look

`references/vivid_collage.py` composes the prompts. What actually makes it:

- A **flat saturated ground** — cobalt, marigold, coral, cream — rotating across beats so
  the film stays vivid while reading as one system. The ground does more work than the
  objects.
- Every object is a **separate cut-out with a thick white sticker border** and a soft
  paper drop shadow. Many small bordered pictures beat one big illustration.
- Objects are **vintage-print illustrations with halftone shading**. State *not CGI, not a
  3D render* explicitly or the model drifts toward glossy.
- A **headline set into torn stock**, condensed all-caps, saturated or per-letter colour.
- Torn newsprint carrying real body text, halftone tape, geometric confetti.

For a person, a place or an object that actually exists, use a **real photograph**,
subject-lifted and given the same white border — never an illustration of that specific
thing. See `references/real-subject-cutouts.md`, which also covers the guardrail: video
models refuse to animate identifiable public figures, so those beats composite the
photograph locally instead.

Public-domain archives are richer than they look for historical work: woodblock prints,
engravings, old maps, early photography. Prefer public domain or CC0 outright — a licence
that demands attribution does not survive a repost.

---

## 4. Animation: depth planes

`references/scene_graph.py` builds a beat as a list of independent layers;
`references/multiplane.py` renders it.

```
0.05  ground              barely moves
0.20  clippings, tape
0.40  rear confetti
0.60  secondary subject
0.80  primary subject
1.00  front confetti      largest, fastest
1.15  headline            nearest the lens
```

Depth drives three things simultaneously: parallax against the camera, drift amplitude,
and draw order. That differential is what the eye reads as space. Each layer also carries
its own entrance, drift, breath and rotation phase, so no two elements ever move together.
A typical beat runs 28–36 independent layers.

Layers rest at their **original positions** over the source artwork, so a frame at rest
reconstructs the composition exactly.

`references/kinetic_overlays.py` adds counters, typewriter reveals, circles, marker
highlights, life grids, route lines and charts. Anchor every annotation to a *measured*
element rather than typed pixel coordinates — that is how a highlight ends up circling
nothing.

---

## 5. Assembly

1. Trim each shot to its beat's narration length. Never hold a freeze frame; regenerate.
2. Concatenate, then lay the narration underneath as the spine.
3. Burn captions as **PNG overlays** rather than a subtitle filter — more portable, and
   many ffmpeg builds ship without `drawtext` or `libass`. Keep them clear of the bottom
   UI zone.
4. Mix: narration at full level, music roughly 12–15 dB under it.
5. **Master to −14 LUFS.** Platforms normalise, so a quiet master is pushed up along with
   its noise floor.
6. Optionally speed the finished film ~1.15–1.25×. Vertical plays better fast.

Check the music bed's *length* before using it. A short loop under a longer film produces
a ghostly doubling that is very easy to misread as a narration fault.

---

## Field notes

Each of these was a visible defect before it became a rule.

- **A continuation cut must not replay its effect.** If one narration line is split across
  two shots, the second renders the *settled* state. Otherwise the reveal runs twice and
  the viewer sees the same animation back to back.
- **Lock wide headline banners.** Let a decomposer split a headline into pieces that drift
  independently and the layout appears to fall apart.
- **Measure text the way you draw it.** Per-letter colouring loses kerning, so a line
  measured with `textlength(whole_string)` overruns the paper it sits on.
- **The ground never fades in.** Ramping its alpha opens the beat on black.
- **Damp the headline's camera response.** It sits nearest the lens, so a full parallax
  response walks it off frame.
- **Front confetti keeps clear of the centre.** Pieces landing on a subject read as dirt
  on the lens.
- **Never overlay what the artwork already says.** A counter animating a number the poster
  already prints reads as a mistake.
- **Exact identifiers beat fuzzy matching.** Tag-overlap search will happily return a
  plausible wrong sprite that survives review because it still looks like a cut-out.
- **Verify sourced imagery is on-topic.** Image search returns confidently wrong results —
  a building in the wrong country, a stamp *of* a thing instead of the thing. Require the
  place name or a distinctive term, and screen out disaster and violence material, which
  is abundant in public-domain government archives and has no place here.
- **Grade with numbers.** Length, seconds-per-cut from frame-difference spikes, audio peak
  and RMS, near-silent windows. Each catches something the eye misses.

## Files

```
references/
  sprite_sheets.py     prompt one keyable sheet per beat
  chroma_sprites.py    key the field, cut objects to true alpha
  scene_graph.py       beat spec -> depth-plane layers
  multiplane.py        render the planes with a camera
  vivid_collage.py     the artwork prompt composer
  kinetic_overlays.py  counters, highlights, charts, route lines
  element_motion.py    single-image layer engine
  auto_elements.py     split an existing image into layers
  lift_cutouts.py      lift white-bordered cut-outs off finished art
  narrative-arcs.md    arc shapes and pacing presets
  hook-library.md      opening patterns
  style-variants.md    alternative looks
  real-subject-cutouts.md  real photographs of real subjects
  map-beats.md         place and route beats (documentation only)
library/
  library.py           the reusable sprite index - CHECK IT FIRST
  paper.py             grounds, banners, confetti, tape, clippings
  sprites/             tagged, alpha-keyed sprites
```
