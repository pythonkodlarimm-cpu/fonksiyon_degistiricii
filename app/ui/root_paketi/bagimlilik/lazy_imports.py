# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/root_paketi/bagimlilik/lazy_imports.py

ROL:
- Root katmanında kullanılan tüm bağımlılıkları merkezi olarak sağlamak
- Sadece yöneticiler ve kontrollü action metotları üzerinden erişim vermek
- UI katmanını servis implementasyonlarından tamamen izole etmek
- Root katmanında dependency injection benzeri bir erişim katmanı sunmak

MİMARİ:
- Eski fonksiyon tabanlı servisler kaldırılmıştır
- Core erişimi CoreYoneticisi üzerinden yapılır
- Services erişimi ServicesYoneticisi üzerinden yapılır
- Lazy import ile performans ve modülerlik korunur
- Root katmanı alt modül yollarını doğrudan bilmez
- Reklam erişimi servis nesnesi değil, yönetici/action API üzerinden sağlanır
- Bu dosya root paketinin bağımlılık geçiş katmanıdır

UYUMLULUK:
- Android ve masaüstü ortamlarda çalışabilecek yapıdadır
- Doğrudan Android bridge çağrısı içermez
- API 35 hedefli Android mimarisi ile uyumludur

SURUM: 7
TARIH: 2026-03-22
IMZA: FY.
"""

from __future__ import annotations


class RootLazyImportsMixin:
    """
    Root katmanında kullanılan bağımlılıklara lazy import ile erişim sağlayan mixin.

    Bu sınıfın amacı:
    - Root içindeki akışların doğrudan alt modül dosya yollarını bilmesini engellemek
    - Core ve Services katmanını merkezi şekilde sunmak
    - Refactor sırasında import kırılmalarını azaltmak
    - UI katmanını servis implementasyon detaylarından ayırmaktır
    """

    # =========================================================
    # CORE
    # =========================================================
    def _get_core_yoneticisi(self):
        """
        Core yöneticisini döner.

        Returns:
            CoreYoneticisi: Uygulamanın çekirdek yöneticisi
        """
        from app.core import CoreYoneticisi
        return CoreYoneticisi()

    # =========================================================
    # SERVICES
    # =========================================================
    def _get_services_yoneticisi(self):
        """
        Services yöneticisini döner.

        Returns:
            ServicesYoneticisi: Servis katmanının merkez yöneticisi
        """
        from app.services import ServicesYoneticisi
        return ServicesYoneticisi()

    # =========================================================
    # SERVICE YONETICILERI
    # =========================================================
    def _get_belge_yoneticisi(self):
        """
        Belge yöneticisini döner.
        """
        return self._get_services_yoneticisi().belge_yoneticisi()

    def _get_dosya_yoneticisi(self):
        """
        Dosya yöneticisini döner.
        """
        return self._get_services_yoneticisi().dosya_yoneticisi()

    def _get_sistem_yoneticisi(self):
        """
        Sistem yöneticisini döner.
        """
        return self._get_services_yoneticisi().sistem_yoneticisi()

    def _get_analiz_yoneticisi(self):
        """
        Analiz yöneticisini döner.
        """
        return self._get_services_yoneticisi().analiz_yoneticisi()

    def _get_reklam_yoneticisi(self):
        """
        Reklam yöneticisini döner.
        """
        return self._get_services_yoneticisi().reklam_yoneticisi()

    def _get_android_yoneticisi(self):
        """
        Android yöneticisini döner.
        """
        return self._get_services_yoneticisi().android_yoneticisi()

    def _get_yedek_yoneticisi(self):
        """
        Yedek yöneticisini döner.
        """
        return self._get_services_yoneticisi().yedek_yoneticisi()

    # =========================================================
    # SERVICE NESNELERI
    # =========================================================
    def _get_gecici_bildirim_servisi(self):
        """
        Geçici bildirim servisini döner.
        """
        return self._get_services_yoneticisi().gecici_bildirim_servisi()

    def _get_replace_karar_servisi(self):
        """
        Replace karar servisini oluşturur ve döner.
        """
        return self._get_services_yoneticisi().replace_karar_servisi_olustur()

    def _get_android_belge_servisi(self):
        """
        Android belge servisini döner.
        """
        return self._get_services_yoneticisi().android_belge_servisi()

    def _get_android_ozel_izin_servisi(self):
        """
        Android özel izin servisini döner.
        """
        return self._get_services_yoneticisi().android_ozel_izin_servisi()

    def _get_android_reklam_kopru_servisi(self):
        """
        Android reklam köprü servisini döner.
        """
        return self._get_services_yoneticisi().android_reklam_kopru_servisi()

    def _get_android_uri_servisi(self):
        """
        Android URI servisini döner.
        """
        return self._get_services_yoneticisi().android_uri_servisi()

    def _get_belge_oturumu_servisi(self):
        """
        Belge oturumu servisini döner.
        """
        return self._get_services_yoneticisi().belge_oturumu_servisi()

    def _get_belge_ice_aktarma_servisi(self):
        """
        Belge içe aktarma servisini döner.
        """
        return self._get_services_yoneticisi().belge_ice_aktarma_servisi()

    def _get_belge_kaydetme_servisi(self):
        """
        Belge kaydetme servisini döner.
        """
        return self._get_services_yoneticisi().belge_kaydetme_servisi()

    def _get_dosya_okuma_servisi(self):
        """
        Dosya okuma servisini döner.
        """
        return self._get_services_yoneticisi().dosya_okuma_servisi()

    def _get_dosya_yazma_servisi(self):
        """
        Dosya yazma servisini döner.
        """
        return self._get_services_yoneticisi().dosya_yazma_servisi()

    def _get_gecici_dosya_servisi(self):
        """
        Geçici dosya servisini döner.
        """
        return self._get_services_yoneticisi().gecici_dosya_servisi()

    def _get_log_servisi(self):
        """
        Log servisini döner.
        """
        return self._get_services_yoneticisi().log_servisi()

    def _get_yedek_listeleme_servisi(self):
        """
        Yedek listeleme servisini döner.
        """
        return self._get_services_yoneticisi().yedek_listeleme_servisi()

    def _get_yedek_silme_servisi(self):
        """
        Yedek silme servisini döner.
        """
        return self._get_services_yoneticisi().yedek_silme_servisi()

    def _get_yedek_indirme_servisi(self):
        """
        Yedek indirme servisini döner.
        """
        return self._get_services_yoneticisi().yedek_indirme_servisi()

    # =========================================================
    # REKLAM (ACTION API)
    # =========================================================
    def _banner_goster(self) -> bool:
        """
        Banner reklamı hemen göstermeyi dener.

        Returns:
            bool: İşlem başarılıysa True
        """
        return self._get_services_yoneticisi().banner_goster()

    def _banner_goster_gecikmeli(self, delay: float = 1.5) -> bool:
        """
        Banner reklamı gecikmeli göstermeyi planlar.

        Args:
            delay (float): Saniye cinsinden gecikme süresi

        Returns:
            bool: Planlama başarılıysa True
        """
        return self._get_services_yoneticisi().banner_goster_gecikmeli(delay=delay)

    def _banner_gizle(self) -> bool:
        """
        Banner reklamı gizlemeyi dener.

        Returns:
            bool: İşlem başarılıysa True
        """
        return self._get_services_yoneticisi().banner_gizle()

    def _banner_gosteriliyor_mu(self) -> bool:
        """
        Banner reklamın görünür durumda olup olmadığını döner.

        Returns:
            bool: Banner görünüyorsa True
        """
        return self._get_services_yoneticisi().banner_gosteriliyor_mu()

    def _banner_baslatildi_mi(self) -> bool:
        """
        Banner reklamın başlatılmış olup olmadığını döner.

        Returns:
            bool: Banner başlatıldıysa True
        """
        return self._get_services_yoneticisi().banner_baslatildi_mi()

    def _banner_planlandi_mi(self) -> bool:
        """
        Banner reklamın gecikmeli başlatma için planlanmış olup olmadığını döner.

        Returns:
            bool: Banner planlandıysa True
        """
        return self._get_services_yoneticisi().banner_planlandi_mi()

    def _reklam_modu(self) -> str:
        """
        Aktif reklam modu etiketini döner.

        Returns:
            str: TEST veya YAYIN
        """
        return self._get_services_yoneticisi().reklam_modu_etiketi()

    def _aktif_admob_app_id(self) -> str:
        """
        Aktif AdMob App ID değerini döner.

        Returns:
            str: Aktif App ID
        """
        return self._get_services_yoneticisi().aktif_admob_app_id()

    def _aktif_banner_reklam_id(self) -> str:
        """
        Aktif banner reklam ID değerini döner.

        Returns:
            str: Aktif banner reklam ID
        """
        return self._get_services_yoneticisi().aktif_banner_reklam_id()

    def _aktif_interstitial_reklam_id(self) -> str:
        """
        Aktif interstitial reklam ID değerini döner.

        Returns:
            str: Aktif interstitial reklam ID
        """
        return self._get_services_yoneticisi().aktif_interstitial_reklam_id()

    def _aktif_rewarded_reklam_id(self) -> str:
        """
        Aktif rewarded reklam ID değerini döner.

        Returns:
            str: Aktif rewarded reklam ID
        """
        return self._get_services_yoneticisi().aktif_rewarded_reklam_id()

    # =========================================================
    # UI
    # =========================================================
    def _get_document_selection_class(self):
        """
        DocumentSelection sınıfını döner.
        """
        from app.ui.dosya_secici_paketi.models import DocumentSelection
        return DocumentSelection

    def _get_replace_karar_popup_class(self):
        """
        ReplaceKararPopup sınıfını döner.
        """
        from app.ui.replace_karar_popup import ReplaceKararPopup
        return ReplaceKararPopup

    def _get_gecici_bildirim_katmani_class(self):
        """
        GeciciBildirimKatmani sınıfını döner.
        """
        from app.ui.gecici_bildirim import GeciciBildirimKatmani
        return GeciciBildirimKatmani

    def _get_kart_class(self):
        """
        Kart sınıfını döner.
        """
        from app.ui.kart import Kart
        return Kart

    # =========================================================
    # ROOT PAKETI YONETICILERI
    # =========================================================
    def _get_root_paketi_yoneticisi(self):
        """
        Root paketi yöneticisini döner.
        """
        from app.ui.root_paketi import RootPaketiYoneticisi
        return RootPaketiYoneticisi()

    def _get_root_dosya_akisi_yoneticisi(self):
        """
        Root dosya akışı yöneticisini döner.
        """
        return self._get_root_paketi_yoneticisi()._dosya_akisi_yoneticisi()

    def _get_root_secim_akisi_yoneticisi(self):
        """
        Root seçim akışı yöneticisini döner.
        """
        return self._get_root_paketi_yoneticisi()._secim_akisi_yoneticisi()

    def _get_root_guncelleme_akisi_yoneticisi(self):
        """
        Root güncelleme akışı yöneticisini döner.
        """
        return self._get_root_paketi_yoneticisi()._guncelleme_akisi_yoneticisi()

    def _get_root_geri_yukleme_akisi_yoneticisi(self):
        """
        Root geri yükleme akışı yöneticisini döner.
        """
        return self._get_root_paketi_yoneticisi()._geri_yukleme_akisi_yoneticisi()

    def _get_root_durum_yoneticisi(self):
        """
        Root durum yöneticisini döner.
        """
        return self._get_root_paketi_yoneticisi()._durum_yoneticisi()

    def _get_root_kaydirma_yoneticisi(self):
        """
        Root kaydırma yöneticisini döner.
        """
        return self._get_root_paketi_yoneticisi()._kaydirma_yoneticisi()

    def _get_root_yardimci_yoneticisi(self):
        """
        Root yardımcı yöneticisini döner.
        """
        return self._get_root_paketi_yoneticisi()._yardimci_yoneticisi()
