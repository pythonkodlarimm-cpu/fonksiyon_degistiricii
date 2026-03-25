# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/root_paketi/akisi_guncelleme/guncelleme_akisi.py

ROL:
- Seçili fonksiyonun güncelleme akışını yönetmek
- Güncellenmiş içeriği belge katmanı üzerinden kaydetmek
- Güncelleme sonrası UI ve seçim durumunu senkronize etmek
- Hata durumunda detaylı, kopyalanabilir hata bilgisini iletmek
- Hedef seçimin gerçekten çalışma dosyasına ait olup olmadığını doğrulamak
- Aktif dile göre kullanıcıya görünen metinleri üretmek
- Kullanıcı gerçekten bu dosyayı seçtiyse uygulama içi dosyaların da güncellenebilmesini desteklemek

MİMARİ:
- SADECE yöneticiler kullanılır
- Eski dict/fallback yapı kaldırıldı
- Analiz, belge, dosya, servis ve core katmanları yöneticiler üzerinden çağrılır
- UI davranışı korunur
- Root paketinin alt güncelleme akışı modülüdür
- Güncelleme akışı sade ve deterministik tutulur
- Seçili fonksiyon komple değiştirilir
- Kullanıcıya görünen metinler _m() üzerinden çözülür
- Hardcoded kullanıcı metni bırakılmaz

API UYUMLULUK:
- Android SAF + content URI uyumlu
- API 35 uyumlu
- APK / AAB davranış farkını azaltacak izole akış sağlar

