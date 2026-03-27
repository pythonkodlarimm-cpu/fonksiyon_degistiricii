# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/root_paketi/root/root_akisi/app_state_kaydet_geri_yukle/app_state_kaydet_geri_yukle.py

ROL:
- Root katmanında uygulama state kaydetme ve geri yükleme akışını yönetir
- Öncelikle RAM içindeki geçici state'i kullanır
- Gerekirse hafif disk fallback uygular
- Kaydedilmiş dosya, seçim, editör ve scroll state'ini geri yükler
- Restore öncesi görünüm state'ini güvenli biçimde temizler
- Fail-soft yaklaşım uygular

MİMARİ:
- Bu modül mixin mantığıyla çalışır
- UI çizmez
- Disk fallback hafif ve geçicidir
- Çeviri için root üzerindeki self._m(...) hattını kullanır
- Amaç state akışını yönetmektir; iş kuralları burada biriktirilmez

SURUM: 4
TARIH: 2026-03-27
IMZA: FY.
"""

from __future__ import annotations

import json
from pathlib import Path

from kivy.clock import Clock


class RootAppStateKaydetGeriYukleMixin:
    """
    Root katmanında uygulama state kaydetme ve geri yükleme akışını yöneten mixin.
    """

    def _safe_getattr(self, name: str, default=None):
        """
        Root üzerinde güvenli getattr çağrısı yapar.
        """
        try:
            return getattr(self, name, default)
        except Exception:
            return default

    def _metne_cevir(self, value) -> str:
        """
        Gelen değeri güvenli biçimde metne çevirir.
        """
        try:
            return str(value or "")
        except Exception:
            return ""

    def _ceviri(self, anahtar: str, varsayilan: str) -> str:
        """
        Root üzerindeki _m çeviri hattını güvenli biçimde kullanır.
        """
        try:
            m = getattr(self, "_m", None)
            if callable(m):
                return str(m(anahtar, varsayilan) or varsayilan)
        except Exception:
            pass
        return str(varsayilan)

    def _status_bilgi_yaz(self, mesaj: str, ikon_adi: str = "onaylandi.png") -> None:
        """
        Root üzerindeki set_status_info metodunu güvenli biçimde çağırır.
        """
        try:
            metod = getattr(self, "set_status_info", None)
            if callable(metod):
                metod(str(mesaj or ""), str(ikon_adi or ""))
        except Exception:
            pass

    def _gecici_restore_durumu_goster(
        self,
        mesaj: str,
        ikon_adi: str = "onaylandi.png",
        sure: float = 3.5,
    ) -> None:
        """
        Root üzerindeki geçici restore bilgi metodunu güvenli biçimde çağırır.
        """
        try:
            metod = getattr(self, "_show_temporary_restore_status", None)
            if callable(metod):
                metod(str(mesaj or ""), str(ikon_adi or ""), float(sure))
        except Exception:
            pass

    def _state_cache_file_path(self) -> Path:
        """
        Hafif disk fallback state dosyasının yolunu üretir.
        """
        try:
            proje_root = Path(__file__).resolve().parents[7]
        except Exception:
            try:
                proje_root = Path.cwd()
            except Exception:
                proje_root = Path(".")

        return proje_root / ".root_memory_app_state.json"

    def _write_state_to_disk(self, state: dict) -> bool:
        """
        State sözlüğünü hafif disk fallback dosyasına yazar.
        """
        try:
            yol = self._state_cache_file_path()
            yol.write_text(
                json.dumps(state or {}, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            return True
        except Exception:
            return False

    def _read_state_from_disk(self) -> dict:
        """
        Hafif disk fallback dosyasından state okumayı dener.
        """
        try:
            yol = self._state_cache_file_path()
            if not yol.exists() or not yol.is_file():
                return {}

            icerik = yol.read_text(encoding="utf-8")
            veri = json.loads(icerik)

            if isinstance(veri, dict):
                return dict(veri)
        except Exception:
            pass

        return {}

    def _clear_state_disk_cache(self) -> None:
        """
        Disk fallback state dosyasını siler.
        """
        try:
            yol = self._state_cache_file_path()
            if yol.exists():
                yol.unlink()
        except Exception:
            pass

    def _clear_restore_view_state(self) -> None:
        """
        Restore öncesi root görünüm state alanlarını temizler.
        """
        try:
            self.current_file_path = ""
            self.current_session = None
            self.items = []
            self.selected_item = None
        except Exception:
            pass

        try:
            temizle = getattr(self, "_clear_scan_transition_state", None)
            if callable(temizle):
                temizle()
        except Exception:
            pass

        try:
            dosya_secici = self._safe_getattr("dosya_secici", None)
            if dosya_secici is not None:
                metod = getattr(dosya_secici, "clear_selection", None)
                if callable(metod):
                    metod()
        except Exception:
            pass

        try:
            function_list = self._safe_getattr("function_list", None)
            if function_list is not None:
                metod = getattr(function_list, "clear_all", None)
                if callable(metod):
                    metod()
        except Exception:
            pass

        try:
            editor = self._safe_getattr("editor", None)
            if editor is not None:
                clear_all = getattr(editor, "clear_all", None)
                if callable(clear_all):
                    clear_all()
                else:
                    clear_selection = getattr(editor, "clear_selection", None)
                    if callable(clear_selection):
                        clear_selection()
        except Exception:
            pass

    def _get_services(self):
        """
        Root üzerindeki services nesnesini döndürür.
        """
        return self._safe_getattr("services", None)

    def _get_belge_yoneticisi(self):
        """
        Services üzerinden belge yöneticisini döndürür.
        """
        services = self._get_services()
        if services is None:
            return None

        try:
            belge_yoneticisi = getattr(services, "belge_yoneticisi", None)
            if callable(belge_yoneticisi):
                return belge_yoneticisi()
        except Exception:
            pass

        return None

    def _get_core_yoneticisi(self):
        """
        Root üzerindeki core yöneticisini döndürür.
        """
        try:
            metod = getattr(self, "_get_core_yoneticisi", None)
            if callable(metod):
                return metod()
        except Exception:
            pass

        return None

    def _get_document_selection_class(self):
        """
        DocumentSelection sınıfını döndürür.
        """
        try:
            metod = getattr(self, "_get_document_selection_class", None)
            if callable(metod):
                sinif = metod()
                if sinif is not None:
                    return sinif
        except Exception:
            pass

        try:
            from app.ui.dosya_secici_paketi.models import DocumentSelection
            return DocumentSelection
        except Exception:
            return None

    def _build_selection_from_state(self, state: dict):
        """
        Kayıtlı state'ten yeniden DocumentSelection nesnesi üretmeyi dener.
        """
        if not isinstance(state, dict):
            return None

        selection_source = self._metne_cevir(state.get("selection_source", "")).strip()
        selection_uri = self._metne_cevir(state.get("selection_uri", "")).strip()
        selection_local_path = self._metne_cevir(
            state.get("selection_local_path", "")
        ).strip()
        selection_mime_type = self._metne_cevir(
            state.get("selection_mime_type", "")
        ).strip()
        selection_display_name = self._metne_cevir(
            state.get("selection_display_name", "")
        ).strip()
        selection_identifier = self._metne_cevir(
            state.get("selection_identifier", "")
        ).strip()

        if not any(
            (
                selection_source,
                selection_uri,
                selection_local_path,
                selection_mime_type,
                selection_display_name,
                selection_identifier,
            )
        ):
            return None

        DocumentSelection = self._get_document_selection_class()
        if DocumentSelection is None:
            return None

        try:
            return DocumentSelection(
                source=selection_source or "unknown",
                uri=selection_uri,
                local_path=selection_local_path,
                display_name=selection_display_name,
                mime_type=selection_mime_type,
            )
        except Exception:
            pass

        try:
            return DocumentSelection(
                source=selection_source or "unknown",
                uri=selection_uri or selection_identifier,
                local_path=selection_local_path,
                display_name=selection_display_name,
                mime_type=selection_mime_type,
            )
        except Exception:
            return None

    def _apply_selection_ui_state(
        self,
        selection,
        current_file_path: str = "",
        selection_identifier: str = "",
        selection_display_name: str = "",
    ) -> bool:
        """
        Dosya seçici UI üzerinde path/selection/display state'ini uygular.
        """
        dosya_secici = self._safe_getattr("dosya_secici", None)
        if dosya_secici is None:
            return False

        uygulandi = False

        if selection is not None:
            try:
                set_selection = getattr(dosya_secici, "set_selection", None)
                if callable(set_selection):
                    set_selection(selection)
                    uygulandi = True
            except Exception:
                pass

        hedef_yol = selection_identifier or current_file_path
        if hedef_yol:
            try:
                set_path = getattr(dosya_secici, "set_path", None)
                if callable(set_path):
                    set_path(hedef_yol)
                    uygulandi = True
            except Exception:
                pass

        if selection_display_name:
            try:
                dosya_secici._last_display_name = selection_display_name
            except Exception:
                pass

            try:
                refresh_summary = getattr(dosya_secici, "_refresh_summary", None)
                if callable(refresh_summary):
                    refresh_summary()
            except Exception:
                pass

        return uygulandi

    def _restore_session_from_selection_state(self, state: dict) -> bool:
        """
        Kayıtlı selection state'ten gerçek belge oturumunu tekrar kurmayı dener.
        """
        if not isinstance(state, dict):
            return False

        selection = self._build_selection_from_state(state)
        if selection is None:
            return False

        belge = self._get_belge_yoneticisi()
        if belge is None:
            return False

        try:
            oturum_baslat = getattr(belge, "oturum_baslat", None)
            if not callable(oturum_baslat):
                return False

            session = oturum_baslat(selection)
            if session is None:
                return False

            self.current_session = session
        except Exception:
            return False

        try:
            calisma_dosyasi_yolu = getattr(belge, "calisma_dosyasi_yolu", None)
            if callable(calisma_dosyasi_yolu):
                yol = self._metne_cevir(calisma_dosyasi_yolu(session)).strip()
                if yol:
                    self.current_file_path = yol
        except Exception:
            pass

        selection_identifier = self._metne_cevir(
            state.get("selection_identifier", "")
        ).strip()
        selection_display_name = self._metne_cevir(
            state.get("selection_display_name", "")
        ).strip()

        self._apply_selection_ui_state(
            selection=selection,
            current_file_path=self._metne_cevir(self.current_file_path).strip(),
            selection_identifier=selection_identifier,
            selection_display_name=selection_display_name,
        )

        return bool(self._metne_cevir(self.current_file_path).strip())

    def _restore_items_from_saved_file(self, saved_file_path: str) -> bool:
        """
        Kayıtlı dosya yolundan fonksiyon listesini yeniden üretir.
        """
        temiz_yol = self._metne_cevir(saved_file_path).strip()
        if not temiz_yol:
            return False

        try:
            yol = Path(temiz_yol)
            if not yol.exists() or not yol.is_file():
                return False
        except Exception:
            return False

        core = self._get_core_yoneticisi()
        if core is None:
            return False

        try:
            scan_functions_from_file = getattr(core, "scan_functions_from_file", None)
            if not callable(scan_functions_from_file):
                return False

            items = list(scan_functions_from_file(temiz_yol) or [])
            if not items:
                return False
        except Exception:
            return False

        try:
            self.current_file_path = temiz_yol
            self.items = items
        except Exception:
            return False

        try:
            function_list = self._safe_getattr("function_list", None)
            if function_list is not None:
                set_items = getattr(function_list, "set_items", None)
                if callable(set_items):
                    set_items(self.items)
        except Exception:
            pass

        return True

    def _apply_saved_state(self, state: dict) -> bool:
        """
        Kayıtlı state sözlüğünü root'a uygular.
        """
        if not isinstance(state, dict) or not state:
            return False

        current_file_path = self._metne_cevir(state.get("current_file_path", "")).strip()
        selected_item_identity = self._metne_cevir(
            state.get("selected_item_identity", "")
        ).strip()
        editor_text = self._metne_cevir(state.get("editor_text", ""))
        scroll_y = state.get("scroll_y", None)
        selection_identifier = self._metne_cevir(
            state.get("selection_identifier", "")
        ).strip()
        selection_display_name = self._metne_cevir(
            state.get("selection_display_name", "")
        ).strip()

        self._clear_restore_view_state()

        session_restored = False
        selection_ui_ok = False
        restore_ok = False
        selected_ok = False
        editor_text_ok = False

        try:
            session_restored = self._restore_session_from_selection_state(state)
        except Exception:
            session_restored = False

        if not session_restored:
            try:
                selection_ui_ok = self._apply_selection_ui_state(
                    selection=None,
                    current_file_path=current_file_path,
                    selection_identifier=selection_identifier,
                    selection_display_name=selection_display_name,
                )
            except Exception:
                selection_ui_ok = False

        hedef_yol = self._metne_cevir(self.current_file_path or current_file_path).strip()
        if hedef_yol:
            try:
                restore_ok = self._restore_items_from_saved_file(hedef_yol)
            except Exception:
                restore_ok = False

        if not restore_ok:
            self._clear_restore_view_state()
            return False

        if selected_item_identity:
            try:
                bul = getattr(self, "_find_item_by_identity_value", None)
                if callable(bul):
                    bulunan = bul(selected_item_identity)
                else:
                    bulunan = None

                if bulunan is not None:
                    sec = getattr(self, "select_item", None)
                    if callable(sec):
                        sec(bulunan)
                        selected_ok = True
                    else:
                        self.selected_item = bulunan
                        editor = self._safe_getattr("editor", None)
                        if editor is not None:
                            set_item = getattr(editor, "set_item", None)
                            if callable(set_item):
                                set_item(bulunan)
                                selected_ok = True
            except Exception:
                pass

        if editor_text:
            try:
                editor_text_yaz = getattr(self, "_editor_text_yaz", None)
                if callable(editor_text_yaz):
                    editor_text_yaz(editor_text)
                    editor_text_ok = True
            except Exception:
                pass

        def _scroll_uygula(*_args):
            try:
                scroll = self._safe_getattr("scroll", None)
                if scroll is not None and scroll_y is not None:
                    scroll.scroll_y = float(scroll_y)
            except Exception:
                pass

        try:
            Clock.schedule_once(_scroll_uygula, 0.12)
        except Exception:
            pass

        try:
            if list(self._safe_getattr("items", []) or []):
                return True
        except Exception:
            pass

        if session_restored or selection_ui_ok or selected_ok or editor_text_ok:
            return True

        self._clear_restore_view_state()
        return False

    def uygulama_durumu_kaydet(self) -> None:
        """
        Geçici RAM state sözlüğünü üretir ve root üzerinde saklar.
        Gerekirse hafif disk fallback dosyasına da yazar.
        """
        try:
            collect = getattr(self, "_collect_app_state", None)
            if not callable(collect):
                return

            state = dict(collect() or {})
            self._memory_app_state = state
            self._write_state_to_disk(state)
        except Exception:
            pass

    def uygulama_durumu_geri_yukle(self) -> None:
        """
        Memory içindeki geçici state'i, gerekirse disk fallback ile root'a geri yükler.
        """
        try:
            state = {}

            memory_state = self._safe_getattr("_memory_app_state", None)
            if isinstance(memory_state, dict) and memory_state:
                state = dict(memory_state)

            if not state:
                disk_state = self._read_state_from_disk()
                if isinstance(disk_state, dict) and disk_state:
                    state = dict(disk_state)
                    try:
                        self._memory_app_state = dict(state)
                    except Exception:
                        pass

            if not state:
                self._status_bilgi_yaz(
                    self._ceviri("new_session_started", "Yeni oturum açıldı."),
                    "onaylandi.png",
                )
                return

            if bool(self._safe_getattr("_resume_restore_scheduled", False)):
                return

            self._resume_restore_scheduled = True

            def _restore(*_args):
                try:
                    self._resume_restore_scheduled = False
                except Exception:
                    pass

                try:
                    restore_ok = self._apply_saved_state(state)
                except Exception:
                    restore_ok = False

                if restore_ok:
                    self._gecici_restore_durumu_goster(
                        self._ceviri("session_restored", "Oturum geri yüklendi."),
                        "onaylandi.png",
                        3.5,
                    )
                    self._clear_state_disk_cache()
                    return

                try:
                    self._clear_restore_view_state()
                except Exception:
                    pass

                self._status_bilgi_yaz(
                    self._ceviri("new_session_started", "Yeni oturum açıldı."),
                    "onaylandi.png",
                )

            Clock.schedule_once(_restore, 0.10)

        except Exception:
            self._status_bilgi_yaz(
                self._ceviri("new_session_started", "Yeni oturum açıldı."),
                "onaylandi.png",
            )

    def _auto_restore_saved_state_on_start(self) -> None:
        """
        Açılışta disk fallback state varsa memory alanına taşır.
        """
        try:
            memory_state = self._safe_getattr("_memory_app_state", None)
            if isinstance(memory_state, dict) and memory_state:
                return

            disk_state = self._read_state_from_disk()
            if isinstance(disk_state, dict) and disk_state:
                self._memory_app_state = dict(disk_state)
        except Exception:
            pass
