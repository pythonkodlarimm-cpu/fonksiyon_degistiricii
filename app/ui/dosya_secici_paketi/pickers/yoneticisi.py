# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/dosya_secici_paketi/pickers/yoneticisi.py

ROL:
- Picker alt paketine tek giriş noktası sağlamak
- Platforma uygun picker sınıfını seçmek
- Üst katmanın picker detaylarını bilmesini engellemek

MİMARİ:
- Android'de AndroidDokumanSecici kullanılır
- Diğer ortamlarda MasaustuSecici kullanılır
- Üst katman sadece bu yöneticiyi bilir

API UYUMLULUK:
- API 35 uyumlu
- Android SAF akışına uyumlu
- Masaüstü path tabanlı akışla uyumlu

SURUM: 1
TARIH: 2026-03-19
IMZA: FY.
"""

from __future__ import annotations

from kivy.utils import platform


class PickerYoneticisi:
    def aktif_picker_sinifi(self):
        if platform == "android":
            from app.ui.dosya_secici_paketi.pickers.android_dokuman import (
                AndroidDokumanSecici,
            )
            return AndroidDokumanSecici

        from app.ui.dosya_secici_paketi.pickers.masaustu import MasaustuSecici
        return MasaustuSecici

    def picker_olustur(self, owner, on_selected):
        picker_sinifi = self.aktif_picker_sinifi()
        return picker_sinifi(owner=owner, on_selected=on_selected)

    def picker_ac(self, owner, on_selected):
        picker = self.picker_olustur(owner=owner, on_selected=on_selected)

        if hasattr(picker, "secici_ac") and callable(getattr(picker, "secici_ac")):
            picker.secici_ac()
            return picker

        if hasattr(picker, "open_picker") and callable(getattr(picker, "open_picker")):
            picker.open_picker()
            return picker

        if hasattr(picker, "open_popup") and callable(getattr(picker, "open_popup")):
            picker.open_popup()
            return picker

        raise ValueError("Uygun picker açma metodu bulunamadı.")