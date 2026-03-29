# -*- coding: utf-8 -*-
"""
DOSYA: app/core/dil_ekle/Yoneticisi.py

ROL:
- dil_gelistirici.py çekirdeğini nesne tabanlı facade ile yönetir
- assets/lang klasöründeki dil dosyası işlemlerini tek sınıfta toplar
- Üst katmanlara deterministik ve sade bir API sunar
- core/dil_ekle/dil_gelistirici.py içindeki fonksiyonları yönetici üzerinden erişilebilir hale getirir

MİMARİ:
- Core yönetici katmanıdır
- UI bilmez
- Service katmanına uygun sade ve deterministik arayüz sunar
- Alt modül çağrılarını tek noktada toplar
- Lazy değil, net modül cache kullanır
- Type güvenliği yüksektir
- Geriye uyumluluk katmanı içermez
- Belirsiz fallback davranışı içermez

SURUM: 1
TARIH: 2026-03-28
IMZA: FY.
"""

from __future__ import annotations

from types import ModuleType
from typing import Any


class DilGelistiriciYonetici:
    """
    Dil geliştirici çekirdeği için nesne tabanlı yönetici.
    """

    __slots__ = (
        "_lang_klasoru",
        "_dg",
    )

    def __init__(self, lang_klasoru: str | None = None) -> None:
        from app.core.dil_ekle import dil_gelistirici as modul

        self._dg: ModuleType = modul
        self._lang_klasoru: str = modul.lang_klasoru_coz(lang_klasoru)

    @property
    def lang_klasoru(self) -> str:
        """
        Aktif dil klasörü yolunu döndürür.
        """
        return self._lang_klasoru

    def lang_klasoru_ayarla(self, lang_klasoru: str | None) -> str:
        """
        Aktif dil klasörünü günceller.
        """
        self._lang_klasoru = self._dg.lang_klasoru_coz(lang_klasoru)
        return self._lang_klasoru

    def varsayilan_lang_klasoru(self) -> str:
        """
        Varsayılan dil klasörünü döndürür.
        """
        return self._dg.varsayilan_lang_klasoru()

    def dil_dosyalarini_listele(self) -> list[dict[str, Any]]:
        """
        Algılanan dil dosyalarını listeler.
        """
        return self._dg.dil_dosyalarini_listele(self._lang_klasoru)

    def dil_kodlarini_listele(self) -> list[str]:
        """
        Algılanan dil kodlarını döndürür.
        """
        return self._dg.dil_kodlarini_listele(self._lang_klasoru)

    def dil_dosyasi_var_mi(self, dil_kodu: str) -> bool:
        """
        Belirli dil dosyasının varlığını kontrol eder.
        """
        return self._dg.dil_dosyasi_var_mi(dil_kodu, self._lang_klasoru)

    def dil_dosyasi_yolu(self, dil_kodu: str) -> str:
        """
        Belirli dil dosyasının tam yolunu döndürür.
        """
        return self._dg.dil_dosyasi_yolu(dil_kodu, self._lang_klasoru)

    def dil_verisini_yukle(self, dil_kodu: str) -> dict[str, Any]:
        """
        Dil json içeriğini yükler.
        """
        return self._dg.dil_verisini_yukle(dil_kodu, self._lang_klasoru)

    def dil_keylerini_getir(
        self,
        dil_kodu: str,
        *,
        meta_dahil: bool = False,
    ) -> list[str]:
        """
        Belirli dil dosyasındaki key listesini döndürür.
        """
        return self._dg.dil_keylerini_getir(
            dil_kodu,
            self._lang_klasoru,
            meta_dahil=meta_dahil,
        )

    def dil_ozeti_getir(self, dil_kodu: str) -> dict[str, Any]:
        """
        Dil dosyasının özet bilgisini döndürür.
        """
        return self._dg.dil_ozeti_getir(dil_kodu, self._lang_klasoru)

    def eksik_keyleri_bul(
        self,
        referans_dil_kodu: str,
        hedef_dil_kodu: str,
    ) -> list[str]:
        """
        Referans dile göre hedef dilde eksik keyleri döndürür.
        """
        return self._dg.eksik_keyleri_bul(
            referans_dil_kodu,
            hedef_dil_kodu,
            self._lang_klasoru,
        )

    def tum_dillerde_eksik_analizi(
        self,
        referans_dil_kodu: str,
    ) -> list[dict[str, Any]]:
        """
        Referans dile göre tüm dillerin eksik analizini döndürür.
        """
        return self._dg.tum_dillerde_eksik_analizi(
            referans_dil_kodu,
            self._lang_klasoru,
        )

    def tek_dile_key_ekle(
        self,
        dil_kodu: str,
        key: str,
        deger: Any = "",
        *,
        varsa_uzerine_yaz: bool = False,
    ) -> dict[str, Any]:
        """
        Tek dile key ekler.
        """
        return self._dg.tek_dile_key_ekle(
            dil_kodu,
            key,
            deger,
            self._lang_klasoru,
            varsa_uzerine_yaz=varsa_uzerine_yaz,
        )

    def coklu_dillere_key_ekle(
        self,
        key: str,
        dil_deger_haritasi: dict[str, Any],
        *,
        eksik_olanlara_ekle: bool = True,
        varsa_uzerine_yaz: bool = False,
    ) -> list[dict[str, Any]]:
        """
        Aynı key'i birden fazla dile ekler.
        """
        return self._dg.coklu_dillere_key_ekle(
            key,
            dil_deger_haritasi,
            self._lang_klasoru,
            eksik_olanlara_ekle=eksik_olanlara_ekle,
            varsa_uzerine_yaz=varsa_uzerine_yaz,
        )

    def tum_dillere_key_ekle(
        self,
        key: str,
        varsayilan_deger: Any = "",
        *,
        referans_dil_kodu: str | None = None,
        referans_degeri_kullan: bool = True,
        varsa_uzerine_yaz: bool = False,
    ) -> list[dict[str, Any]]:
        """
        Aynı key'i tüm dil dosyalarına ekler.
        """
        return self._dg.tum_dillere_key_ekle(
            key,
            varsayilan_deger,
            self._lang_klasoru,
            referans_dil_kodu=referans_dil_kodu,
            referans_degeri_kullan=referans_degeri_kullan,
            varsa_uzerine_yaz=varsa_uzerine_yaz,
        )

    def eksik_keyleri_hedef_dile_ekle(
        self,
        referans_dil_kodu: str,
        hedef_dil_kodu: str,
        *,
        bos_deger_kullan: bool = True,
        varsa_uzerine_yaz: bool = False,
    ) -> dict[str, Any]:
        """
        Referans dildeki eksik keyleri hedef dile ekler.
        """
        return self._dg.eksik_keyleri_hedef_dile_ekle(
            referans_dil_kodu,
            hedef_dil_kodu,
            self._lang_klasoru,
            bos_deger_kullan=bos_deger_kullan,
            varsa_uzerine_yaz=varsa_uzerine_yaz,
        )

    def yeni_dil_sablonu_uret(
        self,
        referans_dil_kodu: str,
        yeni_dil_kodu: str,
        yeni_dil_adi: str,
        *,
        bos_deger_kullan: bool = True,
    ) -> dict[str, Any]:
        """
        Referans dilden yeni dil şablonu üretir.
        """
        return self._dg.yeni_dil_sablonu_uret(
            referans_dil_kodu,
            yeni_dil_kodu,
            yeni_dil_adi,
            self._lang_klasoru,
            bos_deger_kullan=bos_deger_kullan,
        )

    def yeni_dil_dosyasi_olustur(
        self,
        referans_dil_kodu: str,
        yeni_dil_kodu: str,
        yeni_dil_adi: str,
        *,
        bos_deger_kullan: bool = True,
        varsa_uzerine_yaz: bool = False,
    ) -> dict[str, Any]:
        """
        Yeni dil dosyası oluşturur.
        """
        return self._dg.yeni_dil_dosyasi_olustur(
            referans_dil_kodu,
            yeni_dil_kodu,
            yeni_dil_adi,
            self._lang_klasoru,
            bos_deger_kullan=bos_deger_kullan,
            varsa_uzerine_yaz=varsa_uzerine_yaz,
        )