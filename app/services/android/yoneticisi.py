# -*- coding: utf-8 -*-
"""
DOSYA: app/services/android/yoneticisi.py

ROL:
- Android klasörü altındaki servisler için tek giriş noktası sağlamak
- UI ve diğer katmanların alt servis detaylarını bilmesini önlemek
- Android URI ve özel izin servislerini merkezden yönetmek
- İleride Android'e özel yeni servisler eklendiğinde tek noktadan erişim sunmak

MİMARİ:
- Alt servisleri lazy import ile çağırır
- Android dışı ortamlarda güvenli davranır
- UI katmanı sadece bu yöneticiyi bilir
- Alt servislerin iç yapısını dış dünyadan saklar

API UYUMLULUK:
- API 35 uyumlu
- Scoped storage / SAF uyumlu
- AndroidX uyumlu yapı ile çakışmaz

SURUM: 1
TARIH: 2026-03-19
IMZA: FY.
"""

from __future__ import annotations

from pathlib import Path


class AndroidYoneticisi:
    # =========================================================
    # URI
    # =========================================================
    def is_android_document_uri(self, value: str) -> bool:
        from app.services.android.uri_servisi import is_android_document_uri
        return is_android_document_uri(value)

    def parse_uri(self, uri_str: str):
        from app.services.android.uri_servisi import parse_uri
        return parse_uri(uri_str)

    def take_persistable_permission(self, intent, uri_str: str) -> None:
        from app.services.android.uri_servisi import take_persistable_permission
        take_persistable_permission(intent, uri_str)

    def get_display_name(self, uri_str: str) -> str:
        from app.services.android.uri_servisi import get_display_name
        return get_display_name(uri_str)

    def get_mime_type(self, uri_str: str) -> str:
        from app.services.android.uri_servisi import get_mime_type
        return get_mime_type(uri_str)

    def read_text(self, uri_str: str, encoding: str = "utf-8") -> str:
        from app.services.android.uri_servisi import read_text
        return read_text(uri_str, encoding=encoding)

    def write_text(self, uri_str: str, content: str, encoding: str = "utf-8") -> None:
        from app.services.android.uri_servisi import write_text
        write_text(uri_str, content, encoding=encoding)

    def get_app_cache_dir(self) -> Path:
        from app.services.android.uri_servisi import get_app_cache_dir
        return get_app_cache_dir()

    def get_app_files_dir(self) -> Path:
        from app.services.android.uri_servisi import get_app_files_dir
        return get_app_files_dir()

    # =========================================================
    # OZEL IZIN
    # =========================================================
    def android_api_seviyesi(self) -> int:
        from app.services.android.ozel_izin_servisi import android_api_seviyesi
        return android_api_seviyesi()

    def tum_dosya_erisim_destekleniyor_mu(self) -> bool:
        from app.services.android.ozel_izin_servisi import tum_dosya_erisim_destekleniyor_mu
        return tum_dosya_erisim_destekleniyor_mu()

    def tum_dosya_erisim_izni_var_mi(self) -> bool:
        from app.services.android.ozel_izin_servisi import tum_dosya_erisim_izni_var_mi
        return tum_dosya_erisim_izni_var_mi()

    def tum_dosya_erisim_ayarlari_ac(self) -> None:
        from app.services.android.ozel_izin_servisi import tum_dosya_erisim_ayarlari_ac
        tum_dosya_erisim_ayarlari_ac()

    def uygulama_detay_ayarlari_ac(self) -> None:
        from app.services.android.ozel_izin_servisi import uygulama_detay_ayarlari_ac
        uygulama_detay_ayarlari_ac()