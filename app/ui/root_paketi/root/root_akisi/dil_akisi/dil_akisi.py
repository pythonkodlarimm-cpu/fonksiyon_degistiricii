# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/root_paketi/root/root_akisi/dil_akisi/dil_akisi.py

ROL:
- Root katmanında dil (i18n) akışını yöneten merkezi mixin'dir
- Dil değiştirme, mevcut dili alma ve çeviri erişimini tek noktada toplar
- Services üzerinden dil yöneticisine erişir (doğrudan import yapmaz)
- Runtime lazy resolve + cache ile tekrar eden lookup maliyetini azaltır
- UI güncelleme tetiklerini merkezi ve güvenli şekilde yönetir

MİMARİ:
- Bu modül mixin mantığıyla çalışır
- Import-level lazy import yapılmaz; runtime lazy resolve + cache uygulanır
- Services nesnesi ve methodları cache içine alınır
- Root methodları (örn: refresh, rebuild vb.) cache'lenir
- Fail-soft yaklaşım: hata durumunda uygulama akışı kırılmaz

BEKLENEN ROOT ALANLARI:
- self.services

BEKLENEN SERVICES API (opsiyonel varyasyonlar desteklenir):
- dil_yoneticisi()
    -> yonetici.set_lang / dil_degistir / set_language
    -> yonetici.get_lang / dil / current_lang
    -> yonetici.translate / cevir / t

BEKLENEN ROOT METODLARI (opsiyonel):
- refresh_ui
- rebuild_ui
- on_language_changed

NOTLAR:
- Bu modül yalnızca dil akışını yönetir
- UI çizmez
- Disk yazımı yapmaz
- Çoklu API varyasyonları method-first yaklaşımıyla desteklenir

SURUM: 1
TARIH: 2026-03-24
IMZA: FY.
"""

from __future__ import annotations

import traceback


class RootDilAkisiMixin:
    """
    Root katmanında dil akışını yöneten mixin.
    """

    # =========================================================
    # CACHE
    # =========================================================
    def _ensure_dil_cache(self):
        try:
            if not hasattr(self, "_dil_cache"):
                self._dil_cache = {}
        except Exception:
            pass

    def _cache_get(self, key: str, default=None):
        try:
            self._ensure_dil_cache()
            return self._dil_cache.get(key, default)
        except Exception:
            return default

    def _cache_set(self, key: str, value):
        try:
            self._ensure_dil_cache()
            self._dil_cache[key] = value
        except Exception:
            pass

    def _cache_clear(self):
        try:
            self._dil_cache = {}
        except Exception:
            pass

    # =========================================================
    # INTERNAL HELPERS
    # =========================================================
    def _safe_getattr(self, name: str, default=None):
        try:
            return getattr(self, name, default)
        except Exception:
            return default

    def _resolve_root_method(self, method_name: str):
        cache_key = f"root::{id(self)}::{method_name}"

        cached = self._cache_get(cache_key, None)
        if cached is not None:
            return cached

        try:
            method = getattr(self, method_name, None)
            if callable(method):
                self._cache_set(cache_key, method)
                return method
        except Exception:
            pass

        return None

    def _resolve_services(self):
        cached = self._cache_get("services", None)
        if cached is not None:
            return cached

        try:
            services = self._safe_getattr("services", None)
            if services is not None:
                self._cache_set("services", services)
            return services
        except Exception:
            return None

    def _resolve_services_method(self, method_name: str):
        services = self._resolve_services()
        if services is None:
            return None

        cache_key = f"services::{id(services)}::{method_name}"

        cached = self._cache_get(cache_key, None)
        if cached is not None:
            return cached

        try:
            method = getattr(services, method_name, None)
            if callable(method):
                self._cache_set(cache_key, method)
                return method
        except Exception:
            pass

        return None

    def _call_first_available(self, obj, names: tuple[str, ...], *args, **kwargs):
        if obj is None:
            return False, None

        try:
            for name in names:
                fn = getattr(obj, name, None)
                if callable(fn):
                    return True, fn(*args, **kwargs)
        except Exception:
            return False, None

        return False, None

    # =========================================================
    # DIL YONETICISI
    # =========================================================
    def _dil_yoneticisi(self):
        """
        Services üzerinden dil yöneticisini alır (lazy + cache).
        """
        cached = self._cache_get("dil_yoneticisi", None)
        if cached is not None:
            return cached

        try:
            method = self._resolve_services_method("dil_yoneticisi")
            if callable(method):
                yonetici = method()
                if yonetici is not None:
                    self._cache_set("dil_yoneticisi", yonetici)
                return yonetici
        except Exception:
            pass

        return None

    # =========================================================
    # PUBLIC API
    # =========================================================
    def get_current_language(self) -> str:
        """
        Mevcut dili döndürür.
        """
        yonetici = self._dil_yoneticisi()
        if yonetici is None:
            return ""

        try:
            called, value = self._call_first_available(
                yonetici,
                ("get_lang", "dil", "current_lang"),
            )
            if called:
                return str(value or "")
        except Exception:
            pass

        return ""

    def set_language(self, lang_code: str) -> bool:
        """
        Dili değiştirir ve UI güncellemesini tetikler.
        """
        yonetici = self._dil_yoneticisi()
        if yonetici is None:
            return False

        try:
            called, _ = self._call_first_available(
                yonetici,
                ("set_lang", "dil_degistir", "set_language"),
                str(lang_code or ""),
            )
            if not called:
                return False

            # cache invalidate
            self._cache_clear()

            # UI refresh
            self._notify_language_changed()

            return True

        except Exception:
            print("[ROOT_DIL_AKISI] Dil değiştirme başarısız.")
            print(traceback.format_exc())
            return False

    def translate(self, key: str, default: str = "") -> str:
        """
        Çeviri metni döndürür.
        """
        yonetici = self._dil_yoneticisi()
        if yonetici is None:
            return default or key

        try:
            called, value = self._call_first_available(
                yonetici,
                ("translate", "cevir", "t"),
                key,
                default,
            )
            if called:
                return str(value or default or key)
        except Exception:
            pass

        return default or key

    # kısa alias (root._m)
    def _m(self, key: str, default: str = "") -> str:
        return self.translate(key, default)

    # =========================================================
    # UI NOTIFY
    # =========================================================
    def _notify_language_changed(self):
        """
        Dil değişimi sonrası root UI güncellemesini tetikler.
        """
        try:
            for name in (
                "on_language_changed",
                "refresh_ui",
                "rebuild_ui",
            ):
                method = self._resolve_root_method(name)
                if callable(method):
                    try:
                        method()
                    except Exception:
                        continue
        except Exception:
            pass