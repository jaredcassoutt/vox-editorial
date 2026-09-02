import React from "react";
import {
  AbsoluteFill,
  Easing,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { z } from "zod";
import { C, DROP, Grain, Paper, getEntrance, riseFrom } from "../shared/system";
import { ARIAL, DeskEdge, Stamp } from "../shared/pieces";

export const REPUBLIC_DURATION = 334;

export const republicSchema = z.object({
  yearFrame: z.number().default(6),
  captionFrame: z.number().default(56),
  flagStartFrame: z.number().default(148),
  flagEndFrame: z.number().default(192),
  flagX: z.number().default(470),
  flagBottom: z.number().default(180),
  flagWidth: z.number().default(640),
  strokeX: z.number().default(30),
  strokeY: z.number().default(12),
  timelineFrame: z.number().default(193),
  timelineDrawFrames: z.number().default(34),
  nineFrame: z.number().default(206),
  debtFrame: z.number().default(234),
  bracketFrame: z.number().default(266),
  deskStartFrame: z.number().default(0),
  deskEndFrame: z.number().default(26),
});

export type RepublicProps = z.infer<typeof republicSchema>;

const STAR =
  "50,4 61.8,35.5 95,36.5 68.5,57 78.5,89 50,69.5 21.5,89 31.5,57 5,36.5 38.2,35.5";

/** The lone star, rebuilt in the film's four inks rather than its real colours. */
const FlagCard: React.FC<{
  x: number;
  bottom: number;
  width: number;
  startFrame: number;
  endFrame: number;
  strokeX: number;
  strokeY: number;
}> = ({ x, bottom, width, startFrame, endFrame, strokeX, strokeY }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { opacity, progress } = getEntrance(frame, fps, startFrame, endFrame);
  const rise = riseFrom(progress, 380);
  const height = Math.round((width * 2) / 3);
  const band = Math.round(width / 3);
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
      <div
        aria-hidden="true"
        style={{
          ...box,
          left: 960 + x + strokeX,
          background: C.red,
          transform: `translate(-50%, ${rise + strokeY}px) rotate(1.4deg)`,
          zIndex: 11,
        }}
      />
      <div
        style={{
          ...box,
          left: 960 + x,
          display: "flex",
          background: C.card,
          transform: `translate(-50%, ${rise}px) rotate(1.4deg)`,
          filter: DROP,
          zIndex: 12,
        }}
      >
        <div
          style={{
            width: band,
            background: C.ink,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          <svg viewBox="0 0 100 94" width={band * 0.52}>
            <polygon points={STAR} fill={C.card} />
          </svg>
        </div>
        <div style={{ flex: 1, display: "flex", flexDirection: "column" }}>
          <div style={{ flex: 1, background: "#EDE9DE" }} />
          <div style={{ flex: 1, background: C.red }} />
        </div>
      </div>
    </>
  );
};

export const RepublicScene: React.FC<RepublicProps> = ({
  yearFrame = 6,
  captionFrame = 56,
  flagStartFrame = 148,
  flagEndFrame = 192,
  flagX = 470,
  flagBottom = 180,
  flagWidth = 640,
  strokeX = 30,
  strokeY = 12,
  timelineFrame = 193,
  timelineDrawFrames = 34,
  nineFrame = 206,
  debtFrame = 234,
  bracketFrame = 266,
  deskStartFrame = 0,
  deskEndFrame = 26,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const year = getEntrance(frame, fps, yearFrame, yearFrame + 34);
  const cap = getEntrance(frame, fps, captionFrame, captionFrame + 24);
  const nine = getEntrance(frame, fps, nineFrame, nineFrame + 20);

  const line = interpolate(
    frame,
    [timelineFrame, timelineFrame + timelineDrawFrames],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.inOut(Easing.cubic) },
  );
  const bracket = interpolate(frame, [bracketFrame, bracketFrame + 16], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });

  return (
    <AbsoluteFill style={{ backgroundColor: C.paper, overflow: "hidden" }}>
      <Paper />

      {/* Beat 3: the year, big, with the marker stroke applied to type. */}
      <div
        style={{
          position: "absolute",
          left: 128,
          top: 62,
          opacity: year.opacity,
          transform: `translateY(${riseFrom(year.progress, 260)}px)`,
          zIndex: 20,
        }}
      >
        <div style={{ position: "relative" }}>
          <div
            aria-hidden="true"
            style={{
              position: "absolute",
              left: -26,
              top: 12,
              fontFamily: ARIAL,
              fontSize: 250,
              lineHeight: 0.86,
              letterSpacing: -8,
              color: C.red,
            }}
          >
            1845
          </div>
          <div
            style={{
              position: "relative",
              fontFamily: ARIAL,
              fontSize: 250,
              lineHeight: 0.86,
              letterSpacing: -8,
              color: C.ink,
            }}
          >
            1845
          </div>
        </div>
      </div>

      <div
        style={{
          position: "absolute",
          left: 134,
          top: 318,
          opacity: cap.opacity,
          transform: `translateY(${riseFrom(cap.progress, 50)}px)`,
          fontFamily: ARIAL,
          fontSize: 44,
          letterSpacing: 6,
          color: "rgba(26,26,26,0.72)",
          zIndex: 20,
        }}
      >
        TEXAS WAS NOT YET AMERICAN
      </div>

      <FlagCard
        x={flagX}
        bottom={flagBottom}
        width={flagWidth}
        startFrame={flagStartFrame}
        endFrame={flagEndFrame}
        strokeX={strokeX}
        strokeY={strokeY}
      />

      {/* Beat 4: one timeline, annotated three times as the line is spoken. */}
      <div style={{ position: "absolute", left: 128, top: 416, width: 730, zIndex: 20 }}>
        <div
          style={{
            fontFamily: ARIAL,
            fontSize: 26,
            letterSpacing: 8,
            color: "rgba(26,26,26,0.5)",
            marginBottom: 26,
            opacity: nine.opacity,
          }}
        >
          THE REPUBLIC OF TEXAS
        </div>

        <svg viewBox="0 0 730 60" width={730} height={60} style={{ overflow: "visible" }}>
          <path
            d="M 6 30 L 724 30"
            stroke={C.ink}
            strokeWidth={6}
            fill="none"
            pathLength={1}
            strokeDasharray={1}
            strokeDashoffset={line}
          />
          <path
            d="M 6 6 L 6 54"
            stroke={C.ink}
            strokeWidth={6}
            fill="none"
            pathLength={1}
            strokeDasharray={1}
            strokeDashoffset={line}
          />
          <path
            d="M 724 6 L 724 54"
            stroke={C.red}
            strokeWidth={8}
            fill="none"
            pathLength={1}
            strokeDasharray={1}
            strokeDashoffset={bracket}
          />
        </svg>

        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            marginTop: 14,
            fontFamily: ARIAL,
            fontSize: 22,
            letterSpacing: 4,
            color: "rgba(26,26,26,0.62)",
            opacity: 1 - line,
          }}
        >
          <span>MARCH 2, 1836</span>
          <span style={{ color: bracket < 0.5 ? C.red : "rgba(26,26,26,0.62)" }}>
            DECEMBER 1845
          </span>
        </div>

        <div
          style={{
            marginTop: 18,
            fontFamily: ARIAL,
            fontSize: 62,
            letterSpacing: 2,
            color: C.ink,
            opacity: nine.opacity,
            transform: `translateY(${riseFrom(nine.progress, 40)}px)`,
          }}
        >
          NINE YEARS OLD
        </div>
      </div>

      <Stamp
        startFrame={debtFrame}
        x={-520}
        y={252}
        rotate={-7}
        width={412}
        title="DEEP IN DEBT"
      />

      <DeskEdge startFrame={deskStartFrame} endFrame={deskEndFrame} height={220} />
      <Grain />
    </AbsoluteFill>
  );
};
