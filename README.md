<!-- markdownlint-disable MD033 MD041 -->
<p align="center">
  <img alt="LOGO" src="assets/icons/updater.png" width="256" height="256" />
</p>
<div align="center">

# MFW-ChainFlow Updater

**[简体中文](./README.md) | [English](./README-en.md)**

[MFW-ChainFlow Assistant](https://github.com/overflow65537/MFW-PyQt6) 的外置更新器：在主程序退出后以 standalone 方式应用全量更新，支持 Windows / Linux / macOS。

</div>

<p align="center">
  <img alt="license" src="https://img.shields.io/github/license/overflow65537/MFW-Updater">
  <img alt="Python" src="https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white">
  <img alt="platform" src="https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-blueviolet">
  <img alt="commit" src="https://img.shields.io/github/commit-activity/m/overflow65537/MFW-Updater">
</p>

## 简介

本仓库单独维护 MFW 更新器源码与 Nuitka standalone 构建。主程序仓库 [MFW-PyQt6](https://github.com/overflow65537/MFW-PyQt6) 在 CI 组装阶段从本仓库 **GitHub Release** 下载最新预编译产物，无需重复编译更新器。

## 程序信息

| 项 | 值 |
|---|---|
| 产品名称 | MFW-ChainFlow Updater |
| 可执行文件 | `MFWUpdater.exe` / `MFWUpdater` |
| 发行目录 | 与主程序同级的 `MFWUpdater/` |
| 公司 / 组织 | overflow65537 |
| 文件说明 | MFW-ChainFlow Assistant update helper (sidecar) |
| 图标 | 独立「刷新」图标（基于 Lucide ISC），见 [assets/icons/ATTRIBUTION.md](./assets/icons/ATTRIBUTION.md) |
| 许可证 | [MIT](./LICENSE) |

## macOS 是否打成 .app？

**不需要。** 更新器是主程序退出后拉起的 **控制台 sidecar**，用户不会从 Finder 双击打开。三平台统一目录：

```text
MFWUpdater/MFWUpdater   # 或 MFWUpdater.exe
```

若改为 `MFWUpdater.app`，须同步修改主程序路径解析、启动逻辑与 CI 组装；且 `.app` 更适合 GUI 前台程序（如 `MFW.app`），对后台更新器收益很小。macOS standalone 二进制在 Finder 中可能仍显示系统默认可执行文件图标；**Windows / Linux 会嵌入独立 updater 图标**。

## 图标

推荐开源库：**Lucide**（ISC）、Phosphor（MIT）、Tabler（MIT）等，详见 [assets/icons/ATTRIBUTION.md](./assets/icons/ATTRIBUTION.md)。本地生成：

```bash
python -m pip install pillow
python tools/generate_updater_icons.py
```

## 发行布局

Release 附件解压后与 Nuitka `updater.dist` 一致；主程序组装后位于发行根：

```text
MFW/
├── MFW.exe / MFW / MFW.app
├── MFWUpdater/
│   └── MFWUpdater(.exe)
├── maafw/
└── ...
```

## 本地开发

```bash
python -m pip install -r requirements.txt
python updater.py -update
```

## 打包

```bash
python -m pip install -r requirements.txt
python -m nuitka --mode=standalone --output-filename=MFWUpdater updater.py
```

产物目录：`updater.dist/`。

## CI / Release

推送 `v*` 标签触发 `.github/workflows/release.yml`，构建并发布：

| 平台 | 附件 |
|------|------|
| Windows | `MFWUpdater-win-x86_64.zip`、`MFWUpdater-win-aarch64.zip` |
| Linux | `MFWUpdater-linux-{arch}.tar.gz` |
| macOS | `MFWUpdater-macos-{arch}.tar.gz` |

## 与主程序集成

主程序通过 `tools/packaging/fetch_mfw_updater.py` 拉取 Release（默认 `overflow65537/MFW-Updater`、tag `latest`）。

## 许可证

**MIT**，与主程序 [MFW-PyQt6](https://github.com/overflow65537/MFW-PyQt6)（AGPL-3.0）独立授权。详见 [LICENSE](./LICENSE) 与 [AUTHORS.md](./AUTHORS.md)。
