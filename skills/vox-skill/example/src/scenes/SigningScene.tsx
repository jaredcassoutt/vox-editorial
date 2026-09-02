import React from "react";
import {
  AbsoluteFill,
  Easing,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { z } from "zod";
import { C, Cutout, DROP, Grain, Paper, getEntrance, riseFrom } from "../shared/system";
import { ARIAL, DeskEdge, Nameplate, Stamp, tornClip } from "../shared/pieces";
import { PLAYFAIR } from "../shared/fonts";

export const SIGNING_DURATION = 146;

export const signingSchema = z.object({
  jonesX: z.number().default(-586),
  jonesWidth: z.number().default(440),
  jonesHeight: z.number().default(604),
  jonesBottom: z.number().default(248),
  jonesStartFrame: z.number().default(6),
  jonesEndFrame: z.number().default(44),
  platesFrame: z.number().default(50),
  cardX: z.number().default(430),
  cardBottom: z.number().default(200),
  cardWidth: z.number().default(760),
  cardHeight: z.number().default(580),
  cardStartFrame: z.number().default(4),
  cardEndFrame: z.number().default(42),
  strokeX: z.number().default(28),
  strokeY: z.number().default(12),
  dateStampFrame: z.number().default(20),
  signStartFrame: z.number().default(76),
  signEndFrame: z.number().default(128),
  deskStartFrame: z.number().default(0),
  deskEndFrame: z.number().default(22),
});

export type SigningProps = z.infer<typeof signingSchema>;

/** Not a facsimile: a plausible hand, drawn so it reads as a signature at 30fps. */
const SIGNATURE =
  "M 8 118 C 22 60 44 14 64 18 C 82 22 78 66 66 96 C 58 116 44 118 40 104 " +
  "C 36 88 58 78 92 82 C 118 85 132 78 142 60 C 150 46 140 108 158 112 " +
  "C 176 116 184 74 196 62 C 206 52 202 110 222 110 C 246 110 258 52 276 22 " +
  "C 288 2 292 96 312 104 C 330 111 342 80 352 64 C 362 48 358 108 378 110 " +
  "C 398 112 408 76 420 60 C 430 46 428 104 448 106 C 470 108 486 84 500 52 " +
  "C 508 34 478 30 452 46";

export const SigningScene: React.FC<SigningProps> = ({
  jonesX = -586,
  jonesWidth = 440,
  jonesHeight = 604,
  jonesBottom = 248,
  jonesStartFrame = 6,
  jonesEndFrame = 44,
  platesFrame = 50,
  cardX = 430,
  cardBottom = 200,
  cardWidth = 760,
  cardHeight = 580,
  cardStartFrame = 4,
  cardEndFrame = 42,
  strokeX = 28,
  strokeY = 12,
  dateStampFrame = 20,
  signStartFrame = 76,
  signEndFrame = 128,
  deskStartFrame = 0,
  deskEndFrame = 22,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const card = getEntrance(frame, fps, cardStartFrame, cardEndFrame);
  const cardRise = riseFrom(card.progress, 360);
  const sign = interpolate(frame, [signStartFrame, signEndFrame], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.inOut(Easing.cubic),
  });

  const cardBox: React.CSSProperties = {
    position: "absolute",
    bottom: cardBottom,
    width: cardWidth,
    height: cardHeight,
    opacity: card.opacity,
    transformOrigin: "center bottom",
  };

  return (
    <AbsoluteFill style={{ backgroundColor: C.paper, overflow: "hidden" }}>
      <Paper />

      <Cutout
        asset="portraits/jones.png"
        x={jonesX}
        y={0}
        width={jonesWidth}
        height={jonesHeight}
        bottom={jonesBottom}
        startFrame={jonesStartFrame}
        endFrame={jonesEndFrame}
        strokeX={-28}
        strokeY={10}
        frame={frame}
        fps={fps}
      />

      <div
        aria-hidden="true"
        style={{
          ...cardBox,
          left: 960 + cardX + strokeX,
          background: C.red,
          clipPath: tornClip(31, 18, 2.2),
          transform: `translate(-50%, ${cardRise + strokeY}px) rotate(-1.1deg)`,
          zIndex: 11,
        }}
      />
      <div
        style={{
          ...cardBox,
          left: 960 + cardX,
          background: C.card,
          clipPath: tornClip(31, 18, 2.2),
          transform: `translate(-50%, ${cardRise}px) rotate(-1.1deg)`,
          filter: DROP,
          padding: "54px 58px",
          zIndex: 12,
        }}
      >
        <div
          style={{
            fontFamily: ARIAL,
            fontSize: 17,
            letterSpacing: 6,
            color: "rgba(26,26,26,0.45)",
          }}
        >
          APPROVED BY THE CONGRESS
        </div>
        <div
          style={{
            fontFamily: PLAYFAIR,
            fontSize: 48,
            lineHeight: 1.16,
            color: C.inkDeep,
            marginTop: 16,
          }}
        >
          An Act to Incorporate Baylor University
        </div>
        <div style={{ height: 3, background: C.inkDeep, opacity: 0.5, margin: "22px 0 24px" }} />
        {[1, 0.9, 0.62].map((w, i) => (
          <div
            key={i}
            style={{
              height: 9,
              width: `${w * 86}%`,
              background: C.inkDeep,
              opacity: 0.15,
              marginBottom: 18,
              borderRadius: 2,
            }}
          />
        ))}

        <svg
          viewBox="0 0 500 140"
          width={470}
          height={132}
          style={{ display: "block", marginTop: 14, overflow: "visible" }}
        >
          <path
            d={SIGNATURE}
            stroke={C.inkDeep}
            strokeWidth={6}
            strokeLinecap="round"
            strokeLinejoin="round"
            fill="none"
            pathLength={1}
            strokeDasharray={1}
            strokeDashoffset={sign}
          />
        </svg>
        <div
          style={{
            width: 470,
            height: 2,
            background: C.inkDeep,
            opacity: 0.4,
            marginTop: -4,
          }}
        />
        <div
          style={{
            fontFamily: ARIAL,
            fontSize: 17,
            letterSpacing: 5,
            color: "rgba(26,26,26,0.5)",
            marginTop: 12,
          }}
        >
          PRESIDENT OF THE REPUBLIC
        </div>
      </div>

      <Stamp
        startFrame={dateStampFrame}
        x={118}
        y={-312}
        rotate={-8}
        width={470}
        title="FEBRUARY 1"
        sub="1845"
      />

      <DeskEdge startFrame={deskStartFrame} endFrame={deskEndFrame} height={230} />

      <Nameplate
        startFrame={platesFrame}
        x={jonesX}
        bottom={54}
        name="ANSON JONES"
        role="PRESIDENT · REPUBLIC OF TEXAS"
        width={470}
        rotate={-0.6}
      />

      <Grain />
    </AbsoluteFill>
  );
};
