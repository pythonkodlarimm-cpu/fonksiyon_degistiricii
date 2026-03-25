# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/tum_dosya_erisim_paketi/panel/__init__.py

ROL:
- Panel alt paketine tek giriş noktası sağlar
- TumDosyaErisimPanelYoneticisi sınıfına lazy erişim sunar
- Import maliyetini azaltır
- Circular import riskini düşürür
- Üst katmanın panel alt paketini tek kapıdan kullanmasına yardımcı olur

MİMARİ:
- __getattr__ ile lazy import yapılır
- Alt modüller doğrudan dışarı açılmaz
- Paket dışına yalnızca TumDosyaErisimPanelYoneticisi sunulur
- Genişletilebilir yapı korunur

KULLANIM:
from app.ui.tum_dosya_erisim_paketi.panel import TumDosyaErisimPanelYoneticisi

API UYUMLULUK:
- Platform bağımsızdır
- Android API 35 ile uyumludur

SURUM: 3
TARIH: 2026-03-23
IMZA: FY.
"""

from __future__ import annotations

from typing import Any

__all__ = [
    "TumDosyaErisimPanelYoneticisi",
]


def __getattr__(name: str) -> Any:
    if name == "TumDosyaErisimPanelYoneticisi":
        from app.ui.tum_dosya_erisim_paketi.panel.yoneticisi import (
            TumDosyaErisimPanelYoneticisi,
        )
        return TumDosyaErisimPanelYoneticisi

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(__all__)
