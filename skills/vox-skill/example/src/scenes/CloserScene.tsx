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
import { ARIAL, DeskEdge, Seal, Typewriter, tornClip } from "../shared/pieces";
import { PLAYFAIR, TYPEWRITER } from "../shared/fonts";

export const CLOSER_DURATION = 198;

export const closerSchema = z.object({
  cardStartFrame: z.number().default(0),
  cardEndFrame: z.number().default(40),
  cardBottom: z.number().default(170),
  cardWidth: z.number().default(940),
  cardHeight: z.number().default(690),
  cardOpacity: z.number().default(0.62),
  line1Start: z.number().default(3),
  line1End: z.number().default(66),
  revealFrame: z.number().default(98),
  ruleFrame: z.number().default(110),
  subFrame: z.number().default(116),
  line2Start: z.number().default(100),
  line2End: z.number().default(146),
  sealFrame: z.number().default(126),
  vignetteFrame: z.number().default(148),
  deskStartFrame: z.number().default(0),
  deskEndFrame: z.number().default(24),
});

export type CloserProps = z.infer<typeof closerSchema>;

export const CloserScene: React.FC<CloserProps> = ({
  cardStartFrame = 0,
  cardEndFrame = 40,
  cardBottom = 170,
  cardWidth = 940,
  cardHeight = 690,
  cardOpacity = 0.62,
  line1Start = 3,
  line1End = 66,
  revealFrame = 98,
  ruleFrame = 110,
  subFrame = 116,
  line2Start = 100,
  line2End = 146,
  sealFrame = 126,
  vignetteFrame = 148,
  deskStartFrame = 0,
  deskEndFrame = 24,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const card = getEntrance(frame, fps, cardStartFrame, cardEndFrame);
  const cardRise = riseFrom(card.progress, 340);

  const stamp = spring({
    frame: frame - revealFrame,
    fps,
    config: { damping: 12, mass: 0.6, stiffness: 200 },
    durationInFrames: 26,
  });
  const revealScale = interpolate(stamp, [0, 1], [1.4, 1]);
  const revealOpacity = interpolate(frame, [revealFrame, revealFrame + 6], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const rule = interpolate(frame, [ruleFrame, ruleFrame + 18], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
  const sub = getEntrance(frame, fps, subFrame, subFrame + 20);
  const vig = interpolate(frame, [vignetteFrame, vignetteFrame + 42], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });

  return (
    <AbsoluteFill style={{ backgroundColor: C.paper, overflow: "hidden" }}>
      <Paper />

      {/* The act itself, held back so the type can sit on it. */}
      <div
        style={{
          position: "absolute",
          left: 960,
          bottom: cardBottom,
          width: cardWidth,
          height: cardHeight,
          opacity: card.opacity * cardOpacity,
          background: C.card,
          clipPath: tornClip(41, 20, 2),
          transform: `translate(-50%, ${cardRise}px) rotate(-1.4deg)`,
          transformOrigin: "center bottom",
          filter: DROP,
          zIndex: 11,
        }}
      />

      <div
        style={{
          position: "absolute",
          left: 960,
          top: 196,
          width: 1160,
          transform: "translateX(-50%)",
          textAlign: "center",
          zIndex: 20,
        }}
      >
        <Typewriter
          text="One still operates under the charter it was given."
          startFrame={line1Start}
          endFrame={line1End}
          style={{
            fontFamily: TYPEWRITER,
            fontSize: 42,
            letterSpacing: 0.5,
            color: "rgba(26,26,26,0.78)",
          }}
        />
      </div>

      <div
        style={{
          position: "absolute",
          left: 960,
          top: 336,
          width: 1560,
          transform: "translateX(-50%)",
          textAlign: "center",
          zIndex: 22,
        }}
      >
        <div
          style={{
            opacity: revealOpacity,
            transform: `scale(${revealScale})`,
          }}
        >
          <div
            style={{
              fontFamily: ARIAL,
              fontSize: 104,
              letterSpacing: -1,
              lineHeight: 0.98,
              whiteSpace: "nowrap",
              color: C.red,
            }}
          >
            BAYLOR UNIVERSITY
          </div>
        </div>
        <div
          style={{
            height: 9,
            width: 700,
            background: C.red,
            margin: "26px auto 0",
            transformOrigin: "center",
            transform: `scaleX(${rule})`,
          }}
        />
        <div
          style={{
            marginTop: 26,
            opacity: sub.opacity,
            transform: `translateY(${riseFrom(sub.progress, 28)}px)`,
            fontFamily: ARIAL,
            fontSize: 25,
            letterSpacing: 6,
            color: "rgba(26,26,26,0.62)",
          }}
        >
          CHARTERED FEBRUARY 1, 1845 · REPUBLIC OF TEXAS
        </div>
      </div>

      <div
        style={{
          position: "absolute",
          left: 960,
          top: 622,
          width: 1200,
          transform: "translateX(-50%)",
          textAlign: "center",
          zIndex: 22,
        }}
      >
        <Typewriter
          text="Older than Texas itself."
          startFrame={line2Start}
          endFrame={line2End}
          style={{
            fontFamily: PLAYFAIR,
            fontStyle: "italic",
            fontSize: 58,
            color: C.inkDeep,
          }}
        />
      </div>

      <div
        style={{
          position: "absolute",
          left: 1516,
          bottom: 214,
          zIndex: 23,
        }}
      >
        <Seal startFrame={sealFrame} size={132} label="1845" />
      </div>

      <DeskEdge startFrame={deskStartFrame} endFrame={deskEndFrame} height={200} />

      <AbsoluteFill
        aria-hidden="true"
        style={{
          background:
            "radial-gradient(circle at 50% 48%, transparent 38%, rgba(20,16,12,0.62) 100%)",
          opacity: vig,
          pointerEvents: "none",
          zIndex: 30,
        }}
      />
      <Grain />
    </AbsoluteFill>
  );
};
