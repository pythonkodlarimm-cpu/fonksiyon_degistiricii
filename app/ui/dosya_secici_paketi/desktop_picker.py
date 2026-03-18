# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/dosya_secici_paketi/desktop_picker.py

ROL:
- Masaüstü / path tabanlı belge seçici popup'ını açar
- Klasörler ve dosyalar arasında gezinmeyi sağlar
- Seçilen dosya için sade bir DocumentSelection üretir

NOT:
- Bu picker Android sistem picker'ı değildir
- Path tabanlı seçim için kullanılır
- Android API 34 açısından doğrudan özel çağrı içermez
- Görünüm korunmuş, güvenlik ve dayanıklılık artırılmıştır
"""

from __future__ import annotations

from pathlib import Path

from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput

from app.ui.dosya_secici_paketi.helpers import varsayilan_baslangic_klasoru
from app.ui.dosya_secici_paketi.models import DocumentSelection
from app.ui.icon_toolbar import IconToolbar
from app.ui.iconlu_baslik import IconluBaslik
from app.ui.tema import (
    CARD_BG,
    CARD_BG_DARK,
    CARD_BG_SOFT,
    INPUT_BG,
    RADIUS_MD,
    TEXT_MUTED,
    TEXT_PRIMARY,
)


class _SatirKart(BoxLayout):
    def __init__(self, bg=(0.16, 0.16, 0.18, 1), radius=14, **kwargs):
        super().__init__(**kwargs)
        from kivy.graphics import Color, RoundedRectangle

        with self.canvas.before:
            self._bg_color = Color(*tuple(bg))
            self._bg_rect = RoundedRectangle(radius=[dp(float(radius))])

        self.bind(pos=self._u, size=self._u)
        self._u()

    def _u(self, *_args):
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size


class DesktopPicker:
    def __init__(self, owner, on_selected):
        self.owner = owner
        self.on_selected = on_selected
        self.popup = None

    def _debug(self, message: str) -> None:
        try:
            self.owner._debug(f"[DESKTOP_PICKER] {message}")
        except Exception:
            try:
                print("[DESKTOP_PICKER]", str(message))
            except Exception:
                pass

    def _safe_path(self, value) -> Path:
        try:
            p = Path(value).expanduser()
            try:
                return p.resolve()
            except Exception:
                return p
        except Exception:
            return Path.cwd()

    def _initial_folder(self) -> Path:
        try:
            p = self._safe_path(varsayilan_baslangic_klasoru())
            if p.exists() and p.is_dir():
                return p
        except Exception:
            pass

        try:
            p = Path.cwd()
            if p.exists() and p.is_dir():
                return p
        except Exception:
            pass

        try:
            p = Path.home()
            if p.exists() and p.is_dir():
                return p
        except Exception:
            pass

        return Path(".")

    def _build_toolbar(self):
        toolbar = IconToolbar(spacing_dp=14, padding_dp=0)

        geri_btn = toolbar.add_tool(
            icon_name="arrow_back_geri.png",
            text="Yukarı",
            on_release=lambda *_: None,
            icon_size_dp=32,
            text_size="10sp",
            color=TEXT_MUTED,
            icon_bg=None,
        )
        ana_btn = toolbar.add_tool(
            icon_name="folder_open.png",
            text="Ana Depo",
            on_release=lambda *_: None,
            icon_size_dp=32,
            text_size="10sp",
            color=TEXT_MUTED,
            icon_bg=None,
        )
        yenile_btn = toolbar.add_tool(
            icon_name="refresh.png",
            text="Yenile",
            on_release=lambda *_: None,
            icon_size_dp=32,
            text_size="10sp",
            color=TEXT_MUTED,
            icon_bg=None,
        )
        kapat_btn = toolbar.add_tool(
            icon_name="cancel.png",
            text="Kapat",
            on_release=lambda *_: None,
            icon_size_dp=32,
            text_size="10sp",
            color=TEXT_MUTED,
            icon_bg=None,
        )
        return toolbar, geri_btn, ana_btn, yenile_btn, kapat_btn

    def _satir(self, liste, text, callback, renk):
        sarici = _SatirKart(
            orientation="vertical",
            size_hint_y=None,
            height=dp(56),
            bg=renk,
            radius=RADIUS_MD,
        )

        btn = Button(
            text=text,
            size_hint=(1, 1),
            halign="left",
            valign="middle",
            background_normal="",
            background_down="",
            background_color=(0, 0, 0, 0),
            color=TEXT_PRIMARY,
            font_size="13sp",
            shorten=True,
            shorten_from="right",
        )
        btn.bind(size=lambda inst, size: setattr(inst, "text_size", (size[0] - dp(20), size[1])))
        btn.bind(on_release=callback)

        sarici.add_widget(btn)
        liste.add_widget(sarici)

    def open_popup(self):
        if self.popup:
            try:
                self.popup.dismiss()
            except Exception:
                pass
            self.popup = None

        mevcut_klasor = self._initial_folder()

        try:
            alt_sinir = Path(mevcut_klasor.anchor) if mevcut_klasor.anchor else mevcut_klasor
        except Exception:
            alt_sinir = mevcut_klasor

        ana = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(8))

        ana.add_widget(
            IconluBaslik(
                text="Belge / Kod Dosyası Seç",
                icon_name="schema.png",
                height_dp=32,
                font_size="15sp",
                color=TEXT_PRIMARY,
            )
        )

        yol_input = TextInput(
            text="",
            multiline=False,
            readonly=True,
            size_hint_y=None,
            height=dp(44),
            background_normal="",
            background_active="",
            background_color=INPUT_BG,
            foreground_color=TEXT_PRIMARY,
            cursor_color=TEXT_PRIMARY,
            padding=(dp(10), dp(12)),
            font_size="13sp",
        )
        ana.add_widget(yol_input)

        bilgi_lbl = Label(
            text="Klasörler ve dosyalar listelenir. .py dosyaları önde gösterilir.",
            size_hint_y=None,
            height=dp(18),
            color=TEXT_MUTED,
            font_size="12sp",
            halign="left",
            valign="middle",
        )
        bilgi_lbl.bind(size=lambda inst, size: setattr(inst, "text_size", (size[0], None)))
        ana.add_widget(bilgi_lbl)

        ust_bar, geri_btn, ana_btn, yenile_btn, kapat_btn = self._build_toolbar()
        ana.add_widget(ust_bar)

        scroll = ScrollView(
            do_scroll_x=False,
            do_scroll_y=True,
            bar_width=dp(8),
            scroll_type=["bars", "content"],
        )
        liste = GridLayout(
            cols=1,
            spacing=dp(6),
            padding=(0, dp(4)),
            size_hint_y=None,
        )
        liste.bind(minimum_height=liste.setter("height"))
        scroll.add_widget(liste)
        ana.add_widget(scroll)

        popup = Popup(
            title="",
            content=ana,
            size_hint=(0.96, 0.96),
            auto_dismiss=False,
            separator_height=0,
        )
        popup.bind(on_dismiss=lambda *_: setattr(self, "popup", None))
        self.popup = popup

        def yol_yaz():
            try:
                yol_input.text = "Geçerli klasör: " + str(mevcut_klasor)
            except Exception:
                yol_input.text = "Geçerli klasör okunamadı"

        def listeyi_yenile(*_args):
            liste.clear_widgets()
            yol_yaz()

            try:
                klasorler = []
                py_dosyalar = []
                diger = []

                try:
                    ogeler = sorted(
                        mevcut_klasor.iterdir(),
                        key=lambda p: (not p.is_dir(), p.name.lower()),
                    )
                except Exception as exc:
                    self._satir(liste, "[Hata] " + str(exc), lambda *_: None, (0.30, 0.15, 0.15, 1))
                    return

                for oge in ogeler:
                    try:
                        if oge.is_dir():
                            klasorler.append(oge)
                        elif oge.is_file():
                            if str(oge.suffix or "").lower() == ".py":
                                py_dosyalar.append(oge)
                            else:
                                diger.append(oge)
                    except Exception:
                        pass

                for klasor in klasorler:
                    self._satir(
                        liste,
                        "[KLASOR]  " + klasor.name,
                        lambda _btn, p=klasor: klasore_gir(p),
                        CARD_BG,
                    )

                for dosya in py_dosyalar:
                    self._satir(
                        liste,
                        "[PY]  " + dosya.name,
                        lambda _btn, p=dosya: dosya_sec(p),
                        CARD_BG_SOFT,
                    )

                if not py_dosyalar:
                    for dosya in diger:
                        self._satir(
                            liste,
                            "[DOSYA]  " + dosya.name,
                            lambda _btn, p=dosya: dosya_sec(p),
                            CARD_BG_DARK,
                        )

                if not klasorler and not py_dosyalar and not diger:
                    self._satir(liste, "Bu klasörde dosya yok.", lambda *_: None, CARD_BG_DARK)

                try:
                    scroll.scroll_y = 1
                except Exception:
                    pass

            except Exception as exc:
                self._satir(liste, "[Hata] " + str(exc), lambda *_: None, (0.30, 0.15, 0.15, 1))

        def klasore_gir(klasor: Path):
            nonlocal mevcut_klasor
            try:
                hedef = self._safe_path(klasor)
                if hedef.exists() and hedef.is_dir():
                    mevcut_klasor = hedef
                    listeyi_yenile()
            except Exception as exc:
                self._debug(f"Klasöre giriş hatası: {exc}")

        def dosya_sec(dosya: Path):
            try:
                secili_path = self._safe_path(dosya)
                if not secili_path.exists() or not secili_path.is_file():
                    self._debug("Dosya artık bulunamadı")
                    return

                secili = str(secili_path)
                popup.dismiss()

                if self.on_selected:
                    self.on_selected(
                        DocumentSelection(
                            source="filesystem",
                            uri="",
                            local_path=secili,
                            display_name=secili_path.name,
                            mime_type="",
                        )
                    )
            except Exception as exc:
                self._debug(f"Dosya seçim hatası: {exc}")

        def yukari(*_args):
            nonlocal mevcut_klasor
            try:
                mevcut = self._safe_path(mevcut_klasor)

                if str(mevcut) == str(alt_sinir):
                    return

                ust = mevcut.parent
                if ust.exists() and ust.is_dir():
                    mevcut_klasor = self._safe_path(ust)
                    listeyi_yenile()
            except Exception as exc:
                self._debug(f"Yukarı çıkma hatası: {exc}")

        def ana_depoya_don(*_args):
            nonlocal mevcut_klasor
            try:
                mevcut_klasor = self._initial_folder()
                listeyi_yenile()
            except Exception as exc:
                self._debug(f"Ana depoya dönüş hatası: {exc}")

        geri_btn.bind(on_release=yukari)
        ana_btn.bind(on_release=ana_depoya_don)
        yenile_btn.bind(on_release=listeyi_yenile)
        kapat_btn.bind(on_release=lambda *_: popup.dismiss())

        listeyi_yenile()
        popup.open()