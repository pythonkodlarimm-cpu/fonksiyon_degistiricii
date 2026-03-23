# -*- coding: utf-8 -*-
"""
DOSYA: app/services/yoneticisi.py

ROL:
- Services katmanı için tek giriş noktası sağlamak
- Alt servis yöneticilerini merkezileştirmek
- Üst katmanın alt modül detaylarını bilmesini engellemek

MİMARİ:
- Lazy import kullanır
- UI ve root katmanı doğrudan alt servis dosyalarına değil, bu yöneticiye bağlanır
- Refactor sırasında import kırılmalarını azaltır
- Android, belge, dosya, analiz, reklam, güncelleme, sistem ve yedek servislerini tek noktada toplar
- Banner ve geçiş reklamı gibi reklam akışları üst katmana tek kapıdan açılır
- Play Store yönlendirmeli güncelleme akışı üst katmana tek kapıdan açılır

API UYUMLULUK:
- Platform bağımsız çekirdek servislerle uyumludur
- Android servisleri izole biçimde yönetir
- Android API 35 hedefiyle uyumlu mimari için uygundur

SURUM: 5
TARIH: 2026-03-23
IMZA: FY.
"""

from __future__ import annotations


class ServicesYoneticisi:
    # =========================================================
    # ALT YONETICILER
    # =========================================================
    def _analiz_yoneticisi(self):
        from app.services.analiz import AnalizYoneticisi
        return AnalizYoneticisi()

    def _android_yoneticisi(self):
        from app.services.android import AndroidYoneticisi
        return AndroidYoneticisi()

    def _belge_yoneticisi(self):
        from app.services.belge import BelgeYoneticisi
        return BelgeYoneticisi()

    def _dosya_yoneticisi(self):
        from app.services.dosya import DosyaYoneticisi
        return DosyaYoneticisi()

    def _reklam_yoneticisi(self):
        from app.services.reklam import ReklamYoneticisi
        return ReklamYoneticisi()

    def _guncelleme_yoneticisi(self):
        from app.services.guncelleme import GuncellemeYoneticisi
        return GuncellemeYoneticisi()

    def _sistem_yoneticisi(self):
        from app.services.sistem import SistemYoneticisi
        return SistemYoneticisi()

    def _yedek_yoneticisi(self):
        from app.services.yedek import YedekYoneticisi
        return YedekYoneticisi()

    # =========================================================
    # ANALIZ
    # =========================================================
    def analiz_yoneticisi(self):
        return self._analiz_yoneticisi()

    def replace_karar_servisi_olustur(self, *args, **kwargs):
        return self._analiz_yoneticisi().replace_karar_servisi_olustur(
            *args,
            **kwargs,
        )

    # =========================================================
    # ANDROID
    # =========================================================
    def android_yoneticisi(self):
        return self._android_yoneticisi()

    def android_belge_servisi(self):
        return self._android_yoneticisi().android_belge_servisi()

    def android_ozel_izin_servisi(self):
        return self._android_yoneticisi().android_ozel_izin_servisi()

    def android_reklam_kopru_servisi(self):
        return self._android_yoneticisi().android_reklam_kopru_servisi()

    def android_uri_servisi(self):
        return self._android_yoneticisi().android_uri_servisi()

    # =========================================================
    # BELGE
    # =========================================================
    def belge_yoneticisi(self):
        return self._belge_yoneticisi()

    def belge_ice_aktarma_servisi(self):
        return self._belge_yoneticisi().belge_ice_aktarma_servisi()

    def belge_kaydetme_servisi(self):
        return self._belge_yoneticisi().belge_kaydetme_servisi()

    def belge_oturumu_servisi(self):
        return self._belge_yoneticisi().belge_oturumu_servisi()

    # =========================================================
    # DOSYA
    # =========================================================
    def dosya_yoneticisi(self):
        return self._dosya_yoneticisi()

    def dosya_okuma_servisi(self):
        return self._dosya_yoneticisi().dosya_okuma_servisi()

    def dosya_yazma_servisi(self):
        return self._dosya_yoneticisi().dosya_yazma_servisi()

    def gecici_dosya_servisi(self):
        return self._dosya_yoneticisi().gecici_dosya_servisi()

    # =========================================================
    # REKLAM
    # =========================================================
    def reklam_yoneticisi(self):
        return self._reklam_yoneticisi()

    def banner_goster(self) -> bool:
        return self._reklam_yoneticisi().banner_goster()

    def banner_goster_gecikmeli(self, delay: float = 1.5) -> bool:
        return self._reklam_yoneticisi().banner_goster_gecikmeli(delay=delay)

    def banner_gizle(self) -> bool:
        return self._reklam_yoneticisi().banner_gizle()

    def banner_baslatildi_mi(self) -> bool:
        return self._reklam_yoneticisi().banner_baslatildi_mi()

    def banner_gosteriliyor_mu(self) -> bool:
        return self._reklam_yoneticisi().banner_gosteriliyor_mu()

    def banner_planlandi_mi(self) -> bool:
        return self._reklam_yoneticisi().banner_planlandi_mi()

    def gecis_reklami_yukle(self) -> bool:
        return self._reklam_yoneticisi().gecis_reklami_yukle()

    def gecis_reklami_hazir_mi(self) -> bool:
        return self._reklam_yoneticisi().gecis_reklami_hazir_mi()

    def gecis_reklami_yukleniyor_mu(self) -> bool:
        return self._reklam_yoneticisi().gecis_reklami_yukleniyor_mu()

    def gecis_reklami_goster(self, sonrasi_callback=None) -> bool:
        return self._reklam_yoneticisi().gecis_reklami_goster(
            sonrasi_callback=sonrasi_callback,
        )

    def gecis_reklami_temizle(self) -> None:
        self._reklam_yoneticisi().gecis_reklami_temizle()

    def test_modu_aktif_mi(self) -> bool:
        return self._reklam_yoneticisi().test_modu_aktif_mi()

    def yayin_modu_aktif_mi(self) -> bool:
        return self._reklam_yoneticisi().yayin_modu_aktif_mi()

    def reklam_modu_etiketi(self) -> str:
        return self._reklam_yoneticisi().reklam_modu_etiketi()

    def aktif_admob_app_id(self) -> str:
        return self._reklam_yoneticisi().aktif_admob_app_id()

    def aktif_banner_reklam_id(self) -> str:
        return self._reklam_yoneticisi().aktif_banner_reklam_id()

    def aktif_interstitial_reklam_id(self) -> str:
        return self._reklam_yoneticisi().aktif_interstitial_reklam_id()

    def aktif_rewarded_reklam_id(self) -> str:
        return self._reklam_yoneticisi().aktif_rewarded_reklam_id()

    def odullu_reklam_goster(self) -> bool:
        return self._reklam_yoneticisi().odullu_reklam_goster()

    # =========================================================
    # GUNCELLEME
    # =========================================================
    def guncelleme_yoneticisi(self):
        return self._guncelleme_yoneticisi()

    def guncelleme_kontrol_aktif_mi(self) -> bool:
        return self._guncelleme_yoneticisi().guncelleme_kontrol_aktif_mi()

    def guncelleme_bildirim_metni(self) -> str:
        return self._guncelleme_yoneticisi().guncelleme_bildirim_metni()

    def guncelleme_buton_metni(self) -> str:
        return self._guncelleme_yoneticisi().guncelleme_buton_metni()

    def play_store_package_name(self) -> str:
        return self._guncelleme_yoneticisi().play_store_package_name()

    def play_store_sayfasini_ac(self, package_name: str = "") -> bool:
        return self._guncelleme_yoneticisi().play_store_sayfasini_ac(
            package_name=package_name
        )

    def guncelleme_bildirimi_gosterilmeli_mi(self) -> bool:
        return self._guncelleme_yoneticisi().guncelleme_bildirimi_gosterilmeli_mi()

    # =========================================================
    # SISTEM
    # =========================================================
    def sistem_yoneticisi(self):
        return self._sistem_yoneticisi()

    def gecici_bildirim_servisi(self):
        return self._sistem_yoneticisi().gecici_bildirim_servisi()

    def log_servisi(self):
        return self._sistem_yoneticisi().log_servisi()

    # =========================================================
    # YEDEK
    # =========================================================
    def yedek_yoneticisi(self):
        return self._yedek_yoneticisi()

    def yedek_listeleme_servisi(self):
        return self._yedek_yoneticisi().yedek_listeleme_servisi()

    def yedek_silme_servisi(self):
        return self._yedek_yoneticisi().yedek_silme_servisi()

    def yedek_indirme_servisi(self):
        return self._yedek_yoneticisi().yedek_indirme_servisi()
