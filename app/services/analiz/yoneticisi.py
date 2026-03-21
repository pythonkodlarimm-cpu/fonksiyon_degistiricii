# -*- coding: utf-8 -*-
"""
DOSYA: app/services/analiz/yoneticisi.py

ROL:
- Analiz katmanına tek giriş noktası sağlamak
- UI ve diğer katmanların alt analiz servis detaylarını bilmesini engellemek
- Replace karar akışını merkezileştirmek
- İleride analiz motoru büyüdüğünde tek noktadan yönetim sağlamak

MİMARİ:
- Alt analiz servislerine lazy import ile erişir
- UI katmanı sadece bu yöneticiyi bilir
- Analiz katmanının iç yapısını dış dünyadan saklar
- Şimdilik replace karar servisini yönetir
- İleride syntax/diff/ast analizleri için genişletilebilir

API UYUMLULUK:
- API 35 açısından risksizdir
- Platform bağımsızdır
- Android, dosya, URI ve reklam katmanlarından bağımsız çalışır

SURUM: 1
TARIH: 2026-03-19
IMZA: FY.
"""

from __future__ import annotations

from typing import Callable


class AnalizYoneticisi:
    # =========================================================
    # REPLACE KARAR
    # =========================================================
    def create_replace_karar_servisi(self):
        from app.services.analiz.replace_karar_servisi import ReplaceKararServisi
        return ReplaceKararServisi()

    def karar_sor(self, servis, on_result: Callable[[str], None]) -> None:
        servis.karar_sor(on_result)

    def sec_full(self, servis) -> None:
        servis.sec_full()

    def sec_preserve(self, servis) -> None:
        servis.sec_preserve()

    def iptal(self, servis) -> None:
        servis.iptal()

    def full_aciklama(self, servis, child_count: int) -> str:
        return servis.full_aciklama(child_count)

    def preserve_aciklama(self, servis, child_count: int) -> str:
        return servis.preserve_aciklama(child_count)

    def risk_notu(self, servis, child_count: int) -> str:
        return servis.risk_notu(child_count)