#!/usr/bin/env python3
"""news-image-20261126 — FINAL.

One image summing up the world news of Thursday 26 November 2026.
Pure Python 3 stdlib, no network, fully deterministic: two runs write
identical bytes to /output/entry.png (or $MAKEFUN_OUTPUT_DIR).

Stories (all first reported 25-26 Nov 2026, checked live 26 Nov ~08:05 WIB):
  1. Houthis claim attacks on Saudi refinery (Ras Tanura) and Riyadh;
     Brent crude tops $94 (SimpleLife.news).
  2. Russia's war dead near 500,000 (490,334, leaked data / BBC);
     Moscow approves $600bn+ defence budget 2027-29 (Zot.news, EUR Radio).
  3. US proposes up to 15% tariffs on Taiwan goods (Section 301 probe);
     Taiwan shares fall 1,927 points (SimpleLife.news).
  4. Pakistan's first astronaut, Muhammad Zeeshan Ali, joins China's
     Shenzhou-24 mission to Tiangong station (SelfStudys, LibreNews).
  5. Europe-Japan BepiColombo probe reaches Mercury after an 8-year
     journey (LibreNews).
  6. At least 30 dead in Egypt highway fire after a fuel tanker
     overturns near Cairo (Zot.news).
Also: Colombia marks 10 years since its peace deal; Duran Duran
guitarist Andy Taylor dies aged 65; India marks Constitution Day.
"""
import os
import struct
import zlib

W, H = 1024, 1024

# ---- palette: newsprint ----
PAPER = (247, 242, 231)
INK = (26, 26, 26)
NAVY = (20, 33, 61)
NAVY2 = (30, 48, 88)
RED = (180, 35, 24)
ORANGE = (232, 93, 4)
GOLD = (180, 83, 9)
BLUE = (29, 78, 216)
TEAL = (15, 118, 110)
GREY = (110, 108, 100)
LIGHT = (233, 227, 214)
WHITE = (255, 255, 255)
DARKPANEL = (24, 38, 58)

