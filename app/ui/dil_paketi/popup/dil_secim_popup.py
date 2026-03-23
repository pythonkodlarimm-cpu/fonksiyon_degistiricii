# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/dil_paketi/popup/dil_secim_popup.py

ROL:
- Uygulama içi dil seçme popup'ını oluşturmak
- Desteklenen dilleri listelemek
- Seçilen dili settings üzerinden kaydetmek
- Kapanış sonrası üst katmana callback ile bildirmek

MİMARİ:
- UI burada tutulur
- Dil verisi ServicesYoneticisi üzerinden alınır
- Seçim sonrası settings.json güncellenir
- Üst katman isterse UI refresh tetikleyebilir
- Popup katmanı yöneticiden bağımsız sadece görünüm ve seçim işini yapar

API UYUMLULUK:
- Android API 35 uyumlu
- Android ve masaüstünde güvenli çalışır
- Platform bağımsızdır

SURUM: 1
TARIH: 2026-03-23
IMZA: FY.
"""

from __future__ import annotations

from typing import Callable

from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView

from app.services.yoneticisi import ServicesYoneticisi
from app.ui.kart import Kart
from app.ui.tema import TEXT_MUTED, TEXT_PRIMARY


class DilSecimPopup:
    def __init__(
        self,
        services: ServicesYoneticisi | None = None,
        on_language_changed: Callable[[str], None] | None = None,
    ):
        self.services = services or ServicesYoneticisi()
        self.on_language_changed = on_language_changed
        self._popup: Popup | None = None

    # =========================================================
    # HELPERS
    # =========================================================
    def _m(self, anahtar: str, default: str = "") -> str:
        try:
            return str(self.services.metin(anahtar, default) or default or anahtar)
        except Exception:
            return str(default or anahtar)

    def _aktif_dil(self) -> str:
        try:
            return str(self.services.aktif_dil() or "tr").strip()
        except Exception:
            return "tr"

    def _diller(self) -> dict[str, dict[str, object]]:
        try:
            return self.services.desteklenen_diller(sadece_aktifler=False)
        except Exception:
            return {
                "tr": {"ad": "Türkçe", "yerel_ad": "Türkçe", "aktif": True},
                "en": {"ad": "İngilizce", "yerel_ad": "English", "aktif": True},
                "de": {"ad": "Almanca", "yerel_ad": "Deutsch", "aktif": True},
            }

    def _sirali_diller(self) -> list[tuple[str, dict[str, object]]]:
        veriler = self._diller()
        aktifler: list[tuple[str, dict[str, object]]] = []
        digerleri: list[tuple[str, dict[str, object]]] = []

        for kod, bilgi in veriler.items():
            try:
                if bool(bilgi.get("aktif", False)):
                    aktifler.append((kod, bilgi))
                else:
                    digerleri.append((kod, bilgi))
            except Exception:
                digerleri.append((kod, bilgi))

        aktifler.sort(
            key=lambda item: str(item[1].get("yerel_ad") or item[0]).lower()
        )
        digerleri.sort(
            key=lambda item: str(item[1].get("yerel_ad") or item[0]).lower()
        )
        return aktifler + digerleri

    # =========================================================
    # ROW
    # =========================================================
    def _build_row(
        self,
        kod: str,
        bilgi: dict[str, object],
        aktif_dil: str,
    ) -> Button:
        yerel_ad = str(bilgi.get("yerel_ad") or kod)
        ad = str(bilgi.get("ad") or yerel_ad)
        secili = str(kod or "").strip() == str(aktif_dil or "").strip()

        text = yerel_ad if yerel_ad == ad else f"{yerel_ad} • {ad}"
        if secili:
            text = f"✓ {text}"

        buton = Button(
            text=text,
            size_hint_y=None,
            height=dp(46),
            halign="left",
            valign="middle",
            text_size=(dp(520), None),
            background_normal="",
            background_down="",
            background_color=(
                (0.14, 0.34, 0.22, 1) if secili else (0.14, 0.17, 0.22, 1)
            ),
            color=(1, 1, 1, 1),
            font_size="13sp",
        )

        buton.bind(on_release=lambda *_: self._select_language(kod))
        return buton

    # =========================================================
    # ACTION
    # =========================================================
    def _select_language(self, kod: str) -> None:
        temiz = str(kod or "").strip()
        if not temiz:
            return

        try:
            self.services.set_language(temiz)
        except Exception:
            return

        try:
            if callable(self.on_language_changed):
                self.on_language_changed(temiz)
        except Exception:
            pass

        try:
            if self._popup is not None:
                self._popup.dismiss()
        except Exception:
            pass

    # =========================================================
    # PUBLIC
    # =========================================================
    def open(self) -> Popup:
        aktif_dil = self._aktif_dil()

        govde = BoxLayout(
            orientation="vertical",
            spacing=dp(10),
            padding=(dp(12), dp(12), dp(12), dp(12)),
        )

        kart = Kart(
            orientation="vertical",
            spacing=dp(10),
            padding=(dp(12), dp(12), dp(12), dp(12)),
            bg=(0.08, 0.11, 0.16, 1),
            border=(0.18, 0.21, 0.27, 1),
            radius=18,
        )

        baslik = Label(
            text=self._m("select_language", "Dil Seç"),
            size_hint_y=None,
            height=dp(30),
            font_size="18sp",
            bold=True,
            color=TEXT_PRIMARY,
            halign="center",
            valign="middle",
        )
        baslik.bind(size=lambda inst, size: setattr(inst, "text_size", size))
        kart.add_widget(baslik)

        alt = Label(
            text=self._m("language", "Dil"),
            size_hint_y=None,
            height=dp(18),
            font_size="11sp",
            color=TEXT_MUTED,
            halign="center",
            valign="middle",
        )
        alt.bind(size=lambda inst, size: setattr(inst, "text_size", size))
        kart.add_widget(alt)

        scroll = ScrollView(
            do_scroll_x=False,
            do_scroll_y=True,
            bar_width=dp(8),
        )

        liste = BoxLayout(
            orientation="vertical",
            spacing=dp(8),
            size_hint_y=None,
        )
        liste.bind(minimum_height=liste.setter("height"))

        for kod, bilgi in self._sirali_diller():
            liste.add_widget(self._build_row(kod, bilgi, aktif_dil))

        scroll.add_widget(liste)
        kart.add_widget(scroll)

        alt_butonlar = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(44),
            spacing=dp(8),
        )

        kapat_btn = Button(
            text="Kapat",
            background_normal="",
            background_down="",
            background_color=(0.22, 0.24, 0.30, 1),
            color=(1, 1, 1, 1),
        )
        alt_butonlar.add_widget(kapat_btn)
        kart.add_widget(alt_butonlar)

        govde.add_widget(kart)

        self._popup = Popup(
            title="",
            content=govde,
            size_hint=(0.92, 0.84),
            auto_dismiss=True,
            separator_height=0,
        )

        kapat_btn.bind(on_release=lambda *_: self._popup.dismiss())
        self._popup.open()
        return self._popup