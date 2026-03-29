# -*- coding: utf-8 -*-
"""
DOSYA: app/services/android/yoneticisi.py

ROL:
- Android klasörü altındaki servisler için tek giriş noktası sağlar
- UI ve diğer katmanların alt servis detaylarını bilmesini engeller
- Android URI ve picker servislerini merkezden yönetir

MİMARİ:
- Lazy import + strict cache
- Modül ve fonksiyon referansları cache'lenir
- Deterministik davranır
- Type güvenliği yüksektir
- Geriye uyumluluk katmanı içermez

API UYUMLULUK:
- Android API 35 uyumludur
- Scoped storage / SAF uyumludur
- AndroidX uyumlu yapı ile çakışmaz

SURUM: 4
TARIH: 2026-03-28
IMZA: FY.
"""

from __future__ import annotations

from pathlib import Path
from types import ModuleType
from typing import Any, Callable, Final


class AndroidYoneticisi:
    """
    Android servisleri için merkezi erişim yöneticisi.
    """

    __slots__ = (
        "_modul_cache",
        "_fonksiyon_cache",
    )

    URI_MODUL: Final[str] = "app.services.android.uri_servisi"
    PICKER_MODUL: Final[str] = "app.services.android.dosya_secici_servisi"

    def __init__(self) -> None:
        self._modul_cache: dict[str, ModuleType] = {}
        self._fonksiyon_cache: dict[tuple[str, str], Callable[..., Any]] = {}

    def cache_temizle(self) -> None:
        """
        Lazy import cache'lerini temizler.
        """
        self._modul_cache.clear()
        self._fonksiyon_cache.clear()

    def _modul_yukle(self, modul_yolu: str) -> ModuleType:
        """
        Modülü lazy import ile yükler ve cache'e alır.
        """
        cached = self._modul_cache.get(modul_yolu)
        if cached is not None:
            return cached

        module = __import__(modul_yolu, fromlist=["*"])
        self._modul_cache[modul_yolu] = module
        return module

    def _fonksiyon_getir(
        self,
        modul_yolu: str,
        fonksiyon_adi: str,
    ) -> Callable[..., Any]:
        """
        Modül içindeki çağrılabilir fonksiyonu getirir ve cache'ler.
        """
        key = (modul_yolu, fonksiyon_adi)

        cached = self._fonksiyon_cache.get(key)
        if cached is not None:
            return cached

        module = self._modul_yukle(modul_yolu)
        value = getattr(module, fonksiyon_adi, None)

        if value is None:
            raise AttributeError(f"{modul_yolu} içinde '{fonksiyon_adi}' bulunamadı.")

        if not callable(value):
            raise TypeError(f"{modul_yolu}.{fonksiyon_adi} çağrılabilir değil.")

        func = value
        self._fonksiyon_cache[key] = func
        return func

    def _cagir(
        self,
        modul_yolu: str,
        fonksiyon_adi: str,
        *args,
        **kwargs,
    ) -> Any:
        """
        Cache'lenmiş fonksiyonu çağırır.
        """
        func = self._fonksiyon_getir(modul_yolu, fonksiyon_adi)
        return func(*args, **kwargs)

    # =========================================================
    # URI
    # =========================================================
    def is_android_document_uri(self, value: str) -> bool:
        """
        Verilen değerin Android content URI olup olmadığını döndürür.
        """
        return bool(self._cagir(self.URI_MODUL, "is_android_document_uri", value))

    def parse_uri(self, uri_str: str) -> Any:
        """
        URI metnini Android Uri nesnesine çevirir.
        """
        return self._cagir(self.URI_MODUL, "parse_uri", uri_str)

    def take_persistable_permission(self, intent: Any, uri_str: str) -> None:
        """
        Android document URI için kalıcı izni almaya çalışır.
        """
        self._cagir(
            self.URI_MODUL,
            "take_persistable_permission",
            intent,
            uri_str,
        )

    def get_display_name(self, uri_str: str) -> str:
        """
        URI için görünen dosya adını döndürür.
        """
        return str(self._cagir(self.URI_MODUL, "get_display_name", uri_str))

    def get_mime_type(self, uri_str: str) -> str:
        """
        URI için MIME type döndürür.
        """
        return str(self._cagir(self.URI_MODUL, "get_mime_type", uri_str))

    def read_text(self, uri_str: str, encoding: str = "utf-8") -> str:
        """
        Android URI üzerinden metin okur.
        """
        return str(
            self._cagir(
                self.URI_MODUL,
                "read_text",
                uri_str,
                encoding=encoding,
            )
        )

    def write_text(
        self,
        uri_str: str,
        content: str,
        encoding: str = "utf-8",
    ) -> None:
        """
        Android URI üzerine metin yazar.
        """
        self._cagir(
            self.URI_MODUL,
            "write_text",
            uri_str,
            content,
            encoding=encoding,
        )

    def get_app_cache_dir(self) -> Path:
        """
        Android uygulama cache dizinini Path olarak döndürür.
        """
        result = self._cagir(self.URI_MODUL, "get_app_cache_dir")
        if not isinstance(result, Path):
            raise TypeError("get_app_cache_dir Path döndürmedi.")
        return result

    def get_app_files_dir(self) -> Path:
        """
        Android uygulama files dizinini Path olarak döndürür.
        """
        result = self._cagir(self.URI_MODUL, "get_app_files_dir")
        if not isinstance(result, Path):
            raise TypeError("get_app_files_dir Path döndürmedi.")
        return result

    # =========================================================
    # PICKER
    # =========================================================
    def open_file_picker(
        self,
        on_result: Callable[[str], None],
        *,
        initial_uri: str | None = None,
        mime_types: list[str] | None = None,
    ) -> None:
        """
        Android SAF dosya seçicisini açar.
        """
        self._cagir(
            self.PICKER_MODUL,
            "open_file_picker",
            on_result,
            initial_uri=initial_uri,
            mime_types=mime_types,
        )