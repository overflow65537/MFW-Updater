"""安装锚点、发行根与可执行文件路径解析（更新器侧）。"""

from __future__ import annotations

import sys
from pathlib import Path

# 仅作缺省回退；运行时优先用 --mfw-exe-path 解析出的实际 *.app 名称。
DEFAULT_APP_BUNDLE_NAME = "MFW.app"
DEFAULT_APP_EXECUTABLE_NAME = "MFW"
APP_EXECUTABLE_RELATIVE_PATH = Path("Contents") / "MacOS" / DEFAULT_APP_EXECUTABLE_NAME
UPDATER_DIR_NAME = "MFWUpdater"
UPDATER_COPY_DIR_NAME = "MFWUpdater1"
UPDATER_EXECUTABLE_NAME = (
    "MFWUpdater.exe" if sys.platform.startswith("win32") else "MFWUpdater"
)

# 兼容旧导入名
APP_BUNDLE_NAME = DEFAULT_APP_BUNDLE_NAME


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


def _looks_like_app_bundle_executable(path: Path) -> bool:
    executable_dir = path.parent
    contents_dir = executable_dir.parent
    app_dir = contents_dir.parent
    return (
        executable_dir.name == "MacOS"
        and contents_dir.name == "Contents"
        and app_dir.suffix.lower() == ".app"
    )


def resolve_macos_executable_in_app(app_dir: Path | str) -> Path | None:
    """在 ``*.app/Contents/MacOS`` 中挑选可用的主程序入口。"""
    app_path = Path(app_dir)
    macos_dir = app_path / "Contents" / "MacOS"
    if not macos_dir.is_dir():
        return None

    preferred = macos_dir / app_path.stem
    if preferred.is_file():
        return preferred.resolve()

    default = macos_dir / DEFAULT_APP_EXECUTABLE_NAME
    if default.is_file():
        return default.resolve()

    for candidate in sorted(macos_dir.iterdir()):
        if candidate.is_file() and not candidate.name.startswith("."):
            return candidate.resolve()
    return None


def normalize_install_anchor(anchor: Path | str) -> Path:
    """把 ``.app`` 路径和主程序路径统一为 bundle 内的 Mach-O 路径。"""
    resolved = Path(anchor).resolve()
    if resolved.suffix.lower() == ".app":
        executable = resolve_macos_executable_in_app(resolved)
        if executable is not None:
            return executable
        return (resolved / APP_EXECUTABLE_RELATIVE_PATH).resolve()
    return resolved


def is_app_bundle_layout(anchor: Path | str | None = None) -> bool:
    """主程序是否位于标准 ``*.app/Contents/MacOS`` 目录中。"""
    raw = Path(anchor or resolve_install_anchor()).resolve()
    if raw.suffix.lower() == ".app":
        return (raw / "Contents" / "Info.plist").is_file() or (
            raw / "Contents" / "MacOS"
        ).is_dir()
    if _looks_like_app_bundle_executable(raw):
        return True
    resolved = normalize_install_anchor(raw)
    return _looks_like_app_bundle_executable(resolved)


def resolve_app_bundle_dir(anchor: Path | str | None = None) -> Path | None:
    """若锚点位于 ``*.app``（或其 ``Contents/MacOS`` 内），返回该 ``.app`` 目录。"""
    raw = Path(anchor or resolve_install_anchor()).resolve()
    if raw.suffix.lower() == ".app":
        return raw
    if _looks_like_app_bundle_executable(raw):
        return raw.parents[2]
    resolved = normalize_install_anchor(raw)
    if _looks_like_app_bundle_executable(resolved):
        return resolved.parents[2]
    return None


def resolve_install_root(anchor: Path | str | None = None) -> Path:
    """定位外置发行根，即 ``*.app``、资源和用户数据的共同父目录。"""
    raw = Path(anchor or resolve_install_anchor()).resolve()
    app_dir = resolve_app_bundle_dir(raw)
    if app_dir is not None:
        return app_dir.parent

    resolved_anchor = normalize_install_anchor(raw)
    if resolved_anchor.parent.name in {UPDATER_DIR_NAME, UPDATER_COPY_DIR_NAME}:
        return resolved_anchor.parent.parent

    return resolved_anchor.parent


def _iter_root_app_bundles(root: Path) -> list[Path]:
    return sorted(
        path
        for path in root.iterdir()
        if path.is_dir()
        and path.suffix.lower() == ".app"
        and (path / "Contents" / "Info.plist").is_file()
    )


def resolve_main_executable(
    install_root: Path | str | None = None,
    *,
    anchor: Path | str | None = None,
) -> Path:
    """解析可用于锁与重启的主程序入口。"""
    raw = Path(anchor or resolve_install_anchor()).resolve()
    resolved_anchor = normalize_install_anchor(raw)
    if is_app_bundle_layout(resolved_anchor):
        return resolved_anchor

    root = Path(install_root or resolve_install_root(resolved_anchor)).resolve()
    for app_dir in _iter_root_app_bundles(root):
        executable = resolve_macos_executable_in_app(app_dir)
        if executable is not None:
            return executable

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
