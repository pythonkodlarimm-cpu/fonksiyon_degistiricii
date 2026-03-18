# -*- coding: utf-8 -*-
"""
DOSYA: app/services/replace_karar_servisi.py

ROL:
- Fonksiyon güncelleme öncesi replace mode kararını yönetmek
- UI katmanına karar sonucu döndürmek
- Popup için açıklama verisini taşımak

SURUM: 2
TARIH: 2026-03-18
IMZA: FY.
"""

from __future__ import annotations

from typing import Callable, Optional


class ReplaceKararServisi:
    """
    Fonksiyon güncelleme stratejisini yönetir.
    """

    def __init__(self):
        self._callback: Optional[Callable[[str], None]] = None

    def karar_sor(self, on_result: Callable[[str], None]) -> None:
        self._callback = on_result

    def sec_full(self) -> None:
        if self._callback:
            self._callback("full")

    def sec_preserve(self) -> None:
        if self._callback:
            self._callback("preserve_children")

    def iptal(self) -> None:
        if self._callback:
            self._callback("cancel")

    def full_aciklama(self, child_count: int) -> str:
        adet = max(0, int(child_count or 0))
        if adet <= 0:
            return (
                "Seçilen fonksiyonun mevcut gövdesi tamamen yeni kod ile değiştirilir.\n"
                "Alt fonksiyon bulunmadığı için ek bir silinme riski yoktur."
            )

        return (
            "Seçilen fonksiyonun mevcut gövdesi tamamen yeni kod ile değiştirilir.\n"
            f"Bu işlem sırasında içeride bulunan {adet} alt fonksiyon yeni kodda yoksa kaldırılır.\n"
            "Bu mod hızlı ve nettir, ancak yıkıcı olabilir."
        )

    def preserve_aciklama(self, child_count: int) -> str:
        adet = max(0, int(child_count or 0))
        if adet <= 0:
            return (
                "Seçilen fonksiyonun alt fonksiyonu bulunmadı.\n"
                "Bu durumda koruma modu ile tam değişim modu pratikte aynı davranır."
            )

        return (
            "Seçilen fonksiyonun üst gövdesi yeni kod ile güncellenir.\n"
            f"İçeride bulunan {adet} alt fonksiyon korunmaya çalışılır.\n"
            "Bu mod daha güvenlidir, ancak yeni kod yapısına göre dikkatli kullanılmalıdır."
        )

    def risk_notu(self, child_count: int) -> str:
        adet = max(0, int(child_count or 0))
        if adet <= 0:
            return "Risk düşük: alt fonksiyon bulunmadı."
        if adet == 1:
            return "Risk orta: 1 alt fonksiyon etkilenebilir."
        return f"Risk yüksek: {adet} alt fonksiyon etkilenebilir."