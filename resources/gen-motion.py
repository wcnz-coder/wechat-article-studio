#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""中式动效 GIF 生成器

九个效果：桂花飘落 / 墨点晕开 / 水波纹 / 雁阵 / 灯笼 / 雾 / 竹影 / 星火 / 逐字落款

关键点：**所有 GIF 的背景都从同一张长图的空白纸区裁**，
这样插进推文后才不会出现"一张图在动"的黑块/白块。

用法：
    python gen-motion.py --paper page.png --crop 80,330,680,730 -o out/motion
    python gen-motion.py --paper page.png --crop 80,330,680,730 --only 桂花 灯笼
"""
from __future__ import annotations

import argparse
import math
import os
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

F_THRESHOLD = 3  # 量化色数下限控制

DEFAULT_PAPER = (243, 237, 225)


# ---------------------------------------------------------------- 基础


def load_font(size: int, name: str = "simsun.ttc"):
    roots = [
        "C:/Windows/Fonts",
        "/System/Library/Fonts/Supplemental",
        "/System/Library/Fonts",
        "/usr/share/fonts/opentype/noto",
        "/usr/share/fonts/truetype/noto",
        str(Path.home() / ".fonts"),
    ]
    for n in (name, "Songti.ttc", "NotoSerifCJK-Regular.ttc", "msyh.ttc", "PingFang.ttc"):
        for d in roots:
            p = Path(d) / n
            if p.exists():
                try:
                    return ImageFont.truetype(str(p), size)
                except OSError:
                    continue
    return ImageFont.load_default()


class Paper:
    """纸底来源：优先用长图里裁出的真实纸面，兜底用纯色。"""

    def __init__(self, source: Path | None, crop: tuple[int, int, int, int] | None):
        if source and source.exists():
            img = Image.open(source).convert("RGB")
            box = crop or (0, 0, min(600, img.width), min(400, img.height))
            self.patch = img.crop(box).resize((1200, 400), Image.LANCZOS)
        else:
            self.patch = Image.new("RGB", (1200, 400), DEFAULT_PAPER)

    def at(self, w: int, h: int) -> Image.Image:
        return self.patch.resize((w, h), Image.LANCZOS).copy()


def save_gif(path: Path, frames: list[Image.Image], duration: int = 110) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=duration, loop=0, optimize=True)


# ---------------------------------------------------------------- 效果


def petals(P: Paper, w=1200, h=320, n=26, frames=24) -> list[Image.Image]:
    rnd = random.Random(5)
    ps = [(rnd.randint(0, w), rnd.uniform(0, 1), rnd.uniform(0.5, 1.4), rnd.uniform(0, 6.28), rnd.choice([3, 4, 5])) for _ in range(n)]
    out = []
    for fi in range(frames):
        t = fi / frames
        img = P.at(w, h)
        d = ImageDraw.Draw(img)
        for (x, ph, sp, phase, r) in ps:
            y = ((t * sp + ph) % 1.15) * (h + 60) - 30
            drift = 18 * math.sin(2 * math.pi * (t * 0.8 + phase))
            d.ellipse([x + drift - r, y - r * 0.7, x + drift + r, y + r * 0.7], fill=(198, 168, 96))
            d.ellipse([x + drift - r * 0.4, y - r * 0.4, x + drift + r * 0.4, y + r * 0.4], fill=(214, 188, 122))
        out.append(img.quantize(colors=96, dither=Image.Dither.FLOYDSTEINBERG))
    return out


def ink(P: Paper, w=1200, h=320, frames=24) -> list[Image.Image]:
    out, cx, cy = [], w // 2, h // 2
    for fi in range(frames):
        t = fi / frames
        img = P.at(w, h)
        r = 12 + 120 * (t ** 0.7)
        a = int(150 * (1 - t) ** 1.5)
        if a > 0:
            layer = Image.new("L", (w, h), 0)
            ImageDraw.Draw(layer).ellipse([cx - r, cy - r * 0.55, cx + r, cy + r * 0.55], fill=a)
            layer = layer.filter(ImageFilter.GaussianBlur(8 + 18 * t))
            img = Image.composite(Image.new("RGB", (w, h), (45, 43, 40)), img, layer)
            ImageDraw.Draw(img).ellipse([cx - 5, cy - 4, cx + 5, cy + 4], fill=(30, 28, 26))
        out.append(img.quantize(colors=96, dither=Image.Dither.FLOYDSTEINBERG))
    return out


def ripple(P: Paper, w=1200, h=300, frames=24) -> list[Image.Image]:
    out, cy = [], h // 2
    for fi in range(frames):
        t = fi / frames
        img = P.at(w, h)
        d = ImageDraw.Draw(img)
        for k in range(7):
            y = cy - 60 + k * 20
            phase = t * 2 * math.pi + k * 0.7
            pts = [(x, y + 5 * math.sin(phase + x / 90)) for x in range(0, w, 6)]
            d.line(pts, fill=(150, 142, 128))
        out.append(img.quantize(colors=96, dither=Image.Dither.FLOYDSTEINBERG))
    return out


def geese(P: Paper, w=1200, h=260, frames=26) -> list[Image.Image]:
    out = []
    for fi in range(frames):
        t = fi / frames
        img = P.at(w, h)
        d = ImageDraw.Draw(img)
        bx, by = -160 + t * (w + 320), 90
        for i in range(5):
            x, y = bx + i * 44, by + abs(i - 2) * 22
            d.arc([x - 9, y - 4, x + 9, y + 6], 200, 340, fill=(45, 43, 40), width=2)
        for i in range(4):
            x, y = bx - 60 + i * 44, by + 60 + abs(i - 1.5) * 18
            d.arc([x - 7, y - 3, x + 7, y + 5], 200, 340, fill=(96, 90, 82), width=1)
        out.append(img.quantize(colors=96, dither=Image.Dither.FLOYDSTEINBERG))
    return out


def lanterns(P: Paper, w=1200, h=340, frames=22) -> list[Image.Image]:
    out, xs = [], [300, 620, 900]
    for fi in range(frames):
        t = fi / frames
        img = P.at(w, h)
        d = ImageDraw.Draw(img)
        for i, x in enumerate(xs):
            sw = 7 * math.sin(2 * math.pi * (t + i * 0.25))
            y = 70 + i * 26
            cx = x + sw
            d.line([(x, 0), (cx, y - 10)], fill=(140, 132, 118))
            d.rectangle([cx - 10, y - 12, cx + 10, y - 4], fill=(132, 84, 56))
            d.ellipse([cx - 30, y - 4, cx + 30, y + 52], fill=(186, 74, 52))
            for k in (-14, 0, 14):
                d.arc([cx + k - 10, y - 4, cx + k + 10, y + 52], 260, 280, fill=(150, 52, 36))
            d.rectangle([cx - 22, y - 4, cx + 22, y + 2], fill=(150, 52, 36))
            d.rectangle([cx - 22, y + 46, cx + 22, y + 52], fill=(150, 52, 36))
            d.line([(cx, y + 52), (cx, y + 74)], fill=(132, 84, 56), width=2)
            d.line([(cx - 4, y + 74), (cx + 4, y + 74)], fill=(132, 84, 56))
        out.append(img.quantize(colors=96, dither=Image.Dither.FLOYDSTEINBERG))
    return out


def mist(P: Paper, w=1200, h=260, frames=22) -> list[Image.Image]:
    out = []
    for fi in range(frames):
        t = fi / frames
        img = P.at(w, h)
        layer = Image.new("L", (w, h), 0)
        d = ImageDraw.Draw(layer)
        for k in range(4):
            x = ((t + k / 4) % 1.0) * (w + 400) - 200
            d.ellipse([x - 200, h * 0.35, x + 200, h * 0.75], fill=70)
        layer = layer.filter(ImageFilter.GaussianBlur(40))
        img = Image.composite(Image.new("RGB", (w, h), (252, 249, 242)), img, layer)
        out.append(img.quantize(colors=96, dither=Image.Dither.FLOYDSTEINBERG))
    return out


def bamboo(P: Paper, w=1200, h=300, frames=20) -> list[Image.Image]:
    out = []
    for fi in range(frames):
        t = fi / frames
        img = P.at(w, h)
        d = ImageDraw.Draw(img)
        for s in range(3):
            base_x = 260 + s * 330
            sway = 10 * math.sin(2 * math.pi * (t + s * 0.3))
            for k in range(5):
                x, y = base_x + sway * (k / 4) + k * 3, 40 + k * 30
                d.line([(x, y), (x + 2, y + 28)], fill=(120, 112, 96))
                d.line([(x, y), (x - 26, y - 8)], fill=(96, 90, 78))
                d.line([(x, y), (x + 24, y - 10)], fill=(96, 90, 78))
        out.append(img.quantize(colors=96, dither=Image.Dither.FLOYDSTEINBERG))
    return out


def fireflies(P: Paper, w=1200, h=260, frames=22) -> list[Image.Image]:
    rnd = random.Random(9)
    ps = [(rnd.randint(0, w), rnd.randint(20, h - 20), rnd.uniform(0, 6.28), rnd.uniform(0.5, 1.2)) for _ in range(34)]
    out = []
    for fi in range(frames):
        t = fi / frames
        img = P.at(w, h)
        d = ImageDraw.Draw(img)
        for (x, y, ph, sp) in ps:
            a = 0.25 + 0.75 * (0.5 + 0.5 * math.sin(2 * math.pi * (t * sp + ph)))
            r = 2 + 2 * a
            yy = y + 6 * math.sin(2 * math.pi * (t + ph))
            d.ellipse([x - r, yy - r, x + r, yy + r], fill=(200, 176, 96))
        out.append(img.quantize(colors=96, dither=Image.Dither.FLOYDSTEINBERG))
    return out


def typing(P: Paper, text: str = "中秋快乐", w=900, h=300, frames=26) -> list[Image.Image]:
    f = load_font(64)
    out = []
    for fi in range(frames):
        t = fi / frames
        shown = int(len(text) * min(1, t * 1.25))
        img = P.at(w, h)
        d = ImageDraw.Draw(img)
        x = 120
        for i, ch in enumerate(text):
            if i < shown:
                d.text((x, 100), ch, font=f, fill=(30, 28, 26))
            x += 92
        if shown >= len(text):
            s = 74
            d.rectangle([x + 20, 104, x + 20 + s, 104 + s], fill=(166, 59, 42))
            f2 = load_font(34)
            tw = d.textlength("印", font=f2)
            d.text((x + 20 + (s - tw) / 2, 104 + 16), "印", font=f2, fill=(243, 237, 225))
        out.append(img.quantize(colors=96, dither=Image.Dither.FLOYDSTEINBERG))
    return out


EFFECTS = {
    "桂花": lambda P: petals(P),
    "墨点": lambda P: ink(P),
    "水波": lambda P: ripple(P),
    "雁阵": lambda P: geese(P),
    "灯笼": lambda P: lanterns(P),
    "雾": lambda P: mist(P),
    "竹影": lambda P: bamboo(P),
    "星火": lambda P: fireflies(P),
    "落款": lambda P: typing(P),
}


def main() -> None:
    ap = argparse.ArgumentParser(description="生成中式动效 GIF")
    ap.add_argument("--paper", default=None, help="整页长图路径（建议传入，保证底色一致）")
    ap.add_argument("--crop", default=None, help="长图里的空白纸区 x1,y1,x2,y2")
    ap.add_argument("-o", "--out", default="out/motion")
    ap.add_argument("--only", nargs="*", default=None, help="只生成指定效果，如 --only 灯笼 竹影")
    args = ap.parse_args()

    crop = tuple(int(v) for v in args.crop.split(",")) if args.crop else None
    P = Paper(Path(args.paper) if args.paper else None, crop)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    todo = {k: v for k, v in EFFECTS.items() if not args.only or k in args.only}
    for i, (name, fn) in enumerate(todo.items(), 1):
        frames = fn(P)
        save_gif(out / f"{i:02d}-{name}.gif", frames)
        print(f"{i:02d}-{name}.gif  {len(frames)} frames")

    print(f"done -> {out.resolve()}")


if __name__ == "__main__":
    main()
