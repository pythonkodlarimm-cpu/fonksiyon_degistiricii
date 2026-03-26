# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/root_paketi/root/root_akisi/app_state_kaydet_geri_yukle/app_state_kaydet_geri_yukle.py

ROL:
- Root katmanında uygulama state kaydetme ve geri yükleme akışını tek modülde toplar
- Öncelikli olarak RAM içindeki geçici memory state yaklaşımını uygular
- Gerekirse aynı process / Android arka plan senaryoları için hafif disk fallback kullanır
- Kaydedilmiş dosya yolundan veya seçim bilgisinden fonksiyon listesini yeniden üretir
- Seçili item, editör içeriği ve scroll konumunu geri yükler
- UI temizleme ve restore yardımcılarını merkezi hale getirir
- Runtime tarafında lazy resolve ve cache kullanarak tekrar eden lookup maliyetini azaltır
- Android arka plan dönüşlerinde sadece görsel state değil, gerçek belge oturumunu da
  tekrar kurmaya çalışır

MİMARİ:
- Bu modül mixin mantığıyla çalışır
- Import-level lazy import bu dosyada hedeflenmez; burada runtime lazy resolve + cache uygulanır
- Root method ve widget method çözümlemeleri cache içine alınır
- Dosya varlık kontrolü Path ile yapılır
- Ana yaklaşım RAM state'tir; disk sadece güvenli fallback katmanıdır
- Restore sırasında önce selection/session tekrar kurulur, sonra item/editor/scroll uygulanır
- Fail-soft yaklaşım uygulanır; restore hataları root'u çökertmez

DESTEKLENEN ROOT ALANLARI:
- self.current_file_path
- self.current_session
- self.items
- self.selected_item
- self.dosya_secici
- self.function_list
- self.editor
- self.scroll
- self.services
- self._memory_app_state
- self._resume_restore_scheduled

BEKLENEN ROOT METODLARI:
- self._collect_app_state(...)
- self._clear_scan_transition_state(...)
- self._find_item_by_identity_value(...)
- self._editor_text_yaz(...)
- self.select_item(...)
- self._get_core_yoneticisi(...)
- self._m(...)
- self.set_status_info(...)
- self._show_temporary_restore_status(...)

BEKLENEN WIDGET API'LERI:
- dosya_secici.clear_selection()
- dosya_secici.set_path(...)
- dosya_secici.set_selection(...)
- dosya_secici.get_path()
- dosya_secici.get_display_name()
- function_list.clear_all()
- function_list.set_items(...)
- editor.clear_all() veya editor.clear_selection()
- editor.set_item(...)

NOTLAR:
- Önce RAM state kullanılır
- RAM state yoksa disk fallback denenir
- Uygulama tamamen kapanıp açıldığında kalıcılık ana hedef değildir
- Restore başarısız olursa güvenli biçimde yeni oturum başlatılır
- Scroll restore işlemi Clock.schedule_once ile gecikmeli uygulanır
- Bu dosya restore sırasında belge oturumunu tekrar ayağa kaldırmayı dener;
  bu sayede ekranda belge seçili görünüp arka planda "dosya seçili değil" hatası
  oluşma ihtimali azaltılır

