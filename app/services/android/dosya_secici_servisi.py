# -*- coding: utf-8 -*-
"""
DOSYA: app/services/android/dosya_secici_servisi.py

ROL:
- Android SAF dosya seçicisini açar
- Kullanıcı seçimi sonrası content:// URI sonucunu callback ile döndürür
- Son klasör başlangıç URI desteği için intent'e EXTRA_INITIAL_URI ekleyebilir

MİMARİ:
- Android özel servis
- Lazy import dostu
- Callback tabanlı
- Deterministik davranır
- Geriye uyumluluk katmanı içermez

API UYUMLULUK:
- Android API 35 uyumlu
- SAF / Scoped Storage uyumlu
- AndroidX ile çakışmaz

NOT:
- Bazı geliştirme ortamlarında android.activity.bind tabanlı activity result
  callback bağlama desteği çalışmayabilir. Bu durumda UI katmanı geliştirici
  popup dosya seçici moduna düşmelidir.

SURUM: 3
TARIH: 2026-03-28
IMZA: FY.
"""

from __future__ import annotations

from typing import Callable

from kivy.utils import platform


class AndroidDosyaSeciciServisiHatasi(ValueError):
    """
    Android dosya seçici işlemlerinde oluşan kontrollü hata.
    """


_PICKER_REQUEST_CODE = 7342
_ACTIVITY_BIND_EDILDI = False
_SECIM_CALLBACK: Callable[[str], None] | None = None


def _ensure_android() -> None:
    """
    Kodun yalnızca Android ortamında çalışmasını garanti eder.
    """
    if platform != "android":
        raise AndroidDosyaSeciciServisiHatasi(
            "Bu servis yalnızca Android ortamında kullanılabilir."
        )


def _android_siniflari():
    """
    Gerekli Android sınıflarını hazırlar.
    """
    _ensure_android()

    try:
        from jnius import autoclass, cast

        Intent = autoclass("android.content.Intent")
        Activity = autoclass("android.app.Activity")
        PythonActivity = autoclass("org.kivy.android.PythonActivity")
        DocumentsContract = autoclass("android.provider.DocumentsContract")

        activity = cast("android.app.Activity", PythonActivity.mActivity)
        if activity is None:
            raise AndroidDosyaSeciciServisiHatasi("Android activity alınamadı.")

        return {
            "Intent": Intent,
            "Activity": Activity,
            "DocumentsContract": DocumentsContract,
            "activity": activity,
        }

    except AndroidDosyaSeciciServisiHatasi:
        raise
    except Exception as exc:
        raise AndroidDosyaSeciciServisiHatasi(
            "Android picker sınıfları yüklenemedi."
        ) from exc


def _activity_result_bagla() -> None:
    """
    Android activity result callback'ini bağlar.
    """
    global _ACTIVITY_BIND_EDILDI

    if _ACTIVITY_BIND_EDILDI:
        return

    try:
        from android.activity import bind

        bind(on_activity_result=_on_activity_result)
        _ACTIVITY_BIND_EDILDI = True
    except Exception as exc:
        raise AndroidDosyaSeciciServisiHatasi(
            "Android activity result callback bağlanamadı."
        ) from exc


def _callback_guvenli_cagir(
    callback: Callable[[str], None] | None,
    value: str,
) -> None:
    """
    Callback'i güvenli biçimde çağırır.
    """
    if callback is None:
        return

    try:
        callback(str(value or "").strip())
    except Exception:
        pass


def _on_activity_result(request_code, result_code, intent) -> None:
    """
    SAF picker sonucunu yakalar ve callback'e iletir.
    """
    global _SECIM_CALLBACK

    try:
        req = int(request_code)
    except Exception:
        return

    if req != _PICKER_REQUEST_CODE:
        return

    callback = _SECIM_CALLBACK
    _SECIM_CALLBACK = None

    if callback is None:
        return

    try:
        ctx = _android_siniflari()
        Activity = ctx["Activity"]

        if int(result_code) != int(Activity.RESULT_OK):
            _callback_guvenli_cagir(callback, "")
            return

        if intent is None:
            _callback_guvenli_cagir(callback, "")
            return

        data = intent.getData()
        if data is None:
            _callback_guvenli_cagir(callback, "")
            return

        uri_str = str(data.toString() or "").strip()
        _callback_guvenli_cagir(callback, uri_str)

    except Exception:
        _callback_guvenli_cagir(callback, "")


def open_file_picker(
    on_result: Callable[[str], None],
    *,
    initial_uri: str | None = None,
    mime_types: list[str] | None = None,
) -> None:
    """
    Android SAF dosya seçicisini açar.

    Args:
        on_result:
            content:// URI veya boş string dönen callback
        initial_uri:
            Varsa picker başlangıç URI'si
        mime_types:
            İzin verilen mime type listesi
    """
    global _SECIM_CALLBACK

    if not callable(on_result):
        raise AndroidDosyaSeciciServisiHatasi("Geçerli callback verilmedi.")

    ctx = _android_siniflari()
    Intent = ctx["Intent"]
    DocumentsContract = ctx["DocumentsContract"]
    activity = ctx["activity"]

    _activity_result_bagla()
    _SECIM_CALLBACK = on_result

    try:
        intent = Intent(Intent.ACTION_OPEN_DOCUMENT)
        intent.addCategory(Intent.CATEGORY_OPENABLE)
        intent.setType("*/*")

        mime_list = mime_types or [
            "text/x-python",
            "text/plain",
            "application/json",
            "*/*",
        ]

        if len(mime_list) > 1:
            intent.putExtra(Intent.EXTRA_MIME_TYPES, mime_list)

        intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
        intent.addFlags(Intent.FLAG_GRANT_WRITE_URI_PERMISSION)
        intent.addFlags(Intent.FLAG_GRANT_PERSISTABLE_URI_PERMISSION)

        initial_raw = str(initial_uri or "").strip()
        if initial_raw.startswith("content://"):
            try:
                from app.services.android.uri_servisi import parse_uri

                parsed_uri = parse_uri(initial_raw)
                if parsed_uri is not None:
                    intent.putExtra(
                        DocumentsContract.EXTRA_INITIAL_URI,
                        parsed_uri,
                    )
            except Exception:
                pass

        activity.startActivityForResult(intent, _PICKER_REQUEST_CODE)

    except Exception as exc:
        _SECIM_CALLBACK = None
        raise AndroidDosyaSeciciServisiHatasi(
            "Android dosya seçici açılamadı."
        ) from exc