# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/tum_dosya_erisim_paketi/__init__.py

ROL:
- Paket için tek giriş noktası sağlar
- TumDosyaErisimYoneticisi'ne lazy erişim sunar
- Import maliyetini azaltır
- Circular import riskini engeller
- Üst katmanın paket içi dosya yollarını bilmeden yöneticiye ulaşmasını sağlar

MİMARİ:
- Lazy import kullanır
- Paket içi modülleri dış dünyadan gizler
- API yüzü olarak yalnızca yonetici sınıfını expose eder
- Genişletilebilir yapıdadır

KULLANIM:
from app.ui.tum_dosya_erisim_paketi import TumDosyaErisimYoneticisi

SURUM: 3
TARIH: 2026-03-23
IMZA: FY.
"""

from __future__ import annotations

from typing import Any

__all__ = [
    "TumDosyaErisimYoneticisi",
]


def __getattr__(name: str) -> Any:
    if name == "TumDosyaErisimYoneticisi":
        from app.ui.tum_dosya_erisim_paketi.yoneticisi import (
            TumDosyaErisimYoneticisi,
        )
        return TumDosyaErisimYoneticisi

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(__all__)
