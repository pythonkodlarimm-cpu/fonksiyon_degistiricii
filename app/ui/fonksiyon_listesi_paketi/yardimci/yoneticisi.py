# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/fonksiyon_listesi_paketi/yardimci/yoneticisi.py

ROL:
- Yardımcı alt paketine tek giriş noktası sağlamak
- Fonksiyon listesi yardımcı akışlarını merkezileştirmek
- Üst katmanın yardımcı modül detaylarını bilmesini engellemek
- Dil destekli yardımcı çağrıları güvenli biçimde yönlendirmek

MİMARİ:
- Üst katman sadece bu yöneticiyi bilir
- Alt yardımcı modülü doğrudan dışarı açılmaz
- Item anahtarı, seçili öğe geri yükleme ve hata detay formatlama akışları burada toplanır
- Lazy import kullanır
- Fail-soft yaklaşım için tanılama logu bırakır

API UYUMLULUK:
- Platform bağımsızdır
- Android API 35 ile uyumludur
- Doğrudan Android bridge çağrısı içermez

SURUM: 2
TARIH: 2026-03-23
IMZA: FY.
"""

from __future__ import annotations

import traceback


class YardimciYoneticisi:
    def modul(self):
        try:
            from app.ui.fonksiyon_listesi_paketi.yardimci import yardimci
            return yardimci
        except Exception:
            print("[FONKSIYON_LISTESI_YARDIMCI_YONETICI] Modül yüklenemedi.")
            print(traceback.format_exc())
            raise

    def item_key(self, item) -> tuple:
        try:
            return self.modul().item_key(item)
        except Exception:
            print("[FONKSIYON_LISTESI_YARDIMCI_YONETICI] item_key çağrısı başarısız.")
            print(traceback.format_exc())
            return ("", "", "", 0, 0)

    def restore_selected_item(self, all_items, old_item):
        try:
            return self.modul().restore_selected_item(all_items, old_item)
        except Exception:
            print("[FONKSIYON_LISTESI_YARDIMCI_YONETICI] restore_selected_item çağrısı başarısız.")
            print(traceback.format_exc())
            return None

    def format_exception_details(
        self,
        owner,
        exc: Exception,
        title: str = "Fonksiyon Listesi Hatası",
    ) -> str:
        try:
            return self.modul().format_exception_details(
                owner,
                exc,
                title=title,
            )
        except Exception:
            print("[FONKSIYON_LISTESI_YARDIMCI_YONETICI] format_exception_details çağrısı başarısız.")
            print(traceback.format_exc())
            return str(exc or "Hata detayı alınamadı.")
