# -*- coding: utf-8 -*-
"""
DOSYA: app/services/android/uri_servisi.py

ROL:
- Android document URI erişimini yönetir
- content:// URI çözümleme, metadata, okuma, yazma ve kalıcı izin akışlarını sağlar
- Android dosya seçici (SAF) ile gelen URI'lerin güvenli kullanımını merkezileştirir

MİMARİ:
- Type-safe module cache
- Deterministik davranış
- Daha temiz lazy çözümleme
- Gereksiz fallback içermez
- Micro-perf iyileştirme içerir
- Sıfır belirsizlik
- Geriye uyumluluk katmanı içermez

NOTLAR:
- Yalnızca Android ortamında aktif çalışır
- content:// URI akışları için tasarlanmıştır
- Path tabanlı normal dosya erişimi bu modülün sorumluluğunda değildir

API UYUMLULUK:
- Android API 35 uyumlu
- AndroidX uyumlu
- Pydroid3 / Kivy / Pyjnius uyumlu

SURUM: 4
TARIH: 2026-03-28
IMZA: FY.
"""

from __future__ import annotations

from pathlib import Path
from typing import TypedDict, cast

from kivy.utils import platform


# =========================================================
# HATA
# =========================================================
class AndroidUriServisiHatasi(ValueError):
    """
    Android URI işlemleri sırasında oluşan kontrollü hata.
    """


# =========================================================
# TYPE
# =========================================================
class _AndroidCtx(TypedDict):
    Uri: type
    Intent: type
    activity: object
    resolver: object


# =========================================================
# CACHE
# =========================================================
_ANDROID_CTX: _AndroidCtx | None = None


# =========================================================
# INTERNAL
# =========================================================
def _ensure_android() -> None:
    """
    Kodun yalnızca Android ortamında çalışmasını garanti eder.
    """
    if platform != "android":
        raise AndroidUriServisiHatasi(
            "Bu servis yalnızca Android ortamında kullanılabilir."
        )


def _classes() -> _AndroidCtx:
    """
    Android sınıflarını ve temel context nesnelerini cache'li biçimde döndürür.
    """
    global _ANDROID_CTX

    cached = _ANDROID_CTX
    if cached is not None:
        return cached

    _ensure_android()

    try:
        from jnius import autoclass, cast as jcast
    except Exception as exc:
        raise AndroidUriServisiHatasi(
            "Pyjnius sınıfları yüklenemedi."
        ) from exc

    try:
        Uri = autoclass("android.net.Uri")
        Intent = autoclass("android.content.Intent")
        PythonActivity = autoclass("org.kivy.android.PythonActivity")

        activity = jcast("android.app.Activity", PythonActivity.mActivity)
        if activity is None:
            raise AndroidUriServisiHatasi("Android activity alınamadı.")

        resolver = activity.getContentResolver()
        if resolver is None:
            raise AndroidUriServisiHatasi("Android ContentResolver alınamadı.")

        ctx: _AndroidCtx = {
            "Uri": Uri,
            "Intent": Intent,
            "activity": activity,
            "resolver": resolver,
        }
        _ANDROID_CTX = ctx
        return ctx

    except AndroidUriServisiHatasi:
        raise
    except Exception as exc:
        raise AndroidUriServisiHatasi(
            "Android URI sınıfları hazırlanamadı."
        ) from exc


def cache_temizle() -> None:
    """
    Android class/activity/resolver cache'ini temizler.
    """
    global _ANDROID_CTX
    _ANDROID_CTX = None


def _normalize_uri_str(uri_str: str) -> str:
    """
    URI metnini normalize eder ve boş olmasını engeller.
    """
    raw = str(uri_str or "").strip()
    if not raw:
        raise AndroidUriServisiHatasi("URI boş olamaz.")
    return raw


def _safe_close(obj: object | None) -> None:
    """
    Android/Java nesnelerini güvenli biçimde kapatır.
    """
    if obj is None:
        return

    try:
        closer = getattr(obj, "close", None)
        if callable(closer):
            closer()
    except Exception:
        pass


def _read_all_bytes(stream) -> bytes:
    """
    InputStream içeriğini buffer ile okur.
    """
    try:
        from jnius import autoclass
    except Exception as exc:
        raise AndroidUriServisiHatasi(
            "ByteArrayOutputStream sınıfı yüklenemedi."
        ) from exc

    ByteArrayOutputStream = autoclass("java.io.ByteArrayOutputStream")
    baos = None

    try:
        baos = ByteArrayOutputStream()
        chunk_size = 8192

        while True:
            chunk = stream.read()
            if chunk == -1:
                break
            baos.write(int(chunk) & 0xFF)

        data = baos.toByteArray()
        return bytes(data)

    except AndroidUriServisiHatasi:
        raise
    except Exception as exc:
        raise AndroidUriServisiHatasi(
            "Stream veri okuma hatası."
        ) from exc
    finally:
        _safe_close(baos)


