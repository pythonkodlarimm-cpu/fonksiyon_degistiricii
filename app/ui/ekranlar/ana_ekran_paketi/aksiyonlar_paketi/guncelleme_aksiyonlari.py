# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/ekranlar/ana_ekran_paketi/aksiyonlar_paketi/guncelleme_aksiyonlari.py

ROL:
- Ana ekran güncelleme ve geri yükleme aksiyonlarını içerir
- Yeni kod metnini alır ve ön kontrolleri yapar
- Kod doğrulama akışını service facade üzerinden çalıştırır
- Seçili fonksiyonu günceller ve son işlemi geri alır
- Güncelleme / geri yükleme sonrası yeniden tarama akışını güvenli yürütür
- Geçiş reklamı callback akışı ile çakışmadan çalışır
- Hata metinlerini BilgiKutusu üzerinde daha görünür biçimde sunar
- UI güncellemelerini ana Kivy thread üzerinde çalıştırır
- Başarı mesajını ortak feedback pipeline ile güvenli zamanda gösterir

MİMARİ:
- UI yalnızca servis facade katmanını bilir
- Güncelleme akışları burada toplanır
- Yerleşim kodu içermez
- Ortak feedback (_basari / _hata) kullanır
- Fail-soft davranır
- Geriye uyumluluk katmanı içermez
- Nested fonksiyonlu tam fonksiyon güncellemelerini destekler
- Doğrulama mantığı core/service katmanına taşınmıştır
- UI yalnızca sonucu yorumlar ve feedback üretir
- Sonrası callback akışı tek noktadan yürütülür
- Çift tarama / çift callback kaynaklı state bozulmaları engellenir
- Type güvenliği nettir
- Sıfır belirsizlik hedeflenir

