# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/popup/islemler_popup.py

ROL:
- Üst toolbar menü ikonundan açılan işlemler popup'ını sağlar
- Ana motor ve yardımcı aksiyonları kullanıcıya sade biçimde sunar
- Fonksiyon Değiştir, Parça Değiştir, Enjeksiyon, Dil, Yedekler ve Ayarlar
  seçeneklerini callback ile dışarı verir
- Developer mode aktif ise geliştirici ayarları seçeneğini de gösterebilir
- UI tarafında tekrar kullanılabilir işlemler menüsü sunar
- Dil entegrasyonuna uyumludur

MİMARİ:
- UI katmanıdır
- Servis katmanını bilmez
- Aksiyon callback'leri dışarıdan enjekte edilir
- Ortak ikon, renk ve boyut sistemine uyar
- Geriye uyumluluk katmanı içermez
- Mevcut dil anahtar seti korunur
- Deterministik ve sade popup üretimi hedeflenir

SURUM: 4
TARIH: 2026-03-28
IMZA: FY.
"""

from __future__ import annotations

from typing import Callable, Final

from kivy.graphics import Color, Line, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView

from app.ui.ortak.ikonlar import ikon_yolu
from app.ui.ortak.renkler import (
    AYIRICI,
    BUTON,
    KART,
    METIN,
    METIN_SOLUK,
)

_SATIR_YUKSEKLIGI: Final[float] = dp(74)
_SATIR_RADIUS: Final[float] = dp(18)
_POPUP_RADIUS: Final[float] = dp(22)
_IKON_BOYUTU: Final[float] = dp(28)


def _label_tek_satir(
    *,
    text: str,
    color,
    font_size,
    height,
    bold: bool = False,
) -> Label:
    """
    Tek satırlık standart label üretir.
    """
    widget = Label(
        text=str(text or ""),
        color=color,
        bold=bold,
        font_size=font_size,
        halign="left",
        valign="middle",
        size_hint_y=None,
        height=height,
        shorten=True,
        shorten_from="right",
    )
    widget.bind(size=lambda inst, _val: setattr(inst, "text_size", inst.size))
    return widget


def _label_merkez(
    *,
    text: str,
    color,
    font_size,
    width,
    bold: bool = False,
) -> Label:
    """
    Ortalanmış kısa label üretir.
    """
    widget = Label(
        text=str(text or ""),
        color=color,
        bold=bold,
        font_size=font_size,
        size_hint=(None, 1),
        width=width,
        halign="center",
        valign="middle",
    )
    widget.bind(size=lambda inst, _val: setattr(inst, "text_size", inst.size))
    return widget


class _MenuSatiri(ButtonBehavior, BoxLayout):
    """
    İşlemler popup içindeki tek satır menü öğesi.
    """

    __slots__ = (
        "_callback",
        "_bg_rect",
        "_line_rect",
        "_title_label",
        "_desc_label",
    )

    def __init__(
        self,
        *,
        icon_name: str,
        title: str,
        description: str,
        on_press_callback: Callable[[], None] | None = None,
        fallback_text: str = "?",
        **kwargs,
    ):
        kwargs.setdefault("orientation", "horizontal")
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height", _SATIR_YUKSEKLIGI)
        kwargs.setdefault("spacing", dp(10))
        kwargs.setdefault("padding", (dp(12), dp(10), dp(12), dp(10)))

        super().__init__(**kwargs)

        self._callback = on_press_callback

        with self.canvas.before:
            Color(*BUTON)
            self._bg_rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[_SATIR_RADIUS, _SATIR_RADIUS, _SATIR_RADIUS, _SATIR_RADIUS],
            )

        with self.canvas.after:
            Color(*AYIRICI)
            self._line_rect = Line(
                rounded_rectangle=(
                    self.x,
                    self.y,
                    self.width,
                    self.height,
                    _SATIR_RADIUS,
                ),
                width=1.0,
            )

        self.bind(pos=self._yenile, size=self._yenile)

        ikon_alani = AnchorLayout(
            anchor_x="center",
            anchor_y="center",
            size_hint=(None, 1),
            width=dp(48),
        )

        source = ikon_yolu(icon_name)
        if source:
            ikon_widget = Image(
                source=source,
                size_hint=(None, None),
                size=(_IKON_BOYUTU, _IKON_BOYUTU),
                allow_stretch=True,
                keep_ratio=True,
            )
        else:
            ikon_widget = _label_merkez(
                text=str(fallback_text or "?"),
                color=METIN,
                font_size=dp(15),
                width=_IKON_BOYUTU,
                bold=True,
            )
            ikon_widget.size_hint = (None, None)
            ikon_widget.size = (_IKON_BOYUTU, _IKON_BOYUTU)

        ikon_alani.add_widget(ikon_widget)

        metin_alani = BoxLayout(
            orientation="vertical",
            spacing=dp(3),
        )

        self._title_label = _label_tek_satir(
            text=title,
            color=METIN,
            font_size=dp(15),
            height=dp(24),
            bold=True,
        )

        self._desc_label = _label_tek_satir(
            text=description,
            color=METIN_SOLUK,
            font_size=dp(12),
            height=dp(18),
            bold=False,
        )

        metin_alani.add_widget(self._title_label)
        metin_alani.add_widget(self._desc_label)

        sag_ok = _label_merkez(
            text="›",
            color=METIN_SOLUK,
            font_size=dp(22),
            width=dp(20),
            bold=True,
        )

        self.add_widget(ikon_alani)
        self.add_widget(metin_alani)
        self.add_widget(sag_ok)

    def _yenile(self, *_args) -> None:
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size
        self._line_rect.rounded_rectangle = (
            self.x,
            self.y,
            self.width,
            self.height,
            _SATIR_RADIUS,
        )

    def on_release(self) -> None:
        callback = self._callback
        if callable(callback):
            callback()


def islemler_popup(
    *,
    t: Callable[[str], str] | None = None,
    on_fonksiyon_degistir: Callable[[], None] | None = None,
    on_parca_degistir: Callable[[], None] | None = None,
    on_enjeksiyon: Callable[[], None] | None = None,
    on_dil: Callable[[], None] | None = None,
    on_yedekler: Callable[[], None] | None = None,
    on_ayarlar: Callable[[], None] | None = None,
    on_gelistirici_ayarlar: Callable[[], None] | None = None,
    title: str | None = None,
) -> Popup:
    """
    İşlemler popup'ını açar ve popup nesnesini döndürür.
    """
    cevir = t or (lambda key, **_kwargs: key)

    def _tr(key: str, fallback: str) -> str:
        text = str(cevir(key) or "").strip()
        if not text or text == key:
            return fallback
        return text

    baslik = str(title or _tr("menu_operations", "Menü İşlemleri"))

    root = BoxLayout(
        orientation="vertical",
        spacing=dp(10),
        padding=dp(12),
    )

    with root.canvas.before:
        Color(*KART)
        root._bg_rect = RoundedRectangle(  # type: ignore[attr-defined]
            pos=root.pos,
            size=root.size,
            radius=[_POPUP_RADIUS, _POPUP_RADIUS, _POPUP_RADIUS, _POPUP_RADIUS],
        )

    with root.canvas.after:
        Color(*AYIRICI)
        root._line_rect = Line(  # type: ignore[attr-defined]
            rounded_rectangle=(
                root.x,
                root.y,
                root.width,
                root.height,
                _POPUP_RADIUS,
            ),
            width=1.0,
        )

    def _root_tuvali_yenile(inst, _val) -> None:
        inst._bg_rect.pos = inst.pos  # type: ignore[attr-defined]
        inst._bg_rect.size = inst.size  # type: ignore[attr-defined]
        inst._line_rect.rounded_rectangle = (  # type: ignore[attr-defined]
            inst.x,
            inst.y,
            inst.width,
            inst.height,
            _POPUP_RADIUS,
        )

    root.bind(pos=_root_tuvali_yenile, size=_root_tuvali_yenile)

    header = BoxLayout(
        orientation="vertical",
        spacing=dp(4),
        size_hint_y=None,
        height=dp(48),
    )

    title_label = Label(
        text=baslik,
        color=METIN,
        bold=True,
        font_size=dp(17),
        halign="left",
        valign="middle",
        size_hint_y=None,
        height=dp(24),
    )
    title_label.bind(size=lambda inst, _val: setattr(inst, "text_size", inst.size))

    desc_label = Label(
        text=_tr("menu_subtitle", "İşlem seçin"),
        color=METIN_SOLUK,
        font_size=dp(12),
        halign="left",
        valign="middle",
        size_hint_y=None,
        height=dp(18),
    )
    desc_label.bind(size=lambda inst, _val: setattr(inst, "text_size", inst.size))

    header.add_widget(title_label)
    header.add_widget(desc_label)
    root.add_widget(header)

    scroll = ScrollView()
    root.add_widget(scroll)

    liste = BoxLayout(
        orientation="vertical",
        spacing=dp(8),
        size_hint_y=None,
    )
    liste.bind(minimum_height=lambda inst, val: setattr(inst, "height", val))
    scroll.add_widget(liste)

    popup = Popup(
        title="",
        separator_height=0,
        content=root,
        size_hint=(0.92, 0.82),
        auto_dismiss=True,
    )

    def _sar(callback: Callable[[], None] | None) -> Callable[[], None]:
        def _inner() -> None:
            popup.dismiss()
            if callable(callback):
                callback()

        return _inner

    menu_kayitlari = [
        {
            "icon_name": "edit.png",
            "title": _tr("operation_function_change", "Fonksiyon Değiştir"),
            "description": _tr(
                "menu_function_change_desc",
                "Fonksiyon seçip yeni kod ile güncelleyin.",
            ),
            "callback": on_fonksiyon_degistir,
            "fallback_text": "F",
        },
        {
            "icon_name": "layers.png",
            "title": _tr("operation_partial_change", "Parça Değiştir"),
            "description": _tr(
                "menu_partial_change_desc",
                "Kod parçasını bulup hedef içerikle değiştirin.",
            ),
            "callback": on_parca_degistir,
            "fallback_text": "P",
        },
        {
            "icon_name": "schema.png",
            "title": _tr("operation_injection", "Enjeksiyon"),
            "description": _tr(
                "menu_injection_desc",
                "Hedef yapıya ek kod veya blok enjekte edin.",
            ),
            "callback": on_enjeksiyon,
            "fallback_text": "E",
        },
        {
            "icon_name": "dil.png",
            "title": _tr("language", "Dil"),
            "description": _tr(
                "menu_language_desc",
                "Uygulama dilini seçin ve anında güncelleyin.",
            ),
            "callback": on_dil,
            "fallback_text": "D",
        },
        {
            "icon_name": "yedeklenen_dosyalar.png",
            "title": _tr("backups_title", "Yedeklenen Dosyalar"),
            "description": _tr(
                "menu_backups_desc",
                "Yedekleri görüntüleyin ve geri yükleme akışına gidin.",
            ),
            "callback": on_yedekler,
            "fallback_text": "Y",
        },
        {
            "icon_name": "settings.png",
            "title": _tr("settings", "Ayarlar"),
            "description": _tr(
                "menu_settings_desc",
                "Genel uygulama ayarlarını açın.",
            ),
            "callback": on_ayarlar,
            "fallback_text": "A",
        },
    ]

    if callable(on_gelistirici_ayarlar):
        menu_kayitlari.append(
            {
                "icon_name": "settings.png",
                "title": _tr("developer_settings", "Geliştirici Ayarları"),
                "description": _tr(
                    "menu_developer_settings_desc",
                    "Dil dosyaları ve geliştirici araçlarını yönetin.",
                ),
                "callback": on_gelistirici_ayarlar,
                "fallback_text": "G",
            }
        )

    for kayit in menu_kayitlari:
        liste.add_widget(
            _MenuSatiri(
                icon_name=str(kayit["icon_name"]),
                title=str(kayit["title"]),
                description=str(kayit["description"]),
                on_press_callback=_sar(kayit["callback"]),
                fallback_text=str(kayit["fallback_text"]),
            )
        )

    popup.open()
    return popup


__all__ = (
    "islemler_popup",
)