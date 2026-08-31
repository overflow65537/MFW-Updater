<!-- markdownlint-disable MD033 MD041 -->
<p align="center">
  <img alt="LOGO" src="assets/icons/updater.png" width="256" height="256" />
</p>
<div align="center">

# MFW-ChainFlow Updater

**[简体中文](./README.md) | [English](./README-en.md)**

Standalone updater sidecar for [MFW-ChainFlow Assistant](https://github.com/overflow65537/MFW-PyQt6). Applies full UI updates after the main program exits on Windows, Linux, and macOS.

</div>

<p align="center">
  <img alt="license" src="https://img.shields.io/github/license/overflow65537/MFW-Updater">
  <img alt="Python" src="https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white">
  <img alt="platform" src="https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-blueviolet">
  <img alt="commit" src="https://img.shields.io/github/commit-activity/m/overflow65537/MFW-Updater">
</p>

## Overview

This repository owns the updater source and Nuitka standalone builds. [MFW-PyQt6](https://github.com/overflow65537/MFW-PyQt6) downloads prebuilt Release assets during CI assembly instead of compiling the updater again.

## Product metadata

| Field | Value |
|-------|-------|
| Product name | MFW-ChainFlow Updater |
| Executable | `MFWUpdater.exe` / `MFWUpdater` |
| Install folder | `MFWUpdater/` next to the main app |
| Company / org | overflow65537 |
| File description | MFW-ChainFlow Assistant update helper (sidecar) |
| License | [MIT](./LICENSE) |

## macOS: app bundle?

**No.** The updater is a **console sidecar** spawned after MFW exits; users do not launch it from Finder. All platforms use `MFWUpdater/MFWUpdater` (or `.exe`). A `.app` bundle would require path and launch changes in MFW-PyQt6 with little benefit for a headless tool. Windows and Linux embed the dedicated updater icon; macOS standalone binaries may keep the generic executable icon in Finder.

See [assets/icons/ATTRIBUTION.md](./assets/icons/ATTRIBUTION.md) for open-source icon libraries (Lucide ISC, Phosphor MIT, etc.).

## Layout

```text
MFW/
├── MFW.exe / MFW / MFW.app
├── MFWUpdater/
│   └── MFWUpdater(.exe)
├── maafw/
└── ...
```

## Development

```bash
python -m pip install -r requirements.txt
python updater.py -update
```

## Build

```bash
python -m pip install -r requirements.txt
python -m nuitka --mode=standalone --output-filename=MFWUpdater updater.py
```

Output: `updater.dist/`.

## CI / Release

Tag pushes (`v*`) run `.github/workflows/release.yml` and publish platform archives listed in the Chinese README.

## License

**MIT**. The main app [MFW-PyQt6](https://github.com/overflow65537/MFW-PyQt6) is **AGPL-3.0**. See [LICENSE](./LICENSE) and [AUTHORS.md](./AUTHORS.md).
