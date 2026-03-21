# -*- coding: utf-8 -*-
"""
DOSYA: app/core/meta/yoneticisi.py

ROL:
- Uygulama metadata katmanına tek giriş noktası sağlamak
- Sabitler ve sürüm bilgilerini merkezileştirmek
- Üst katmanın sabitler.py detaylarını bilmesini engellemek

MİMARİ:
- Lazy import kullanır
- UI ve uygulama başlangıcı bu yöneticiyi kullanmalıdır
- Android / APK tarafında güvenli metadata erişimi sağlar

SURUM: 1
TARIH: 2026-03-19
IMZA: FY.
"""

from __future__ import annotations


class MetaYoneticisi:
    def _modul(self):
        from app.core.meta import sabitler
        return sabitler

    def uygulama_adi(self) -> str:
        return str(self._modul().UYGULAMA_ADI)

    def paket_adi(self) -> str:
        return str(self._modul().PAKET_ADI)

    def surum(self) -> str:
        return str(self._modul().SURUM)

    def build(self) -> int:
        return int(self._modul().BUILD)

    def tarih(self) -> str:
        return str(self._modul().TARIH)

    def imza(self) -> str:
        return str(self._modul().IMZA)

    def aciklama(self) -> str:
        return str(self._modul().ACIKLAMA)

    def tam_surum(self) -> str:
        return str(self._modul().tam_surum())

    def apk_surum_kodu(self) -> int:
        return int(self._modul().apk_surum_kodu())

    def apk_surum_adi(self) -> str:
        return str(self._modul().apk_surum_adi())

    def uygulama_etiketi(self) -> str:
        return str(self._modul().uygulama_etiketi())

    def meta_bilgisi(self) -> dict:
        return dict(self._modul().meta_bilgisi())