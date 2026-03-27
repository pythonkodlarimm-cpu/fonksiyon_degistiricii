# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/root_paketi/akisi_secim/secim_akisi.py

ROL:
- Fonksiyon seçimi sonrası UI durumunu günceller
- Seçilen öğeyi function list ve editor ile senkronize eder
- Güncelleme sonrası yenilenmiş öğeyi listede tekrar bulur
- Restore sonrası seçili item'i editor ve liste tarafına tekrar güvenli biçimde bağlar

MİMARİ:
- Core yöneticisi üzerinden kimlik eşleme yapabilir
- Servis katmanına değil, mevcut taranmış item listesine dayanır
- Root paketinin alt seçim akışı modülüdür
- Editor ve liste güncellemesi fail-soft yürütülür
- Çeviri için root üzerindeki self._m(...) hattını kullanır

SURUM: 8
TARIH: 2026-03-27
IMZA: FY.
"""

from __future__ import annotations

from kivy.clock import Clock


class RootSecimAkisiMixin:
    def _core(self):
        try:
            return self._get_core_yoneticisi()
        except Exception:
            return None

    def _ceviri(self, anahtar: str, varsayilan: str) -> str:
        """
        Varsa root içindeki çeviri metodunu kullanır.
        """
        try:
            metod = getattr(self, "_m", None)
            if callable(metod):
                return str(metod(anahtar, varsayilan) or varsayilan)
        except Exception:
            pass
        return str(varsayilan)

    def _item_gecerli_mi(self, item) -> bool:
        if item is None:
            return False

        for alan in ("path", "name", "source", "identity", "dotted_path"):
            try:
                deger = str(getattr(item, alan, "") or "").strip()
                if deger:
                    return True
            except Exception:
                continue

        return False

    def _item_labeli(self, item) -> str:
        if item is None:
            return self._ceviri("function_generic", "Fonksiyon")

        for alan in (
            "path",
            "name",
            "signature",
            "dotted_path",
            "identity",
            "source",
        ):
            try:
                deger = str(getattr(item, alan, "") or "").strip()
                if deger:
                    return deger
            except Exception:
                continue

        return self._ceviri("function_generic", "Fonksiyon")

    def _listeye_secili_item_yaz(self, item) -> None:
        """
        Function list tarafına seçili item bilgisini güvenli biçimde yazar.
        """
        function_list = getattr(self, "function_list", None)
        if function_list is None:
            return

        try:
            function_list.selected_item = item
        except Exception:
            pass

        try:
            metod = getattr(function_list, "set_selected_item", None)
            if callable(metod):
                metod(item)
        except Exception:
            pass

        try:
            metod = getattr(function_list, "set_selected_preview", None)
            if callable(metod):
                metod(str(getattr(item, "source", "") or ""))
        except Exception:
            pass

        try:
            metod = getattr(function_list, "clear_new_preview", None)
            if callable(metod):
                metod()
        except Exception:
            pass

    def _editoru_temizlemeden_item_uygula(self, item) -> None:
        """
        Editöre seçili item'i uygular.
        Restore akışında mevcut yeni kod içeriğini korumaya yardımcı olur.
        """
        if not self._item_gecerli_mi(item):
            return

        editor = getattr(self, "editor", None)
        if editor is None:
            return

        try:
            metod = getattr(editor, "set_item", None)
            if callable(metod):
                metod(item)
        except Exception:
            pass

    def select_item(self, item) -> None:
        """
        Seçilen item'i liste ve editör ile senkronize eder.
        """
        if not self._item_gecerli_mi(item):
            try:
                self.set_status_warning(
                    self._ceviri(
                        "function_select_error",
                        "Seçilen fonksiyon bilgisi geçersiz.",
                    )
                )
            except Exception:
                pass
            return

        self.selected_item = item
        self._listeye_secili_item_yaz(item)

        try:
            self.set_status_info(
                f"{self._ceviri('selected_prefix', 'Seçildi:')} {self._item_labeli(item)}",
                "visibility_on.png",
            )
        except Exception:
            try:
                self.set_status_info(
                    self._ceviri("function_selected", "Fonksiyon seçildi."),
                    "visibility_on.png",
                )
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
        Clock.schedule_once(
            lambda *_: self._focus_new_code_area_guvenli(),
            0.08,
        )

    def _apply_selected_item_to_editor_guvenli(self, item) -> None:
        """
        Seçili item'i editöre uygular ve yeni kod alanını temizler.
        """
        if not self._item_gecerli_mi(item):
            return

        editor = getattr(self, "editor", None)
        if editor is None:
            return

        try:
            metod = getattr(editor, "set_item", None)
            if callable(metod):
                metod(item)
        except Exception as exc:
            try:
                self.set_status_warning(
                    f"{self._ceviri('function_select_error', 'Editör seçimi uygulanamadı:')} {exc}"
                )
            except Exception:
                pass
            return

        try:
            metod = getattr(editor, "set_new_code_text", None)
            if callable(metod):
                metod("")
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

        try:
            metod = getattr(core, "find_item_by_identity", None) if core is not None else None
            if callable(metod):
                bulunan = metod(
                    items,
                    path=str(getattr(old_item, "path", "") or ""),
                    name=str(getattr(old_item, "name", "") or ""),
                    lineno=int(getattr(old_item, "lineno", 0) or 0),
                    kind=str(getattr(old_item, "kind", "") or ""),
                )
                if bulunan is not None:
                    return bulunan
        except Exception:
            pass

        eski_identity = ""
        eski_dotted = ""
        try:
            eski_identity = str(getattr(old_item, "identity", "") or "").strip()
        except Exception:
            pass
        try:
            eski_dotted = str(getattr(old_item, "dotted_path", "") or "").strip()
        except Exception:
            pass

        if eski_identity or eski_dotted:
            for current in items:
                try:
                    current_identity = str(getattr(current, "identity", "") or "").strip()
                    current_dotted = str(getattr(current, "dotted_path", "") or "").strip()

                    if eski_identity and current_identity == eski_identity:
                        return current

                    if eski_dotted and current_dotted == eski_dotted:
                        return current
                except Exception:
                    continue

        try:
            eski_path = str(getattr(old_item, "path", "") or "")
            eski_end_lineno = int(getattr(old_item, "end_lineno", 0) or 0)

            for current in items:
                try:
                    if (
                        str(getattr(current, "path", "") or "") == eski_path
                        and int(getattr(current, "end_lineno", 0) or 0) == eski_end_lineno
                    ):
                        return current
                except Exception:
                    continue
        except Exception:
            pass

        try:
            eski_path = str(getattr(old_item, "path", "") or "")
            eski_lineno = int(getattr(old_item, "lineno", 0) or 0)
            eski_name = str(getattr(old_item, "name", "") or "").strip()

            for current in items:
                try:
                    if (
                        str(getattr(current, "path", "") or "") == eski_path
                        and int(getattr(current, "lineno", 0) or 0) == eski_lineno
                        and str(getattr(current, "name", "") or "").strip() == eski_name
                    ):
                        return current
                except Exception:
                    continue
        except Exception:
            pass

        try:
            eski_path = str(getattr(old_item, "path", "") or "")
            eski_signature = str(getattr(old_item, "signature", "") or "").strip()

            for current in items:
                try:
                    if (
                        str(getattr(current, "path", "") or "") == eski_path
                        and str(getattr(current, "signature", "") or "").strip() == eski_signature
                    ):
                        return current
                except Exception:
                    continue
        except Exception:
            pass

        return None
