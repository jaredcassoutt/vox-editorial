# Style variants

The paper-collage look is the default, not the only option. Pick the variant that fits the
BEAT, and say which one you used in `script.json` as `"style_variant"`. Most films use one
variant throughout; a map beat dropped into a collage film is the common exception.

| Variant | Use it for | Look |
|---|---|---|
| `paper-collage` (default) | Ideas, history, arguments, anything abstract | Cutouts with white sticker borders on textured paper, halftone, washi tape, one accent colour |
| `map-beat` | Anything about PLACE or MOVEMENT — itineraries, routes, borders, "where" | Editorial vector map, camera zooming to a coordinate, pins dropping, routes drawing on, region highlights. See `map-beats.md` |
| `dark-signal` | Technology, attention, surveillance, systems working on you | Deep charcoal paper, bone-white cutouts, ONE cold screen-blue accent. Reads cold and clinical |
| `archive-doc` | A named person or a specific dated event | Real licensed photo cutouts (see `real-subject-cutouts.md`) over a near-empty field, newspaper and document textures, date stamps |
| `grid-editorial` | Data, money, geopolitics, systems - the plain modern look | Light grey graph-paper ground with grain and vignette, halftone photo cutouts with a coloured OFFSET shadow (not a white border), heavy black condensed headlines, typewriter for quotes. Built by `grid_background()` + `offset_shadow()` |
| `number-slam` | A single statistic that IS the point | One enormous condensed numeral filling the frame, tiny human figures for scale, everything else stripped out |

## Choosing

- If the beat answers **"where"** or **"how did it move"** → `map-beat`.
- If the beat answers **"who"** or **"when exactly"** → `archive-doc`.
- If the beat is **one number** → `number-slam` for that beat only, then return to the film's base variant.
- Otherwise → the film's base variant.

Do not mix more than two variants in one film. The palette (`accent_color`) stays constant
across every variant so the film still reads as one piece.
