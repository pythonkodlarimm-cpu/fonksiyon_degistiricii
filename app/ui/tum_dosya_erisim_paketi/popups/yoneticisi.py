# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/tum_dosya_erisim_paketi/popups/yoneticisi.py

ROL:
- Tüm dosya erişim paketi popup katmanına tek giriş noktası sağlamak
- Popup modüllerini merkezileştirmek
- Üst katmanın popup dosyalarının iç detaylarını bilmesini engellemek
- Menü popup üzerinden dil seçimi akışına gerekli servis ve callback bilgisini iletmek
- Popup katmanında services bağımlılığını kontrollü biçimde aşağı aktarmak

MİMARİ:
- Lazy import kullanır
- Popup modüllerine doğrudan değil, bu yönetici üzerinden erişilir
- Üst katman sadece bu yöneticiyi bilir
- Menü popup açılışında servis ve dil callback bağımlılıkları bu katmandan geçirilir
- Basit popup, onay popup, indirme sonuç popup, yedek görüntüleme popup
  ve yedekler popup çağrılarında services parametresi aşağı aktarılabilir
- Hardcoded kullanıcı metni minimumda tutulur ve override edilebilir

API UYUMLULUK:
- Platform bağımsızdır
- Android API 35 ile uyumludur
- Doğrudan Android bridge çağrısı içermez

SURUM: 6
TARIH: 2026-03-23
IMZA: FY.
"""

from __future__ import annotations


class TumDosyaErisimPopupsYoneticisi:
    # =========================================================
    # SIMPLE / BASIC
    # =========================================================
    def show_simple_popup(
        self,
        title_text: str,
        body_text: str,
        icon_name: str = "onaylandi.png",
        auto_close_seconds: float | None = 1.8,
        compact: bool = True,
        services=None,
    ):
        from app.ui.tum_dosya_erisim_paketi.popups.basit_popup import (
            show_simple_popup,
        )

        return show_simple_popup(
            title_text=title_text,
            body_text=body_text,
            icon_name=icon_name,
            auto_close_seconds=auto_close_seconds,
            compact=compact,
            services=services,
        )

    # =========================================================
    # MENU
    # =========================================================
    def open_main_menu(
        self,
        open_backups_popup,
        on_language_changed=None,
        services=None,
    ):
        from app.ui.tum_dosya_erisim_paketi.popups.menu_popup import (
            open_main_menu,
        )

        return open_main_menu(
            open_backups_popup=open_backups_popup,
            on_language_changed=on_language_changed,
            services=services,
        )

    # =========================================================
    # CONFIRM
    # =========================================================
    def show_confirm_popup(
        self,
        title_text: str,
        body_text: str,
        on_confirm,
        confirm_icon: str = "delete.png",
        services=None,
    ):
        from app.ui.tum_dosya_erisim_paketi.popups.onay_popup import (
            show_confirm_popup,
        )

        return show_confirm_popup(
            title_text=title_text,
            body_text=body_text,
            on_confirm=on_confirm,
            confirm_icon=confirm_icon,
            services=services,
        )

    # =========================================================
    # DOWNLOAD RESULT
    # =========================================================
    def show_download_result_popup(
        self,
        saved_path,
        selected_by_user: bool = False,
        services=None,
    ):
        from app.ui.tum_dosya_erisim_paketi.popups.indirme_sonuc_popup import (
            show_download_result_popup,
        )

        return show_download_result_popup(
            saved_path=saved_path,
            selected_by_user=selected_by_user,
            services=services,
        )

    # =========================================================
    # DELETE STATUS
    # =========================================================
    def silme_durum_popup_sinifi(self):
        from app.ui.tum_dosya_erisim_paketi.popups.silme_durum_popup import (
            SilmeDurumPopup,
        )

        return SilmeDurumPopup

    def silme_durum_popup_olustur(
        self,
        title_text: str = "",
        body_text: str = "",
        success_text: str = "",
        icon_name: str = "onaylandi.png",
        services=None,
    ):
        sinif = self.silme_durum_popup_sinifi()
        return sinif(
            title_text=title_text,
            body_text=body_text,
            success_text=success_text,
            icon_name=icon_name,
            services=services,
        )

    # =========================================================
    # BACKUP VIEW
    # =========================================================
    def open_backup_view_popup(self, yedek, services=None):
        from app.ui.tum_dosya_erisim_paketi.popups.yedek_goruntuleme_popup import (
            open_backup_view_popup,
        )

        return open_backup_view_popup(
            yedek=yedek,
            services=services,
        )

    # =========================================================
    # BACKUPS LIST
    # =========================================================
    def open_backups_popup(self, debug=None, services=None):
        from app.ui.tum_dosya_erisim_paketi.popups.yedekler_popup import (
            open_backups_popup,
        )

        return open_backups_popup(
            debug=debug,
            services=services,
    )
