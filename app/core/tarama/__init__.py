# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Any

__all__ = ["TaramaYoneticisi", "FunctionScanError", "scan_functions_from_code", "scan_functions_from_file"]


def __getattr__(name: str) -> Any:
    if name == "TaramaYoneticisi":
        from app.core.tarama.yoneticisi import TaramaYoneticisi
        return TaramaYoneticisi

    if name == "FunctionScanError":
        from app.core.tarama.tarayici import FunctionScanError
        return FunctionScanError

    if name == "scan_functions_from_code":
        from app.core.tarama.tarayici import scan_functions_from_code
        return scan_functions_from_code

    if name == "scan_functions_from_file":
        from app.core.tarama.tarayici import scan_functions_from_file
        return scan_functions_from_file

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(__all__)
