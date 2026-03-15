# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/dosya_secici_paketi/desktop_picker.py

ROL:
- Uygulama içi özel dosya seçici motoru
- Android ve masaüstünde aynı popup tabanlı gezinme akışını sağlar
- Klasörleri ve dosyaları listeler
- Python dosyalarını öncelikli gösterir
- Gerekirse diğer dosyaları da gösterir
- Seçilen dosyayı üst katmana bildirir

NOT:
- Bu dosya adı teknik nedenlerle desktop_picker olarak korunmuştur
- Ancak artık sadece masaüstü için değil, tüm platformlar için kullanılır
- Güvenli Klasör gibi ortamlarda uzantıya aşırı bağımlı olunmaz

SURUM: 6
TARIH: 2026-03-15
IMZA: FY.
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
from app.ui.dosya_secici_paketi.helpers import varsayilan_baslangic_klasoru
from app.ui.dosya_secici_paketi.models import PickerSelection


class _SatirKart(BoxLayout):
    def __init__(self, bg=(0.16, 0.16, 0.18, 1), radius=14, **kwargs):
        super().__init__(**kwargs)
        from kivy.graphics import Color, RoundedRectangle

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


class DesktopPicker:
    def __init__(self, owner, on_selected):
        self.owner = owner
        self.on_selected = on_selected
        self.popup = None

    def _debug(self, message: str) -> None:
        try:
            self.owner._debug(message)
        except Exception:
            pass

    def _aday_baslangic_klasorleri(self) -> list[Path]:
        adaylar = [
            Path("/storage/emulated/0"),
            Path("/sdcard"),
            varsayilan_baslangic_klasoru(),
            Path.cwd(),
        ]

        temiz = []
        gorulen = set()

        for aday in adaylar:
            try:
                cozulmus = aday.resolve() if aday.exists() else aday
                anahtar = str(cozulmus)
                if anahtar not in gorulen:
                    temiz.append(cozulmus)
                    gorulen.add(anahtar)
            except Exception:
                try:
                    anahtar = str(aday)
                    if anahtar not in gorulen:
                        temiz.append(aday)
                        gorulen.add(anahtar)
                except Exception:
                    pass

        return temiz

    def _baslangic_klasoru_sec(self) -> Path:
        for aday in self._aday_baslangic_klasorleri():
            try:
                if aday.exists() and aday.is_dir():
                    self._debug(f"Başlangıç klasörü: {aday}")
                    return aday
            except Exception:
                pass

        fallback = Path.cwd().resolve()
        self._debug(f"Fallback başlangıç klasörü: {fallback}")
        return fallback

    def _alt_sinir_bul(self, mevcut_klasor: Path) -> Path:
        adaylar = [
            Path("/storage/emulated/0"),
            Path("/sdcard"),
        ]

        for aday in adaylar:
            try:
                if aday.exists() and aday.is_dir():
                    return aday.resolve()
            except Exception:
                pass

        try:
            return Path(mevcut_klasor.anchor) if mevcut_klasor.anchor else mevcut_klasor
        except Exception:
            return mevcut_klasor

    def _dosya_turu_etiketi(self, dosya: Path) -> str:
        try:
            suffix = str(dosya.suffix or "").lower()
        except Exception:
            suffix = ""

        if suffix == ".py":
            return "[PY]"
        if suffix:
            return f"[DOSYA {suffix}]"
        return "[DOSYA]"

    def _build_popup_toolbar(self):
        toolbar = IconToolbar(
            spacing_dp=14,
            padding_dp=0,
        )

        geri_btn = toolbar.add_tool(
            icon_name="arrow_back_geri.png",
            text="Yukarı",
            on_release=lambda *_: None,
            icon_size_dp=32,
            text_size="10sp",
            color=TEXT_MUTED,
            icon_bg=None,
        )

        ana_depo_btn = toolbar.add_tool(
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

        return toolbar, geri_btn, ana_depo_btn, yenile_btn, kapat_btn

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

    def open_popup(self) -> None:
        if self.popup:
            try:
                self.popup.dismiss()
            except Exception:
                pass
            self.popup = None

        mevcut_klasor = self._baslangic_klasoru_sec()
        alt_sinir = self._alt_sinir_bul(mevcut_klasor)

        ana = BoxLayout(
            orientation="vertical",
            spacing=dp(8),
            padding=dp(8),
        )

        ust_baslik = IconluBaslik(
            text="Python Dosyası Seç",
            icon_name="schema.png",
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
            text="Klasörler ve dosyalar listelenir. .py dosyaları önceliklidir.",
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

        ust_bar, geri_btn, ana_depo_btn, yenile_btn, kapat_btn = self._build_popup_toolbar()
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
                py_dosyalari = []
                diger_dosyalar = []
                hata_sayisi = 0

                for oge in sorted(
                    mevcut_klasor.iterdir(),
                    key=lambda p: (not p.is_dir(), p.name.lower()),
                ):
                    try:
                        if oge.is_dir():
                            klasorler.append(oge)
                        elif oge.is_file():
                            suffix = str(oge.suffix or "").lower()
                            if suffix == ".py":
                                py_dosyalari.append(oge)
                            else:
                                diger_dosyalar.append(oge)
                    except Exception as exc:
                        hata_sayisi += 1
                        self._debug(f"Oge okunamadı: {oge} | {exc}")

                for klasor in klasorler:
                    self._popup_satiri_ekle(
                        liste,
                        "[KLASOR]  " + klasor.name,
                        lambda _btn, p=klasor: klasore_gir(p),
                        CARD_BG,
                    )

                for dosya in py_dosyalari:
                    self._popup_satiri_ekle(
                        liste,
                        "[PY]  " + dosya.name,
                        lambda _btn, p=dosya: dosya_sec(p),
                        CARD_BG_SOFT,
                    )

                if not py_dosyalari and diger_dosyalar:
                    for dosya in diger_dosyalar:
                        etiket = self._dosya_turu_etiketi(dosya)
                        self._popup_satiri_ekle(
                            liste,
                            f"{etiket}  {dosya.name}",
                            lambda _btn, p=dosya: dosya_sec(p),
                            CARD_BG_DARK,
                        )

                if not klasorler and not py_dosyalari and not diger_dosyalar:
                    self._popup_satiri_ekle(
                        liste,
                        "Bu klasörde gösterilebilir dosya yok.",
                        lambda *_: None,
                        CARD_BG_DARK,
                    )

                if hata_sayisi > 0:
                    self._debug(f"Listeleme sırasında {hata_sayisi} öğe atlandı")

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
                    self._debug(f"Klasöre girildi: {mevcut_klasor}")
                    listeyi_yenile()
            except Exception as exc:
                self._debug(f"Klasöre giriş hatası: {exc}")

        def dosya_sec(dosya: Path):
            try:
                secili = str(dosya.resolve())
                self._debug(f"Dosya seçildi: {secili}")
                popup.dismiss()
                self.on_selected(
                    PickerSelection(
                        path=secili,
                        display_name=dosya.name,
                        source="internal_picker",
                    )
                )
            except Exception as exc:
                self._debug(f"Dosya seçim hatası: {exc}")

        def yukari_cik(*_args):
            nonlocal mevcut_klasor
            try:
                mevcut = mevcut_klasor.resolve()

                if str(mevcut) == str(alt_sinir):
                    self._debug("Alt sınıra gelindi, daha yukarı çıkılmadı")
                    return

                ust = mevcut.parent
                if ust.exists() and ust.is_dir():
                    mevcut_klasor = ust.resolve()
                    self._debug(f"Yukarı çıkıldı: {mevcut_klasor}")
                    listeyi_yenile()
            except Exception as exc:
                self._debug(f"Yukarı çıkma hatası: {exc}")

        def ana_depoya_don(*_args):
            nonlocal mevcut_klasor
            try:
                mevcut_klasor = self._baslangic_klasoru_sec()
                self._debug(f"Ana depoya dönüldü: {mevcut_klasor}")
                listeyi_yenile()
            except Exception as exc:
                self._debug(f"Ana depoya dönüş hatası: {exc}")

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
