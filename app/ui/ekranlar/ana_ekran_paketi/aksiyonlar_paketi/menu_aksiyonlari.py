# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/ekranlar/ana_ekran_paketi/aksiyonlar_paketi/menu_aksiyonlari.py

ROL:
- Ana ekran üst toolbar menü aksiyonlarını içerir
- İşlem popup'ını açar
- Aktif motor başlığını günceller
- Geri, yenile ve ayarlar gibi genel aksiyonları toplar
- BilgiKutusu feedback pipeline ile entegre çalışır
- Dosya seçili değilse motor geçişlerinde ekranı başlangıç durumuna döndürür
- UI etkisi oluşturan aksiyonları ana Kivy thread üzerinde güvenli yürütür

MİMARİ:
- UI yalnızca servis facade katmanını bilir
- Menü ve yönlendirme aksiyonları burada toplanır
- Yerleşim kodu içermez
- Ortak feedback katmanını kullanır
- Fail-soft davranır
- Geriye uyumluluk katmanı içermez
- Deterministik akış sunar
- Sıfır belirsizlik hedeflenir
- State temizleme gerekiyorsa ana ekran yardımcı akışını çağırır
- Popup / callback / tarama tetikleri ortak ui_thread katmanı ile ana thread'e alınır

SURUM: 4
TARIH: 2026-03-29
IMZA: FY.
"""

from __future__ import annotations

from kivy.logger import Logger

from app.config import DEVELOPER_MODE
from app.ui.ortak.ui_thread import ui_thread_uzerinde_calistir
from app.ui.popup.islemler_popup import islemler_popup


class AnaEkranMenuAksiyonMixin:
    """
    Menü ve toolbar aksiyonları.
    """

    def _menu(self, *_args) -> None:
        """
        Üst toolbar menü ikonundan işlemler popup'ını açar.
        """
        Logger.info("AnaEkranMenuAksiyon: _menu girdi.")

        def _ui() -> None:
            try:
                islemler_popup(
                    t=self._t,
                    on_fonksiyon_degistir=self._motor_fonksiyon_degistir,
                    on_parca_degistir=self._motor_parca_degistir,
                    on_enjeksiyon=self._motor_enjeksiyon,
                    on_dil=self._dil_sec,
                    on_yedekler=self._yedekler,
                    on_ayarlar=self._ayarlar,
                    on_gelistirici_ayarlar=(
                        self._ac_gelistirici_ayarlar if DEVELOPER_MODE else None
                    ),
                    title=self._t("menu_operations"),
                )
            except Exception as exc:
                Logger.exception(
                    f"AnaEkranMenuAksiyon: islemler_popup acilamadi: {exc}"
                )
                if hasattr(self, "_hata"):
                    self._hata("menu_open_failed")
                elif self._bilgi is not None:
                    self._bilgi.mesaj(
                        f"{self._t('error_title')}: {exc}",
                        hata=True,
                    )

        ui_thread_uzerinde_calistir(_ui)

    def _motor_fonksiyon_degistir(self) -> None:
        """
        Fonksiyon değiştirme işlemini aktif başlık olarak ayarlar.
        """
        Logger.info("AnaEkranMenuAksiyon: _motor_fonksiyon_degistir girdi.")

        def _ui() -> None:
            self._aktif_islem_kodu = "fonksiyon_degistir"
            self._aktif_islem_basligini_yenile()

            if not str(self._secili_kaynak or "").strip():
                Logger.info(
                    "AnaEkranMenuAksiyon: dosya secili degil, bos duruma donuluyor."
                )
                if hasattr(self, "_bos_duruma_don"):
                    self._bos_duruma_don()

            if hasattr(self, "_basari"):
                self._basari("operation_function_change")
            elif self._bilgi is not None:
                text = self._t("operation_function_change")
                if text == "operation_function_change":
                    text = "Fonksiyon Değiştir"
                self._bilgi.mesaj(text)

        ui_thread_uzerinde_calistir(_ui)

    def _motor_parca_degistir(self) -> None:
        """
        Parça değiştirme işlemini aktif başlık olarak ayarlar.
        """
        Logger.info("AnaEkranMenuAksiyon: _motor_parca_degistir girdi.")

        def _ui() -> None:
            self._aktif_islem_kodu = "parca_degistir"
            self._aktif_islem_basligini_yenile()

            if not str(self._secili_kaynak or "").strip():
                Logger.info(
                    "AnaEkranMenuAksiyon: dosya secili degil, bos duruma donuluyor."
                )
                if hasattr(self, "_bos_duruma_don"):
                    self._bos_duruma_don()

            if hasattr(self, "_basari"):
                self._basari("operation_partial_change")
            elif self._bilgi is not None:
                text = self._t("operation_partial_change")
                if text == "operation_partial_change":
                    text = "Parça Değiştir"
                self._bilgi.mesaj(text)

        ui_thread_uzerinde_calistir(_ui)

    def _motor_enjeksiyon(self) -> None:
        """
        Enjeksiyon işlemini aktif başlık olarak ayarlar.
        """
        Logger.info("AnaEkranMenuAksiyon: _motor_enjeksiyon girdi.")

        def _ui() -> None:
            self._aktif_islem_kodu = "enjeksiyon"
            self._aktif_islem_basligini_yenile()

            if not str(self._secili_kaynak or "").strip():
                Logger.info(
                    "AnaEkranMenuAksiyon: dosya secili degil, bos duruma donuluyor."
                )
                if hasattr(self, "_bos_duruma_don"):
                    self._bos_duruma_don()

            if hasattr(self, "_basari"):
                self._basari("operation_injection")
            elif self._bilgi is not None:
                text = self._t("operation_injection")
                if text == "operation_injection":
                    text = "Enjeksiyon"
                self._bilgi.mesaj(text)

        ui_thread_uzerinde_calistir(_ui)

    def _geri(self, *_args) -> None:
        """
        Geri aksiyonu.
        """
        Logger.info("AnaEkranMenuAksiyon: _geri girdi.")

        def _ui() -> None:
            if hasattr(self, "_basari"):
                self._basari("back")
            elif self._bilgi is not None:
                self._bilgi.mesaj(self._t("back"))

        ui_thread_uzerinde_calistir(_ui)

    def _yenile(self, *_args) -> None:
        """
        Mevcut kaynağı yeniden tarar.
        """
        Logger.info("AnaEkranMenuAksiyon: _yenile girdi.")

        def _ui() -> None:
            if not self._secili_kaynak:
                if hasattr(self, "_hata"):
                    self._hata("file_not_selected")
                elif self._bilgi is not None:
                    self._bilgi.mesaj(self._t("file_not_selected"), hata=True)
                return

            self._tara()

        ui_thread_uzerinde_calistir(_ui)

    def _ayarlar(self, *_args) -> None:
        """
        Ayarlar aksiyonu.
        """
        Logger.info("AnaEkranMenuAksiyon: _ayarlar girdi.")

        def _ui() -> None:
            if hasattr(self, "_basari"):
                self._basari("settings")
            elif self._bilgi is not None:
                self._bilgi.mesaj(self._t("settings"))

        ui_thread_uzerinde_calistir(_ui)