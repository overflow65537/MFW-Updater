"""可执行文件与发行元数据（与 Nuitka / CI 保持一致）。"""

from __future__ import annotations

import re

from mfw_updater.__version__ import __version__

PRODUCT_NAME = "MFW-ChainFlow Updater"
PRODUCT_INTERNAL_NAME = "MFWUpdater"
FILE_DESCRIPTION = "MFW-ChainFlow Assistant update helper (sidecar)"
LEGALCopyright = (
    "Copyright (C) overflow65537 and contributors. Licensed under MIT."
)
LICENSE_NAME = "MIT"
GITHUB_OWNER = "overflow65537"
GITHUB_REPO = "MFW-Updater"
MAIN_PROGRAM_REPO = "overflow65537/MFW-PyQt6"


def tag_to_win_version(tag: str) -> str:
    """将 Git tag / __version__ 转为 Windows 四段版本号（与 CI 一致）。"""
    core = tag.strip()
    if core.startswith("v"):
        core = core[1:]
    match = re.match(r"^(\d+)(?:\.(\d+))?(?:\.(\d+))?(?:\.(\d+))?", core)
    parts = [g for g in (match.groups() if match else ()) if g is not None]
    if not parts:
        parts = ["0"]
    while len(parts) < 4:
        parts.append("0")
    return ".".join(parts[:4])


FILE_VERSION = tag_to_win_version(__version__)
PRODUCT_VERSION = FILE_VERSION
