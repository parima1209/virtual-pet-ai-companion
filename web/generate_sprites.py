"""
generate_sprites.py
สร้างสไปรต์ Pixel Art เบื้องต้นของสัตว์เลี้ยง (placeholder) สำหรับ 4 สถานะ:
idle, happy, hungry, sleepy

วาดบนแคนวาสเล็ก (ไม่ anti-alias) แล้วขยายด้วย NEAREST เพื่อให้ได้ลุค pixel art ที่คมชัด
รัน: python3 generate_sprites.py
"""

from PIL import Image, ImageDraw
import os

OUT_DIR = os.path.join(os.path.dirname(__file__), "static", "sprites")
os.makedirs(OUT_DIR, exist_ok=True)

CANVAS = 40           # px แคนวาสจริงตอนวาด
SCALE = 8              # ขยายกี่เท่า
FINAL = CANVAS * SCALE

BODY = (252, 224, 176, 255)     # ครีมอุ่น
BODY_SHADE = (240, 200, 150, 255)
OUTLINE = (47, 60, 126, 255)    # navy
CHEEK = (249, 97, 103, 255)     # coral
EYE = (35, 43, 77, 255)
WHITE = (255, 255, 255, 255)
EAR = (249, 145, 87, 255)


def base_canvas():
    img = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # ears
    d.ellipse([4, 3, 12, 12], fill=EAR, outline=OUTLINE)
    d.ellipse([28, 3, 36, 12], fill=EAR, outline=OUTLINE)
    # body / head (round blob)
    d.ellipse([5, 8, 35, 34], fill=BODY, outline=OUTLINE)
    # shading (bottom-left crescent)
    d.pieslice([5, 8, 35, 34], start=100, end=190, fill=BODY_SHADE)
    d.ellipse([5, 8, 35, 34], outline=OUTLINE)  # re-stroke outline
    # cheeks
    d.ellipse([7, 22, 13, 27], fill=CHEEK)
    d.ellipse([27, 22, 33, 27], fill=CHEEK)
    return img, d


def save(img, name):
    big = img.resize((FINAL, FINAL), Image.NEAREST)
    big.save(os.path.join(OUT_DIR, name))
    print("wrote", name, big.size)


def make_idle():
    img, d = base_canvas()
    # eyes: open round
    d.ellipse([12, 15, 16, 19], fill=EYE)
    d.ellipse([24, 15, 28, 19], fill=EYE)
    d.ellipse([13, 15, 14, 16], fill=WHITE)
    d.ellipse([25, 15, 26, 16], fill=WHITE)
    # small smile
    d.arc([15, 19, 25, 27], start=20, end=160, fill=OUTLINE, width=1)
    save(img, "pet_idle.png")


def make_happy():
    img, d = base_canvas()
    # closed happy eyes (^ ^)
    d.line([11, 18, 14, 15], fill=EYE, width=2)
    d.line([14, 15, 17, 18], fill=EYE, width=2)
    d.line([23, 18, 26, 15], fill=EYE, width=2)
    d.line([26, 15, 29, 18], fill=EYE, width=2)
    # big open smile
    d.arc([13, 17, 27, 29], start=10, end=170, fill=OUTLINE, width=2)
    # little hearts floating
    for (hx, hy) in [(3, 4), (33, 6)]:
        d.ellipse([hx, hy, hx + 3, hy + 3], fill=CHEEK)
        d.ellipse([hx + 2, hy, hx + 5, hy + 3], fill=CHEEK)
        d.polygon([(hx, hy + 2), (hx + 5, hy + 2), (hx + 2.5, hy + 6)], fill=CHEEK)
    save(img, "pet_happy.png")


def make_hungry():
    img, d = base_canvas()
    # small dot eyes, slightly worried
    d.ellipse([12, 16, 15, 19], fill=EYE)
    d.ellipse([25, 16, 28, 19], fill=EYE)
    # open wanting mouth (oval)
    d.ellipse([17, 21, 23, 27], fill=OUTLINE)
    d.ellipse([18, 22, 22, 25], fill=(120, 40, 50, 255))
    # sweat drop
    d.polygon([(30, 12), (33, 17), (30, 20), (27, 17)], fill=(150, 210, 240, 255), outline=OUTLINE)
    save(img, "pet_hungry.png")


def make_sleepy():
    img, d = base_canvas()
    # flat closed eyes
    d.line([12, 17, 16, 17], fill=EYE, width=2)
    d.line([24, 17, 28, 17], fill=EYE, width=2)
    # small o mouth
    d.ellipse([18, 21, 22, 25], outline=OUTLINE, width=1)
    # Z Z Z
    d.text((30, 2), "z", fill=OUTLINE)
    d.text((34, 6), "Z", fill=OUTLINE)
    save(img, "pet_sleepy.png")


if __name__ == "__main__":
    make_idle()
    make_happy()
    make_hungry()
    make_sleepy()
    print("done")
