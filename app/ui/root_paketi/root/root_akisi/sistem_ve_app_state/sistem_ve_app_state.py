# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/root_paketi/root/root_akisi/sistem_ve_app_state/sistem_ve_app_state.py

ROL:
- Root katmanında sistem ve uygulama state erişim yardımcılarını tek modülde toplar
- ServicesYoneticisi üzerinden sistem yöneticisine güvenli erişim sağlar
- Uygulama state kaydetme / yükleme için fail-soft arayüz sunar
- Root içinde sistem bağımlılıklarını izole eder
- Sistem erişiminde lazy resolve ve runtime cache uygular
- RAM öncelikli state yaklaşımını destekler
- Gerekirse services katmanında mevcutsa app state erişimini kullanır

MİMARİ:
- Bu modül mixin mantığıyla çalışır
- RootWidget içinde kullanılan sistem/app state yardımcı metodları burada tanımlanır
- Sistem erişimi yalnızca services üzerinden yapılır
- Fail-soft yaklaşım uygulanır (hata durumunda None/boş değer döner)
- İlk uygun services method resolve edildikten sonra cache içine alınır
- İstenirse cache temizlenebilir
- Bu dosyada import-level lazy import yerine runtime lazy resolve + cache uygulanır

NOTLAR:
- Uygulama state için ana yaklaşım root içindeki memory state akışıdır
- Bu modül, services katmanında varsa app state metodlarını ek yardımcı katman olarak kullanır
- Services tarafında state API yoksa sessizce fail-soft davranır
- Genişletilmek istenirse bu noktadan services/state entegrasyonu artırılabilir
- Bu dosya doğrudan UI çizmez

BEKLENEN ROOT ALANLARI:
- self.services

DESTEKLENEN SERVICES API VARYASYONLARI:
- sistem_yoneticisi()
- get_sistem_yoneticisi()
- system_manager()
- get_system_manager()

OPSİYONEL APP STATE API VARYASYONLARI:
- get_app_state(default=...)
- set_app_state(state)
- clear_app_state()

