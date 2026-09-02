import React from "react";
import { Easing, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { C, DROP, getEntrance, riseFrom } from "./system";

export const ARIAL = "'Arial Black', 'Helvetica Neue', Helvetica, sans-serif";

/** Deterministic jitter so torn edges stay identical frame to frame. */
const rnd = (seed: number) => {
  const x = Math.sin(seed * 12.9898) * 43758.5453;
  return x - Math.floor(x);
};

/** A torn-edge polygon for clipPath. Top and bottom edges get the jitter. */
export const tornClip = (seed = 1, points = 16, depth = 1.1) => {
  const top: string[] = [];
  const bottom: string[] = [];
  for (let i = 0; i <= points; i++) {
    const p = (i / points) * 100;
    top.push(`${p.toFixed(2)}% ${(rnd(seed + i) * depth).toFixed(2)}%`);
    bottom.push(
      `${(100 - p).toFixed(2)}% ${(100 - rnd(seed + 90 + i) * depth).toFixed(2)}%`,
    );
  }
  return `polygon(${[...top, ...bottom].join(", ")})`;
};

/**
 * Layer 24: the occluding foreground. Every scene needs one or the shot is a
 * slide. A dark desk edge that crops the midground at the chest.
 */
export const DeskEdge: React.FC<{
  startFrame: number;
  endFrame: number;
  height?: number;
  label?: string;
}> = ({ startFrame, endFrame, height = 250, label }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { opacity, progress } = getEntrance(frame, fps, startFrame, endFrame);
  const rise = riseFrom(progress, 300);
  return (
    <div
      style={{
        position: "absolute",
        left: -40,
        right: -40,
        bottom: 0,
        height,
        opacity,
        transform: `translateY(${rise}px)`,
        zIndex: 24,
        filter: DROP,
      }}
    >
      <div
        style={{
          position: "absolute",
          inset: 0,
          background: `linear-gradient(180deg, #2A241D 0%, ${C.inkDeep} 42%, #0E0B08 100%)`,
          clipPath: tornClip(7, 20, 3.4),
        }}
      />
      <div
        style={{
          position: "absolute",
          left: 0,
          right: 0,
          top: 10,
          height: 3,
          background: "rgba(226,219,205,0.22)",
        }}
      />
      {label ? (
        <div
          style={{
            position: "absolute",
            left: 118,
            top: 42,
            fontFamily: ARIAL,
            fontSize: 21,
            letterSpacing: 5,
            color: "rgba(226,219,205,0.5)",
          }}
        >
          {label}
        </div>
      ) : null}
    </div>
  );
};

/** A pale torn paper strip. The lighter alternative foreground. */
export const PaperBand: React.FC<{
  startFrame: number;
  endFrame: number;
  height?: number;
  bottom?: number;
  rotate?: number;
  children?: React.ReactNode;
}> = ({ startFrame, endFrame, height = 190, bottom = -34, rotate = -0.8, children }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { opacity, progress } = getEntrance(frame, fps, startFrame, endFrame);
  const rise = riseFrom(progress, 280);
  return (
    <div
      style={{
        position: "absolute",
        left: -60,
        right: -60,
        bottom,
        height,
        opacity,
        transform: `translateY(${rise}px) rotate(${rotate}deg)`,
        background: C.card,
        clipPath: tornClip(3, 18, 5),
        filter: DROP,
        zIndex: 24,
      }}
    >
      {children}
    </div>
  );
};

/** A rubber stamp: overshoots, settles, sits crooked. */
export const Stamp: React.FC<{
  startFrame: number;
  x: number;
  y: number;
  rotate?: number;
  color?: string;
  title: string;
  sub?: string;
  /** Frame at which a marker line strikes through the sub line. */
  subStrikeFrame?: number;
  width?: number;
  zIndex?: number;
}> = ({
  startFrame,
  x,
  y,
  rotate = -4,
  color = C.red,
  title,
  sub,
  subStrikeFrame,
  width = 560,
  zIndex = 22,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s = spring({
    frame: frame - startFrame,
    fps,
    config: { damping: 11, mass: 0.6, stiffness: 190 },
    durationInFrames: 26,
  });
  const scale = interpolate(s, [0, 1], [1.55, 1]);
  const opacity = interpolate(frame, [startFrame, startFrame + 5], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  return (
    <div
      style={{
        position: "absolute",
        left: 960 + x,
        top: 540 + y,
        width,
        opacity: opacity * 0.93,
        transform: `translate(-50%, -50%) rotate(${rotate}deg) scale(${scale})`,
        border: `7px solid ${color}`,
        padding: "18px 30px 22px",
        textAlign: "center",
        color,
        zIndex,
      }}
    >
      <div style={{ fontFamily: ARIAL, fontSize: 52, letterSpacing: 1, lineHeight: 1.02 }}>
        {title}
      </div>
      {sub ? (
        <>
          <div style={{ height: 3, background: color, margin: "13px 0 11px" }} />
          <div style={{ position: "relative", fontFamily: ARIAL, fontSize: 30, letterSpacing: 7 }}>
            {sub}
            {subStrikeFrame === undefined ? null : (
              <Strike startFrame={subStrikeFrame} duration={11} top="46%" thickness={6} />
            )}
          </div>
        </>
      ) : null}
    </div>
  );
};

/** A nameplate that sits on the foreground, in front of a portrait. */
export const Nameplate: React.FC<{
  startFrame: number;
  x: number;
  bottom: number;
  name: string;
  role: string;
  width?: number;
  rotate?: number;
}> = ({ startFrame, x, bottom, name, role, width = 460, rotate = -0.6 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { opacity, progress } = getEntrance(frame, fps, startFrame, startFrame + 22);
  const rise = riseFrom(progress, 60);
  return (
    <div
      style={{
        position: "absolute",
        left: 960 + x,
        bottom,
        width,
        opacity,
        transform: `translate(-50%, ${rise}px) rotate(${rotate}deg)`,
        background: C.card,
        padding: "16px 20px 18px",
        textAlign: "center",
        filter: DROP,
        zIndex: 26,
      }}
    >
      <div style={{ height: 5, background: C.red, marginBottom: 12 }} />
      <div
        style={{
          fontFamily: ARIAL,
          fontSize: 28,
          letterSpacing: 0.4,
          color: C.ink,
          lineHeight: 1.12,
        }}
      >
        {name}
      </div>
      <div
        style={{
          fontFamily: ARIAL,
          fontSize: 17,
          letterSpacing: 4,
          color: "rgba(26,26,26,0.52)",
          marginTop: 8,
        }}
      >
        {role}
      </div>
    </div>
  );
};

/** A red marker line that draws left to right through its parent. */
export const Strike: React.FC<{
  startFrame: number;
  duration?: number;
  top?: string;
  rotate?: number;
  thickness?: number;
  /** How far the line runs past its parent. Small cards want ~2, words want -14. */
  inset?: number;
}> = ({
  startFrame,
  duration = 9,
  top = "52%",
  rotate = -0.9,
  thickness = 8,
  inset = -14,
}) => {
  const frame = useCurrentFrame();
  const w = interpolate(frame, [startFrame, startFrame + duration], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.quad),
  });
  return (
    <div
      aria-hidden="true"
      style={{
        position: "absolute",
        left: inset,
        right: inset,
        top,
        height: thickness,
        background: C.red,
        borderRadius: thickness,
        transformOrigin: "left center",
        transform: `scaleX(${w}) rotate(${rotate}deg)`,
        zIndex: 3,
      }}
    />
  );
};

/** Typewriter reveal with a solid red caret. */
export const Typewriter: React.FC<{
  text: string;
  startFrame: number;
  endFrame: number;
  style?: React.CSSProperties;
}> = ({ text, startFrame, endFrame, style }) => {
  const frame = useCurrentFrame();
  const n = Math.floor(
    interpolate(frame, [startFrame, endFrame], [0, text.length], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    }),
  );
  const done = n >= text.length;
  const caret = frame >= startFrame && (!done || frame < endFrame + 40) && Math.floor(frame / 8) % 2 === 0;
  return (
    <div style={style}>
      {text.slice(0, n)}
      <span
        style={{
          display: "inline-block",
          width: 5,
          height: "0.92em",
          background: C.red,
          marginLeft: 5,
          verticalAlign: "-0.1em",
          opacity: caret ? 1 : 0,
        }}
      />
    </div>
  );
};

/** A wax seal that presses in. */
export const Seal: React.FC<{
  startFrame: number;
  size?: number;
  label?: string;
}> = ({ startFrame, size = 128, label = "1845" }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s = spring({
    frame: frame - startFrame,
    fps,
    config: { damping: 12, mass: 0.7, stiffness: 210 },
    durationInFrames: 24,
  });
  const scale = interpolate(s, [0, 1], [1.9, 1]);
  const opacity = interpolate(frame, [startFrame, startFrame + 5], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  return (
    <div
      style={{
        width: size,
        height: size,
        borderRadius: "50%",
        background: "radial-gradient(circle at 38% 32%, #B33A24, #7E2314 70%)",
        opacity,
        transform: `scale(${scale}) rotate(-6deg)`,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        boxShadow: "inset 0 0 0 6px rgba(255,255,255,0.14), 0 10px 16px rgba(55,45,31,0.35)",
      }}
    >
      <div
        style={{
          fontFamily: ARIAL,
          fontSize: size * 0.24,
          letterSpacing: 1,
          color: "rgba(255,236,226,0.86)",
        }}
      >
        {label}
      </div>
    </div>
  );
};
