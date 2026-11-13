"""Deterministic, original pixel textures for the island scene. Requires Pillow."""
from pathlib import Path
from PIL import Image, ImageDraw
import random
import math

OUT = Path(__file__).resolve().parents[1] / "assets" / "island"
OUT.mkdir(parents=True, exist_ok=True)
rng = random.Random(731)


def surface(name, palette, size=64):
    image = Image.new("RGB", (size, size), palette[2])
    draw = ImageDraw.Draw(image)
    for _ in range(950):
        x, y = rng.randrange(size), rng.randrange(size)
        w, h = rng.choice((1, 2, 3, 5, 8)), rng.choice((1, 1, 2, 3))
        draw.rectangle((x, y, x + w, y + h), fill=rng.choice(palette))
    if name == "granite":
        for _ in range(20):
            x, y = rng.randrange(size), rng.randrange(size)
            points = [(x, y)]
            for step in range(rng.randint(3, 8)):
                x += rng.randint(-3, 4)
                y += rng.randint(2, 6)
                points.append((x, y))
            draw.line(points, fill=palette[0], width=1)
            draw.line([(a+1, b) for a, b in points], fill=palette[-1], width=1)
    if name == "wood":
        for y in range(0, size, 5):
            x = rng.randrange(15)
            draw.line((x, y, size, y+rng.choice((-1, 0, 1))), fill=palette[0])
    image.save(OUT / f"{name}.png")


surface("grass", ["#355c39", "#416a3b", "#507a40", "#5e8645", "#6b914c", "#81a05c"])
surface("granite", ["#696f6a", "#83877f", "#959a8d", "#a7aa98", "#b7b9a3", "#c8c7b0"])
surface("path", ["#8d9172", "#a7a383", "#b6b18d", "#c6c09d", "#d6cda8", "#e5d9b3"])
surface("wood", ["#554937", "#756040", "#8d734b", "#a18a5e", "#b6a174", "#caba8c"])

# Dense, asymmetric needle boughs. Transparent gaps survive nearest filtering.
im = Image.new("RGBA", (128, 72))
d = ImageDraw.Draw(im)
for _ in range(155):
    x = rng.gauss(64, 24)
    y = rng.gauss(36, 11)
    if ((x-64)/61)**2 + ((y-36)/31)**2 > 1:
        continue
    radius = rng.randint(3, 10)
    col = rng.choice(["#123d31", "#1e5137", "#2e663c", "#407840", "#578a48", "#719d54"])
    d.polygon([(int(x-radius), int(y)), (int(x-radius//2), int(y-radius//2)),
               (int(x+radius//2), int(y-radius//2-2)), (int(x+radius), int(y)),
               (int(x+radius//2), int(y+radius//3)), (int(x-radius//2), int(y+radius//3))], fill=col)
    for k in range(7):
        dx, dy = rng.randint(-radius, radius), rng.randint(-radius//2, radius//2)
        d.line((int(x), int(y), int(x+dx), int(y+dy-4)), fill=col, width=rng.choice((1, 1, 2)))
    d.rectangle((int(x)-2, int(y)-1, int(x)+3, int(y)+1), fill=col)
im.save(OUT / "pine_bough.png")

im = Image.new("RGBA", (48, 64))
d = ImageDraw.Draw(im)
for j in range(18):
    bx, by = rng.randint(17, 31), 63
    tx, ty = bx + rng.randint(-18, 18), rng.randint(12, 49)
    col = rng.choice(["#305f38", "#467d3d", "#6c9c45", "#96b95e", "#b2ca7b"])
    d.line((bx, by, (bx+tx)//2, ty+12, tx, ty), fill=col, width=1)
    if j % 4 == 0:
        d.line((tx, ty+5, tx+2, ty-4), fill="#d9ce8c", width=1)
im.save(OUT / "grass_tuft.png")

im = Image.new("RGBA", (96, 80))
d = ImageDraw.Draw(im)
for k in range(9):
    angle = -math.pi + k * math.pi / 8
    length = rng.randint(32, 52)
    end = (48 + math.cos(angle)*length, 72 + math.sin(angle)*length-10)
    d.line((48, 76, *end), fill="#b1bc61", width=1)
    for t in range(2, 11):
        f = t/12
        x, y = 48+(end[0]-48)*f, 76+(end[1]-76)*f
        leaf = 8*(1-f)+2
        col = rng.choice(["#246442", "#39854a", "#5ba456", "#80ba64"])
        d.line((x-leaf, y-5, x, y, x+leaf, y-4), fill=col, width=2)
im.save(OUT / "fern.png")

im = Image.new("RGBA", (96, 64))
d = ImageDraw.Draw(im)
for k in range(7):
    x, y = rng.randint(15, 85), rng.randint(10, 42)
    d.line((48, 61, x, y), fill="#577c42", width=1)
    for j in range(5):
        lx, ly = x+rng.randint(-18, 18), y+rng.randint(-9, 9)
        d.polygon([(x, y), (lx-2, ly), (lx, ly-12), (lx+2, ly)], fill=rng.choice(["#245c3f", "#3d7e48", "#63a25b", "#88ba68"]))
im.save(OUT / "bamboo_leaves.png")
print(f"Generated eight island textures in {OUT}")
