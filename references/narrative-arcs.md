# Narrative arcs, pacing and shot patterns

A beat-layer arc library. The system is
more developed than the single arc this skill shipped with. Use this at Stage 1, before writing
a word of narration.

## 1. Pick an arc (AI recommends, user confirms)

| Arc | When | Beat shape |
|---|---|---|
| `hook_payoff` | default for any single idea | Hook → Context → Build → Payoff → Button |
| `pas` | pain-aware, urgency | Problem → Agitate → Solve → Proof → CTA |
| `bab` | when the "after" sells better than the pain | Before → After → Bridge → CTA |
| `aida` | cold audience | Attention → Interest → Desire → Action |
| `storybrand` | customer-as-hero | Hero wants → Problem → Guide → Plan → CTA → stakes |
| `how_it_works` | product/process/system | Hook → What it is → 2-3 shown steps → Benefit |
| `timeline` | history, "evolution of", journeys | Start → event → event → turning point → present |
| `man_in_hole` | case study, comeback (highest-rated arc) | OK → fall → deepen → climb out → better than before |
| `story_spine` | mission/founder tales | Once… → Every day… → Until one day… → Because… → Ever since… |
| `origin` | "why we exist" | World → spark → leap → struggle → breakthrough → today |
| `myth_buster` | correct a misconception | FACT first → the myth → expose fallacy → what to believe |
| `listicle` | "N ways to…" | Promise → item → item → #1 → recap |
| `three_act` | any narrative 60s piece | Setup → Confrontation → Resolution |
| `story_circle` | character-driven | You → Need → Go → Search → Find → Take → Return → Change |

**Topic → arc:** concept/system → `how_it_works`/`hook_payoff`; historical → `timeline`;
transformation/case study → `man_in_hole`; brand/mission → `story_spine`/`origin`;
correcting a belief → `myth_buster`; ranking/tips → `listicle`; ad → `pas`/`bab`/`aida`.

Record the choice in `script.json` as `"arc"`.

## 2. Pacing presets (firm)

- **Hook in ≤3s.** ~65% of viewers decide by 3 seconds. Beat 1 carries the payoff-promise.
  Never spend beat 1 on setup. (Pair with `hook-library.md` for the archetype.)
- Beat counts:

  | Duration | Beats | Beat length | VO words |
  |---|---|---|---|
  | 30s | 6-8 | ~4-5s | ~70-80 |
  | 60s | 10-12 | ~5-6s | ~130-150 |

- **Change something visually every 3-5s. Never hold a static frame beyond 8s.**
- Proportions: hook 1-3s → body 70-80% → payoff 10-20% → end 0-2s.
- Endings: `hard_cut` (default, drives rewatches) · `quick_cta` (≤2s, 3-5 words) ·
  `loop_close` (last line mirrors the first, so replay is seamless).

## 3. Shot patterns

Shot sizes: `EST_WIDE` (orient, scale) · `WIDE` (subject in environment) · `MEDIUM` (workhorse)
· `CLOSE` (one detail, emphasis) · `DETAIL/ECU` (a single word, number or texture — a punch).

Coverage plays out ACROSS beats:
- **Move-in** `EST_WIDE → MEDIUM → CLOSE` builds intensity, peak on CLOSE.
- **Move-out** `CLOSE → … → WIDE` reveals context; good ending.
- **The best two-shot beat**: establishing wide to orient, then a hard cut to a CLOSE of the key
  element. Generate two frames for that beat.

Keep the vocabulary hard-constrained. Never let the model free-form a camera move — it will
emit "orbit" or "dolly-zoom" and break the flat art.
