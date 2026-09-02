import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { z } from "zod";
import { C, DROP, Grain, Paper, getEntrance, riseFrom } from "../shared/system";
import { ARIAL, DeskEdge, Stamp } from "../shared/pieces";
import { TEXAS_PATH, TEXAS_VIEWBOX } from "../shared/texas";

export const OLDER_THAN_STATE_DURATION = 241;

export const olderThanStateSchema = z.object({
  texasWidth: z.number().default(640),
  texasX: z.number().default(302),
  texasBottom: z.number().default(214),
  texasStartFrame: z.number().default(6),
  texasEndFrame: z.number().default(46),
  strokeX: z.number().default(-30),
  strokeY: z.number().default(12),
  captionFrame: z.number().default(52),
  stampFrame: z.number().default(130),
  stampStrikeFrame: z.number().default(184),
  deskStartFrame: z.number().default(0),
  deskEndFrame: z.number().default(28),
});

export type OlderThanStateProps = z.infer<typeof olderThanStateSchema>;

/** The state outline, ink, with its offset red marker silhouette behind it. */
const TexasShape: React.FC<{
  width: number;
  x: number;
  bottom: number;
  startFrame: number;
  endFrame: number;
  strokeX: number;
  strokeY: number;
}> = ({ width, x, bottom, startFrame, endFrame, strokeX, strokeY }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { opacity, progress } = getEntrance(frame, fps, startFrame, endFrame);
  const rise = riseFrom(progress, 360);
  const height = (width * 946) / 1000;
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
        viewBox={TEXAS_VIEWBOX}
        aria-hidden="true"
        style={{
          ...box,
          left: 960 + x + strokeX,
          transform: `translate(-50%, ${rise + strokeY}px)`,
          zIndex: 11,
        }}
      >
        <path d={TEXAS_PATH} fill={C.red} />
      </svg>
      <svg
        viewBox={TEXAS_VIEWBOX}
        style={{
          ...box,
          left: 960 + x,
          transform: `translate(-50%, ${rise}px)`,
          filter: DROP,
          zIndex: 12,
        }}
      >
        <path d={TEXAS_PATH} fill={C.ink} />
      </svg>
    </>
  );
};

export const OlderThanStateScene: React.FC<OlderThanStateProps> = ({
  texasWidth = 640,
  texasX = 302,
  texasBottom = 214,
  texasStartFrame = 6,
  texasEndFrame = 46,
  strokeX = -30,
  strokeY = 12,
  captionFrame = 52,
  stampFrame = 130,
  stampStrikeFrame = 184,
  deskStartFrame = 0,
  deskEndFrame = 28,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const cap = getEntrance(frame, fps, captionFrame, captionFrame + 22);

  return (
    <AbsoluteFill style={{ backgroundColor: C.paper, overflow: "hidden" }}>
      <Paper />

      <TexasShape
        width={texasWidth}
        x={texasX}
        bottom={texasBottom}
        startFrame={texasStartFrame}
        endFrame={texasEndFrame}
        strokeX={strokeX}
        strokeY={strokeY}
      />

      {/* The date the viewer will need in ninety seconds, planted early. */}
      <div
        style={{
          position: "absolute",
          left: 960 + texasX,
          top: 78,
          opacity: cap.opacity,
          transform: `translate(-50%, ${riseFrom(cap.progress, 44)}px)`,
          textAlign: "center",
          zIndex: 20,
        }}
      >
        <div style={{ fontFamily: ARIAL, fontSize: 34, letterSpacing: 9, color: C.ink }}>
          THE STATE OF TEXAS
        </div>
        <div
          style={{
            fontFamily: ARIAL,
            fontSize: 20,
            letterSpacing: 6,
            color: "rgba(26,26,26,0.5)",
            whiteSpace: "nowrap",
            marginTop: 12,
          }}
        >
          ADMITTED TO THE UNION · DECEMBER 29, 1845
        </div>
      </div>

      <Stamp
        startFrame={stampFrame}
        x={-472}
        y={48}
        rotate={-5}
        width={620}
        title="REPUBLIC OF TEXAS"
        sub="1836 — 1845"
        subStrikeFrame={stampStrikeFrame}
      />

      <DeskEdge startFrame={deskStartFrame} endFrame={deskEndFrame} height={230} />
      <Grain />
    </AbsoluteFill>
  );
};
