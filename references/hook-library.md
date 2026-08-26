# Hook Library — 15 cold-open archetypes

Beat 1 is the ONLY thing standing between the film and a swipe. On vertical short-form
you have about 1.5 seconds. Every script must open with one of these, chosen at random
so the channel never develops a formula.

## Selection rule (do this, don't skip it)

Pick RANDOMLY. Do not default to the one that feels safest — that's how every video ends
up sounding the same. Roll it:

```bash
python3 -c "import random;print(random.randint(1,15))"
```

Use the returned id. Record the chosen id in `script.json` as `"hook_style"` so a rerun
can reproduce or deliberately avoid it. If the drawn hook genuinely cannot carry the
topic (rare), roll again once and note both ids.

## The 15

| # | Name | Shape | Example |
|---|---|---|---|
| 1 | **Cold Number** | Lead with one surprising concrete figure, no setup | "Four years. That's the gap between this speech and the presidency." |
| 2 | **Contradiction** | Famous for X, but X nearly never happened | "The most famous speech of his life almost went to somebody else." |
| 3 | **Direct Question** | Ask the viewer something they can't answer | "How does a man nobody has heard of become president in four years?" |
| 4 | **Timestamp** | Drop a precise moment, present tense | "It's July twenty seventh, two thousand four. Boston." |
| 5 | **You've Seen This** | Second person, a familiar image reframed | "You've seen this photo. You've never noticed the man on the left." |
| 6 | **Before / After** | Two states, brutal gap between them | "This is him losing by thirty points. This is him four years later." |
| 7 | **The Object** | Start on a thing, not a person | "This is a laminated card he carried in his pocket every day." |
| 8 | **Negation** | What everyone believes is wrong | "Everyone remembers the speech. Almost nobody remembers what it cost." |
| 9 | **Stakes** | If this had failed, the world is different | "If seventeen minutes had gone badly, none of the rest happens." |
| 10 | **Underdog** | Nobody thought this would work | "He had just been beaten so badly his own party wrote him off." |
| 11 | **Absurd Comparison** | Scale it to something familiar | "More people watched it than the finale of most TV shows that year." |
| 12 | **Cold Quote** | Open inside a striking line, then pull back | "'There is not a liberal America and a conservative America.' Nobody knew who was saying it." |
| 13 | **In Medias Res** | Drop mid-action, explain later | "He is standing backstage, and the teleprompter is wrong." |
| 14 | **Pattern Interrupt** | Command the viewer to look | "Stop. Watch what his hands do here." |
| 15 | **The Untold Part** | Everyone knows the story, not this bit | "Everyone knows how it ended. Nobody talks about the part before it." |

## Rules for all hooks

- **One sentence, maybe two.** Under 20 words spoken.
- **No throat-clearing.** Never "in this video", "let's talk about", "have you ever wondered".
- **Concrete beats abstract.** A number, a date, an object, a name.
- **The hook must be paid off** by the resolution beat. If the last beat doesn't answer
  the hook, the film has no spine.
- **Beat 1 visual is the strongest frame in the film.** Give it the biggest contrast,
  the boldest type, the most motion.
