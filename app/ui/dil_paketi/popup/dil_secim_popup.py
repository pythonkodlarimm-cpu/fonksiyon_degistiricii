# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/dil_paketi/popup/dil_secim_popup.py

ROL:
- Uygulama içi dil seçme popup'ını oluşturmak
- diller/ klasöründe otomatik algılanan dilleri listelemek
- Seçilen dili settings üzerinden kaydetmek
- Kapanış sonrası üst katmana callback ile bildirmek
- Mobil ekranda taşmayan ve okunabilir dil seçim görünümü sunmak
- Görünen metinleri aktif dil üzerinden üretmek

MİMARİ:
- UI burada tutulur
- Dil verisi ServicesYoneticisi üzerinden alınır
- Seçim sonrası settings.json güncellenir
- Üst katman isterse UI refresh tetikleyebilir
- Popup katmanı yöneticiden bağımsız sadece görünüm ve seçim işini yapar
- Satırlar tek tek tıklanabilir kart benzeri yapı ile üretilir
- Görünen sabit metinler mümkün olduğunca dil servisi üzerinden alınır
- services verilmezse güvenli fallback ile çalışır
- Sabit dil listesi kullanılmaz; diller klasörü otomatik taranır

API UYUMLULUK:
- Android API 35 uyumlu
- Android ve masaüstünde güvenli çalışır
- Platform bağımsızdır

