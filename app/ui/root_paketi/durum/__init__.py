# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/root_paketi/durum/__init__.py

ROL:
- Root durum alt paketine tek giriş noktası sağlar
- RootDurumYoneticisi sınıfına lazy erişim sunar
- Import maliyetini azaltır
- Circular import riskini düşürür

KULLANIM:
from app.ui.root_paketi.durum import RootDurumYoneticisi

MİMARİ:
- Alt modülleri doğrudan expose etmez
- Lazy import ile ihtiyaç anında yükleme yapar
- Paket dışına kontrollü API sunar

API UYUMLULUK:
- Android ve masaüstü ile uyumludur
- Platform bağımsızdır

SURUM: 2
TARIH: 2026-03-23
IMZA: FY.
"""

from __future__ import annotations

from typing import Any

__all__ = ["RootDurumYoneticisi"]


def __getattr__(name: str) -> Any:
    if name == "RootDurumYoneticisi":
        from app.ui.root_paketi.durum.yoneticisi import RootDurumYoneticisi
        return RootDurumYoneticisi

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(__all__)
