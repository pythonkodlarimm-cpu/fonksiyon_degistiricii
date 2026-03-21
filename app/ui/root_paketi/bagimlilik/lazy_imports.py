# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/root_paketi/bagimlilik/lazy_imports.py

ROL:
- Root katmanında kullanılan tüm bağımlılıkları merkezi olarak sağlamak
- Sadece yöneticiler üzerinden erişim vermek
- UI katmanını servis implementasyonlarından tamamen izole etmek

MİMARİ:
- Eski fonksiyon tabanlı servisler kaldırıldı
- Core erişimi CoreYoneticisi üzerinden yapılır
- Services erişimi ServicesYoneticisi üzerinden yapılır
- Lazy import ile performans ve modülerlik sağlanır
- Bu dosya sistemin dependency injection katmanıdır
- Root paketinin alt bağımlılık modülüdür

SURUM: 6
TARIH: 2026-03-20
IMZA: FY.
"""

from __future__ import annotations


class RootLazyImportsMixin:
    # =========================================================
    # CORE
    # =========================================================
    def _get_core_yoneticisi(self):
        from app.core import CoreYoneticisi
        return CoreYoneticisi()

    # =========================================================
    # SERVICES
    # =========================================================
    def _get_services_yoneticisi(self):
        from app.services import ServicesYoneticisi
        return ServicesYoneticisi()

    # =========================================================
    # SERVICE YONETICILERI
    # =========================================================
    def _get_belge_yoneticisi(self):
        return self._get_services_yoneticisi().belge_yoneticisi()

    def _get_dosya_yoneticisi(self):
        return self._get_services_yoneticisi().dosya_yoneticisi()

    def _get_sistem_yoneticisi(self):
        return self._get_services_yoneticisi().sistem_yoneticisi()

    def _get_analiz_yoneticisi(self):
        return self._get_services_yoneticisi().analiz_yoneticisi()

    def _get_reklam_yoneticisi(self):
        return self._get_services_yoneticisi().reklam_yoneticisi()

    def _get_android_yoneticisi(self):
        return self._get_services_yoneticisi().android_yoneticisi()

    def _get_yedek_yoneticisi(self):
        return self._get_services_yoneticisi().yedek_yoneticisi()

    # =========================================================
    # SERVICE NESNELERI
    # =========================================================
    def _get_gecici_bildirim_servisi(self):
        return self._get_services_yoneticisi().gecici_bildirim_servisi()

    def _get_replace_karar_servisi(self):
        return self._get_services_yoneticisi().replace_karar_servisi_olustur()

    def _get_android_belge_servisi(self):
        return self._get_services_yoneticisi().android_belge_servisi()

    def _get_android_ozel_izin_servisi(self):
        return self._get_services_yoneticisi().android_ozel_izin_servisi()

    def _get_android_reklam_kopru_servisi(self):
        return self._get_services_yoneticisi().android_reklam_kopru_servisi()

    def _get_android_uri_servisi(self):
        return self._get_services_yoneticisi().android_uri_servisi()

    def _get_belge_oturumu_servisi(self):
        return self._get_services_yoneticisi().belge_oturumu_servisi()

    def _get_belge_ice_aktarma_servisi(self):
        return self._get_services_yoneticisi().belge_ice_aktarma_servisi()

    def _get_belge_kaydetme_servisi(self):
        return self._get_services_yoneticisi().belge_kaydetme_servisi()

    def _get_dosya_okuma_servisi(self):
        return self._get_services_yoneticisi().dosya_okuma_servisi()

    def _get_dosya_yazma_servisi(self):
        return self._get_services_yoneticisi().dosya_yazma_servisi()

    def _get_gecici_dosya_servisi(self):
        return self._get_services_yoneticisi().gecici_dosya_servisi()

    def _get_banner_servisi(self):
        return self._get_services_yoneticisi().banner_servisi()

    def _get_log_servisi(self):
        return self._get_services_yoneticisi().log_servisi()

    def _get_yedek_listeleme_servisi(self):
        return self._get_services_yoneticisi().yedek_listeleme_servisi()

    def _get_yedek_silme_servisi(self):
        return self._get_services_yoneticisi().yedek_silme_servisi()

    def _get_yedek_indirme_servisi(self):
        return self._get_services_yoneticisi().yedek_indirme_servisi()

    # =========================================================
    # UI
    # =========================================================
    def _get_document_selection_class(self):
        from app.ui.dosya_secici_paketi.models import DocumentSelection
        return DocumentSelection

    def _get_replace_karar_popup_class(self):
        from app.ui.replace_karar_popup import ReplaceKararPopup
        return ReplaceKararPopup

    def _get_gecici_bildirim_katmani_class(self):
        from app.ui.gecici_bildirim import GeciciBildirimKatmani
        return GeciciBildirimKatmani

    def _get_kart_class(self):
        from app.ui.kart import Kart
        return Kart

    # =========================================================
    # ROOT PAKETI YONETICILERI
    # =========================================================
    def _get_root_paketi_yoneticisi(self):
        from app.ui.root_paketi import RootPaketiYoneticisi
        return RootPaketiYoneticisi()

    def _get_root_dosya_akisi_yoneticisi(self):
        return self._get_root_paketi_yoneticisi()._dosya_akisi_yoneticisi()

    def _get_root_secim_akisi_yoneticisi(self):
        return self._get_root_paketi_yoneticisi()._secim_akisi_yoneticisi()

    def _get_root_guncelleme_akisi_yoneticisi(self):
        return self._get_root_paketi_yoneticisi()._guncelleme_akisi_yoneticisi()

    def _get_root_geri_yukleme_akisi_yoneticisi(self):
        return self._get_root_paketi_yoneticisi()._geri_yukleme_akisi_yoneticisi()

    def _get_root_durum_yoneticisi(self):
        return self._get_root_paketi_yoneticisi()._durum_yoneticisi()

    def _get_root_kaydirma_yoneticisi(self):
        return self._get_root_paketi_yoneticisi()._kaydirma_yoneticisi()

    def _get_root_yardimci_yoneticisi(self):
        return self._get_root_paketi_yoneticisi()._yardimci_yoneticisi()