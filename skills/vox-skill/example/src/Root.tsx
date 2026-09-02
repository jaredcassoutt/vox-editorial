import React from "react";
import { Composition } from "remotion";
import { BaylorFoundingSequence, SEQUENCE_DURATION } from "./scenes/BaylorFoundingSequence";
import { D } from "./shared/timing";
import { OlderThanStateScene } from "./scenes/OlderThanStateScene";
import { RepublicScene } from "./scenes/RepublicScene";
import { PetitionScene } from "./scenes/PetitionScene";
import { FoundersScene } from "./scenes/FoundersScene";
import { NamingScene } from "./scenes/NamingScene";
import { SigningScene } from "./scenes/SigningScene";
import { AnnexationScene } from "./scenes/AnnexationScene";
import { CloserScene } from "./scenes/CloserScene";

// Every defaultProps below is an INLINE object literal. Remotion Studio cannot
// write prop edits back to disk otherwise, and every tuning session is lost.
export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="BaylorFoundingSequence"
        component={BaylorFoundingSequence}
        durationInFrames={SEQUENCE_DURATION}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{}}
      />

      <Composition
        id="OlderThanState"
        component={OlderThanStateScene}
        durationInFrames={D.olderThanState}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          texasWidth: 640,
          texasX: 302,
          texasBottom: 214,
          texasStartFrame: 6,
          texasEndFrame: 46,
          strokeX: -30,
          strokeY: 12,
          captionFrame: 52,
          stampFrame: 130,
          stampStrikeFrame: 184,
          deskStartFrame: 0,
          deskEndFrame: 28,
        }}
      />

      <Composition
        id="Republic"
        component={RepublicScene}
        durationInFrames={D.republic}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          yearFrame: 6,
          captionFrame: 56,
          flagStartFrame: 148,
          flagEndFrame: 192,
          flagX: 470,
          flagBottom: 180,
          flagWidth: 640,
          strokeX: 30,
          strokeY: 12,
          timelineFrame: 193,
          timelineDrawFrames: 34,
          nineFrame: 206,
          debtFrame: 234,
          bracketFrame: 266,
          deskStartFrame: 0,
          deskEndFrame: 26,
        }}
      />

      <Composition
        id="Petition"
        component={PetitionScene}
        durationInFrames={D.petition}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          docX: -120,
          docBottom: 150,
          docWidth: 980,
          docHeight: 640,
          docStartFrame: 8,
          docEndFrame: 50,
          strokeX: -28,
          strokeY: 12,
          titleFrame: 30,
          sealFrame: 94,
          captionFrame: 60,
          deskStartFrame: 0,
          deskEndFrame: 24,
        }}
      />

      <Composition
        id="Founders"
        component={FoundersScene}
        durationInFrames={D.founders}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          kickerFrame: 24,
          baylorX: -608,
          baylorWidth: 573,
          baylorStartFrame: 78,
          baylorEndFrame: 118,
          baylorPlateFrame: 130,
          huckinsX: 0,
          huckinsWidth: 488,
          huckinsStartFrame: 168,
          huckinsEndFrame: 208,
          huckinsPlateFrame: 208,
          tryonX: 608,
          tryonWidth: 446,
          tryonStartFrame: 254,
          tryonEndFrame: 294,
          tryonPlateFrame: 300,
          portraitHeight: 600,
          portraitBottom: 250,
          deskHeight: 300,
          deskStartFrame: 0,
          deskEndFrame: 26,
        }}
      />

      <Composition
        id="Naming"
        component={NamingScene}
        durationInFrames={D.naming}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          kickerFrame: 8,
          cardX: 546,
          cardBottom: 196,
          cardWidth: 700,
          cardHeight: 624,
          cardStartFrame: 10,
          cardEndFrame: 54,
          strokeX: 28,
          strokeY: 12,
          sanJacintoFrame: 24,
          sanJacintoStrike: 50,
          milamFrame: 78,
          milamStrike: 103,
          baylorFrame: 254,
          baylorRuleFrame: 268,
          baylorSubFrame: 276,
          deskStartFrame: 0,
          deskEndFrame: 26,
        }}
      />

      <Composition
        id="Signing"
        component={SigningScene}
        durationInFrames={D.signing}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          jonesX: -586,
          jonesWidth: 440,
          jonesHeight: 604,
          jonesBottom: 248,
          jonesStartFrame: 6,
          jonesEndFrame: 44,
          platesFrame: 50,
          cardX: 430,
          cardBottom: 200,
          cardWidth: 760,
          cardHeight: 580,
          cardStartFrame: 4,
          cardEndFrame: 42,
          strokeX: 28,
          strokeY: 12,
          dateStampFrame: 20,
          signStartFrame: 76,
          signEndFrame: 128,
          deskStartFrame: 0,
          deskEndFrame: 22,
        }}
      />

      <Composition
        id="Annexation"
        component={AnnexationScene}
        durationInFrames={D.annexation}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          texasStartFrame: 4,
          texasEndFrame: 42,
          texasWidth: 520,
          labelStrikeFrame: 54,
          annexStampFrame: 71,
          unionLabelFrame: 104,
          actOneOutFrame: 150,
          gridInFrame: 176,
          headingFrame: 178,
          strikeStartFrame: 244,
          strikeSpacing: 4,
          survivorIndex: 7,
          survivorFrame: 304,
          deskStartFrame: 0,
          deskEndFrame: 24,
        }}
      />

      <Composition
        id="Closer"
        component={CloserScene}
        durationInFrames={D.closer}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          cardStartFrame: 0,
          cardEndFrame: 40,
          cardBottom: 170,
          cardWidth: 940,
          cardHeight: 690,
          cardOpacity: 0.62,
          line1Start: 3,
          line1End: 66,
          revealFrame: 98,
          ruleFrame: 110,
          subFrame: 116,
          line2Start: 100,
          line2End: 146,
          sealFrame: 126,
          vignetteFrame: 148,
          deskStartFrame: 0,
          deskEndFrame: 24,
        }}
      />
    </>
  );
};
