# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/ekranlar/ana_ekran_paketi/aksiyonlar_paketi/gelistirici_aksiyonlari.py

ROL:
- Ana ekran geliştirici aksiyonlarını içerir
- Geliştirici ayarları / dil geliştirici ekranını açar
- Geliştirici ekrandan ana ekrana geri dönüş akışını sağlar

MİMARİ:
- UI yalnızca servis facade katmanını bilir
- Geliştirici ekran yönlendirmesi burada toplanır
- Yerleşim kodu içermez
- Fail-soft davranır
- Geriye uyumluluk katmanı içermez
- Ekran değiştirici varsa onu kullanır, yoksa kontrollü fallback uygular

SURUM: 2
TARIH: 2026-03-28
IMZA: FY.
"""

from __future__ import annotations

from kivy.logger import Logger


class AnaEkranGelistiriciAksiyonMixin:
    """
    Geliştirici aksiyonları.
    """

    def _gelistirici_ayarlardan_geri(self) -> None:
        """
        Geliştirici ekranından ana ekran görünümüne geri döner.
        """
        Logger.info("AnaEkranGelistiriciAksiyon: _gelistirici_ayarlardan_geri girdi.")

        try:
            self._ui_yenile()
        except Exception as exc:
            Logger.exception(
                "AnaEkranGelistiriciAksiyon: geri donus sirasinda ui_yenile hatasi: "
                f"{exc}"
            )
            if self._bilgi is not None:
                self._bilgi.mesaj(str(exc), hata=True)

    def _ac_gelistirici_ayarlar(self) -> None:
        """
        Geliştirici ayarları ekranını açar.
        """
        Logger.info("AnaEkranGelistiriciAksiyon: _ac_gelistirici_ayarlar girdi.")

        try:
            from app.ui.ekranlar.gelistirici_ayarlar import create_root

            ekran = create_root(
                servisler=self._services,
                t=self._t,
                on_geri=self._gelistirici_ayarlardan_geri,
            )

            ekran_degistir = getattr(self, "_ekran_degistir", None)
            if callable(ekran_degistir):
                ekran_degistir(ekran)
                return

            if hasattr(self, "clear_widgets") and callable(self.clear_widgets):
                self.clear_widgets()
                self.add_widget(ekran)
                Logger.info(
                    "AnaEkranGelistiriciAksiyon: fallback ile ekran dogrudan yerlestirildi."
                )
                return

            Logger.warning(
                "AnaEkranGelistiriciAksiyon: _ekran_degistir bulunamadi ve fallback uygulanamadi."
            )
            if self._bilgi is not None:
                self._bilgi.mesaj(
                    "Geliştirici ekranı açılamadı.",
                    hata=True,
                )

        except Exception as exc:
            Logger.exception(
                f"AnaEkranGelistiriciAksiyon: gelistirici ekran acilamadi: {exc}"
            )
            if self._bilgi is not None:
                self._bilgi.mesaj(str(exc), hata=True)