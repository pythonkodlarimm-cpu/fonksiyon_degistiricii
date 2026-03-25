# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/editor_paketi/yoneticisi.py

ROL:
- Editor paketine tek giriş noktası sağlamak
- Alt paket yöneticilerini merkezileştirmek
- Üst katmanın editor paketi iç yapısını bilmesini engellemek
- Panel, root, aksiyon, popup, doğrulama, bildirim, bileşen ve yardımcı akışları tek yerden sunmak
- Editör popup ve panel akışlarında seçili dil destekli metinlerin aşağı katmanda korunmasına aracılık etmek

MİMARİ:
- Üst katman sadece bu yöneticiyi bilir
- Alt paketlere doğrudan erişim yerine ilgili yönetici sınıfları kullanılır
- Lazy import korunur
- Paket dışına iç modül detayları sızdırılmaz
- Editor paneli oluşturma akışı üst katmandan gelen callback'leri bozmadan aşağı taşır
- Popup ve yardımcı akışlar ilgili alt yöneticiler üzerinden merkezi biçimde yürütülür

API UYUMLULUK:
- Platform bağımsızdır
- Android API 35 ile uyumludur
- Doğrudan Android bridge çağrısı içermez

SURUM: 3
TARIH: 2026-03-23
IMZA: FY.
"""

from __future__ import annotations


class EditorYoneticisi:
    # =========================================================
    # ALT YONETICILER
    # =========================================================
    def _panel_yoneticisi(self):
        from app.ui.editor_paketi.panel import PanelYoneticisi
        return PanelYoneticisi()

    def _root_yoneticisi(self):
        from app.ui.editor_paketi.root import RootYoneticisi
        return RootYoneticisi()

    def _aksiyon_yoneticisi(self):
        from app.ui.editor_paketi.aksiyon import AksiyonYoneticisi
        return AksiyonYoneticisi()

    def _popup_yoneticisi(self):
        from app.ui.editor_paketi.popup import PopupYoneticisi
        return PopupYoneticisi()

    def _dogrulama_yoneticisi(self):
        from app.ui.editor_paketi.dogrulama import DogrulamaYoneticisi
        return DogrulamaYoneticisi()

    def _bildirim_yoneticisi(self):
        from app.ui.editor_paketi.bildirim import BildirimYoneticisi
        return BildirimYoneticisi()

    def _bilesenler_yoneticisi(self):
        from app.ui.editor_paketi.bilesenler import BilesenlerYoneticisi
        return BilesenlerYoneticisi()

    def _yardimci_yoneticisi(self):
        from app.ui.editor_paketi.yardimci import YardimciYoneticisi
        return YardimciYoneticisi()

    # =========================================================
    # PANEL
    # =========================================================
    def panel_sinifi(self):
        return self._panel_yoneticisi().panel_sinifi()

    def panel_olustur(self, **kwargs):
        return self._panel_yoneticisi().panel_olustur(**kwargs)

    # =========================================================
    # ROOT
    # =========================================================
    def root_sinifi(self):
        return self._root_yoneticisi().root_sinifi()

    def root_olustur(self, **kwargs):
        return self._root_yoneticisi().root_olustur(**kwargs)

    # =========================================================
    # AKSIYON
    # =========================================================
    def copy_current_to_new(self, panel, *_args):
        return self._aksiyon_yoneticisi().copy_current_to_new(panel, *_args)

    def clear_new_code(self, panel, *_args):
        return self._aksiyon_yoneticisi().clear_new_code(panel, *_args)

    def check_new_code(self, panel, *_args):
        return self._aksiyon_yoneticisi().check_new_code(panel, *_args)

    def handle_update(self, panel, *_args):
        return self._aksiyon_yoneticisi().handle_update(panel, *_args)

    def handle_restore(self, panel, *_args):
        return self._aksiyon_yoneticisi().handle_restore(panel, *_args)

    # =========================================================
    # POPUP
    # =========================================================
    def build_popup_toolbar(self, actions):
        return self._popup_yoneticisi().build_popup_toolbar(actions)

    def open_current_code_popup(self, panel, *_args):
        return self._popup_yoneticisi().open_current_code_popup(panel, *_args)

    def open_new_code_editor_popup(self, panel, *_args):
        return self._popup_yoneticisi().open_new_code_editor_popup(panel, *_args)

    # =========================================================
    # DOGRULAMA
    # =========================================================
    def normalize_code_text(self, text, trim_outer_blank_lines: bool = False) -> str:
        return self._dogrulama_yoneticisi().normalize_code_text(
            text,
            trim_outer_blank_lines=trim_outer_blank_lines,
        )

    def first_meaningful_line(self, text: str) -> str:
        return self._dogrulama_yoneticisi().first_meaningful_line(text)

    def looks_like_full_function(self, text: str) -> bool:
        return self._dogrulama_yoneticisi().looks_like_full_function(text)

    def basic_parse_check(self, text: str) -> None:
        return self._dogrulama_yoneticisi().basic_parse_check(text)

    def extract_line_number(self, exc) -> int:
        return self._dogrulama_yoneticisi().extract_line_number(exc)

    def validate_new_code(self, text: str) -> tuple[bool, str, int]:
        return self._dogrulama_yoneticisi().validate_new_code(text)

    # =========================================================
    # BILDIRIM
    # =========================================================
    def bildirim_sinifi(self):
        return self._bildirim_yoneticisi().bildirim_sinifi()

    def bildirim_olustur(self, **kwargs):
        return self._bildirim_yoneticisi().bildirim_olustur(**kwargs)

    # =========================================================
    # BILESENLER
    # =========================================================
    def kod_editoru_sinifi(self):
        return self._bilesenler_yoneticisi().kod_editoru_sinifi()

    def kod_paneli_sinifi(self):
        return self._bilesenler_yoneticisi().kod_paneli_sinifi()

    def bilgi_kutusu_sinifi(self):
        return self._bilesenler_yoneticisi().bilgi_kutusu_sinifi()

    def sade_kod_alani_sinifi(self):
        return self._bilesenler_yoneticisi().sade_kod_alani_sinifi()

    def sade_kod_alani_olustur(self, **kwargs):
        return self._bilesenler_yoneticisi().sade_kod_alani_olustur(**kwargs)

    def bilgi_kutusu_olustur(self, **kwargs):
        return self._bilesenler_yoneticisi().bilgi_kutusu_olustur(**kwargs)

    # =========================================================
    # YARDIMCI
    # =========================================================
    def toast(self, text: str, icon_name: str = "", duration: float = 2.2) -> None:
        return self._yardimci_yoneticisi().toast(
            text=text,
            icon_name=icon_name,
            duration=duration,
        )

    def close_popups(self, panel) -> None:
        return self._yardimci_yoneticisi().close_popups(panel)

    def current_item_display(self, panel) -> str:
        return self._yardimci_yoneticisi().current_item_display(panel)

    def show_inline_notice(
        self,
        panel,
        title: str,
        text: str,
        icon_name: str = "onaylandi.png",
        tone: str = "success",
        duration: float = 4.0,
        on_tap=None,
    ) -> None:
        return self._yardimci_yoneticisi().show_inline_notice(
            panel=panel,
            title=title,
            text=text,
            icon_name=icon_name,
            tone=tone,
            duration=duration,
            on_tap=on_tap,
        )

    def set_status_info(self, panel, message: str = "", line_no: int = 0):
        return self._yardimci_yoneticisi().set_status_info(panel, message, line_no)

    def set_status_warning(self, panel, message: str = "", line_no: int = 0):
        return self._yardimci_yoneticisi().set_status_warning(panel, message, line_no)

    def set_status_error(self, panel, message: str = "", line_no: int = 0):
        return self._yardimci_yoneticisi().set_status_error(panel, message, line_no)

    def set_status_success(self, panel, message: str = "", line_no: int = 0):
        return self._yardimci_yoneticisi().set_status_success(panel, message, line_no)

    def set_popup_error(
        self,
        label,
        editor_area,
        message: str = "",
        line_no: int = 0,
    ):
        return self._yardimci_yoneticisi().set_popup_error(
            label,
            editor_area,
            message,
            line_no,
        )
