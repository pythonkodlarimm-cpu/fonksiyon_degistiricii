# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/root_paketi/akisi_guncelleme/guncelleme_akisi.py

ROL:
- Seçili fonksiyonun güncelleme akışını yönetmek
- Güncellenmiş içeriği belge katmanı üzerinden kaydetmek
- Güncelleme sonrası UI ve seçim durumunu senkronize etmek
- Hata durumunda detaylı, kopyalanabilir hata bilgisini iletmek
- Hedef seçimin gerçekten çalışma dosyasına ait olup olmadığını doğrulamak

MİMARİ:
- SADECE yöneticiler kullanılır
- Eski dict/fallback yapı kaldırıldı
- Analiz, belge, dosya, servis ve core katmanları yöneticiler üzerinden çağrılır
- UI davranışı korunur
- Root paketinin alt güncelleme akışı modülüdür
- Güncelleme akışı sade ve deterministik tutulur
- Seçili fonksiyon komple değiştirilir

API UYUMLULUK:
- Android SAF + content URI uyumlu
- API 35 uyumlu
- APK / AAB davranış farkını azaltacak izole akış sağlar

SURUM: 10
TARIH: 2026-03-20
IMZA: FY.
"""

from __future__ import annotations

import traceback


class RootGuncellemeAkisiMixin:
    # =========================================================
    # INTERNAL HELPERS
    # =========================================================
    def _services(self):
        return self._get_services_yoneticisi()

    def _core(self):
        return self._get_core_yoneticisi()

    def _belge(self):
        return self._services().belge_yoneticisi()

    def _dosya(self):
        return self._services().dosya_yoneticisi()

    def _analiz(self):
        return self._services().analiz_yoneticisi()

    def _debug(self, message: str) -> None:
        try:
            print(f"[ROOT_GUNCELLEME_AKISI] {message}")
        except Exception:
            pass

    def _is_invalid_internal_item(self, item) -> bool:
        try:
            if item is None:
                return True

            path = str(getattr(item, "path", "") or "").strip()
            file_path = str(getattr(item, "file_path", "") or "").strip().replace("\\", "/")

            if not path:
                return True

            if "RootGuncellemeAkisiMixin" in path:
                return True

            if "/app/ui/root_paketi/akisi_guncelleme/guncelleme_akisi.py" in file_path:
                return True

            return False
        except Exception:
            return True

    def _is_item_from_current_working_file(self, item) -> bool:
        try:
            if item is None:
                return False

            item_file = str(getattr(item, "file_path", "") or "").strip()
            current_file = str(getattr(self, "current_file_path", "") or "").strip()

            if not current_file:
                return False

            current_file = current_file.replace("\\", "/")

            # file_path taşınmadıysa burada direkt red verme.
            if not item_file:
                return True

            item_file = item_file.replace("\\", "/")
            return item_file == current_file
        except Exception:
            return False

    def _resolve_real_target_item(self, item):
        adaylar = []

        if item is not None:
            adaylar.append(item)

        secili = getattr(self, "selected_item", None)
        if secili is not None and secili is not item:
            adaylar.append(secili)

        for aday in adaylar:
            if self._is_invalid_internal_item(aday):
                continue

            aday_path = str(getattr(aday, "path", "") or "").strip()
            aday_file_path = str(getattr(aday, "file_path", "") or "").strip()

            if not aday_path:
                continue

            for current in list(self.items or []):
                current_path = str(getattr(current, "path", "") or "").strip()
                current_file_path = str(getattr(current, "file_path", "") or "").strip()

                if current_path != aday_path:
                    continue

                if self._is_invalid_internal_item(current):
                    continue

                if current_file_path:
                    current_file_path = current_file_path.replace("\\", "/")
                    work_file = str(getattr(self, "current_file_path", "") or "").strip().replace("\\", "/")
                    if work_file and current_file_path != work_file:
                        continue

                if aday_file_path and current_file_path and aday_file_path != current_file_path:
                    continue

                return current

            return aday

        return None

    # =========================================================
    # REFRESH / RESOLVE
    # =========================================================
    def _reload_items_after_update(self) -> None:
        if not self._working_file_ready():
            self.items = []

            try:
                if self.function_list is not None:
                    self.function_list.clear_all()
            except Exception:
                pass

            return

        self.items = self._core().scan_functions_from_file(self.current_file_path)

    def _find_refreshed_item(self, eski_item):
        try:
            if eski_item is None:
                return None

            eski_path = str(getattr(eski_item, "path", "") or "").strip()
            if not eski_path:
                return None

            for current in list(self.items or []):
                current_path = str(getattr(current, "path", "") or "").strip()
                if current_path == eski_path:
                    return current

            return None
        except Exception:
            return None

    def _safe_backup_text(self) -> str:
        try:
            return str(self.current_file_path or "").strip() or "bilinmiyor"
        except Exception:
            return "bilinmiyor"

    # =========================================================
    # APPLY UPDATE
    # =========================================================
    def _apply_selected_function_update(
        self,
        item,
        new_code: str,
        replace_mode: str = "full",
    ) -> None:
        try:
            if self.current_session is None:
                self.set_status_warning("Önce dosya seç.")
                return

            if not self._working_file_ready():
                self.set_status_error(
                    "Çalışma dosyası artık bulunamadı.",
                    detailed_text=(
                        "BASLIK:\nÇalışma Dosyası Bulunamadı\n\n"
                        f"DOSYA:\n{str(self.current_file_path or '').strip() or 'bilinmiyor'}"
                    ),
                    popup_title="Çalışma Dosyası Hatası",
                )
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

            old_source = self._dosya().read_text(self.current_file_path)

            updated_source = self._core().update_function_in_code(
                source_code=old_source,
                target_item=item,
                new_code=new_code,
                replace_mode=replace_mode,
            )

            backup_path = self._belge().guncellenmis_icerigi_kaydet(
                self.current_session,
                updated_source,
            )

            self._reload_items_after_update()

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

            if refreshed is not None:
                self.set_status_success(
                    f"Güncellendi: {refreshed.path} | Yedek: {backup_text}"
                )
            else:
                self.set_status_success(
                    f"Güncellendi. Seçim yenilenemedi ama dosya kaydedildi. Yedek: {backup_text}"
                )

        except ValueError as exc:
            self.set_status_error(
                str(exc),
                detailed_text=self._format_exception_details(
                    exc,
                    title="Güncelleme Hatası",
                ),
                popup_title="Güncelleme Hatası",
            )
        except SyntaxError as exc:
            self.set_status_error(
                f"Sözdizimi hatası: {exc}",
                detailed_text=self._format_exception_details(
                    exc,
                    title="Sözdizimi Hatası",
                ),
                popup_title="Sözdizimi Hatası",
            )
        except Exception as exc:
            self.set_status_error(
                "Güncelleme hatası oluştu.",
                detailed_text=self._format_exception_details(
                    exc,
                    title="Güncelleme Hatası",
                ),
                popup_title="Güncelleme Hatası",
            )
            print(traceback.format_exc())

    # =========================================================
    # PUBLIC API
    # =========================================================
    def update_selected_function(self, item, new_code: str) -> None:
        try:
            if self.current_session is None:
                self.set_status_warning("Önce dosya seç.")
                return

            if not str(new_code or "").strip():
                self.set_status_warning("Yeni fonksiyon kodu boş olamaz.")
                return

            hedef_item = self._resolve_real_target_item(item)

            if (
                self._is_invalid_internal_item(hedef_item)
                or not self._is_item_from_current_working_file(hedef_item)
            ):
                self.set_status_error(
                    "Gerçek hedef fonksiyon seçilemedi.",
                    detailed_text=(
                        "BASLIK:\nSeçim Hatası\n\n"
                        f"GELEN ITEM PATH:\n{str(getattr(item, 'path', '') or '-').strip() or '-'}\n\n"
                        f"GELEN ITEM FILE:\n{str(getattr(item, 'file_path', '') or '-').strip() or '-'}\n\n"
                        f"SELECTED ITEM PATH:\n{str(getattr(getattr(self, 'selected_item', None), 'path', '') or '-').strip() or '-'}\n\n"
                        f"SELECTED ITEM FILE:\n{str(getattr(getattr(self, 'selected_item', None), 'file_path', '') or '-').strip() or '-'}\n\n"
                        f"CURRENT WORK FILE:\n{str(getattr(self, 'current_file_path', '') or '-').strip() or '-'}\n\n"
                        f"TOPLAM ITEM:\n{len(list(self.items or []))}\n\n"
                        "DETAY:\nGüncelleme akışına seçili çalışma dosyası dışından veya uygulama içinden bir fonksiyon geldi."
                    ),
                    popup_title="Seçim Hatası",
                )
                return

            self.selected_item = hedef_item

            self._apply_selected_function_update(
                item=hedef_item,
                new_code=new_code,
                replace_mode="full",
            )

        except Exception as exc:
            self.set_status_error(
                "Güncelleme hazırlık hatası oluştu.",
                detailed_text=self._format_exception_details(
                    exc,
                    title="Güncelleme Hazırlık Hatası",
                ),
                popup_title="Güncelleme Hazırlık Hatası",
            )
            print(traceback.format_exc())
