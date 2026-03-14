# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/dosya_secici.py
ROL:
- Python dosyası seçme alanı
- Seçilen dosyayı tarama / yenileme akışını başlatma
- Mobil uyumlu özel dosya seçim popup'ı sağlama

MİMARİ:
- Kendi görünümünü kendi çizer
- Root sadece callback verir
- Dosya seçimi, popup ve araç satırı burada yönetilir

SURUM: 2
"""

from __future__ import annotations

from pathlib import Path

from kivy.graphics import Color
from kivy.graphics import RoundedRectangle
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput

from app.ui.iconlu_baslik import IconluBaslik
from app.ui.iconlu_buton import IconluButon
from app.ui.tema import (
    ACCENT,
    CARD_BG,
    CARD_BG_DARK,
    CARD_BG_SOFT,
    DANGER,
    INPUT_BG,
    RADIUS_MD,
    SUCCESS,
    TEXT_MUTED,
    TEXT_PRIMARY,
)


def _varsayilan_baslangic_klasoru() -> Path:
    adaylar = [
        Path("/storage/emulated/0"),
        Path("/sdcard"),
        Path.cwd(),
    ]

    for aday in adaylar:
        try:
            if aday.exists() and aday.is_dir():
                return aday.resolve()
        except Exception:
            pass

    return Path.cwd().resolve()


class _SatirKart(BoxLayout):
    def __init__(self, bg=(0.16, 0.16, 0.18, 1), radius=14, **kwargs):
        super().__init__(**kwargs)
        self._bg = tuple(bg)
        self._radius = float(radius)

        with self.canvas.before:
            self._bg_color = Color(*self._bg)
            self._bg_rect = RoundedRectangle(radius=[dp(self._radius)])

        self.bind(pos=self._update_canvas, size=self._update_canvas)
        self._update_canvas()

    def _update_canvas(self, *_args):
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size


class DosyaSecici(BoxLayout):
    """
    Dosya seçme ve tarama paneli.

    Özellikler:
    - seçili dosya yolunu gösterir
    - dosya popup'ı ile klasör içinde gezinir
    - .py dosyalarını filtreler
    - tara / yenile akışını dış callback'lere devreder
    """

    def __init__(self, on_scan, on_refresh=None, **kwargs):
        super().__init__(
            orientation="vertical",
            size_hint_y=None,
            height=dp(140),
            spacing=dp(8),
            **kwargs,
        )

        self.on_scan = on_scan
        self.on_refresh = on_refresh
        self.popup = None

        self._build_ui()

    # =========================================================
    # UI
    # =========================================================
    def _build_ui(self) -> None:
        self._build_header()
        self._build_path_box()
        self._build_action_row()

    def _build_header(self) -> None:
        self.header = IconluBaslik(
            text="Dosya Seçimi",
            icon_name="folder_open.png",
            height_dp=30,
            font_size="15sp",
            color=TEXT_PRIMARY,
        )
        self.add_widget(self.header)

    def _build_path_box(self) -> None:
        self.path_input = TextInput(
            hint_text="Python dosyası seç...",
            multiline=False,
            readonly=True,
            size_hint_y=None,
            height=dp(46),
            background_normal="",
            background_active="",
            background_color=INPUT_BG,
            foreground_color=TEXT_PRIMARY,
            cursor_color=TEXT_PRIMARY,
            padding=(dp(12), dp(12)),
            font_size="14sp",
        )
        self.add_widget(self.path_input)

        self.path_hint = Label(
            text="Seçilen dosya burada görünecek",
            size_hint_y=None,
            height=dp(16),
            color=TEXT_MUTED,
            font_size="12sp",
            halign="left",
            valign="middle",
            shorten=True,
            shorten_from="right",
        )
        self.path_hint.bind(
            size=lambda inst, size: setattr(inst, "text_size", (size[0], None))
        )
        self.add_widget(self.path_hint)

    def _build_action_row(self) -> None:
        row = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(52),
            spacing=dp(8),
        )

        self.choose_button = IconluButon(
            text="Dosya Seç",
            icon_name="folder_open.png",
            bg=CARD_BG,
            size_hint_x=0.34,
            icon_width_dp=20,
            height_dp=52,
        )
        self.choose_button.bind(on_release=self._open_popup)
        row.add_widget(self.choose_button)

        self.scan_button = IconluButon(
            text="Tara",
            icon_name="search.png",
            bg=ACCENT,
            size_hint_x=0.33,
            icon_width_dp=20,
            height_dp=52,
        )
        self.scan_button.bind(on_release=self._handle_scan)
        row.add_widget(self.scan_button)

        self.refresh_button = IconluButon(
            text="Yenile",
            icon_name="refresh.png",
            bg=CARD_BG_SOFT,
            size_hint_x=0.33,
            icon_width_dp=20,
            height_dp=52,
        )
        self.refresh_button.bind(on_release=self._handle_refresh)
        row.add_widget(self.refresh_button)

        self.add_widget(row)

    # =========================================================
    # PUBLIC API
    # =========================================================
    def get_path(self) -> str:
        return self.path_input.text.strip()

    def set_path(self, value: str) -> None:
        temiz = str(value or "").strip()
        self.path_input.text = temiz
        self.path_hint.text = temiz if temiz else "Seçilen dosya burada görünecek"

    # =========================================================
    # ACTIONS
    # =========================================================
    def _handle_scan(self, *_args):
        yol = self.get_path()
        if self.on_scan:
            self.on_scan(yol)

    def _handle_refresh(self, *_args):
        yol = self.get_path()
        if self.on_refresh:
            self.on_refresh(yol)
        elif self.on_scan:
            self.on_scan(yol)

    # =========================================================
    # POPUP HELPERS
    # =========================================================
    def _build_popup_button_row(self):
        ust_bar = GridLayout(
            cols=2,
            size_hint_y=None,
            height=dp(112),
            spacing=dp(8),
        )

        geri_btn = IconluButon(
            text="Yukarı",
            icon_name="arrow_back_geri.png",
            bg=CARD_BG,
            height_dp=52,
        )
        ust_bar.add_widget(geri_btn)

        ana_depo_btn = IconluButon(
            text="Ana Depo",
            icon_name="folder_open.png",
            bg=ACCENT,
            height_dp=52,
        )
        ust_bar.add_widget(ana_depo_btn)

        yenile_btn = IconluButon(
            text="Yenile",
            icon_name="refresh.png",
            bg=SUCCESS,
            height_dp=52,
        )
        ust_bar.add_widget(yenile_btn)

        kapat_btn = IconluButon(
            text="Kapat",
            icon_name="cancel.png",
            bg=DANGER,
            height_dp=52,
        )
        ust_bar.add_widget(kapat_btn)

        return ust_bar, geri_btn, ana_depo_btn, yenile_btn, kapat_btn

    def _popup_satiri_ekle(self, liste, text, callback, renk):
        sarici = _SatirKart(
            orientation="vertical",
            size_hint_y=None,
            height=dp(56),
            padding=(0, 0),
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
            bold=False,
            font_size="13sp",
            shorten=True,
            shorten_from="right",
        )
        btn.bind(
            size=lambda inst, size: setattr(
                inst,
                "text_size",
                (size[0] - dp(20), size[1]),
            )
        )
        btn.bind(on_release=callback)

        sarici.add_widget(btn)
        liste.add_widget(sarici)

    # =========================================================
    # POPUP
    # =========================================================
    def _open_popup(self, *_args):
        if self.popup:
            try:
                self.popup.dismiss()
            except Exception:
                pass
            self.popup = None

        mevcut_klasor = _varsayilan_baslangic_klasoru()
        alt_sinir = Path("/storage/emulated/0")

        ana = BoxLayout(
            orientation="vertical",
            spacing=dp(8),
            padding=dp(8),
        )

        ust_baslik = IconluBaslik(
            text="Python Dosyası Seç",
            icon_name="folder_open.png",
            height_dp=32,
            font_size="15sp",
            color=TEXT_PRIMARY,
        )
        ana.add_widget(ust_baslik)

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
            text=".py dosyaları listelenir",
            size_hint_y=None,
            height=dp(18),
            color=TEXT_MUTED,
            font_size="12sp",
            halign="left",
            valign="middle",
        )
        bilgi_lbl.bind(
            size=lambda inst, size: setattr(inst, "text_size", (size[0], None))
        )
        ana.add_widget(bilgi_lbl)

        ust_bar, geri_btn, ana_depo_btn, yenile_btn, kapat_btn = self._build_popup_button_row()
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

        def _popup_kapaninca(*_args):
            self.popup = None

        popup.bind(on_dismiss=_popup_kapaninca)
        self.popup = popup

        def yol_yaz():
            yol_input.text = "Geçerli klasör: " + str(mevcut_klasor)

        def listeyi_yenile(*_args):
            liste.clear_widgets()
            yol_yaz()

            try:
                klasorler = []
                dosyalar = []

                for oge in sorted(
                    mevcut_klasor.iterdir(),
                    key=lambda p: (not p.is_dir(), p.name.lower()),
                ):
                    if oge.is_dir():
                        klasorler.append(oge)
                    elif oge.is_file() and oge.suffix.lower() == ".py":
                        dosyalar.append(oge)

                for klasor in klasorler:
                    self._popup_satiri_ekle(
                        liste,
                        "[KLASOR]  " + klasor.name,
                        lambda _btn, p=klasor: klasore_gir(p),
                        CARD_BG,
                    )

                for dosya in dosyalar:
                    self._popup_satiri_ekle(
                        liste,
                        "[PY]  " + dosya.name,
                        lambda _btn, p=dosya: dosya_sec(p),
                        CARD_BG_SOFT,
                    )

                if not klasorler and not dosyalar:
                    self._popup_satiri_ekle(
                        liste,
                        "Bu klasörde Python dosyası yok.",
                        lambda *_: None,
                        CARD_BG_DARK,
                    )

            except Exception as exc:
                self._popup_satiri_ekle(
                    liste,
                    "[Hata] " + str(exc),
                    lambda *_: None,
                    (0.30, 0.15, 0.15, 1),
                )

            try:
                scroll.scroll_y = 1
            except Exception:
                pass

        def klasore_gir(klasor: Path):
            nonlocal mevcut_klasor
            try:
                if klasor.exists() and klasor.is_dir():
                    mevcut_klasor = klasor.resolve()
                    listeyi_yenile()
            except Exception:
                pass

        def dosya_sec(dosya: Path):
            try:
                secili = str(dosya.resolve())
                self.set_path(secili)
                popup.dismiss()
            except Exception:
                pass

        def yukari_cik(*_args):
            nonlocal mevcut_klasor
            try:
                mevcut = mevcut_klasor.resolve()
                sinir = alt_sinir.resolve() if alt_sinir.exists() else alt_sinir

                if str(mevcut) == str(sinir):
                    return

                ust = mevcut.parent
                if ust.exists() and ust.is_dir():
                    mevcut_klasor = ust.resolve()
                    listeyi_yenile()
            except Exception:
                pass

        def ana_depoya_don(*_args):
            nonlocal mevcut_klasor
            try:
                mevcut_klasor = _varsayilan_baslangic_klasoru()
                listeyi_yenile()
            except Exception:
                pass

        def kapat_popup(*_args):
            try:
                popup.dismiss()
            except Exception:
                self.popup = None

        geri_btn.bind(on_release=yukari_cik)
        ana_depo_btn.bind(on_release=ana_depoya_don)
        yenile_btn.bind(on_release=listeyi_yenile)
        kapat_btn.bind(on_release=kapat_popup)

        listeyi_yenile()
        popup.open()