# Map beats — place, routes and movement

Adapted from the `map-animation` skill (iart-ai). Use for any beat that establishes WHERE
something is or HOW it moved: an itinerary, a border, a migration, a flight path, a
"we went here, then here" sequence. This is the workhorse variant for Bilbo travel films.

## The signature: the 12fps stutter

The single most recognisable trait of the editorial map look is that the **graphic layer
steps at 12fps inside a smooth 30fps edit**. Pins, route draw-on and label pops move in
deliberate steps; the base map and audio stay smooth. It reads as hand-built infographic
motion rather than soft video.

```js
const STEP = Math.round(fps / 12);            // 2-3 at 24-30fps
const f = Math.floor(frame / STEP) * STEP;    // use f for GRAPHICS, frame for the base
```

Stutter only the overlay. Stuttering everything just looks like dropped frames.

## Projection — one coordinate space for everything

Project GeoJSON once, then every pin, route and label shares that space, so they all track
the camera together.

```js
import { geoMercator, geoPath } from "d3-geo";
const projection = geoMercator().fitSize([W, H], geojson);
const toPath = geoPath(projection);
const [x, y] = projection([lng, lat]);        // lat/long -> screen pixels
```

Camera move = a transform toward a target coordinate:

```js
const [tx, ty] = projection([targetLng, targetLat]);
const scale = interpolate(f, [0, 36], [1, 4], { extrapolateRight: "clamp" });
const transform = `translate(${W/2 - tx*scale}px, ${H/2 - ty*scale}px) scale(${scale})`;
```

## Overlays

- **Pin drop** — `spring({frame: f - i*STEP*4, config:{damping:12}})` so it overshoots and
  settles; stagger across the coordinate array.
- **Route draw-on** — build the path from projected points, then stroke it on with
  `strokeDashoffset` from 1 to 0 (`pathLength=1`).
- **Region highlight** — fill the focus feature in the accent colour, drop everything else
  to a low-opacity ink; never hide the context entirely.
- **Labels** — fade in AFTER the pin lands, anchored to `projection([lng,lat])`. Keep them
  horizontal and inside the safe area; never let a label rotate with the map.

## Vertical (9:16) rules

Our films are vertical, and most map data is landscape. So:
- `fitSize([W*1.6, H*0.55])` and place the map in the upper two-thirds, captions below.
- Zoom harder than feels right on desktop — a country that reads fine at 16:9 is a smudge
  at 9:16. Target one country or one city per beat, never a continent.
- Put the route's start and end in the vertical middle third; that is the only area a
  phone viewer actually reads.

## Data-driven: one array drives the beat

Keep a single coordinates array as the source of truth so the whole sequence is
regenerable and re-timeable:

```json
{"stops":[{"name":"Reykjavik","lng":-21.94,"lat":64.15,"t":0.0},
          {"name":"Vik","lng":-19.01,"lat":63.42,"t":2.4}]}
```

## Two production paths

| You need | Path |
|---|---|
| Clean editorial vector look, fully code-rendered, free | **GeoJSON + SVG** in Remotion (or PIL/ffmpeg for stills-plus-motion) |
| Photoreal terrain and a cinematic 3D camera | **Google Earth Studio** -> image sequence + camera `.jsx` -> After Effects |

Prefer the vector path here: it costs nothing, renders locally, and matches the flat
editorial grammar of the rest of the film. Reach for Earth Studio only when the beat
genuinely needs real satellite terrain.

## Gotchas

- Natural Earth GeoJSON at 1:110m is enough for country shapes and keeps renders fast;
  1:50m only when you need coastline detail.
- Mercator badly distorts near the poles — use `geoEqualEarth` for anything global.
- Always `fitSize` to the data you are actually showing, not the whole world, or your
  subject ends up 40px wide.
