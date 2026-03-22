# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/root_paketi/bagimlilik/yoneticisi.py

ROL:
- Root katmanındaki bağımlılık yönetimini merkezileştirir
- RootLazyImportsMixin sınıfına tek noktadan erişim sağlar
- RootWidget ve diğer root bileşenlerinin doğrudan dosya yoluna bağımlı olmasını engeller

MİMARİ:
- Lazy import prensibi kullanılır
- Root katmanı doğrudan alt modül dosyalarını bilmez
- Bağımlılık katmanı, üst katman ile alt modüller arasında izolasyon sağlar
- Refactor sırasında import kırılmalarını minimize eder

KULLANIM:
- RootPaketiYoneticisi üzerinden çağrılır
- RootWidget içinde dolaylı olarak kullanılır
- Sadece mixin sınıfı döner, instance üretmez

UYUMLULUK:
- Android ve masaüstü platformlarıyla uyumludur
- Platforma özel kod içermez

SURUM: 2
TARIH: 2026-03-22
IMZA: FY.
"""

from __future__ import annotations


class RootBagimlilikYoneticisi:
    """
    Root bağımlılık katmanı yöneticisi.

    Bu sınıf, root katmanında kullanılan mixin'lerin
    doğrudan import edilmesini engelleyerek,
    bağımlılıkları merkezi ve kontrollü şekilde sağlar.
    """

    def mixin_sinifi(self):
        """
        RootLazyImportsMixin sınıfını döner.

        Returns:
            type: RootLazyImportsMixin sınıfı
        """
        from app.ui.root_paketi.bagimlilik.lazy_imports import RootLazyImportsMixin
        return RootLazyImportsMixin
