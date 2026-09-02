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
import { ARIAL, DeskEdge, Strike, tornClip } from "../shared/pieces";
import { PLAYFAIR } from "../shared/fonts";

export const NAMING_DURATION = 313;

export const namingSchema = z.object({
  kickerFrame: z.number().default(8),
  cardX: z.number().default(546),
  cardBottom: z.number().default(196),
  cardWidth: z.number().default(700),
  cardHeight: z.number().default(624),
  cardStartFrame: z.number().default(10),
  cardEndFrame: z.number().default(54),
  strokeX: z.number().default(28),
  strokeY: z.number().default(12),
  sanJacintoFrame: z.number().default(24),
  sanJacintoStrike: z.number().default(50),
  milamFrame: z.number().default(78),
  milamStrike: z.number().default(103),
  baylorFrame: z.number().default(254),
  baylorRuleFrame: z.number().default(268),
  baylorSubFrame: z.number().default(276),
  deskStartFrame: z.number().default(0),
  deskEndFrame: z.number().default(26),
});

export type NamingProps = z.infer<typeof namingSchema>;

const Candidate: React.FC<{
  label: string;
  startFrame: number;
  strikeFrame: number;
  top: number;
}> = ({ label, startFrame, strikeFrame, top }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { opacity, progress } = getEntrance(frame, fps, startFrame, startFrame + 26);
  const fade = interpolate(frame, [strikeFrame + 12, strikeFrame + 26], [1, 0.34], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  return (
    <div
      style={{
        position: "absolute",
        left: 0,
        top,
        opacity: opacity * fade,
        transform: `translateY(${riseFrom(progress, 54)}px)`,
      }}
    >
      <div
        style={{
          position: "relative",
          display: "inline-block",
          fontFamily: ARIAL,
          fontSize: 96,
          letterSpacing: -2,
          color: C.ink,
        }}
      >
        {label}
        <Strike startFrame={strikeFrame} duration={10} top="52%" thickness={10} />
      </div>
    </div>
  );
};

export const NamingScene: React.FC<NamingProps> = ({
  kickerFrame = 8,
  cardX = 546,
  cardBottom = 196,
  cardWidth = 700,
  cardHeight = 624,
  cardStartFrame = 10,
  cardEndFrame = 54,
  strokeX = 28,
  strokeY = 12,
  sanJacintoFrame = 24,
  sanJacintoStrike = 50,
  milamFrame = 78,
  milamStrike = 103,
  baylorFrame = 254,
  baylorRuleFrame = 268,
  baylorSubFrame = 276,
  deskStartFrame = 0,
  deskEndFrame = 26,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const kicker = getEntrance(frame, fps, kickerFrame, kickerFrame + 24);
  const card = getEntrance(frame, fps, cardStartFrame, cardEndFrame);
  const cardRise = riseFrom(card.progress, 380);

  const stamp = spring({
    frame: frame - baylorFrame,
    fps,
    config: { damping: 12, mass: 0.62, stiffness: 200 },
    durationInFrames: 26,
  });
  const baylorScale = interpolate(stamp, [0, 1], [1.42, 1]);
  const baylorOpacity = interpolate(frame, [baylorFrame, baylorFrame + 6], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const rule = interpolate(frame, [baylorRuleFrame, baylorRuleFrame + 16], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
  const sub = getEntrance(frame, fps, baylorSubFrame, baylorSubFrame + 20);

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

      {/* Midground: the act itself, held at the right of frame. */}
      <div
        aria-hidden="true"
        style={{
          ...cardBox,
          left: 960 + cardX + strokeX,
          background: C.red,
          clipPath: tornClip(21, 18, 2.2),
          transform: `translate(-50%, ${cardRise + strokeY}px) rotate(1.2deg)`,
          zIndex: 11,
        }}
      />
      <div
        style={{
          ...cardBox,
          left: 960 + cardX,
          background: C.card,
          clipPath: tornClip(21, 18, 2.2),
          transform: `translate(-50%, ${cardRise}px) rotate(1.2deg)`,
          filter: DROP,
          padding: "56px 60px",
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
          AN ACT TO INCORPORATE
        </div>
        <div
          style={{
            fontFamily: PLAYFAIR,
            fontSize: 46,
            lineHeight: 1.18,
            color: C.inkDeep,
            marginTop: 18,
          }}
        >
          A University in the Town of Independence
        </div>
        <div style={{ height: 3, background: C.inkDeep, opacity: 0.5, margin: "26px 0 28px" }} />
        {[1, 0.93, 0.98, 0.72, 0.95, 0.55].map((w, i) => (
          <div
            key={i}
            style={{
              height: 9,
              width: `${w * 88}%`,
              background: C.inkDeep,
              opacity: 0.15,
              marginBottom: 19,
              borderRadius: 2,
            }}
          />
        ))}
      </div>

      {/* The naming, as three candidates: two struck, one stamped. */}
      <div style={{ position: "absolute", left: 168, top: 186, width: 820, zIndex: 20 }}>
        <div
          style={{
            opacity: kicker.opacity,
            transform: `translateY(${riseFrom(kicker.progress, 42)}px)`,
            fontFamily: ARIAL,
            fontSize: 26,
            letterSpacing: 9,
            color: "rgba(26,26,26,0.52)",
          }}
        >
          THE NAME ON THE CHARTER
        </div>

        <div style={{ position: "relative", height: 480, marginTop: 66 }}>
          <Candidate
            label="SAN JACINTO"
            startFrame={sanJacintoFrame}
            strikeFrame={sanJacintoStrike}
            top={0}
          />
          <Candidate label="MILAM" startFrame={milamFrame} strikeFrame={milamStrike} top={126} />

          <div
            style={{
              position: "absolute",
              left: 0,
              top: 252,
              opacity: baylorOpacity,
              transform: `scale(${baylorScale})`,
              transformOrigin: "left top",
            }}
          >
            <div
              style={{
                fontFamily: ARIAL,
                fontSize: 146,
                letterSpacing: -4,
                lineHeight: 0.94,
                color: C.red,
              }}
            >
              BAYLOR
            </div>
            <div
              style={{
                height: 11,
                width: 560,
                background: C.red,
                marginTop: 16,
                transformOrigin: "left center",
                transform: `scaleX(${rule})`,
              }}
            />
            <div
              style={{
                marginTop: 28,
                opacity: sub.opacity,
                transform: `translateY(${riseFrom(sub.progress, 30)}px)`,
                fontFamily: ARIAL,
                fontSize: 24,
                letterSpacing: 6,
                color: "rgba(26,26,26,0.6)",
              }}
            >
              ASKED FOR JUST BEFORE THE FINAL VOTE
            </div>
          </div>
        </div>
      </div>

      <DeskEdge startFrame={deskStartFrame} endFrame={deskEndFrame} height={196} />
      <Grain />
    </AbsoluteFill>
  );
};