# =========================================================
# URI
# =========================================================
def is_android_document_uri(value: str) -> bool:
    """
    Verilen değerin Android document/content URI olup olmadığını döndürür.
    """
    return str(value or "").strip().startswith("content://")


def parse_uri(uri_str: str):
    """
    content:// URI metnini Android Uri nesnesine çevirir.
    """
    raw = _normalize_uri_str(uri_str)

    if not is_android_document_uri(raw):
        raise AndroidUriServisiHatasi("Geçersiz Android document URI.")

    try:
        return _classes()["Uri"].parse(raw)
    except Exception as exc:
        raise AndroidUriServisiHatasi("URI parse edilemedi.") from exc


# =========================================================
# PERMISSION
# =========================================================
def take_persistable_permission(intent, uri_str: str) -> None:
    """
    Android document URI için kalıcı okuma/yazma izni almaya çalışır.
    """
    if intent is None:
        raise AndroidUriServisiHatasi("Intent boş olamaz.")

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
        raise AndroidUriServisiHatasi(
            "Kalıcı URI izni alınamadı."
        ) from exc


# =========================================================
# METADATA
# =========================================================
def get_display_name(uri_str: str) -> str:
    """
    Android URI için görünen dosya adını döndürür.
    """
    ctx = _classes()
    resolver = ctx["resolver"]
    uri = parse_uri(uri_str)

    cursor = None

    try:
        cursor = resolver.query(uri, None, None, None, None)

        if cursor is not None and cursor.moveToFirst():
            idx = cursor.getColumnIndex("_display_name")
            if idx >= 0:
                value = cursor.getString(idx)
                if value:
                    return str(value).strip()

    except Exception as exc:
        raise AndroidUriServisiHatasi(
            "URI görünen adı alınamadı."
        ) from exc
    finally:
        _safe_close(cursor)

    raw = _normalize_uri_str(uri_str)
    return raw.rsplit("/", 1)[-1]


def get_mime_type(uri_str: str) -> str:
    """
    Android URI için MIME type döndürür.
    """
    try:
        value = _classes()["resolver"].getType(parse_uri(uri_str))
        return str(value or "").strip()
    except Exception as exc:
        raise AndroidUriServisiHatasi(
            "URI mime type alınamadı."
        ) from exc


# =========================================================
# IO
# =========================================================
def read_text(uri_str: str, encoding: str = "utf-8") -> str:
    """
    Android document URI üzerinden metin okur.
    """
    resolver = _classes()["resolver"]
    uri = parse_uri(uri_str)

    stream = None

    try:
        stream = resolver.openInputStream(uri)
        if stream is None:
            raise AndroidUriServisiHatasi("Input stream açılamadı.")

        data = _read_all_bytes(stream)
        return data.decode(encoding)

    except UnicodeDecodeError as exc:
        raise AndroidUriServisiHatasi("Metin decode edilemedi.") from exc
    except AndroidUriServisiHatasi:
        raise
    except Exception as exc:
        raise AndroidUriServisiHatasi("URI metin okuma hatası.") from exc
    finally:
        _safe_close(stream)


def write_text(uri_str: str, content: str, encoding: str = "utf-8") -> None:
    """
    Android document URI üzerine metin yazar.
    """
    resolver = _classes()["resolver"]
    uri = parse_uri(uri_str)

    stream = None

    try:
        try:
            stream = resolver.openOutputStream(uri, "wt")
        except Exception:
            stream = resolver.openOutputStream(uri, "w")

        if stream is None:
            raise AndroidUriServisiHatasi("Output stream açılamadı.")

        payload = str(content or "").encode(encoding)
        stream.write(payload)
        stream.flush()

    except AndroidUriServisiHatasi:
        raise
    except Exception as exc:
        raise AndroidUriServisiHatasi("URI metin yazma hatası.") from exc
    finally:
        _safe_close(stream)


# =========================================================
# APP DIR
# =========================================================
def get_app_cache_dir() -> Path:
    """
    Android uygulama cache dizinini döndürür.
    """
    activity = _classes()["activity"]

    try:
        path = activity.getCacheDir()
        root = Path(str(path.getAbsolutePath()))
        root.mkdir(parents=True, exist_ok=True)
        return root
    except Exception as exc:
        raise AndroidUriServisiHatasi(
            "App cache dizini alınamadı."
        ) from exc


def get_app_files_dir() -> Path:
    """
    Android uygulama files dizinini döndürür.
    """
    activity = _classes()["activity"]

    try:
        path = activity.getFilesDir()
        root = Path(str(path.getAbsolutePath()))
        root.mkdir(parents=True, exist_ok=True)
        return root
    except Exception as exc:
        raise AndroidUriServisiHatasi(
            "App files dizini alınamadı."
        ) from exc