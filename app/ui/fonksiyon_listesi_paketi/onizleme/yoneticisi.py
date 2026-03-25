# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/fonksiyon_listesi_paketi/onizleme/yoneticisi.py

ROL:
- Önizleme alt paketine tek giriş noktası sağlamak
- Fonksiyon metni önizleme akışını merkezileştirmek
- Üst katmanın önizleme modülü detaylarını bilmesini engellemek
- Dil destekli önizleme üretimini güvenli biçimde yönlendirmek

MİMARİ:
- Üst katman sadece bu yöneticiyi bilir
- Alt önizleme modülü doğrudan dışarı açılmaz
- Önizleme üretimi bu yönetici üzerinden çağrılır
- Lazy import kullanır
- Fail-soft yaklaşım için tanılama logu bırakır

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


class OnizlemeYoneticisi:
    def _debug(self, message: str) -> None:
        try:
            print(f"[FONKSIYON_LISTESI_ONIZLEME_YONETICI] {message}")
        except Exception:
            pass

    def modul(self):
        try:
            from app.ui.fonksiyon_listesi_paketi.onizleme import onizleme
            return onizleme
        except Exception:
            self._debug("Modül yüklenemedi.")
            self._debug(traceback.format_exc())
            raise

    def preview_from_text(self, owner, text: str, max_lines: int = 5) -> str:
        try:
            return str(
                self.modul().preview_from_text(
                    owner,
                    text,
                    max_lines=max_lines,
                )
                or ""
            )
        except Exception:
            self._debug("preview_from_text çağrısı başarısız.")
            self._debug(traceback.format_exc())

            try:
                if owner is not None and hasattr(owner, "_m"):
                    return str(
                        owner._m("preview_empty", "Henüz önizleme yok.")
                        or "Henüz önizleme yok."
                    )
            except Exception:
                pass

            return str(text or "")
