#!/usr/bin/env python3
"""从 Lucide SVG 路径栅格化生成 updater.svg / updater.png / updater.ico。"""

from __future__ import annotations

import sys
from io import BytesIO
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ICONS = ROOT / "assets" / "icons"

# Lucide refresh-cw (ISC) — https://lucide.dev/icons/refresh-cw
LUCIDE_PATHS = (
    "M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8",
    "M21 3v5h-5",
    "M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16",
    "M3 21v-5h5",
)

UPDATER_SVG = """\
<svg xmlns="http://www.w3.org/2000/svg" width="256" height="256" viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <!-- Lucide refresh-cw (ISC) https://lucide.dev/icons/refresh-cw -->
  <rect width="24" height="24" rx="4" fill="#2563eb" stroke="none"/>
  <path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"/>
  <path d="M21 3v5h-5"/>
  <path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"/>
  <path d="M3 21v-5h5"/>
</svg>
"""

VIEWBOX = 24.0
BG_COLOR = (37, 99, 235, 255)
FG_COLOR = (255, 255, 255, 255)
CORNER_RADIUS = 4.0
STROKE_WIDTH = 2.0


def _path_points(d: str, size: int) -> list[tuple[float, float]]:
    from svg.path import parse_path

    path = parse_path(d)
    steps = max(24, int(path.length() * size / VIEWBOX))
    scale = size / VIEWBOX
    return [(path.point(i / steps).real * scale, path.point(i / steps).imag * scale) for i in range(steps + 1)]


def _render_png(size: int):
    from PIL import Image, ImageDraw

    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    radius = CORNER_RADIUS * size / VIEWBOX
    draw.rounded_rectangle([0, 0, size - 1, size - 1], radius=radius, fill=BG_COLOR)

    stroke = max(1, round(STROKE_WIDTH * size / VIEWBOX))
    for d in LUCIDE_PATHS:
        points = _path_points(d, size)
        if len(points) >= 2:
            draw.line(points, fill=FG_COLOR, width=stroke, joint="curve")

    return img


def main() -> int:
    try:
        from PIL import Image  # noqa: F401
        from svg.path import parse_path  # noqa: F401
    except ImportError:
        print("请先安装: python -m pip install -r requirements-build.txt", file=sys.stderr)
        return 1

    ICONS.mkdir(parents=True, exist_ok=True)
    (ICONS / "updater.svg").write_text(UPDATER_SVG, encoding="utf-8")

    png = _render_png(256)
    png.save(ICONS / "updater.png")

    sizes = [16, 32, 48, 64, 128, 256]
    images = [_render_png(size) for size in sizes]
    buffer = BytesIO()
    images[0].save(
        buffer,
        format="ICO",
        sizes=[(size, size) for size in sizes],
        append_images=images[1:],
    )
    (ICONS / "updater.ico").write_bytes(buffer.getvalue())

    print(f"[INFO] wrote {ICONS / 'updater.svg'}")
    print(f"[INFO] wrote {ICONS / 'updater.png'}")
    print(f"[INFO] wrote {ICONS / 'updater.ico'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
