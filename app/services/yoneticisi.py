# -*- coding: utf-8 -*-
"""
DOSYA: app/services/yoneticisi.py

ROL:
- Services katmanı için tek giriş noktası sağlamak
- Alt servis yöneticilerini merkezileştirmek
- Üst katmanın alt modül detaylarını bilmesini engellemek
- Lazy import ve cache sistemi ile servis erişim maliyetini azaltmak

MİMARİ:
- Lazy import kullanır
- UI ve root katmanı doğrudan alt servis dosyalarına değil, bu yöneticiye bağlanır
- Refactor sırasında import kırılmalarını azaltır
- Android, belge, dosya, analiz, reklam, güncelleme, sistem ve yedek servislerini tek noktada toplar
- Banner ve geçiş reklamı gibi reklam akışları üst katmana tek kapıdan açılır
- Play Store yönlendirmeli güncelleme akışı üst katmana tek kapıdan açılır
- Dil ve lokalizasyon akışı üst katmana tek kapıdan açılır
- diller/ klasörüne eklenen json dosyalarının otomatik algılanması sistem katmanı üzerinden dışarı açılır
- Aynı ServicesYoneticisi instance'ı içinde alt yöneticiler cache'lenir
- Özellikle sistem/dil akışında state kaybını önlemek için yönetici instance'ları tekrar kullanılabilir tutulur
- Modül ve yönetici referansları tek instance içinde tekrar kullanılır

API UYUMLULUK:
- Platform bağımsız çekirdek servislerle uyumludur
- Android servisleri izole biçimde yönetir
- Android API 35 hedefiyle uyumlu mimari için uygundur

SURUM: 12
TARIH: 2026-03-24
IMZA: FY.
"""

from __future__ import annotations

import traceback


