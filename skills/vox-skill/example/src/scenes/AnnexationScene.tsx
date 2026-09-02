import React from "react";
import {
  AbsoluteFill,
  Easing,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { z } from "zod";
import { C, DROP, Grain, Paper, getEntrance, riseFrom } from "../shared/system";
import { ARIAL, DeskEdge, Stamp, Strike } from "../shared/pieces";
import { TEXAS_PATH, TEXAS_VIEWBOX } from "../shared/texas";

export const ANNEXATION_DURATION = 358;

export const annexationSchema = z.object({
  texasStartFrame: z.number().default(4),
  texasEndFrame: z.number().default(42),
  texasWidth: z.number().default(520),
  labelStrikeFrame: z.number().default(54),
  annexStampFrame: z.number().default(71),
  unionLabelFrame: z.number().default(104),
  actOneOutFrame: z.number().default(150),
  gridInFrame: z.number().default(176),
  headingFrame: z.number().default(178),
  strikeStartFrame: z.number().default(244),
  strikeSpacing: z.number().default(4),
  survivorIndex: z.number().default(7),
  survivorFrame: z.number().default(304),
  deskStartFrame: z.number().default(0),
  deskEndFrame: z.number().default(24),
});

export type AnnexationProps = z.infer<typeof annexationSchema>;

const COLS = 5;
const ROWS = 3;
const CARD_W = 252;
const CARD_H = 152;
const GAP = 30;

const CharterCard: React.FC<{
  index: number;
  survivor: boolean;
  inFrame: number;
  strikeFrame: number;
  survivorFrame: number;
}> = ({ index, survivor, inFrame, strikeFrame, survivorFrame }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const start = inFrame + index * 2;
  const { opacity, progress } = getEntrance(frame, fps, start, start + 22);
  const rise = riseFrom(progress, 70);

  const fade = survivor
    ? 1
    : interpolate(frame, [strikeFrame + 10, strikeFrame + 24], [1, 0.46], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      });

  const pop = spring({
    frame: frame - survivorFrame,
    fps,
    config: { damping: 13, mass: 0.6, stiffness: 190 },
    durationInFrames: 24,
  });
  const scale = survivor ? interpolate(pop, [0, 1], [1, 1.11]) : 1;
  const ring = survivor
    ? interpolate(frame, [survivorFrame, survivorFrame + 10], [0, 1], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      })
    : 0;

  const tilt = ((index * 37) % 7) / 7 - 0.5;

  return (
    <div
      style={{
        position: "relative",
        width: CARD_W,
        height: CARD_H,
        opacity: opacity * fade,
        transform: `translateY(${rise}px) rotate(${(tilt * 1.6).toFixed(2)}deg) scale(${scale})`,
        background: C.card,
        filter: DROP,
        padding: "26px 24px",
        boxShadow: ring > 0 ? `0 0 0 ${(ring * 7).toFixed(1)}px ${C.red}` : undefined,
      }}
    >
      {[1, 0.82, 0.94].map((w, i) => (
        <div
          key={i}
          style={{
            height: 8,
            width: `${w * 82}%`,
            background: C.inkDeep,
            opacity: 0.26,
            marginBottom: 16,
            borderRadius: 2,
          }}
        />
      ))}
      <div
        style={{
          position: "absolute",
          right: 22,
          bottom: 20,
          width: 30,
          height: 30,
          borderRadius: "50%",
          background: survivor && ring > 0 ? C.red : C.inkDeep,
          opacity: survivor && ring > 0 ? 1 : 0.26,
        }}
      />
      {survivor ? null : (
        <Strike startFrame={strikeFrame} duration={7} top="46%" thickness={9} inset={3} />
      )}
    </div>
  );
};

