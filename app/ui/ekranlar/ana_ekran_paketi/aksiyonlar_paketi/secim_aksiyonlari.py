# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/ekranlar/ana_ekran_paketi/aksiyonlar_paketi/secim_aksiyonlari.py

ROL:
- Dosya/kaynak seçme akışlarını içerir
- Seçilen kaynağın UI ve iç durum üzerine uygulanmasını sağlar
- Son klasör kaydını ve seçim sonrası tarama tetiklerini yönetir
- Fonksiyon seçiminden sonra preview alanını günceller
- Seçim sonrası layout görünümünü yeniler
- Liste yükleme ve seçim temizleme akışını yönetir
- BilgiKutusu feedback pipeline ile entegre çalışır

MİMARİ:
- UI yalnızca servis facade katmanını bilir
- Seçim ve liste yükleme sorumluluğu burada toplanır
- Yerleşim kodu içermez
- Ortak feedback katmanını kullanır
- Fail-soft davranır
- Geriye uyumluluk katmanı içermez
- Deterministik UI durumu hedeflenir
- Sıfır belirsizlikli akış amaçlanır
- Layout güncelleme yalnızca state değişimi sonrası tetiklenir

SURUM: 4
TARIH: 2026-03-28
IMZA: FY.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from kivy.logger import Logger

from app.ui.popup.dosya_sec_popup import dosya_sec

if TYPE_CHECKING:
    from app.core.modeller.modeller import FunctionItem


