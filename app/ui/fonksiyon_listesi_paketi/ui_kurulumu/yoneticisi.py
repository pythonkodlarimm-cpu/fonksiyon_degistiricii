# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/fonksiyon_listesi_paketi/ui_kurulumu/yoneticisi.py

ROL:
- UI kurulum alt paketine tek giriş noktası sağlamak
- Fonksiyon listesi panelinin UI kurulum akışını merkezileştirmek
- Üst katmanın UI kurulum modülü detaylarını bilmesini engellemek
- Dil destekli UI oluşturma çağrılarını güvenli biçimde yönlendirmek

MİMARİ:
- Üst katman sadece bu yöneticiyi bilir
- Alt UI kurulum modülü doğrudan dışarı açılmaz
- Başlık, arama, liste ve önizleme kartı kurulumları burada toplanır
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


class UiKurulumuYoneticisi:
    def _modul(self):
        try:
            from app.ui.fonksiyon_listesi_paketi.ui_kurulumu import ui_kurulumu
            return ui_kurulumu
        except Exception:
            print("[FONKSIYON_LISTESI_UI_KURULUM_YONETICI] Modül yüklenemedi.")
            print(traceback.format_exc())
            raise

    def build_ui(self, owner) -> None:
        try:
            self._modul().build_ui(owner)
        except Exception:
            print("[FONKSIYON_LISTESI_UI_KURULUM_YONETICI] build_ui çağrısı başarısız.")
            print(traceback.format_exc())
            raise

    def build_header_row(self, owner) -> None:
        try:
            self._modul().build_header_row(owner)
        except Exception:
            print("[FONKSIYON_LISTESI_UI_KURULUM_YONETICI] build_header_row çağrısı başarısız.")
            print(traceback.format_exc())
            raise

    def build_search_box(self, owner) -> None:
        try:
            self._modul().build_search_box(owner)
        except Exception:
            print("[FONKSIYON_LISTESI_UI_KURULUM_YONETICI] build_search_box çağrısı başarısız.")
            print(traceback.format_exc())
            raise

    def build_list_box(self, owner) -> None:
        try:
            self._modul().build_list_box(owner)
        except Exception:
            print("[FONKSIYON_LISTESI_UI_KURULUM_YONETICI] build_list_box çağrısı başarısız.")
            print(traceback.format_exc())
            raise

    def build_preview_boxes(self, owner) -> None:
        try:
            self._modul().build_preview_boxes(owner)
        except Exception:
            print("[FONKSIYON_LISTESI_UI_KURULUM_YONETICI] build_preview_boxes çağrısı başarısız.")
            print(traceback.format_exc())
            raise

    def build_preview_card(self, owner, title: str, icon_name: str):
        try:
            return self._modul().build_preview_card(
                owner,
                title=title,
                icon_name=icon_name,
            )
        except Exception:
            print("[FONKSIYON_LISTESI_UI_KURULUM_YONETICI] build_preview_card çağrısı başarısız.")
            print(traceback.format_exc())
            raise

    def build_table_header_label(self, owner, text: str, size_hint_x: float):
        try:
            return self._modul().build_table_header_label(
                owner,
                text=text,
                size_hint_x=size_hint_x,
            )
        except Exception:
            print("[FONKSIYON_LISTESI_UI_KURULUM_YONETICI] build_table_header_label çağrısı başarısız.")
            print(traceback.format_exc())
            raise
