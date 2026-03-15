# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path

from kivy.utils import platform


class AndroidUriServisiHatasi(ValueError):
    pass


def is_android_document_uri(value: str) -> bool:
    return str(value or "").strip().startswith("content://")


def _ensure_android() -> None:
    if platform != "android":
        raise AndroidUriServisiHatasi("Bu servis yalnızca Android'de çalışır.")


def _classes():
    _ensure_android()
    try:
        from jnius import autoclass, cast  # type: ignore

        Uri = autoclass("android.net.Uri")
        Intent = autoclass("android.content.Intent")
        PythonActivity = autoclass("org.kivy.android.PythonActivity")
        current_activity = cast("android.app.Activity", PythonActivity.mActivity)
        resolver = current_activity.getContentResolver()

        return {
            "Uri": Uri,
            "Intent": Intent,
            "activity": current_activity,
            "resolver": resolver,
        }
    except Exception as exc:
        raise AndroidUriServisiHatasi("Android sınıfları yüklenemedi.") from exc


def parse_uri(uri_str: str):
    raw = str(uri_str or "").strip()
    if not raw or not is_android_document_uri(raw):
        raise AndroidUriServisiHatasi("Geçerli bir Android document URI değil.")
    try:
        return _classes()["Uri"].parse(raw)
    except Exception as exc:
        raise AndroidUriServisiHatasi("URI parse edilemedi.") from exc


def take_persistable_permission(intent, uri_str: str) -> None:
    if intent is None:
        raise AndroidUriServisiHatasi("Intent boş.")
    ctx = _classes()
    resolver = ctx["resolver"]
    Intent = ctx["Intent"]
    uri = parse_uri(uri_str)

    try:
        flags = intent.getFlags()
        take_flags = flags & (Intent.FLAG_GRANT_READ_URI_PERMISSION | Intent.FLAG_GRANT_WRITE_URI_PERMISSION)
        resolver.takePersistableUriPermission(uri, take_flags)
    except Exception as exc:
        raise AndroidUriServisiHatasi("Persistable URI izni alınamadı.") from exc


def get_display_name(uri_str: str) -> str:
    ctx = _classes()
    resolver = ctx["resolver"]
    uri = parse_uri(uri_str)

    cursor = None
    try:
        cursor = resolver.query(uri, None, None, None, None)
        if cursor is not None and cursor.moveToFirst():
            idx = cursor.getColumnIndex("_display_name")
            if idx >= 0:
                val = cursor.getString(idx)
                if val:
                    return str(val).strip()
    except Exception:
        pass
    finally:
        try:
            if cursor is not None:
                cursor.close()
        except Exception:
            pass

    try:
        return str(uri_str).rsplit("/", 1)[-1]
    except Exception:
        return ""


def get_mime_type(uri_str: str) -> str:
    try:
        return str(_classes()["resolver"].getType(parse_uri(uri_str)) or "").strip()
    except Exception:
        return ""


def read_text(uri_str: str, encoding: str = "utf-8") -> str:
    resolver = _classes()["resolver"]
    uri = parse_uri(uri_str)
    input_stream = None
    try:
        input_stream = resolver.openInputStream(uri)
        if input_stream is None:
            raise AndroidUriServisiHatasi("Input stream açılamadı.")
        data = bytearray()
        while True:
            b = input_stream.read()
            if b == -1:
                break
            data.append(b)
        return bytes(data).decode(encoding)
    except UnicodeDecodeError as exc:
        raise AndroidUriServisiHatasi(f"URI içeriği '{encoding}' ile çözümlenemedi.") from exc
    except AndroidUriServisiHatasi:
        raise
    except Exception as exc:
        raise AndroidUriServisiHatasi("URI içeriği okunamadı.") from exc
    finally:
        try:
            if input_stream is not None:
                input_stream.close()
        except Exception:
            pass


def write_text(uri_str: str, content: str, encoding: str = "utf-8") -> None:
    resolver = _classes()["resolver"]
    uri = parse_uri(uri_str)
    output_stream = None
    try:
        output_stream = resolver.openOutputStream(uri, "wt")
        if output_stream is None:
            raise AndroidUriServisiHatasi("Output stream açılamadı.")
        output_stream.write(str(content or "").encode(encoding))
        output_stream.flush()
    except AndroidUriServisiHatasi:
        raise
    except Exception as exc:
        raise AndroidUriServisiHatasi("URI içeriği yazılamadı.") from exc
    finally:
        try:
            if output_stream is not None:
                output_stream.close()
        except Exception:
            pass


def get_app_cache_dir() -> Path:
    try:
        activity = _classes()["activity"]
        root = Path(str(activity.getCacheDir().getAbsolutePath()))
        root.mkdir(parents=True, exist_ok=True)
        return root
    except Exception as exc:
        raise AndroidUriServisiHatasi("Cache klasörü alınamadı.") from exc


def get_app_files_dir() -> Path:
    try:
        activity = _classes()["activity"]
        root = Path(str(activity.getFilesDir().getAbsolutePath()))
        root.mkdir(parents=True, exist_ok=True)
        return root
    except Exception as exc:
        raise AndroidUriServisiHatasi("Files klasörü alınamadı.") from exc