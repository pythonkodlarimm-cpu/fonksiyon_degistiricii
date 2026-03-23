# -*- coding: utf-8 -*-
"""
DOSYA: app/services/guncelleme/yoneticisi.py

ROL:
- Güncelleme katmanına tek giriş noktası sağlamak
- Play Store güncelleme yönlendirmesini merkezileştirmek
- Uzak version.json kontrol akışını yönetmek
- UI katmanının alt güncelleme servis detaylarını bilmesini engellemek

MİMARİ:
- Alt güncelleme servislerine lazy import ile erişir
- Root ve diğer UI katmanları sadece bu yöneticiyi bilir
- Güncelleme davranışı tek merkezden yönetilir

API UYUMLULUK:
- Android API 35 uyumlu
- Play Store yönlendirme akışına uygundur
- Ek kullanıcı izni gerektirmez

SURUM: 2
TARIH: 2026-03-23
IMZA: FY.
"""

from __future__ import annotations


class GuncellemeYoneticisi:
    def guncelleme_kontrol_aktif_mi(self) -> bool:
        from app.services.guncelleme.ayarlari import GUNCELLEME_KONTROL_AKTIF
        return bool(GUNCELLEME_KONTROL_AKTIF)

    def guncelleme_bildirim_metni(self) -> str:
        from app.services.guncelleme.ayarlari import GUNCELLEME_BILDIRIM_METNI
        return str(GUNCELLEME_BILDIRIM_METNI)

    def guncelleme_buton_metni(self) -> str:
        from app.services.guncelleme.ayarlari import GUNCELLEME_BUTON_METNI
        return str(GUNCELLEME_BUTON_METNI)

    def play_store_package_name(self) -> str:
        from app.services.guncelleme.ayarlari import PLAY_STORE_PACKAGE_NAME
        return str(PLAY_STORE_PACKAGE_NAME)

    def play_store_sayfasini_ac(self, package_name: str = "") -> bool:
        from app.services.guncelleme.play_store_guncelleme_servisi import (
            play_store_sayfasini_ac,
        )
        return play_store_sayfasini_ac(package_name=package_name)

    def guncelleme_durumu_hesapla(self, mevcut_surum: str) -> dict:
        from app.services.guncelleme.versiyon_kontrol_servisi import (
            guncelleme_durumu_hesapla,
        )
        return guncelleme_durumu_hesapla(mevcut_surum=mevcut_surum)