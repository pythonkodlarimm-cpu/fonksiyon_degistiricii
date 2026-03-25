# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/fonksiyon_listesi_paketi/hata_akisi/yoneticisi.py

ROL:
- Hata akışı alt paketine tek giriş noktası sağlamak
- Fonksiyon listesi hata yönetimini merkezileştirmek
- Üst katmanın hata akışı modül detaylarını bilmesini engellemek
- Dil destekli hata formatlama ve raporlama akışını yönlendirmek

MİMARİ:
- Üst katman sadece bu yöneticiyi bilir
- Alt hata modülü doğrudan dışarı açılmaz
- Hata debug, formatlama ve raporlama akışları burada toplanır
- Lazy import kullanılır
- Fail-soft yaklaşım uygulanır
- Gereksiz raise yerine güvenli fallback döndürülür

API UYUMLULUK:
- Platform bağımsızdır
- Android API 35 ile uyumludur
- Doğrudan Android bridge çağrısı içermez

SURUM: 3
TARIH: 2026-03-24
IMZA: FY.
"""

from __future__ import annotations

import traceback


class HataAkisiYoneticisi:
    def _debug(self, message: str) -> None:
        try:
            print(f"[FONKSIYON_LISTESI_HATA_YONETICI] {message}")
        except Exception:
            pass

    def _modul(self):
        try:
            from app.ui.fonksiyon_listesi_paketi.hata_akisi import hata_akisi
            return hata_akisi
        except Exception:
            self._debug("Modül yüklenemedi.")
            self._debug(traceback.format_exc())
            raise

    def debug(self, owner, message: str) -> None:
        try:
            self._modul().debug(owner, message)
        except Exception:
            self._debug("debug çağrısı başarısız.")
            self._debug(traceback.format_exc())

    def format_exception_details(self, owner, exc: Exception, title: str) -> str:
        try:
            return self._modul().format_exception_details(owner, exc, title)
        except Exception:
            self._debug("format_exception_details çağrısı başarısız.")
            self._debug(traceback.format_exc())

            try:
                if owner is not None and hasattr(owner, "_m"):
                    return str(
                        owner._m(
                            "detail_unavailable",
                            "Ayrıntı alınamadı.",
                        )
                        or "Ayrıntı alınamadı."
                    )
            except Exception:
                pass

            return str(exc or "Ayrıntı alınamadı.")

    def report_error(
        self,
        owner,
        exc: Exception,
        title: str = "",
        detailed_text: str = "",
    ) -> None:
        try:
            self._modul().report_error(
                owner=owner,
                exc=exc,
                title=title,
                detailed_text=detailed_text,
            )
        except Exception:
            self._debug("report_error çağrısı başarısız.")
            self._debug(traceback.format_exc())
