# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/fonksiyon_listesi_paketi/yoneticisi.py

ROL:
- Fonksiyon listesi paketi için tek giriş noktası sağlar
- Alt paket yöneticilerini merkezileştirir
- Üst katmanın iç modül detaylarını bilmesini engeller
- Panel oluşturma ve alt akış erişimlerini tek kapıdan sunar

MİMARİ:
- Lazy import kullanır
- Panel oluşturma akışında services ve callback zincirini aşağı taşır
- Alt paketlere doğrudan değil, ilgili yönetici sınıfları üzerinden erişir
- Paket dışına iç modül detayları sızdırılmaz
- Fail-soft yaklaşım kullanır (çökmez, log basar)

API UYUMLULUK:
- Platform bağımsızdır
- Android API 35 ile uyumludur
- Doğrudan Android bridge çağrısı içermez

SURUM: 3
TARIH: 2026-03-23
IMZA: FY.
"""

from __future__ import annotations

import traceback


class FonksiyonListesiYoneticisi:
    # =========================================================
    # ALT YONETICILER
    # =========================================================
    def _panel_yoneticisi(self):
        try:
            from app.ui.fonksiyon_listesi_paketi.panel import PanelYoneticisi
            return PanelYoneticisi()
        except Exception:
            print("[FONK_LIST_YONETICI] PanelYoneticisi yüklenemedi.")
            print(traceback.format_exc())
            raise

    def _satir_yoneticisi(self):
        try:
            from app.ui.fonksiyon_listesi_paketi.satir import SatirYoneticisi
            return SatirYoneticisi()
        except Exception:
            print("[FONK_LIST_YONETICI] SatirYoneticisi yüklenemedi.")
            print(traceback.format_exc())
            raise

    def _arama_yoneticisi(self):
        try:
            from app.ui.fonksiyon_listesi_paketi.arama import AramaYoneticisi
            return AramaYoneticisi()
        except Exception:
            print("[FONK_LIST_YONETICI] AramaYoneticisi yüklenemedi.")
            print(traceback.format_exc())
            raise

    def _onizleme_yoneticisi(self):
        try:
            from app.ui.fonksiyon_listesi_paketi.onizleme import OnizlemeYoneticisi
            return OnizlemeYoneticisi()
        except Exception:
            print("[FONK_LIST_YONETICI] OnizlemeYoneticisi yüklenemedi.")
            print(traceback.format_exc())
            raise

    def _yardimci_yoneticisi(self):
        try:
            from app.ui.fonksiyon_listesi_paketi.yardimci import YardimciYoneticisi
            return YardimciYoneticisi()
        except Exception:
            print("[FONK_LIST_YONETICI] YardimciYoneticisi yüklenemedi.")
            print(traceback.format_exc())
            raise

    def _gorunum_akisi_yoneticisi(self):
        try:
            from app.ui.fonksiyon_listesi_paketi.gorunum_akisi import (
                GorunumAkisiYoneticisi,
            )
            return GorunumAkisiYoneticisi()
        except Exception:
            print("[FONK_LIST_YONETICI] GorunumAkisiYoneticisi yüklenemedi.")
            print(traceback.format_exc())
            raise

    def _hata_akisi_yoneticisi(self):
        try:
            from app.ui.fonksiyon_listesi_paketi.hata_akisi import (
                HataAkisiYoneticisi,
            )
            return HataAkisiYoneticisi()
        except Exception:
            print("[FONK_LIST_YONETICI] HataAkisiYoneticisi yüklenemedi.")
            print(traceback.format_exc())
            raise

    def _ui_kurulumu_yoneticisi(self):
        try:
            from app.ui.fonksiyon_listesi_paketi.ui_kurulumu import (
                UiKurulumuYoneticisi,
            )
            return UiKurulumuYoneticisi()
        except Exception:
            print("[FONK_LIST_YONETICI] UiKurulumuYoneticisi yüklenemedi.")
            print(traceback.format_exc())
            raise

    def _render_akisi_yoneticisi(self):
        try:
            from app.ui.fonksiyon_listesi_paketi.render_akisi import (
                RenderAkisiYoneticisi,
            )
            return RenderAkisiYoneticisi()
        except Exception:
            print("[FONK_LIST_YONETICI] RenderAkisiYoneticisi yüklenemedi.")
            print(traceback.format_exc())
            raise

    # =========================================================
    # PANEL
    # =========================================================
    def panel_sinifi(self):
        try:
            return self._panel_yoneticisi().panel_sinifi()
        except Exception:
            print("[FONK_LIST_YONETICI] panel_sinifi alınamadı.")
            print(traceback.format_exc())
            raise

    def panel_olustur(
        self,
        on_select,
        on_error=None,
        services=None,
        **kwargs,
    ):
        try:
            if services is None:
                print("[FONK_LIST_YONETICI] UYARI: services verilmedi.")

            return self._panel_yoneticisi().panel_olustur(
                on_select=on_select,
                on_error=on_error,
                services=services,
                **kwargs,
            )

        except Exception:
            print("[FONK_LIST_YONETICI] Panel oluşturulamadı.")
            print(traceback.format_exc())
            raise

    # =========================================================
    # ALT AKISLAR
    # =========================================================
    def satir_sinifi(self):
        return self._satir_yoneticisi().satir_sinifi()

    def satir_olustur(
        self,
        item,
        on_press_row,
        on_error=None,
        is_selected=False,
        services=None,
        **kwargs,
    ):
        return self._satir_yoneticisi().satir_olustur(
            item=item,
            on_press_row=on_press_row,
            on_error=on_error,
            is_selected=is_selected,
            services=services,
            **kwargs,
        )

    def arama_yoneticisi(self):
        return self._arama_yoneticisi()

    def onizleme_yoneticisi(self):
        return self._onizleme_yoneticisi()

    def yardimci_yoneticisi(self):
        return self._yardimci_yoneticisi()

    def gorunum_akisi_yoneticisi(self):
        return self._gorunum_akisi_yoneticisi()

    def hata_akisi_yoneticisi(self):
        return self._hata_akisi_yoneticisi()

    def ui_kurulumu_yoneticisi(self):
        return self._ui_kurulumu_yoneticisi()

    def render_akisi_yoneticisi(self):
        return self._render_akisi_yoneticisi()
