# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/root_paketi/akisi_dosya/dosya_akisi.py

ROL:
- Dosya seçimi sonrası belge oturumu başlatmak
- Çalışma kopyasını doğrulamak
- Çalışma dosyasından fonksiyonları yeniden taramak
- Tarama / yenileme akışını tek yerde toplamak
- Hata durumunda detaylı, kopyalanabilir hata bilgisini iletmek
- Tarama göstergesi overlay akışını yönetmek
- Ağır tarama işini UI thread'i bloklamadan yürütmek
- Geçiş reklamı öncesi tarama sonucunu bekleyen state olarak hazırlamak
- Diğer akışların tekrar kullanacağı dosya yenileme yardımcılarını sağlamak
- Arka plan dönüşünde mevcut belge/session varsa onu koruyarak yeniden taramaya yardımcı olmak
- Restore sonrası selection nesnesi eksik olsa bile mevcut session/current_file_path üzerinden
  çalışmayı sürdürebilmek

MİMARİ:
- SADECE CoreYoneticisi, ServicesYoneticisi ve Root bağımlılık katmanı kullanılır
- Eski helper/dict/fallback yapısı yoktur
- UI tamamen servislerden izole tutulur
- Session tabanlı çalışma modeli korunur
- Root paketinin alt akış modülüdür
- Public API korunur
- Arka plan thread'i yalnızca ağır iş yapar, UI güncellemesi ana thread'e döner
- Aynı anda ikinci tarama başlatılmaz
- Başarılı sonuçta loading overlay yavaşlayarak kapanır, sonra success overlay açılır
- Tarama tamamlandıktan sonra fonksiyon listesine geçiş için bekleyen sonuç state'i hazırlanabilir
- Fonksiyon listesi verisi, geçiş tamamlanmadan UI'ye uygulanmaz
- Restore/resume senaryolarında mevcut oturumu gereksiz yere sıfırlamaz
- Önce gerçek selection, sonra session/current_file_path fallback mantığı uygulanır

API UYUMLULUK:
- Android (SAF + content URI) uyumludur
- API 34+ / API 35 güvenlidir
- Public API değiştirilmeden tarama loading / success overlay desteği eklenmiştir
- _reload_items_from_current_file yardımcı API'si korunmuştur

