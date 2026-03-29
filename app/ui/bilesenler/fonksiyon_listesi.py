# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/bilesenler/fonksiyon_listesi.py

ROL:
- Fonksiyon öğelerini profesyonel liste paneli halinde sunar
- Arama, sayaç, seçili özet ve scroll liste içerir
- Dış callback ile fonksiyon seçimini iletir
- Büyük ekran / küçük ekran dengesini koruyarak okunabilir liste sunar
- Dil entegrasyonuna uyumludur

MİMARİ:
- UI bileşenidir
- Item verisini sadece gösterir ve filtreler
- Seçili item durumunu içeride yönetir
- Deterministik render akışı kullanır
- Geriye uyumluluk katmanı içermez
- Mevcut dil anahtar seti korunur
- Çözülmeyen anahtarlar için yalnızca yerel fallback metin kullanılır

SURUM: 4
TARIH: 2026-03-28
IMZA: FY.
"""

from __future__ import annotations

from typing import Any, Callable

from kivy.graphics import Color, Line, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput

from app.ui.bilesenler.fonksiyon_satiri import FonksiyonSatiri
from app.ui.ortak.renkler import (
    INPUT_ARKAPLAN,
    INPUT_IPUCU,
    KART_ALT,
    KENARLIK,
    METIN,
    METIN_SOLUK,
)


class FonksiyonListesi(BoxLayout):
    """
    Fonksiyonları arama ve detay özetli biçimde listeleyen panel.
    """

    __slots__ = (
        "_t",
        "_on_select",
        "_items",
        "_filtered_items",
        "_secili_item",
        "_satirlar",
        "_bg_rect",
        "_line_rect",
        "_baslik",
        "_sayac_label",
        "_ozet_label",
        "_arama_input",
        "_liste_container",
        "_bos_label",
    )

    def __init__(
        self,
        *,
        t: Callable[[str], str] | None = None,
        on_select: Callable[[Any], None] | None = None,
        **kwargs,
    ):
        kwargs.setdefault("orientation", "vertical")
        kwargs.setdefault("spacing", dp(12))
        kwargs.setdefault("padding", (dp(14), dp(14), dp(14), dp(14)))

        super().__init__(**kwargs)

        self._t = t or (lambda key, **_kwargs: key)
        self._on_select = on_select
        self._items: list[Any] = []
        self._filtered_items: list[Any] = []
        self._secili_item: Any | None = None
        self._satirlar: list[FonksiyonSatiri] = []

        with self.canvas.before:
            Color(*KART_ALT)
            self._bg_rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(22), dp(22), dp(22), dp(22)],
            )

        with self.canvas.after:
            Color(*KENARLIK)
            self._line_rect = Line(
                rounded_rectangle=(
                    self.x,
                    self.y,
                    self.width,
                    self.height,
                    dp(22),
                ),
                width=1.0,
            )

        self.bind(pos=self._yenile, size=self._yenile)

        self.add_widget(self._header_olustur())
        self.add_widget(self._arama_alani_olustur())
        self.add_widget(self._ozet_alani_olustur())
        self.add_widget(self._liste_alani_olustur())

        self._render()

    # =========================================================
    # YARDIMCI
    # =========================================================
    def _yenile(self, *_args) -> None:
        """
        Arka plan ve kenarlık çizimini günceller.
        """
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size
        self._line_rect.rounded_rectangle = (
            self.x,
            self.y,
            self.width,
            self.height,
            dp(22),
        )

    def _tr(self, key: str, fallback: str) -> str:
        """
        Dil anahtarını çözer; çözülmezse fallback döner.
        """
        text = self._t(key)
        if text == key:
            return fallback
        return str(text or fallback)

    @staticmethod
    def _item_attr(item: Any, *names: str, default=None):
        """
        Dict veya obje üzerinden güvenli alan okur.
        """
        for name in names:
            if isinstance(item, dict) and name in item:
                return item.get(name)
            if hasattr(item, name):
                return getattr(item, name)
        return default

    def _arama_ipucu_metni(self) -> str:
        """
        Arama alanı ipucu metnini çözer.
        """
        hint = self._t("function_search_hint")
        if hint == "function_search_hint":
            hint = self._t("search_functions")
        if hint == "search_functions":
            hint = "Fonksiyon ara..."
        return str(hint or "Fonksiyon ara...")

    def _bos_liste_metni(self) -> str:
        """
        Boş liste durum metnini çözer.
        """
        text = self._t("function_list_empty")
        if text == "function_list_empty":
            text = self._t("no_function_found")
        if text == "no_function_found":
            text = "Henüz fonksiyon bulunamadı\nDosya seçtikten sonra liste dolacaktır"
        return str(text or "")

    # =========================================================
    # HEADER
    # =========================================================
    def _header_olustur(self) -> BoxLayout:
        """
        Başlık ve sayaç bölümünü üretir.
        """
        root = BoxLayout(
            orientation="vertical",
            spacing=dp(6),
            size_hint_y=None,
            height=dp(56),
        )

        self._baslik = Label(
            text=self._tr("function_list_title", "Fonksiyon Listesi"),
            color=METIN,
            bold=True,
            font_size=dp(17),
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(26),
        )
        self._baslik.bind(
            size=lambda inst, _val: setattr(inst, "text_size", inst.size)
        )

        self._sayac_label = Label(
            text=self._tr("function_count_empty", "Fonksiyon yok"),
            color=METIN_SOLUK,
            font_size=dp(12),
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(20),
        )
        self._sayac_label.bind(
            size=lambda inst, _val: setattr(inst, "text_size", inst.size)
        )

        root.add_widget(self._baslik)
        root.add_widget(self._sayac_label)
        return root

    # =========================================================
    # ARAMA
    # =========================================================
    def _arama_alani_olustur(self) -> TextInput:
        """
        Arama alanını üretir.
        """
        self._arama_input = TextInput(
            multiline=False,
            size_hint_y=None,
            height=dp(46),
            hint_text=self._arama_ipucu_metni(),
            background_color=INPUT_ARKAPLAN,
            foreground_color=METIN,
            hint_text_color=INPUT_IPUCU,
            padding=(dp(14), dp(12), dp(14), dp(12)),
            font_size=dp(15),
        )
        self._arama_input.bind(text=lambda *_args: self._filtrele_ve_render())
        return self._arama_input

    # =========================================================
    # ÖZET
    # =========================================================
    def _ozet_alani_olustur(self) -> BoxLayout:
        """
        Seçili fonksiyon özet alanını üretir.
        """
        kutu = BoxLayout(
            orientation="vertical",
            spacing=dp(2),
            size_hint_y=None,
            height=dp(60),
            padding=(dp(12), dp(10), dp(12), dp(10)),
        )

        with kutu.canvas.before:
            Color(0.18, 0.20, 0.27, 1)
            kutu._bg = RoundedRectangle(  # type: ignore[attr-defined]
                pos=kutu.pos,
                size=kutu.size,
                radius=[dp(16), dp(16), dp(16), dp(16)],
            )

        kutu.bind(
            pos=lambda inst, _val: setattr(inst._bg, "pos", inst.pos),   # type: ignore[attr-defined]
            size=lambda inst, _val: setattr(inst._bg, "size", inst.size),  # type: ignore[attr-defined]
        )

        self._ozet_label = Label(
            text=self._tr("selected_function", "Seçili fonksiyon: -"),
            color=METIN_SOLUK,
            font_size=dp(12),
            halign="left",
            valign="middle",
        )
        self._ozet_label.bind(
            size=lambda inst, _val: setattr(inst, "text_size", inst.size)
        )

        kutu.add_widget(self._ozet_label)
        return kutu

    # =========================================================
    # LİSTE
    # =========================================================
    def _liste_alani_olustur(self) -> ScrollView:
        """
        Scroll destekli liste alanını üretir.
        """
        scroll = ScrollView()

        self._liste_container = BoxLayout(
            orientation="vertical",
            spacing=dp(10),
            size_hint_y=None,
            padding=(0, dp(4), 0, dp(12)),
        )
        self._liste_container.bind(
            minimum_height=lambda inst, val: setattr(inst, "height", val)
        )

        self._bos_label = Label(
            text=self._bos_liste_metni(),
            color=METIN_SOLUK,
            size_hint_y=None,
            height=dp(88),
            halign="center",
            valign="middle",
        )
        self._bos_label.bind(
            size=lambda inst, _val: setattr(inst, "text_size", inst.size)
        )

        scroll.add_widget(self._liste_container)
        return scroll

    # =========================================================
    # DATA
    # =========================================================
    def set_items(self, items: list[Any]) -> None:
        """
        Liste item'larını set eder ve render eder.
        """
        self._items = list(items or [])
        self._secili_item = None
        self._filtrele_ve_render()

    def clear_items(self) -> None:
        """
        Listeyi temizler ve başlangıç görünümüne döner.
        """
        self._items = []
        self._filtered_items = []
        self._secili_item = None

        if self._arama_input is not None:
            self._arama_input.text = ""

        self._render()

    def _filtrele_ve_render(self) -> None:
        """
        Arama metnine göre filtreler ve yeniden render eder.
        """
        q = str(self._arama_input.text or "").strip().lower()

        if not q:
            self._filtered_items = list(self._items)
        else:
            sonuc: list[Any] = []

            for item in self._items:
                name = str(
                    self._item_attr(item, "name", "ad", default="") or ""
                ).lower()
                kind = str(
                    self._item_attr(item, "kind", "type", "tur", default="") or ""
                ).lower()
                path = str(
                    self._item_attr(item, "path", default="") or ""
                ).lower()

                havuz = " ".join((name, kind, path))
                if q in havuz:
                    sonuc.append(item)

            self._filtered_items = sonuc

        self._render()

    # =========================================================
    # RENDER
    # =========================================================
    def _render(self) -> None:
        """
        UI durumunu item listesine göre yeniden üretir.
        """
        self._liste_container.clear_widgets()
        self._satirlar.clear()
        self._bos_label.text = self._bos_liste_metni()

        toplam = len(self._items)
        filtreli = len(self._filtered_items)

        if toplam == 0:
            self._baslik.text = self._tr("select_file_first", "Önce dosya seç")
            self._sayac_label.text = self._tr("no_function", "Fonksiyon yok")
        elif self._secili_item is None:
            self._baslik.text = self._tr("function_select_title", "Fonksiyon seç")
            kalip = self._t("function_count_all")
            if kalip == "function_count_all":
                kalip = "{count} fonksiyon bulundu"
            self._sayac_label.text = str(kalip).format(count=toplam)
        else:
            self._baslik.text = self._tr("function_selected_title", "Fonksiyon seçildi")

            if toplam == filtreli:
                kalip = self._t("function_count_all")
                if kalip == "function_count_all":
                    kalip = "{count} fonksiyon bulundu"
                self._sayac_label.text = str(kalip).format(count=toplam)
            else:
                kalip = self._t("function_count_filtered")
                if kalip == "function_count_filtered":
                    kalip = "{filtered} / {total} fonksiyon"
                self._sayac_label.text = str(kalip).format(
                    filtered=filtreli,
                    total=toplam,
                )

        self._ozet_guncelle()

        if not self._filtered_items:
            self._liste_container.add_widget(self._bos_label)
            return

        for item in self._filtered_items:
            satir = FonksiyonSatiri(
                item=item,
                on_select=self._satir_secildi,
                t=self._t,
            )
            satir.secili_yap(item is self._secili_item)
            satir.size_hint_y = None
            satir.height = dp(80)

            self._satirlar.append(satir)
            self._liste_container.add_widget(satir)

    # =========================================================
    # SELECTION
    # =========================================================
    def _ozet_guncelle(self) -> None:
        """
        Seçili fonksiyon özet metnini günceller.
        """
        if self._secili_item is None:
            self._ozet_label.text = self._tr(
                "selected_function",
                "Seçili fonksiyon: -",
            )
            return

        ad = str(
            self._item_attr(self._secili_item, "name", "ad", default="bilinmiyor")
            or "bilinmiyor"
        )
        start = self._item_attr(self._secili_item, "lineno", "satir", default="?")
        end = self._item_attr(self._secili_item, "end_lineno", "bitis_satiri", default="?")

        secildi = self._tr("selected_prefix", "Seçildi:")
        satir = self._tr("line", "Satır")

        self._ozet_label.text = f"{secildi} {ad}\n{satir}: {start}-{end}"

    def _satir_secildi(self, item: Any) -> None:
        """
        Satır seçimi sonrası iç state ve görünümü günceller.
        """
        self._secili_item = item

        for satir in self._satirlar:
            satir.secili_yap(satir._item is item)  # kontrollü iç kullanım

        self._ozet_guncelle()
        self._render()

        if callable(self._on_select):
            self._on_select(item)