SURUM: 4
TARIH: 2026-03-26
IMZA: FY.
"""

from __future__ import annotations


class RootSistemVeAppStateMixin:
    """
    Root katmanında sistem ve uygulama state erişimini sağlayan mixin.
    """

    # =========================================================
    # CACHE
    # =========================================================
    def _ensure_sistem_app_state_cache(self) -> None:
        """
        Sistem/app state yardımcı cache alanlarını hazırlar.
        """
        try:
            if not hasattr(self, "_sistem_app_state_cache"):
                self._sistem_app_state_cache = {}
        except Exception:
            pass

    def _sistem_app_state_cache_temizle(self) -> None:
        """
        Sistem/app state cache alanlarını temizler.
        """
        try:
            self._sistem_app_state_cache = {}
        except Exception:
            pass

    # =========================================================
    # INTERNAL HELPERS
    # =========================================================
    def _safe_getattr(self, name: str, default=None):
        """
        Root üzerinde güvenli getattr çağrısı yapar.

        Args:
            name: Alan adı.
            default: Alan yoksa dönecek varsayılan değer.

        Returns:
            Any
        """
        try:
            return getattr(self, name, default)
        except Exception:
            return default

    def _cache_get(self, key: str, default=None):
        """
        Cache içinden güvenli biçimde değer alır.

        Args:
            key: Cache anahtarı.
            default: Anahtar yoksa dönecek varsayılan değer.

        Returns:
            Any
        """
        try:
            self._ensure_sistem_app_state_cache()
            return self._sistem_app_state_cache.get(key, default)
        except Exception:
            return default

    def _cache_set(self, key: str, value) -> None:
        """
        Cache içine güvenli biçimde değer yazar.

        Args:
            key: Cache anahtarı.
            value: Yazılacak değer.
        """
        try:
            self._ensure_sistem_app_state_cache()
            self._sistem_app_state_cache[key] = value
        except Exception:
            pass

    def _resolve_services(self):
        """
        Root üzerindeki services nesnesini alır ve cache'ler.

        Returns:
            object | None
        """
        try:
            cached = self._cache_get("resolved_services_obj", None)
            if cached is not None:
                return cached
        except Exception:
            pass

        try:
            services = self._safe_getattr("services", None)
            if services is not None:
                self._cache_set("resolved_services_obj", services)
            return services
        except Exception:
            return None

    def _resolve_services_method(self, services, method_names: tuple[str, ...]):
        """
        Services nesnesi üzerinde ilk uygun callable metodu bulur ve cache'ler.

        Args:
            services: Services nesnesi.
            method_names: Denenecek method adları.

        Returns:
            callable | None
        """
        if services is None:
            return None

        self._ensure_sistem_app_state_cache()

        cache_key = None

        try:
            cache_key = ("services_method", id(services), tuple(method_names))
            cached_method = self._cache_get(cache_key, None)
            if cached_method is not None:
                return cached_method
        except Exception:
            cache_key = None

        bulunan = None

        try:
            for method_name in method_names:
                method = getattr(services, method_name, None)
                if callable(method):
                    bulunan = method
                    break
        except Exception:
            bulunan = None

        try:
            if cache_key is not None and bulunan is not None:
                self._cache_set(cache_key, bulunan)
        except Exception:
            pass

        return bulunan

    def _resolve_sistem_method(self, sistem, method_names: tuple[str, ...]):
        """
        Sistem yöneticisi üzerinde ilk uygun callable metodu bulur ve cache'ler.

        Args:
            sistem: Sistem yöneticisi nesnesi.
            method_names: Denenecek method adları.

        Returns:
            callable | None
        """
        if sistem is None:
            return None

        self._ensure_sistem_app_state_cache()

        cache_key = None

        try:
            cache_key = ("sistem_method", id(sistem), tuple(method_names))
            cached_method = self._cache_get(cache_key, None)
            if cached_method is not None:
                return cached_method
        except Exception:
            cache_key = None

        bulunan = None

        try:
            for method_name in method_names:
                method = getattr(sistem, method_name, None)
                if callable(method):
                    bulunan = method
                    break
        except Exception:
            bulunan = None

        try:
            if cache_key is not None and bulunan is not None:
                self._cache_set(cache_key, bulunan)
        except Exception:
            pass

        return bulunan

    # =========================================================
    # SISTEM ERISIMI
    # =========================================================
    def _sistem(self):
        """
        Services üzerinden sistem yöneticisini döndürür.

        Lazy resolve + cache akışı:
        1) Önce cached sistem nesnesi varsa onu döndürür
        2) Yoksa services üzerinde uygun methodu bulur
        3) Sonucu cache içine alır
        4) Başarısız olursa None döner

        Returns:
            object | None
        """
        try:
            cached_sistem = self._cache_get("resolved_sistem_manager", None)
            if cached_sistem is not None:
                return cached_sistem
        except Exception:
            pass

        try:
            services = self._resolve_services()
            if services is None:
                return None

            get_sistem = self._resolve_services_method(
                services,
                (
                    "sistem_yoneticisi",
                    "get_sistem_yoneticisi",
                    "system_manager",
                    "get_system_manager",
                ),
            )
            if not callable(get_sistem):
                return None

            sistem = get_sistem()
            if sistem is not None:
                self._cache_set("resolved_sistem_manager", sistem)
            return sistem

        except Exception:
            return None

    # =========================================================
    # APP STATE HELPERS
    # =========================================================
    def _get_app_state_api_reader(self):
        """
        App state okuma metodunu services veya sistem yöneticisi üstünden bulur.

        Returns:
            callable | None
        """
        try:
            cached = self._cache_get("resolved_app_state_reader", None)
            if cached is not None:
                return cached
        except Exception:
            pass

        reader = None

        try:
            services = self._resolve_services()
            reader = self._resolve_services_method(
                services,
                (
                    "get_app_state",
                    "app_state_al",
                ),
            )
        except Exception:
            reader = None

        if reader is None:
            try:
                sistem = self._sistem()
                reader = self._resolve_sistem_method(
                    sistem,
                    (
                        "get_app_state",
                        "app_state_al",
                    ),
                )
            except Exception:
                reader = None

        try:
            if reader is not None:
                self._cache_set("resolved_app_state_reader", reader)
        except Exception:
            pass

        return reader

    def _get_app_state_api_writer(self):
        """
        App state yazma metodunu services veya sistem yöneticisi üstünden bulur.

        Returns:
            callable | None
        """
        try:
            cached = self._cache_get("resolved_app_state_writer", None)
            if cached is not None:
                return cached
        except Exception:
            pass

        writer = None

        try:
            services = self._resolve_services()
            writer = self._resolve_services_method(
                services,
                (
                    "set_app_state",
                    "app_state_yaz",
                ),
            )
        except Exception:
            writer = None

        if writer is None:
            try:
                sistem = self._sistem()
                writer = self._resolve_sistem_method(
                    sistem,
                    (
                        "set_app_state",
                        "app_state_yaz",
                    ),
                )
            except Exception:
                writer = None

        try:
            if writer is not None:
                self._cache_set("resolved_app_state_writer", writer)
        except Exception:
            pass

        return writer

    def _get_app_state_api_clearer(self):
        """
        App state temizleme metodunu services veya sistem yöneticisi üstünden bulur.

        Returns:
            callable | None
        """
        try:
            cached = self._cache_get("resolved_app_state_clearer", None)
            if cached is not None:
                return cached
        except Exception:
            pass

        clearer = None

        try:
            services = self._resolve_services()
            clearer = self._resolve_services_method(
                services,
                (
                    "clear_app_state",
                    "app_state_temizle",
                ),
            )
        except Exception:
            clearer = None

        if clearer is None:
            try:
                sistem = self._sistem()
                clearer = self._resolve_sistem_method(
                    sistem,
                    (
                        "clear_app_state",
                        "app_state_temizle",
                    ),
                )
            except Exception:
                clearer = None

        try:
            if clearer is not None:
                self._cache_set("resolved_app_state_clearer", clearer)
        except Exception:
            pass

        return clearer

    # =========================================================
    # APP STATE API
    # =========================================================
    def _save_app_state_to_settings(self, state: dict) -> None:
        """
        Uygulama state'ini uygun services/sistem API varsa kaydetmeyi dener.

        Not:
        - Bu metod fail-soft çalışır
        - API yoksa sessizce çıkar
        - Root tarafındaki memory state akışını bozmaz

        Args:
            state: Kaydedilmek istenen state sözlüğü
        """
        try:
            if not isinstance(state, dict):
                return

            writer = self._get_app_state_api_writer()
            if callable(writer):
                writer(dict(state))
        except Exception:
            pass

    def _load_app_state_from_settings(self) -> dict:
        """
        Uygun services/sistem API varsa app state okumayı dener.

        Not:
        - API yoksa veya hata olursa boş dict döner
        - Root tarafındaki memory/disk fallback akışına yardımcı katmandır

        Returns:
            dict
        """
        try:
            reader = self._get_app_state_api_reader()
            if not callable(reader):
                return {}

            try:
                value = reader(default={})
            except TypeError:
                value = reader()

            if isinstance(value, dict):
                return dict(value)

            return {}
        except Exception:
            return {}

    def _clear_app_state_from_settings(self) -> None:
        """
        Uygun services/sistem API varsa app state temizlemeyi dener.

        Not:
        - API yoksa sessizce çıkar
        """
        try:
            clearer = self._get_app_state_api_clearer()
            if callable(clearer):
                clearer()
        except Exception:
            pass
