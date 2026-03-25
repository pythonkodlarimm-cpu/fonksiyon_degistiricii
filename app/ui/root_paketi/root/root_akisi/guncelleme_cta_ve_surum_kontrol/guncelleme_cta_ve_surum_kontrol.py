# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/root_paketi/root/root_akisi/guncelleme_cta_ve_surum_kontrol/guncelleme_cta_ve_surum_kontrol.py

ROL:
- Root katmanında uygulama sürüm kontrolü ve güncelleme CTA (Call-To-Action) akışını yönetir
- Remote endpoint üzerinden sürüm bilgisi alır
- Mevcut sürüm ile karşılaştırma yapar
- Güncelleme varsa kullanıcıya CTA gösterir
- Güncelleme butonu / yönlendirme akışını tetikler
- Runtime tarafında lazy resolve ve cache kullanarak tekrar eden lookup maliyetini azaltır

MİMARİ:
- Bu modül mixin mantığıyla çalışır
- Network çağrısı minimum seviyede tutulur (cache ile)
- Root içindeki UI bileşenlerine direkt bağımlılık yoktur
- set_status_info, _m gibi root metodları cache ile resolve edilir
- Fail-soft yaklaşım uygulanır (network hatası UI'yı bozmaz)

BEKLENEN ROOT ALANLARI:
- self.app_version  (örn: "0.1.12")
- self.update_url   (opsiyonel)

BEKLENEN ROOT METODLARI:
- self.set_status_info(...)
- self._m(...)

NOTLAR:
- Network işlemi blocking yapılmaz (thread ile çalışır)
- Endpoint JSON formatı beklenir:
    {
        "version": "0.1.25",
        "force": false,
        "url": "https://..."
    }

SURUM: 1
TARIH: 2026-03-24
IMZA: FY.
"""

from __future__ import annotations

import threading
import json

from urllib.request import urlopen, Request


class RootGuncellemeCtaVeSurumKontrolMixin:

    # =========================================================
    # CACHE
    # =========================================================
    def _ensure_update_cache(self):
        if not hasattr(self, "_update_cache"):
            self._update_cache = {}

    def _cache_get(self, key, default=None):
        try:
            self._ensure_update_cache()
            return self._update_cache.get(key, default)
        except Exception:
            return default

    def _cache_set(self, key, value):
        try:
            self._ensure_update_cache()
            self._update_cache[key] = value
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
        try:
            cache_key = f"root_method::{method_name}"
            cached = self._cache_get(cache_key, None)
            if cached is not None:
                return cached

            method = getattr(self, method_name, None)
            if callable(method):
                self._cache_set(cache_key, method)
                return method
        except Exception:
            pass
        return None

    def _m_cached(self, key: str, default: str):
        try:
            m = self._resolve_root_method("_m")
            if callable(m):
                return str(m(key, default) or default)
        except Exception:
            pass
        return str(default)

    def _set_status_info_cached(self, msg: str, icon: str):
        try:
            fn = self._resolve_root_method("set_status_info")
            if callable(fn):
                fn(msg, icon)
        except Exception:
            pass

    # =========================================================
    # VERSION COMPARE
    # =========================================================
    def _version_to_tuple(self, version: str):
        try:
            return tuple(int(x) for x in str(version).split("."))
        except Exception:
            return (0,)

    def _is_newer_version(self, remote: str, local: str) -> bool:
        try:
            return self._version_to_tuple(remote) > self._version_to_tuple(local)
        except Exception:
            return False

    # =========================================================
    # NETWORK
    # =========================================================
    def _fetch_update_info(self, url: str):
        try:
            req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urlopen(req, timeout=5) as r:
                data = r.read().decode("utf-8")
                return json.loads(data)
        except Exception:
            return None

    # =========================================================
    # MAIN CHECK
    # =========================================================
    def _check_update_from_endpoint(self, *_args):
        """
        Update kontrolünü başlatır (thread içinde çalışır)
        """
        try:
            endpoint = self._safe_getattr("update_url", None)
            if not endpoint:
                return
        except Exception:
            return

        # cache check (aynı sessionda tekrar çağırma)
        if self._cache_get("checked_once", False):
            return

        self._cache_set("checked_once", True)

        def worker():
            try:
                data = self._fetch_update_info(endpoint)
                if not data:
                    return

                remote_version = str(data.get("version", "0"))
                force = bool(data.get("force", False))
                url = str(data.get("url", "") or endpoint)

                local_version = str(self._safe_getattr("app_version", "0"))

                if not self._is_newer_version(remote_version, local_version):
                    return

                # cache result
                self._cache_set("update_available", True)
                self._cache_set("update_url_final", url)
                self._cache_set("update_force", force)

                # UI bilgi
                self._set_status_info_cached(
                    self._m_cached("update_available", "Yeni sürüm mevcut."),
                    "update.png",
                )

            except Exception:
                pass

        threading.Thread(target=worker, daemon=True).start()

    # =========================================================
    # CTA ACTION
    # =========================================================
    def _open_update_url(self):
        """
        Güncelleme linkini açar
        """
        try:
            url = self._cache_get("update_url_final", None)
            if not url:
                return

            import webbrowser

            webbrowser.open(url)
        except Exception:
            pass

    def _is_update_available(self) -> bool:
        """
        Güncelleme var mı?
        """
        try:
            return bool(self._cache_get("update_available", False))
        except Exception:
            return False