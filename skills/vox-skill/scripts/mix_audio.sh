#!/usr/bin/env bash
# Master the narration and duck a music bed under it.
#   mix_audio.sh <vo.mp3> <bed.wav> <out.wav> [music_db]
#
# Raw TTS is dry, thin and unmastered. The chain below is most of the distance
# between "text to speech" and "documentary narration", and it matters more than
# which voice model you picked.
#
#   highpass 85      kill rumble and plosive energy the voice never uses
#   -2 dB @ 350 Hz   take out the boxiness every neural TTS has
#   +2.5 dB @ 3 kHz  presence, which is what makes consonants land
#   -3 dB @ 6.8 kHz  de-ess; TTS sibilance is harsher than a real mouth
#   acompressor      3:1 so quiet clauses sit at the same level as loud ones
#   loudnorm -16     broadcast-ish target, sensible on phones and laptops
#
# The sidechain key is apad-ed so the duck runs the bed's full length; without
# that the mix truncates to the (shorter) narration.
#
# The bed should be cut to the SEQUENCE length, not the voice length, so it
# carries the closing hold. The music is set to `music_db` under the voice (default -20, per the
# documentary convention of -18 to -22) and then sidechain-ducked a further
# ~6 dB whenever the voice is actually speaking, so it swells back up in the
# gaps between lines rather than sitting at one flat level.
set -euo pipefail

VO="${1:?usage: mix_audio.sh <vo> <bed> <out> [music_db]}"
BED="${2:?usage: mix_audio.sh <vo> <bed> <out> [music_db]}"
OUT="${3:?usage: mix_audio.sh <vo> <bed> <out> [music_db]}"
MUSIC_DB="${4:--20}"

ffmpeg -y -v error \
  -i "$VO" -i "$BED" \
  -filter_complex "
    [0:a]highpass=f=85,
         equalizer=f=350:t=q:w=1.2:g=-2,
         equalizer=f=3000:t=q:w=1.0:g=2.5,
         equalizer=f=6800:t=q:w=2.0:g=-3,
         acompressor=threshold=0.1:ratio=3:attack=5:release=120,
         loudnorm=I=-16:TP=-1.5:LRA=11,
         aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo,
         asplit=2[voice][keyraw];
    [keyraw]apad[key];
    [1:a]aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo,
         volume=${MUSIC_DB}dB[bed];
    [bed][key]sidechaincompress=threshold=0.03:ratio=8:attack=18:release=420:makeup=1[ducked];
    [voice][ducked]amix=inputs=2:duration=longest:dropout_transition=0:normalize=0,
         alimiter=limit=0.94
  " \
  -ar 48000 -ac 2 "$OUT"

echo "  wrote $OUT"
ffmpeg -hide_banner -i "$OUT" -af ebur128=framelog=quiet -f null /dev/null 2>&1 \
  | grep -A4 "Integrated" | sed 's/^/  /'
