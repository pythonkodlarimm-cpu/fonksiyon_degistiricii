# -*- coding: utf-8 -*-
"""
DOSYA: app/services/android/uri_servisi.py

SURUM: 2
"""

from __future__ import annotations

from pathlib import Path
from kivy.utils import platform

# =========================================================
# HATA
# =========================================================
class AndroidUriServisiHatasi(ValueError):
    pass


# =========================================================
# CACHE (çok önemli performans iyileştirmesi)
# =========================================================
_ANDROID_CTX = None


def _debug(msg: str):
    try:
        print("[ANDROID_URI]", msg)
    except Exception:
        pass


def _ensure_android():
    if platform != "android":
        raise AndroidUriServisiHatasi("Sadece Android desteklenir.")


def _classes():
    global _ANDROID_CTX

    if _ANDROID_CTX is not None:
        return _ANDROID_CTX

    _ensure_android()

    try:
        from jnius import autoclass, cast

        Uri = autoclass("android.net.Uri")
        Intent = autoclass("android.content.Intent")
        PythonActivity = autoclass("org.kivy.android.PythonActivity")

        activity = cast("android.app.Activity", PythonActivity.mActivity)
        if activity is None:
            raise AndroidUriServisiHatasi("Activity alınamadı.")

        resolver = activity.getContentResolver()
        if resolver is None:
            raise AndroidUriServisiHatasi("Resolver alınamadı.")

        _ANDROID_CTX = {
            "Uri": Uri,
            "Intent": Intent,
            "activity": activity,
            "resolver": resolver,
        }

        return _ANDROID_CTX

    except Exception as exc:
        raise AndroidUriServisiHatasi("Android sınıfları yüklenemedi.") from exc


# =========================================================
# URI
# =========================================================
def is_android_document_uri(value: str) -> bool:
    return str(value or "").strip().startswith("content://")


def parse_uri(uri_str: str):
    raw = str(uri_str or "").strip()

    if not raw or not is_android_document_uri(raw):
        raise AndroidUriServisiHatasi("Geçersiz URI")

    try:
        return _classes()["Uri"].parse(raw)
    except Exception as exc:
        raise AndroidUriServisiHatasi("URI parse edilemedi.") from exc


# =========================================================
# PERMISSION
# =========================================================
def take_persistable_permission(intent, uri_str: str) -> None:
    if intent is None:
        raise AndroidUriServisiHatasi("Intent boş")

    ctx = _classes()
    resolver = ctx["resolver"]
    Intent = ctx["Intent"]

    uri = parse_uri(uri_str)

    try:
        flags = int(intent.getFlags() or 0)

        read_flag = int(Intent.FLAG_GRANT_READ_URI_PERMISSION)
        write_flag = int(Intent.FLAG_GRANT_WRITE_URI_PERMISSION)

        take_flags = flags & (read_flag | write_flag)
        if take_flags == 0:
            take_flags = read_flag

        resolver.takePersistableUriPermission(uri, take_flags)

    except Exception as exc:
        raise AndroidUriServisiHatasi("Permission alınamadı.") from exc


# =========================================================
# METADATA
# =========================================================
def get_display_name(uri_str: str) -> str:
    ctx = _classes()
    resolver = ctx["resolver"]
    uri = parse_uri(uri_str)

    cursor = None

    try:
        cursor = resolver.query(uri, None, None, None, None)
        if cursor and cursor.moveToFirst():
            idx = cursor.getColumnIndex("_display_name")
            if idx >= 0:
                val = cursor.getString(idx)
                if val:
                    return str(val).strip()
    except Exception:
        pass
    finally:
        try:
            if cursor:
                cursor.close()
        except Exception:
            pass

    return str(uri_str).rsplit("/", 1)[-1]


def get_mime_type(uri_str: str) -> str:
    try:
        return str(_classes()["resolver"].getType(parse_uri(uri_str)) or "").strip()
    except Exception:
        return ""


# =========================================================
# IO
# =========================================================
def read_text(uri_str: str, encoding: str = "utf-8") -> str:
    resolver = _classes()["resolver"]
    uri = parse_uri(uri_str)

    try:
        stream = resolver.openInputStream(uri)
        if stream is None:
            raise AndroidUriServisiHatasi("Stream açılamadı")

        # 🔥 performanslı okuma
        data = bytearray()
        buffer = bytearray(4096)

        while True:
            read = stream.read(buffer)
            if read == -1:
                break
            data.extend(buffer[:read])

        stream.close()

        return bytes(data).decode(encoding)

    except UnicodeDecodeError as exc:
        raise AndroidUriServisiHatasi("Decode hatası") from exc
    except Exception as exc:
        raise AndroidUriServisiHatasi("Okuma hatası") from exc


def write_text(uri_str: str, content: str, encoding: str = "utf-8") -> None:
    resolver = _classes()["resolver"]
    uri = parse_uri(uri_str)

    try:
        stream = resolver.openOutputStream(uri, "wt")
        if stream is None:
            raise AndroidUriServisiHatasi("Stream açılamadı")

        stream.write(str(content or "").encode(encoding))
        stream.flush()
        stream.close()

    except Exception as exc:
        raise AndroidUriServisiHatasi("Yazma hatası") from exc


# =========================================================
# DIR
# =========================================================
def get_app_cache_dir() -> Path:
    activity = _classes()["activity"]

    try:
        path = activity.getCacheDir()
        root = Path(str(path.getAbsolutePath()))
        root.mkdir(parents=True, exist_ok=True)
        return root
    except Exception as exc:
        raise AndroidUriServisiHatasi("Cache alınamadı") from exc


def get_app_files_dir() -> Path:
    activity = _classes()["activity"]

    try:
        path = activity.getFilesDir()
        root = Path(str(path.getAbsolutePath()))
        root.mkdir(parents=True, exist_ok=True)
        return root
    except Exception as exc:
        raise AndroidUriServisiHatasi("Files alınamadı") from exc