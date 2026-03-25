# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/root_paketi/root/root_akisi/gecis_reklami_on_yukleme/gecis_reklami_on_yukleme.py

ROL:
- Root katmanında geçiş reklamı (interstitial) ön yükleme akışını yönetir
- Reklam servisini lazy resolve eder ve cache'ler
- Reklam yükleme / hazır olma / gösterme akışını merkezi hale getirir
- UI akışını bloklamadan arka planda preload çalıştırır
- Reklam hazır değilse fail-soft davranır

MİMARİ:
- Bu modül mixin mantığıyla çalışır
- Reklam servisi doğrudan import edilmez (lazy resolve)
- Services katmanı üzerinden reklam yöneticisi bulunur
- Method lookup ve servis referansı cache'lenir
- Tekrarlı preload çağrıları kontrol altına alınır

BEKLENEN ROOT ALANLARI:
- self.services

BEKLENEN SERVICES API (esnek):
- get_ad_manager / ad_manager / reklam_yoneticisi
- preload_interstitial / load_interstitial
- is_interstitial_ready / interstitial_ready
- show_interstitial

NOTLAR:
- Bu modül sadece preload + show akışını yönetir
- AdMob / SDK detayları services tarafında kalır
- Network ve SDK hataları swallow edilir
- UI thread bloklanmaz

SURUM: 1
TARIH: 2026-03-24
IMZA: FY.
"""

from __future__ import annotations

import threading


class RootGecisReklamiOnYuklemeMixin:

    # =========================================================
    # CACHE
    # =========================================================
    def _ensure_ad_cache(self):
        try:
            if not hasattr(self, "_ad_cache"):
                self._ad_cache = {}
        except Exception:
            pass

    def _cache_get(self, key, default=None):
        try:
            self._ensure_ad_cache()
            return self._ad_cache.get(key, default)
        except Exception:
            return default

    def _cache_set(self, key, value):
        try:
            self._ensure_ad_cache()
            self._ad_cache[key] = value
        except Exception:
            pass

    def _ad_cache_temizle(self):
        try:
            self._ad_cache = {}
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

    def _resolve_services(self):
        try:
            cached = self._cache_get("services_obj", None)
            if cached is not None:
                return cached

            services = self._safe_getattr("services", None)
            if services is not None:
                self._cache_set("services_obj", services)
            return services
        except Exception:
            return None

    def _resolve_ad_manager(self):
        """
        Services üzerinden reklam yöneticisini bulur (lazy + cache)
        """
        try:
            cached = self._cache_get("ad_manager", None)
            if cached is not None:
                return cached
        except Exception:
            pass

        services = self._resolve_services()
        if services is None:
            return None

        manager = None

        try:
            for name in (
                "get_ad_manager",
                "ad_manager",
                "reklam_yoneticisi",
            ):
                attr = getattr(services, name, None)

                if callable(attr):
                    manager = attr()
                elif attr is not None:
                    manager = attr

                if manager:
                    break
        except Exception:
            manager = None

        if manager:
            self._cache_set("ad_manager", manager)

        return manager

    def _resolve_ad_method(self, manager, method_names):
        """
        Reklam yöneticisi üzerinde metod bulur ve cache'ler
        """
        if manager is None:
            return None

        try:
            cache_key = f"ad_method::{id(manager)}::{method_names}"
            cached = self._cache_get(cache_key, None)
            if cached is not None:
                return cached
        except Exception:
            cache_key = None

        found = None

        try:
            for name in method_names:
                method = getattr(manager, name, None)
                if callable(method):
                    found = method
                    break
        except Exception:
            found = None

        try:
            if cache_key and found:
                self._cache_set(cache_key, found)
        except Exception:
            pass

        return found

    # =========================================================
    # PRELOAD
    # =========================================================
    def _preload_interstitial(self):
        """
        Geçiş reklamını arka planda yükler
        """
        if self._cache_get("preloading", False):
            return

        self._cache_set("preloading", True)

        def worker():
            try:
                manager = self._resolve_ad_manager()
                if manager is None:
                    return

                load = self._resolve_ad_method(
                    manager,
                    ("preload_interstitial", "load_interstitial"),
                )
                if callable(load):
                    load()

            except Exception:
                pass
            finally:
                self._cache_set("preloading", False)

        threading.Thread(target=worker, daemon=True).start()

    # =========================================================
    # READY CHECK
    # =========================================================
    def _is_interstitial_ready(self) -> bool:
        try:
            manager = self._resolve_ad_manager()
            if manager is None:
                return False

            check = self._resolve_ad_method(
                manager,
                ("is_interstitial_ready", "interstitial_ready"),
            )
            if callable(check):
                return bool(check())

        except Exception:
            pass

        return False

    # =========================================================
    # SHOW
    # =========================================================
    def _show_interstitial_if_ready(self) -> bool:
        """
        Reklam hazırsa gösterir
        """
        try:
            if not self._is_interstitial_ready():
                return False

            manager = self._resolve_ad_manager()
            if manager is None:
                return False

            show = self._resolve_ad_method(
                manager,
                ("show_interstitial",),
            )
            if callable(show):
                show()
                return True

        except Exception:
            pass

        return False

    # =========================================================
    # FULL FLOW
    # =========================================================
    def _try_show_interstitial_with_fallback(self) -> bool:
        """
        Reklam göster, gösteremezsen preload başlat
        """
        try:
            if self._show_interstitial_if_ready():
                return True
        except Exception:
            pass

        # fallback → preload
        try:
            self._preload_interstitial()
        except Exception:
            pass

        return False