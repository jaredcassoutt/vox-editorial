import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { z } from "zod";
import { C, Cutout, DROP, Grain, Paper, getEntrance, riseFrom } from "../shared/system";
import { ARIAL, DeskEdge, Nameplate } from "../shared/pieces";

export const FOUNDERS_DURATION = 368;

export const foundersSchema = z.object({
  kickerFrame: z.number().default(24),
  baylorX: z.number().default(-608),
  baylorWidth: z.number().default(573),
  baylorStartFrame: z.number().default(78),
  baylorEndFrame: z.number().default(118),
  baylorPlateFrame: z.number().default(130),
  huckinsX: z.number().default(0),
  huckinsWidth: z.number().default(488),
  huckinsStartFrame: z.number().default(168),
  huckinsEndFrame: z.number().default(208),
  huckinsPlateFrame: z.number().default(208),
  tryonX: z.number().default(608),
  tryonWidth: z.number().default(446),
  tryonStartFrame: z.number().default(254),
  tryonEndFrame: z.number().default(294),
  tryonPlateFrame: z.number().default(300),
  portraitHeight: z.number().default(600),
  portraitBottom: z.number().default(250),
  deskHeight: z.number().default(300),
  deskStartFrame: z.number().default(0),
  deskEndFrame: z.number().default(26),
});

export type FoundersProps = z.infer<typeof foundersSchema>;

/**
 * Tryon has no public-domain likeness, so he gets an ink bust instead of a
 * borrowed face. Same box, same marker stroke, so the row still reads as a set.
 */
const BustSilhouette: React.FC<{
  x: number;
  width: number;
  height: number;
  bottom: number;
  startFrame: number;
  endFrame: number;
  strokeX: number;
  strokeY: number;
}> = ({ x, width, height, bottom, startFrame, endFrame, strokeX, strokeY }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { opacity, progress } = getEntrance(frame, fps, startFrame, endFrame);
  const rise = riseFrom(progress, 390);
  const d =
    "M 100 16 C 120 16 136 32 136 52 C 136 72 120 88 100 88 C 80 88 64 72 64 52 " +
    "C 64 32 80 16 100 16 Z " +
    "M 100 96 C 142 96 180 128 192 200 L 8 200 C 20 128 58 96 100 96 Z";
  const box: React.CSSProperties = {
    position: "absolute",
    bottom,
    width,
    height,
    opacity,
    transformOrigin: "center bottom",
  };
  return (
    <>
      <svg
        viewBox="0 0 200 200"
        preserveAspectRatio="xMidYMax meet"
        aria-hidden="true"
        style={{
          ...box,
          left: 960 + x + strokeX,
          transform: `translate(-50%, ${rise + strokeY}px)`,
          zIndex: 11,
        }}
      >
        <path d={d} fill={C.red} />
      </svg>
      <svg
        viewBox="0 0 200 200"
        preserveAspectRatio="xMidYMax meet"
        style={{
          ...box,
          left: 960 + x,
          transform: `translate(-50%, ${rise}px)`,
          filter: DROP,
          zIndex: 12,
        }}
      >
        <path d={d} fill={C.ink} opacity={0.9} />
      </svg>
      <div
        style={{
          position: "absolute",
          left: 960 + x,
          bottom: bottom + height * 0.11,
          width: width * 0.62,
          opacity: opacity,
          transform: `translate(-50%, ${rise}px)`,
          textAlign: "center",
          fontFamily: ARIAL,
          fontSize: 19,
          letterSpacing: 3,
          lineHeight: 1.8,
          color: "rgba(240,235,225,0.95)",
          zIndex: 14,
        }}
      >
        NO PUBLIC-DOMAIN
        <br />
        LIKENESS
      </div>
    </>
  );
};

export const FoundersScene: React.FC<FoundersProps> = ({
  kickerFrame = 24,
  baylorX = -608,
  baylorWidth = 573,
  baylorStartFrame = 78,
  baylorEndFrame = 118,
  baylorPlateFrame = 130,
  huckinsX = 0,
  huckinsWidth = 488,
  huckinsStartFrame = 168,
  huckinsEndFrame = 208,
  huckinsPlateFrame = 208,
  tryonX = 608,
  tryonWidth = 446,
  tryonStartFrame = 254,
  tryonEndFrame = 294,
  tryonPlateFrame = 300,
  portraitHeight = 600,
  portraitBottom = 250,
  deskHeight = 300,
  deskStartFrame = 0,
  deskEndFrame = 26,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const kicker = getEntrance(frame, fps, kickerFrame, kickerFrame + 24);

  return (
    <AbsoluteFill style={{ backgroundColor: C.paper, overflow: "hidden" }}>
      <Paper />

      <div
        style={{
          position: "absolute",
          left: 960,
          top: 92,
          opacity: kicker.opacity,
          transform: `translate(-50%, ${riseFrom(kicker.progress, 44)}px)`,
          textAlign: "center",
          zIndex: 20,
        }}
      >
        <div style={{ fontFamily: ARIAL, fontSize: 46, letterSpacing: 12, color: C.ink }}>
          THREE MEN
        </div>
        <div style={{ height: 5, width: 128, background: C.red, margin: "18px auto 0" }} />
      </div>

      <Cutout
        asset="portraits/baylor.png"
        x={baylorX}
        y={0}
        width={baylorWidth}
        height={portraitHeight}
        bottom={portraitBottom}
        startFrame={baylorStartFrame}
        endFrame={baylorEndFrame}
        strokeX={-28}
        strokeY={10}
        frame={frame}
        fps={fps}
      />
      <Cutout
        asset="portraits/huckins.png"
        x={huckinsX}
        y={0}
        width={huckinsWidth}
        height={portraitHeight}
        bottom={portraitBottom}
        startFrame={huckinsStartFrame}
        endFrame={huckinsEndFrame}
        strokeX={-26}
        strokeY={10}
        frame={frame}
        fps={fps}
      />
      <BustSilhouette
        x={tryonX}
        width={tryonWidth}
        height={portraitHeight}
        bottom={portraitBottom}
        startFrame={tryonStartFrame}
        endFrame={tryonEndFrame}
        strokeX={28}
        strokeY={10}
      />

      <DeskEdge
        startFrame={deskStartFrame}
        endFrame={deskEndFrame}
        height={deskHeight}
      />

      <Nameplate
        startFrame={baylorPlateFrame}
        x={baylorX}
        bottom={62}
        name="R. E. B. BAYLOR"
        role="DISTRICT JUDGE"
        rotate={-0.7}
      />
      <Nameplate
        startFrame={huckinsPlateFrame}
        x={huckinsX}
        bottom={62}
        name="JAMES HUCKINS"
        role="MISSIONARY"
        rotate={0.5}
      />
      <Nameplate
        startFrame={tryonPlateFrame}
        x={tryonX}
        bottom={62}
        name="WILLIAM MILTON TRYON"
        role="PASTOR"
        rotate={-0.4}
      />

      <Grain />
    </AbsoluteFill>
  );
};
