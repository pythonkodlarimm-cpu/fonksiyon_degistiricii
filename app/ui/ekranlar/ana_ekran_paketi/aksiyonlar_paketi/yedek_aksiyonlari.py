# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/ekranlar/ana_ekran_paketi/aksiyonlar_paketi/yedek_aksiyonlari.py

ROL:
- Ana ekran yedek aksiyonlarını içerir
- Yedek sayısını kullanıcıya bildirir
- BilgiKutusu feedback pipeline ile entegre çalışır
- UI etkilerini güvenli biçimde ana Kivy thread üzerinde yürütür

MİMARİ:
- UI yalnızca servis facade katmanını bilir
- Yedek aksiyonları burada toplanır
- Yerleşim kodu içermez
- Ortak feedback katmanını kullanır
- Fail-soft davranır
- Geriye uyumluluk katmanı içermez
- Deterministik sonuç üretir
- Lazy cache ile servis erişimi optimize edilir
- Sıfır belirsizlik hedeflenir
- Callback / popup / servis sonrası UI etkileri ortak ui_thread katmanı ile
  ana thread'e alınır

SURUM: 3
TARIH: 2026-03-29
IMZA: FY.
"""

from __future__ import annotations

from typing import Any

from kivy.logger import Logger

from app.ui.ortak.ui_thread import ui_thread_uzerinde_calistir


class AnaEkranYedekAksiyonMixin:
    """
    Yedek aksiyonları.
    """

    _yedek_servisi_cache: Any | None = None

    def _yedek_servisi(self):
        """
        Lazy + cached servis erişimi.
        """
        svc = self._yedek_servisi_cache
        if svc is None:
            svc = self._services.sil_yada_geri_yukle()
            self._yedek_servisi_cache = svc
        return svc

    def _yedekler(self, *_args) -> None:
        """
        Yedek sayısını kullanıcıya bildirir.
        """
        Logger.info("AnaEkranYedekAksiyon: _yedekler girdi.")

        try:
            servis = self._yedek_servisi()
            yedekler = servis.yedekleri_listele("degistirme")
            adet: int = len(yedekler or [])

            def _ui() -> None:
                if hasattr(self, "_basari"):
                    self._basari("backups_title", count=adet)
                elif self._bilgi is not None:
                    self._bilgi.mesaj(f"{self._t('backups_title')}: {adet}")

            ui_thread_uzerinde_calistir(_ui)

        except Exception as exc:
            Logger.exception(f"AnaEkranYedekAksiyon: _yedekler hata: {exc}")

            def _error_ui() -> None:
                if hasattr(self, "_hata"):
                    self._hata("backup_error")
                elif self._bilgi is not None:
                    self._bilgi.mesaj(
                        f"{self._t('backup')} {exc}",
                        hata=True,
                    )

            ui_thread_uzerinde_calistir(_error_ui)