import React from "react";
import { Audio, interpolate, Series, staticFile, useCurrentFrame } from "remotion";
import { z } from "zod";
import { D, SEQUENCE_DURATION } from "../shared/timing";
import { CUE } from "../shared/timing";
import { OlderThanStateScene } from "./OlderThanStateScene";
import { RepublicScene } from "./RepublicScene";
import { PetitionScene } from "./PetitionScene";
import { FoundersScene } from "./FoundersScene";
import { NamingScene } from "./NamingScene";
import { SigningScene } from "./SigningScene";
import { AnnexationScene } from "./AnnexationScene";
import { CloserScene } from "./CloserScene";

export { SEQUENCE_DURATION };

/**
 * Nothing here is a tuned frame number. Scene lengths and every cue come from
 * src/shared/timing.ts, generated from vo/timing.json + cues.json. Change the
 * voice or a line of script, re-run gen_vo.py then sync_timing.py, and the whole
 * film re-times itself. Only layout props are hand-set.
 */

/** Narration and music are pre-mixed in public/audio/mix.mp3 (see mix_audio.sh). */
const BAKE_AUDIO = true;
const AUDIO_TRACK = "audio/mix.mp3";

export const baylorFoundingSequenceSchema = z.object({});

const Narration: React.FC = () => {
  const frame = useCurrentFrame();
  const volume = interpolate(
    frame,
    [0, 10, SEQUENCE_DURATION - 40, SEQUENCE_DURATION],
    [0, 1, 1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
  );
  return <Audio src={staticFile(AUDIO_TRACK)} volume={volume} />;
};

export const BaylorFoundingSequence: React.FC = () => {
  return (
    <>
      {BAKE_AUDIO ? <Narration /> : null}
      <Series>
        <Series.Sequence durationInFrames={D.olderThanState}>
          <OlderThanStateScene
            texasWidth={640}
            texasX={302}
            texasBottom={214}
            texasStartFrame={6}
            texasEndFrame={46}
            strokeX={-30}
            strokeY={12}
            captionFrame={CUE["s1.caption"]}
            stampFrame={CUE["s1.stamp"]}
            stampStrikeFrame={CUE["s1.strike"]}
            deskStartFrame={0}
            deskEndFrame={28}
          />
        </Series.Sequence>

        <Series.Sequence durationInFrames={D.republic}>
          <RepublicScene
            yearFrame={6}
            captionFrame={CUE["s2.caption"]}
            flagStartFrame={CUE["s2.flagIn"]}
            flagEndFrame={CUE["s2.flagOut"]}
            flagX={470}
            flagBottom={180}
            flagWidth={640}
            strokeX={30}
            strokeY={12}
            timelineFrame={CUE["s2.timeline"]}
            timelineDrawFrames={30}
            nineFrame={CUE["s2.nine"]}
            debtFrame={CUE["s2.debt"]}
            bracketFrame={CUE["s2.bracket"]}
            deskStartFrame={0}
            deskEndFrame={26}
          />
        </Series.Sequence>

        <Series.Sequence durationInFrames={D.petition}>
          <PetitionScene
            docX={-120}
            docBottom={150}
            docWidth={980}
            docHeight={640}
            docStartFrame={8}
            docEndFrame={50}
            strokeX={-28}
            strokeY={12}
            titleFrame={30}
            sealFrame={CUE["s3.seal"]}
            captionFrame={CUE["s3.caption"]}
            deskStartFrame={0}
            deskEndFrame={24}
          />
        </Series.Sequence>

        <Series.Sequence durationInFrames={D.founders}>
          <FoundersScene
            kickerFrame={CUE["s4.kicker"]}
            baylorX={-608}
            baylorWidth={573}
            baylorStartFrame={CUE["s4.baylorIn"]}
            baylorEndFrame={CUE["s4.baylorOut"]}
            baylorPlateFrame={CUE["s4.baylorPlate"]}
            huckinsX={0}
            huckinsWidth={488}
            huckinsStartFrame={CUE["s4.huckinsIn"]}
            huckinsEndFrame={CUE["s4.huckinsOut"]}
            huckinsPlateFrame={CUE["s4.huckinsPlate"]}
            tryonX={608}
            tryonWidth={446}
            tryonStartFrame={CUE["s4.tryonIn"]}
            tryonEndFrame={CUE["s4.tryonOut"]}
            tryonPlateFrame={CUE["s4.tryonPlate"]}
            portraitHeight={600}
            portraitBottom={250}
            deskHeight={300}
            deskStartFrame={0}
            deskEndFrame={26}
          />
        </Series.Sequence>

        <Series.Sequence durationInFrames={D.naming}>
          <NamingScene
            kickerFrame={8}
            cardX={546}
            cardBottom={196}
            cardWidth={700}
            cardHeight={624}
            cardStartFrame={10}
            cardEndFrame={54}
            strokeX={28}
            strokeY={12}
            sanJacintoFrame={CUE["s5.sanJacintoIn"]}
            sanJacintoStrike={CUE["s5.sanJacintoStrike"]}
            milamFrame={CUE["s5.milamIn"]}
            milamStrike={CUE["s5.milamStrike"]}
            baylorFrame={CUE["s5.baylor"]}
            baylorRuleFrame={CUE["s5.baylorRule"]}
            baylorSubFrame={CUE["s5.baylorSub"]}
            deskStartFrame={0}
            deskEndFrame={26}
          />
        </Series.Sequence>

        <Series.Sequence durationInFrames={D.signing}>
          <SigningScene
            jonesX={-586}
            jonesWidth={440}
            jonesHeight={604}
            jonesBottom={248}
            jonesStartFrame={6}
            jonesEndFrame={44}
            platesFrame={CUE["s6.plate"]}
            cardX={430}
            cardBottom={200}
            cardWidth={760}
            cardHeight={580}
            cardStartFrame={4}
            cardEndFrame={42}
            strokeX={28}
            strokeY={12}
            dateStampFrame={CUE["s6.dateStamp"]}
            signStartFrame={CUE["s6.signStart"]}
            signEndFrame={CUE["s6.signEnd"]}
            deskStartFrame={0}
            deskEndFrame={22}
          />
        </Series.Sequence>

        <Series.Sequence durationInFrames={D.annexation}>
          <AnnexationScene
            texasStartFrame={4}
            texasEndFrame={42}
            texasWidth={520}
            labelStrikeFrame={CUE["s7.labelStrike"]}
            annexStampFrame={CUE["s7.annexStamp"]}
            unionLabelFrame={CUE["s7.unionLabel"]}
            actOneOutFrame={CUE["s7.actOneOut"]}
            gridInFrame={CUE["s7.gridIn"]}
            headingFrame={CUE["s7.heading"]}
            strikeStartFrame={CUE["s7.strikeStart"]}
            strikeSpacing={4}
            survivorIndex={7}
            survivorFrame={CUE["s7.survivor"]}
            deskStartFrame={0}
            deskEndFrame={24}
          />
        </Series.Sequence>

        <Series.Sequence durationInFrames={D.closer}>
          <CloserScene
            cardStartFrame={0}
            cardEndFrame={40}
            cardBottom={170}
            cardWidth={940}
            cardHeight={690}
            cardOpacity={0.62}
            line1Start={CUE["s8.line1Start"]}
            line1End={CUE["s8.line1End"]}
            revealFrame={CUE["s8.reveal"]}
            ruleFrame={CUE["s8.rule"]}
            subFrame={CUE["s8.sub"]}
            line2Start={CUE["s8.line2Start"]}
            line2End={CUE["s8.line2End"]}
            sealFrame={CUE["s8.seal"]}
            vignetteFrame={CUE["s8.vignette"]}
            deskStartFrame={0}
            deskEndFrame={24}
          />
        </Series.Sequence>
      </Series>
    </>
  );
};
