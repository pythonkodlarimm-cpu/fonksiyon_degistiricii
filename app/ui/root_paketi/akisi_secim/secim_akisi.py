# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/root_paketi/akisi_secim/secim_akisi.py

ROL:
- Fonksiyon seçimi sonrası UI durumunu güncellemek
- Seçilen öğeyi function list ve editor ile senkronize etmek
- Güncelleme sonrası yenilenmiş öğeyi listede tekrar bulmak
- Seçim akışını UI donmasını azaltacak şekilde kademeli yürütmek
- Android restore akışında eksik/yarım item kaynaklı UI çökmesini azaltmak

MİMARİ:
- CoreYoneticisi üzerinden kimlik eşleme yapar
- UI davranışını korur
- Servis katmanına değil, mevcut taranmış item listesine dayanır
- Root paketinin alt seçim akışı modülüdür
- Editor ve liste güncellemesi güvenli fallback ile yürütülür

SURUM: 5
TARIH: 2026-03-23
IMZA: FY.
"""

from __future__ import annotations

from kivy.clock import Clock


class RootSecimAkisiMixin:
    def _core(self):
        return self._get_core_yoneticisi()

    def _item_gecerli_mi(self, item) -> bool:
        if item is None:
            return False

        try:
            path_value = str(getattr(item, "path", "") or "").strip()
            name_value = str(getattr(item, "name", "") or "").strip()
            source_value = str(getattr(item, "source", "") or "").strip()

            return bool(path_value or name_value or source_value)
        except Exception:
            return False

    def _item_labeli(self, item) -> str:
        if item is None:
            return "Fonksiyon"

        for attr_name in ("path", "name", "signature", "source"):
            try:
                value = str(getattr(item, attr_name, "") or "").strip()
                if value:
                    return value
            except Exception:
                pass

        return "Fonksiyon"

    def select_item(self, item) -> None:
        if not self._item_gecerli_mi(item):
            try:
                self.set_status_warning("Seçilen fonksiyon bilgisi geçersiz.")
            except Exception:
                pass
            return

        self.selected_item = item

        try:
            if self.function_list is not None:
                self.function_list.selected_item = item

                try:
                    self.function_list.set_selected_preview(
                        str(getattr(item, "source", "") or "")
                    )
                except Exception:
                    pass

                try:
                    self.function_list.clear_new_preview()
                except Exception:
                    pass
        except Exception:
            pass

        try:
            self.set_status_info(
                f"Seçildi: {self._item_labeli(item)}",
                "visibility_on.png",
            )
        except Exception:
            try:
                self.set_status_info("Fonksiyon seçildi.", "visibility_on.png")
            except Exception:
                pass

        try:
            self._scroll_to_editor()
        except Exception:
            pass

        Clock.schedule_once(
            lambda *_: self._apply_selected_item_to_editor_guvenli(item),
            0.02,
        )
        Clock.schedule_once(lambda *_: self._focus_new_code_area_guvenli(), 0.08)

    def _apply_selected_item_to_editor_guvenli(self, item) -> None:
        if not self._item_gecerli_mi(item):
            return

        try:
            if self.editor is None:
                return

            if not hasattr(self.editor, "set_item"):
                return

            self.editor.set_item(item)

            try:
                if hasattr(self.editor, "set_new_code_text"):
                    self.editor.set_new_code_text("")
            except Exception:
                pass

        except Exception as exc:
            try:
                self.set_status_warning(f"Editör seçimi uygulanamadı: {exc}")
            except Exception:
                pass

    def _focus_new_code_area_guvenli(self) -> None:
        try:
            self._focus_new_code_area()
        except Exception:
            pass

    def _find_refreshed_item(self, old_item):
        if old_item is None:
            return None

        try:
            refreshed = self._core().find_item_by_identity(
                self.items,
                path=str(getattr(old_item, "path", "") or ""),
                name=str(getattr(old_item, "name", "") or ""),
                lineno=int(getattr(old_item, "lineno", 0) or 0),
                kind=str(getattr(old_item, "kind", "") or ""),
            )
            if refreshed is not None:
                return refreshed
        except Exception:
            pass

        try:
            old_path = str(getattr(old_item, "path", "") or "")
            old_end_lineno = int(getattr(old_item, "end_lineno", 0) or 0)
            old_signature = str(getattr(old_item, "signature", "") or "").strip()

            for current in self.items:
                try:
                    if (
                        str(getattr(current, "path", "") or "") == old_path
                        and int(getattr(current, "end_lineno", 0) or 0) == old_end_lineno
                    ):
                        return current
                except Exception:
                    continue

            for current in self.items:
                try:
                    if (
                        str(getattr(current, "path", "") or "") == old_path
                        and str(getattr(current, "signature", "") or "").strip()
                        == old_signature
                    ):
                        return current
                except Exception:
                    continue
        except Exception:
            pass

        return None
