# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/ekranlar/ana_ekran_paketi/aksiyonlar_paketi/dil_aksiyonlari.py

ROL:
- Ana ekran dil seçim aksiyonlarını içerir
- Dil seçim popup'ını açar
- Dil değişimi sonrası UI yenileme akışını yönetir
- Ortak feedback pipeline ile entegre çalışır

MİMARİ:
- UI yalnızca servis facade katmanını bilir
- Dil aksiyonları burada toplanır
- Yerleşim kodu içermez
- Ortak feedback (_basari / _hata) kullanır
- Fail-soft davranır
- Geriye uyumluluk katmanı içermez
- UI yenileme sonrası mesajı güvenli zamanda gösterir
- Sıfır belirsizlikle deterministik akış izler

SURUM: 4
TARIH: 2026-03-28
IMZA: FY.
"""

from __future__ import annotations

from kivy.clock import Clock
from kivy.logger import Logger

from app.ui.popup.dil_sec_popup import dil_sec_popup


class AnaEkranDilAksiyonMixin:
    """
    Dil aksiyonları mixin'i.

    Notlar:
    - Başarı ve hata mesajları ortak feedback pipeline üzerinden verilir
    - UI yeniden kurulduktan sonra mesaj bir sonraki frame'de gösterilir
    - Dil değişimi sırasında ekran yeniden üretildiği için doğrudan anlık mesaj
      yerine schedule_once kullanılır
    """

    def _dil_sec(self, *_args) -> None:
        """
        Dil seçim popup'ını açar.
        """
        Logger.info("AnaEkranDilAksiyon: _dil_sec girdi.")

        def _basari_mesaji_goster(_dt: float) -> None:
            """
            UI yenilendikten sonra başarı mesajını gösterir.
            """
            try:
                self._basari("language_saved")
            except Exception as exc:
                Logger.exception(
                    f"AnaEkranDilAksiyon: basari mesaji gosterilemedi: {exc}"
                )
                if getattr(self, "_bilgi", None) is not None:
                    self._bilgi.mesaj(
                        self._t("language_saved"),
                        ikon="onaylandi.png",
                        pulse=True,
                        hata=False,
                    )

        def _hata_mesaji_goster(mesaj: str):
            """
            Hata mesajını bir sonraki frame'de gösterecek closure üretir.
            """

            def _goster(_dt: float) -> None:
                try:
                    if hasattr(self, "_hata"):
                        self._hata("error_title")
                    else:
                        raise RuntimeError("Base hata pipeline bulunamadi.")
                except Exception:
                    if getattr(self, "_bilgi", None) is not None:
                        self._bilgi.mesaj(
                            mesaj,
                            ikon="error.png",
                            pulse=True,
                            hata=True,
                        )

            return _goster

        def _degisti() -> None:
            """
            Dil değişti callback'i.
            """
            Logger.info("AnaEkranDilAksiyon: dil degisti callback geldi.")

            try:
                self._ui_yenile()
                Clock.schedule_once(_basari_mesaji_goster, 0)
            except Exception as exc:
                Logger.exception(f"AnaEkranDilAksiyon: dil degisimi hata: {exc}")
                hata_mesaji = f"{self._t('error_title')}: {exc}"
                Clock.schedule_once(_hata_mesaji_goster(hata_mesaji), 0)

        try:
            dil_sec_popup(
                services=self._services,
                on_degisti=_degisti,
            )
        except Exception as exc:
            Logger.exception(f"AnaEkranDilAksiyon: dil_sec_popup acilamadi: {exc}")
            if getattr(self, "_bilgi", None) is not None:
                self._bilgi.mesaj(
                    f"{self._t('error_title')}: {exc}",
                    ikon="error.png",
                    pulse=True,
                    hata=True,
                )