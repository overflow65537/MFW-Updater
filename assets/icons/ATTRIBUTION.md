# 更新器图标

发行版使用 **`updater.png` / `updater.ico`**（蓝色圆角底 + 白色循环箭头），视觉语义为「刷新 / 更新」，与主程序 logo 区分。

## 推荐的开源图标库

以下项目均可免费用于开源软件（发布时请保留对应许可证说明）：

| 项目 | 许可证 | 链接 | 适合更新器的图标示例 |
|------|--------|------|----------------------|
| **Lucide** | ISC | https://lucide.dev | `refresh-cw`、`download`、`package-down` |
| **Phosphor Icons** | MIT | https://phosphoricons.com | `arrows-clockwise`、`download-simple` |
| **Tabler Icons** | MIT | https://tabler.io/icons | `refresh`、`cloud-download` |
| **Material Symbols** | Apache-2.0 | https://fonts.google.com/icons | `sync`、`download` |
| **Feather Icons** | MIT | https://feathericons.com | `refresh-cw`、`download` |

当前 `updater.svg` 中的路径来自 **Lucide `refresh-cw`**（ISC），见 https://github.com/lucide-icons/lucide .

## 重新生成资源

```bash
python -m pip install pillow
python tools/generate_updater_icons.py
```

会写入 `assets/icons/updater.svg`、`updater.png`、`updater.ico`。CI 在 Nuitka 编译前会自动执行上述步骤。

## 平台说明

- **Windows**：`--windows-icon-from-ico=updater.ico`，资源管理器中可见独立图标。
- **Linux**：`--linux-icon=updater.png`。
- **macOS**：更新器为 **standalone 控制台二进制**，**不打包为 `.app`**；Finder 中通常仍显示通用终端/可执行文件图标，对后台 sidecar 进程足够。若强行 `--macos-create-app-bundle`，启动路径需改为 `MFWUpdater.app/Contents/MacOS/MFWUpdater`，与主程序现有组装逻辑不一致，故不推荐。