# ---- 5x7 bitmap font (own hand-written glyphs) ----
FONT = {
    'A': ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    'B': ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
    'C': ["01110", "10001", "10000", "10000", "10000", "10001", "01110"],
    'D': ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
    'E': ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    'F': ["11111", "10000", "10000", "11110", "10000", "10000", "10000"],
    'G': ["01110", "10001", "10000", "10111", "10001", "10001", "01111"],
    'H': ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
    'I': ["01110", "00100", "00100", "00100", "00100", "00100", "01110"],
    'J': ["00111", "00010", "00010", "00010", "00010", "10010", "01100"],
    'K': ["10001", "10010", "10100", "11000", "10100", "10010", "10001"],
    'L': ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    'M': ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
    'N': ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
    'O': ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    'P': ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
    'Q': ["01110", "10001", "10001", "10001", "10101", "10010", "01101"],
    'R': ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    'S': ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    'T': ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    'U': ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
    'V': ["10001", "10001", "10001", "10001", "10001", "01010", "00100"],
    'W': ["10001", "10001", "10001", "10101", "10101", "11011", "10001"],
    'X': ["10001", "10001", "01010", "00100", "01010", "10001", "10001"],
    'Y': ["10001", "10001", "01010", "00100", "00100", "00100", "00100"],
    'Z': ["11111", "00001", "00010", "00100", "01000", "10000", "11111"],
    '0': ["01110", "10001", "10011", "10101", "11001", "10001", "01110"],
    '1': ["00100", "01100", "00100", "00100", "00100", "00100", "01110"],
    '2': ["01110", "10001", "00001", "00110", "01000", "10000", "11111"],
    '3': ["11111", "00010", "00100", "00010", "00001", "10001", "01110"],
    '4': ["00010", "00110", "01010", "10010", "11111", "00010", "00010"],
    '5': ["11111", "10000", "11110", "00001", "00001", "10001", "01110"],
    '6': ["00110", "01000", "10000", "11110", "10001", "10001", "01110"],
    '7': ["11111", "00001", "00010", "00100", "01000", "01000", "01000"],
    '8': ["01110", "10001", "10001", "01110", "10001", "10001", "01110"],
    '9': ["01110", "10001", "10001", "01111", "00001", "00010", "01100"],
    ' ': ["00000", "00000", "00000", "00000", "00000", "00000", "00000"],
    '.': ["00000", "00000", "00000", "00000", "00000", "01100", "01100"],
    ',': ["00000", "00000", "00000", "00000", "01100", "00100", "01000"],
    ':': ["00000", "01100", "01100", "00000", "01100", "01100", "00000"],
    ';': ["00000", "01100", "01100", "00000", "01100", "00100", "01000"],
    "'": ["00100", "00100", "01000", "00000", "00000", "00000", "00000"],
    '-': ["00000", "00000", "00000", "01110", "00000", "00000", "00000"],
    '!': ["00100", "00100", "00100", "00100", "00100", "00000", "00100"],
    '?': ["01110", "10001", "00001", "00110", "00100", "00000", "00100"],
    '/': ["00001", "00010", "00010", "00100", "01000", "01000", "10000"],
    '%': ["11001", "11010", "00010", "00100", "01000", "01011", "10011"],
    '$': ["00100", "01111", "10100", "01110", "00101", "11110", "00100"],
    '&': ["01100", "10010", "10100", "01000", "10101", "10010", "01101"],
    '(': ["00010", "00100", "01000", "01000", "01000", "00100", "00010"],
    ')': ["01000", "00100", "00010", "00010", "00010", "00100", "01000"],
    '+': ["00000", "00100", "00100", "11111", "00100", "00100", "00000"],
    '=': ["00000", "00000", "11111", "00000", "11111", "00000", "00000"],
    '>': ["10000", "01000", "00100", "00010", "00100", "01000", "10000"],
    '<': ["00001", "00010", "00100", "01000", "00100", "00010", "00001"],
    '*': ["00000", "10101", "01110", "11111", "01110", "10101", "00000"],
}


