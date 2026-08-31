# SPDX-License-Identifier: MIT

"""7z / 7-Zip SFX 归档检测与解压（依赖 py7zr）。"""

from __future__ import annotations

import logging
from pathlib import Path, PurePosixPath
from typing import Callable

logger = logging.getLogger(__name__)


def import_py7zr():
    try:
        import py7zr

        return py7zr
    except ImportError:
        return None


def path_readable_by_py7zr(path: Path | str) -> bool:
    py7zr = import_py7zr()
    if py7zr is None:
        return False
    try:
        with py7zr.SevenZipFile(Path(path), mode="r") as archive:
            archive.getnames()
        return True
    except Exception:
        return False


def extract_all_7z_to_directory(archive_path: Path | str, dest: Path) -> bool:
    py7zr = import_py7zr()
    if py7zr is None:
        return False
    dest.mkdir(parents=True, exist_ok=True)
    try:
        with py7zr.SevenZipFile(Path(archive_path), mode="r") as archive:
            archive.extractall(path=str(dest))
        return True
    except Exception as exc:
        logger.debug("extract_all_7z_to_directory 失败: %s", exc)
        return False


def extract_7z_hotfix_flat(
    archive_path: Path | str,
    extract_to_path: Path,
    *,
    interface_names: set[str],
) -> bool:
    py7zr = import_py7zr()
    if py7zr is None:
        return False
    extract_to_path.mkdir(parents=True, exist_ok=True)
    interface_names_lower = {n.lower() for n in interface_names}
    archive_path = Path(archive_path)
    try:
        with py7zr.SevenZipFile(archive_path, mode="r") as archive:
            raw_names = archive.getnames()
            members = [n.replace("\\", "/") for n in raw_names]

            interface_dir_parts: tuple[str, ...] | None = None
            for member in members:
                member_path = Path(member)
                if member_path.name.lower() in interface_names_lower:
                    interface_dir_parts = tuple(
                        p for p in member_path.parent.parts if p and p != "."
                    )
                    break

            for raw, member in zip(raw_names, members):
                member_path = Path(member)
                member_parts = tuple(p for p in member_path.parts if p and p != ".")
                if interface_dir_parts:
                    if member_parts[: len(interface_dir_parts)] != interface_dir_parts:
                        continue
                    relative_parts = member_parts[len(interface_dir_parts) :]
                else:
                    relative_parts = member_parts
                if not relative_parts:
                    continue
                if member.endswith("/"):
                    extract_to_path.joinpath(*relative_parts).mkdir(
                        parents=True, exist_ok=True
                    )
                    continue
                data = archive.read([raw])
                bio = data.get(raw)
                if bio is None:
                    for key, value in data.items():
                        if key.replace("\\", "/") == member:
                            bio = value
                            break
                if bio is None:
                    continue
                target_path = extract_to_path.joinpath(*relative_parts)
                target_path.parent.mkdir(parents=True, exist_ok=True)
                with open(target_path, "wb") as out_f:
                    bio.seek(0)
                    out_f.write(bio.read())
        return True
    except Exception:
        logger.exception("extract_7z_hotfix_flat 失败: %s", archive_path)
        return False
