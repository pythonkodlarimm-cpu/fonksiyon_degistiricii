# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/root_paketi/akisi_dosya/yoneticisi.py

ROL:
- Root dosya akışı katmanına tek giriş noktası sağlamak
- RootDosyaAkisiMixin erişimini merkezileştirmek
- Root paketi üst yöneticisinin bu katmana güvenli erişmesini sağlamak

MİMARİ:
- Lazy import kullanır
- Alt modül detaylarını dış dünyaya sızdırmaz
- RootPaketiYoneticisi ile entegre çalışır

API UYUMLULUK:
- Android ve masaüstü ortamlarıyla uyumludur
- Doğrudan platform bağımlı çağrı içermez

SURUM: 2
TARIH: 2026-03-20
IMZA: FY.
"""

from __future__ import annotations


class RootDosyaAkisiYoneticisi:
    """
    Root dosya akışı mixin sınıfına erişim sağlayan yönetici.

    Bu sınıfın görevi:
    - RootDosyaAkisiMixin sınıfını lazy import ile yüklemek
    - Root paketi üst katmanının alt dosya akışı modülünü doğrudan bilmesini engellemek
    - Modüler mimaride tek giriş noktası sunmaktır
    """

    def mixin_sinifi(self):
        """
        Root dosya akışı mixin sınıfını döndürür.

        Returns:
            type: RootDosyaAkisiMixin sınıfı
        """
        from app.ui.root_paketi.akisi_dosya.dosya_akisi import RootDosyaAkisiMixin
        return RootDosyaAkisiMixin