class AnaEkranSecimAksiyonMixin:
    """
    Dosya/kaynak seçim aksiyonları.
    """

    def _secili_kaynagi_uygula(self, kaynak: str) -> None:
        """
        Seçilen kaynak bilgisini UI ve iç durum üzerinde uygular.
        """
        raw = str(kaynak or "").strip()
        Logger.info(f"AnaEkranSecimAksiyon: _secili_kaynagi_uygula raw={raw!r}")

        if not raw:
            self._secili_kaynak = ""
            self._secili_kaynak_tipi = ""
            self._secili_item = None

            if self._dosya_alani is not None:
                self._dosya_alani.dosya_yolu_ayarla("")

            if self._dosya_bilgi_label is not None:
                self._dosya_bilgi_label.text = self._t("file_waiting")

            if self._fonksiyon_listesi is not None:
                self._fonksiyon_listesi.clear_items()

            if self._mevcut_kod_input is not None:
                self._mevcut_kod_input.text = ""

            if self._yeni_kod_input is not None:
                self._yeni_kod_input.text = ""

            if hasattr(self, "_layout_guncelle"):
                self._layout_guncelle()

            if hasattr(self, "_hata"):
                self._hata("file_not_selected")
            elif self._bilgi is not None:
                self._bilgi.mesaj(self._t("file_not_selected"), hata=True)

            return

        self._secili_kaynak = raw

        try:
            kaynak_tipi = self._services.dosya_erisim().kaynak_tipi(raw)
        except Exception as exc:
            Logger.warning(
                "AnaEkranSecimAksiyon: kaynak_tipi alinamadi, path varsayildi: "
                f"{exc}"
            )
            kaynak_tipi = "path"

        self._secili_kaynak_tipi = str(kaynak_tipi or "path")
        Logger.info(
            f"AnaEkranSecimAksiyon: secili kaynak tipi={self._secili_kaynak_tipi!r}"
        )

        if self._dosya_alani is not None:
            self._dosya_alani.dosya_yolu_ayarla(raw)

        if self._dosya_bilgi_label is not None:
            self._dosya_bilgi_label.text = self._t("file_selected_auto_scan")

    def _secim_sonrasi_kaydet(self, secilen_kaynak: str) -> None:
        """
        Seçilen kaynağı son klasör servisine kaydeder.
        """
        Logger.info(
            f"AnaEkranSecimAksiyon: _secim_sonrasi_kaydet kaynak={secilen_kaynak!r}"
        )

        try:
            self._services.son_klasor().son_klasor_kaydet(secilen_kaynak)
        except Exception as exc:
            Logger.warning(f"AnaEkranSecimAksiyon: son_klasor kayit hatasi: {exc}")

    def _son_klasor_bilgisi_yukle(self) -> None:
        """
        Son klasör bilgisinden kullanıcıya bilgilendirici mesaj üretir.
        """
        Logger.info("AnaEkranSecimAksiyon: _son_klasor_bilgisi_yukle girdi.")

        try:
            son_kayit = self._services.son_klasor().picker_baslangic_kaynagi()
        except Exception as exc:
            Logger.warning(
                "AnaEkranSecimAksiyon: picker_baslangic_kaynagi hatasi: "
                f"{exc}"
            )
            son_kayit = None

        if not son_kayit:
            if hasattr(self, "_basari"):
                self._basari("app_ready")
            elif self._bilgi is not None:
                self._bilgi.mesaj(self._t("app_ready"))
            return

        try:
            kaynak_tipi = self._services.dosya_erisim().kaynak_tipi(son_kayit)
        except Exception as exc:
            Logger.warning(
                "AnaEkranSecimAksiyon: son kayit kaynak_tipi hatasi: "
                f"{exc}"
            )
            kaynak_tipi = "path"

        if kaynak_tipi == "android_uri":
            if hasattr(self, "_basari"):
                self._basari("previous_session_restored")
            elif self._bilgi is not None:
                self._bilgi.mesaj(self._t("previous_session_restored"))
        else:
            if hasattr(self, "_basari"):
                self._basari("session_restored")
            elif self._bilgi is not None:
                self._bilgi.mesaj(self._t("session_restored"))

    def _fonksiyon_secildi(self, item: FunctionItem | None) -> None:
        """
        Fonksiyon listesinde seçim yapıldığında preview alanını günceller
        ve layout görünümünü seçim durumuna göre yeniler.
        """
        Logger.info(f"AnaEkranSecimAksiyon: _fonksiyon_secildi item={item!r}")

        self._secili_item = item
        preview = self._item_preview_text(item) if item is not None else ""

        if self._mevcut_kod_input is not None:
            self._mevcut_kod_input.text = preview or ""

        if item is not None:
            if hasattr(self, "_basari"):
                self._basari("function_selected")
            elif self._bilgi is not None:
                self._bilgi.mesaj(self._t("function_selected"))

        if hasattr(self, "_layout_guncelle"):
            self._layout_guncelle()

    def _listeyi_yukle(self, items: list[FunctionItem] | None) -> None:
        """
        Taranan item listesini UI üzerinde gösterir.
        """
        liste = list(items or [])
        Logger.info(f"AnaEkranSecimAksiyon: _listeyi_yukle adet={len(liste)}")

        if self._fonksiyon_listesi is not None:
            self._fonksiyon_listesi.set_items(liste)

        self._secili_item = None

        if self._mevcut_kod_input is not None:
            self._mevcut_kod_input.text = ""

        if self._yeni_kod_input is not None:
            self._yeni_kod_input.text = ""

        if hasattr(self, "_layout_guncelle"):
            self._layout_guncelle()

    def _dosya_sec(self, *_args) -> None:
        """
        Dosya seçim popup'ını açar.
        """
        Logger.info("AnaEkranSecimAksiyon: _dosya_sec girdi.")

        def _secildi(kaynak: str) -> None:
            Logger.info(f"AnaEkranSecimAksiyon: _secildi callback geldi: {kaynak!r}")

            raw = str(kaynak or "").strip()

            if not raw:
                Logger.info("AnaEkranSecimAksiyon: secim bos veya iptal.")
                if hasattr(self, "_hata"):
                    self._hata("file_not_selected")
                elif self._bilgi is not None:
                    self._bilgi.mesaj(self._t("file_not_selected"), hata=True)
                return

            try:
                self._secili_kaynagi_uygula(raw)
                self._secim_sonrasi_kaydet(raw)
                self._tara()

                Logger.info(
                    "AnaEkranSecimAksiyon: secim uygulandi ve tarama baslatildi."
                )

            except Exception as exc:
                Logger.exception(f"AnaEkranSecimAksiyon: _secildi hata: {exc}")
                if self._bilgi is not None:
                    self._bilgi.mesaj(f"{self._t('error_title')}: {exc}", hata=True)

        try:
            Logger.info("AnaEkranSecimAksiyon: dosya_sec popup cagriliyor.")
            dosya_sec(
                services=self._services,
                on_secildi=_secildi,
                title=self._t("file_picker_title"),
            )
            Logger.info("AnaEkranSecimAksiyon: dosya_sec popup cagrisi tamam.")
        except Exception as exc:
            Logger.exception(f"AnaEkranSecimAksiyon: dosya_sec acilamadi: {exc}")
            if hasattr(self, "_hata"):
                self._hata("file_picker_open_failed")
            elif self._bilgi is not None:
                self._bilgi.mesaj(
                    f"{self._t('file_picker_open_failed')} {exc}",
                    hata=True,
                )