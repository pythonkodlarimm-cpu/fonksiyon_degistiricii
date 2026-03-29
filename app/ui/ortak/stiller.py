# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/ortak/stiller.py

ROL:
- Ortak UI stil yardımcılarını sağlar
- Tekrarlı canvas kodlarını merkezi hale getirir
- Deterministik ve performanslı çizim sağlar

MİMARİ:
- Canvas clear yerine referanslı güncelleme kullanır
- Widget üzerinde state tutmaz (yan etkisiz)
- Tekrarlı bind/clear maliyetini azaltır
- Ortak boyut ve renk sistemine bağlıdır
- Geriye uyumluluk katmanı içermez

SURUM: 2
TARIH: 2026-03-28
IMZA: FY.
"""

from __future__ import annotations

from kivy.graphics import Color, RoundedRectangle

from app.ui.ortak.boyutlar import KART_RADIUS
from app.ui.ortak.renkler import KART, KENARLIK


def rounded_bg(
    widget,
    *,
    bg_color=KART,
    line_color=KENARLIK,
    radius=None,
) -> None:
    """
    Widget için arka plan + kenarlık çizer.

    Bu sürüm:
    - canvas.clear() kullanmaz
    - referanslı rectangle ile performanslıdır
    - redraw sırasında sadece pos/size günceller

    Args:
        widget: Hedef widget
        bg_color: Arkaplan rengi
        line_color: Kenarlık rengi
        radius: Köşe radius (None -> KART_RADIUS)
    """
    if radius is None:
        radius = KART_RADIUS

    # -----------------------------------------------------
    # ARKA PLAN
    # -----------------------------------------------------
    with widget.canvas.before:
        Color(*bg_color)
        bg_rect = RoundedRectangle(
            pos=widget.pos,
            size=widget.size,
            radius=radius,
        )

    # -----------------------------------------------------
    # KENARLIK
    # -----------------------------------------------------
    with widget.canvas.after:
        Color(*line_color)
        line_rect = RoundedRectangle(
            pos=widget.pos,
            size=widget.size,
            radius=radius,
        )

    # -----------------------------------------------------
    # GÜNCELLEME
    # -----------------------------------------------------
    def _guncelle(*_args):
        bg_rect.pos = widget.pos
        bg_rect.size = widget.size

        line_rect.pos = widget.pos
        line_rect.size = widget.size

    widget.bind(pos=_guncelle, size=_guncelle)