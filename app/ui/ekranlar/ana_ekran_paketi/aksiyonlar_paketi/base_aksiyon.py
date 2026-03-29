# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/ekranlar/ana_ekran_paketi/aksiyonlar_paketi/base_aksiyon.py

ROL:
- Tüm aksiyonlar için ortak feedback (geri bildirim) pipeline sağlar
- Başarı ve hata mesajlarını standart hale getirir
- BilgiKutusu bileşeni ile entegre çalışır
- Mesaj + ikon + pulse animasyon akışını tek noktadan yönetir

MİMARİ:
- UI aksiyon katmanında ortak base mixin olarak kullanılır
- Alt aksiyon mixin'leri bu sınıf üzerinden feedback üretir
- Tekrarlayan mesaj/ikon/pulse kodunu ortadan kaldırır
- Deterministik ve sade bir API sunar (_basari / _hata)
- Geriye uyumluluk katmanı içermez

KULLANIM:
- Alt aksiyonlarda doğrudan self._bilgi.mesaj(...) çağrılmaz
- Bunun yerine:
    self._basari("key")
    self._hata("key")

SURUM: 2
TARIH: 2026-03-28
IMZA: FY.
"""

from __future__ import annotations


class AnaEkranBaseAksiyonMixin:
    """
    Ana ekran aksiyonları için ortak feedback sağlayıcı mixin.

    Özellikler:
    - başarı mesajı üretir (_basari)
    - hata mesajı üretir (_hata)
    - ikon + pulse otomatik uygulanır
    - ikon bulunamazsa fallback kullanır

    Bağımlılıklar:
    - self._t -> çeviri fonksiyonu
    - self._bilgi -> BilgiKutusu instance
    """

    # 👇 ikon fallback sistemi
    _IKON_BASARI = "onaylandi.png"
    _IKON_HATA = "error.png"  # varsa kullanılır
    _IKON_FALLBACK = "onaylandi.png"  # garanti ikon

    def _basari(self, key: str, **fmt) -> None:
        """
        Başarı durumunda kullanıcıya bilgi verir.
        """
        mesaj = self._t(key, **fmt)

        self._bilgi.mesaj(
            mesaj,
            ikon=self._IKON_BASARI or self._IKON_FALLBACK,
            pulse=True,
            hata=False,
        )

    def _hata(self, key: str, **fmt) -> None:
        """
        Hata durumunda kullanıcıya bilgi verir.
        """
        mesaj = self._t(key, **fmt)

        ikon = self._IKON_HATA or self._IKON_FALLBACK

        self._bilgi.mesaj(
            mesaj,
            ikon=ikon,
            pulse=True,
            hata=True,
        )