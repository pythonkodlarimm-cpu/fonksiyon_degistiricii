# -*- coding: utf-8 -*-
"""
DOSYA: app/services/yoneticisi.py

ROL:
- Services katmanı için merkezi yönetici sağlar
- Tüm servisleri tek noktadan üretir ve cache eder
- Core katmanına servis bağımlılıklarını izole eder
- Ayarlar (developer mode dahil) yönetimini merkezileştirir
- Dil, dosya, işlem, reklam ve dil geliştirici servislerini tek facade altında toplar

MİMARİ:
- Lazy load + kesin instance cache
- Her servis yalnızca 1 kez oluşturulur
- Ortak bağımlılıklar (core / dosya / yedek) paylaşılır
- Deterministik davranış
- Type güvenliği yüksektir
- Micro-perf optimize
- Geriye uyumluluk katmanı içermez
- Alt servisler tekrar tekrar oluşturulmaz
- Sıfır fallback / sürpriz davranış

SERVISLER:
- android
- dil_servisi
- dil_gelistirici
- ayarlar
- sil_yada_geri_yukle
- fonksiyon_islemleri
- parca_islemleri
- enjeksiyon_islemleri
- dosya_erisim
- son_klasor
- reklam

API UYUMLULUK:
- Platform bağımsızdır
- Android API 35 ile uyumludur
- Pydroid3 / masaüstü / test ortamlarında aynı mantıkla davranır

NOT:
- ayarlar() servisi ile developer mode kontrol edilir
- UI katmanı bu servisi kullanarak conditional render yapmalıdır

SURUM: 13
TARIH: 2026-03-28
IMZA: FY.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from app.core.yoneticisi import CoreYoneticisi

if TYPE_CHECKING:
    from app.services.android.yoneticisi import AndroidYoneticisi
    from app.services.ayarlar_servisi import AyarlarServisi
    from app.services.dil_gelistirici_servisi import DilGelistiriciServisi
    from app.services.dil_servisi import DilServisi
    from app.services.dosya_erisim_servisi import DosyaErisimServisi
    from app.services.enjeksiyon_islemleri import EnjeksiyonIslemleriServisi
    from app.services.fonksiyon_islemleri import FonksiyonIslemleriServisi
    from app.services.parca_islemleri import ParcaIslemleriServisi
    from app.services.reklam.yoneticisi import ReklamYoneticisi
    from app.services.sil_yada_geri_yukle import SilYadaGeriYukleServisi
    from app.services.son_klasor_servisi import SonKlasorServisi


class ServisYoneticisi:
    """
    Services facade yöneticisi.
    """

    __slots__ = (
        "_core",
        "_android_yoneticisi",
        "_dil_servisi",
        "_dil_gelistirici_servisi",
        "_ayarlar_servisi",
        "_sil_yada_geri_yukle_servisi",
        "_fonksiyon_islemleri_servisi",
        "_parca_islemleri_servisi",
        "_enjeksiyon_islemleri_servisi",
        "_dosya_erisim_servisi",
        "_son_klasor_servisi",
        "_reklam_yoneticisi",
    )

    def __init__(self) -> None:
        self._core: CoreYoneticisi = CoreYoneticisi()

        self._android_yoneticisi: AndroidYoneticisi | None = None
        self._dil_servisi: DilServisi | None = None
        self._dil_gelistirici_servisi: DilGelistiriciServisi | None = None
        self._ayarlar_servisi: AyarlarServisi | None = None
        self._sil_yada_geri_yukle_servisi: SilYadaGeriYukleServisi | None = None
        self._fonksiyon_islemleri_servisi: FonksiyonIslemleriServisi | None = None
        self._parca_islemleri_servisi: ParcaIslemleriServisi | None = None
        self._enjeksiyon_islemleri_servisi: EnjeksiyonIslemleriServisi | None = None
        self._dosya_erisim_servisi: DosyaErisimServisi | None = None
        self._son_klasor_servisi: SonKlasorServisi | None = None
        self._reklam_yoneticisi: ReklamYoneticisi | None = None

    # =========================================================
    # INTERNAL ORTAK BAGIMLILIKLAR
    # =========================================================
    def _lang_path(self) -> Path:
        """
        Uygulama dil klasörü yolunu üretir.
        """
        return Path(__file__).resolve().parents[1] / "assets" / "lang"

    # =========================================================
    # INTERNAL (LAZY + STRICT CACHE)
    # =========================================================
    def _android_yoneticisi_olustur(self) -> AndroidYoneticisi:
        obj = self._android_yoneticisi
        if obj is None:
            from app.services.android import AndroidYoneticisi

            obj = AndroidYoneticisi()
            self._android_yoneticisi = obj
        return obj

    def _dil_servisi_olustur(self) -> DilServisi:
        obj = self._dil_servisi
        if obj is None:
            from app.services.dil_servisi import DilServisi

            obj = DilServisi(self._lang_path())
            self._dil_servisi = obj
        return obj

    def _dil_gelistirici_servisi_olustur(self) -> DilGelistiriciServisi:
        obj = self._dil_gelistirici_servisi
        if obj is None:
            from app.services.dil_gelistirici_servisi import DilGelistiriciServisi

            obj = DilGelistiriciServisi(core=self._core)
            self._dil_gelistirici_servisi = obj
        return obj

    def _ayarlar_servisi_olustur(self) -> AyarlarServisi:
        obj = self._ayarlar_servisi
        if obj is None:
            from app.services.ayarlar_servisi import AyarlarServisi

            obj = AyarlarServisi()
            self._ayarlar_servisi = obj
        return obj

    def _dosya_erisim_servisi_olustur(self) -> DosyaErisimServisi:
        obj = self._dosya_erisim_servisi
        if obj is None:
            from app.services.dosya_erisim_servisi import DosyaErisimServisi

            obj = DosyaErisimServisi()
            self._dosya_erisim_servisi = obj
        return obj

    def _sil_yada_geri_yukle_servisi_olustur(self) -> SilYadaGeriYukleServisi:
        obj = self._sil_yada_geri_yukle_servisi
        if obj is None:
            from app.services.sil_yada_geri_yukle import SilYadaGeriYukleServisi

            obj = SilYadaGeriYukleServisi()
            self._sil_yada_geri_yukle_servisi = obj
        return obj

    def _fonksiyon_islemleri_servisi_olustur(self) -> FonksiyonIslemleriServisi:
        obj = self._fonksiyon_islemleri_servisi
        if obj is None:
            from app.services.fonksiyon_islemleri import FonksiyonIslemleriServisi

            obj = FonksiyonIslemleriServisi(
                core=self._core,
                yedek=self._sil_yada_geri_yukle_servisi_olustur(),
                dosya=self._dosya_erisim_servisi_olustur(),
            )
            self._fonksiyon_islemleri_servisi = obj
        return obj

    def _parca_islemleri_servisi_olustur(self) -> ParcaIslemleriServisi:
        obj = self._parca_islemleri_servisi
        if obj is None:
            from app.services.parca_islemleri import ParcaIslemleriServisi

            obj = ParcaIslemleriServisi()
            self._parca_islemleri_servisi = obj
        return obj

    def _enjeksiyon_islemleri_servisi_olustur(self) -> EnjeksiyonIslemleriServisi:
        obj = self._enjeksiyon_islemleri_servisi
        if obj is None:
            from app.services.enjeksiyon_islemleri import EnjeksiyonIslemleriServisi

            obj = EnjeksiyonIslemleriServisi()
            self._enjeksiyon_islemleri_servisi = obj
        return obj

    def _son_klasor_servisi_olustur(self) -> SonKlasorServisi:
        obj = self._son_klasor_servisi
        if obj is None:
            from app.services.son_klasor_servisi import SonKlasorServisi

            obj = SonKlasorServisi()
            self._son_klasor_servisi = obj
        return obj

    def _reklam_yoneticisi_olustur(self) -> ReklamYoneticisi:
        obj = self._reklam_yoneticisi
        if obj is None:
            from app.services.reklam import ReklamYoneticisi

            obj = ReklamYoneticisi()
            self._reklam_yoneticisi = obj
        return obj

    # =========================================================
    # PUBLIC API
    # =========================================================
    @property
    def core(self) -> CoreYoneticisi:
        """
        Ortak core yöneticisini döndürür.
        """
        return self._core

    def android(self) -> AndroidYoneticisi:
        return self._android_yoneticisi_olustur()

    def dil_servisi(self) -> DilServisi:
        return self._dil_servisi_olustur()

    def dil_gelistirici(self) -> DilGelistiriciServisi:
        return self._dil_gelistirici_servisi_olustur()

    def ayarlar(self) -> AyarlarServisi:
        """
        Uygulama ayarları servisi.
        (developer mode kontrolü dahil)
        """
        return self._ayarlar_servisi_olustur()

    def sil_yada_geri_yukle(self) -> SilYadaGeriYukleServisi:
        return self._sil_yada_geri_yukle_servisi_olustur()

    def fonksiyon_islemleri(self) -> FonksiyonIslemleriServisi:
        return self._fonksiyon_islemleri_servisi_olustur()

    def parca_islemleri(self) -> ParcaIslemleriServisi:
        return self._parca_islemleri_servisi_olustur()

    def enjeksiyon_islemleri(self) -> EnjeksiyonIslemleriServisi:
        return self._enjeksiyon_islemleri_servisi_olustur()

    def dosya_erisim(self) -> DosyaErisimServisi:
        return self._dosya_erisim_servisi_olustur()

    def son_klasor(self) -> SonKlasorServisi:
        return self._son_klasor_servisi_olustur()

    def reklam(self) -> ReklamYoneticisi:
        return self._reklam_yoneticisi_olustur()