# -*- coding: utf-8 -*-
"""
DOSYA: app/services/__init__.py

ROL:
- Services katmanı için dışa açık lazy import giriş noktası sağlar
- ServicesYoneticisi sınıfını tek kapıdan erişilebilir hale getirir
- Import maliyetini azaltır ve modüler yapıyı korur
- Dil, güncelleme, reklam ve diğer servis akışlarının üst katmana tek kapıdan açılmasını destekler

MİMARİ:
- Services katmanının dış dünyaya açılan yüzüdür
- Alt modül yollarını dış katmanlardan gizler
- Lazy import ile gereksiz erken yüklemeyi önler
- Circular import riskini azaltmaya yardımcı olur
- Dış dünya yalnızca ServicesYoneticisi sınıfını bilir

UYUMLULUK:
- Android ve masaüstü çalışma düzeniyle uyumludur
- Platforma özel kod içermez

SURUM: 3
TARIH: 2026-03-23
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
