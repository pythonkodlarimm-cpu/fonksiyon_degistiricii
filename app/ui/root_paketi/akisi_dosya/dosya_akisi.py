# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/root_paketi/akisi_dosya/dosya_akisi.py

ROL:
- Dosya seçimi sonrası belge oturumu başlatır
- Çalışma kopyasını doğrular
- Çalışma dosyasından fonksiyonları yeniden tarar
- Tarama / yenileme akışını tek yerde toplar
- Tarama göstergesi overlay akışını yönetir
- Ağır tarama işini UI thread'ini bloklamadan yürütür
- Geçiş reklamı / liste açılışı öncesi bekleyen tarama sonucunu hazırlar
- Restore / resume durumlarında mevcut session üzerinden devam edebilir

MİMARİ:
- Root mixin yapısındadır
- UI güncellemesi ana thread'e döner
- Ağır tarama işini worker thread yapar
- Yeni gerçek seçim varsa onu önceliklendirir
- Gerçek seçim yoksa mevcut session/current_file_path fallback olarak kullanılabilir
- Çeviri metinleri root üzerindeki self._m(...) hattından alınır

SURUM: 23
TARIH: 2026-03-27
IMZA: FY.
"""

from __future__ import annotations

from pathlib import Path
from threading import Thread

from kivy.clock import Clock


class RootDosyaAkisiMixin:
    def _services(self):
        return self._get_services_yoneticisi()

    def _belge(self):
        services = self._services()
        if services is None:
            return None
        return services.belge_yoneticisi()

    def _core(self):
        return self._get_core_yoneticisi()

    def _ceviri(self, anahtar: str, varsayilan: str) -> str:
        try:
            metod = getattr(self, "_m", None)
            if callable(metod):
                return str(metod(anahtar, varsayilan) or varsayilan)
        except Exception:
            pass
        return str(varsayilan)

    def _debug_scan(self, message: str) -> None:
        try:
            print("[ROOT_DOSYA_AKISI]", str(message))
        except Exception:
            pass

    def _ensure_scan_state(self) -> None:
        if not hasattr(self, "_scan_in_progress"):
            self._scan_in_progress = False

        if not hasattr(self, "_pending_scan_result"):
            self._pending_scan_result = None

        if not hasattr(self, "_pending_scan_item_count"):
            self._pending_scan_item_count = 0

        if not hasattr(self, "_pending_scan_display_name"):
            self._pending_scan_display_name = ""

        if not hasattr(self, "_pending_scan_ready"):
            self._pending_scan_ready = False

    def _safe_path_text(self, value) -> str:
        try:
            return str(value or "").strip()
        except Exception:
            return ""

    def _safe_exists_file(self, value) -> bool:
        try:
            yol = Path(str(value or "").strip())
            return yol.exists() and yol.is_file()
        except Exception:
            return False

    def _safe_display_name_from_path(self, value: str) -> str:
        try:
            return Path(str(value or "").strip()).name
        except Exception:
            return ""

    def _selection_identity(self, selection) -> str:
        if selection is None:
            return ""

        for alan in ("uri", "local_path", "display_name"):
            try:
                deger = getattr(selection, alan, None)
                metin = self._safe_path_text(deger)
                if metin:
                    return metin
            except Exception:
                continue

        return ""

    def _current_session_identity(self) -> str:
        try:
            if self.current_session is None:
                return ""

            belge = self._belge()
            if belge is None:
                return ""

            kimlik = belge.oturum_identifier(self.current_session)
            return self._safe_path_text(kimlik)
        except Exception:
            return ""

    def _show_scan_loading(
        self,
        title: str = "",
        detail: str = "",
    ) -> None:
        baslik = title or self._ceviri("scan_in_progress", "Taranıyor...")
        detay = detail or self._ceviri(
            "functions_analyzing",
            "Fonksiyonlar analiz ediliyor",
        )

        try:
            overlay = getattr(self, "tarama_loading_overlay", None)
            if overlay is not None:
                overlay.show(title=str(baslik), detail=str(detay))
        except Exception as exc:
            self._debug_scan(f"loading overlay show hatası: {exc}")

    def _hide_scan_loading(self) -> None:
        try:
            overlay = getattr(self, "tarama_loading_overlay", None)
            if overlay is not None:
                overlay.hide_immediately()
        except Exception:
            pass

    def _show_scan_success(self, item_count: int = 0) -> None:
        try:
            overlay = getattr(self, "tarama_success_overlay", None)
            if overlay is None:
                return

            if int(item_count or 0) > 0:
                detay = self._ceviri(
                    "functions_found_count",
                    f"{int(item_count)} fonksiyon bulundu",
                )
            else:
                detay = self._ceviri(
                    "function_list_preparing",
                    "Fonksiyon listesi hazırlanıyor",
                )

            overlay.show_then_hide(
                title=self._ceviri("scan_completed", "Tarama tamamlandı"),
                detail=detay,
                duration=0.65,
            )
        except Exception:
            pass

    def _scan_finish_success_visual(self, item_count: int = 0) -> None:
        try:
            overlay = getattr(self, "tarama_loading_overlay", None)
            if overlay is not None and hasattr(overlay, "finish_and_hide"):
                overlay.finish_and_hide(
                    on_done=lambda: self._show_scan_success(item_count=item_count)
                )
                return
        except Exception:
            pass

        try:
            self._hide_scan_loading()
        except Exception:
            pass

        try:
            self._show_scan_success(item_count=item_count)
        except Exception:
            pass

    def _scan_finish_error_visual(self) -> None:
        try:
            self._hide_scan_loading()
        except Exception:
            pass

    def _clear_pending_scan_transition(self) -> None:
        self._ensure_scan_state()
        self._pending_scan_result = None
        self._pending_scan_item_count = 0
        self._pending_scan_display_name = ""
        self._pending_scan_ready = False

    def _prepare_pending_scan_transition(
        self,
        result: dict,
        item_count: int,
        display_name: str = "",
    ) -> None:
        self._ensure_scan_state()
        self._pending_scan_result = dict(result or {})
        self._pending_scan_item_count = int(item_count or 0)
        self._pending_scan_display_name = str(display_name or "").strip()
        self._pending_scan_ready = True

    def _open_function_list_directly(self) -> None:
        try:
            if self.function_list is not None:
                self.function_list.set_items(self.items)
        except Exception:
            pass

        try:
            Clock.schedule_once(lambda *_: self._scroll_to_function_list(), 0.10)
        except Exception:
            pass

    def _notify_scan_transition_ready(self, item_count: int, display_name: str) -> bool:
        try:
            hook = getattr(self, "_on_scan_transition_ready", None)
            if callable(hook):
                hook(
                    item_count=int(item_count or 0),
                    display_name=str(display_name or "").strip(),
                )
                return True
        except Exception as exc:
            self._debug_scan(f"_on_scan_transition_ready hatası: {exc}")

        try:
            hook = getattr(self, "scan_transition_ready", None)
            if callable(hook):
                hook(
                    item_count=int(item_count or 0),
                    display_name=str(display_name or "").strip(),
                )
                return True
        except Exception as exc:
            self._debug_scan(f"scan_transition_ready hatası: {exc}")

        return False

    def _working_file_ready(self) -> bool:
        try:
            if self.current_session is None:
                return False

            belge = self._belge()
            if belge is None:
                return False

            calisma_yolu = self._safe_path_text(
                belge.calisma_dosyasi_yolu(self.current_session)
            )

            if calisma_yolu:
                self.current_file_path = calisma_yolu

            if not self._safe_path_text(self.current_file_path):
                return False

            return bool(belge.calisma_kopyasi_var_mi(self.current_session))
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
            self.items = self._core().scan_functions_from_file(self.current_file_path)
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
            if self.dosya_secici is not None and hasattr(self.dosya_secici, "get_selection"):
                secim = self.dosya_secici.get_selection()
                if secim is not None:
                    return secim
        except Exception:
            pass

        try:
            if self.dosya_secici is not None:
                for attr_name in (
                    "_selection",
                    "selection",
                    "_secim",
                    "secim",
                    "_current_selection",
                ):
                    try:
                        secim = getattr(self.dosya_secici, attr_name, None)
                        if secim is not None:
                            return secim
                    except Exception:
                        continue
        except Exception:
            pass

        try:
            if self.dosya_secici is not None and hasattr(self.dosya_secici, "get_path"):
                ham_yol = self._safe_path_text(self.dosya_secici.get_path())
                if ham_yol and self._safe_exists_file(ham_yol):
                    DocumentSelection = self._get_document_selection_class()
                    return DocumentSelection(
                        source="filesystem",
                        uri="",
                        local_path=ham_yol,
                        display_name=Path(ham_yol).name,
                        mime_type="",
                    )
        except Exception:
            pass

        return None

    def _selection_from_file_path(self, file_path: str):
        temiz_yol = self._safe_path_text(file_path)
        if not temiz_yol:
            return None

        try:
            yol = Path(temiz_yol)
            if not yol.exists() or not yol.is_file():
                return None

            DocumentSelection = self._get_document_selection_class()
            return DocumentSelection(
                source="filesystem",
                uri="",
                local_path=str(yol),
                display_name=yol.name,
                mime_type="",
            )
        except Exception:
            return None

    def _selection_from_current_session(self):
        try:
            if self.current_session is not None:
                belge = self._belge()
                if belge is None:
                    return None

                kaynak_kimligi = self._safe_path_text(
                    belge.oturum_identifier(self.current_session)
                )
                gosterim_adi = self._safe_path_text(
                    belge.oturum_display_name(self.current_session)
                )
                calisma_yolu = self._safe_path_text(
                    belge.calisma_dosyasi_yolu(self.current_session)
                )

                if kaynak_kimligi or calisma_yolu:
                    DocumentSelection = self._get_document_selection_class()
                    return DocumentSelection(
                        source="session_restore",
                        uri=kaynak_kimligi if not self._safe_exists_file(kaynak_kimligi) else "",
                        local_path=calisma_yolu if self._safe_exists_file(calisma_yolu) else "",
                        display_name=gosterim_adi or self._safe_display_name_from_path(calisma_yolu),
                        mime_type="",
                    )
        except Exception:
            pass

        try:
            if self._safe_exists_file(self.current_file_path):
                return self._selection_from_file_path(self.current_file_path)
        except Exception:
            pass

        return None

    def _resolve_scan_selection(self, file_path: str = ""):
        selection = self._selection_from_ui()
        if selection is not None:
            return selection

        selection = self._selection_from_file_path(file_path)
        if selection is not None:
            return selection

        selection = self._selection_from_current_session()
        if selection is not None:
            return selection

        return None

    def _new_selection_requested(self, selection, file_path: str = "") -> bool:
        """
        Yeni gerçek seçim isteği varsa bunu mevcut session fallback'inden ayırır.
        """
        ui_selection = self._selection_from_ui()
        if ui_selection is not None:
            ui_id = self._selection_identity(ui_selection)
            session_id = self._current_session_identity()
            return bool(ui_id and ui_id != session_id)

        temiz_yol = self._safe_path_text(file_path)
        if temiz_yol:
            mevcut_yol = self._safe_path_text(self.current_file_path)
            return temiz_yol != mevcut_yol

        return False

    def _reset_before_new_scan(self) -> None:
        """
        Yeni dosya taraması öncesi önceki session ve seçim state'ini sıfırlar.
        """
        try:
            self.current_session = None
        except Exception:
            pass

        try:
            self.current_file_path = ""
        except Exception:
            pass

        try:
            self.items = []
        except Exception:
            pass

        try:
            self.selected_item = None
        except Exception:
            pass

        try:
            self._clear_pending_scan_transition()
        except Exception:
            pass

        try:
            if hasattr(self, "_editor_state_cache_temizle"):
                self._editor_state_cache_temizle()
        except Exception:
            pass

        try:
            if hasattr(self, "_app_state_cache_temizle"):
                self._app_state_cache_temizle()
        except Exception:
            pass

        try:
            if self.function_list is not None:
                self.function_list.clear_all()
        except Exception:
            pass

        try:
            if self.editor is not None:
                if hasattr(self.editor, "clear_all"):
                    self.editor.clear_all()
                elif hasattr(self.editor, "clear_selection"):
                    self.editor.clear_selection()
        except Exception:
            pass

        try:
            self._reset_selection_only()
        except Exception:
            pass

    def _scan_from_existing_session_worker(self) -> dict:
        try:
            if not self._working_file_ready():
                return {
                    "ok": False,
                    "kind": "warning",
                    "message": self._ceviri("file_not_selected", "Dosya seçilmedi."),
                }

            calisma_yolu = self._safe_path_text(self.current_file_path)
            if not calisma_yolu:
                return {
                    "ok": False,
                    "kind": "warning",
                    "message": self._ceviri("file_not_selected", "Dosya seçilmedi."),
                }

            session = self.current_session
            belge = self._belge()
            if belge is None:
                return {
                    "ok": False,
                    "kind": "error",
                    "message": self._ceviri("session_start_failed", "Oturum başlatılamadı."),
                }

            gosterim_adi = ""
            kaynak_kimligi = ""

            try:
                if session is not None:
                    gosterim_adi = self._safe_path_text(belge.oturum_display_name(session))
                    kaynak_kimligi = self._safe_path_text(belge.oturum_identifier(session))
            except Exception:
                pass

            items = self._core().scan_functions_from_file(calisma_yolu)

            return {
                "ok": True,
                "selection": self._selection_from_ui() or self._selection_from_current_session(),
                "session": session,
                "calisma_yolu": calisma_yolu,
                "kaynak_kimligi": kaynak_kimligi,
                "gosterim_adi": gosterim_adi,
                "items": list(items or []),
                "used_existing_session": True,
            }
        except Exception as exc:
            return {
                "ok": False,
                "kind": "error",
                "message": f"{self._ceviri('scan_error', 'Tarama hatası oluştu')}: {exc}",
                "detail": self._format_exception_details(exc, title="Tarama Hatası"),
                "popup_title": self._ceviri("scan_error_title", "Tarama Hatası"),
            }

    def _scan_or_refresh_worker(self, selection) -> dict:
        if selection is None:
            return {
                "ok": False,
                "kind": "warning",
                "message": self._ceviri("file_not_selected", "Dosya seçilmedi."),
            }

        belge = self._belge()
        if belge is None:
            return {
                "ok": False,
                "kind": "error",
                "message": self._ceviri("session_start_failed", "Oturum başlatılamadı."),
            }

        try:
            session = belge.oturum_baslat(selection)
        except Exception as exc:
            return {
                "ok": False,
                "kind": "error",
                "message": f"{self._ceviri('session_start_failed', 'Oturum başlatılamadı')}: {exc}",
                "detail": self._format_exception_details(
                    exc,
                    title=self._ceviri("session_start_error_title", "Oturum Başlatma Hatası"),
                ),
                "popup_title": self._ceviri("session_start_error_title", "Oturum Başlatma Hatası"),
            }

        calisma_yolu = self._safe_path_text(belge.calisma_dosyasi_yolu(session))
        kaynak_kimligi = self._safe_path_text(belge.oturum_identifier(session))
        gosterim_adi = self._safe_path_text(belge.oturum_display_name(session))

        if not calisma_yolu:
            return {
                "ok": False,
                "kind": "error",
                "message": self._ceviri(
                    "working_file_not_created",
                    "Çalışma dosyası oluşturulamadı.",
                ),
                "detail": (
                    f"BASLIK:\n{self._ceviri('working_file_error_title', 'Çalışma Dosyası Hatası')}\n\n"
                    f"DETAY:\n{self._ceviri('working_file_path_empty', 'Belge oturumu oluştu ancak çalışma dosyası yolu boş geldi.')}\n\n"
                    f"KAYNAK KİMLİĞİ:\n{kaynak_kimligi or 'bilinmiyor'}\n\n"
                    f"BELGE:\n{gosterim_adi or 'bilinmiyor'}"
                ),
                "popup_title": self._ceviri("working_file_error_title", "Çalışma Dosyası Hatası"),
            }

        try:
            if not belge.calisma_kopyasi_var_mi(session):
                return {
                    "ok": False,
                    "kind": "error",
                    "message": self._ceviri(
                        "working_copy_missing",
                        "Çalışma dosyası bulunamadı.",
                    ),
                    "detail": (
                        f"BASLIK:\n{self._ceviri('working_copy_error_title', 'Çalışma Kopyası Hatası')}\n\n"
                        f"DOSYA:\n{calisma_yolu}\n\n"
                        f"KAYNAK KİMLİĞİ:\n{kaynak_kimligi or 'bilinmiyor'}\n\n"
                        f"BELGE:\n{gosterim_adi or 'bilinmiyor'}"
                    ),
                    "popup_title": self._ceviri("working_copy_error_title", "Çalışma Kopyası Hatası"),
                }
        except Exception as exc:
            return {
                "ok": False,
                "kind": "error",
                "message": f"{self._ceviri('working_copy_validate_failed', 'Çalışma kopyası doğrulanamadı')}: {exc}",
                "detail": self._format_exception_details(
                    exc,
                    title=self._ceviri(
                        "working_copy_validate_error_title",
                        "Çalışma Kopyası Doğrulama Hatası",
                    ),
                ),
                "popup_title": self._ceviri(
                    "working_copy_validate_error_title",
                    "Çalışma Kopyası Doğrulama Hatası",
                ),
            }

        try:
            items = self._core().scan_functions_from_file(calisma_yolu)
        except Exception as exc:
            return {
                "ok": False,
                "kind": "error",
                "message": f"{self._ceviri('scan_error', 'Tarama hatası oluştu')}: {exc}",
                "detail": self._format_exception_details(
                    exc,
                    title=self._ceviri("scan_error_title", "Tarama Hatası"),
                ),
                "popup_title": self._ceviri("scan_error_title", "Tarama Hatası"),
            }

        return {
            "ok": True,
            "selection": selection,
            "session": session,
            "calisma_yolu": calisma_yolu,
            "kaynak_kimligi": kaynak_kimligi,
            "gosterim_adi": gosterim_adi,
            "items": list(items or []),
            "used_existing_session": False,
        }

    def _apply_scan_result(self, result: dict) -> None:
        self._ensure_scan_state()
        self._scan_in_progress = False

        if not result.get("ok"):
            self._scan_finish_error_visual()
            self._clear_pending_scan_transition()
            self._clear_state()

            kind = self._safe_path_text(result.get("kind", "")).lower()
            message = self._safe_path_text(result.get("message", ""))
            detail = self._safe_path_text(result.get("detail", ""))
            popup_title = self._safe_path_text(result.get("popup_title", ""))

            if kind == "warning":
                self.set_status_warning(
                    message or self._ceviri("file_not_selected", "Dosya seçilmedi.")
                )
                return

            self.set_status_error(
                message or self._ceviri("scan_error", "Tarama hatası oluştu."),
                detailed_text=detail,
                popup_title=popup_title or self._ceviri("scan_error_title", "Tarama Hatası"),
            )
            return

        selection = result.get("selection")
        session = result.get("session")
        calisma_yolu = self._safe_path_text(result.get("calisma_yolu", ""))
        kaynak_kimligi = self._safe_path_text(result.get("kaynak_kimligi", ""))
        gosterim_adi = self._safe_path_text(result.get("gosterim_adi", ""))
        items = list(result.get("items") or [])
        item_count = len(items)
        used_existing_session = bool(result.get("used_existing_session", False))

        self._clear_view_only()

        if session is not None:
            self.current_session = session

        self.current_file_path = calisma_yolu
        self.items = items

        try:
            if self.dosya_secici is not None:
                if kaynak_kimligi or calisma_yolu:
                    self.dosya_secici.set_path(kaynak_kimligi or calisma_yolu)

                if selection is not None and hasattr(self.dosya_secici, "set_selection"):
                    self.dosya_secici.set_selection(selection)
        except Exception:
            pass

        try:
            if self.function_list is not None:
                self.function_list.clear_all()
        except Exception as exc:
            self._scan_finish_error_visual()
            self.set_status_error(
                self._ceviri(
                    "function_list_prepare_failed",
                    "Fonksiyon listesi geçiş için hazırlanırken hata oluştu.",
                ),
                detailed_text=self._format_exception_details(
                    exc,
                    title=self._ceviri(
                        "function_list_prepare_error_title",
                        "Fonksiyon Listesi Hazırlama Hatası",
                    ),
                ),
                popup_title=self._ceviri(
                    "function_list_prepare_error_title",
                    "Fonksiyon Listesi Hazırlama Hatası",
                ),
            )
            return

        self._reset_selection_only()
        self._prepare_pending_scan_transition(
            result=result,
            item_count=item_count,
            display_name=gosterim_adi,
        )

        if gosterim_adi:
            if used_existing_session:
                self.set_status_success(
                    self._ceviri(
                        "session_preserved_scan_ready",
                        f"Oturum korundu. {item_count} fonksiyon hazır. Belge: {gosterim_adi}",
                    )
                )
            else:
                self.set_status_success(
                    self._ceviri(
                        "scan_completed_count_with_doc",
                        f"Tarama tamamlandı. {item_count} fonksiyon bulundu. Belge: {gosterim_adi}",
                    )
                )
        else:
            if used_existing_session:
                self.set_status_success(
                    self._ceviri(
                        "session_preserved_scan_ready_no_doc",
                        f"Oturum korundu. {item_count} fonksiyon hazır.",
                    )
                )
            else:
                self.set_status_success(
                    self._ceviri(
                        "scan_completed_count",
                        f"Tarama tamamlandı. {item_count} fonksiyon bulundu.",
                    )
                )

        self._scan_finish_success_visual(item_count=item_count)

        if self._notify_scan_transition_ready(
            item_count=item_count,
            display_name=gosterim_adi,
        ):
            return

        self._open_function_list_directly()

    def _start_scan_or_refresh(self, file_path: str = "") -> None:
        self._ensure_scan_state()

        if self._scan_in_progress:
            self._debug_scan("Tarama zaten sürüyor. Yeni istek yok sayıldı.")
            return

        yeni_secim_istendi = False
        selection = None

        try:
            selection = self._resolve_scan_selection(file_path=file_path)
            yeni_secim_istendi = self._new_selection_requested(selection, file_path=file_path)
        except Exception:
            selection = None
            yeni_secim_istendi = False

        if yeni_secim_istendi:
            self._debug_scan("Yeni dosya seçimi algılandı. Eski session temizleniyor.")
            self._reset_before_new_scan()

            try:
                selection = self._resolve_scan_selection(file_path=file_path)
            except Exception:
                selection = None

        mevcut_session_korunabilir = False
        if not yeni_secim_istendi:
            try:
                mevcut_session_korunabilir = self._working_file_ready()
            except Exception:
                mevcut_session_korunabilir = False

        self._scan_in_progress = True
        self._clear_pending_scan_transition()

        self._show_scan_loading(
            title=self._ceviri("scan_in_progress", "Taranıyor..."),
            detail=self._ceviri("functions_analyzing", "Fonksiyonlar analiz ediliyor"),
        )

        def _worker():
            try:
                if mevcut_session_korunabilir:
                    result = self._scan_from_existing_session_worker()
                else:
                    result = self._scan_or_refresh_worker(selection)
            except Exception as exc:
                result = {
                    "ok": False,
                    "kind": "error",
                    "message": f"{self._ceviri('scan_error', 'Tarama hatası oluştu')}: {exc}",
                    "detail": self._format_exception_details(
                        exc,
                        title=self._ceviri("scan_error_title", "Tarama Hatası"),
                    ),
                    "popup_title": self._ceviri("scan_error_title", "Tarama Hatası"),
                }

            Clock.schedule_once(lambda *_: self._apply_scan_result(result), 0)

        try:
            Thread(target=_worker, daemon=True).start()
        except Exception as exc:
            self._scan_in_progress = False
            self._scan_finish_error_visual()
            self._clear_pending_scan_transition()
            self.set_status_error(
                f"{self._ceviri('scan_start_failed', 'Tarama başlatılamadı')}: {exc}",
                detailed_text=self._format_exception_details(
                    exc,
                    title=self._ceviri("scan_start_error_title", "Tarama Başlatma Hatası"),
                ),
                popup_title=self._ceviri("scan_start_error_title", "Tarama Başlatma Hatası"),
            )

    def refresh_file(self, file_path: str) -> None:
        try:
            self._start_scan_or_refresh(file_path)
        except Exception as exc:
            self._ensure_scan_state()
            self._scan_in_progress = False
            self._clear_pending_scan_transition()
            self._clear_state()
            self._scan_finish_error_visual()
            self.set_status_error(
                f"{self._ceviri('refresh_error', 'Yenileme hatası oluştu')}: {exc}",
                detailed_text=self._format_exception_details(
                    exc,
                    title=self._ceviri("refresh_error_title", "Yenileme Hatası"),
                ),
                popup_title=self._ceviri("refresh_error_title", "Yenileme Hatası"),
            )

    def scan_file(self, file_path: str) -> None:
        try:
            self._start_scan_or_refresh(file_path)
        except Exception as exc:
            self._ensure_scan_state()
            self._scan_in_progress = False
            self._clear_pending_scan_transition()
            self._clear_state()
            self._scan_finish_error_visual()
            self.set_status_error(
                f"{self._ceviri('scan_error', 'Tarama hatası oluştu')}: {exc}",
                detailed_text=self._format_exception_details(
                    exc,
                    title=self._ceviri("scan_error_title", "Tarama Hatası"),
                ),
                popup_title=self._ceviri("scan_error_title", "Tarama Hatası"),
      )
