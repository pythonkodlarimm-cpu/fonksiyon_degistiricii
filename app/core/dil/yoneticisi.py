# -*- coding: utf-8 -*-
"""
DOSYA: app/core/dil/yoneticisi.py

ROL:
- Aktif dili yönetir
- Key çözümleme yapar (t)
- Fallback sistemi sağlar
- RTL kontrolü yapar
- Kalıcı dil ayarı (persist) yönetir

MİMARİ:
- Deterministik
- Strict cache
- Lazy yok (service zaten cache’li)
- Fail-safe fallback
- Micro-perf optimize

SURUM: 2
TARIH: 2026-03-28
IMZA: FY.
"""

from __future__ import annotations

from typing import Dict

from app.services.dil_servisi import DilServisi
from app.services.dil_ayar import (
    kayitli_dili_getir,
    dili_kaydet,
)


class DilYoneticisi:
    """
    Dil yönetim katmanı (core).
    """

    __slots__ = (
        "_service",
        "_current_lang",
        "_default_lang",
        "_rtl_set",
        "_cache",
    )

    def __init__(self, service: DilServisi, default_lang: str = "en") -> None:
        self._service = service
        self._default_lang = str(default_lang).strip().lower()

        self._rtl_set = {"ar", "fa", "he", "ur"}

        self._cache: Dict[str, dict] = {}

        # =========================================================
        # INITIAL LOAD (persist)
        # =========================================================
        saved = kayitli_dili_getir()

        if self._service.has_language(saved):
            self._current_lang = saved
        else:
            self._current_lang = self._default_lang

    # =========================================================
    # LANGUAGE
    # =========================================================
    def set_language(self, code: str) -> None:
        code = str(code or "").strip().lower()

        if not self._service.has_language(code):
            raise ValueError(f"Dil yok: {code}")

        if code == self._current_lang:
            return  # micro-perf (gereksiz write yok)

        self._current_lang = code
        dili_kaydet(code)

    def get_language(self) -> str:
        return self._current_lang

    def available_languages(self) -> Dict[str, dict]:
        return self._service.get_available_languages()

    # =========================================================
    # RTL
    # =========================================================
    def is_rtl(self) -> bool:
        return self._current_lang in self._rtl_set

    # =========================================================
    # INTERNAL CACHE
    # =========================================================
    def _get_lang_data(self, code: str) -> dict:
        data = self._cache.get(code)
        if data is None:
            data = self._service.get_language(code)
            self._cache[code] = data
        return data

    # =========================================================
    # TRANSLATE
    # =========================================================
    def t(self, key: str) -> str:
        key = str(key or "").strip()

        if not key:
            return ""

        # 1. aktif dil
        current = self._get_lang_data(self._current_lang)
        val = current.get(key)
        if isinstance(val, str):
            return val

        # 2. fallback (default)
        if self._current_lang != self._default_lang:
            default = self._get_lang_data(self._default_lang)
            val = default.get(key)
            if isinstance(val, str):
                return val

        # 3. final fallback
        return key