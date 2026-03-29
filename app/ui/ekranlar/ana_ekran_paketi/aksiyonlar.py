# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/ekranlar/ana_ekran_paketi/aksiyonlar.py

ROL:
- Ana ekran aksiyon mixin facade dosyasıdır
- Alt aksiyon mixin dosyalarını tek sınıfta birleştirir
- UI katmanının tek noktadan import yapmasını sağlar
- Aksiyon katmanını deterministik ve modüler tutar

MİMARİ:
- Yerleşim kodu içermez
- Her aksiyon ayrı mixin dosyasındadır
- Facade yalnızca birleştirici görev görür
- Lazy import yok → doğrudan ve net çözümleme
- Type güvenliği korunur (her mixin açıkça tanımlı)
- Alt yöneticiler tekrar oluşturulmaz
- Geriye uyumluluk katmanı içermez

PERFORMANS:
- Import zinciri minimal ve sabittir
- Runtime lookup yok
- Deterministik MRO (method resolution order)

SURUM: 3
TARIH: 2026-03-28
IMZA: FY.
"""

from __future__ import annotations

# =========================================================
# CORE AKSIYON MIXINLER
# =========================================================

from app.ui.ekranlar.ana_ekran_paketi.aksiyonlar_paketi import (
    AnaEkranDilAksiyonMixin,
    AnaEkranGelistiriciAksiyonMixin,
    AnaEkranGuncellemeAksiyonMixin,
    AnaEkranMenuAksiyonMixin,
    AnaEkranSecimAksiyonMixin,
    AnaEkranTaramaAksiyonMixin,
    AnaEkranYedekAksiyonMixin,
)

from app.ui.ekranlar.ana_ekran_paketi.aksiyonlar_paketi.base_aksiyon import (
    AnaEkranBaseAksiyonMixin,
)

# =========================================================
# YENİ AKSIYONLAR
# =========================================================

from app.ui.ekranlar.ana_ekran_paketi.aksiyonlar_paketi.temizle import (
    AnaEkranTemizleAksiyonMixin,
)

from app.ui.ekranlar.ana_ekran_paketi.aksiyonlar_paketi.yapistir import (
    AnaEkranYapistirAksiyonMixin,
)


# =========================================================
# FACADE
# =========================================================

class AnaEkranAksiyonMixin(
    AnaEkranBaseAksiyonMixin,

    # çekirdek akış
    AnaEkranSecimAksiyonMixin,
    AnaEkranTaramaAksiyonMixin,
    AnaEkranGuncellemeAksiyonMixin,
    AnaEkranYedekAksiyonMixin,

    # UI / sistem aksiyonları
    AnaEkranMenuAksiyonMixin,
    AnaEkranDilAksiyonMixin,
    AnaEkranGelistiriciAksiyonMixin,

    # 🔥 yeni aksiyonlar (en altta → override güvenliği)
    AnaEkranTemizleAksiyonMixin,
    AnaEkranYapistirAksiyonMixin,
):
    """
    Ana ekran için birleşik aksiyon mixin sınıfı.

    Özellikler:
    - Tek noktadan aksiyon erişimi sağlar
    - MRO sırası deterministik olarak ayarlanmıştır
    - Yeni aksiyonlar en alta eklenir (override güvenliği)
    - UI katmanı sadece bu sınıfı bilir

    Not:
    - Bu sınıf içinde metod yazılmaz
    - Tüm aksiyonlar alt mixinlerde tanımlıdır
    """

    __slots__ = ()  # 🔥 micro-perf + bellek optimizasyonu

    pass


__all__ = (
    "AnaEkranAksiyonMixin",
)