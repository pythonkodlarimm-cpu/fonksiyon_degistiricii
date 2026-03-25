# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/root_paketi/root/root_akisi/dil_yardimcilari/dil_yardimcilari.py

ROL:
- Root katmanındaki dil yardımcı işlevlerini tek modülde toplar
- ServicesYoneticisi üzerinden çeviri metni çözümleme akışını sağlar
- Dile bağlı widget'ların refresh/apply_language çağrılarını merkezi biçimde yürütür
- Root içindeki genel dil yenileme akışını güvenli ve fail-soft şekilde uygular
- Canvas, layout ve bağlı alt widget güncellemelerini sırayla tetikler

EKSTRA (OPTIMIZATION):
- Çeviri metinleri cache’lenir
- Widget method lookup cache uygulanır
- getattr maliyeti minimize edilir
- Çeviri cache anahtarına aktif dil eklenir
- Dil değiştiğinde çeviri cache’i güvenli biçimde temizlenebilir
- Widget method cache bozulursa kendini toparlayabilir

MİMARİ:
- Mixin yapısı korunur
- Lazy import zaten üst katmanda (yonetici / init)
- Bu dosya runtime optimizasyon katmanıdır
- Widget method cache ile translation cache birbirinden ayrı tutulur
- Widget method cache korunur, translation cache dil değişiminde sıfırlanır
- RootDilAkisiMixin ve root callback zinciri ile uyumlu çalışır

