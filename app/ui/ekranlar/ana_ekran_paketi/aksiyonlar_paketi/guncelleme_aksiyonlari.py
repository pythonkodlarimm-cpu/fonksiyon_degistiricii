# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/ekranlar/ana_ekran_paketi/aksiyonlar_paketi/guncelleme_aksiyonlari.py

ROL:
- Ana ekran güncelleme ve geri yükleme aksiyonlarını içerir
- Yeni kod metnini alır ve ön kontrolleri yapar
- Kod doğrulama akışını service facade üzerinden çalıştırır
- Seçili fonksiyonu günceller ve son işlemi geri alır

MİMARİ:
- UI yalnızca servis facade katmanını bilir
- Güncelleme akışları burada toplanır
- Yerleşim kodu içermez
- Fail-soft davranır
- Geriye uyumluluk katmanı içermez
- Nested fonksiyonlu tam fonksiyon güncellemelerini destekler
- Doğrulama mantığı core/service katmanına taşınmıştır
- UI yalnızca sonucu yorumlar ve feedback üretir

SURUM: 3
TARIH: 2026-03-28
IMZA: FY.
"""

from __future__ import annotations

from kivy.logger import Logger


class AnaEkranGuncellemeAksiyonMixin:
    """
    Güncelleme ve geri yükleme aksiyonları.
    """

    def _ui_yenile(self) -> None:
        """
        Ekranı yeniden kurar ve mümkünse mevcut seçimi korur.
        """
        Logger.info("AnaEkranGuncellemeAksiyon: _ui_yenile girdi.")

        mevcut_kaynak = self._secili_kaynak
        mevcut_item = self._secili_item
        mevcut_islem = str(getattr(self, "_aktif_islem_kodu", "") or "")
        yeni_kod = str(self._yeni_kod_input.text or "") if self._yeni_kod_input else ""

        self._kur()

        self._aktif_islem_kodu = mevcut_islem or "fonksiyon_degistir"
        self._aktif_islem_basligini_yenile()

        if mevcut_kaynak:
            self._secili_kaynagi_uygula(mevcut_kaynak)

        if self._yeni_kod_input is not None and yeni_kod:
            self._yeni_kod_input.text = yeni_kod

        self._secili_item = mevcut_item

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
            elif self._bilgi is not None:
                self._bilgi.mesaj(self._t("file_not_selected"), hata=True)
            return None

        if self._secili_item is None:
            if hasattr(self, "_hata"):
                self._hata("select_function_first")
            elif self._bilgi is not None:
                self._bilgi.mesaj(self._t("select_function_first"), hata=True)
            return None

        yeni_kod = self._yeni_kod_metni_al()
        if not yeni_kod:
            if hasattr(self, "_hata"):
                self._hata("new_function_code_cannot_be_empty")
            elif self._bilgi is not None:
                self._bilgi.mesaj(
                    self._t("new_function_code_cannot_be_empty"),
                    hata=True,
                )
            return None

        return yeni_kod

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
            if hasattr(self, "_hata"):
                self._hata("validation_error")
            elif self._bilgi is not None:
                self._bilgi.mesaj(
                    f"{self._t('validation_error')}: {exc}",
                    hata=True,
                )
            return False

        if sonuc.get("valid", False):
            return True

        hata_kodu = str(sonuc.get("error_code", "") or "").strip()
        hata_mesaji = str(sonuc.get("message", "") or "").strip()

        Logger.warning(
            "AnaEkranGuncellemeAksiyon: dogrulama basarisiz "
            f"error_code={hata_kodu!r} message={hata_mesaji!r}"
        )

        if self._bilgi is not None:
            if hata_kodu == "validation_error_syntax_prefix" and hata_mesaji:
                self._bilgi.mesaj(hata_mesaji, hata=True)
                return False

            if hata_kodu == "validation_error_single_function_required":
                self._bilgi.mesaj(
                    self._t("validation_error_single_function_required"),
                    hata=True,
                )
                return False

            if hata_kodu == "validation_error_only_def_allowed":
                anahtar = self._t("validation_error_only_def_allowed")
                self._bilgi.mesaj(
                    anahtar if anahtar != "validation_error_only_def_allowed" else hata_mesaji,
                    hata=True,
                )
                return False

            if hata_kodu == "selection_error_title" and hata_mesaji:
                self._bilgi.mesaj(hata_mesaji, hata=True)
                return False

            if hata_kodu == "validation_error_code_empty":
                self._bilgi.mesaj(
                    self._t("validation_error_code_empty"),
                    hata=True,
                )
                return False

            self._bilgi.mesaj(
                hata_mesaji or self._t("validation_error"),
                hata=True,
            )

        return False

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

            def _sonrasi() -> None:
                try:
                    if hasattr(self, "_basari"):
                        self._basari("update_completed_full")
                    elif self._bilgi is not None:
                        mesaj = self._t("update_completed_full")
                        if mesaj == "update_completed_full":
                            mesaj = "Değişiklikler kaydedildi. Şu an güncel dosya ile çalışıyorsunuz."
                        self._bilgi.mesaj(mesaj)

                    self._tara()
                except Exception as inner_exc:
                    Logger.exception(
                        f"AnaEkranGuncellemeAksiyon: guncelle sonrasi akisi hata: {inner_exc}"
                    )

            try:
                reklam_yoneticisi = self._services.reklam()
                gosterildi = reklam_yoneticisi.gecis_reklami_goster(
                    sonrasi_callback=_sonrasi
                )
                if not gosterildi:
                    _sonrasi()
            except Exception:
                _sonrasi()

        except Exception as exc:
            Logger.exception(f"AnaEkranGuncellemeAksiyon: _guncelle hata: {exc}")

            mesaj = (
                f"{self._t('update_error')}: {exc} "
                f"[kaynak_tipi={self._secili_kaynak_tipi}]"
            )

            if self._bilgi is not None:
                self._bilgi.mesaj(mesaj, hata=True)

    def _geri_yukle(self, *_args) -> None:
        """
        Son güncelleme işlemini geri yükler.
        """
        Logger.info("AnaEkranGuncellemeAksiyon: _geri_yukle girdi.")

        if not self._secili_kaynak:
            if hasattr(self, "_hata"):
                self._hata("file_not_selected")
            elif self._bilgi is not None:
                self._bilgi.mesaj(self._t("file_not_selected"), hata=True)
            return

        try:
            ok = self._services.fonksiyon_islemleri().son_islemi_geri_al(
                hedef_dosya=self._secili_kaynak
            )

            if not ok:
                if hasattr(self, "_hata"):
                    self._hata("restore_not_connected")
                elif self._bilgi is not None:
                    self._bilgi.mesaj(self._t("restore_not_connected"), hata=True)
                return

            def _sonrasi() -> None:
                try:
                    if hasattr(self, "_basari"):
                        self._basari("restore_completed")
                    elif self._bilgi is not None:
                        self._bilgi.mesaj(self._t("restore_completed"))

                    self._tara()
                except Exception as inner_exc:
                    Logger.exception(
                        f"AnaEkranGuncellemeAksiyon: geri yukle sonrasi akisi hata: {inner_exc}"
                    )

            try:
                reklam_yoneticisi = self._services.reklam()
                gosterildi = reklam_yoneticisi.gecis_reklami_goster(
                    sonrasi_callback=_sonrasi
                )
                if not gosterildi:
                    _sonrasi()
            except Exception:
                _sonrasi()

        except Exception as exc:
            Logger.exception(f"AnaEkranGuncellemeAksiyon: _geri_yukle hata: {exc}")

            if self._bilgi is not None:
                self._bilgi.mesaj(
                    f"{self._t('restore_error')}: {exc}",
                    hata=True,
                )
