# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/tema.py
ROL:
- UI katmanı için ortak renk, boşluk ve boyut sabitleri
- Görsel tutarlılığı tek merkezden yönetmek

NOT:
- Root ve alt paneller burada tanımlı sabitleri kullanır
- Böylece renk/ölçü değişikliği tek yerden yapılır

APK / ANDROID NOTLARI:
- Tema sabitleri düz python tuple/int olarak tutulur
- Kivy tarafında doğrudan kullanılabilecek biçimdedir
- Ek yardımcılar eski kullanımı bozmaz
"""

from __future__ import annotations


def _rgba(r: float, g: float, b: float, a: float = 1.0) -> tuple[float, float, float, float]:
    return (float(r), float(g), float(b), float(a))


def _radius(value: int) -> int:
    return int(value)


APP_BG = _rgba(0.07, 0.08, 0.10, 1)

CARD_BG = _rgba(0.15, 0.17, 0.21, 1)
CARD_BG_SOFT = _rgba(0.12, 0.13, 0.16, 1)
CARD_BG_DARK = _rgba(0.09, 0.10, 0.13, 1)

TEXT_PRIMARY = _rgba(0.95, 0.97, 1.00, 1)
TEXT_SECONDARY = _rgba(0.72, 0.78, 0.88, 1)
TEXT_MUTED = _rgba(0.58, 0.66, 0.76, 1)

ACCENT = _rgba(0.16, 0.46, 0.78, 1)
SUCCESS = _rgba(0.12, 0.50, 0.28, 1)
WARNING = _rgba(0.72, 0.48, 0.12, 1)
DANGER = _rgba(0.58, 0.22, 0.22, 1)

INPUT_BG = _rgba(0.11, 0.12, 0.15, 1)
LIST_ITEM_BG = _rgba(0.18, 0.18, 0.22, 1)
LIST_ITEM_SELECTED_BG = _rgba(0.22, 0.30, 0.42, 1)

RADIUS_SM = _radius(12)
RADIUS_MD = _radius(16)
RADIUS_LG = _radius(18)
RADIUS_XL = _radius(22)


def clamp_rgba(color, fallback=(1, 1, 1, 1)) -> tuple[float, float, float, float]:
    """
    Gelen rengi güvenli RGBA tuple formatına çevirir.
    Eski kodu bozmaz; ihtiyaç olursa yardımcı olarak kullanılabilir.
    """
    try:
        values = tuple(color)
        if len(values) != 4:
            return tuple(fallback)

        out = []
        for value in values:
            num = float(value)
            if num < 0:
                num = 0.0
            if num > 1:
                num = 1.0
            out.append(num)

        return tuple(out)
    except Exception:
        return tuple(fallback)


def get_theme_snapshot() -> dict:
    """
    Tema değerlerini tek sözlük halinde döndürür.
    Debug veya ileride tema kontrolü için kullanılabilir.
    """
    return {
        "APP_BG": APP_BG,
        "CARD_BG": CARD_BG,
        "CARD_BG_SOFT": CARD_BG_SOFT,
        "CARD_BG_DARK": CARD_BG_DARK,
        "TEXT_PRIMARY": TEXT_PRIMARY,
        "TEXT_SECONDARY": TEXT_SECONDARY,
        "TEXT_MUTED": TEXT_MUTED,
        "ACCENT": ACCENT,
        "SUCCESS": SUCCESS,
        "WARNING": WARNING,
        "DANGER": DANGER,
        "INPUT_BG": INPUT_BG,
        "LIST_ITEM_BG": LIST_ITEM_BG,
        "LIST_ITEM_SELECTED_BG": LIST_ITEM_SELECTED_BG,
        "RADIUS_SM": RADIUS_SM,
        "RADIUS_MD": RADIUS_MD,
        "RADIUS_LG": RADIUS_LG,
        "RADIUS_XL": RADIUS_XL,
    }