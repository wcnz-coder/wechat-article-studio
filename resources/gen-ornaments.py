#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""中式纹样 / 印章 / 边框 / 底纹 生成器

纯程序生成，输出可商用（CC0）。无外部素材依赖，只需要 Pillow。

用法：
    python gen-ornaments.py                 # 默认输出到 ./out
    python gen-ornaments.py -o assets       # 指定输出目录
    python gen-ornaments.py --palette ink    # 换配色（gold / ink / red）

字体：自动在 Windows / macOS / Linux 常见路径里找宋体，找不到就退回默认字体。
"""
from __future__ import annotations

import argparse
import os
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

# ---------------------------------------------------------------- 字体

FONT_DIRS = [
    "C:/Windows/Fonts",
    "/System/Library/Fonts/Supplemental",
    "/System/Library/Fonts",
    "/usr/share/fonts/opentype/noto",
    "/usr/share/fonts/truetype/noto",
    str(Path.home() / ".fonts"),
    str(Path.home() / "Library/Fonts"),
]

SERIF_CANDIDATES = ["simsun.ttc", "Songti.ttc", "STSong.ttf", "NotoSerifCJK-Regular.ttc", "NotoSerifCJKsc-Regular.otf"]
SANS_CANDIDATES = ["msyh.ttc", "PingFang.ttc", "STHeiti Light.ttc", "NotoSansCJK-Regular.ttc", "simhei.ttf"]


def find_font(candidates: list[str]) -> str | None:
    for name in candidates:
        for d in FONT_DIRS:
            p = Path(d) / name
            if p.exists():
                return str(p)
    return None


def load_font(size: int, kind: str = "serif") -> ImageFont.FreeTypeFont:
    path = find_font(SERIF_CANDIDATES if kind == "serif" else SANS_CANDIDATES)
    if path:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            pass
    return ImageFont.load_default()


# ---------------------------------------------------------------- 配色

PALETTES = {
    "gold": {"line": (201, 169, 106), "soft": (219, 207, 182), "paper": (243, 237, 225)},
    "ink": {"line": (45, 43, 40), "soft": (140, 134, 122), "paper": (247, 244, 238)},
    "red": {"line": (166, 59, 42), "soft": (206, 150, 136), "paper": (250, 243, 238)},
}
PAL = PALETTES["gold"]


def rgba(color, a=255):
    return tuple(color) + (a,)


# ---------------------------------------------------------------- 纹样


def fret(width: int = 1200, height: int = 30, cell: int = 24, rail: bool = True) -> Image.Image:
    """回纹带。cell 越小越密。"""
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    line, soft = PAL["line"], PAL["soft"]
    if rail:
        d.line([(0, 4), (width, 4)], fill=rgba(soft, 150))
        d.line([(0, height - 5), (width, height - 5)], fill=rgba(soft, 150))
    x = 4
    while x + cell < width:
        d.line(
            [(x, height - 5), (x, 11), (x + cell - 8, 11), (x + cell - 8, height - 11), (x + 8, height - 11), (x + 8, 17)],
            fill=rgba(line, 205),
        )
        x += cell
    return img


def lattice(width: int = 1200, height: int = 26, step: int = 26) -> Image.Image:
    """菱格纹。"""
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    soft = PAL["soft"]
    for x in range(-step, width + step, step):
        d.line([(x, 3), (x + step // 2, height - 4), (x + step, 3)], fill=rgba(soft, 150))
        d.line([(x, height - 4), (x + step // 2, 3), (x + step, height - 4)], fill=rgba(soft, 80))
    return img


def wave(width: int = 1200, height: int = 40, amp: int = 8, period: int = 60) -> Image.Image:
    """水波纹（单线正弦）。"""
    import math

    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    pts = [(x, height // 2 + int(amp * math.sin(2 * math.pi * x / period))) for x in range(0, width + 1, 2)]
    d.line(pts, fill=rgba(PAL["line"], 170))
    return img


def rule(width: int = 640, height: int = 26, style: str = "diamond") -> Image.Image:
    """分割线：diamond / dot / tridot / dash / bracket。"""
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    y, cx = height // 2, width // 2
    line, soft = PAL["line"], PAL["soft"]

    if style == "dot":
        d.line([(60, y), (width - 60, y)], fill=rgba(soft, 150))
        d.ellipse([cx - 3, y - 3, cx + 3, y + 3], fill=rgba(line, 225))
    elif style == "tridot":
        d.line([(60, y), (width - 60, y)], fill=rgba(soft, 130))
        for dx in (-16, 0, 16):
            d.ellipse([cx + dx - 3, y - 3, cx + dx + 3, y + 3], fill=rgba(line, 220))
    elif style == "dash":
        x = 60
        while x < width - 60:
            d.line([(x, y), (x + 18, y)], fill=rgba(soft, 170))
            x += 30
    elif style == "bracket":
        d.line([(60, y), (cx - 40, y)], fill=rgba(soft, 150))
        d.line([(cx + 40, y), (width - 60, y)], fill=rgba(soft, 150))
        d.line([(cx - 40, y - 7), (cx - 40, y + 7)], fill=rgba(line, 220))
        d.line([(cx + 40, y - 7), (cx + 40, y + 7)], fill=rgba(line, 220))
        d.ellipse([cx - 3, y - 3, cx + 3, y + 3], fill=rgba(line, 220))
    else:  # diamond
        d.line([(60, y), (width - 60, y)], fill=rgba(soft, 150))
        d.polygon([(cx, y - 6), (cx + 7, y), (cx, y + 6), (cx - 7, y)], outline=rgba(line, 220))
    return img


# ---------------------------------------------------------------- 印章


def seal_circle(text: str, sub: str = "小天摄影", size: int = 320) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    line = PAL["line"]
    d.ellipse([8, 8, size - 9, size - 9], outline=rgba(line, 235), width=4)
    d.ellipse([26, 26, size - 27, size - 27], outline=rgba(line, 140), width=2)
    f1, f2 = load_font(int(size * 0.19), "serif"), load_font(int(size * 0.07), "sans")
    for t, f, cy in ((text, f1, size // 2 - int(size * 0.11)), (sub, f2, size // 2 + int(size * 0.13))):
        w = d.textlength(t, font=f)
        d.text(((size - w) / 2, cy), t, font=f, fill=rgba(line, 240))
    return img


def seal_square(char: str, size: int = 120) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    line = PAL["line"]
    d.rectangle([4, 4, size - 5, size - 5], outline=rgba(line, 235), width=3)
    d.rectangle([12, 12, size - 13, size - 13], outline=rgba(line, 140), width=1)
    f = load_font(int(size * 0.52), "serif")
    bb = d.textbbox((0, 0), char, font=f)
    d.text(
        ((size - (bb[2] - bb[0])) / 2 - bb[0], (size - (bb[3] - bb[1])) / 2 - bb[1]),
        char,
        font=f,
        fill=rgba(line, 240),
    )
    return img


def badge(num: int, size: int = 160) -> Image.Image:
    """编号徽章 01 02 03。"""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    line = PAL["line"]
    d.ellipse([6, 6, size - 7, size - 7], outline=rgba(line, 235), width=3)
    d.ellipse([18, 18, size - 19, size - 19], outline=rgba(line, 110), width=1)
    f = load_font(int(size * 0.36), "sans")
    t = f"{num:02d}"
    bb = d.textbbox((0, 0), t, font=f)
    d.text(((size - (bb[2] - bb[0])) / 2 - bb[0], (size - (bb[3] - bb[1])) / 2 - bb[1]), t, font=f, fill=rgba(line, 240))
    return img


# ---------------------------------------------------------------- 角花 / 标签


def corner(size: int = 220, variant: int = 1, rotate: int = 0) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    line, soft = PAL["line"], PAL["soft"]
    if variant == 1:
        d.line([(14, 14), (14, 120)], fill=rgba(line, 200), width=2)
        d.line([(14, 14), (120, 14)], fill=rgba(line, 200), width=2)
        d.line([(14, 34), (100, 34)], fill=rgba(soft, 170))
        d.line([(34, 14), (34, 100)], fill=rgba(soft, 170))
        d.line([(34, 34), (34, 62), (62, 62)], fill=rgba(line, 170))
        d.line([(34, 34), (62, 34), (62, 62)], fill=rgba(line, 170))
    else:
        d.line([(16, 16), (16, 96)], fill=rgba(line, 190))
        d.line([(16, 16), (96, 16)], fill=rgba(line, 190))
        d.arc([16, 16, 66, 66], 180, 270, fill=rgba(line, 150))
        d.ellipse([28, 28, 34, 34], fill=rgba(line, 200))
    return img.rotate(rotate, expand=False)


def tag(text: str, size: int = 22, bg=(79, 168, 220), fg=(255, 255, 255)) -> Image.Image:
    f = load_font(size, "sans")
    probe = Image.new("RGB", (10, 10))
    w = ImageDraw.Draw(probe).textlength(text, font=f)
    pad_x, pad_y = int(size * 0.8), int(size * 0.35)
    img = Image.new("RGBA", (int(w) + pad_x * 2, size + pad_y * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, img.width - 1, img.height - 1], radius=max(4, size // 3), fill=rgba(bg))
    d.text((pad_x, pad_y - 2), text, font=f, fill=rgba(fg))
    return img


# ---------------------------------------------------------------- 底纹


def paper(width: int = 1200, height: int = 1600, seed: int = 31, grain: int = 1) -> Image.Image:
    """无缝宣纸底（纯噪声保证上下可平铺）。"""
    base = PAL["paper"]
    img = Image.new("RGB", (width, height), base)
    px = img.load()
    rnd = random.Random(seed)
    span = 3 if grain >= 2 else 2
    for y in range(height):
        for x in range(width):
            n = rnd.randint(-span, span)
            r, g, b = px[x, y]
            px[x, y] = (max(0, min(255, r + n)), max(0, min(255, g + n)), max(0, min(255, b + n // 2)))

    d = ImageDraw.Draw(img)
    fiber = tuple(max(0, c - 7) for c in base)
    for _ in range(70):
        x = rnd.randint(0, width - 1)
        y0 = rnd.randint(0, max(1, height - 200))
        d.line([(x, y0), (x + rnd.randint(-3, 3), y0 + rnd.randint(80, 400))], fill=fiber)

    img = img.filter(ImageFilter.GaussianBlur(0.4))
    return img


def ice(width: int = 500, height: int = 400, seed: int = 1, alpha: int = 18) -> Image.Image:
    """冰裂纹（半透明白线，压深色底用）。"""
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    rnd = random.Random(seed)
    pts = [(rnd.randint(0, width), rnd.randint(0, height)) for _ in range(28)]
    for i, p in enumerate(pts):
        for q in pts[i + 1 : i + 4]:
            if (p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2 < 175 ** 2:
                d.line([p, q], fill=(255, 255, 255, alpha))
    return img


# ---------------------------------------------------------------- 主流程


def build(out_dir: Path) -> None:
    (out_dir).mkdir(parents=True, exist_ok=True)

    for name, cell in (("密", 20), ("中", 24), ("疏", 34)):
        fret(cell=cell).save(out_dir / f"回纹_{name}.png")

    lattice().save(out_dir / "菱格.png")
    wave().save(out_dir / "水波.png")

    for s in ("diamond", "dot", "tridot", "dash", "bracket"):
        rule(style=s).save(out_dir / f"分割_{s}.png")

    seal_circle("中秋").save(out_dir / "圆印_中秋.png")
    seal_circle("团圆", "小天摄影").save(out_dir / "圆印_团圆.png")
    for ch in "摄月影光秋圆桂湖":
        seal_square(ch).save(out_dir / f"方印_{ch}.png")
    for i in range(1, 9):
        badge(i).save(out_dir / f"编号_{i:02d}.png")

    names = ("左上", "右上", "右下", "左下")
    for v in (1, 2):
        for i, rot in enumerate((0, 90, 180, 270)):
            corner(variant=v, rotate=rot).save(out_dir / f"角花{v}_{names[i]}.png")

    tag("征集中").save(out_dir / "标签_征集中.png")
    tag("中秋特别企划", bg=(27, 58, 92)).save(out_dir / "标签_企划.png")

    paper().save(out_dir / "纸底.jpg", quality=88, optimize=True)
    for s in range(1, 5):
        ice(seed=s).save(out_dir / f"冰裂_{s}.png")


def main() -> None:
    ap = argparse.ArgumentParser(description="生成中式纹样 / 印章 / 底纹")
    ap.add_argument("-o", "--out", default="out", help="输出目录（默认 ./out）")
    ap.add_argument("--palette", default="gold", choices=sorted(PALETTES), help="配色")
    args = ap.parse_args()

    global PAL
    PAL = PALETTES[args.palette]
    build(Path(args.out))
    print(f"done -> {Path(args.out).resolve()}  (palette={args.palette})")


if __name__ == "__main__":
    main()
