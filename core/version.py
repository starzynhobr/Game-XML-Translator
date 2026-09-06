from __future__ import annotations

import re
import sys
from pathlib import Path

try:
    from core._build_version import BUILD_VERSION as _EMBEDDED_BUILD_VERSION
except ImportError:
    _EMBEDDED_BUILD_VERSION = None

_VERSION_RE = re.compile(r"^\s*set\s+APP_VERSION=(\d+)\.(\d+)\.(\d+)\.(\d+)\s*$", re.I | re.M)
_EMBEDDED_VERSION_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)\.(\d+)$")
_PACKAGED_EXE_NAME = "stzxmltranslator.exe"


def _build_script_version(path: Path) -> tuple[int, int, int, int] | None:
    try:
        match = _VERSION_RE.search(path.read_text(encoding="utf-8"))
    except OSError:
        return None
    if not match:
        return None
    return tuple(int(part) for part in match.groups())


def _embedded_version_parts() -> tuple[int, int, int, int] | None:
    if not isinstance(_EMBEDDED_BUILD_VERSION, str):
        return None
    match = _EMBEDDED_VERSION_RE.fullmatch(_EMBEDDED_BUILD_VERSION.strip())
    if not match:
        return None
    return tuple(int(part) for part in match.groups())


def _windows_executable_version(path: str) -> tuple[int, int, int, int] | None:
    if sys.platform != "win32":
        return None
    try:
        import ctypes
        from ctypes import wintypes

        size = ctypes.windll.version.GetFileVersionInfoSizeW(path, None)
        if not size:
            return None
        data = ctypes.create_string_buffer(size)
        if not ctypes.windll.version.GetFileVersionInfoW(path, 0, size, data):
            return None
        value = ctypes.c_void_p()
        value_size = wintypes.UINT()
        if not ctypes.windll.version.VerQueryValueW(
            data, "\\", ctypes.byref(value), ctypes.byref(value_size)
        ):
            return None

        class FixedFileInfo(ctypes.Structure):
            _fields_ = [
                ("signature", wintypes.DWORD),
                ("struct_version", wintypes.DWORD),
                ("file_version_ms", wintypes.DWORD),
                ("file_version_ls", wintypes.DWORD),
            ]

        info = ctypes.cast(value, ctypes.POINTER(FixedFileInfo)).contents
        return (
            info.file_version_ms >> 16,
            info.file_version_ms & 0xFFFF,
            info.file_version_ls >> 16,
            info.file_version_ls & 0xFFFF,
        )
    except (AttributeError, OSError, ValueError):
        return None


def app_version_parts() -> tuple[int, int, int, int]:
    """Resolve the product version from its canonical build declaration."""
    is_packaged = (
        getattr(sys, "frozen", False)
        or "__compiled__" in globals()
        or Path(sys.executable).name.casefold() == _PACKAGED_EXE_NAME
    )
    if is_packaged:
        embedded_version = _embedded_version_parts()
        if embedded_version:
            return embedded_version
        executable_version = _windows_executable_version(sys.executable)
        if executable_version:
            return executable_version

    script = Path(__file__).resolve().parents[1] / "build_nuitka.bat"
    return _build_script_version(script) or (0, 0, 0, 0)


def app_version() -> str:
    major, minor, patch, _build = app_version_parts()
    return f"{major}.{minor}.{patch}"
