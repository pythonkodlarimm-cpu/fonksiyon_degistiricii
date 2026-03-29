# -*- coding: utf-8 -*-
"""
DOSYA: app/core/tarama/__init__.py

ROL:
- Tarama paketinin dışa açılan API yüzünü tanımlar
- TaramaYoneticisi, FunctionScanError ve tarama fonksiyonlarını tek noktadan sunar
- Üst katmanın alt modülleri (tarayici.py, yoneticisi.py) doğrudan bilmesini engeller

MİMARİ:
- Lazy import kullanır
- İlk erişimden sonra cache mekanizması ile performans artırılır
- Sadece __all__ içinde tanımlı export'lar erişilebilir
- Paket iç yapısı tamamen gizlenir

EXPORT'LAR:
- TaramaYoneticisi
- FunctionScanError
- scan_functions_from_code
- scan_functions_from_file

BAĞIMLILIKLAR:
- app/core/tarama/tarayici.py
- app/core/tarama/yoneticisi.py

API UYUMLULUK:
- Platform bağımsızdır
- Android API 35 ile uyumludur
- Saf Python çalışır
- APK / AAB ortamında güvenlidir

PERFORMANS:
- Gereksiz import yükü yoktur
- Lazy load sayesinde uygulama açılış süresi optimize edilir

SURUM: 2
TARIH: 2026-03-27
IMZA: FY.
"""

from __future__ import annotations

from typing import Any

__all__ = [
    "TaramaYoneticisi",
    "FunctionScanError",
    "scan_functions_from_code",
    "scan_functions_from_file",
]

# Lazy import cache
__lazy_cache: dict[str, Any] = {}


def __getattr__(name: str) -> Any:
    """
    Lazy attribute resolver.

    Yalnızca __all__ içinde tanımlı export'lar çözümlenir.
    """
    if name not in __all__:
        raise AttributeError(
            f"{__name__!r} modülünde '{name}' adında export yok."
        )

    if name in __lazy_cache:
        return __lazy_cache[name]

    if name == "TaramaYoneticisi":
        from app.core.tarama.yoneticisi import TaramaYoneticisi
        __lazy_cache[name] = TaramaYoneticisi
        return TaramaYoneticisi

    if name == "FunctionScanError":
        from app.core.tarama.tarayici import FunctionScanError
        __lazy_cache[name] = FunctionScanError
        return FunctionScanError

    if name == "scan_functions_from_code":
        from app.core.tarama.tarayici import scan_functions_from_code
        __lazy_cache[name] = scan_functions_from_code
        return scan_functions_from_code

    if name == "scan_functions_from_file":
        from app.core.tarama.tarayici import scan_functions_from_file
        __lazy_cache[name] = scan_functions_from_file
        return scan_functions_from_file

    # teorik fallback (asla düşmemeli)
    raise AttributeError(
        f"{__name__!r} modülünde '{name}' çözümlenemedi."
    )


def __dir__() -> list[str]:
    """
    IDE / autocomplete desteği için export listesi döner.
    """
    return list(__all__)