SURUM: 13
TARIH: 2026-03-24
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

    def _m(self, anahtar: str, default: str = "") -> str:
        try:
            if hasattr(self, "services") and self.services is not None:
                return str(self.services.metin(anahtar, default) or default or anahtar)
        except Exception:
            pass
        return str(default or anahtar)

    def _debug(self, message: str) -> None:
        try:
            print(f"[ROOT_GUNCELLEME_AKISI] {message}")
        except Exception:
            pass

    def _normalize_path(self, value) -> str:
        try:
            return str(value or "").strip().replace("\\", "/")
        except Exception:
            return ""

    def _is_invalid_internal_item(self, item) -> bool:
        """
        Önceki sürümde uygulamanın kendi dosyaları doğrudan engelleniyordu.
        Bu da kullanıcı gerçekten bu dosyaları seçtiğinde güncellemeyi bozuyordu.

        Yeni mantık:
        - item None ise geçersiz
        - path boşsa geçersiz
        - bunun dışında dosyanın uygulama içinden gelmesi tek başına geçersiz sayılmaz
        """
        try:
            if item is None:
                return True

            path_value = str(getattr(item, "path", "") or "").strip()
            if not path_value:
                return True

            return False
        except Exception:
            return True

    def _is_item_from_current_working_file(self, item) -> bool:
        try:
            if item is None:
                return False

            item_file = self._normalize_path(getattr(item, "file_path", ""))
            current_file = self._normalize_path(getattr(self, "current_file_path", ""))

            if not current_file:
                return False

            if not item_file:
                return True

            return item_file == current_file
        except Exception:
            return False

    def _resolve_real_target_item(self, item):
        """
        Hedef item çözümleme akışı:
        1) Gelen item ve selected_item aday kabul edilir
        2) Önce mevcut taranmış self.items içinden aynı path + aynı çalışma dosyası eşleşmesi aranır
        3) Bulunamazsa ama aday geçerli ve current working file ile uyumluysa adayın kendisi döner
        """
        adaylar = []

        if item is not None:
            adaylar.append(item)

        secili = getattr(self, "selected_item", None)
        if secili is not None and secili is not item:
            adaylar.append(secili)

        work_file = self._normalize_path(getattr(self, "current_file_path", ""))

        for aday in adaylar:
            if self._is_invalid_internal_item(aday):
                continue

            aday_path = str(getattr(aday, "path", "") or "").strip()
            aday_file_path = self._normalize_path(getattr(aday, "file_path", ""))

            if not aday_path:
                continue

            for current in list(self.items or []):
                try:
                    if self._is_invalid_internal_item(current):
                        continue

                    current_path = str(getattr(current, "path", "") or "").strip()
                    current_file_path = self._normalize_path(
                        getattr(current, "file_path", "")
                    )

                    if current_path != aday_path:
                        continue

                    if work_file and current_file_path and current_file_path != work_file:
                        continue

                    if aday_file_path and current_file_path:
                        if aday_file_path != current_file_path:
                            continue

                    return current
                except Exception:
                    continue

            if self._is_item_from_current_working_file(aday):
                return aday

        return None

    def _detail_pair(self, baslik_anahtar: str, baslik_default: str, deger) -> str:
        return (
            f"{self._m(baslik_anahtar, baslik_default)}:\n"
            f"{str(deger or '').strip() or '-'}"
        )

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

            eski_file = self._normalize_path(getattr(eski_item, "file_path", ""))

            for current in list(self.items or []):
                current_path = str(getattr(current, "path", "") or "").strip()
                current_file = self._normalize_path(getattr(current, "file_path", ""))

                if current_path != eski_path:
                    continue

                if eski_file and current_file and eski_file != current_file:
                    continue

                return current

            return None
        except Exception:
            return None

    def _safe_backup_text(self) -> str:
        try:
            return (
                str(self.current_file_path or "").strip()
                or self._m("unknown", "bilinmiyor")
            )
        except Exception:
            return self._m("unknown", "bilinmiyor")

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
                self.set_status_warning(
                    self._m("select_file_first_short", "Önce dosya seç.")
                )
                return

            if not self._working_file_ready():
                self.set_status_error(
                    self._m(
                        "working_file_not_found_anymore",
                        "Çalışma dosyası artık bulunamadı.",
                    ),
                    detailed_text=(
                        f"{self._m('title', 'BASLIK')}:\n"
                        f"{self._m('working_file_not_found_title', 'Çalışma Dosyası Bulunamadı')}\n\n"
                        f"{self._m('file', 'DOSYA')}:\n"
                        f"{str(self.current_file_path or '').strip() or self._m('unknown', 'bilinmiyor')}"
                    ),
                    popup_title=self._m(
                        "working_file_error_title",
                        "Çalışma Dosyası Hatası",
                    ),
                )
                return

            if item is None:
                self.set_status_warning(
                    self._m("select_function_first_short", "Önce bir fonksiyon seç.")
                )
                return

            if not str(new_code or "").strip():
                self.set_status_warning(
                    self._m(
                        "new_function_code_cannot_be_empty",
                        "Yeni fonksiyon kodu boş olamaz.",
                    )
                )
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
                    self._m(
                        "updated_with_backup_info",
                        "Güncellendi: {path} | Yedek: {backup}",
                    )
                    .replace("{path}", str(getattr(refreshed, "path", "") or ""))
                    .replace("{backup}", backup_text)
                )
            else:
                self.set_status_success(
                    self._m(
                        "updated_selection_not_refreshed_but_saved",
                        "Güncellendi. Seçim yenilenemedi ama dosya kaydedildi. Yedek: {backup}",
                    ).replace("{backup}", backup_text)
                )

            try:
                if hasattr(self, "_ensure_banner_visibility"):
                    from kivy.clock import Clock
                    Clock.schedule_once(self._ensure_banner_visibility, 0.30)
                    Clock.schedule_once(self._ensure_banner_visibility, 1.00)
            except Exception:
                pass

        except ValueError as exc:
            self.set_status_error(
                str(exc),
                detailed_text=self._format_exception_details(
                    exc,
                    title=self._m("update_error_title", "Güncelleme Hatası"),
                ),
                popup_title=self._m("update_error_title", "Güncelleme Hatası"),
            )
        except SyntaxError as exc:
            self.set_status_error(
                self._m(
                    "syntax_error_prefix",
                    "Sözdizimi hatası: {error}",
                ).replace("{error}", str(exc)),
                detailed_text=self._format_exception_details(
                    exc,
                    title=self._m("syntax_error_title", "Sözdizimi Hatası"),
                ),
                popup_title=self._m("syntax_error_title", "Sözdizimi Hatası"),
            )
        except Exception as exc:
            self.set_status_error(
                self._m("update_error_occurred", "Güncelleme hatası oluştu."),
                detailed_text=self._format_exception_details(
                    exc,
                    title=self._m("update_error_title", "Güncelleme Hatası"),
                ),
                popup_title=self._m("update_error_title", "Güncelleme Hatası"),
            )
            print(traceback.format_exc())

    # =========================================================
    # PUBLIC API
    # =========================================================
    def update_selected_function(self, item, new_code: str) -> None:
        try:
            if self.current_session is None:
                self.set_status_warning(
                    self._m("select_file_first_short", "Önce dosya seç.")
                )
                return

            if not str(new_code or "").strip():
                self.set_status_warning(
                    self._m(
                        "new_function_code_cannot_be_empty",
                        "Yeni fonksiyon kodu boş olamaz.",
                    )
                )
                return

            hedef_item = self._resolve_real_target_item(item)

            if (
                self._is_invalid_internal_item(hedef_item)
                or not self._is_item_from_current_working_file(hedef_item)
            ):
                self.set_status_error(
                    self._m(
                        "real_target_function_could_not_be_selected",
                        "Gerçek hedef fonksiyon seçilemedi.",
                    ),
                    detailed_text="\n\n".join(
                        [
                            f"{self._m('title', 'BASLIK')}:\n"
                            f"{self._m('selection_error_title', 'Seçim Hatası')}",
                            self._detail_pair(
                                "incoming_item_path_label",
                                "GELEN ITEM PATH",
                                str(getattr(item, "path", "") or "-"),
                            ),
                            self._detail_pair(
                                "incoming_item_file_label",
                                "GELEN ITEM FILE",
                                str(getattr(item, "file_path", "") or "-"),
                            ),
                            self._detail_pair(
                                "selected_item_path_label",
                                "SELECTED ITEM PATH",
                                str(
                                    getattr(
                                        getattr(self, "selected_item", None),
                                        "path",
                                        "",
                                    )
                                    or "-"
                                ),
                            ),
                            self._detail_pair(
                                "selected_item_file_label",
                                "SELECTED ITEM FILE",
                                str(
                                    getattr(
                                        getattr(self, "selected_item", None),
                                        "file_path",
                                        "",
                                    )
                                    or "-"
                                ),
                            ),
                            self._detail_pair(
                                "current_work_file_label",
                                "CURRENT WORK FILE",
                                str(getattr(self, "current_file_path", "") or "-"),
                            ),
                            self._detail_pair(
                                "total_item_count_label",
                                "TOPLAM ITEM",
                                len(list(self.items or [])),
                            ),
                            f"{self._m('detail', 'DETAY')}:\n"
                            f"{self._m('update_flow_wrong_target_detail', 'Güncelleme akışına seçili çalışma dosyası dışından veya uygulama içinden bir fonksiyon geldi.')}",
                        ]
                    ),
                    popup_title=self._m("selection_error_title", "Seçim Hatası"),
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
                self._m(
                    "update_prepare_error_occurred",
                    "Güncelleme hazırlık hatası oluştu.",
                ),
                detailed_text=self._format_exception_details(
                    exc,
                    title=self._m(
                        "update_prepare_error_title",
                        "Güncelleme Hazırlık Hatası",
                    ),
                ),
                popup_title=self._m(
                    "update_prepare_error_title",
                    "Güncelleme Hazırlık Hatası",
                ),
            )
            print(traceback.format_exc())
