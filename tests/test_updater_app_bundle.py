import os
import stat
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

import updater


def _write_app(root: Path, version: str, *, app_name: str = "MFW.app") -> Path:
    app = root / app_name
    executable_name = Path(app_name).stem
    executable = app / "Contents" / "MacOS" / executable_name
    executable.parent.mkdir(parents=True)
    executable.write_text(version, encoding="utf-8")
    (app / "Contents" / "Info.plist").write_text(
        f"<plist><string>{version}</string></plist>", encoding="utf-8"
    )
    return app


class AppBundleUpdateTests(unittest.TestCase):
    def tearDown(self):
        updater.RUNTIME_OPTS.mfw_exe_path = None
        updater.RUNTIME_OPTS.startup_executable_name = None

    def test_zip_extraction_preserves_executable_mode(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            archive_path = root / "app.zip"
            info = zipfile.ZipInfo("MFW.app/Contents/MacOS/MFW")
            info.external_attr = (stat.S_IFREG | 0o755) << 16
            with zipfile.ZipFile(archive_path, "w") as archive:
                archive.writestr(info, b"binary")

            destination = root / "extract"
            with zipfile.ZipFile(archive_path) as archive:
                updater._extract_zip_member_preserving_mode(
                    archive, archive.getinfo(info.filename), destination
                )

            executable = destination / info.filename
            self.assertEqual(executable.read_bytes(), b"binary")
            if os.name != "nt":
                self.assertTrue(executable.stat().st_mode & stat.S_IXUSR)

    def test_tar_gz_extraction_preserves_executable_mode(self):
        import io
        import tarfile

        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            archive_path = root / "app.tar.gz"
            with tarfile.open(archive_path, "w:gz") as archive:
                for name, payload in (
                    ("MFW.app/Contents/MacOS/MFW", b"binary"),
                    ("run-mfw.sh", b"#!/bin/sh\n"),
                ):
                    info = tarfile.TarInfo(name)
                    info.size = len(payload)
                    info.mode = 0o755
                    archive.addfile(info, io.BytesIO(payload))

            destination = root / "extract"
            with tarfile.open(archive_path, "r:gz") as archive:
                for member in archive.getmembers():
                    updater._extract_tar_member_preserving_mode(
                        archive, member, destination
                    )

            extracted_bin = destination / "MFW.app" / "Contents" / "MacOS" / "MFW"
            extracted_script = destination / "run-mfw.sh"
            self.assertEqual(extracted_bin.read_bytes(), b"binary")
            self.assertEqual(extracted_script.read_bytes(), b"#!/bin/sh\n")
            if os.name != "nt":
                self.assertTrue(extracted_bin.stat().st_mode & stat.S_IXUSR)
                self.assertTrue(extracted_script.stat().st_mode & stat.S_IXUSR)

    def test_path_accepts_tar_gz_update_package(self):
        self.assertTrue(updater._path_is_tar_gz("MFW-linux-x86_64-v1.0.0.tar.gz"))
        self.assertTrue(updater._path_is_supported_update_package("update.tgz"))
        self.assertTrue(updater._path_is_supported_update_package("update.zip"))
        self.assertFalse(updater._path_is_supported_update_package("notes.txt"))

    def test_replaces_app_atomically_and_overlays_runtime(self):
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            install_root = base / "install"
            payload = base / "payload"
            install_root.mkdir()
            payload.mkdir()
            _write_app(install_root, "old")
            _write_app(payload, "new")
            (install_root / "maafw").mkdir()
            (install_root / "maafw" / "old.dylib").write_text("old")
            (install_root / "resource").mkdir()
            (install_root / "resource" / "keep.bin").write_text("keep")
            (payload / "maafw").mkdir()
            (payload / "maafw" / "new.dylib").write_text("new")
            (payload / "resource").mkdir()
            (payload / "resource" / "new.bin").write_text("new")
            (payload / "MFWUpdater").mkdir()
            (payload / "MFWUpdater" / "MFWUpdater").write_text("updater")

            for name in ("config", "debug", "update", "MFWUpdater1"):
                directory = install_root / name
                directory.mkdir()
                (directory / "keep.txt").write_text("keep")

            self.assertTrue(
                updater._replace_app_bundle_atomic(payload, install_root)
            )
            self.assertEqual(
                (
                    install_root
                    / "MFW.app"
                    / "Contents"
                    / "MacOS"
                    / "MFW"
                ).read_text(),
                "new",
            )
            self.assertTrue((install_root / "maafw" / "new.dylib").is_file())
            # 普通覆盖/合并：包内未提供的同级文件可保留（resource 半包语义）
            self.assertTrue((install_root / "resource" / "keep.bin").is_file())
            self.assertTrue((install_root / "resource" / "new.bin").is_file())
            self.assertTrue((install_root / "MFWUpdater" / "MFWUpdater").is_file())
            for name in ("config", "debug", "update", "MFWUpdater1"):
                self.assertTrue((install_root / name / "keep.txt").is_file())

    def test_uses_mfw_exe_path_app_bundle_name(self):
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            install_root = base / "install"
            payload = base / "payload"
            install_root.mkdir()
            payload.mkdir()
            installed = _write_app(install_root, "old", app_name="FOS.app")
            _write_app(payload, "new", app_name="FOS.app")
            (payload / "resource").mkdir()
            (payload / "resource" / "a.txt").write_text("a")

            updater.RUNTIME_OPTS.mfw_exe_path = str(
                installed / "Contents" / "MacOS" / "FOS"
            )
            self.assertTrue(
                updater._replace_app_bundle_atomic(payload, install_root)
            )
            self.assertEqual(
                (
                    install_root / "FOS.app" / "Contents" / "MacOS" / "FOS"
                ).read_text(),
                "new",
            )
            self.assertFalse((install_root / "MFW.app").exists())
            self.assertTrue((install_root / "resource" / "a.txt").is_file())

    def test_maps_package_default_app_onto_runtime_name(self):
        """包内仍是默认名时，安装到 --mfw-exe-path 对应的目标 .app 名。"""
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            install_root = base / "install"
            payload = base / "payload"
            install_root.mkdir()
            payload.mkdir()
            installed = _write_app(install_root, "old", app_name="FOS.app")
            _write_app(payload, "new", app_name="MFW.app")

            updater.RUNTIME_OPTS.mfw_exe_path = str(
                installed / "Contents" / "MacOS" / "FOS"
            )
            self.assertTrue(
                updater._replace_app_bundle_atomic(payload, install_root)
            )
            self.assertEqual(
                (
                    install_root / "FOS.app" / "Contents" / "MacOS" / "MFW"
                ).read_text(),
                "new",
            )
            self.assertFalse((install_root / "MFW.app").exists())

    def test_rolls_back_when_staging_cannot_be_installed(self):
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            install_root = base / "install"
            payload = base / "payload"
            install_root.mkdir()
            payload.mkdir()
            _write_app(install_root, "old")
            _write_app(payload, "new")

            real_replace = os.replace
            failed_once = False

            def fail_new_app_once(src, dst):
                nonlocal failed_once
                src_path = Path(src)
                dst_path = Path(dst)
                if (
                    not failed_once
                    and ".MFW.app.staging-" in src_path.name
                    and dst_path.name == "MFW.app"
                ):
                    failed_once = True
                    raise OSError("simulated install failure")
                return real_replace(src, dst)

            with patch("updater.os.replace", side_effect=fail_new_app_once):
                self.assertFalse(
                    updater._replace_app_bundle_atomic(payload, install_root)
                )

            executable = (
                install_root / "MFW.app" / "Contents" / "MacOS" / "MFW"
            )
            self.assertEqual(executable.read_text(), "old")
            self.assertFalse(
                any(".staging-" in path.name for path in install_root.iterdir())
            )

    def test_rejects_incomplete_app(self):
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            install_root = base / "install"
            payload = base / "payload"
            install_root.mkdir()
            (payload / "MFW.app" / "Contents").mkdir(parents=True)
            self.assertFalse(
                updater._replace_app_bundle_atomic(payload, install_root)
            )

    def test_restart_uses_install_root_as_working_directory(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            executable = root / "MFW.app" / "Contents" / "MacOS" / "MFW"
            executable.parent.mkdir(parents=True)
            executable.touch()
            with (
                patch(
                    "updater._restore_startup_executable_name",
                    return_value=str(executable),
                ),
                patch("updater.os.getcwd", return_value=str(root)),
                patch("updater.subprocess.Popen") as popen,
            ):
                updater.start_mfw_process()
            popen.assert_called_once()
            self.assertEqual(popen.call_args.kwargs["cwd"], str(root))

    def test_ensure_install_root_cwd_from_updater_subdir(self):
        """从 MFWUpdater1/ 启动时，应 chdir 到发行根。"""
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            updater_dir = root / "MFWUpdater1"
            updater_dir.mkdir()
            fos = root / "FOS.exe"
            fos.touch()
            original_cwd = Path.cwd()
            try:
                os.chdir(updater_dir)
                updater.RUNTIME_OPTS.mfw_exe_path = str(fos)
                resolved = updater.ensure_install_root_cwd()
                self.assertEqual(resolved, root.resolve())
                self.assertEqual(Path.cwd().resolve(), root.resolve())
            finally:
                updater.RUNTIME_OPTS.mfw_exe_path = None
                os.chdir(original_cwd)

    def test_setup_update_logger_writes_under_install_root(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            wrong_cwd = root / "MFWUpdater1"
            wrong_cwd.mkdir()
            original_cwd = Path.cwd()
            logger = None
            try:
                os.chdir(wrong_cwd)
                logger = updater.setup_update_logger(root)
                log_path = root / "debug" / "updater.log"
                self.assertTrue(log_path.exists())
                self.assertFalse((wrong_cwd / "debug" / "updater.log").exists())
                logger.info("cwd-guard-test")
                for handler in list(logger.handlers):
                    handler.flush()
                self.assertIn("cwd-guard-test", log_path.read_text(encoding="utf-8"))
            finally:
                if logger is not None:
                    for handler in list(logger.handlers):
                        handler.close()
                    logger.handlers.clear()
                os.chdir(original_cwd)
                # 必须先回到原 cwd，再重绑模块级 logger，避免把 handler 留在临时目录
                updater.update_logger = updater.setup_update_logger()


if __name__ == "__main__":
    unittest.main()
