# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/root_paketi/root/root_akisi/sistem_ve_app_state/sistem_ve_app_state.py

ROL:
- Root katmanında sistem ve uygulama state erişim yardımcılarını toplar
- Services üzerinden sistem yöneticisine güvenli erişim sağlar
- Uygulama state kaydetme / yükleme için fail-soft arayüz sunar
- Root içinde sistem bağımlılıklarını izole eder

MİMARİ:
- Bu modül mixin mantığıyla çalışır
- Sistem erişimi yalnızca services üzerinden yapılır
- Fail-soft yaklaşım uygulanır
- Uygulama state için ana yaklaşım root içindeki memory state akışıdır
- Services veya sistem yöneticisinde varsa app state API'lerini yardımcı katman olarak kullanır
- UI çizmez

SURUM: 5
TARIH: 2026-03-27
IMZA: FY.
"""

from __future__ import annotations


class RootSistemVeAppStateMixin:
    """
    Root katmanında sistem ve uygulama state erişimini sağlayan mixin.
    """

    def _safe_getattr(self, name: str, default=None):
        """
        Root üzerinde güvenli getattr çağrısı yapar.
        """
        try:
            return getattr(self, name, default)
        except Exception:
            return default

    def _services(self):
        """
        Root üzerindeki services nesnesini döndürür.
        """
        return self._safe_getattr("services", None)

    def _ilk_cagrilabilir_metod(self, nesne, metod_adlari: tuple[str, ...]):
        """
        Verilen nesnede ilk uygun callable metodu döndürür.
        """
        if nesne is None:
            return None

        for metod_adi in metod_adlari:
            try:
                metod = getattr(nesne, metod_adi, None)
                if callable(metod):
                    return metod
            except Exception:
                continue

        return None

    def _sistem(self):
        """
        Services üzerinden sistem yöneticisini döndürür.

        Desteklenen services API varyasyonları:
        - sistem_yoneticisi()
        - get_sistem_yoneticisi()
        - system_manager()
        - get_system_manager()
        """
        services = self._services()
        if services is None:
            return None

        metod = self._ilk_cagrilabilir_metod(
            services,
            (
                "sistem_yoneticisi",
                "get_sistem_yoneticisi",
                "system_manager",
                "get_system_manager",
            ),
        )
        if not callable(metod):
            return None

        try:
            return metod()
        except Exception:
            return None

    def _get_app_state_api_reader(self):
        """
        App state okuma metodunu services veya sistem yöneticisi üstünden bulur.
        """
        services = self._services()
        metod = self._ilk_cagrilabilir_metod(
            services,
            (
                "get_app_state",
                "app_state_al",
            ),
        )
        if callable(metod):
            return metod

        sistem = self._sistem()
        metod = self._ilk_cagrilabilir_metod(
            sistem,
            (
                "get_app_state",
                "app_state_al",
            ),
        )
        return metod

    def _get_app_state_api_writer(self):
        """
        App state yazma metodunu services veya sistem yöneticisi üstünden bulur.
        """
        services = self._services()
        metod = self._ilk_cagrilabilir_metod(
            services,
            (
                "set_app_state",
                "app_state_yaz",
            ),
        )
        if callable(metod):
            return metod

        sistem = self._sistem()
        metod = self._ilk_cagrilabilir_metod(
            sistem,
            (
                "set_app_state",
                "app_state_yaz",
            ),
        )
        return metod

    def _get_app_state_api_clearer(self):
        """
        App state temizleme metodunu services veya sistem yöneticisi üstünden bulur.
        """
        services = self._services()
        metod = self._ilk_cagrilabilir_metod(
            services,
            (
                "clear_app_state",
                "app_state_temizle",
            ),
        )
        if callable(metod):
            return metod

        sistem = self._sistem()
        metod = self._ilk_cagrilabilir_metod(
            sistem,
            (
                "clear_app_state",
                "app_state_temizle",
            ),
        )
        return metod

    def _save_app_state_to_settings(self, state: dict) -> None:
        """
        Uygulama state'ini uygun services/sistem API varsa kaydetmeyi dener.
        """
        if not isinstance(state, dict):
            return

        try:
            writer = self._get_app_state_api_writer()
            if callable(writer):
                writer(dict(state))
        except Exception:
            pass

    def _load_app_state_from_settings(self) -> dict:
        """
        Uygun services/sistem API varsa app state okumayı dener.
        API yoksa veya hata olursa boş dict döner.
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
        except Exception:
            pass

        return {}

    def _clear_app_state_from_settings(self) -> None:
        """
        Uygun services/sistem API varsa app state temizlemeyi dener.
        """
        try:
            clearer = self._get_app_state_api_clearer()
            if callable(clearer):
                clearer()
        except Exception:
            pass
