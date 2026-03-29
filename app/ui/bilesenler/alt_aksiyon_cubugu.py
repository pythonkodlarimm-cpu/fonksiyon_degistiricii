# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/bilesenler/alt_aksiyon_cubugu.py

ROL:
- Ana ekran ve benzeri alanlarda kullanılacak alt aksiyon çubuğunu sağlar
- Dosya seç, yapıştır, kontrol, tamamlama, temizleme ve geri yükleme aksiyonlarını sunar
- Duruma göre aksiyon görünürlüğünü yönetir
- İlk durumda yalnızca Dosya Seç aksiyonunu öne çıkarabilir
- Toolbar benzeri sade ve profesyonel görünüm sağlar
- Her ikonun altında sönük açıklama metni gösterir
- Panel alanını dengeli, ortalı ve taşma olmadan kullanır
- Geçişlerde yumuşak görünürlük animasyonu uygular
- Dil entegrasyonuna uyumludur

MİMARİ:
- UI bileşenidir
- Servis katmanını bilmez
- Callback referanslarını dışarıdan alır
- Deterministik görünürlük API'si sunar
- State tabanlı görünürlük yönetimi yapar
- Geriye uyumluluk katmanı içermez

SURUM: 10
TARIH: 2026-03-28
IMZA: FY.
"""

from __future__ import annotations

from typing import Callable

from kivy.animation import Animation
from kivy.graphics import Color, Line, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label

from app.ui.ortak.boyutlar import (
    KART_RADIUS,
    PADDING_KART,
    SPACING_BLOK,
    YUKSEKLIK_ALT_PANEL,
)
from app.ui.ortak.ikonlar import ikon_yolu
from app.ui.ortak.renkler import (
    AYIRICI,
    KART_ALT,
    METIN,
    METIN_SOLUK,
)


class _AltCubukPanel(BoxLayout):
    """
    Alt çubuk arka plan ve kenarlık kapsayıcısı.
    """

    __slots__ = ("_bg_rect", "_line")

    def __init__(
        self,
        *,
        bg_color=KART_ALT,
        line_color=AYIRICI,
        line_width: float = 1.0,
        **kwargs,
    ):
        super().__init__(**kwargs)

        with self.canvas.before:
            Color(*bg_color)
            self._bg_rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=KART_RADIUS,
            )

        with self.canvas.after:
            Color(*line_color)
            self._line = Line(
                rounded_rectangle=(
                    self.x,
                    self.y,
                    self.width,
                    self.height,
                    KART_RADIUS[0] if KART_RADIUS else 0,
                ),
                width=line_width,
            )

        self.bind(pos=self._yenile, size=self._yenile)

    def _yenile(self, *_args) -> None:
        """
        Panel arka plan ve kenarlık çizimini günceller.
        """
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size
        self._line.rounded_rectangle = (
            self.x,
            self.y,
            self.width,
            self.height,
            KART_RADIUS[0] if KART_RADIUS else 0,
        )


class _ToolbarIkonButonu(ButtonBehavior, AnchorLayout):
    """
    Arkaplansız düz toolbar ikon butonu.
    """

    __slots__ = ("_callback", "_icon_widget")

    def __init__(
        self,
        *,
        icon_name: str,
        on_press_callback: Callable | None = None,
        fallback_text: str = "?",
        icon_size=(dp(34), dp(34)),
        **kwargs,
    ):
        kwargs.setdefault("anchor_x", "center")
        kwargs.setdefault("anchor_y", "center")
        kwargs.setdefault("size_hint", (1, 1))

        super().__init__(**kwargs)

        self._callback = on_press_callback

        source = ikon_yolu(icon_name)
        if source:
            self._icon_widget = Image(
                source=source,
                size_hint=(None, None),
                size=icon_size,
                allow_stretch=True,
                keep_ratio=True,
            )
        else:
            lbl = Label(
                text=str(fallback_text or "?"),
                color=METIN,
                bold=True,
                halign="center",
                valign="middle",
                size_hint=(None, None),
                size=icon_size,
            )
            lbl.bind(size=lambda inst, _val: setattr(inst, "text_size", inst.size))
            self._icon_widget = lbl

        self.add_widget(self._icon_widget)

    def ikon_boyutu_ayarla(self, width: float, height: float) -> None:
        """
        İkon widget boyutunu günceller.
        """
        if self._icon_widget is not None:
            self._icon_widget.size = (width, height)

    def on_release(self) -> None:
        """
        Basım callback'ini güvenli biçimde tetikler.
        """
        if callable(self._callback):
            self._callback(self)


class AltAksiyonCubugu(_AltCubukPanel):
    """
    Alt aksiyon ikonlarını toolbar stilinde sunan bileşen.
    """

    __slots__ = (
        "_on_dosya_sec",
        "_on_kontrol",
        "_on_guncelle",
        "_on_geri_yukle",
        "_on_temizle",
        "_on_yapistir",
        "_icerik",
        "_t",
        "_buton_kapsayicilari",
        "_tekli_mod",
    )

    def __init__(
        self,
        *,
        on_dosya_sec: Callable | None = None,
        on_kontrol: Callable | None = None,
        on_guncelle: Callable | None = None,
        on_geri_yukle: Callable | None = None,
        on_temizle: Callable | None = None,
        on_yapistir: Callable | None = None,
        t: Callable[[str], str] | None = None,
        **kwargs,
    ):
        kwargs.setdefault("orientation", "vertical")
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height", YUKSEKLIK_ALT_PANEL)
        kwargs.setdefault("padding", PADDING_KART)

        super().__init__(**kwargs)

        self._on_dosya_sec = on_dosya_sec
        self._on_kontrol = on_kontrol
        self._on_guncelle = on_guncelle
        self._on_geri_yukle = on_geri_yukle
        self._on_temizle = on_temizle
        self._on_yapistir = on_yapistir
        self._t = t or (lambda key, **_kwargs: key)

        self._buton_kapsayicilari: dict[str, BoxLayout] = {}
        self._tekli_mod = False

        self._icerik = BoxLayout(
            orientation="horizontal",
            size_hint=(1, None),
            height=dp(64),
            spacing=SPACING_BLOK,
        )

        self.add_widget(self._icerik)
        self._butonlari_kur()

    def _t_label(self, key: str, fallback: str) -> str:
        """
        Dil anahtarını çözer; çözülmezse fallback döner.
        """
        text = self._t(key)
        return fallback if text == key else str(text or fallback)

    def _butonlari_kur(self) -> None:
        """
        Alt aksiyon butonlarını oluşturur.
        """
        butonlar = [
            (
                "dosya_sec",
                "dosya_sec.png",
                self._on_dosya_sec,
                "D",
                self._t_label("select_file", "Dosya Seç"),
            ),
            (
                "yapistir",
                "paste.png",
                self._on_yapistir,
                "P",
                self._t_label("paste", "Yapıştır"),
            ),
            (
                "kontrol",
                "code_check.png",
                self._on_kontrol,
                "K",
                self._t_label("check", "Kontrol"),
            ),
            (
                "tamamla",
                "onaylandi.png",
                self._on_guncelle,
                "✔",
                self._t_label("complete", "Tamamla"),
            ),
            (
                "temizle",
                "clear.png",
                self._on_temizle,
                "T",
                self._t_label("clear", "Temizle"),
            ),
            (
                "geri",
                "geri_yukle.png",
                self._on_geri_yukle,
                "R",
                self._t_label("restore", "Geri Yükle"),
            ),
        ]

        for anahtar, icon, callback, fallback_text, label_text in butonlar:
            kapsayici = self._etiketli_toolbar_butonu(
                icon_name=icon,
                callback=callback,
                fallback_text=fallback_text,
                label_text=label_text,
            )
            self._buton_kapsayicilari[anahtar] = kapsayici
            self._icerik.add_widget(kapsayici)

    def _etiketli_toolbar_butonu(
        self,
        *,
        icon_name: str,
        callback: Callable | None,
        fallback_text: str,
        label_text: str,
    ) -> BoxLayout:
        """
        Alt aksiyon için ikon + etiket kapsayıcısı üretir.
        """
        kapsayici = BoxLayout(
            orientation="vertical",
            size_hint=(1, 1),
            spacing=dp(2),
        )

        ikon_alani = AnchorLayout(
            anchor_x="center",
            anchor_y="center",
            size_hint_y=None,
            height=dp(40),
        )

        ikon_buton = _ToolbarIkonButonu(
            icon_name=icon_name,
            on_press_callback=callback,
            fallback_text=fallback_text,
            icon_size=(dp(32), dp(32)),
        )

        etiket = Label(
            text=str(label_text or ""),
            color=METIN_SOLUK,
            size_hint_y=None,
            height=dp(18),
            font_size=dp(11),
            halign="center",
            valign="middle",
            shorten=True,
            shorten_from="right",
        )
        etiket.bind(size=lambda inst, _val: setattr(inst, "text_size", inst.size))

        ikon_alani.add_widget(ikon_buton)
        kapsayici.add_widget(ikon_alani)
        kapsayici.add_widget(etiket)

        kapsayici._ikon_alani = ikon_alani       # type: ignore[attr-defined]
        kapsayici._ikon_buton = ikon_buton       # type: ignore[attr-defined]
        kapsayici._etiket = etiket               # type: ignore[attr-defined]

        return kapsayici

    def yalnizca_dosya_sec_modu(self) -> None:
        """
        Sadece Dosya Seç aksiyonunu görünür bırakır ve büyütür.
        """
        self._tekli_mod = True
        self._icerik.spacing = 0

        for anahtar, kapsayici in self._buton_kapsayicilari.items():
            if anahtar == "dosya_sec":
                Animation.cancel_all(kapsayici)
                kapsayici.opacity = 1
                kapsayici.disabled = False
                kapsayici.size_hint_x = 1
                kapsayici.width = 0

                kapsayici._ikon_alani.height = dp(52)          # type: ignore[attr-defined]
                kapsayici._ikon_buton.ikon_boyutu_ayarla(      # type: ignore[attr-defined]
                    dp(42),
                    dp(42),
                )
                kapsayici._etiket.font_size = dp(13)           # type: ignore[attr-defined]
                kapsayici._etiket.height = dp(20)              # type: ignore[attr-defined]
            else:
                Animation.cancel_all(kapsayici)
                kapsayici.opacity = 0
                kapsayici.disabled = True
                kapsayici.size_hint_x = None
                kapsayici.width = 0

    def normal_mod(self) -> None:
        """
        Tüm alt aksiyonları normal görünümüne döndürür.

        Not:
        - Geçişte yumuşak fade-in animasyonu uygulanır.
        """
        self._tekli_mod = False
        self._icerik.spacing = SPACING_BLOK

        for kapsayici in self._buton_kapsayicilari.values():
            Animation.cancel_all(kapsayici)

            kapsayici.disabled = False
            kapsayici.size_hint_x = 1
            kapsayici.width = 0

            kapsayici._ikon_alani.height = dp(40)              # type: ignore[attr-defined]
            kapsayici._ikon_buton.ikon_boyutu_ayarla(          # type: ignore[attr-defined]
                dp(32),
                dp(32),
            )
            kapsayici._etiket.font_size = dp(11)               # type: ignore[attr-defined]
            kapsayici._etiket.height = dp(18)                  # type: ignore[attr-defined]

            kapsayici.opacity = 0
            Animation(opacity=1, duration=0.25).start(kapsayici)

    def duruma_gore_guncelle(
        self,
        *,
        dosya_secili: bool,
        fonksiyon_secili: bool,
    ) -> None:
        """
        Dosya ve fonksiyon seçim durumuna göre görünürlüğü günceller.

        Kural:
        - Fonksiyon seçilmemişse yalnızca Dosya Seç görünür
        - Fonksiyon seçilmişse tüm aksiyonlar görünür
        """
        if not fonksiyon_secili:
            self.yalnizca_dosya_sec_modu()
            return

        self.normal_mod()


__all__ = ("AltAksiyonCubugu",)