"""Give a transparent cutout the collage 'sticker' treatment:
a thick white border that follows the silhouette + a soft drop shadow.

Note: the Vision cutout is cropped tight to the subject, so the alpha MUST be padded
onto a larger canvas before dilating or the border is clipped away at the edges.
"""
from PIL import Image, ImageFilter
import sys

def sticker(src, dst, border=52, shadow=True, max_side=1400):
    im = Image.open(src).convert("RGBA")
    im.thumbnail((max_side, max_side), Image.LANCZOS)
    pad = int(border * 2.2)
    W, H = im.width + pad * 2, im.height + pad * 2

    a = im.split()[3].point(lambda v: 255 if v > 40 else 0).filter(ImageFilter.MedianFilter(5))
    canvas_a = Image.new("L", (W, H), 0)
    canvas_a.paste(a, (pad, pad))                      # pad FIRST, then grow
    grow = canvas_a.filter(ImageFilter.GaussianBlur(border * 0.60)).point(lambda v: 255 if v > 26 else 0)
    grow = grow.filter(ImageFilter.GaussianBlur(1.5)).point(lambda v: 255 if v > 120 else 0)

    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if shadow:
        sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        sh.paste(Image.new("RGBA", (W, H), (20, 18, 16, 150)), (0, 14), grow)
        out.alpha_composite(sh.filter(ImageFilter.GaussianBlur(18)))
    out.paste(Image.new("RGBA", (W, H), (255, 255, 255, 255)), (0, 0), grow)
    body = Image.new("RGBA", im.size, (0, 0, 0, 0)); body.paste(im, (0, 0), a)
    out.alpha_composite(body, (pad, pad))
    bbox = out.split()[3].getbbox()
    if bbox: out = out.crop(bbox)
    out.save(dst)
    return out.size

if __name__ == "__main__":
    print(sticker(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 52))
