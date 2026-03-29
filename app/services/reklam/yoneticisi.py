# -*- coding: utf-8 -*-
"""
DOSYA: app/services/reklam/yoneticisi.py

ROL:
- Reklam servislerine tek giriş noktası sağlar
- Uygulamanın geri kalanını reklam servis detaylarından soyutlar
- Banner ve geçiş reklamlarını tek merkezden yönetir
- Reklam katmanını UI katmanından izole tutar
- Lazy import + strict cache ile tekrar eden çözümleme maliyetini azaltır

MİMARİ:
- Banner ve geçiş reklam servislerine lazy import ile erişir
- Root ve diğer UI katmanları sadece bu yöneticiyi bilir
- Reklam servis detaylarını dışarı sızdırmaz
- Ödüllü reklam desteğine genişletilebilir yapı korunur
- Modül ve fonksiyon referansları instance içinde cache'lenir
- İlk resolve sonrası aynı import/fonksiyon tekrar aranmaz
- Deterministik davranır
- Geriye uyumluluk katmanı içermez

API UYUMLULUK:
- Android API 35 uyumludur
- AndroidX uyumludur
- AdMob entegrasyon yapısına uyumludur

SURUM: 7
TARIH: 2026-03-28
IMZA: FY.
"""

from __future__ import annotations

from types import ModuleType
from typing import Callable


class ReklamYoneticisi:
    """
    Reklam servisleri için merkezi erişim yöneticisi.
    """

    __slots__ = (
        "_modul_cache",
        "_fonksiyon_cache",
    )

    BANNER_MODUL = "app.services.reklam.banner_reklam_servisi"
    GECIS_MODUL = "app.services.reklam.gecis_reklam_servisi"
    AYAR_MODUL = "app.services.reklam.ayarlari"

    def __init__(self) -> None:
        self._modul_cache: dict[str, ModuleType] = {}
        self._fonksiyon_cache: dict[tuple[str, str], Callable[..., object]] = {}

    # =========================================================
    # CACHE
    # =========================================================
    def cache_temizle(self) -> None:
        """
        Modül ve fonksiyon cache'lerini temizler.
        """
        self._modul_cache.clear()
        self._fonksiyon_cache.clear()

    # =========================================================
    # INTERNAL
    # =========================================================
    def _modul_yukle(self, modul_yolu: str) -> ModuleType:
        """
        Hedef modülü lazy import + cache ile yükler.
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
    ) -> Callable[..., object]:
        """
        Modül içindeki fonksiyonu lazy resolve + cache ile getirir.
        """
        key = (modul_yolu, fonksiyon_adi)

        cached = self._fonksiyon_cache.get(key)
        if cached is not None:
            return cached

        module = self._modul_yukle(modul_yolu)
        value = getattr(module, fonksiyon_adi)

        if not callable(value):
            raise TypeError(
                f"{modul_yolu}.{fonksiyon_adi} çağrılabilir değil."
            )

        self._fonksiyon_cache[key] = value
        return value

    def _cagir(
        self,
        modul_yolu: str,
        fonksiyon_adi: str,
        *args,
        **kwargs,
    ) -> object:
        """
        Hedef fonksiyonu deterministik biçimde çağırır.
        """
        func = self._fonksiyon_getir(modul_yolu, fonksiyon_adi)
        return func(*args, **kwargs)

    # =========================================================
    # BANNER
    # =========================================================
    def banner_goster(self) -> bool:
        return bool(self._cagir(self.BANNER_MODUL, "banner_goster"))

    def banner_goster_gecikmeli(self, delay: float = 1.5) -> bool:
        return bool(
            self._cagir(
                self.BANNER_MODUL,
                "banner_goster_gecikmeli",
                delay=delay,
            )
        )

    def banner_gizle(self) -> bool:
        return bool(self._cagir(self.BANNER_MODUL, "banner_gizle"))

    def banner_baslatildi_mi(self) -> bool:
        return bool(self._cagir(self.BANNER_MODUL, "banner_baslatildi_mi"))

    def banner_gosteriliyor_mu(self) -> bool:
        return bool(self._cagir(self.BANNER_MODUL, "banner_gosteriliyor_mu"))

    def banner_planlandi_mi(self) -> bool:
        return bool(self._cagir(self.BANNER_MODUL, "banner_planlandi_mi"))

    def banner_yukleniyor_mu(self) -> bool:
        return bool(self._cagir(self.BANNER_MODUL, "banner_yukleniyor_mu"))

    # =========================================================
    # GECIS REKLAMI
    # =========================================================
    def gecis_reklami_yukle(self) -> bool:
        return bool(self._cagir(self.GECIS_MODUL, "gecis_reklami_yukle"))

    def gecis_reklami_hazir_mi(self) -> bool:
        return bool(self._cagir(self.GECIS_MODUL, "gecis_reklami_hazir_mi"))

    def gecis_reklami_yukleniyor_mu(self) -> bool:
        return bool(self._cagir(self.GECIS_MODUL, "gecis_reklami_yukleniyor_mu"))

    def gecis_reklami_goster(self, sonrasi_callback=None) -> bool:
        return bool(
            self._cagir(
                self.GECIS_MODUL,
                "gecis_reklami_goster",
                sonrasi_callback=sonrasi_callback,
            )
        )

    def gecis_reklami_temizle(self) -> None:
        self._cagir(self.GECIS_MODUL, "gecis_reklami_temizle")

    # =========================================================
    # AYAR / DURUM
    # =========================================================
    def test_modu_aktif_mi(self) -> bool:
        return bool(self._cagir(self.AYAR_MODUL, "test_modu_aktif_mi"))

    def yayin_modu_aktif_mi(self) -> bool:
        return bool(self._cagir(self.AYAR_MODUL, "yayin_modu_aktif_mi"))

    def reklam_modu_etiketi(self) -> str:
        return str(self._cagir(self.AYAR_MODUL, "reklam_modu_etiketi"))

    def aktif_admob_app_id(self) -> str:
        return str(self._cagir(self.AYAR_MODUL, "aktif_admob_app_id"))

    def aktif_banner_reklam_id(self) -> str:
        return str(self._cagir(self.AYAR_MODUL, "aktif_banner_reklam_id"))

    def aktif_interstitial_reklam_id(self) -> str:
        return str(self._cagir(self.AYAR_MODUL, "aktif_interstitial_reklam_id"))

    def aktif_rewarded_reklam_id(self) -> str:
        return str(self._cagir(self.AYAR_MODUL, "aktif_rewarded_reklam_id"))

    # =========================================================
    # ODULLU REKLAM
    # =========================================================
    def odullu_reklam_goster(self) -> bool:
        """
        Gelecekte rewarded servis bağlanınca aktif kullanılacak.
        Şimdilik güvenli no-op davranışı döner.
        """
        return False