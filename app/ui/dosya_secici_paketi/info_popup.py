# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/dosya_secici_paketi/info_popup.py

ROL:
- Bilgi / hata popup'ları
- Android erişim açıklama popup'ı
"""

from __future__ import annotations

from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup

from app.ui.icon_toolbar import IconToolbar
from app.ui.tema import TEXT_MUTED, TEXT_PRIMARY


def show_info_popup(owner, title: str, message: str) -> None:
    try:
        owner._debug(f"POPUP -> {title}: {message}")
    except Exception:
        pass

    icerik = BoxLayout(
        orientation="vertical",
        spacing=dp(10),
        padding=dp(12),
    )

    lbl = Label(
        text=message,
        color=TEXT_PRIMARY,
        halign="left",
        valign="middle",
    )
    lbl.bind(size=lambda inst, size: setattr(inst, "text_size", size))
    icerik.add_widget(lbl)

    btn = Button(
        text="Tamam",
        size_hint_y=None,
        height=dp(42),
        background_normal="",
        background_down="",
        background_color=(0.20, 0.20, 0.24, 1),
        color=TEXT_PRIMARY,
    )

    popup = Popup(
        title=title,
        content=icerik,
        size_hint=(0.86, 0.36),
        auto_dismiss=False,
    )

    btn.bind(on_release=lambda *_: popup.dismiss())
    icerik.add_widget(btn)
    popup.open()


def show_android_access_popup(owner, on_continue, on_settings) -> None:
    ana = BoxLayout(
        orientation="vertical",
        spacing=dp(12),
        padding=dp(12),
    )

    mesaj = (
        "Python dosyası seçmek üzeresiniz.\n\n"
        "Uygulama yalnızca sizin seçtiğiniz dosyaya erişir.\n"
        "Bu erişimi daha sonra cihaz ayarlarından değiştirebilirsiniz.\n\n"
        "Devam ettiğinizde Android sistem dosya seçicisi açılacaktır."
    )

    lbl = Label(
        text=mesaj,
        color=TEXT_PRIMARY,
        halign="left",
        valign="top",
        size_hint_y=None,
        font_size="15sp",
    )

    def _lbl_guncelle(*_args):
        try:
            lbl.text_size = (lbl.width, None)
            lbl.texture_update()
            lbl.height = lbl.texture_size[1]
        except Exception:
            pass

    lbl.bind(width=lambda *_: _lbl_guncelle(), texture_size=lambda *_: _lbl_guncelle())
    _lbl_guncelle()
    ana.add_widget(lbl)

    toolbar = IconToolbar(
        spacing_dp=18,
        padding_dp=6,
    )

    vazgec_btn = toolbar.add_tool(
        icon_name="cancel.png",
        text="Vazgeç",
        on_release=lambda *_: None,
        icon_size_dp=36,
        text_size="11sp",
        color=TEXT_MUTED,
        icon_bg=None,
    )

    ayarlar_btn = toolbar.add_tool(
        icon_name="settings.png",
        text="Ayarlar",
        on_release=lambda *_: None,
        icon_size_dp=36,
        text_size="11sp",
        color=TEXT_MUTED,
        icon_bg=None,
    )

    devam_btn = toolbar.add_tool(
        icon_name="onaylandi.png",
        text="Devam",
        on_release=lambda *_: None,
        icon_size_dp=36,
        text_size="11sp",
        color=TEXT_MUTED,
        icon_bg=None,
    )

    ana.add_widget(toolbar)

    popup = Popup(
        title="Dosya Erişimi",
        content=ana,
        size_hint=(0.92, 0.50),
        auto_dismiss=False,
        separator_height=0,
    )

    def _vazgec(*_args):
        try:
            owner._debug("Picker bilgi popup: vazgeç")
        except Exception:
            pass
        popup.dismiss()

    def _ayarlar(*_args):
        try:
            owner._debug("Picker bilgi popup: ayarlar")
        except Exception:
            pass
        on_settings()

    def _devam(*_args):
        try:
            owner._debug("Picker bilgi popup: devam")
        except Exception:
            pass
        popup.dismiss()
        on_continue()

    vazgec_btn.bind(on_release=_vazgec)
    ayarlar_btn.bind(on_release=_ayarlar)
    devam_btn.bind(on_release=_devam)

    popup.open()