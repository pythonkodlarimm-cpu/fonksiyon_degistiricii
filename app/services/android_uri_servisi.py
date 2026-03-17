# -*- coding: utf-8 -*-
"""
DOSYA: app/services/android_uri_servisi.py

ROL:
- Android document/content URI işlemlerini yönetmek
- Persistable URI izni almak
- URI üzerinden metin okumak ve yazmak
- Android uygulama içi cache/files klasörlerini almak

API 34 UYUMLULUK NOTU:
- Bu servis Android SAF (Storage Access Framework) mantığına göre çalışır.
- API 34 hedeflenerek güvenli activity/resolver kontrolleri eklenmiştir.
- content:// URI erişiminde persistable permission akışı korunmuştur.
- Doğrudan dosya yolu yerine URI tabanlı erişim tercih edilir.
"""

from __future__ import annotations

from pathlib import Path

from kivy.utils import platform


class AndroidUriServisiHatasi(ValueError):
    """Android URI işlemleri sırasında oluşan kontrollü hata."""


def is_android_document_uri(value: str) -> bool:
    """
    Verilen değerin Android content URI olup olmadığını kontrol eder.

    API 34 uyumluluk notu:
    - SAF üzerinden gelen seçimler tipik olarak content:// ile başlar.
    """
    return str(value or "").strip().startswith("content://")


def _ensure_android() -> None:
    """
    Servisin yalnızca Android'de kullanılmasını garanti eder.

    API 34 uyumluluk notu:
    - Android dışı ortamlarda pyjnius ve Android sınıfları güvenli şekilde engellenir.
    """
    if platform != "android":
        raise AndroidUriServisiHatasi("Bu servis yalnızca Android'de çalışır.")


def _classes():
    """
    Android sınıflarını ve gerekli çalışma nesnelerini yükler.

    Dönenler:
    - Uri
    - Intent
    - activity
    - resolver

    API 34 uyumluluk notu:
    - Activity ve ContentResolver null gelirse kontrollü hata üretilir.
    """
    _ensure_android()
    try:
        from jnius import autoclass, cast  # type: ignore

        Uri = autoclass("android.net.Uri")
        Intent = autoclass("android.content.Intent")
        PythonActivity = autoclass("org.kivy.android.PythonActivity")

        current_activity = cast("android.app.Activity", PythonActivity.mActivity)
        if current_activity is None:
            raise AndroidUriServisiHatasi("Geçerli Android activity alınamadı.")

        resolver = current_activity.getContentResolver()
        if resolver is None:
            raise AndroidUriServisiHatasi("ContentResolver alınamadı.")

        return {
            "Uri": Uri,
            "Intent": Intent,
            "activity": current_activity,
            "resolver": resolver,
        }
    except AndroidUriServisiHatasi:
        raise
    except Exception as exc:
        raise AndroidUriServisiHatasi("Android sınıfları yüklenemedi.") from exc


def parse_uri(uri_str: str):
    """
    URI metnini Android Uri nesnesine çevirir.

    API 34 uyumluluk notu:
    - Yalnızca SAF/content tabanlı URI'ler kabul edilir.
    """
    raw = str(uri_str or "").strip()
    if not raw or not is_android_document_uri(raw):
        raise AndroidUriServisiHatasi("Geçerli bir Android document URI değil.")

    try:
        return _classes()["Uri"].parse(raw)
    except Exception as exc:
        raise AndroidUriServisiHatasi("URI parse edilemedi.") from exc


def take_persistable_permission(intent, uri_str: str) -> None:
    """
    Verilen URI için persistable erişim izni alır.

    Parametreler:
    - intent: Android seçim intent'i
    - uri_str: content:// URI

    API 34 uyumluluk notu:
    - SAF ile gelen URI izinleri uygulama yeniden açıldığında da korunabilsin diye
      takePersistableUriPermission çağrısı yapılır.
    - Flag bilgisi eksikse güvenli fallback olarak READ izni kullanılır.
    """
    if intent is None:
        raise AndroidUriServisiHatasi("Intent boş.")

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
        raise AndroidUriServisiHatasi("Persistable URI izni alınamadı.") from exc


def get_display_name(uri_str: str) -> str:
    """
    URI'nin kullanıcıya gösterilecek adını döndürür.

    API 34 uyumluluk notu:
    - SAF sağlayıcılarından _display_name okunmaya çalışılır.
    - Bulunamazsa URI son parçası fallback olarak kullanılır.
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
    """
    URI'nin MIME türünü döndürür.

    API 34 uyumluluk notu:
    - ContentResolver.getType üzerinden güvenli sorgu yapılır.
    """
    try:
        return str(_classes()["resolver"].getType(parse_uri(uri_str)) or "").strip()
    except Exception:
        return ""


def read_text(uri_str: str, encoding: str = "utf-8") -> str:
    """
    URI içeriğini metin olarak okur.

    Parametreler:
    - uri_str: content:// URI
    - encoding: çözümlenecek metin kodlaması

    API 34 uyumluluk notu:
    - SAF üzerinden InputStream açılır.
    - Doğrudan dosya yolu değil, resolver tabanlı erişim kullanılır.
    """
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
        raise AndroidUriServisiHatasi(
            f"URI içeriği '{encoding}' ile çözümlenemedi."
        ) from exc
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
    """
    URI içeriğine metin yazar.

    Parametreler:
    - uri_str: content:// URI
    - content: yazılacak metin
    - encoding: metin kodlaması

    API 34 uyumluluk notu:
    - SAF üzerinden OutputStream açılır.
    - Yazma işlemi doğrudan path ile değil resolver üzerinden yapılır.
    """
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
    """
    Uygulamanın cache klasörünü Path olarak döndürür.

    API 34 uyumluluk notu:
    - Uygulama sandbox içindeki güvenli cache dizini kullanılır.
    """
    try:
        activity = _classes()["activity"]
        if activity is None:
            raise AndroidUriServisiHatasi("Geçerli Android activity alınamadı.")

        cache_dir = activity.getCacheDir()
        if cache_dir is None:
            raise AndroidUriServisiHatasi("Cache klasörü alınamadı.")

        root = Path(str(cache_dir.getAbsolutePath()))
        root.mkdir(parents=True, exist_ok=True)
        return root

    except AndroidUriServisiHatasi:
        raise
    except Exception as exc:
        raise AndroidUriServisiHatasi("Cache klasörü alınamadı.") from exc


def get_app_files_dir() -> Path:
    """
    Uygulamanın files klasörünü Path olarak döndürür.

    API 34 uyumluluk notu:
    - Uygulama sandbox içindeki güvenli files dizini kullanılır.
    """
    try:
        activity = _classes()["activity"]
        if activity is None:
            raise AndroidUriServisiHatasi("Geçerli Android activity alınamadı.")

        files_dir = activity.getFilesDir()
        if files_dir is None:
            raise AndroidUriServisiHatasi("Files klasörü alınamadı.")

        root = Path(str(files_dir.getAbsolutePath()))
        root.mkdir(parents=True, exist_ok=True)
        return root

    except AndroidUriServisiHatasi:
        raise
    except Exception as exc:
        raise AndroidUriServisiHatasi("Files klasörü alınamadı.") from exc