class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def rect(self, x, y, w, h, c):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, c)

    def hline(self, x, y, w, c, t=1):
        self.rect(x, y, w, t, c)

    def vline(self, x, y, h, c, t=1):
        self.rect(x, y, t, h, c)

    def border(self, x, y, w, h, c, t=2):
        self.hline(x, y, w, c, t)
        self.hline(x, y + h - t, w, c, t)
        self.vline(x, y, h, c, t)
        self.vline(x + w - t, y, h, c, t)

    def line(self, x0, y0, x1, y1, c, t=1):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            for a in range(t):
                for b in range(t):
                    self.set(x0 + a, y0 + b, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.set(xx, yy, c)

    def ring(self, cx, cy, r, c, t=3):
        for yy in range(cy - r - t, cy + r + t + 1):
            for xx in range(cx - r - t, cx + r + t + 1):
                d = ((xx - cx) ** 2 + (yy - cy) ** 2) ** 0.5
                if r - t <= d <= r:
                    self.set(xx, yy, c)

    def triangle(self, x0, y0, x1, y1, x2, y2, c):
        # filled triangle via scanline
        pts = sorted([(x0, y0), (x1, y1), (x2, y2)], key=lambda p: p[1])
        (ax, ay), (bx, by), (cx, cy) = pts
        def edge(xa, ya, xb, yb, y):
            if yb == ya:
                return xa
            return xa + (xb - xa) * (y - ya) / (yb - ya)
        for y in range(ay, cy + 1):
            if y < by:
                xa = edge(ax, ay, bx, by, y)
                xb = edge(ax, ay, cx, cy, y)
            else:
                xa = edge(bx, by, cx, cy, y)
                xb = edge(ax, ay, cx, cy, y)
            for x in range(int(min(xa, xb)), int(max(xa, xb)) + 1):
                self.set(x, y, c)

    def text(self, x, y, s, scale, c):
        s = s.upper()
        cx = x
        for ch in s:
            g = FONT.get(ch, FONT[' '])
            for r, row in enumerate(g):
                for col, bit in enumerate(row):
                    if bit == '1':
                        self.rect(cx + col * scale, y + r * scale, scale, scale, c)
            cx += 6 * scale
        return cx

    def text_w(self, s, scale):
        return len(s) * 6 * scale - scale

    def text_center(self, cx, y, s, scale, c):
        self.text(cx - self.text_w(s, scale) // 2, y, s, scale, c)

    def wrap(self, s, scale, maxw):
        words = s.split(' ')
        lines, cur = [], ''
        for wd in words:
            trial = (cur + ' ' + wd).strip()
            if self.text_w(trial, scale) <= maxw:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = wd
        if cur:
            lines.append(cur)
        return lines

    def para(self, x, y, s, scale, c, maxw, lh=None):
        lh = lh or int(9 * scale)
        for ln in self.wrap(s, scale, maxw):
            self.text(x, y, ln, scale, c)
            y += lh
        return y


# ---- small drawn icons ----
def draw_flame(cv, cx, base_y, h, c1, c2):
    # simple flame: stacked triangles + circle
    cv.triangle(cx - h // 3, base_y, cx + h // 3, base_y, cx, base_y - h, c1)
    cv.circle(cx, base_y - h // 3, h // 4, c2)
    cv.triangle(cx - h // 6, base_y, cx + h // 6, base_y, cx, base_y - h // 2, c2)


def draw_refinery(cv, x, y, w, h):
    # dark panel with towers, pipes and flame
    cv.rect(x, y, w, h, DARKPANEL)
    # ground
    cv.rect(x, y + h - 26, w, 26, (16, 26, 40))
    # towers
    for i, (tx, tw, th) in enumerate([(x + 18, 26, h - 90), (x + 62, 20, h - 70),
                                     (x + 100, 30, h - 110), (x + 150, 18, h - 80)]):
        cv.rect(tx, y + h - 26 - th, tw, th, (70, 90, 120))
        cv.rect(tx - 4, y + h - 26 - th - 10, tw + 8, 10, (70, 90, 120))
        # blinking lights (static)
        cv.rect(tx + tw // 2 - 2, y + h - 26 - th - 16, 4, 4, RED)
    # horizontal pipe
    cv.rect(x + 10, y + h - 60, w - 20, 8, (90, 110, 140))
    # flame on top of tallest tower
    draw_flame(cv, x + 115, y + h - 26 - (h - 110) - 12, 56, ORANGE, GOLD)
    # big "$94" oil barrel
    cv.rect(x + w - 78, y + h - 84, 56, 58, (120, 60, 20))
    cv.rect(x + w - 78, y + h - 84, 56, 8, (150, 80, 30))
    cv.text(x + w - 66, y + h - 66, "$94", 2, WHITE)


def draw_star(cv, cx, cy, r, c):
    pts = []
    import math
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + int(rr * math.cos(ang)), cy + int(rr * math.sin(ang))))
    for i in range(10):
        x0, y0 = pts[i]
        x1, y1 = pts[(i + 1) % 10]
        cv.line(cx, cy, x0, y0, c)
    # fill by triangles from center
    for i in range(10):
        x0, y0 = pts[i]
        x1, y1 = pts[(i + 1) % 10]
        cv.triangle(cx, cy, x0, y0, x1, y1, c)


def draw_chart_down(cv, x, y, w, h):
    cv.rect(x, y, w, h, LIGHT)
    # bars falling
    bars = [0.85, 0.78, 0.82, 0.66, 0.55, 0.42]
    bw = w // 7
    for i, f in enumerate(bars):
        bh = int(h * f * 0.8)
        cv.rect(x + 8 + i * bw, y + h - 10 - bh, bw - 6, bh, BLUE if i < 4 else RED)
    # red arrow down-right
    cv.line(x + 10, y + 14, x + w - 12, y + h - 22, RED, 4)


def draw_rocket(cv, cx, cy, s):
    # body
    cv.rect(cx - 12 * s // 2, cy - 30 * s, 12 * s, 46 * s, WHITE)
    cv.border(cx - 12 * s // 2, cy - 30 * s, 12 * s, 46 * s, INK, 2)
    # nose cone
    cv.triangle(cx - 12 * s // 2, cy - 30 * s, cx + 12 * s // 2, cy - 30 * s,
                cx, cy - 46 * s, RED)
    # window
    cv.circle(cx, cy - 14 * s, 4 * s, BLUE)
    # fins
    cv.triangle(cx - 12 * s // 2, cy + 8 * s, cx - 22 * s // 2, cy + 20 * s,
                cx - 12 * s // 2, cy + 16 * s, RED)
    cv.triangle(cx + 12 * s // 2, cy + 8 * s, cx + 22 * s // 2, cy + 20 * s,
                cx + 12 * s // 2, cy + 16 * s, RED)
    # flame
    draw_flame(cv, cx, cy + 20 * s + 6, 18 * s, ORANGE, GOLD)


def draw_planet(cv, cx, cy, r):
    cv.circle(cx, cy, r, (176, 141, 87))
    cv.circle(cx - r // 3, cy - r // 4, r // 5, (140, 108, 66))
    cv.circle(cx + r // 4, cy + r // 5, r // 6, (140, 108, 66))
    cv.circle(cx + r // 6, cy - r // 2, r // 8, (140, 108, 66))
    cv.ring(cx, cy, r + 10, TEAL, 3)


def compose():
    cv = Canvas(W, H, PAPER)
    M = 28  # margin
    # ---- masthead ----
    cv.rect(M, M, W - 2 * M, 118, NAVY)
    cv.rect(M, M, W - 2 * M, 6, GOLD)
    cv.text_center(W // 2, M + 18, "THE WORLD TODAY", 6, WHITE)
    cv.text_center(W // 2, M + 74, "THURSDAY 26 NOVEMBER 2026", 3, (232, 180, 90))
    cv.hline(M, M + 128, W - 2 * M, INK, 3)

    # ---- lead story ----
    ly = 168
    lh = 300
    cv.border(M, ly, W - 2 * M, lh, INK, 3)
    # illustration left
    ix, iy, iw, ih = M + 12, ly + 12, 330, lh - 24
    draw_refinery(cv, ix, iy, iw, ih)
    # text right
    tx = ix + iw + 22
    tw = W - M - 12 - tx
    cv.text(tx, ly + 18, "MIDDLE EAST  -  OIL", 2, RED)
    y = ly + 46
    for ln in cv.wrap("OIL SPIKES AS HOUTHIS CLAIM SAUDI REFINERY STRIKE", 4, tw):
        cv.text(tx, y, ln, 4, INK)
        y += 36
    y += 6
    y = cv.para(tx, y, "Brent crude tops $94 a barrel after Yemen's Houthi forces claim attacks on the Ras Tanura refinery and Riyadh, raising fears of disruption to Middle East energy supplies.", 2, (60, 58, 52), tw)
    y += 8
    cv.text(tx, y, "BRENT $94.61  +3.5%  -  WTI $83.53", 2, TEAL)

    # ---- middle row: two stories ----
    my = ly + lh + 16
    mh = 210
    half = (W - 2 * M - 16) // 2
    # left: Russia
    cv.border(M, my, half, mh, INK, 2)
    cv.text(M + 16, my + 14, "UKRAINE WAR", 2, RED)
    draw_star(cv, M + half - 44, my + 30, 18, RED)
    y = my + 40
    for ln in cv.wrap("RUSSIA'S WAR DEAD NEAR 500,000", 3, half - 32):
        cv.text(M + 16, y, ln, 3, INK)
        y += 26
    y = cv.para(M + 16, y + 4, "Leaked data put Russian military deaths at 490,334. Moscow approves a defence budget of more than $600bn for 2027-29.", 2, (60, 58, 52), half - 32)
    # right: tariffs
    rx = M + half + 16
    cv.border(rx, my, half, mh, INK, 2)
    cv.text(rx + 16, my + 14, "TRADE", 2, RED)
    y = my + 40
    for ln in cv.wrap("US PLANS 15% TARIFFS ON TAIWAN", 3, half - 150):
        cv.text(rx + 16, y, ln, 3, INK)
        y += 26
    draw_chart_down(cv, rx + half - 132, my + 40, 116, 84)
    y = cv.para(rx + 16, y + 4, "Washington proposes levies of up to 15% on Taiwanese goods in an overcapacity probe. Taiwan shares fall 1,927 points.", 2, (60, 58, 52), half - 150)

    # ---- bottom row: three stories ----
    by = my + mh + 16
    bh = 196
    third = (W - 2 * M - 32) // 3
    # 1. astronaut
    x0 = M
    cv.border(x0, by, third, bh, INK, 2)
    cv.text(x0 + 14, by + 12, "SPACE", 2, RED)
    draw_rocket(cv, x0 + third // 2, by + 104, 1)
    y = by + 150
    cv.text(x0 + 14, by + 132, "PAKISTAN'S FIRST", 2, INK)
    cv.text(x0 + 14, by + 150, "ASTRONAUT", 2, INK)
    cv.text(x0 + 14, by + 170, "FLIES WITH CHINA", 2, (60, 58, 52))
    # 2. Mercury
    x1 = M + third + 16
    cv.border(x1, by, third, bh, INK, 2)
    cv.text(x1 + 14, by + 12, "SPACE", 2, RED)
    draw_planet(cv, x1 + third // 2, by + 76, 40)
    cv.text(x1 + 14, by + 132, "EUROPE-JAPAN PROBE", 2, INK)
    cv.text(x1 + 14, by + 150, "REACHES MERCURY", 2, INK)
    cv.text(x1 + 14, by + 170, "AFTER 8-YEAR TRIP", 2, (60, 58, 52))
    # 3. Egypt fire
    x2 = M + 2 * (third + 16)
    cv.border(x2, by, third, bh, INK, 2)
    cv.text(x2 + 14, by + 12, "EGYPT", 2, RED)
    draw_flame(cv, x2 + third // 2, by + 118, 64, ORANGE, RED)
    cv.text(x2 + 14, by + 132, "30 DEAD IN EGYPT", 2, INK)
    cv.text(x2 + 14, by + 150, "HIGHWAY FIRE", 2, INK)
    cv.text(x2 + 14, by + 170, "FUEL TANKER BURNS", 2, (60, 58, 52))

    # ---- footer strip ----
    fy = by + bh + 16
    cv.rect(M, fy, W - 2 * M, 44, NAVY)
    cv.text_center(W // 2, fy + 13, "ALSO: COLOMBIA MARKS 10 YEARS OF PEACE  -  ANDY TAYLOR DIES AT 65", 2, WHITE)
    cv.text_center(W // 2, fy + 52, "THE DAY IN WORLD NEWS  -  26 NOVEMBER 2026", 2, GREY)
    return cv


def png_bytes(cv):
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)
        raw.extend(cv.px[y * cv.w * 3:(y + 1) * cv.w * 3])

    def chunk(typ, data):
        c = struct.pack(">I", len(data)) + typ + data
        return c + struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + chunk(b"IEND", b""))


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    data = png_bytes(compose())
    with open(os.path.join(outdir, "entry.png"), "wb") as f:
        f.write(data)


if __name__ == "__main__":
    main()