export const AnnexationScene: React.FC<AnnexationProps> = ({
  texasStartFrame = 4,
  texasEndFrame = 42,
  texasWidth = 520,
  labelStrikeFrame = 54,
  annexStampFrame = 71,
  unionLabelFrame = 104,
  actOneOutFrame = 150,
  gridInFrame = 176,
  headingFrame = 178,
  strikeStartFrame = 244,
  strikeSpacing = 4,
  survivorIndex = 7,
  survivorFrame = 304,
  deskStartFrame = 0,
  deskEndFrame = 24,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const tx = getEntrance(frame, fps, texasStartFrame, texasEndFrame);
  const txRise = riseFrom(tx.progress, 340);
  const actOne = interpolate(frame, [actOneOutFrame, actOneOutFrame + 22], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.in(Easing.cubic),
  });
  const union = getEntrance(frame, fps, unionLabelFrame, unionLabelFrame + 18);
  const heading = getEntrance(frame, fps, headingFrame, headingFrame + 24);
  const survivorPlate = getEntrance(frame, fps, survivorFrame + 8, survivorFrame + 30);

  const texasHeight = (texasWidth * 946) / 1000;
  let struck = -1;

  return (
    <AbsoluteFill style={{ backgroundColor: C.paper, overflow: "hidden" }}>
      <Paper />

      {/* Act one: the republic ends. */}
      <div style={{ opacity: actOne, pointerEvents: "none" }}>
        <svg
          viewBox={TEXAS_VIEWBOX}
          aria-hidden="true"
          style={{
            position: "absolute",
            left: 960 - 26,
            bottom: 300,
            width: texasWidth,
            height: texasHeight,
            opacity: tx.opacity,
            transform: `translate(-50%, ${txRise + 12}px)`,
            zIndex: 11,
          }}
        >
          <path d={TEXAS_PATH} fill={C.red} />
        </svg>
        <svg
          viewBox={TEXAS_VIEWBOX}
          style={{
            position: "absolute",
            left: 960,
            bottom: 300,
            width: texasWidth,
            height: texasHeight,
            opacity: tx.opacity,
            transform: `translate(-50%, ${txRise}px)`,
            filter: DROP,
            zIndex: 12,
          }}
        >
          <path d={TEXAS_PATH} fill={C.ink} />
        </svg>

        <div
          style={{
            position: "absolute",
            left: 960,
            top: 128,
            transform: "translateX(-50%)",
            opacity: tx.opacity,
            zIndex: 20,
          }}
        >
          <div
            style={{
              position: "relative",
              display: "inline-block",
              fontFamily: ARIAL,
              fontSize: 42,
              letterSpacing: 9,
              color: C.ink,
            }}
          >
            REPUBLIC OF TEXAS
            <Strike startFrame={labelStrikeFrame} duration={12} top="50%" thickness={8} />
          </div>
        </div>

        <Stamp
          startFrame={annexStampFrame}
          x={0}
          y={-8}
          rotate={-7}
          width={620}
          title="ANNEXED"
        />

        <div
          style={{
            position: "absolute",
            left: 960,
            bottom: 214,
            transform: `translate(-50%, ${riseFrom(union.progress, 34)}px)`,
            opacity: union.opacity,
            fontFamily: ARIAL,
            fontSize: 26,
            letterSpacing: 7,
            color: "rgba(26,26,26,0.6)",
            zIndex: 22,
          }}
        >
          DECEMBER 29, 1845 · UNITED STATES
        </div>
      </div>

      {/* Act two: fifteen charters, fourteen struck. */}
      <div
        style={{
          position: "absolute",
          left: 960,
          top: 138,
          transform: `translate(-50%, ${riseFrom(heading.progress, 40)}px)`,
          opacity: heading.opacity,
          textAlign: "center",
          zIndex: 20,
        }}
      >
        <div style={{ fontFamily: ARIAL, fontSize: 44, letterSpacing: 7, color: C.ink }}>
          FIFTEEN COLLEGES CHARTERED
        </div>
        <div style={{ height: 5, width: 150, background: C.red, margin: "18px auto 0" }} />
      </div>

      <div
        style={{
          position: "absolute",
          left: 960,
          top: 296,
          transform: "translateX(-50%)",
          display: "grid",
          gridTemplateColumns: `repeat(${COLS}, ${CARD_W}px)`,
          gridAutoRows: `${CARD_H}px`,
          gap: GAP,
          zIndex: 14,
        }}
      >
        {Array.from({ length: COLS * ROWS }, (_, i) => {
          const survivor = i === survivorIndex;
          if (!survivor) struck += 1;
          return (
            <CharterCard
              key={i}
              index={i}
              survivor={survivor}
              inFrame={gridInFrame}
              strikeFrame={strikeStartFrame + struck * strikeSpacing}
              survivorFrame={survivorFrame}
            />
          );
        })}
      </div>

      <DeskEdge startFrame={deskStartFrame} endFrame={deskEndFrame} height={200} />

      <div
        style={{
          position: "absolute",
          left: 960,
          bottom: 52,
          transform: `translate(-50%, ${riseFrom(survivorPlate.progress, 40)}px)`,
          opacity: survivorPlate.opacity,
          textAlign: "center",
          zIndex: 26,
        }}
      >
        <div style={{ fontFamily: ARIAL, fontSize: 21, letterSpacing: 7, color: C.red }}>
          STILL OPERATING
        </div>
        <div
          style={{
            fontFamily: ARIAL,
            fontSize: 44,
            letterSpacing: 3,
            color: "rgba(240,236,228,0.94)",
            marginTop: 12,
          }}
        >
          BAYLOR UNIVERSITY
        </div>
      </div>

      <Grain />
    </AbsoluteFill>
  );
};