class ServicesYoneticisi:
    """
    Tüm servis yöneticileri için merkezi erişim katmanı.
    """

    def __init__(self) -> None:
        self._analiz_yonetici_cache = None
        self._android_yonetici_cache = None
        self._belge_yonetici_cache = None
        self._dosya_yonetici_cache = None
        self._reklam_yonetici_cache = None
        self._guncelleme_yonetici_cache = None
        self._sistem_yonetici_cache = None
        self._yedek_yonetici_cache = None

        self._modul_cache: dict[str, object] = {}

    # =========================================================
    # CACHE / INTERNAL
    # =========================================================
    def cache_temizle(self) -> None:
        """
        Tüm modül ve yönetici cache alanlarını temizler.
        """
        try:
            self._analiz_yonetici_cache = None
            self._android_yonetici_cache = None
            self._belge_yonetici_cache = None
            self._dosya_yonetici_cache = None
            self._reklam_yonetici_cache = None
            self._guncelleme_yonetici_cache = None
            self._sistem_yonetici_cache = None
            self._yedek_yonetici_cache = None
            self._modul_cache = {}
        except Exception:
            pass

    def _modul_yukle(self, modul_yolu: str):
        """
        Hedef modülü lazy import + cache ile yükler.

        Args:
            modul_yolu: Yüklenecek modül yolu.

        Returns:
            module | None
        """
        try:
            cached = self._modul_cache.get(modul_yolu)
            if cached is not None:
                return cached
        except Exception:
            pass

        try:
            modul = __import__(modul_yolu, fromlist=["*"])
            self._modul_cache[modul_yolu] = modul
            return modul
        except Exception:
            print(f"[SERVICES] Modül yüklenemedi: {modul_yolu}")
            print(traceback.format_exc())
            return None

    def _yonetici_sinifini_getir(self, modul_yolu: str, sinif_adi: str):
        """
        Modül içinden hedef yönetici sınıfını alır.

        Args:
            modul_yolu: Modül yolu.
            sinif_adi: Sınıf adı.

        Returns:
            type | None
        """
        modul = self._modul_yukle(modul_yolu)
        if modul is None:
            return None

        try:
            cls = getattr(modul, sinif_adi, None)
            if cls is None:
                print(f"[SERVICES] Sınıf bulunamadı: {modul_yolu}.{sinif_adi}")
            return cls
        except Exception:
            print(f"[SERVICES] Sınıf alınamadı: {modul_yolu}.{sinif_adi}")
            print(traceback.format_exc())
            return None

    # =========================================================
    # ALT YONETICILER
    # =========================================================
    def _analiz_yoneticisi(self):
        if self._analiz_yonetici_cache is None:
            cls = self._yonetici_sinifini_getir(
                "app.services.analiz",
                "AnalizYoneticisi",
            )
            if cls is None:
                raise RuntimeError("AnalizYoneticisi bulunamadı.")
            self._analiz_yonetici_cache = cls()
        return self._analiz_yonetici_cache

    def _android_yoneticisi(self):
        if self._android_yonetici_cache is None:
            cls = self._yonetici_sinifini_getir(
                "app.services.android",
                "AndroidYoneticisi",
            )
            if cls is None:
                raise RuntimeError("AndroidYoneticisi bulunamadı.")
            self._android_yonetici_cache = cls()
        return self._android_yonetici_cache

    def _belge_yoneticisi(self):
        if self._belge_yonetici_cache is None:
            cls = self._yonetici_sinifini_getir(
                "app.services.belge",
                "BelgeYoneticisi",
            )
            if cls is None:
                raise RuntimeError("BelgeYoneticisi bulunamadı.")
            self._belge_yonetici_cache = cls()
        return self._belge_yonetici_cache

    def _dosya_yoneticisi(self):
        if self._dosya_yonetici_cache is None:
            cls = self._yonetici_sinifini_getir(
                "app.services.dosya",
                "DosyaYoneticisi",
            )
            if cls is None:
                raise RuntimeError("DosyaYoneticisi bulunamadı.")
            self._dosya_yonetici_cache = cls()
        return self._dosya_yonetici_cache

    def _reklam_yoneticisi(self):
        if self._reklam_yonetici_cache is None:
            cls = self._yonetici_sinifini_getir(
                "app.services.reklam",
                "ReklamYoneticisi",
            )
            if cls is None:
                raise RuntimeError("ReklamYoneticisi bulunamadı.")
            self._reklam_yonetici_cache = cls()
        return self._reklam_yonetici_cache

    def _guncelleme_yoneticisi(self):
        if self._guncelleme_yonetici_cache is None:
            cls = self._yonetici_sinifini_getir(
                "app.services.guncelleme",
                "GuncellemeYoneticisi",
            )
            if cls is None:
                raise RuntimeError("GuncellemeYoneticisi bulunamadı.")
            self._guncelleme_yonetici_cache = cls()
        return self._guncelleme_yonetici_cache

    def _sistem_yoneticisi(self):
        if self._sistem_yonetici_cache is None:
            cls = self._yonetici_sinifini_getir(
                "app.services.sistem",
                "SistemYoneticisi",
            )
            if cls is None:
                raise RuntimeError("SistemYoneticisi bulunamadı.")
            self._sistem_yonetici_cache = cls()
        return self._sistem_yonetici_cache

    def _yedek_yoneticisi(self):
        if self._yedek_yonetici_cache is None:
            cls = self._yonetici_sinifini_getir(
                "app.services.yedek",
                "YedekYoneticisi",
            )
            if cls is None:
                raise RuntimeError("YedekYoneticisi bulunamadı.")
            self._yedek_yonetici_cache = cls()
        return self._yedek_yonetici_cache

    # =========================================================
    # ANALIZ
    # =========================================================
    def analiz_yoneticisi(self):
        return self._analiz_yoneticisi()

    def replace_karar_servisi_olustur(self, *args, **kwargs):
        return self._analiz_yoneticisi().replace_karar_servisi_olustur(
            *args,
            **kwargs,
        )

    # =========================================================
    # ANDROID
    # =========================================================
    def android_yoneticisi(self):
        return self._android_yoneticisi()

    def android_belge_servisi(self):
        return self._android_yoneticisi().android_belge_servisi()

    def android_ozel_izin_servisi(self):
        return self._android_yoneticisi().android_ozel_izin_servisi()

    def android_reklam_kopru_servisi(self):
        return self._android_yoneticisi().android_reklam_kopru_servisi()

    def android_uri_servisi(self):
        return self._android_yoneticisi().android_uri_servisi()

    # =========================================================
    # BELGE
    # =========================================================
    def belge_yoneticisi(self):
        return self._belge_yoneticisi()

    def belge_ice_aktarma_servisi(self):
        return self._belge_yoneticisi().belge_ice_aktarma_servisi()

    def belge_kaydetme_servisi(self):
        return self._belge_yoneticisi().belge_kaydetme_servisi()

    def belge_oturumu_servisi(self):
        return self._belge_yoneticisi().belge_oturumu_servisi()

    # =========================================================
    # DOSYA
    # =========================================================
    def dosya_yoneticisi(self):
        return self._dosya_yoneticisi()

    def dosya_okuma_servisi(self):
        return self._dosya_yoneticisi().dosya_okuma_servisi()

    def dosya_yazma_servisi(self):
        return self._dosya_yoneticisi().dosya_yazma_servisi()

    def gecici_dosya_servisi(self):
        return self._dosya_yoneticisi().gecici_dosya_servisi()

    # =========================================================
    # REKLAM
    # =========================================================
    def reklam_yoneticisi(self):
        return self._reklam_yoneticisi()

    def banner_goster(self) -> bool:
        return self._reklam_yoneticisi().banner_goster()

    def banner_goster_gecikmeli(self, delay: float = 1.5) -> bool:
        return self._reklam_yoneticisi().banner_goster_gecikmeli(delay=delay)

    def banner_gizle(self) -> bool:
        return self._reklam_yoneticisi().banner_gizle()

    def banner_baslatildi_mi(self) -> bool:
        return self._reklam_yoneticisi().banner_baslatildi_mi()

    def banner_gosteriliyor_mu(self) -> bool:
        return self._reklam_yoneticisi().banner_gosteriliyor_mu()

    def banner_planlandi_mi(self) -> bool:
        return self._reklam_yoneticisi().banner_planlandi_mi()

    def gecis_reklami_yukle(self) -> bool:
        return self._reklam_yoneticisi().gecis_reklami_yukle()

    def gecis_reklami_hazir_mi(self) -> bool:
        return self._reklam_yoneticisi().gecis_reklami_hazir_mi()

    def gecis_reklami_yukleniyor_mu(self) -> bool:
        return self._reklam_yoneticisi().gecis_reklami_yukleniyor_mu()

    def gecis_reklami_goster(self, sonrasi_callback=None) -> bool:
        return self._reklam_yoneticisi().gecis_reklami_goster(
            sonrasi_callback=sonrasi_callback,
        )

    def gecis_reklami_temizle(self) -> None:
        self._reklam_yoneticisi().gecis_reklami_temizle()

    def test_modu_aktif_mi(self) -> bool:
        return self._reklam_yoneticisi().test_modu_aktif_mi()

    def yayin_modu_aktif_mi(self) -> bool:
        return self._reklam_yoneticisi().yayin_modu_aktif_mi()

    def reklam_modu_etiketi(self) -> str:
        return self._reklam_yoneticisi().reklam_modu_etiketi()

    def aktif_admob_app_id(self) -> str:
        return self._reklam_yoneticisi().aktif_admob_app_id()

    def aktif_banner_reklam_id(self) -> str:
        return self._reklam_yoneticisi().aktif_banner_reklam_id()

    def aktif_interstitial_reklam_id(self) -> str:
        return self._reklam_yoneticisi().aktif_interstitial_reklam_id()

    def aktif_rewarded_reklam_id(self) -> str:
        return self._reklam_yoneticisi().aktif_rewarded_reklam_id()

    def odullu_reklam_goster(self) -> bool:
        return self._reklam_yoneticisi().odullu_reklam_goster()

    # =========================================================
    # GUNCELLEME
    # =========================================================
    def guncelleme_yoneticisi(self):
        return self._guncelleme_yoneticisi()

    def guncelleme_kontrol_aktif_mi(self) -> bool:
        return self._guncelleme_yoneticisi().guncelleme_kontrol_aktif_mi()

    def guncelleme_bildirim_metni(self) -> str:
        return self._guncelleme_yoneticisi().guncelleme_bildirim_metni()

    def guncelleme_buton_metni(self) -> str:
        return self._guncelleme_yoneticisi().guncelleme_buton_metni()

    def play_store_package_name(self) -> str:
        return self._guncelleme_yoneticisi().play_store_package_name()

    def play_store_sayfasini_ac(self, package_name: str = "") -> bool:
        return self._guncelleme_yoneticisi().play_store_sayfasini_ac(
            package_name=package_name
        )

    def guncelleme_bildirimi_gosterilmeli_mi(self) -> bool:
        return self._guncelleme_yoneticisi().guncelleme_bildirimi_gosterilmeli_mi()

    def guncelleme_durumu_hesapla(self, mevcut_surum: str) -> dict:
        return self._guncelleme_yoneticisi().guncelleme_durumu_hesapla(
            mevcut_surum=mevcut_surum
        )

    # =========================================================
    # SISTEM
    # =========================================================
    def sistem_yoneticisi(self):
        return self._sistem_yoneticisi()

    def ayarlari_yukle(self) -> dict:
        return self._sistem_yoneticisi().ayarlari_yukle()

    def ayarlari_kaydet(self, data: dict) -> None:
        self._sistem_yoneticisi().ayarlari_kaydet(data)

    def get_language(self, default: str = "tr") -> str:
        return self._sistem_yoneticisi().get_language(default=default)

    def set_language(self, code: str) -> None:
        self._sistem_yoneticisi().set_language(code)

    def supported_languages(self) -> list[str]:
        return self._sistem_yoneticisi().supported_languages()

    def language_supported(self, code: str) -> bool:
        return self._sistem_yoneticisi().language_supported(code)

    def aktif_dil(self) -> str:
        return self._sistem_yoneticisi().aktif_dil()

    def dil_degistir(self, code: str) -> bool:
        return self._sistem_yoneticisi().dil_degistir(code)

    def set_active_language(self, code: str) -> bool:
        return self._sistem_yoneticisi().set_active_language(code)

    def aktif_dili_ayardan_yukle(self, default: str = "tr") -> str:
        return self._sistem_yoneticisi().aktif_dili_ayardan_yukle(default=default)

    def dil_destekleniyor_mu(self, code: str) -> bool:
        return self._sistem_yoneticisi().dil_destekleniyor_mu(code)

    def dil_var_mi(self, code: str) -> bool:
        return self._sistem_yoneticisi().dil_var_mi(code)

    def mevcut_dilleri_listele(self) -> list[dict[str, str]]:
        return self._sistem_yoneticisi().mevcut_dilleri_listele()

    def mevcut_dil_kodlari(self) -> list[str]:
        return self._sistem_yoneticisi().mevcut_dil_kodlari()

    def dilleri_yeniden_tara(self) -> list[dict[str, str]]:
        return self._sistem_yoneticisi().dilleri_yeniden_tara()

    def desteklenen_diller(
        self,
        sadece_aktifler: bool = False,
    ) -> dict[str, dict[str, object]]:
        return self._sistem_yoneticisi().desteklenen_diller(
            sadece_aktifler=sadece_aktifler
        )

    def dil_adi(self, code: str, default: str = "") -> str:
        return self._sistem_yoneticisi().dil_adi(code=code, default=default)

    def metin(self, anahtar: str, default: str = "") -> str:
        return self._sistem_yoneticisi().metin(
            anahtar=anahtar,
            default=default,
        )

    def get_app_state(self, default: dict | None = None) -> dict:
        return self._sistem_yoneticisi().get_app_state(default=default)

    def set_app_state(self, state: dict) -> None:
        self._sistem_yoneticisi().set_app_state(state)

    def clear_app_state(self) -> None:
        self._sistem_yoneticisi().clear_app_state()

    def register_bildirim_layer(self, layer) -> bool:
        return self._sistem_yoneticisi().register_bildirim_layer(layer)

    def unregister_bildirim_layer(self) -> None:
        self._sistem_yoneticisi().unregister_bildirim_layer()

    def bildirim_layer_var_mi(self) -> bool:
        return self._sistem_yoneticisi().bildirim_layer_var_mi()

    def bildirim_goster(
        self,
        text: str,
        icon_name: str = "",
        duration: float = 2.4,
        title: str = "",
        tone: str = "info",
        on_tap=None,
    ) -> bool:
        return self._sistem_yoneticisi().bildirim_goster(
            text=text,
            icon_name=icon_name,
            duration=duration,
            title=title,
            tone=tone,
            on_tap=on_tap,
        )

    def bildirim_gizle(self) -> bool:
        return self._sistem_yoneticisi().bildirim_gizle()

    def bildirimi_aninda_gizle(self) -> bool:
        return self._sistem_yoneticisi().bildirimi_aninda_gizle()

    def premium_aktif_mi(self) -> bool:
        return self._sistem_yoneticisi().premium_aktif_mi()

    # =========================================================
    # YEDEK
    # =========================================================
    def yedek_yoneticisi(self):
        return self._yedek_yoneticisi()

    def yedek_listeleme_servisi(self):
        return self._yedek_yoneticisi().yedek_listeleme_servisi()

    def yedek_silme_servisi(self):
        return self._yedek_yoneticisi().yedek_silme_servisi()

    def yedek_indirme_servisi(self):
        return self._yedek_yoneticisi().yedek_indirme_servisi()
