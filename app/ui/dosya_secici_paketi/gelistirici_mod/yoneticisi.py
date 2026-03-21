# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/dosya_secici_paketi/gelistirici_mod/yoneticisi.py
"""

from __future__ import annotations

from pathlib import Path

from app.ui.dosya_secici_paketi.gelistirici_mod.yardimci import (
    dev_mode_aktif_mi,
    test_dosya_adi,
    test_mime_type_bul,
    test_yolu_gecerli_mi,
)


class GelistiriciModYoneticisi:
    def dev_mode_aktif_mi(self) -> bool:
        return dev_mode_aktif_mi()

    def popup_sinifi(self):
        from app.ui.dosya_secici_paketi.gelistirici_mod.test_dosya_secici_popup import (
            TestDosyaSeciciPopup,
        )
        return TestDosyaSeciciPopup

    def document_selection_class(self):
        from app.ui.dosya_secici_paketi.models import DocumentSelection
        return DocumentSelection

    def test_popup_ac(self, on_select=None, start_dir: str | None = None):
        popup = self.popup_sinifi()(
            on_select=on_select,
            start_dir=start_dir,
        )
        popup.open()
        return popup

    def test_selection_olustur(self, path: str):
        temiz_yol = str(path or "").strip()
        if not test_yolu_gecerli_mi(temiz_yol):
            return None

        DocumentSelection = self.document_selection_class()

        return DocumentSelection(
            source="filesystem",
            uri="",
            local_path=temiz_yol,
            display_name=test_dosya_adi(temiz_yol) or Path(temiz_yol).name,
            mime_type=test_mime_type_bul(temiz_yol),
        )