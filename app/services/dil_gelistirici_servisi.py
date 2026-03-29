# -*- coding: utf-8 -*-
"""
DOSYA: app/services/dil_gelistirici_servisi.py

ROL:
- Dil geliştirici işlemlerini service katmanında sunar
- UI ile core/dil_ekle yöneticisi arasında facade görevi görür
- assets/lang klasöründeki dil dosyalarını yönetmek için sade API sağlar
- Mevcut dil dosyalarını algılama, eksik key analizi, yeni key ekleme
  ve yeni dil dosyası oluşturma akışlarını dış katmana taşır

MİMARİ:
- Service katmanıdır
- UI core detaylarını bilmez
- CoreYoneticisi üzerinden entegre çalışır
- Lazy + cache mantığı core katmanında korunur
- Geriye uyumluluk katmanı içermez
- Deterministik ve type-safe akış hedeflenir

ENTEGRASYON:
- app.core.yoneticisi.CoreYoneticisi ile entegredir
- Core içindeki dil_gelistirici / dil_ekle yöneticisini kullanır
- Dış katman yalnızca bu servis sınıfını çağırır

SURUM: 2
TARIH: 2026-03-28
IMZA: FY.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from app.core.yoneticisi import CoreYoneticisi

if TYPE_CHECKING:
    from app.core.dil_ekle.yoneticisi import DilGelistiriciYonetici


class DilGelistiriciServisi:
    """
    Dil geliştirici işlemleri için service facade sınıfı.
    """

    __slots__ = (
        "_core",
    )

    def __init__(self, core: CoreYoneticisi | None = None) -> None:
        self._core: CoreYoneticisi = core if core is not None else CoreYoneticisi()

    @property
    def core(self) -> CoreYoneticisi:
        """
        Aktif core yöneticisini döndürür.
        """
        return self._core

    def _yonetici(self) -> DilGelistiriciYonetici:
        """
        Core içindeki dil geliştirici yöneticisini döndürür.
        """
        return self._core.dil_gelistirici()

    # =========================================================
    # LANG KLASORU
    # =========================================================
    def lang_klasoru(self) -> str:
        """
        Aktif lang klasörü yolunu döndürür.
        """
        return self._yonetici().lang_klasoru

    def lang_klasoru_ayarla(self, lang_klasoru: str | None) -> str:
        """
        Aktif lang klasörünü günceller.
        """
        return self._yonetici().lang_klasoru_ayarla(lang_klasoru)

    def varsayilan_lang_klasoru(self) -> str:
        """
        Varsayılan lang klasörü yolunu döndürür.
        """
        return self._yonetici().varsayilan_lang_klasoru()

    # =========================================================
    # DIL DOSYALARI
    # =========================================================
    def dilleri_listele(self) -> list[dict[str, Any]]:
        """
        Algılanan dil dosyalarını listeler.
        """
        return self._yonetici().dil_dosyalarini_listele()

    def dil_kodlarini_listele(self) -> list[str]:
        """
        Algılanan dil kodlarını döndürür.
        """
        return self._yonetici().dil_kodlarini_listele()

    def dil_var_mi(self, dil_kodu: str) -> bool:
        """
        Belirli dil dosyası mevcut mu kontrol eder.
        """
        return self._yonetici().dil_dosyasi_var_mi(dil_kodu)

    def dil_dosyasi_yolu(self, dil_kodu: str) -> str:
        """
        Belirli dil dosyasının tam yolunu döndürür.
        """
        return self._yonetici().dil_dosyasi_yolu(dil_kodu)

    def dil_verisini_getir(self, dil_kodu: str) -> dict[str, Any]:
        """
        İstenen dil dosyasının json içeriğini döndürür.
        """
        return self._yonetici().dil_verisini_yukle(dil_kodu)

    def dil_ozeti_getir(self, dil_kodu: str) -> dict[str, Any]:
        """
        İstenen dil dosyasının özet bilgisini döndürür.
        """
        return self._yonetici().dil_ozeti_getir(dil_kodu)

    def dil_keylerini_getir(
        self,
        dil_kodu: str,
        *,
        meta_dahil: bool = False,
    ) -> list[str]:
        """
        İstenen dil dosyasındaki key listesini döndürür.
        """
        return self._yonetici().dil_keylerini_getir(
            dil_kodu,
            meta_dahil=meta_dahil,
        )

    # =========================================================
    # EKSIK KEY ANALIZI
    # =========================================================
    def eksik_keyleri_getir(
        self,
        referans_dil_kodu: str,
        hedef_dil_kodu: str,
    ) -> list[str]:
        """
        Referans dil dosyasına göre hedef dilde eksik keyleri döndürür.
        """
        return self._yonetici().eksik_keyleri_bul(
            referans_dil_kodu,
            hedef_dil_kodu,
        )

    def tum_dillerde_eksik_analizi(
        self,
        referans_dil_kodu: str,
    ) -> list[dict[str, Any]]:
        """
        Referans dile göre tüm diller için eksik key analizini döndürür.
        """
        return self._yonetici().tum_dillerde_eksik_analizi(referans_dil_kodu)

    def eksik_keyleri_hedef_dile_ekle(
        self,
        referans_dil_kodu: str,
        hedef_dil_kodu: str,
        *,
        bos_deger_kullan: bool = True,
        varsa_uzerine_yaz: bool = False,
    ) -> dict[str, Any]:
        """
        Referans dilde bulunan ama hedef dilde olmayan keyleri hedef dile ekler.
        """
        return self._yonetici().eksik_keyleri_hedef_dile_ekle(
            referans_dil_kodu,
            hedef_dil_kodu,
            bos_deger_kullan=bos_deger_kullan,
            varsa_uzerine_yaz=varsa_uzerine_yaz,
        )

    # =========================================================
    # KEY EKLEME
    # =========================================================
    def tek_dile_key_ekle(
        self,
        dil_kodu: str,
        key: str,
        deger: str = "",
        *,
        varsa_uzerine_yaz: bool = False,
    ) -> dict[str, Any]:
        """
        Tek bir dil dosyasına key ekler.
        """
        return self._yonetici().tek_dile_key_ekle(
            dil_kodu,
            key,
            deger,
            varsa_uzerine_yaz=varsa_uzerine_yaz,
        )

    def coklu_dillere_key_ekle(
        self,
        key: str,
        dil_deger_haritasi: dict[str, str],
        *,
        eksik_olanlara_ekle: bool = True,
        varsa_uzerine_yaz: bool = False,
    ) -> list[dict[str, Any]]:
        """
        Aynı key'i birden fazla dil dosyasına ekler.
        """
        return self._yonetici().coklu_dillere_key_ekle(
            key,
            dil_deger_haritasi,
            eksik_olanlara_ekle=eksik_olanlara_ekle,
            varsa_uzerine_yaz=varsa_uzerine_yaz,
        )

    def tum_dillere_key_ekle(
        self,
        key: str,
        varsayilan_deger: str = "",
        *,
        referans_dil_kodu: str | None = None,
        referans_degeri_kullan: bool = True,
        varsa_uzerine_yaz: bool = False,
    ) -> list[dict[str, Any]]:
        """
        Aynı key'i algılanan tüm dil dosyalarına ekler.
        """
        return self._yonetici().tum_dillere_key_ekle(
            key,
            varsayilan_deger,
            referans_dil_kodu=referans_dil_kodu,
            referans_degeri_kullan=referans_degeri_kullan,
            varsa_uzerine_yaz=varsa_uzerine_yaz,
        )

    # =========================================================
    # YENI DIL
    # =========================================================
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
        return self._yonetici().yeni_dil_sablonu_uret(
            referans_dil_kodu,
            yeni_dil_kodu,
            yeni_dil_adi,
            bos_deger_kullan=bos_deger_kullan,
        )

    def yeni_dil_olustur(
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
        return self._yonetici().yeni_dil_dosyasi_olustur(
            referans_dil_kodu,
            yeni_dil_kodu,
            yeni_dil_adi,
            bos_deger_kullan=bos_deger_kullan,
            varsa_uzerine_yaz=varsa_uzerine_yaz,
        )

    # =========================================================
    # TOPLU KULLANIM AKISLARI
    # =========================================================
    def referans_dile_gore_durum_ozeti(
        self,
        referans_dil_kodu: str,
    ) -> dict[str, Any]:
        """
        Referans dile göre genel durum özeti döndürür.
        """
        diller = self.dilleri_listele()
        analiz = self.tum_dillerde_eksik_analizi(referans_dil_kodu)

        return {
            "referans_dil_kodu": referans_dil_kodu,
            "toplam_dil_sayisi": len(diller),
            "diller": diller,
            "analiz": analiz,
        }

    def yeni_keyi_tum_dillere_ekle(
        self,
        key: str,
        *,
        referans_dil_kodu: str | None = None,
        referans_deger: str = "",
        diger_diller_degeri: str = "",
        varsa_uzerine_yaz: bool = False,
    ) -> list[dict[str, Any]]:
        """
        Yeni key'i tüm dillere ekler.
        Referans dil verilirse ona referans_deger, diğer dillere
        diger_diller_degeri yazılır.
        """
        dil_kodlari = self.dil_kodlarini_listele()
        harita: dict[str, str] = {}

        for kod in dil_kodlari:
            if referans_dil_kodu and kod == referans_dil_kodu:
                harita[kod] = referans_deger
            else:
                harita[kod] = diger_diller_degeri

        return self.coklu_dillere_key_ekle(
            key,
            harita,
            eksik_olanlara_ekle=not varsa_uzerine_yaz,
            varsa_uzerine_yaz=varsa_uzerine_yaz,
        )


__all__ = (
    "DilGelistiriciServisi",
)