# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/dil_paketi/__init__.py

ROL:
- Dil UI paketi için dışa açık lazy import giriş noktası sağlar
- DilYoneticisi sınıfını tek kapıdan erişilebilir hale getirir
- Import maliyetini azaltır ve modüler yapıyı korur
- Dil seçim akışını yalnızca yönetici katmanı üzerinden dışa açar

MİMARİ:
- Dil UI katmanının dış dünyaya açılan yüzüdür
- Alt modül yollarını dış katmanlardan gizler
- Lazy import ile gereksiz erken yüklemeyi önler
- Circular import riskini azaltmaya yardımcı olur
- Paket dışına yalnızca DilYoneticisi açılır
- Popup sınıfı ve popup yöneticisi dışarıya doğrudan açılmaz

KULLANIM:
from app.ui.dil_paketi import DilYoneticisi

API UYUMLULUK:
- Android ve masaüstü çalışma düzeniyle uyumludur
- Platforma özel kod içermez

SURUM: 4
TARIH: 2026-03-24
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
