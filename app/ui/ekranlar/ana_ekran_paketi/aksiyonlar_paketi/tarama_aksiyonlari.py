# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/ekranlar/ana_ekran_paketi/aksiyonlar_paketi/tarama_aksiyonlari.py

ROL:
- Ana ekran tarama ve doğrulama aksiyonlarını içerir
- Seçili kaynaktaki fonksiyonları tarar
- Yeni kod alanındaki fonksiyonu doğrular
- BilgiKutusu feedback pipeline ile entegre çalışır
- UI güncellemelerini güvenli biçimde ana Kivy thread üzerinde yürütür

MİMARİ:
- UI yalnızca servis facade katmanını bilir
- Tarama ve doğrulama sorumluluğu burada toplanır
- Yerleşim kodu içermez
- Ortak feedback katmanını kullanır
- Fail-soft davranır
- Geriye uyumluluk katmanı içermez
- Deterministik sonuç üretmeye odaklanır
- Lazy cache ile servis erişimi optimize edilir
- Silent mode ile kontrol edilen feedback üretimi sağlar
- Tarama sonrası UI etkileri ortak ui_thread katmanı ile ana thread'e alınır

SURUM: 5
TARIH: 2026-03-29
IMZA: FY.
"""

from __future__ import annotations

from typing import Any

from kivy.logger import Logger

from app.ui.ortak.ui_thread import ui_thread_uzerinde_calistir


class AnaEkranTaramaAksiyonMixin:
    """
    Tarama ve doğrulama aksiyonları.
    """

    _fonksiyon_servisi_cache: Any | None = None

    def _fonksiyon_servisi(self):
        """
        Lazy + cached servis erişimi.
        """
        svc = self._fonksiyon_servisi_cache
        if svc is None:
            svc = self._services.fonksiyon_islemleri()
            self._fonksiyon_servisi_cache = svc
        return svc

    def _tara(self, *_args, silent: bool = False) -> None:
        """
        Seçili kaynaktaki fonksiyonları tarar ve listeye yükler.

        Parametre:
        - silent: True ise kullanıcıya mesaj göstermez (arka plan tarama)
        """
        kaynak = self._secili_kaynak
        Logger.info(
            f"AnaEkranTaramaAksiyon: _tara girdi. secili_kaynak={kaynak!r} silent={silent}"
        )

        if not kaynak:
            def _no_file_ui() -> None:
                if not silent:
                    if hasattr(self, "_hata"):
                        self._hata("file_not_selected")
                    elif self._bilgi is not None:
                        self._bilgi.mesaj(self._t("file_not_selected"), hata=True)

            ui_thread_uzerinde_calistir(_no_file_ui)
            return

        try:
            servis = self._fonksiyon_servisi()
            items = servis.dosyadan_fonksiyonlari_tara(kaynak)
            liste = list(items or [])

            def _ui() -> None:
                self._listeyi_yukle(liste)

                if not silent:
                    if hasattr(self, "_basari"):
                        self._basari("scan_completed_with_count", count=len(liste))
                    elif self._bilgi is not None:
                        self._bilgi.mesaj(
                            self._t("scan_completed_with_count", count=len(liste))
                        )

            ui_thread_uzerinde_calistir(_ui)

        except Exception as exc:
            Logger.exception(f"AnaEkranTaramaAksiyon: _tara hata: {exc}")

            def _error_ui() -> None:
                if hasattr(self, "_hata"):
                    self._hata("scan_error_message")
                elif self._bilgi is not None:
                    self._bilgi.mesaj(
                        f"{self._t('scan_error_message')} {exc}",
                        hata=True,
                    )

            ui_thread_uzerinde_calistir(_error_ui)

    def _kontrol(self, *_args) -> None:
        """
        Yeni kod alanındaki fonksiyonu doğrular.
        """
        Logger.info("AnaEkranTaramaAksiyon: _kontrol girdi.")

        yeni_kod = self._yeni_kod_metni_al()

        if not yeni_kod:
            def _empty_ui() -> None:
                if hasattr(self, "_hata"):
                    self._hata("validation_error_new_code_empty")
                elif self._bilgi is not None:
                    self._bilgi.mesaj(
                        self._t("validation_error_new_code_empty"),
                        hata=True,
                    )

            ui_thread_uzerinde_calistir(_empty_ui)
            return

        if self._yeni_kodu_dogrula(yeni_kod):
            def _success_ui() -> None:
                if hasattr(self, "_basari"):
                    self._basari("validation_successful")
                elif self._bilgi is not None:
                    self._bilgi.mesaj(self._t("validation_successful"))

            ui_thread_uzerinde_calistir(_success_ui)