# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/dil_paketi/__init__.py

ROL:
- Dil UI paketi için dışa açık lazy import giriş noktası sağlar
- DilYoneticisi sınıfını tek kapıdan erişilebilir hale getirir
- Import maliyetini azaltır ve modüler yapıyı korur

MİMARİ:
- Dil UI katmanının dış dünyaya açılan yüzüdür
- Alt modül yollarını dış katmanlardan gizler
- Lazy import ile gereksiz erken yüklemeyi önler
- Circular import riskini azaltmaya yardımcı olur

API UYUMLULUK:
- Android ve masaüstü çalışma düzeniyle uyumludur
- Platforma özel kod içermez

SURUM: 1
TARIH: 2026-03-23
IMZA: FY.
"""

from __future__ import annotations

from typing import Any

__all__ = ["DilYoneticisi"]


def __getattr__(name: str) -> Any:
    if name == "DilYoneticisi":
        from app.ui.dil_paketi.yoneticisi import DilYoneticisi
        return DilYoneticisi

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(__all__)
