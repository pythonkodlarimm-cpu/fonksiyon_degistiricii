# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path

import traceback


class RootDosyaAkisiMixin:
    def _working_file_ready(self) -> bool:
        try:
            if self.current_session is None:
                return False

            belge_oturumu = self._get_belge_oturumu()

            path = str(belge_oturumu["calisma_dosyasi_yolu"](self.current_session) or "").strip()
            if path:
                self.current_file_path = path

            if not self.current_file_path:
                return False

            return bool(belge_oturumu["calisma_kopyasi_var_mi"](self.current_session))
        except Exception:
            return False

    def _reload_items_from_current_file(self) -> None:
        if not self._working_file_ready():
            self.items = []
            try:
                if self.function_list is not None:
                    self.function_list.clear_all()
            except Exception:
                pass
            return

        try:
            core = self._get_core_helpers()
            self.items = core["scan_functions_from_file"](self.current_file_path)
        except Exception:
            self.items = []
            raise

        try:
            if self.function_list is not None:
                self.function_list.set_items(self.items)
        except Exception:
            pass

    def _selection_from_ui(self):
        try:
            if self.dosya_secici is not None:
                secim = self.dosya_secici.get_selection()
                if secim is not None:
                    return secim
        except Exception:
            pass

        try:
            if self.dosya_secici is not None:
                ham = str(self.dosya_secici.get_path() or "").strip()
                if ham and Path(ham).exists() and Path(ham).is_file():
                    DocumentSelection = self._get_document_selection_class()
                    return DocumentSelection(
                        source="filesystem",
                        uri="",
                        local_path=ham,
                        display_name=Path(ham).name,
                        mime_type="",
                    )
        except Exception:
            pass

        return None

    def _scan_or_refresh(self, _ignored_file_path: str) -> None:
        selection = self._selection_from_ui()
        if selection is None:
            self._clear_state()
            self.set_status_warning("Dosya seçilmedi.")
            return

        belge_oturumu = self._get_belge_oturumu()

        try:
            session = belge_oturumu["oturum_baslat"](selection)
        except belge_oturumu["BelgeOturumuServisiHatasi"] as exc:
            self._clear_state()
            self.set_status_error(f"Oturum başlatılamadı: {exc}")
            return
        except Exception as exc:
            self._clear_state()
            self.set_status_error(f"Oturum başlatılamadı: {exc}")
            return

        working_path = str(belge_oturumu["calisma_dosyasi_yolu"](session) or "").strip()
        source_identifier = str(belge_oturumu["oturum_identifier"](session) or "").strip()
        display_name = str(belge_oturumu["oturum_display_name"](session) or "").strip()

        if not working_path:
            self._clear_state()
            self.set_status_error("Çalışma dosyası oluşturulamadı.")
            return

        self.current_session = session
        self.current_file_path = working_path

        if not belge_oturumu["calisma_kopyasi_var_mi"](session):
            self._clear_state()
            self.set_status_error("Çalışma dosyası bulunamadı.")
            return

        try:
            if self.dosya_secici is not None:
                self.dosya_secici.set_path(source_identifier or working_path)
                self.dosya_secici.set_selection(selection)
        except Exception:
            pass

        self._clear_view_only()
        self._reload_items_from_current_file()
        self._reset_selection_only()

        if display_name:
            self.set_status_success(
                f"Tarama tamamlandı. {len(self.items)} fonksiyon bulundu. Belge: {display_name}"
            )
        else:
            self.set_status_success(
                f"Tarama tamamlandı. {len(self.items)} fonksiyon bulundu."
            )

        self._scroll_to_function_list()

    def refresh_file(self, file_path: str) -> None:
        try:
            self._scan_or_refresh(file_path)
        except Exception:
            self._clear_state()
            self.set_status_error("Yenileme hatası oluştu.")
            print(traceback.format_exc())

    def scan_file(self, file_path: str) -> None:
        try:
            self._scan_or_refresh(file_path)
        except Exception:
            self._clear_state()
            self.set_status_error("Tarama hatası oluştu.")
            print(traceback.format_exc())