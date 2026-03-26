# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/root_paketi/akisi_secim/secim_akisi.py

ROL:
- Fonksiyon seçimi sonrası UI durumunu güncellemek
- Seçilen öğeyi function list ve editor ile senkronize etmek
- Güncelleme sonrası yenilenmiş öğeyi listede tekrar bulmak
- Seçim akışını UI donmasını azaltacak şekilde kademeli yürütmek
- Android restore akışında eksik/yarım item kaynaklı UI çökmesini azaltmak
- Restore sonrası seçili item'in editor ve liste tarafına tekrar güvenli biçimde bağlanmasını sağlamak

MİMARİ:
- CoreYoneticisi üzerinden kimlik eşleme yapar
- UI davranışını korur
- Servis katmanına değil, mevcut taranmış item listesine dayanır
- Root paketinin alt seçim akışı modülüdür
- Editor ve liste güncellemesi güvenli fallback ile yürütülür
- Seçim uygulanırken function_list/editor yoksa fail-soft davranır
- Restore senaryosunda eski/yarım item gelirse ek güvenlik kontrolleri devrededir

SURUM: 7
TARIH: 2026-03-26
IMZA: FY.
"""

from __future__ import annotations

from kivy.clock import Clock


class RootSecimAkisiMixin:
    # =========================================================
    # INTERNAL
    # =========================================================
    def _core(self):
        try:
            return self._get_core_yoneticisi()
        except Exception:
            return None

    def _m_secim(self, anahtar: str, default: str) -> str:
        """
        Varsa root içindeki çeviri metodunu kullanır.
        """
        try:
            if hasattr(self, "_m") and callable(getattr(self, "_m")):
                return str(self._m(anahtar, default) or default or anahtar)
        except Exception:
            pass
        return str(default or anahtar)

    def _item_gecerli_mi(self, item) -> bool:
        if item is None:
            return False

        try:
            path_value = str(getattr(item, "path", "") or "").strip()
            name_value = str(getattr(item, "name", "") or "").strip()
            source_value = str(getattr(item, "source", "") or "").strip()
            identity_value = str(getattr(item, "identity", "") or "").strip()
            dotted_value = str(getattr(item, "dotted_path", "") or "").strip()

            return bool(
                path_value
                or name_value
                or source_value
                or identity_value
                or dotted_value
            )
        except Exception:
            return False

    def _item_labeli(self, item) -> str:
        if item is None:
            return self._m_secim("function_generic", "Fonksiyon")

        for attr_name in (
            "path",
            "name",
            "signature",
            "dotted_path",
            "identity",
            "source",
        ):
            try:
                value = str(getattr(item, attr_name, "") or "").strip()
                if value:
                    return value
            except Exception:
                pass

        return self._m_secim("function_generic", "Fonksiyon")

    def _listeye_secili_item_yaz(self, item) -> None:
        """
        Function list tarafına seçili item bilgisini güvenli biçimde yazar.
        """
        try:
            function_list = getattr(self, "function_list", None)
            if function_list is None:
                return

            try:
                function_list.selected_item = item
            except Exception:
                pass

            try:
                if hasattr(function_list, "set_selected_item"):
                    function_list.set_selected_item(item)
            except Exception:
                pass

            try:
                if hasattr(function_list, "set_selected_preview"):
                    function_list.set_selected_preview(
                        str(getattr(item, "source", "") or "")
                    )
            except Exception:
                pass

            try:
                if hasattr(function_list, "clear_new_preview"):
                    function_list.clear_new_preview()
            except Exception:
                pass
        except Exception:
            pass

    def _editoru_temizlemeden_item_uygula(self, item) -> None:
        """
        Editöre seçili item'i uygular. Yeni kod alanını yalnızca gerekiyorsa temizler.
        Restore akışında kullanıldığında mevcut yazıyı korumaya yardımcı olur.
        """
        if not self._item_gecerli_mi(item):
            return

        try:
            editor = getattr(self, "editor", None)
            if editor is None:
                return

            if not hasattr(editor, "set_item"):
                return

            editor.set_item(item)
        except Exception:
            pass

    # =========================================================
    # SELECTION FLOW
    # =========================================================
    def select_item(self, item) -> None:
        if not self._item_gecerli_mi(item):
            try:
                self.set_status_warning(
                    self._m_secim(
                        "function_select_error",
                        "Seçilen fonksiyon bilgisi geçersiz.",
                    )
                )
            except Exception:
                pass
            return

        self.selected_item = item

        # -----------------------------------------------------
        # LISTE SENKRON
        # -----------------------------------------------------
        self._listeye_secili_item_yaz(item)

        # -----------------------------------------------------
        # STATUS
        # -----------------------------------------------------
        try:
            self.set_status_info(
                f"{self._m_secim('selected_prefix', 'Seçildi:')} {self._item_labeli(item)}",
                "visibility_on.png",
            )
        except Exception:
            try:
                self.set_status_info(
                    self._m_secim("function_selected", "Fonksiyon seçildi."),
                    "visibility_on.png",
                )
            except Exception:
                pass

        # -----------------------------------------------------
        # SCROLL + EDITOR APPLY (ASYNC)
        # -----------------------------------------------------
        try:
            self._scroll_to_editor()
        except Exception:
            pass

        Clock.schedule_once(
            lambda *_: self._apply_selected_item_to_editor_guvenli(item),
            0.02,
        )
        Clock.schedule_once(
            lambda *_: self._focus_new_code_area_guvenli(),
            0.08,
        )

    # =========================================================
    # EDITOR APPLY
    # =========================================================
    def _apply_selected_item_to_editor_guvenli(self, item) -> None:
        if not self._item_gecerli_mi(item):
            return

        try:
            editor = getattr(self, "editor", None)
            if editor is None:
                return

            if not hasattr(editor, "set_item"):
                return

            editor.set_item(item)

            try:
                if hasattr(editor, "set_new_code_text"):
                    editor.set_new_code_text("")
            except Exception:
                pass

        except Exception as exc:
            try:
                self.set_status_warning(
                    f"{self._m_secim('function_select_error', 'Editör seçimi uygulanamadı:')} {exc}"
                )
            except Exception:
                pass

    def _focus_new_code_area_guvenli(self) -> None:
        try:
            self._focus_new_code_area()
        except Exception:
            pass

    def _rebind_selected_item_after_restore(self) -> bool:
        """
        Restore sonrası self.selected_item mevcutsa bunu UI bileşenlerine tekrar uygular.
        Yeni kod içeriğini silmez.
        """
        item = getattr(self, "selected_item", None)
        if not self._item_gecerli_mi(item):
            return False

        try:
            self._listeye_secili_item_yaz(item)
        except Exception:
            pass

        try:
            self._editoru_temizlemeden_item_uygula(item)
        except Exception:
            pass

        return True

    # =========================================================
    # REFRESH MATCHING
    # =========================================================
    def _find_refreshed_item(self, old_item):
        """
        Tarama sonrası eski item'ın yeni karşılığını bulur.
        """
        if old_item is None:
            return None

        items = getattr(self, "items", None)
        if not items:
            return None

        core = self._core()

        # -----------------------------------------------------
        # PRIMARY: CORE IDENTITY MATCH
        # -----------------------------------------------------
        try:
            if core is not None and hasattr(core, "find_item_by_identity"):
                refreshed = core.find_item_by_identity(
                    items,
                    path=str(getattr(old_item, "path", "") or ""),
                    name=str(getattr(old_item, "name", "") or ""),
                    lineno=int(getattr(old_item, "lineno", 0) or 0),
                    kind=str(getattr(old_item, "kind", "") or ""),
                )
                if refreshed is not None:
                    return refreshed
        except Exception:
            pass

        # -----------------------------------------------------
        # FALLBACK 0: IDENTITY / DOTTED PATH
        # -----------------------------------------------------
        try:
            old_identity = str(getattr(old_item, "identity", "") or "").strip()
            old_dotted = str(getattr(old_item, "dotted_path", "") or "").strip()

            for current in items:
                try:
                    current_identity = str(
                        getattr(current, "identity", "") or ""
                    ).strip()
                    current_dotted = str(
                        getattr(current, "dotted_path", "") or ""
                    ).strip()

                    if old_identity and current_identity == old_identity:
                        return current

                    if old_dotted and current_dotted == old_dotted:
                        return current
                except Exception:
                    continue
        except Exception:
            pass

        # -----------------------------------------------------
        # FALLBACK 1: PATH + END LINENO
        # -----------------------------------------------------
        try:
            old_path = str(getattr(old_item, "path", "") or "")
            old_end_lineno = int(getattr(old_item, "end_lineno", 0) or 0)

            for current in items:
                try:
                    if (
                        str(getattr(current, "path", "") or "") == old_path
                        and int(getattr(current, "end_lineno", 0) or 0)
                        == old_end_lineno
                    ):
                        return current
                except Exception:
                    continue
        except Exception:
            pass

        # -----------------------------------------------------
        # FALLBACK 2: PATH + LINENO + NAME
        # -----------------------------------------------------
        try:
            old_path = str(getattr(old_item, "path", "") or "")
            old_lineno = int(getattr(old_item, "lineno", 0) or 0)
            old_name = str(getattr(old_item, "name", "") or "").strip()

            for current in items:
                try:
                    if (
                        str(getattr(current, "path", "") or "") == old_path
                        and int(getattr(current, "lineno", 0) or 0) == old_lineno
                        and str(getattr(current, "name", "") or "").strip() == old_name
                    ):
                        return current
                except Exception:
                    continue
        except Exception:
            pass

        # -----------------------------------------------------
        # FALLBACK 3: PATH + SIGNATURE
        # -----------------------------------------------------
        try:
            old_path = str(getattr(old_item, "path", "") or "")
            old_signature = str(getattr(old_item, "signature", "") or "").strip()

            for current in items:
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
