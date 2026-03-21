# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/root_paketi/yoneticisi.py

ROL:
- root_paketi için tek giriş noktası sağlamak
- Alt root paket yöneticilerine erişimi merkezileştirmek
- RootWidget ve root akışlarını dış dünyaya kontrollü açmak

MİMARİ:
- Alt paket yöneticilerine lazy import ile erişir
- Dış dünya root_paketi içindeki dosya yollarını bilmek zorunda kalmaz
- RootWidget oluşturma ve mixin erişimi tek kapıdan yönetilir

API UYUMLULUK:
- Android ve masaüstü ortamlarıyla uyumludur
- Doğrudan Android bridge çağrısı yapmaz

SURUM: 1
TARIH: 2026-03-20
IMZA: FY.
"""

from __future__ import annotations


class RootPaketiYoneticisi:
    # =========================================================
    # ALT YONETICILER
    # =========================================================
    def _dosya_akisi_yoneticisi(self):
        from app.ui.root_paketi.akisi_dosya import RootDosyaAkisiYoneticisi
        return RootDosyaAkisiYoneticisi()

    def _secim_akisi_yoneticisi(self):
        from app.ui.root_paketi.akisi_secim import RootSecimAkisiYoneticisi
        return RootSecimAkisiYoneticisi()

    def _guncelleme_akisi_yoneticisi(self):
        from app.ui.root_paketi.akisi_guncelleme import RootGuncellemeAkisiYoneticisi
        return RootGuncellemeAkisiYoneticisi()

    def _geri_yukleme_akisi_yoneticisi(self):
        from app.ui.root_paketi.akisi_geri_yukleme import RootGeriYuklemeAkisiYoneticisi
        return RootGeriYuklemeAkisiYoneticisi()

    def _durum_yoneticisi(self):
        from app.ui.root_paketi.durum import RootDurumYoneticisi
        return RootDurumYoneticisi()

    def _kaydirma_yoneticisi(self):
        from app.ui.root_paketi.kaydirma import RootKaydirmaYoneticisi
        return RootKaydirmaYoneticisi()

    def _yardimci_yoneticisi(self):
        from app.ui.root_paketi.yardimci import RootYardimciYoneticisi
        return RootYardimciYoneticisi()

    def _bagimlilik_yoneticisi(self):
        from app.ui.root_paketi.bagimlilik import RootBagimlilikYoneticisi
        return RootBagimlilikYoneticisi()

    def _root_yoneticisi(self):
        from app.ui.root_paketi.root import RootWidgetYoneticisi
        return RootWidgetYoneticisi()

    # =========================================================
    # ROOT
    # =========================================================
    def root_widget_sinifi(self):
        return self._root_yoneticisi().root_widget_sinifi()

    def root_widget_olustur(self, **kwargs):
        return self._root_yoneticisi().root_widget_olustur(**kwargs)

    # =========================================================
    # MIXIN SINIFLARI
    # =========================================================
    def root_dosya_akisi_mixin(self):
        return self._dosya_akisi_yoneticisi().mixin_sinifi()

    def root_secim_akisi_mixin(self):
        return self._secim_akisi_yoneticisi().mixin_sinifi()

    def root_guncelleme_akisi_mixin(self):
        return self._guncelleme_akisi_yoneticisi().mixin_sinifi()

    def root_geri_yukleme_akisi_mixin(self):
        return self._geri_yukleme_akisi_yoneticisi().mixin_sinifi()

    def root_durum_mixin(self):
        return self._durum_yoneticisi().mixin_sinifi()

    def root_kaydirma_mixin(self):
        return self._kaydirma_yoneticisi().mixin_sinifi()

    def root_yardimci_mixin(self):
        return self._yardimci_yoneticisi().mixin_sinifi()

    def root_lazy_imports_mixin(self):
        return self._bagimlilik_yoneticisi().mixin_sinifi()