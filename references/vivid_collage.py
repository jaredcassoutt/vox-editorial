"""Vibrant paper-collage style, built from the four reference stills.

What the references actually have in common, in the order that matters:

1. A FLAT SATURATED PAPER GROUND (cobalt, marigold, green, cream-with-red-border),
   never a dark ground. This is what reads as "vibrant" more than the objects do.
2. EVERY object is a separate cutout with a THICK WHITE STICKER BORDER and a soft
   real drop shadow - the moon, the emperor, each courtier, each ear of corn, both
   hands. Many small bordered pictures beat one big one.
3. The objects are vintage-print ILLUSTRATIONS with halftone shading, not photos
   and never 3D renders.
4. A TITLE SET INTO TORN WHITE PAPER: bold condensed all-caps sitting in a torn
   paper banner, letters in saturated colour (solid red, or multicolour per letter).
5. Small torn newspaper clippings carrying real printed body text, halftone-dot
   washi tape strips, and scattered flat geometric confetti - triangles, zigzags,
   rings, squares - in the accent palette.
"""

ACCENTS = ("coral red, marigold yellow, cobalt blue, teal green and hot pink")

SUFFIX = (
    "Vibrant editorial paper-collage illustration, VERTICAL 9:16 composition. "
    "Flat saturated {ground} paper background with visible paper grain and torn edges. "
    "EVERY object is a separately hand-cut paper cutout with a THICK WHITE STICKER "
    "BORDER and a soft real paper drop shadow, layered over the background. Objects are "
    "vintage-print, engraved, hand-drawn ILLUSTRATIONS with halftone dot shading. "
    f"Scattered flat geometric paper confetti - triangles, zigzags, small rings and "
    f"squares - in {ACCENTS}. A few halftone-dot washi tape strips and two or three small "
    "torn newspaper clippings with fine printed body text. Generous margins, slight print "
    "misregistration, matte paper texture, bold graphic composition. "
    "NOT photorealistic, NOT CGI, NOT a 3D render, no glossy lighting, no gradients."
)

TITLE = ("A torn white paper banner across the composition carrying the headline "
         "\"{title}\" in bold condensed all-caps display lettering, letters in {tcol}, "
         "the banner taped down at its corners. Spell it exactly, no other words.")

# ground rotates on a 4-colour cycle so the film reads as one system while staying vivid
GROUNDS = ["deep cobalt blue", "marigold yellow", "warm coral red", "aged cream"]

BEATS = {
 1:  dict(title="BUILT BY ONE MAN", tcol="coral red",
          scene="A large illustrated hand holding a phone, cut out with a thick white "
                "border, centred low. The phone screen is a flat cobalt rectangle with a "
                "long ribbon of scrolling paper spilling out of it down the frame. A "
                "halftone moon-like circle upper left."),
 2:  dict(title="2006", tcol="cobalt blue",
          scene="An illustrated boxy 2006 desktop computer and CRT monitor cutout with a "
                "thick white border on a desk, a coffee cup cutout, a paper calendar "
                "clipping reading OCT 2006, a stack of floppy disks. NO PEOPLE anywhere "
                "in the frame, leave the centre-right area open and uncluttered."),
 3:  dict(title="PAGES USED TO END", tcol="coral red",
          scene="Three illustrated web-page rectangles as white paper cards with thick "
                "white borders, stacked receding up the frame, each with a small blue "
                "NEXT button cutout at its bottom edge, and a big illustrated pointing "
                "hand cutout about to click the last one."),
 4:  dict(title="INFINITE SCROLL", tcol="multicolour, one saturated colour per letter",
          scene="A single endless ribbon of white paper unrolling from the top of the "
                "frame to the bottom and off the edge, thick white bordered, with tiny "
                "repeated post rectangles printed down it, and an illustrated hand "
                "cutout swiping upward on it."),
 5:  dict(title="EVERY APP", tcol="cobalt blue",
          scene="A three by three grid of nine illustrated phone cutouts, each with its "
                "own thick white sticker border and drop shadow, each screen a different "
                "saturated flat colour from the accent palette, arranged with generous "
                "gaps."),
 6:  dict(title="A PAGE THAT ENDS ASKS", tcol="coral red",
          scene="A single illustrated white page cutout with a thick white border, "
                "centred, with a large bold question mark printed on it, and a small "
                "illustrated hand cutout resting at the page's bottom edge where it "
                "stops. Lots of open ground around it."),
 7:  dict(title="IT NEVER ASKS", tcol="marigold yellow",
          scene="The same white page cutout but its bottom edge torn away and trailing "
                "off the bottom of the frame in ragged strips, no stopping point, small "
                "torn fragments falling. A tiny illustrated hand cutout far below still "
                "reaching."),
 8:  dict(title="500,000 LIFETIMES", tcol="coral red",
          scene="An enormous printed numeral 500,000 as a bold condensed cutout filling "
                "the upper middle, and beneath it a dense crowd of tiny identical "
                "illustrated human figure cutouts stretching across the full width of "
                "the frame, each figure a small paper cutout."),
 9:  dict(title="HE REGRETS IT", tcol="cobalt blue",
          scene="An empty illustrated picture frame cutout with a thick white sticker "
                "border, centred, waiting to be filled, on an aged cream ground with a "
                "torn newspaper clipping beside it and a halftone circle behind. NO "
                "PEOPLE and no faces anywhere in the frame, keep the centre completely "
                "empty."),
 10: dict(title="PUT IT BACK", tcol="multicolour, one saturated colour per letter",
          scene="An illustrated hand cutout with a thick white border pressing a bold "
                "horizontal bar of paper back onto the bottom edge of a white page "
                "cutout, sealing it shut, small confetti bursting outward around it."),
}


def prompt(bid):
    b = BEATS[bid]
    ground = GROUNDS[(bid - 1) % len(GROUNDS)]
    return (f"{b['scene']} {TITLE.format(title=b['title'], tcol=b['tcol'])} "
            f"{SUFFIX.format(ground=ground)}")


if __name__ == "__main__":
    for i in sorted(BEATS):
        print(f"--- {i} [{GROUNDS[(i-1)%4]}] ---\n{prompt(i)}\n")
