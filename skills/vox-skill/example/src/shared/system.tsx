import React from "react";
import {
  AbsoluteFill,
  Easing,
  Img,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

/** The locked palette. Do not add a colour. */
export const C = {
  paper: "#DAD9D5",
  ink: "#1A1A1A",
  inkDeep: "#16110D",
  red: "#E04329",
  orange: "#E85D24",
  orange2: "#E8741E",
  amber: "#F5C518",
  card: "#EFEBE0",
} as const;

export const SHADOW = "rgba(55, 45, 31, 0.28)";
export const DROP = `drop-shadow(0 28px 26px ${SHADOW})`;

/** The one entrance every element uses: a spring rise crossed with an opacity ramp. */
export const getEntrance = (
  frame: number,
  fps: number,
  startFrame: number,
  endFrame: number,
) => {
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

export const riseFrom = (progress: number, distance = 390) =>
  interpolate(progress, [0, 1], [distance, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

/**
 * Frame-aware layout. Scenes position against these instead of hard-coding 960,
 * so the same components render at 1920x1080 and 1080x1920.
 *
 * `safe` is the region the platform does NOT draw its own interface over. On a
 * vertical cut TikTok covers the top strip, the bottom fifth and the right edge;
 * anything there is hidden behind the caption, the username and the buttons.
 */
export const useLayout = () => {
  const { width, height } = useVideoConfig();
  const isVertical = height > width;
  const safe = isVertical
    ? { top: 180, bottom: 420, left: 40, right: 150 }
    : { top: 60, bottom: 60, left: 80, right: 80 };
  return {
    W: width,
    H: height,
    cx: width / 2,
    cy: height / 2,
    isVertical,
    safe,
    /** Centre of the usable region: above the geometric centre on vertical. */
    safeCx: (safe.left + (width - safe.right)) / 2,
    safeCy: (safe.top + (height - safe.bottom)) / 2,
    /** Type scale. A narrower frame needs LARGER type relative to its width. */
    ts: isVertical ? 1.4 : 1,
  };
};

/** Layer 0 + 2: the locked texture and its soft-light wash. Never changes. */
export const Paper: React.FC<{ asset?: string }> = ({
  asset = "background.png",
}) => (
  <>
    <Img
      src={staticFile(asset)}
      alt=""
      style={{
        position: "absolute",
        inset: 0,
        width: "100%",
        height: "100%",
        objectFit: "cover",
        zIndex: 0,
      }}
    />
    <AbsoluteFill
      aria-hidden="true"
      style={{
        background:
          "linear-gradient(180deg, rgba(255,255,255,0.06), rgba(63,54,42,0.12)), radial-gradient(circle at 50% 72%, rgba(255,255,255,0.18), transparent 38%)",
        mixBlendMode: "soft-light",
        pointerEvents: "none",
        zIndex: 2,
      }}
    />
  </>
);

/** A cut-out with its offset red marker silhouette. The signature of the system. */
export const Cutout: React.FC<{
  asset: string;
  x: number;
  y: number;
  width: number;
  height: number;
  scale?: number;
  startFrame: number;
  endFrame: number;
  strokeX?: number;
  strokeY?: number;
  strokeColor?: string;
  strokeOpacity?: number;
  bottom?: number;
  distance?: number;
  zIndex?: number;
  frame: number;
  fps: number;
}> = ({
  asset,
  x,
  y,
  width,
  height,
  scale = 1,
  startFrame,
  endFrame,
  strokeX = -26,
  strokeY = 8,
  strokeColor = C.red,
  strokeOpacity = 0.95,
  bottom = 330,
  distance = 390,
  zIndex = 11,
  frame,
  fps,
}) => {
  const { cx } = useLayout();
  const { opacity, progress } = getEntrance(frame, fps, startFrame, endFrame);
  const rise = riseFrom(progress, distance);
  const url = staticFile(asset);
  const box = {
    position: "absolute" as const,
    bottom: bottom + y,
    width,
    height,
    opacity,
    objectFit: "contain" as const,
    objectPosition: "center bottom",
    transformOrigin: "center bottom",
  };
  return (
    <>
      <div
        aria-hidden="true"
        style={{
          ...box,
          left: cx + x + strokeX,
          backgroundColor: strokeColor,
          maskImage: `url(${url})`,
          maskRepeat: "no-repeat",
          maskSize: "100% 100%",
          maskPosition: "center bottom",
          WebkitMaskImage: `url(${url})`,
          WebkitMaskRepeat: "no-repeat",
          WebkitMaskSize: "100% 100%",
          WebkitMaskPosition: "center bottom",
          opacity: opacity * strokeOpacity,
          transform: `translate(-50%, ${rise + strokeY}px) scale(${scale})`,
          willChange: "transform, opacity",
          zIndex,
        }}
      />
      <Img
        src={url}
        alt=""
        style={{
          ...box,
          left: cx + x,
          transform: `translate(-50%, ${rise}px) scale(${scale})`,
          filter: DROP,
          willChange: "transform, opacity",
          zIndex: zIndex + 1,
        }}
      />
    </>
  );
};

/** Optional paper grain over the whole frame. */
export const Grain: React.FC = () => (
  <AbsoluteFill
    aria-hidden="true"
    style={{
      backgroundImage:
        "radial-gradient(rgba(40,32,24,0.5) 0.6px, transparent 0.7px)",
      backgroundSize: "3px 3px",
      mixBlendMode: "multiply",
      opacity: 0.05,
      pointerEvents: "none",
      zIndex: 28,
    }}
  />
);

/**
 * Burned captions for vertical cuts. Most of the audience has the sound off, so
 * a vertical film without these is a silent film. Data comes from
 * scripts/captions.py, which reads the same word boundaries that time the
 * animation, so the two cannot drift apart.
 */
export const Captions: React.FC<{
  captions: { text: string; from: number; to: number }[];
  bottom?: number;
  fontSize?: number;
}> = ({ captions, bottom, fontSize }) => {
  const frame = useCurrentFrame();
  const { safe, ts, isVertical } = useLayout();
  const active = captions.find((c) => frame >= c.from && frame < c.to);
  if (!active) return null;
  const pop = interpolate(frame, [active.from, active.from + 3], [0.94, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  return (
    <div
      style={{
        position: "absolute",
        left: "50%",
        bottom: bottom ?? safe.bottom + 40,
        transform: `translateX(-50%) scale(${pop})`,
        maxWidth: isVertical ? 900 : 1400,
        padding: "16px 30px",
        background: "rgba(22,17,13,0.82)",
        textAlign: "center",
        fontFamily: "'Arial Black', 'Helvetica Neue', Helvetica, sans-serif",
        fontSize: fontSize ?? Math.round(46 * ts),
        letterSpacing: 0.5,
        lineHeight: 1.16,
        color: "#F4F1EA",
        zIndex: 40,
      }}
    >
      {active.text}
    </div>
  );
};
