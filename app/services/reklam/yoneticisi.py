# -*- coding: utf-8 -*-
"""
DOSYA: app/services/reklam/yoneticisi.py

ROL:
- Reklam servislerine tek giriş noktası sağlamak
- Uygulamanın geri kalanını reklam servis detaylarından soyutlamak
- Banner ve geçiş reklamlarını tek merkezden yönetmek
- Reklam katmanını UI katmanından izole tutmak

MİMARİ:
- Banner ve geçiş reklam servislerine lazy import ile erişir
- Root ve diğer UI katmanları sadece bu yöneticiyi bilir
- Reklam servislerinin iç detaylarını dışarı sızdırmaz
- Ödüllü reklam desteğine genişletilebilir yapı korunur

API UYUMLULUK:
- API 35 uyumlu
- AndroidX uyumlu
- AdMob entegrasyon yapısına uyumlu

SURUM: 5
TARIH: 2026-03-22
IMZA: FY.
"""

from __future__ import annotations


class ReklamYoneticisi:
    # =========================================================
    # BANNER
    # =========================================================
    def banner_goster(self) -> bool:
        from app.services.reklam.banner_reklam_servisi import banner_goster
        return banner_goster()

    def banner_goster_gecikmeli(self, delay: float = 1.5) -> bool:
        from app.services.reklam.banner_reklam_servisi import (
            banner_goster_gecikmeli,
        )
        return banner_goster_gecikmeli(delay=delay)

    def banner_gizle(self) -> bool:
        from app.services.reklam.banner_reklam_servisi import banner_gizle
        return banner_gizle()

    def banner_baslatildi_mi(self) -> bool:
        from app.services.reklam.banner_reklam_servisi import banner_baslatildi_mi
        return banner_baslatildi_mi()

    def banner_gosteriliyor_mu(self) -> bool:
        from app.services.reklam.banner_reklam_servisi import banner_gosteriliyor_mu
        return banner_gosteriliyor_mu()

    def banner_planlandi_mi(self) -> bool:
        from app.services.reklam.banner_reklam_servisi import banner_planlandi_mi
        return banner_planlandi_mi()

    # =========================================================
    # GEÇİŞ REKLAMI
    # =========================================================
    def gecis_reklami_yukle(self) -> bool:
        from app.services.reklam.gecis_reklam_servisi import gecis_reklami_yukle
        return gecis_reklami_yukle()

    def gecis_reklami_hazir_mi(self) -> bool:
        from app.services.reklam.gecis_reklam_servisi import (
            gecis_reklami_hazir_mi,
        )
        return gecis_reklami_hazir_mi()

    def gecis_reklami_yukleniyor_mu(self) -> bool:
        from app.services.reklam.gecis_reklam_servisi import (
            gecis_reklami_yukleniyor_mu,
        )
        return gecis_reklami_yukleniyor_mu()

    def gecis_reklami_goster(self, sonrasi_callback=None) -> bool:
        from app.services.reklam.gecis_reklam_servisi import gecis_reklami_goster
        return gecis_reklami_goster(sonrasi_callback=sonrasi_callback)

    def gecis_reklami_temizle(self) -> None:
        from app.services.reklam.gecis_reklam_servisi import gecis_reklami_temizle
        gecis_reklami_temizle()

    # =========================================================
    # AYAR / DURUM
    # =========================================================
    def test_modu_aktif_mi(self) -> bool:
        from app.services.reklam.ayarlari import test_modu_aktif_mi
        return test_modu_aktif_mi()

    def yayin_modu_aktif_mi(self) -> bool:
        from app.services.reklam.ayarlari import yayin_modu_aktif_mi
        return yayin_modu_aktif_mi()

    def reklam_modu_etiketi(self) -> str:
        from app.services.reklam.ayarlari import reklam_modu_etiketi
        return reklam_modu_etiketi()

    def aktif_admob_app_id(self) -> str:
        from app.services.reklam.ayarlari import aktif_admob_app_id
        return aktif_admob_app_id()

    def aktif_banner_reklam_id(self) -> str:
        from app.services.reklam.ayarlari import aktif_banner_reklam_id
        return aktif_banner_reklam_id()

    def aktif_interstitial_reklam_id(self) -> str:
        from app.services.reklam.ayarlari import aktif_interstitial_reklam_id
        return aktif_interstitial_reklam_id()

    def aktif_rewarded_reklam_id(self) -> str:
        from app.services.reklam.ayarlari import aktif_rewarded_reklam_id
        return aktif_rewarded_reklam_id()

    # =========================================================
    # ÖDÜLLÜ REKLAM - HAZIR ALAN
    # =========================================================
    def odullu_reklam_goster(self) -> bool:
        """
        Gelecekte rewarded servis bağlanınca aktif kullanılacak.
        Şimdilik güvenli no-op davranışı döner.
        """
        return False