SURUM: 3
TARIH: 2026-03-26
IMZA: FY.
"""

from __future__ import annotations

import json
import traceback
from pathlib import Path

from kivy.clock import Clock


class RootAppStateKaydetGeriYukleMixin:
    """
    Root katmanında uygulama state kaydetme ve geri yükleme akışını yöneten mixin.
    """

    # =========================================================
    # CACHE
    # =========================================================
    def _ensure_app_state_cache(self) -> None:
        """
        App state akışı için yardımcı cache alanlarını hazırlar.
        """
        try:
            if not hasattr(self, "_app_state_cache"):
                self._app_state_cache = {}
        except Exception:
            pass

    def _app_state_cache_temizle(self) -> None:
        """
        App state cache alanlarını temizler.
        """
        try:
            self._app_state_cache = {}
        except Exception:
            pass

    def _app_state_cache_get(self, key: str, default=None):
        """
        Cache içinden güvenli biçimde değer okur.
        """
        try:
            self._ensure_app_state_cache()
            return self._app_state_cache.get(key, default)
        except Exception:
            return default

    def _app_state_cache_set(self, key: str, value) -> None:
        """
        Cache içine güvenli biçimde değer yazar.
        """
        try:
            self._ensure_app_state_cache()
            self._app_state_cache[key] = value
        except Exception:
            pass

    # =========================================================
    # INTERNAL HELPERS
    # =========================================================
    def _safe_getattr(self, name: str, default=None):
        """
        Root üzerinde güvenli getattr çağrısı yapar.
        """
        try:
            return getattr(self, name, default)
        except Exception:
            return default

    def _coerce_text(self, value) -> str:
        """
        Gelen değeri güvenli biçimde metne çevirir.
        """
        try:
            return str(value or "")
        except Exception:
            return ""

    def _state_cache_file_path(self) -> Path:
        """
        Hafif disk fallback state dosya yolunu üretir.
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
            path = self._state_cache_file_path()
            path.write_text(
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
            path = self._state_cache_file_path()
            if not path.exists() or not path.is_file():
                return {}

            raw = path.read_text(encoding="utf-8")
            data = json.loads(raw)

            if isinstance(data, dict):
                return dict(data)

            return {}
        except Exception:
            return {}

    def _clear_state_disk_cache(self) -> None:
        """
        Başarılı restore veya temizlik durumunda disk fallback dosyasını siler.
        """
        try:
            path = self._state_cache_file_path()
            if path.exists():
                path.unlink()
        except Exception:
            pass

    def _resolve_root_method(self, method_name: str):
        """
        Root üzerindeki callable metodu lazy resolve eder ve cache'ler.
        """
        cache_key = None

        try:
            cache_key = f"root_method::{id(self)}::{method_name}"
            cached = self._app_state_cache_get(cache_key, None)
            if cached is not None:
                return cached
        except Exception:
            cache_key = None

        bulunan = None
        try:
            method = getattr(self, method_name, None)
            if callable(method):
                bulunan = method
        except Exception:
            bulunan = None

        try:
            if cache_key is not None and bulunan is not None:
                self._app_state_cache_set(cache_key, bulunan)
        except Exception:
            pass

        return bulunan

    def _resolve_object_method(self, obj, method_name: str):
        """
        Verilen nesne üzerindeki callable metodu lazy resolve eder ve cache'ler.
        """
        if obj is None:
            return None

        cache_key = None

        try:
            cache_key = f"obj_method::{id(obj)}::{method_name}"
            cached = self._app_state_cache_get(cache_key, None)
            if cached is not None:
                return cached
        except Exception:
            cache_key = None

        bulunan = None
        try:
            method = getattr(obj, method_name, None)
            if callable(method):
                bulunan = method
        except Exception:
            bulunan = None

        try:
            if cache_key is not None and bulunan is not None:
                self._app_state_cache_set(cache_key, bulunan)
        except Exception:
            pass

        return bulunan

    def _root_call(self, method_name: str, *args, **kwargs):
        """
        Root üzerindeki metodu güvenli biçimde çağırır.

        Returns:
            tuple[bool, Any]
        """
        try:
            method = self._resolve_root_method(method_name)
            if callable(method):
                return True, method(*args, **kwargs)
        except Exception:
            pass
        return False, None

    def _object_call(self, obj, method_name: str, *args, **kwargs):
        """
        Nesne üzerindeki metodu güvenli biçimde çağırır.

        Returns:
            tuple[bool, Any]
        """
        try:
            method = self._resolve_object_method(obj, method_name)
            if callable(method):
                return True, method(*args, **kwargs)
        except Exception:
            pass
        return False, None

    def _m_cached(self, anahtar: str, default: str = "") -> str:
        """
        Root üzerindeki _m metodunu cache ile çağırır.
        """
        try:
            called, value = self._root_call("_m", anahtar, default)
            if called:
                return str(value or default or anahtar)
        except Exception:
            pass
        return str(default or anahtar)

    def _set_status_info_cached(self, message: str, icon_name: str) -> bool:
        """
        Root üzerindeki set_status_info metodunu çağırır.
        """
        try:
            called, _ = self._root_call(
                "set_status_info",
                str(message or ""),
                str(icon_name or ""),
            )
            return bool(called)
        except Exception:
            return False

    def _show_temporary_restore_status_cached(
        self,
        message: str,
        icon_name: str = "onaylandi.png",
        duration: float = 3.5,
    ) -> bool:
        """
        Root üzerindeki _show_temporary_restore_status metodunu çağırır.
        """
        try:
            called, _ = self._root_call(
                "_show_temporary_restore_status",
                str(message or ""),
                str(icon_name or ""),
                float(duration),
            )
            return bool(called)
        except Exception:
            return False

    def _select_item_cached(self, item) -> bool:
        """
        Root üzerindeki select_item metodunu çağırır.
        """
        try:
            called, _ = self._root_call("select_item", item)
            return bool(called)
        except Exception:
            return False

    def _clear_scan_transition_state_cached(self) -> None:
        """
        Root üzerindeki _clear_scan_transition_state metodunu çağırır.
        """
        try:
            self._root_call("_clear_scan_transition_state")
        except Exception:
            pass

    def _get_core_yoneticisi_cached(self):
        """
        Root üzerindeki _get_core_yoneticisi metodunu çağırır.
        """
        try:
            called, value = self._root_call("_get_core_yoneticisi")
            if called:
                return value
        except Exception:
            pass
        return None

    def _get_services_cached(self):
        """
        Root üzerindeki services nesnesini döndürür.
        """
        try:
            cached = self._app_state_cache_get("resolved_services", None)
            if cached is not None:
                return cached
        except Exception:
            pass

        try:
            services = self._safe_getattr("services", None)
            if services is not None:
                self._app_state_cache_set("resolved_services", services)
            return services
        except Exception:
            return None

    def _get_belge_yoneticisi_cached(self):
        """
        Services üzerinden belge yöneticisini döndürür.
        """
        try:
            cached = self._app_state_cache_get("resolved_belge_yoneticisi", None)
            if cached is not None:
                return cached
        except Exception:
            pass

        try:
            services = self._get_services_cached()
            if services is None:
                return None

            belge_fn = getattr(services, "belge_yoneticisi", None)
            if callable(belge_fn):
                belge = belge_fn()
                if belge is not None:
                    self._app_state_cache_set("resolved_belge_yoneticisi", belge)
                return belge
        except Exception:
            pass

        return None

    def _get_document_selection_class_cached(self):
        """
        DocumentSelection sınıfını güvenli biçimde resolve eder.
        """
        try:
            cached = self._app_state_cache_get("document_selection_class", None)
            if cached is not None:
                return cached
        except Exception:
            pass

        try:
            called, value = self._root_call("_get_document_selection_class")
            if called and value is not None:
                self._app_state_cache_set("document_selection_class", value)
                return value
        except Exception:
            pass

        try:
            from app.ui.dosya_secici_paketi.models import DocumentSelection

            self._app_state_cache_set("document_selection_class", DocumentSelection)
            return DocumentSelection
        except Exception:
            return None

    def _find_item_by_identity_value_cached(self, identity: str):
        """
        Root üzerindeki _find_item_by_identity_value metodunu çağırır.
        """
        try:
            called, value = self._root_call("_find_item_by_identity_value", identity)
            if called:
                return value
        except Exception:
            pass
        return None

    def _editor_text_yaz_cached(self, text: str) -> None:
        """
        Root üzerindeki _editor_text_yaz metodunu çağırır.
        """
        try:
            self._root_call("_editor_text_yaz", text)
        except Exception:
            pass

    def _build_selection_from_state(self, state: dict):
        """
        Kayıtlı state'ten yeniden DocumentSelection nesnesi üretmeyi dener.
        """
        if not isinstance(state, dict):
            return None

        selection_source = self._coerce_text(state.get("selection_source", "")).strip()
        selection_uri = self._coerce_text(state.get("selection_uri", "")).strip()
        selection_local_path = self._coerce_text(
            state.get("selection_local_path", "")
        ).strip()
        selection_mime_type = self._coerce_text(
            state.get("selection_mime_type", "")
        ).strip()
        selection_display_name = self._coerce_text(
            state.get("selection_display_name", "")
        ).strip()
        selection_identifier = self._coerce_text(
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

        DocumentSelection = self._get_document_selection_class_cached()
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
        selection_ui_ok = False

        try:
            dosya_secici = self._safe_getattr("dosya_secici", None)
            if dosya_secici is None:
                return False

            if selection is not None:
                called, _ = self._object_call(dosya_secici, "set_selection", selection)
                if called:
                    selection_ui_ok = True

            if selection_identifier:
                called, _ = self._object_call(
                    dosya_secici,
                    "set_path",
                    selection_identifier,
                )
                if called:
                    selection_ui_ok = True
            elif current_file_path:
                called, _ = self._object_call(
                    dosya_secici,
                    "set_path",
                    current_file_path,
                )
                if called:
                    selection_ui_ok = True

            if selection_display_name:
                try:
                    dosya_secici._last_display_name = selection_display_name
                except Exception:
                    pass

                try:
                    refresh_summary = self._resolve_object_method(
                        dosya_secici,
                        "_refresh_summary",
                    )
                    if callable(refresh_summary):
                        refresh_summary()
                except Exception:
                    pass

        except Exception:
            pass

        return selection_ui_ok

    def _restore_session_from_selection_state(self, state: dict) -> bool:
        """
        Kayıtlı selection state'ten gerçek belge oturumunu tekrar kurmayı dener.
        """
        if not isinstance(state, dict):
            return False

        selection = self._build_selection_from_state(state)
        if selection is None:
            return False

        try:
            belge = self._get_belge_yoneticisi_cached()
            if belge is None:
                return False

            oturum_baslat = self._resolve_object_method(belge, "oturum_baslat")
            if not callable(oturum_baslat):
                return False

            session = oturum_baslat(selection)
            if session is None:
                return False

            self.current_session = session

            try:
                calisma_yolu_fn = self._resolve_object_method(
                    belge,
                    "calisma_dosyasi_yolu",
                )
                if callable(calisma_yolu_fn):
                    calisma_yolu = self._coerce_text(calisma_yolu_fn(session)).strip()
                    if calisma_yolu:
                        self.current_file_path = calisma_yolu
            except Exception:
                pass

            selection_identifier = self._coerce_text(
                state.get("selection_identifier", "")
            ).strip()
            selection_display_name = self._coerce_text(
                state.get("selection_display_name", "")
            ).strip()

            self._apply_selection_ui_state(
                selection=selection,
                current_file_path=self._coerce_text(self.current_file_path).strip(),
                selection_identifier=selection_identifier,
                selection_display_name=selection_display_name,
            )

            return bool(self._coerce_text(self.current_file_path).strip())
        except Exception:
            print("[ROOT] Selection state üzerinden session restore başarısız.")
            print(traceback.format_exc())
            return False

    # =========================================================
    # APP STATE SAVE
    # =========================================================
    def uygulama_durumu_kaydet(self) -> None:
        """
        Geçici RAM state sözlüğünü üretir ve root üzerinde saklar.
        Gerekirse hafif disk fallback dosyasına da yazar.
        """
        try:
            called, state = self._root_call("_collect_app_state")
            if not called:
                print("[ROOT] Uygulama durumu kaydedilemedi. _collect_app_state yok.")
                return

            state_dict = dict(state or {})
            self._memory_app_state = state_dict

            disk_ok = self._write_state_to_disk(state_dict)

            if disk_ok:
                print("[ROOT] Uygulama durumu memory + disk fallback içinde kaydedildi.")
            else:
                print("[ROOT] Uygulama durumu memory içinde kaydedildi.")
        except Exception:
            print("[ROOT] Uygulama durumu kaydedilemedi.")
            print(traceback.format_exc())

    # =========================================================
    # CLEAR VIEW STATE
    # =========================================================
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
            self._clear_scan_transition_state_cached()
        except Exception:
            pass

        try:
            dosya_secici = self._safe_getattr("dosya_secici", None)
            self._object_call(dosya_secici, "clear_selection")
        except Exception:
            pass

        try:
            function_list = self._safe_getattr("function_list", None)
            self._object_call(function_list, "clear_all")
        except Exception:
            pass

        try:
            editor = self._safe_getattr("editor", None)
            if editor is not None:
                called, _ = self._object_call(editor, "clear_all")
                if not called:
                    self._object_call(editor, "clear_selection")
        except Exception:
            pass

    # =========================================================
    # RESTORE FROM FILE
    # =========================================================
    def _restore_items_from_saved_file(self, saved_file_path: str) -> bool:
        """
        Kayıtlı dosya yolundan fonksiyon listesini yeniden üretir.

        Args:
            saved_file_path: Restore edilecek dosya yolu.

        Returns:
            bool
        """
        temiz_yol = self._coerce_text(saved_file_path).strip()
        if not temiz_yol:
            return False

        try:
            path_obj = Path(temiz_yol)
            if not path_obj.exists() or not path_obj.is_file():
                print(f"[ROOT] Kayıtlı çalışma dosyası bulunamadı: {temiz_yol}")
                return False
        except Exception:
            print(f"[ROOT] Kayıtlı çalışma dosyası doğrulanamadı: {temiz_yol}")
            return False

        try:
            core = self._get_core_yoneticisi_cached()
            if core is None:
                print("[ROOT] Core yöneticisi alınamadı.")
                return False

            scan_method = self._resolve_object_method(core, "scan_functions_from_file")
            if not callable(scan_method):
                print("[ROOT] scan_functions_from_file metodu bulunamadı.")
                return False

            items = scan_method(temiz_yol)
        except Exception:
            print("[ROOT] Kayıtlı çalışma dosyası yeniden taranamadı.")
            print(traceback.format_exc())
            return False

        try:
            items = list(items or [])
            if not items:
                print("[ROOT] Kayıtlı çalışma dosyası tarandı ama fonksiyon listesi boş.")
                return False

            self.current_file_path = temiz_yol
            self.items = items

            function_list = self._safe_getattr("function_list", None)
            self._object_call(function_list, "set_items", self.items)

            print(
                "[ROOT] Kayıtlı çalışma dosyasından içerik geri yüklendi. "
                f"item_count={len(self.items)}"
            )
            return True
        except Exception:
            print("[ROOT] Kayıtlı çalışma dosyası UI'ye uygulanamadı.")
            print(traceback.format_exc())
            return False

    # =========================================================
    # APPLY SAVED STATE
    # =========================================================
    def _apply_saved_state(self, state: dict) -> bool:
        """
        Kayıtlı state sözlüğünü root'a uygular.

        Args:
            state: Daha önce kaydedilmiş state sözlüğü.

        Returns:
            bool
        """
        if not isinstance(state, dict) or not state:
            return False

        current_file_path = self._coerce_text(state.get("current_file_path", "")).strip()
        selected_item_identity = self._coerce_text(
            state.get("selected_item_identity", "")
        ).strip()
        editor_text = self._coerce_text(state.get("editor_text", ""))
        scroll_y = state.get("scroll_y", None)
        selection_identifier = self._coerce_text(
            state.get("selection_identifier", "")
        ).strip()
        selection_display_name = self._coerce_text(
            state.get("selection_display_name", "")
        ).strip()

        self._clear_restore_view_state()

        restore_ok = False
        selected_ok = False
        editor_text_ok = False
        selection_ui_ok = False
        session_restored = False

        try:
            session_restored = self._restore_session_from_selection_state(state)
        except Exception:
            session_restored = False

        try:
            if not session_restored:
                selection_ui_ok = self._apply_selection_ui_state(
                    selection=None,
                    current_file_path=current_file_path,
                    selection_identifier=selection_identifier,
                    selection_display_name=selection_display_name,
                )
        except Exception:
            pass

        try:
            hedef_yol = self._coerce_text(self.current_file_path or current_file_path).strip()
            if hedef_yol:
                restore_ok = self._restore_items_from_saved_file(hedef_yol)
        except Exception:
            print("[ROOT] Saved file restore aşaması başarısız.")
            print(traceback.format_exc())
            restore_ok = False

        if not restore_ok:
            self._clear_restore_view_state()
            return False

        try:
            if selected_item_identity:
                bulunan = self._find_item_by_identity_value_cached(
                    selected_item_identity
                )
                if bulunan is not None:
                    try:
                        selected_ok = self._select_item_cached(bulunan)
                        if not selected_ok:
                            self.selected_item = bulunan
                            editor = self._safe_getattr("editor", None)
                            called, _ = self._object_call(editor, "set_item", bulunan)
                            if called:
                                selected_ok = True
                    except Exception:
                        pass
        except Exception:
            print("[ROOT] Kayıtlı seçili fonksiyon geri yüklenemedi.")
            print(traceback.format_exc())

        try:
            if editor_text:
                self._editor_text_yaz_cached(editor_text)
                editor_text_ok = True
        except Exception:
            print("[ROOT] Kayıtlı editör metni geri yüklenemedi.")
            print(traceback.format_exc())

        def _apply_scroll(*_args):
            try:
                scroll = self._safe_getattr("scroll", None)
                if scroll_y is not None and scroll is not None:
                    scroll.scroll_y = float(scroll_y)
            except Exception:
                pass

        try:
            Clock.schedule_once(_apply_scroll, 0.12)
        except Exception:
            pass

        try:
            if list(self._safe_getattr("items", []) or []):
                return True
        except Exception:
            pass

        if selected_ok or editor_text_ok or selection_ui_ok or session_restored:
            return True

        self._clear_restore_view_state()
        return False

    # =========================================================
    # RESTORE ENTRYPOINT
    # =========================================================
    def uygulama_durumu_geri_yukle(self) -> None:
        """
        Memory içindeki geçici state'i, gerekirse disk fallback'i kullanarak
        root'a geri yüklemeyi dener.
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
                    print("[ROOT] Memory state boştu, disk fallback state yüklendi.")

            if not state:
                print("[ROOT] Memory/disk app state bulunamadı.")
                self._set_status_info_cached(
                    self._m_cached("new_session_started", "Yeni oturum açıldı."),
                    "onaylandi.png",
                )
                return

            if bool(self._safe_getattr("_resume_restore_scheduled", False)):
                return

            self._resume_restore_scheduled = True

            def _restore(*_args):
                self._resume_restore_scheduled = False
                try:
                    restore_ok = self._apply_saved_state(state)

                    if restore_ok:
                        self._show_temporary_restore_status_cached(
                            self._m_cached("session_restored", "Oturum geri yüklendi."),
                            "onaylandi.png",
                            3.5,
                        )
                        self._clear_state_disk_cache()
                        print("[ROOT] Uygulama durumu restore edildi.")
                        return

                    self._set_status_info_cached(
                        self._m_cached("new_session_started", "Yeni oturum açıldı."),
                        "onaylandi.png",
                    )
                    print("[ROOT] Restore başarısız. Yeni oturum başlatıldı.")

                except Exception:
                    self._clear_restore_view_state()
                    print("[ROOT] Uygulama durumu geri yüklenemedi.")
                    print(traceback.format_exc())
                    self._set_status_info_cached(
                        self._m_cached("new_session_started", "Yeni oturum açıldı."),
                        "onaylandi.png",
                    )

            Clock.schedule_once(_restore, 0.10)

        except Exception:
            print("[ROOT] uygulama_durumu_geri_yukle çağrısı başarısız.")
            print(traceback.format_exc())
            self._set_status_info_cached(
                self._m_cached("new_session_started", "Yeni oturum açıldı."),
                "onaylandi.png",
            )

    # =========================================================
    # AUTO RESTORE
    # =========================================================
    def _auto_restore_saved_state_on_start(self) -> None:
        """
        Açılışta disk fallback state varsa memory alanına taşımayı dener.
        """
        try:
            memory_state = self._safe_getattr("_memory_app_state", None)
            if isinstance(memory_state, dict) and memory_state:
                return

            disk_state = self._read_state_from_disk()
            if isinstance(disk_state, dict) and disk_state:
                self._memory_app_state = dict(disk_state)
                print("[ROOT] Açılışta disk fallback state memory'e taşındı.")
        except Exception:
            pass