SURUM: 4
TARIH: 2026-03-24
IMZA: FY.
"""

from __future__ import annotations


class RootDilYardimcilariMixin:
    # =========================================================
    # INIT CACHE
    # =========================================================
    def _ensure_dil_cache(self):
        try:
            if not hasattr(self, "_dil_cache"):
                self._dil_cache = {}
        except Exception:
            pass

        try:
            if not hasattr(self, "_widget_method_cache"):
                self._widget_method_cache = {}
        except Exception:
            pass

        try:
            if not hasattr(self, "_aktif_dil_cache_kodu"):
                self._aktif_dil_cache_kodu = ""
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

    def _aktif_dil_kodu(self) -> str:
        """
        Services üzerinden aktif dil kodunu güvenli biçimde döndürür.
        """
        try:
            services = self._safe_getattr("services", None)
            if services is None:
                return ""

            aktif_dil = getattr(services, "aktif_dil", None)
            if callable(aktif_dil):
                return str(aktif_dil() or "").strip()

            get_language = getattr(services, "get_language", None)
            if callable(get_language):
                return str(get_language(default="") or "").strip()

        except Exception:
            pass

        return ""

    def _clear_translation_cache(self) -> None:
        """
        Sadece çeviri cache'ini temizler.
        Widget method cache korunur.
        """
        try:
            self._ensure_dil_cache()
            self._dil_cache = {}
        except Exception:
            pass

    def _clear_widget_method_cache(self) -> None:
        """
        Widget method cache'ini temizler.

        Not:
        - Normalde gerekli değildir
        - Widget değişimi / popup rebuild gibi durumlarda kullanılabilir
        """
        try:
            self._ensure_dil_cache()
            self._widget_method_cache = {}
        except Exception:
            pass

    def _sync_translation_cache_language(self) -> None:
        """
        Aktif dil değişmişse translation cache'i sıfırlar.
        """
        try:
            self._ensure_dil_cache()
            aktif_kod = self._aktif_dil_kodu()
            onceki_kod = str(self._safe_getattr("_aktif_dil_cache_kodu", "") or "")

            if aktif_kod != onceki_kod:
                self._dil_cache = {}
                self._aktif_dil_cache_kodu = aktif_kod
        except Exception:
            pass

    # =========================================================
    # DIL METIN COZUMLEME (CACHE)
    # =========================================================
    def _m(self, anahtar: str, default: str = "") -> str:
        """
        Aktif dile göre çevrilmiş metni döndürür.

        Cache anahtarı:
        - aktif dil
        - anahtar
        - default

        Böylece dil değişince eski dil sonucu dönmez.
        """
        self._ensure_dil_cache()
        self._sync_translation_cache_language()

        aktif_dil = self._aktif_dil_kodu()
        cache_key = f"{aktif_dil}|{anahtar}|{default}"

        try:
            if cache_key in self._dil_cache:
                return self._dil_cache[cache_key]
        except Exception:
            pass

        try:
            services = self._safe_getattr("services", None)
            if services is None:
                result = str(default or anahtar)
            else:
                result = str(services.metin(anahtar, default) or default or anahtar)

            try:
                self._dil_cache[cache_key] = result
            except Exception:
                pass

            return result

        except Exception:
            result = str(default or anahtar)
            try:
                self._dil_cache[cache_key] = result
            except Exception:
                pass
            return result

    # =========================================================
    # WIDGET METHOD CACHE
    # =========================================================
    def _get_widget_refresh_method(self, widget):
        self._ensure_dil_cache()

        if widget is None:
            return None

        wid = id(widget)

        try:
            if wid in self._widget_method_cache:
                cached = self._widget_method_cache[wid]
                if callable(cached):
                    return cached
                if cached is None:
                    return None
        except Exception:
            pass

        try:
            for method_name in ("refresh_language", "apply_language"):
                method = getattr(widget, method_name, None)
                if callable(method):
                    self._widget_method_cache[wid] = method
                    return method
        except Exception:
            pass

        try:
            self._widget_method_cache[wid] = None
        except Exception:
            pass

        return None

    # =========================================================
    # WIDGET BAZLI DIL YENILEME
    # =========================================================
    def _refresh_widget_language(self, widget) -> None:
        if widget is None:
            return

        try:
            method = self._get_widget_refresh_method(widget)
            if method:
                method()
                return
        except Exception:
            # Cache'te bozulmuş bound method kalmış olabilir.
            pass

        try:
            wid = id(widget)
            if hasattr(self, "_widget_method_cache") and wid in self._widget_method_cache:
                self._widget_method_cache.pop(wid, None)
        except Exception:
            pass

        try:
            method = self._get_widget_refresh_method(widget)
            if method:
                method()
        except Exception:
            pass

    def _refresh_all_language_bound_widgets(self) -> None:
        try:
            self._refresh_widget_language(self._safe_getattr("dosya_secici", None))
        except Exception:
            pass

        try:
            self._refresh_widget_language(self._safe_getattr("function_list", None))
        except Exception:
            pass

        try:
            self._refresh_widget_language(self._safe_getattr("editor", None))
        except Exception:
            pass

        try:
            self._refresh_widget_language(self._safe_getattr("status", None))
        except Exception:
            pass

        try:
            self._refresh_widget_language(self._safe_getattr("file_access_panel", None))
        except Exception:
            pass

        try:
            self._refresh_widget_language(self._safe_getattr("main_root", None))
        except Exception:
            pass

        try:
            self._refresh_widget_language(self._safe_getattr("bottom_bar", None))
        except Exception:
            pass

        try:
            refresh_version_label = self._safe_getattr("_refresh_version_label", None)
            if callable(refresh_version_label):
                refresh_version_label()
        except Exception:
            pass

        try:
            self._refresh_widget_language(self._safe_getattr("version_wrap", None))
        except Exception:
            pass

    # =========================================================
    # FULL REFRESH
    # =========================================================
    def _full_language_refresh(self) -> None:
        """
        Dil refresh öncesi translation cache'i aktif dile senkronlar,
        sonra tüm bağlı widget'ları ve layout'u günceller.
        """
        try:
            self._sync_translation_cache_language()
        except Exception:
            pass

        try:
            self._refresh_all_language_bound_widgets()
        except Exception:
            pass

        try:
            canvas = self._safe_getattr("canvas", None)
            if canvas and hasattr(canvas, "ask_update"):
                canvas.ask_update()
        except Exception:
            pass

        try:
            do_layout = self._safe_getattr("do_layout", None)
            if callable(do_layout):
                do_layout()
        except Exception:
            pass

        try:
            main_root = self._safe_getattr("main_root", None)
            if main_root and hasattr(main_root, "do_layout"):
                main_root.do_layout()
        except Exception:
            pass

        try:
            main_column = self._safe_getattr("main_column", None)
            if main_column and hasattr(main_column, "do_layout"):
                main_column.do_layout()
        except Exception:
            pass

        try:
            scroll = self._safe_getattr("scroll", None)
            if scroll and hasattr(scroll, "do_layout"):
                scroll.do_layout()
        except Exception:
            pass