SURUM: 22
TARIH: 2026-03-26
IMZA: FY.
"""

from __future__ import annotations

import traceback
from pathlib import Path
from threading import Thread

from kivy.clock import Clock


class RootDosyaAkisiMixin:
    # =========================================================
    # INTERNAL
    # =========================================================
    def _services(self):
        return self._get_services_yoneticisi()

    def _belge(self):
        return self._services().belge_yoneticisi()

    def _core(self):
        return self._get_core_yoneticisi()

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
            path_obj = Path(str(value or "").strip())
            return path_obj.exists() and path_obj.is_file()
        except Exception:
            return False

    def _safe_display_name_from_path(self, value: str) -> str:
        try:
            return Path(str(value or "").strip()).name
        except Exception:
            return ""

    # =========================================================
    # TARAMA OVERLAY
    # =========================================================
    def _show_scan_loading(
        self,
        title: str = "Taranıyor...",
        detail: str = "Fonksiyonlar analiz ediliyor",
    ) -> None:
        try:
            overlay = getattr(self, "tarama_loading_overlay", None)
            self._debug_scan(f"loading overlay var mı = {overlay is not None}")
            if overlay is not None:
                overlay.show(
                    title=str(title or "Taranıyor..."),
                    detail=str(detail or "Fonksiyonlar analiz ediliyor"),
                )
        except Exception as exc:
            self._debug_scan(f"loading overlay show hatası = {exc}")

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
            if overlay is not None:
                detay = (
                    f"{int(item_count or 0)} fonksiyon bulundu"
                    if int(item_count or 0) > 0
                    else "Fonksiyon listesi hazırlanıyor"
                )
                overlay.show_then_hide(
                    title="Tarama tamamlandı",
                    detail=detay,
                    duration=0.65,
                )
        except Exception:
            pass

    def _scan_finish_success_visual(self, item_count: int = 0) -> None:
        """
        Başarılı durumda loading bir anda kapanmaz.
        Önce yavaşlayarak kapanır, ardından success overlay görünür.
        """
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

    # =========================================================
    # GEÇIŞ HAZIRLAMA
    # =========================================================
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

        self._debug_scan(
            "Geçiş için bekleyen tarama sonucu hazırlandı | "
            f"item_count={self._pending_scan_item_count} "
            f"display_name={self._pending_scan_display_name}"
        )

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
        """
        Root tarafında geçiş CTA / reklam akışı varsa ona devreder.
        Yoksa False döner ve klasik davranış fallback olarak çalışır.
        """
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

    # =========================================================
    # STATE / FILE
    # =========================================================
    def _working_file_ready(self) -> bool:
        try:
            if self.current_session is None:
                return False

            calisma_yolu = str(
                self._belge().calisma_dosyasi_yolu(self.current_session) or ""
            ).strip()

            if calisma_yolu:
                self.current_file_path = calisma_yolu

            if not str(self.current_file_path or "").strip():
                return False

            return bool(self._belge().calisma_kopyasi_var_mi(self.current_session))
        except Exception:
            return False

    def _reload_items_from_current_file(self) -> None:
        """
        Güncel çalışma dosyasını yeniden tarar ve function list ile senkronize eder.
        Bu yardımcı method diğer akışlar tarafından da kullanılabilir.
        """
        if not self._working_file_ready():
            self.items = []

            try:
                if self.function_list is not None:
                    self.function_list.clear_all()
            except Exception:
                pass

            return

        try:
            self.items = self._core().scan_functions_from_file(
                self.current_file_path
            )
        except Exception:
            self.items = []
            raise

        try:
            if self.function_list is not None:
                self.function_list.set_items(self.items)
        except Exception:
            pass

    def _selection_from_ui(self):
        """
        UI üzerindeki gerçek selection nesnesini almaya çalışır.
        """
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
                ham_yol = str(self.dosya_secici.get_path() or "").strip()

                if ham_yol and Path(ham_yol).exists() and Path(ham_yol).is_file():
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
        """
        Dışarıdan gelen file_path değerinden gerekiyorsa geçici seçim nesnesi üretir.
        """
        temiz_yol = self._safe_path_text(file_path)
        if not temiz_yol:
            return None

        try:
            path_obj = Path(temiz_yol)
            if not path_obj.exists() or not path_obj.is_file():
                return None

            DocumentSelection = self._get_document_selection_class()
            return DocumentSelection(
                source="filesystem",
                uri="",
                local_path=str(path_obj),
                display_name=path_obj.name,
                mime_type="",
            )
        except Exception:
            return None

    def _selection_from_current_session(self):
        """
        Mümkünse mevcut session/current_file_path üzerinden geçici selection üretir.
        """
        try:
            if self.current_session is not None:
                belge = self._belge()
                kaynak_kimligi = str(
                    belge.oturum_identifier(self.current_session) or ""
                ).strip()
                gosterim_adi = str(
                    belge.oturum_display_name(self.current_session) or ""
                ).strip()
                calisma_yolu = str(
                    belge.calisma_dosyasi_yolu(self.current_session) or ""
                ).strip()

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
        """
        Tarama için kullanılacak selection nesnesini çözmeye çalışır.

        Öncelik:
        1) dosya_secici üstündeki selection
        2) file_path parametresi
        3) mevcut session/current_file_path
        """
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

    def _scan_from_existing_session_worker(self) -> dict:
        """
        Mevcut session ve çalışma kopyası hazırsa yeni session açmadan yeniden tarar.
        """
        try:
            if not self._working_file_ready():
                return {
                    "ok": False,
                    "kind": "warning",
                    "message": "Dosya seçilmedi.",
                }

            calisma_yolu = self._safe_path_text(self.current_file_path)
            if not calisma_yolu:
                return {
                    "ok": False,
                    "kind": "warning",
                    "message": "Dosya seçilmedi.",
                }

            session = self.current_session
            gosterim_adi = ""
            kaynak_kimligi = ""

            try:
                if session is not None:
                    gosterim_adi = str(
                        self._belge().oturum_display_name(session) or ""
                    ).strip()
                    kaynak_kimligi = str(
                        self._belge().oturum_identifier(session) or ""
                    ).strip()
            except Exception:
                gosterim_adi = ""
                kaynak_kimligi = ""

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
                "message": f"Tarama hatası oluştu: {exc}",
                "detail": self._format_exception_details(
                    exc,
                    title="Tarama Hatası",
                ),
                "popup_title": "Tarama Hatası",
            }

    # =========================================================
    # WORKER LOGIC
    # =========================================================
    def _scan_or_refresh_worker(self, selection) -> dict:
        if selection is None:
            return {
                "ok": False,
                "kind": "warning",
                "message": "Dosya seçilmedi.",
            }

        try:
            session = self._belge().oturum_baslat(selection)
        except Exception as exc:
            return {
                "ok": False,
                "kind": "error",
                "message": f"Oturum başlatılamadı: {exc}",
                "detail": self._format_exception_details(
                    exc,
                    title="Oturum Başlatma Hatası",
                ),
                "popup_title": "Oturum Başlatma Hatası",
            }

        calisma_yolu = str(
            self._belge().calisma_dosyasi_yolu(session) or ""
        ).strip()

        kaynak_kimligi = str(
            self._belge().oturum_identifier(session) or ""
        ).strip()

        gosterim_adi = str(
            self._belge().oturum_display_name(session) or ""
        ).strip()

        if not calisma_yolu:
            return {
                "ok": False,
                "kind": "error",
                "message": "Çalışma dosyası oluşturulamadı.",
                "detail": (
                    "BASLIK:\nÇalışma Dosyası Hatası\n\n"
                    "DETAY:\nBelge oturumu oluştu ancak çalışma dosyası yolu boş geldi.\n\n"
                    f"KAYNAK KİMLİĞİ:\n{kaynak_kimligi or 'bilinmiyor'}\n\n"
                    f"BELGE:\n{gosterim_adi or 'bilinmiyor'}"
                ),
                "popup_title": "Çalışma Dosyası Hatası",
            }

        try:
            if not self._belge().calisma_kopyasi_var_mi(session):
                return {
                    "ok": False,
                    "kind": "error",
                    "message": "Çalışma dosyası bulunamadı.",
                    "detail": (
                        "BASLIK:\nÇalışma Kopyası Bulunamadı\n\n"
                        f"DOSYA:\n{calisma_yolu}\n\n"
                        f"KAYNAK KİMLİĞİ:\n{kaynak_kimligi or 'bilinmiyor'}\n\n"
                        f"BELGE:\n{gosterim_adi or 'bilinmiyor'}"
                    ),
                    "popup_title": "Çalışma Kopyası Hatası",
                }
        except Exception as exc:
            return {
                "ok": False,
                "kind": "error",
                "message": f"Çalışma kopyası doğrulanamadı: {exc}",
                "detail": self._format_exception_details(
                    exc,
                    title="Çalışma Kopyası Doğrulama Hatası",
                ),
                "popup_title": "Çalışma Kopyası Doğrulama Hatası",
            }

        try:
            items = self._core().scan_functions_from_file(calisma_yolu)
        except Exception as exc:
            return {
                "ok": False,
                "kind": "error",
                "message": f"Tarama hatası oluştu: {exc}",
                "detail": self._format_exception_details(
                    exc,
                    title="Tarama Hatası",
                ),
                "popup_title": "Tarama Hatası",
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

    # =========================================================
    # UI APPLY
    # =========================================================
    def _apply_scan_result(self, result: dict) -> None:
        self._ensure_scan_state()
        self._scan_in_progress = False

        if not result.get("ok"):
            self._scan_finish_error_visual()
            self._clear_pending_scan_transition()
            self._clear_state()

            kind = str(result.get("kind", "") or "").strip().lower()
            message = str(result.get("message", "") or "").strip()
            detail = str(result.get("detail", "") or "").strip()
            popup_title = str(result.get("popup_title", "") or "").strip()

            if kind == "warning":
                self.set_status_warning(message or "Dosya seçilmedi.")
                return

            self.set_status_error(
                message or "Tarama hatası oluştu.",
                detailed_text=detail,
                popup_title=popup_title or "Tarama Hatası",
            )
            return

        selection = result.get("selection")
        session = result.get("session")
        calisma_yolu = str(result.get("calisma_yolu", "") or "").strip()
        kaynak_kimligi = str(result.get("kaynak_kimligi", "") or "").strip()
        gosterim_adi = str(result.get("gosterim_adi", "") or "").strip()
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
                print("LISTE GEÇİŞ ÖNCESİ TEMİZLENDİ | item_count =", len(self.items))
            else:
                print("LISTE GEÇİŞ ÖNCESİ TEMİZLENEMEDİ (function_list yok)")
        except Exception as exc:
            self._scan_finish_error_visual()
            self.set_status_error(
                "Fonksiyon listesi geçiş için hazırlanırken hata oluştu.",
                detailed_text=self._format_exception_details(
                    exc,
                    title="Fonksiyon Listesi Hazırlama Hatası",
                ),
                popup_title="Fonksiyon Listesi Hazırlama Hatası",
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
                    f"Oturum korundu. {item_count} fonksiyon hazır. "
                    f"Belge: {gosterim_adi}"
                )
            else:
                self.set_status_success(
                    f"Tarama tamamlandı. {item_count} fonksiyon bulundu. "
                    f"Belge: {gosterim_adi}"
                )
        else:
            if used_existing_session:
                self.set_status_success(
                    f"Oturum korundu. {item_count} fonksiyon hazır."
                )
            else:
                self.set_status_success(
                    f"Tarama tamamlandı. {item_count} fonksiyon bulundu."
                )

        self._scan_finish_success_visual(item_count=item_count)

        if self._notify_scan_transition_ready(
            item_count=item_count,
            display_name=gosterim_adi,
        ):
            return

        self._debug_scan(
            "Geçiş hook bulunamadı. Klasik liste açma davranışına dönülüyor."
        )
        self._open_function_list_directly()

    # =========================================================
    # START
    # =========================================================
    def _start_scan_or_refresh(self, file_path: str = "") -> None:
        self._ensure_scan_state()

        if self._scan_in_progress:
            self._debug_scan("Tarama zaten sürüyor. Yeni istek yok sayıldı.")
            return

        self._scan_in_progress = True
        self._clear_pending_scan_transition()
        self._debug_scan("_start_scan_or_refresh çağrıldı")

        selection = self._resolve_scan_selection(file_path=file_path)
        mevcut_session_korunabilir = self._working_file_ready()

        self._show_scan_loading(
            title="Taranıyor...",
            detail="Fonksiyonlar analiz ediliyor",
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
                    "message": f"Tarama hatası oluştu: {exc}",
                    "detail": self._format_exception_details(
                        exc,
                        title="Tarama Hatası",
                    ),
                    "popup_title": "Tarama Hatası",
                }

            Clock.schedule_once(lambda *_: self._apply_scan_result(result), 0)

        try:
            Thread(target=_worker, daemon=True).start()
        except Exception as exc:
            self._scan_in_progress = False
            self._scan_finish_error_visual()
            self._clear_pending_scan_transition()
            self.set_status_error(
                f"Tarama başlatılamadı: {exc}",
                detailed_text=self._format_exception_details(
                    exc,
                    title="Tarama Başlatma Hatası",
                ),
                popup_title="Tarama Başlatma Hatası",
            )

    # =========================================================
    # PUBLIC API
    # =========================================================
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
                f"Yenileme hatası oluştu: {exc}",
                detailed_text=self._format_exception_details(
                    exc,
                    title="Yenileme Hatası",
                ),
                popup_title="Yenileme Hatası",
            )
            print(traceback.format_exc())

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
                f"Tarama hatası oluştu: {exc}",
                detailed_text=self._format_exception_details(
                    exc,
                    title="Tarama Hatası",
                ),
                popup_title="Tarama Hatası",
            )
            print(traceback.format_exc())