SURUM: 8
TARIH: 2026-03-29
IMZA: FY.
"""

from __future__ import annotations

from kivy.clock import Clock
from kivy.logger import Logger


class AnaEkranGuncellemeAksiyonMixin:
    """
    Güncelleme ve geri yükleme aksiyonları.
    """

    # =========================================================
    # INTERNAL HELPERS
    # =========================================================
    def _mesaj_ver(
        self,
        anahtar: str,
        *,
        fallback: str = "",
        hata: bool = False,
    ) -> None:
        """
        Bilgi kutusuna güvenli mesaj basar.
        """
        if self._bilgi is None:
            return

        mesaj = self._t(anahtar)
        if mesaj == anahtar:
            mesaj = fallback or anahtar

        self._bilgi.mesaj(str(mesaj or ""), hata=hata)

    def _scan_error_label(self) -> str:
        """
        Tarama hatası etiketi üretir.
        """
        etiket = self._t("scan_error")
        if etiket == "scan_error":
            etiket = "Tarama Hatası"
        return str(etiket or "Tarama Hatası")

    def _validation_error_label(self) -> str:
        """
        Doğrulama hatası etiketi üretir.
        """
        etiket = self._t("validation_error")
        if etiket == "validation_error":
            etiket = "Doğrulama Hatası"
        return str(etiket or "Doğrulama Hatası")

    def _guncelleme_basarili_metin(self) -> str:
        """
        Güncelleme tamamlandı mesajını üretir.
        """
        mesaj = self._t("update_completed_full")
        if mesaj == "update_completed_full":
            mesaj = "Fonksiyon güncellendi. Güncellenmiş dosya ile devam ediyorsunuz."
        return str(
            mesaj or "Fonksiyon güncellendi. Güncellenmiş dosya ile devam ediyorsunuz."
        )

    def _geri_yukleme_basarili_metin(self) -> str:
        """
        Geri yükleme tamamlandı mesajını üretir.
        """
        mesaj = self._t("restore_completed")
        if mesaj == "restore_completed":
            mesaj = "Geri yükleme tamamlandı."
        return str(mesaj or "Geri yükleme tamamlandı.")

    def _reklam_sonrasi_cagir(self, callback) -> None:
        """
        Geçiş reklamı sonrası callback akışını güvenli biçimde başlatır.

        Not:
        - Reklam servisi callback'i kendisi de çalıştırabildiği için
          burada ikinci kez manuel callback tetiklenmez.
        - Yalnızca reklam çağrısı exception verirse fallback callback çalışır.
        """
        try:
            reklam_yoneticisi = self._services.reklam()
            reklam_yoneticisi.gecis_reklami_goster(
                sonrasi_callback=callback,
            )
        except Exception as exc:
            Logger.exception(
                "AnaEkranGuncellemeAksiyon: gecis reklami gosterim hatasi: "
                f"{exc}"
            )
            callback()

    def _guncelleme_basarisi_goster(self, _dt: float) -> None:
        """
        Güncelleme başarı mesajını ortak feedback pipeline ile gösterir.
        """
        try:
            if hasattr(self, "_basari"):
                self._basari("update_completed_full")
            else:
                raise RuntimeError("Base basari pipeline bulunamadi.")
        except Exception as exc:
            Logger.exception(
                f"AnaEkranGuncellemeAksiyon: guncelleme basari mesaji gosterilemedi: {exc}"
            )
            if self._bilgi is not None:
                self._bilgi.mesaj(
                    self._guncelleme_basarili_metin(),
                    ikon="onaylandi.png",
                    pulse=True,
                    hata=False,
                )

    def _geri_yukleme_basarisi_goster(self, _dt: float) -> None:
        """
        Geri yükleme başarı mesajını ortak feedback pipeline ile gösterir.
        """
        try:
            if hasattr(self, "_basari"):
                self._basari("restore_completed")
            else:
                raise RuntimeError("Base basari pipeline bulunamadi.")
        except Exception as exc:
            Logger.exception(
                f"AnaEkranGuncellemeAksiyon: geri yukleme basari mesaji gosterilemedi: {exc}"
            )
            if self._bilgi is not None:
                self._bilgi.mesaj(
                    self._geri_yukleme_basarili_metin(),
                    ikon="onaylandi.png",
                    pulse=True,
                    hata=False,
                )

    def _tarama_hatasi_mesaji_goster(self, mesaj: str):
        """
        Tarama hatasını bir sonraki frame'de gösterecek closure üretir.
        """

        def _goster(_dt: float) -> None:
            try:
                if hasattr(self, "_hata"):
                    self._hata("scan_error")
                else:
                    raise RuntimeError("Base hata pipeline bulunamadi.")
            except Exception:
                if self._bilgi is not None:
                    self._bilgi.mesaj(
                        mesaj,
                        ikon="error.png",
                        pulse=True,
                        hata=True,
                    )

        return _goster

    # =========================================================
    # UI REFRESH
    # =========================================================
    def _ui_yenile(self) -> None:
        """
        Ekranı yeniden kurar ve mümkünse mevcut seçimi korur.
        """
        Logger.info("AnaEkranGuncellemeAksiyon: _ui_yenile girdi.")

        mevcut_kaynak = self._secili_kaynak
        mevcut_item = self._secili_item
        mevcut_islem = str(getattr(self, "_aktif_islem_kodu", "") or "")
        yeni_kod = (
            str(self._yeni_kod_input.text or "")
            if self._yeni_kod_input is not None
            else ""
        )

        self._kur()

        self._aktif_islem_kodu = mevcut_islem or "fonksiyon_degistir"
        self._aktif_islem_basligini_yenile()

        if mevcut_kaynak:
            self._secili_kaynagi_uygula(mevcut_kaynak)

        if self._yeni_kod_input is not None and yeni_kod:
            self._yeni_kod_input.text = yeni_kod

        self._secili_item = mevcut_item

    # =========================================================
    # INPUT / PRECHECK
    # =========================================================
    def _yeni_kod_metni_al(self) -> str:
        """
        Yeni kod metnini güvenli biçimde döndürür.
        """
        if self._yeni_kod_input is None:
            return ""
        return str(self._yeni_kod_input.text or "").strip()

    def _guncelleme_on_kontrol(self) -> str | None:
        """
        Güncelleme öncesi temel zorunlu kontrolleri yapar.
        """
        Logger.info("AnaEkranGuncellemeAksiyon: _guncelleme_on_kontrol girdi.")

        if not self._secili_kaynak:
            if hasattr(self, "_hata"):
                self._hata("file_not_selected")
            else:
                self._mesaj_ver(
                    "file_not_selected",
                    fallback="Dosya seçilmedi.",
                    hata=True,
                )
            return None

        if self._secili_item is None:
            if hasattr(self, "_hata"):
                self._hata("select_function_first")
            else:
                self._mesaj_ver(
                    "select_function_first",
                    fallback="Önce fonksiyon seçin.",
                    hata=True,
                )
            return None

        yeni_kod = self._yeni_kod_metni_al()
        if not yeni_kod:
            if hasattr(self, "_hata"):
                self._hata("new_function_code_cannot_be_empty")
            else:
                self._mesaj_ver(
                    "new_function_code_cannot_be_empty",
                    fallback="Yeni fonksiyon kodu boş olamaz.",
                    hata=True,
                )
            return None

        return yeni_kod

    # =========================================================
    # VALIDATION
    # =========================================================
    def _yeni_kodu_dogrula(self, yeni_kod: str) -> bool:
        """
        Yeni kodu service facade üzerinden doğrular.

        Kurallar:
        - Nested fonksiyonlar serbesttir
        - Top-level düzeyde tam 1 fonksiyon beklenir
        - Seçili hedef adı ile gelen fonksiyon adı eşleşmelidir
        """
        Logger.info("AnaEkranGuncellemeAksiyon: _yeni_kodu_dogrula girdi.")

        secili_ad = str(getattr(self._secili_item, "name", "") or "").strip()

        try:
            sonuc = self._services.fonksiyon_islemleri().yeni_fonksiyon_kodunu_dogrula(
                source_code=yeni_kod,
                beklenen_fonksiyon_adi=secili_ad or None,
                allow_async=True,
                allow_other_top_level_nodes=False,
            )
        except Exception as exc:
            Logger.exception(
                f"AnaEkranGuncellemeAksiyon: service dogrulama hatasi: {exc}"
            )
            if self._bilgi is not None:
                self._bilgi.mesaj(
                    f"{self._validation_error_label()}: {exc}",
                    ikon="error.png",
                    pulse=True,
                    hata=True,
                )
            return False

        if bool(sonuc.get("valid", False)):
            return True

        hata_kodu = str(sonuc.get("error_code", "") or "").strip()
        hata_mesaji = str(sonuc.get("message", "") or "").strip()

        Logger.warning(
            "AnaEkranGuncellemeAksiyon: dogrulama basarisiz "
            f"error_code={hata_kodu!r} message={hata_mesaji!r}"
        )

        if self._bilgi is None:
            return False

        if hata_kodu == "validation_error_syntax_prefix" and hata_mesaji:
            self._bilgi.mesaj(
                hata_mesaji,
                ikon="error.png",
                pulse=True,
                hata=True,
            )
            return False

        if hata_kodu == "validation_error_single_function_required":
            self._mesaj_ver(
                "validation_error_single_function_required",
                fallback="Kod tek bir top-level fonksiyon içermelidir.",
                hata=True,
            )
            return False

        if hata_kodu == "validation_error_only_def_allowed":
            anahtar = self._t("validation_error_only_def_allowed")
            self._bilgi.mesaj(
                anahtar
                if anahtar != "validation_error_only_def_allowed"
                else (
                    hata_mesaji
                    or "Yalnızca tek bir fonksiyon tanımı kabul edilir."
                ),
                ikon="error.png",
                pulse=True,
                hata=True,
            )
            return False

        if hata_kodu == "selection_error_title" and hata_mesaji:
            self._bilgi.mesaj(
                hata_mesaji,
                ikon="error.png",
                pulse=True,
                hata=True,
            )
            return False

        if hata_kodu == "validation_error_code_empty":
            self._mesaj_ver(
                "validation_error_code_empty",
                fallback="Kod boş olamaz.",
                hata=True,
            )
            return False

        if hata_mesaji:
            self._bilgi.mesaj(
                hata_mesaji,
                ikon="error.png",
                pulse=True,
                hata=True,
            )
            return False

        self._bilgi.mesaj(
            self._validation_error_label(),
            ikon="error.png",
            pulse=True,
            hata=True,
        )
        return False

    # =========================================================
    # POST ACTION FLOWS
    # =========================================================
    def _guncelle_sonrasi_akisi(self) -> None:
        """
        Güncelleme sonrası yeniden tarama akışını yürütür ve
        başarı mesajını tarama bittikten sonra gösterir.
        """
        def _ui(_dt: float) -> None:
            try:
                self._tara()
                Clock.schedule_once(self._guncelleme_basarisi_goster, 0)
            except Exception as exc:
                Logger.exception(
                    "AnaEkranGuncellemeAksiyon: guncelle sonrasi tarama hatasi: "
                    f"{exc}"
                )
                hata_mesaji = f"{self._scan_error_label()}: {exc}"
                Clock.schedule_once(
                    self._tarama_hatasi_mesaji_goster(hata_mesaji),
                    0,
                )

        Clock.schedule_once(_ui, 0)

    def _geri_yukle_sonrasi_akisi(self) -> None:
        """
        Geri yükleme sonrası yeniden tarama akışını yürütür ve
        başarı mesajını tarama bittikten sonra gösterir.
        """
        def _ui(_dt: float) -> None:
            try:
                self._tara()
                Clock.schedule_once(self._geri_yukleme_basarisi_goster, 0)
            except Exception as exc:
                Logger.exception(
                    "AnaEkranGuncellemeAksiyon: geri yukle sonrasi tarama hatasi: "
                    f"{exc}"
                )
                hata_mesaji = f"{self._scan_error_label()}: {exc}"
                Clock.schedule_once(
                    self._tarama_hatasi_mesaji_goster(hata_mesaji),
                    0,
                )

        Clock.schedule_once(_ui, 0)

    # =========================================================
    # UPDATE
    # =========================================================
    def _guncelle(self, *_args) -> None:
        """
        Seçili fonksiyonu yeni kod ile günceller.
        """
        Logger.info("AnaEkranGuncellemeAksiyon: _guncelle girdi.")

        yeni_kod = self._guncelleme_on_kontrol()
        if yeni_kod is None:
            return

        if not self._yeni_kodu_dogrula(yeni_kod):
            return

        try:
            self._services.fonksiyon_islemleri().dosyada_fonksiyon_degistir(
                file_path=self._secili_kaynak,
                target_item=self._secili_item,
                new_code=yeni_kod,
                backup=True,
            )

            self._reklam_sonrasi_cagir(self._guncelle_sonrasi_akisi)

        except Exception as exc:
            Logger.exception(f"AnaEkranGuncellemeAksiyon: _guncelle hata: {exc}")

            mesaj = (
                f"{self._t('update_error')}: {exc} "
                f"[kaynak_tipi={self._secili_kaynak_tipi}]"
            )

            if self._bilgi is not None:
                self._bilgi.mesaj(
                    mesaj,
                    ikon="error.png",
                    pulse=True,
                    hata=True,
                )

    # =========================================================
    # RESTORE
    # =========================================================
    def _geri_yukle(self, *_args) -> None:
        """
        Son güncelleme işlemini geri yükler.
        """
        Logger.info("AnaEkranGuncellemeAksiyon: _geri_yukle girdi.")

        if not self._secili_kaynak:
            if hasattr(self, "_hata"):
                self._hata("file_not_selected")
            else:
                self._mesaj_ver(
                    "file_not_selected",
                    fallback="Dosya seçilmedi.",
                    hata=True,
                )
            return

        try:
            ok = self._services.fonksiyon_islemleri().son_islemi_geri_al(
                hedef_dosya=self._secili_kaynak
            )

            if not ok:
                if hasattr(self, "_hata"):
                    self._hata("restore_not_connected")
                else:
                    self._mesaj_ver(
                        "restore_not_connected",
                        fallback="Geri yükleme bağlantısı bulunamadı.",
                        hata=True,
                    )
                return

            self._reklam_sonrasi_cagir(self._geri_yukle_sonrasi_akisi)

        except Exception as exc:
            Logger.exception(f"AnaEkranGuncellemeAksiyon: _geri_yukle hata: {exc}")

            if self._bilgi is not None:
                self._bilgi.mesaj(
                    f"{self._t('restore_error')}: {exc}",
                    ikon="error.png",
                    pulse=True,
                    hata=True,
            )
