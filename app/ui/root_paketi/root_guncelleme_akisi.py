# -*- coding: utf-8 -*-
from __future__ import annotations

import traceback


class RootGuncellemeAkisiMixin:
    def _count_child_functions(self, item) -> int:
        try:
            item_path = str(getattr(item, "path", "") or "").strip()
            if not item_path:
                return 0

            prefix = item_path + "."
            count = 0

            for current in self.items:
                current_path = str(getattr(current, "path", "") or "").strip()
                if current_path.startswith(prefix):
                    count += 1

            return count
        except Exception:
            return 0

    def _child_function_names(self, item) -> list[str]:
        try:
            item_path = str(getattr(item, "path", "") or "").strip()
            if not item_path:
                return []

            prefix = item_path + "."
            out: list[str] = []

            for current in self.items:
                current_path = str(getattr(current, "path", "") or "").strip()
                if current_path.startswith(prefix):
                    out.append(current_path)

            out.sort()
            return out
        except Exception:
            return []

    def _item_has_child_functions(self, item) -> bool:
        return self._count_child_functions(item) > 0

    def _start_replace_decision_flow(self, item, new_code: str) -> None:
        self._pending_update_payload = {
            "item": item,
            "new_code": str(new_code or ""),
        }

        child_count = self._count_child_functions(item)
        child_names = self._child_function_names(item)

        if child_count <= 0:
            self._continue_update_with_mode("full")
            return

        try:
            ReplaceKararServisi = self._get_replace_karar_servisi_class()
            ReplaceKararPopup = self._get_replace_karar_popup_class()

            self._replace_karar_servisi = ReplaceKararServisi()

            def _on_result(mode: str) -> None:
                self._continue_update_with_mode(mode)

            self._replace_karar_servisi.karar_sor(_on_result)

            popup = ReplaceKararPopup(
                self._replace_karar_servisi,
                function_name=str(getattr(item, "name", "") or ""),
                function_path=str(getattr(item, "path", "") or ""),
                child_count=child_count,
                child_names=child_names,
            )
            popup.open()

            self.set_status_warning(
                "Bu fonksiyonun içinde alt fonksiyonlar var. Güncelleme modu seçin."
            )
        except Exception as exc:
            self._debug(f"replace karar akışı açılamadı: {exc}")
            self._continue_update_with_mode("full")

    def _continue_update_with_mode(self, replace_mode: str) -> None:
        payload = dict(self._pending_update_payload or {})
        self._pending_update_payload = None

        mode = str(replace_mode or "").strip().lower()
        if mode == "cancel":
            self.set_status_info("Fonksiyon güncelleme iptal edildi.")
            return

        if mode not in {"full", "preserve_children"}:
            mode = "full"

        item = payload.get("item")
        new_code = str(payload.get("new_code", "") or "")

        self._apply_selected_function_update(
            item=item,
            new_code=new_code,
            replace_mode=mode,
        )

    def _apply_selected_function_update(self, item, new_code: str, replace_mode: str) -> None:
        belge_oturumu = self._get_belge_oturumu()
        dosya_servisi = self._get_dosya_servisi()
        core = self._get_core_helpers()

        try:
            if self.current_session is None:
                self.set_status_warning("Önce dosya seç.")
                return

            if not self._working_file_ready():
                self.set_status_error("Çalışma dosyası artık bulunamadı.")
                return

            if item is None:
                self.set_status_warning("Önce bir fonksiyon seç.")
                return

            if not str(new_code or "").strip():
                self.set_status_warning("Yeni fonksiyon kodu boş olamaz.")
                return

            try:
                if self.function_list is not None:
                    self.function_list.set_new_preview(str(new_code or ""))
                if self.editor is not None:
                    self.editor.set_new_code_text(str(new_code or ""))
            except Exception:
                pass

            old_source = dosya_servisi["read_text"](self.current_file_path)
            updated_source = core["update_function_in_code"](
                old_source,
                item,
                new_code,
                replace_mode=replace_mode,
            )

            backup_path = belge_oturumu["guncellenmis_icerigi_kaydet"](
                self.current_session,
                updated_source,
            )

            self._reload_items_from_current_file()

            refreshed = self._find_refreshed_item(item)
            self.selected_item = refreshed

            try:
                if self.function_list is not None:
                    self.function_list.set_items(self.items)
                    self.function_list.selected_item = refreshed
                    self.function_list.set_selected_preview(
                        str(getattr(refreshed, "source", "") or "")
                    )
                    self.function_list.set_new_preview(str(new_code or ""))
            except Exception:
                pass

            try:
                if self.editor is not None:
                    self.editor.set_item(refreshed)
                    self.editor.set_new_code_text(str(new_code or ""))
            except Exception:
                pass

            backup_text = str(backup_path or "").strip() or self._safe_backup_text()
            mode_text = (
                "alt fonksiyonlar korunarak"
                if replace_mode == "preserve_children"
                else "komple değişim"
            )

            if refreshed is not None:
                self.set_status_success(
                    f"Güncellendi ({mode_text}): {refreshed.path} | Yedek: {backup_text}"
                )
            else:
                self.set_status_success(
                    f"Güncellendi ({mode_text}). Seçim yenilenemedi ama dosya kaydedildi. "
                    f"Yedek: {backup_text}"
                )

        except belge_oturumu["BelgeOturumuServisiHatasi"] as exc:
            self.set_status_error(str(exc))
        except ValueError as exc:
            self.set_status_error(str(exc))
        except SyntaxError as exc:
            self.set_status_error(f"Sözdizimi hatası: {exc}")
        except Exception:
            self.set_status_error("Güncelleme hatası oluştu.")
            print(traceback.format_exc())

    def update_selected_function(self, item, new_code: str) -> None:
        try:
            if self.current_session is None:
                self.set_status_warning("Önce dosya seç.")
                return

            if item is None:
                self.set_status_warning("Önce bir fonksiyon seç.")
                return

            if not str(new_code or "").strip():
                self.set_status_warning("Yeni fonksiyon kodu boş olamaz.")
                return

            self._start_replace_decision_flow(item, new_code)

        except Exception:
            self.set_status_error("Güncelleme hazırlık hatası oluştu.")
            print(traceback.format_exc())