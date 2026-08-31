#!/usr/bin/env python3
"""从 SVG 或程序化绘制生成 updater.png / updater.ico。"""

from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ICONS = ROOT / "assets" / "icons"

# Lucide refresh-cw (ISC) — https://lucide.dev/icons/refresh-cw
UPDATER_SVG = """\
<svg xmlns="http://www.w3.org/2000/svg" width="256" height="256" viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"/>
  <path d="M21 3v5h-5"/>
  <path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"/>
  <path d="M3 21v-5h5"/>
</svg>
"""


def _render_png(size: int):
    from PIL import Image, ImageDraw

    img = Image.new("RGBA", (size, size), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    margin = size // 8
    draw.rounded_rectangle(
        [margin, margin, size - margin, size - margin],
        radius=size // 6,
        fill=(37, 99, 235, 255),
    )
    cx = cy = size // 2
    radius = size // 4
    width = max(3, size // 32)
    for start in (35, 215):
        for step in range(58):
            angle0 = math.radians(start + step * 2.85)
            angle1 = math.radians(start + (step + 1) * 2.85)
            draw.line(
                [
                    (cx + radius * math.cos(angle0), cy + radius * math.sin(angle0)),
                    (cx + radius * math.cos(angle1), cy + radius * math.sin(angle1)),
                ],
                fill=(255, 255, 255, 255),
                width=width,
            )
    for angle_deg in (92, 272):
        angle = math.radians(angle_deg)
        tip = (cx + radius * math.cos(angle), cy + radius * math.sin(angle))
        for delta in (-28, 28):
            branch = math.radians(angle_deg + delta)
            head_len = max(8, size // 22)
            draw.line(
                [
                    tip,
                    (
                        tip[0] - head_len * math.cos(branch),
                        tip[1] - head_len * math.sin(branch),
                    ),
                ],
                fill=(255, 255, 255, 255),
                width=width,
            )
    return img


def main() -> int:
    try:
        from PIL import Image  # noqa: F401
    except ImportError:
        print("请先安装: python -m pip install pillow", file=sys.stderr)
        return 1

    ICONS.mkdir(parents=True, exist_ok=True)
    (ICONS / "updater.svg").write_text(UPDATER_SVG, encoding="utf-8")
    png = _render_png(256)
    png.save(ICONS / "updater.png")
    sizes = [16, 32, 48, 64, 128, 256]
    images = [_render_png(size) for size in sizes]
    images[0].save(
        ICONS / "updater.ico",
        format="ICO",
        sizes=[(size, size) for size in sizes],
        append_images=images[1:],
    )
    print(f"[INFO] wrote {ICONS / 'updater.png'}")
    print(f"[INFO] wrote {ICONS / 'updater.ico'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
