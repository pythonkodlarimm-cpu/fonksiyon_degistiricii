# -*- coding: utf-8 -*-
"""
DOSYA: app/services/__init__.py

ROL:
- Services katmanı için dışa açık lazy import giriş noktası sağlar
- ServicesYoneticisi sınıfını tek kapıdan erişilebilir hale getirir
- Import maliyetini azaltır ve modüler yapıyı korur

MİMARİ:
- Services katmanının dış dünyaya açılan yüzüdür
- Alt modül yollarını dış katmanlardan gizler
- Lazy import ile gereksiz erken yüklemeyi önler
- Circular import riskini azaltmaya yardımcı olur

UYUMLULUK:
- Android ve masaüstü çalışma düzeniyle uyumludur
- Platforma özel kod içermez

SURUM: 2
TARIH: 2026-03-22
IMZA: FY.
"""

from __future__ import annotations

from typing import Any

__all__ = ["ServicesYoneticisi"]


def __getattr__(name: str) -> Any:
    if name == "ServicesYoneticisi":
        from app.services.yoneticisi import ServicesYoneticisi
        return ServicesYoneticisi

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(__all__)
