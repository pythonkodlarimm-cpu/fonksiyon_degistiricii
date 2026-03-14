# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/tema.py
ROL:
- UI katmanı için ortak renk, boşluk ve boyut sabitleri
- Görsel tutarlılığı tek merkezden yönetmek

NOT:
- Root ve alt paneller burada tanımlı sabitleri kullanır
- Böylece renk/ölçü değişikliği tek yerden yapılır
"""

from __future__ import annotations


APP_BG = (0.07, 0.08, 0.10, 1)

CARD_BG = (0.15, 0.17, 0.21, 1)
CARD_BG_SOFT = (0.12, 0.13, 0.16, 1)
CARD_BG_DARK = (0.09, 0.10, 0.13, 1)

TEXT_PRIMARY = (0.95, 0.97, 1, 1)
TEXT_SECONDARY = (0.72, 0.78, 0.88, 1)
TEXT_MUTED = (0.58, 0.66, 0.76, 1)

ACCENT = (0.16, 0.46, 0.78, 1)
SUCCESS = (0.12, 0.50, 0.28, 1)
WARNING = (0.72, 0.48, 0.12, 1)
DANGER = (0.58, 0.22, 0.22, 1)

INPUT_BG = (0.11, 0.12, 0.15, 1)
LIST_ITEM_BG = (0.18, 0.18, 0.22, 1)
LIST_ITEM_SELECTED_BG = (0.22, 0.30, 0.42, 1)

RADIUS_SM = 12
RADIUS_MD = 16
RADIUS_LG = 18
RADIUS_XL = 22