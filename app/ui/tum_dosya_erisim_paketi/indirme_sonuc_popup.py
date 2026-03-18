# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path

from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup

from app.ui.tema import TEXT_MUTED, TEXT_PRIMARY
from app.ui.tum_dosya_erisim_paketi.bilesenler import AnimatedSeparator


def _open_path_in_file_manager(path_value: str | Path) -> bool:
    try:
        from kivy.utils import platform
    except Exception:
        return False

    if platform != "android":
        return False

    try:
        from android import mActivity
        from jnius import autoclass

        path_obj = Path(str(path_value or "").strip())
        if not path_obj.exists():
            return False

        target_dir = path_obj.parent if path_obj.is_file() else path_obj

        Intent = autoclass("android.content.Intent")
        Uri = autoclass("android.net.Uri")
        File = autoclass("java.io.File")

        intent = Intent(Intent.ACTION_VIEW)
        uri = Uri.fromFile(File(str(target_dir)))

        intent.setDataAndType(uri, "*/*")
        intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)

        chooser = Intent.createChooser(intent, "Konumu Aç")
        chooser.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)

        mActivity.startActivity(chooser)
        return True
    except Exception:
        return False


def show_download_result_popup(
    saved_path: str | Path,
    selected_by_user: bool = False,
):
    hedef = str(saved_path or "").strip()

    title_text = "İşlem Tamam"
    if selected_by_user:
        body_text = f"Yedek şu konuma kaydedildi:\n{hedef}"
    else:
        body_text = f"Yedek varsayılan konuma kaydedildi:\n{hedef}"

    content = BoxLayout(
        orientation="vertical",
        padding=dp(14),
        spacing=dp(10),
    )

    title = Label(
        text=title_text,
        color=TEXT_PRIMARY,
        font_size="17sp",
        bold=True,
        size_hint_y=None,
        height=dp(26),
        halign="center",
        valign="middle",
    )
    title.bind(size=lambda inst, size: setattr(inst, "text_size", size))
    content.add_widget(title)

    content.add_widget(AnimatedSeparator())

    body = Label(
        text=body_text,
        color=TEXT_MUTED,
        font_size="12sp",
        size_hint_y=None,
        height=dp(86),
        halign="center",
        valign="middle",
    )
    body.bind(size=lambda inst, size: setattr(inst, "text_size", (size[0], None)))
    content.add_widget(body)

    content.add_widget(AnimatedSeparator())

    button_row = BoxLayout(
        orientation="horizontal",
        size_hint_y=None,
        height=dp(42),
        spacing=dp(8),
    )

    btn_open = Button(
        text="Konumu Aç",
        background_normal="",
        background_color=(0.18, 0.55, 0.28, 1),
        color=(0.95, 0.95, 0.98, 1),
    )

    btn_ok = Button(
        text="Tamam",
        background_normal="",
        background_color=(0.18, 0.18, 0.22, 1),
        color=(0.95, 0.95, 0.98, 1),
    )

    button_row.add_widget(btn_open)
    button_row.add_widget(btn_ok)
    content.add_widget(button_row)

    popup = Popup(
        title="",
        content=content,
        size_hint=(0.88, 0.34),
        auto_dismiss=True,
        separator_height=0,
    )

    def _on_open(*_args):
        acildi = _open_path_in_file_manager(hedef)
        if acildi:
            popup.dismiss()
            return

        from app.ui.tum_dosya_erisim_paketi.basit_popup import show_simple_popup

        show_simple_popup(
            title_text="Konum Açılamadı",
            body_text="Dosya yöneticisi ile konum açılamadı.",
            icon_name="warning.png",
            auto_close_seconds=1.7,
            compact=True,
        )

    def _on_ok(*_args):
        popup.dismiss()

    btn_open.bind(on_release=_on_open)
    btn_ok.bind(on_release=_on_ok)

    popup.open()
    return popup