SURUM: 4
TARIH: 2026-03-24
IMZA: FY.
"""

from __future__ import annotations

from typing import Callable

from kivy.metrics import dp
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView

from app.services.yoneticisi import ServicesYoneticisi
from app.ui.kart import Kart
from app.ui.tema import TEXT_MUTED, TEXT_PRIMARY


class DilSatiri(ButtonBehavior, Kart):
    def __init__(
        self,
        kod: str,
        yerel_ad: str,
        ad: str,
        secili: bool = False,
        aktif: bool = True,
        durum_metin: str = "",
        on_release_callback=None,
        **kwargs,
    ):
        bg = (0.15, 0.38, 0.24, 1) if secili else (0.14, 0.17, 0.22, 1)
        border = (0.20, 0.46, 0.30, 1) if secili else (0.20, 0.24, 0.30, 1)

        super().__init__(
            orientation="horizontal",
            spacing=dp(10),
            padding=(dp(12), dp(10), dp(12), dp(10)),
            size_hint_y=None,
            height=dp(58),
            bg=bg,
            border=border,
            radius=14,
            **kwargs,
        )

        self.kod = str(kod or "").strip()
        self.on_release_callback = on_release_callback

        sol = BoxLayout(
            orientation="vertical",
            spacing=dp(2),
        )

        ana_metin = yerel_ad if yerel_ad else self.kod
        alt_metin = ad if ad and ad != yerel_ad else self.kod

        self.baslik = Label(
            text=f"✓ {ana_metin}" if secili else ana_metin,
            color=(1, 1, 1, 1) if aktif else (0.76, 0.76, 0.80, 1),
            font_size="14sp",
            bold=secili,
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(22),
            shorten=True,
            shorten_from="right",
            max_lines=1,
        )
        self.baslik.bind(
            size=lambda inst, size: setattr(inst, "text_size", (size[0], None))
        )

        self.alt = Label(
            text=f"{alt_metin} • {self.kod}",
            color=(0.86, 0.92, 1, 1) if secili else TEXT_MUTED,
            font_size="11sp",
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(18),
            shorten=True,
            shorten_from="right",
            max_lines=1,
        )
        self.alt.bind(
            size=lambda inst, size: setattr(inst, "text_size", (size[0], None))
        )

        sol.add_widget(self.baslik)
        sol.add_widget(self.alt)

        sag = Label(
            text=str(durum_metin or ""),
            color=(0.90, 1.0, 0.92, 1) if secili else (0.72, 0.80, 0.92, 1),
            font_size="10sp",
            bold=secili,
            size_hint=(None, 1),
            width=dp(72),
            halign="right",
            valign="middle",
        )
        sag.bind(size=lambda inst, size: setattr(inst, "text_size", size))

        self.add_widget(sol)
        self.add_widget(sag)

    def on_press(self):
        try:
            if callable(self.on_release_callback):
                self.on_release_callback(self.kod)
        except Exception:
            pass


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
            kod = str(self.services.aktif_dil() or "").strip()
            if kod:
                return kod
        except Exception:
            pass

        try:
            return str(self.services.get_language(default="tr") or "tr").strip()
        except Exception:
            return "tr"

    def _varsayilan_dil_listesi(self) -> list[dict[str, str]]:
        return [
            {"code": "tr", "name": "Türkçe", "selected": "1"},
            {"code": "en", "name": "English", "selected": "0"},
            {"code": "de", "name": "Deutsch", "selected": "0"},
        ]

    def _diller(self) -> list[dict[str, str]]:
        try:
            liste = self.services.mevcut_dilleri_listele()
            if isinstance(liste, list) and liste:
                return liste
        except Exception:
            pass
        return self._varsayilan_dil_listesi()

    def _sirali_diller(self) -> list[dict[str, str]]:
        liste = list(self._diller() or [])
        aktif_dil = self._aktif_dil()

        def _sort_key(item: dict[str, str]):
            kod = str(item.get("code", "") or "").strip()
            ad = str(item.get("name", "") or kod).strip().lower()
            secili_oncelik = 0 if kod == aktif_dil else 1
            return (secili_oncelik, ad, kod)

        try:
            return sorted(liste, key=_sort_key)
        except Exception:
            return liste

    def _durum_metin(self, secili: bool, aktif: bool) -> str:
        if secili:
            return self._m("active", "AKTİF")
        if aktif:
            return self._m("available", "Açık")
        return self._m("not_ready", "Hazır değil")

    # =========================================================
    # ROW
    # =========================================================
    def _build_row(
        self,
        bilgi: dict[str, str],
        aktif_dil: str,
    ) -> DilSatiri:
        kod = str(bilgi.get("code", "") or "").strip()
        yerel_ad = str(bilgi.get("name", "") or kod).strip() or kod
        ad = yerel_ad
        secili = kod == aktif_dil
        aktif = True

        return DilSatiri(
            kod=kod,
            yerel_ad=yerel_ad,
            ad=ad,
            secili=secili,
            aktif=aktif,
            durum_metin=self._durum_metin(secili, aktif),
            on_release_callback=self._select_language,
        )

    # =========================================================
    # ACTION
    # =========================================================
    def _select_language(self, kod: str) -> None:
        temiz = str(kod or "").strip()
        if not temiz:
            return

        ok = False

        try:
            ok = bool(self.services.dil_degistir(temiz))
        except Exception:
            ok = False

        if not ok:
            try:
                self.services.set_language(temiz)
                ok = True
            except Exception:
                ok = False

        if not ok:
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
        try:
            self.services.dilleri_yeniden_tara()
        except Exception:
            pass

        try:
            self.services.aktif_dili_ayardan_yukle(default="tr")
        except Exception:
            pass

        aktif_dil = self._aktif_dil()

        govde = BoxLayout(
            orientation="vertical",
            spacing=dp(10),
            padding=(dp(10), dp(10), dp(10), dp(10)),
        )

        kart = Kart(
            orientation="vertical",
            spacing=dp(10),
            padding=(dp(14), dp(14), dp(14), dp(14)),
            bg=(0.08, 0.11, 0.16, 1),
            border=(0.18, 0.21, 0.27, 1),
            radius=20,
        )

        baslik = Label(
            text=self._m("select_language", "Dil Seç"),
            size_hint_y=None,
            height=dp(34),
            font_size="20sp",
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
            height=dp(20),
            font_size="12sp",
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
            size_hint=(1, 1),
        )

        liste = BoxLayout(
            orientation="vertical",
            spacing=dp(8),
            size_hint_y=None,
            padding=(0, dp(4), 0, dp(4)),
        )
        liste.bind(minimum_height=liste.setter("height"))

        for bilgi in self._sirali_diller():
            liste.add_widget(self._build_row(bilgi, aktif_dil))

        scroll.add_widget(liste)
        kart.add_widget(scroll)

        alt_butonlar = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(48),
            spacing=dp(8),
        )

        kapat_btn = Button(
            text=self._m("close", "Kapat"),
            background_normal="",
            background_down="",
            background_color=(0.24, 0.28, 0.38, 1),
            color=(1, 1, 1, 1),
            font_size="14sp",
        )
        alt_butonlar.add_widget(kapat_btn)
        kart.add_widget(alt_butonlar)

        govde.add_widget(kart)

        self._popup = Popup(
            title="",
            content=govde,
            size_hint=(0.90, 0.86),
            auto_dismiss=True,
            separator_height=0,
        )

        kapat_btn.bind(on_release=lambda *_: self._popup.dismiss())
        self._popup.open()
        return self._popup


def open_dil_secim_popup(
    services: ServicesYoneticisi | None = None,
    on_language_changed: Callable[[str], None] | None = None,
) -> Popup:
    return DilSecimPopup(
        services=services,
        on_language_changed=on_language_changed,
    ).open()
