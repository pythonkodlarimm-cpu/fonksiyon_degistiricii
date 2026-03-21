# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/root_paketi/akisi_secim/secim_akisi.py

ROL:
- Fonksiyon seçimi sonrası UI durumunu güncellemek
- Seçilen öğeyi function list ve editor ile senkronize etmek
- Güncelleme sonrası yenilenmiş öğeyi listede tekrar bulmak
- Seçim akışını UI donmasını azaltacak şekilde kademeli yürütmek

MİMARİ:
- CoreYoneticisi üzerinden kimlik eşleme yapar
- UI davranışını korur
- Servis katmanına değil, mevcut taranmış item listesine dayanır
- Root paketinin alt seçim akışı modülüdür

SURUM: 4
TARIH: 2026-03-20
IMZA: FY.
"""

from __future__ import annotations

from kivy.clock import Clock


class RootSecimAkisiMixin:
    def _core(self):
        return self._get_core_yoneticisi()

    def select_item(self, item) -> None:
        self.selected_item = item

        try:
            if self.function_list is not None:
                self.function_list.selected_item = item
                self.function_list.set_selected_preview(
                    str(getattr(item, "source", "") or "")
                )
                self.function_list.clear_new_preview()
        except Exception:
            pass

        try:
            self.set_status_info(f"Seçildi: {item.path}", "visibility_on.png")
        except Exception:
            self.set_status_info("Fonksiyon seçildi.", "visibility_on.png")

        # Önce kullanıcıya anında tepki ver
        try:
            self._scroll_to_editor()
        except Exception:
            pass

        # Ağır editor güncellemesini sonraki frame'e bırak
        Clock.schedule_once(lambda *_: self._apply_selected_item_to_editor(item), 0)

        # Focus işlemini bir tık daha sonra ver
        Clock.schedule_once(lambda *_: self._focus_new_code_area(), 0.05)

    def _apply_selected_item_to_editor(self, item) -> None:
        try:
            if self.editor is not None:
                self.editor.set_item(item)
                self.editor.set_new_code_text("")
        except Exception:
            pass

    def _find_refreshed_item(self, old_item):
        if old_item is None:
            return None

        refreshed = self._core().find_item_by_identity(
            self.items,
            path=str(getattr(old_item, "path", "") or ""),
            name=str(getattr(old_item, "name", "") or ""),
            lineno=int(getattr(old_item, "lineno", 0) or 0),
            kind=str(getattr(old_item, "kind", "") or ""),
        )
        if refreshed is not None:
            return refreshed

        old_path = str(getattr(old_item, "path", "") or "")
        old_end_lineno = int(getattr(old_item, "end_lineno", 0) or 0)
        old_signature = str(getattr(old_item, "signature", "") or "").strip()

        for current in self.items:
            if (
                str(getattr(current, "path", "") or "") == old_path
                and int(getattr(current, "end_lineno", 0) or 0) == old_end_lineno
            ):
                return current

        for current in self.items:
            if (
                str(getattr(current, "path", "") or "") == old_path
                and str(getattr(current, "signature", "") or "").strip() == old_signature
            ):
                return current

        return None