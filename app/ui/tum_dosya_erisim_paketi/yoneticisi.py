# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/tum_dosya_erisim_paketi/yoneticisi.py

ROL:
- Tüm dosya erişim paketi için tek giriş noktası sağlamak
- Alt paket yöneticilerini merkezileştirmek
- Üst katmanın iç modül detaylarını bilmesini engellemek

MİMARİ:
- Üst katman sadece bu yöneticiyi bilir
- Alt paketlere lazy import ile erişir
- Panel, popup, yedek ve ortak akışları burada toplanır

API UYUMLULUK:
- Platform bağımsızdır
- Android API 35 ile uyumludur
- Doğrudan Android bridge çağrısı içermez

SURUM: 3
TARIH: 2026-03-22
IMZA: FY.
"""

from __future__ import annotations


class TumDosyaErisimYoneticisi:
    # =========================================================
    # ALT YONETICILER
    # =========================================================
    def _panel_yoneticisi(self):
        from app.ui.tum_dosya_erisim_paketi.panel import (
            TumDosyaErisimPanelYoneticisi,
        )
        return TumDosyaErisimPanelYoneticisi()

    def _popups_yoneticisi(self):
        from app.ui.tum_dosya_erisim_paketi.popups import (
            TumDosyaErisimPopupsYoneticisi,
        )
        return TumDosyaErisimPopupsYoneticisi()

    def _yedek_yoneticisi(self):
        from app.ui.tum_dosya_erisim_paketi.yedek import (
            TumDosyaErisimYedekYoneticisi,
        )
        return TumDosyaErisimYedekYoneticisi()

    def _ortak_yoneticisi(self):
        from app.ui.tum_dosya_erisim_paketi.ortak import (
            TumDosyaErisimOrtakYoneticisi,
        )
        return TumDosyaErisimOrtakYoneticisi()

    # =========================================================
    # PANEL
    # =========================================================
    def panel_sinifi(self):
        return self._panel_yoneticisi().panel_sinifi()

    def panel_olustur(self, **kwargs):
        return self._panel_yoneticisi().panel_olustur(**kwargs)

    # =========================================================
    # POPUPS
    # =========================================================
    def show_simple_popup(
        self,
        title_text: str,
        body_text: str,
        icon_name: str = "onaylandi.png",
        auto_close_seconds: float | None = 1.8,
        compact: bool = True,
    ):
        return self._popups_yoneticisi().show_simple_popup(
            title_text=title_text,
            body_text=body_text,
            icon_name=icon_name,
            auto_close_seconds=auto_close_seconds,
            compact=compact,
        )

    def open_main_menu(self, open_backups_popup):
        return self._popups_yoneticisi().open_main_menu(
            open_backups_popup=open_backups_popup,
        )

    def show_confirm_popup(
        self,
        title_text: str,
        body_text: str,
        on_confirm,
        confirm_icon: str = "delete.png",
    ):
        return self._popups_yoneticisi().show_confirm_popup(
            title_text=title_text,
            body_text=body_text,
            on_confirm=on_confirm,
            confirm_icon=confirm_icon,
        )

    def show_download_result_popup(
        self,
        saved_path,
        selected_by_user: bool = False,
    ):
        return self._popups_yoneticisi().show_download_result_popup(
            saved_path=saved_path,
            selected_by_user=selected_by_user,
        )

    def silme_durum_popup_sinifi(self):
        return self._popups_yoneticisi().silme_durum_popup_sinifi()

    def silme_durum_popup_olustur(
        self,
        title_text="Silme İşlemi",
        body_text="Silme işlemi başlatılıyor...",
        success_text="Silme tamamlandı.",
        icon_name="onaylandi.png",
    ):
        return self._popups_yoneticisi().silme_durum_popup_olustur(
            title_text=title_text,
            body_text=body_text,
            success_text=success_text,
            icon_name=icon_name,
        )

    def open_backup_view_popup(self, yedek):
        return self._popups_yoneticisi().open_backup_view_popup(yedek)

    def open_backups_popup(self, debug=None):
        return self._popups_yoneticisi().open_backups_popup(debug=debug)

    # =========================================================
    # YEDEK
    # =========================================================
    def yedek_satiri_olustur(self, yedek, on_view, on_download, on_delete):
        return self._yedek_yoneticisi().yedek_satiri_olustur(
            yedek=yedek,
            on_view=on_view,
            on_download=on_download,
            on_delete=on_delete,
        )

    def yedek_indirme_islemi_baslat(
        self,
        debug,
        yedek,
        hedef_klasor=None,
    ):
        return self._yedek_yoneticisi().yedek_indirme_islemi_baslat(
            debug=debug,
            yedek=yedek,
            hedef_klasor=hedef_klasor,
        )

    def dosya_yolu_ac(self, path_value, debug=None) -> bool:
        return self._yedek_yoneticisi().dosya_yolu_ac(
            path_value=path_value,
            debug=debug,
        )

    # =========================================================
    # ORTAK
    # =========================================================
    def tiklanabilir_icon_sinifi(self):
        return self._ortak_yoneticisi().tiklanabilir_icon_sinifi()

    def animated_separator_sinifi(self):
        return self._ortak_yoneticisi().animated_separator_sinifi()

    def start_icon_glow(self, widget, size_small_dp=36, size_big_dp=40, duration=0.60):
        return self._ortak_yoneticisi().start_icon_glow(
            widget=widget,
            size_small_dp=size_small_dp,
            size_big_dp=size_big_dp,
            duration=duration,
        )

    def dil_popup_baslat(self, *args, **kwargs):
        return self._ortak_yoneticisi().dil_popup_baslat(*args, **kwargs)
