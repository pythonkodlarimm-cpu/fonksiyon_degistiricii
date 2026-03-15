# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/dosya_secici_paketi/models.py

ROL:
- Dosya seçici paketinde ortak model tanımları
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PickerSelection:
    path: str = ""
    uri: str = ""
    display_name: str = ""
    source: str = ""