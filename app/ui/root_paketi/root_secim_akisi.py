# -*- coding: utf-8 -*-
from __future__ import annotations


class RootSecimAkisiMixin:
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
            if self.editor is not None:
                self.editor.set_item(item)
                self.editor.set_new_code_text("")
        except Exception:
            pass

        try:
            self.set_status_info(f"Seçildi: {item.path}", "visibility_on.png")
        except Exception:
            self.set_status_info("Fonksiyon seçildi.", "visibility_on.png")

        self._scroll_to_editor()
        self._focus_new_code_area()

    def _find_refreshed_item(self, old_item):
        if old_item is None:
            return None

        core = self._get_core_helpers()

        refreshed = core["find_item_by_identity"](
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