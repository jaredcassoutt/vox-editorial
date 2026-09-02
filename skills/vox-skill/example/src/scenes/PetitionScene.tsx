import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { z } from "zod";
import { C, DROP, Grain, Paper, getEntrance, riseFrom } from "../shared/system";
import { ARIAL, DeskEdge, Seal, tornClip } from "../shared/pieces";
import { PLAYFAIR } from "../shared/fonts";

export const PETITION_DURATION = 151;

export const petitionSchema = z.object({
  docX: z.number().default(-120),
  docBottom: z.number().default(150),
  docWidth: z.number().default(980),
  docHeight: z.number().default(640),
  docStartFrame: z.number().default(8),
  docEndFrame: z.number().default(50),
  strokeX: z.number().default(-28),
  strokeY: z.number().default(12),
  titleFrame: z.number().default(30),
  sealFrame: z.number().default(94),
  captionFrame: z.number().default(60),
  deskStartFrame: z.number().default(0),
  deskEndFrame: z.number().default(24),
});

export type PetitionProps = z.infer<typeof petitionSchema>;

/** Ruled lines rather than invented text: it reads as a document without
 *  putting words in a real petition's mouth. */
const RULED = [1, 0.96, 0.99, 0.82, 0.97, 0.93, 0.62];

export const PetitionScene: React.FC<PetitionProps> = ({
  docX = -120,
  docBottom = 150,
  docWidth = 980,
  docHeight = 640,
  docStartFrame = 8,
  docEndFrame = 50,
  strokeX = -28,
  strokeY = 12,
  titleFrame = 30,
  sealFrame = 94,
  captionFrame = 60,
  deskStartFrame = 0,
  deskEndFrame = 24,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const doc = getEntrance(frame, fps, docStartFrame, docEndFrame);
  const rise = riseFrom(doc.progress, 380);
  const title = getEntrance(frame, fps, titleFrame, titleFrame + 22);
  const cap = getEntrance(frame, fps, captionFrame, captionFrame + 22);

  const box: React.CSSProperties = {
    position: "absolute",
    bottom: docBottom,
    width: docWidth,
    height: docHeight,
    opacity: doc.opacity,
    transformOrigin: "center bottom",
  };

  return (
    <AbsoluteFill style={{ backgroundColor: C.paper, overflow: "hidden" }}>
      <Paper />

      <div
        aria-hidden="true"
        style={{
          ...box,
          left: 960 + docX + strokeX,
          background: C.red,
          clipPath: tornClip(11, 18, 2.4),
          transform: `translate(-50%, ${rise + strokeY}px) rotate(1.6deg)`,
          zIndex: 11,
        }}
      />
      <div
        style={{
          ...box,
          left: 960 + docX,
          background: C.card,
          clipPath: tornClip(11, 18, 2.4),
          transform: `translate(-50%, ${rise}px) rotate(1.6deg)`,
          filter: DROP,
          padding: "62px 76px",
          zIndex: 12,
        }}
      >
        <div style={{ opacity: title.opacity }}>
          <div
            style={{
              fontFamily: ARIAL,
              fontSize: 19,
              letterSpacing: 7,
              color: "rgba(26,26,26,0.5)",
            }}
          >
            WINTER · 1845
          </div>
          <div
            style={{
              fontFamily: PLAYFAIR,
              fontSize: 56,
              lineHeight: 1.12,
              color: C.inkDeep,
              marginTop: 20,
              maxWidth: 700,
            }}
          >
            Petition of the Texas Baptist Education Society
          </div>
          <div style={{ height: 3, background: C.inkDeep, opacity: 0.55, margin: "26px 0 30px" }} />
        </div>

        {RULED.map((w, i) => (
          <div
            key={i}
            style={{
              height: 9,
              width: `${w * 78}%`,
              background: C.inkDeep,
              opacity: 0.16,
              marginBottom: 20,
              borderRadius: 2,
            }}
          />
        ))}
      </div>

      <div
        style={{
          position: "absolute",
          left: 960 + docX + docWidth / 2 - 150,
          bottom: docBottom + 66,
          transform: `translateY(${rise}px)`,
          opacity: doc.opacity,
          zIndex: 20,
        }}
      >
        <Seal startFrame={sealFrame} size={150} label="1845" />
      </div>

      <div
        style={{
          position: "absolute",
          right: 108,
          top: 128,
          textAlign: "right",
          opacity: cap.opacity,
          transform: `translateY(${riseFrom(cap.progress, 46)}px)`,
          zIndex: 20,
        }}
      >
        <div style={{ fontFamily: ARIAL, fontSize: 40, letterSpacing: 4, color: C.ink }}>
          A PETITION
        </div>
        <div style={{ height: 5, background: C.red, margin: "16px 0 14px", marginLeft: "auto", width: 150 }} />
        <div
          style={{
            fontFamily: ARIAL,
            fontSize: 21,
            letterSpacing: 5,
            color: "rgba(26,26,26,0.55)",
            lineHeight: 1.7,
          }}
        >
          FOR A BAPTIST UNIVERSITY
          <br />
          IN THE REPUBLIC OF TEXAS
        </div>
      </div>

      <DeskEdge startFrame={deskStartFrame} endFrame={deskEndFrame} height={210} />
      <Grain />
    </AbsoluteFill>
  );
};
