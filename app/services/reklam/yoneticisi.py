# -*- coding: utf-8 -*-
"""
DOSYA: app/services/reklam/yoneticisi.py

ROL:
- Reklam servislerine tek giriş noktası sağlamak
- Uygulamanın geri kalanını reklam servis detaylarından soyutlamak
- Banner ve geçiş reklamlarını tek merkezden yönetmek
- Reklam katmanını UI katmanından izole tutmak
- Lazy import ve cache sistemi ile tekrar eden import maliyetini azaltmak

MİMARİ:
- Banner ve geçiş reklam servislerine lazy import ile erişir
- Root ve diğer UI katmanları sadece bu yöneticiyi bilir
- Reklam servislerinin iç detaylarını dışarı sızdırmaz
- Ödüllü reklam desteğine genişletilebilir yapı korunur
- Modül ve fonksiyon referansları instance içinde cache'lenir
- İlk resolve sonrası aynı import/fonksiyon tekrar tekrar aranmaz

API UYUMLULUK:
- API 35 uyumlu
- AndroidX uyumlu
- AdMob entegrasyon yapısına uyumlu

SURUM: 6
TARIH: 2026-03-24
IMZA: FY.
"""

from __future__ import annotations

import traceback


class ReklamYoneticisi:
    """
    Reklam servisleri için merkezi erişim yöneticisi.
    """

    def __init__(self) -> None:
        self._modul_cache: dict[str, object] = {}
        self._fonksiyon_cache: dict[tuple[str, str], object] = {}

    # =========================================================
    # CACHE
    # =========================================================
    def cache_temizle(self) -> None:
        """
        Modül ve fonksiyon cache'lerini temizler.
        """
        try:
            self._modul_cache = {}
        except Exception:
            pass

        try:
            self._fonksiyon_cache = {}
        except Exception:
            pass

    def _cache_modul_getir(self, modul_yolu: str):
        try:
            return self._modul_cache.get(modul_yolu)
        except Exception:
            return None

    def _cache_modul_yaz(self, modul_yolu: str, modul) -> None:
        try:
            self._modul_cache[modul_yolu] = modul
        except Exception:
            pass

    def _cache_fonksiyon_getir(self, modul_yolu: str, fonksiyon_adi: str):
        try:
            return self._fonksiyon_cache.get((modul_yolu, fonksiyon_adi))
        except Exception:
            return None

    def _cache_fonksiyon_yaz(
        self,
        modul_yolu: str,
        fonksiyon_adi: str,
        fonksiyon,
    ) -> None:
        try:
            self._fonksiyon_cache[(modul_yolu, fonksiyon_adi)] = fonksiyon
        except Exception:
            pass

    # =========================================================
    # INTERNAL
    # =========================================================
    def _modul_yukle(self, modul_yolu: str):
        """
        Hedef modülü lazy import + cache ile yükler.

        Args:
            modul_yolu: Yüklenecek modül yolu.

        Returns:
            module | None
        """
        try:
            cached = self._cache_modul_getir(modul_yolu)
            if cached is not None:
                return cached
        except Exception:
            pass

        try:
            modul = __import__(modul_yolu, fromlist=["*"])
            self._cache_modul_yaz(modul_yolu, modul)
            return modul
        except Exception:
            print(f"[REKLAM_YONETICISI] Modül yüklenemedi: {modul_yolu}")
            print(traceback.format_exc())
            return None

    def _fonksiyon_getir(self, modul_yolu: str, fonksiyon_adi: str):
        """
        Modül içindeki fonksiyonu lazy resolve + cache ile getirir.

        Args:
            modul_yolu: Modül yolu.
            fonksiyon_adi: Hedef fonksiyon adı.

        Returns:
            callable | None
        """
        try:
            cached = self._cache_fonksiyon_getir(modul_yolu, fonksiyon_adi)
            if cached is not None:
                return cached
        except Exception:
            pass

        modul = self._modul_yukle(modul_yolu)
        if modul is None:
            return None

        try:
            fonksiyon = getattr(modul, fonksiyon_adi, None)
            if callable(fonksiyon):
                self._cache_fonksiyon_yaz(modul_yolu, fonksiyon_adi, fonksiyon)
                return fonksiyon
        except Exception:
            print(
                "[REKLAM_YONETICISI] "
                f"Fonksiyon alınamadı: {modul_yolu}.{fonksiyon_adi}"
            )
            print(traceback.format_exc())

        return None

    def _cagir(self, modul_yolu: str, fonksiyon_adi: str, *args, **kwargs):
        """
        Hedef fonksiyonu güvenli biçimde çağırır.

        Args:
            modul_yolu: Modül yolu.
            fonksiyon_adi: Fonksiyon adı.
            *args: Argümanlar.
            **kwargs: Keyword argümanlar.

        Returns:
            Any
        """
        fonksiyon = self._fonksiyon_getir(modul_yolu, fonksiyon_adi)
        if fonksiyon is None:
            return None

        try:
            return fonksiyon(*args, **kwargs)
        except Exception:
            print(
                "[REKLAM_YONETICISI] "
                f"Fonksiyon çağrısı başarısız: {modul_yolu}.{fonksiyon_adi}"
            )
            print(traceback.format_exc())
            return None

    # =========================================================
    # MODUL YOLLARI
    # =========================================================
    BANNER_MODUL = "app.services.reklam.banner_reklam_servisi"
    GECIS_MODUL = "app.services.reklam.gecis_reklam_servisi"
    AYAR_MODUL = "app.services.reklam.ayarlari"

    # =========================================================
    # BANNER
    # =========================================================
    def banner_goster(self) -> bool:
        return bool(self._cagir(self.BANNER_MODUL, "banner_goster") or False)

    def banner_goster_gecikmeli(self, delay: float = 1.5) -> bool:
        return bool(
            self._cagir(
                self.BANNER_MODUL,
                "banner_goster_gecikmeli",
                delay=delay,
            )
            or False
        )

    def banner_gizle(self) -> bool:
        return bool(self._cagir(self.BANNER_MODUL, "banner_gizle") or False)

    def banner_baslatildi_mi(self) -> bool:
        return bool(
            self._cagir(self.BANNER_MODUL, "banner_baslatildi_mi") or False
        )

    def banner_gosteriliyor_mu(self) -> bool:
        return bool(
            self._cagir(self.BANNER_MODUL, "banner_gosteriliyor_mu") or False
        )

    def banner_planlandi_mi(self) -> bool:
        return bool(
            self._cagir(self.BANNER_MODUL, "banner_planlandi_mi") or False
        )

    # =========================================================
    # GEÇİŞ REKLAMI
    # =========================================================
    def gecis_reklami_yukle(self) -> bool:
        return bool(self._cagir(self.GECIS_MODUL, "gecis_reklami_yukle") or False)

    def gecis_reklami_hazir_mi(self) -> bool:
        return bool(
            self._cagir(self.GECIS_MODUL, "gecis_reklami_hazir_mi") or False
        )

    def gecis_reklami_yukleniyor_mu(self) -> bool:
        return bool(
            self._cagir(self.GECIS_MODUL, "gecis_reklami_yukleniyor_mu") or False
        )

    def gecis_reklami_goster(self, sonrasi_callback=None) -> bool:
        return bool(
            self._cagir(
                self.GECIS_MODUL,
                "gecis_reklami_goster",
                sonrasi_callback=sonrasi_callback,
            )
            or False
        )

    def gecis_reklami_temizle(self) -> None:
        self._cagir(self.GECIS_MODUL, "gecis_reklami_temizle")

    # =========================================================
    # AYAR / DURUM
    # =========================================================
    def test_modu_aktif_mi(self) -> bool:
        return bool(self._cagir(self.AYAR_MODUL, "test_modu_aktif_mi") or False)

    def yayin_modu_aktif_mi(self) -> bool:
        return bool(self._cagir(self.AYAR_MODUL, "yayin_modu_aktif_mi") or False)

    def reklam_modu_etiketi(self) -> str:
        return str(self._cagir(self.AYAR_MODUL, "reklam_modu_etiketi") or "")

    def aktif_admob_app_id(self) -> str:
        return str(self._cagir(self.AYAR_MODUL, "aktif_admob_app_id") or "")

    def aktif_banner_reklam_id(self) -> str:
        return str(self._cagir(self.AYAR_MODUL, "aktif_banner_reklam_id") or "")

    def aktif_interstitial_reklam_id(self) -> str:
        return str(
            self._cagir(self.AYAR_MODUL, "aktif_interstitial_reklam_id") or ""
        )

    def aktif_rewarded_reklam_id(self) -> str:
        return str(self._cagir(self.AYAR_MODUL, "aktif_rewarded_reklam_id") or "")

    # =========================================================
    # ÖDÜLLÜ REKLAM - HAZIR ALAN
    # =========================================================
    def odullu_reklam_goster(self) -> bool:
        """
        Gelecekte rewarded servis bağlanınca aktif kullanılacak.
        Şimdilik güvenli no-op davranışı döner.
        """
        return False
