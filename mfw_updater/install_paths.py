"""安装锚点、发行根与可执行文件路径解析（更新器侧）。"""

from __future__ import annotations

import sys
from pathlib import Path

APP_BUNDLE_NAME = "MFW.app"
APP_EXECUTABLE_RELATIVE_PATH = Path("Contents") / "MacOS" / "MFW"
UPDATER_DIR_NAME = "MFWUpdater"
UPDATER_COPY_DIR_NAME = "MFWUpdater1"
UPDATER_EXECUTABLE_NAME = (
    "MFWUpdater.exe" if sys.platform.startswith("win32") else "MFWUpdater"
)


def resolve_install_anchor() -> Path:
    """定位 MFW 安装锚点（主程序 Mach-O/exe 或更新器可执行文件）。"""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve()

    compiled = globals().get("__compiled__")
    if compiled is not None:
        argv0 = getattr(compiled, "onefile_argv0", None) or sys.argv[0]
        return Path(argv0).resolve()

    if sys.argv and sys.argv[0]:
        candidate = Path(sys.argv[0]).resolve()
        if candidate.exists():
            return candidate

    root = Path(__file__).resolve().parents[1]
    return (root / "updater.py").resolve()


def normalize_install_anchor(anchor: Path | str) -> Path:
    """把 ``.app`` 路径和主程序路径统一为 bundle 内的 Mach-O 路径。"""
    resolved = Path(anchor).resolve()
    if resolved.suffix.lower() == ".app":
        return (resolved / APP_EXECUTABLE_RELATIVE_PATH).resolve()
    return resolved


def is_app_bundle_layout(anchor: Path | str | None = None) -> bool:
    """主程序是否位于标准 ``*.app/Contents/MacOS`` 目录中。"""
    resolved = normalize_install_anchor(anchor or resolve_install_anchor())
    executable_dir = resolved.parent
    contents_dir = executable_dir.parent
    app_dir = contents_dir.parent
    return (
        executable_dir.name == "MacOS"
        and contents_dir.name == "Contents"
        and app_dir.suffix.lower() == ".app"
    )


def resolve_install_root(anchor: Path | str | None = None) -> Path:
    """定位外置发行根，即 ``MFW.app``、资源和用户数据的共同父目录。"""
    resolved_anchor = normalize_install_anchor(anchor or resolve_install_anchor())
    if is_app_bundle_layout(resolved_anchor):
        return resolved_anchor.parents[3]

    if resolved_anchor.parent.name in {UPDATER_DIR_NAME, UPDATER_COPY_DIR_NAME}:
        return resolved_anchor.parent.parent

    return resolved_anchor.parent


def resolve_main_executable(
    install_root: Path | str | None = None,
    *,
    anchor: Path | str | None = None,
) -> Path:
    """解析可用于锁与重启的主程序入口。"""
    resolved_anchor = normalize_install_anchor(anchor or resolve_install_anchor())
    if is_app_bundle_layout(resolved_anchor):
        return resolved_anchor

    root = Path(install_root or resolve_install_root(resolved_anchor)).resolve()
    app_executable = root / APP_BUNDLE_NAME / APP_EXECUTABLE_RELATIVE_PATH
    if app_executable.is_file():
        return app_executable.resolve()

    default_name = "MFW.exe" if sys.platform.startswith("win32") else "MFW"
    default_executable = root / default_name
    if default_executable.is_file():
        return default_executable.resolve()

    if resolved_anchor.suffix.lower() in {".exe", ".bin"}:
        return resolved_anchor
    return resolved_anchor


def resolve_updater_dir(install_root: Path | str | None = None) -> Path:
    root = Path(install_root or resolve_install_root()).resolve()
    return root / UPDATER_DIR_NAME


def resolve_updater_executable(updater_dir: Path | str) -> Path:
    return Path(updater_dir).resolve() / UPDATER_EXECUTABLE_NAME
