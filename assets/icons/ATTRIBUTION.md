# 更新器图标归属

发行版使用 **`updater.png` / `updater.ico`**（蓝色圆角底 + 白色循环箭头），视觉语义为「刷新 / 更新」，与主程序 logo 区分。

## Lucide `refresh-cw`（ISC）

以下文件直接或间接使用了 Lucide 图标 **`refresh-cw`** 的 SVG 路径数据：

- `assets/icons/updater.svg`
- `tools/generate_updater_icons.py`（内嵌 SVG 字符串）

来源：[lucide-icons/lucide](https://github.com/lucide-icons/lucide) · [refresh-cw](https://lucide.dev/icons/refresh-cw)

`updater.png` 与 `updater.ico` 由 `tools/generate_updater_icons.py` 程序化绘制生成，视觉上与 `refresh-cw` 一致，但不包含 Lucide 原始路径的逐像素栅格化副本。

## ISC License

本目录中与 Lucide `refresh-cw` 相关的 SVG 路径数据，遵循 Lucide 项目的 ISC 许可证。分发时须保留下列版权声明与许可全文：

```text
ISC License

Copyright (c) Lucide Icons and Contributors

Permission to use, copy, modify, and/or distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
```

## 重新生成资源

```bash
python -m pip install pillow
python tools/generate_updater_icons.py
```

会写入 `assets/icons/updater.svg`、`updater.png`、`updater.ico`。CI 在 Nuitka 编译前会自动执行上述步骤。

## 平台说明

- **Windows**：`--windows-icon-from-ico=updater.ico`，资源管理器中可见独立图标。
- **Linux**：`--linux-icon=updater.png`。
- **macOS**：更新器为 standalone 控制台二进制，不打包为 `.app`；Finder 中通常仍显示通用可执行文件图标。
