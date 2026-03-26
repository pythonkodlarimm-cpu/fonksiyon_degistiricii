# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/root_paketi/root/root_akisi/editor_state/editor_state.py

ROL:
- Root katmanında editör içeriğini okuma/yazma yardımcılarını tek modülde toplar
- Farklı editör implementasyonlarını tek bir ortak erişim katmanından yönetir
- Editörde seçili fonksiyon/metin içeriğini güvenli ve fail-soft şekilde alır
- Editöre metin basma akışını ortaklaştırır
- Seçili item kimliği çözümleme ve kayıtlı item'i geri bulma yardımcılarını sağlar
- Uygulama state toplama akışında gereken editör/selection verisini üretir
- Sık erişilen metod ve attribute çözümlemelerini cache içinde tutar
- Runtime tarafında lookup maliyetini azaltır
- Android arka plan / geri dönüş akışında seçim bilgisinin eksik kalmaması için
  dosya seçimine ait ayrıntılı selection state alanlarını da toplar

MİMARİ:
- Bu modül mixin mantığıyla çalışır
- RootWidget içinde kullanılan editör state helper metodları burada tanımlanır
- Editör widget'ı için method-first, attr-second yaklaşımı uygulanır
- Aşağıdaki editör API varyasyonları desteklenir:
    - get_text / set_text
    - metni_al / metni_yaz
    - icerik_al / icerik_yaz
    - kod_al / kod_yaz
    - editor_input.text
    - doğrudan text / metin / content / icerik / code attribute erişimi
- Seçili item kimliği için aşağıdaki alanlar sırayla denenir:
    - identity
    - full_path
    - dotted_path
    - path
    - name
- Dosya seçici için aşağıdaki alanlar mümkün olduğunda toplanır:
    - selection_identifier
    - selection_display_name
    - selection_source
    - selection_uri
    - selection_local_path
    - selection_mime_type
- Hatalar UI akışını kırmamak için swallow edilir
- Root nesnesinde self.editor, self.selected_item, self.items, self.dosya_secici,
  self.scroll ve self.current_file_path üyelerinin bulunması beklenir

NOTLAR:
- Bu modül import seviyesinde lazy import hedeflemez; burada amaç runtime cache optimizasyonudur
- Disk yazımı yapmaz
- Tarama veya geri yükleme yürütmez
- Kayıt için uygun state sözlüğü üretir
- Method/attribute erişimleri ilk çözümlemeden sonra cache'lenir
- Cache anahtarlarında nesne id + method/attr listesi kullanılır
- Android restore akışında eksik/yarım widget state durumlarına fail-soft yaklaşım uygular

SURUM: 4
TARIH: 2026-03-26
IMZA: FY.
"""

from __future__ import annotations


class RootEditorStateMixin:
    """
    Root katmanında editör state yardımcı davranışlarını sağlayan mixin.

    Beklenen root alanları:
    - self.editor
    - self.selected_item
    - self.items
    - self.dosya_secici
    - self.scroll
    - self.current_file_path
    """

    # =========================================================
    # CACHE
    # =========================================================
    def _ensure_editor_state_cache(self) -> None:
        """
        Editor state yardımcı cache alanlarını hazırlar.
        """
        try:
            if not hasattr(self, "_editor_state_method_cache"):
                self._editor_state_method_cache = {}
        except Exception:
            pass

        try:
            if not hasattr(self, "_editor_state_attr_cache"):
                self._editor_state_attr_cache = {}
        except Exception:
            pass

        try:
            if not hasattr(self, "_editor_state_editor_input_cache"):
                self._editor_state_editor_input_cache = {}
        except Exception:
            pass

        try:
            if not hasattr(self, "_editor_state_item_identity_attr_cache"):
                self._editor_state_item_identity_attr_cache = {}
        except Exception:
            pass

        try:
            if not hasattr(self, "_editor_state_dosya_secici_method_cache"):
                self._editor_state_dosya_secici_method_cache = {}
        except Exception:
            pass

        try:
            if not hasattr(self, "_editor_state_dosya_secici_attr_cache"):
                self._editor_state_dosya_secici_attr_cache = {}
        except Exception:
            pass

    def _editor_state_cache_temizle(self) -> None:
        """
        Editor state yardımcı cache alanlarını temizler.
        """
        try:
            self._editor_state_method_cache = {}
        except Exception:
            pass

        try:
            self._editor_state_attr_cache = {}
        except Exception:
            pass

        try:
            self._editor_state_editor_input_cache = {}
        except Exception:
            pass

        try:
            self._editor_state_item_identity_attr_cache = {}
        except Exception:
            pass

        try:
            self._editor_state_dosya_secici_method_cache = {}
        except Exception:
            pass

        try:
            self._editor_state_dosya_secici_attr_cache = {}
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
        Gelen değeri güvenli şekilde metne çevirir.
        """
        try:
            return str(value or "")
        except Exception:
            return ""

    def _get_cached_method(
        self,
        obj,
        cache_group: str,
        method_names: tuple[str, ...],
    ):
        """
        Verilen nesne için ilk uygun metodu bulur ve cache'ler.
        """
        if obj is None:
            return None

        self._ensure_editor_state_cache()

        cache_key = None

        try:
            object_id = id(obj)
            group_cache = getattr(self, cache_group, None)
            if not isinstance(group_cache, dict):
                group_cache = {}
                setattr(self, cache_group, group_cache)

            cache_key = (object_id, tuple(method_names))

            if cache_key in group_cache:
                return group_cache[cache_key]
        except Exception:
            cache_key = None

        bulunan = None
        try:
            for method_name in method_names:
                method = getattr(obj, method_name, None)
                if callable(method):
                    bulunan = method
                    break
        except Exception:
            bulunan = None

        try:
            group_cache = getattr(self, cache_group, None)
            if isinstance(group_cache, dict) and cache_key is not None:
                group_cache[cache_key] = bulunan
        except Exception:
            pass

        return bulunan

    def _get_cached_attr_name(
        self,
        obj,
        cache_group: str,
        attr_names: tuple[str, ...],
        *,
        require_string: bool = False,
    ):
        """
        Verilen nesne için ilk uygun attribute adını bulur ve cache'ler.
        """
        if obj is None:
            return None

        self._ensure_editor_state_cache()

        cache_key = None

        try:
            object_id = id(obj)
            group_cache = getattr(self, cache_group, None)
            if not isinstance(group_cache, dict):
                group_cache = {}
                setattr(self, cache_group, group_cache)

            cache_key = (object_id, tuple(attr_names), bool(require_string))

            if cache_key in group_cache:
                return group_cache[cache_key]
        except Exception:
            cache_key = None

        bulunan = None

        try:
            for attr_name in attr_names:
                if not hasattr(obj, attr_name):
                    continue

                value = getattr(obj, attr_name, None)
                if require_string and not isinstance(value, str):
                    continue

                bulunan = attr_name
                break
        except Exception:
            bulunan = None

        try:
            group_cache = getattr(self, cache_group, None)
            if isinstance(group_cache, dict) and cache_key is not None:
                group_cache[cache_key] = bulunan
        except Exception:
            pass

        return bulunan

    def _call_first_available(
        self,
        obj,
        method_names: tuple[str, ...],
        *args,
        **kwargs,
    ):
        """
        Verilen nesnede bulunan ilk callable metodu çağırır.
        Cache desteklidir.
        """
        if obj is None:
            return False, None

        try:
            method = self._get_cached_method(
                obj,
                "_editor_state_method_cache",
                method_names,
            )
            if callable(method):
                return True, method(*args, **kwargs)
        except Exception:
            return False, None

        return False, None

    # =========================================================
    # EDITOR TEXT READ
    # =========================================================
    def _editor_text_al(self) -> str:
        """
        Editördeki mevcut metni olabildiğince uyumlu biçimde okur.

        Öncelik sırası:
        1) get_text / metni_al / icerik_al / kod_al metodları
        2) doğrudan text / metin / content / icerik / code attribute'ları
        3) editor_input.text
        """
        try:
            editor = self._safe_getattr("editor", None)
            if editor is None:
                return ""

            called, value = self._call_first_available(
                editor,
                ("get_text", "metni_al", "icerik_al", "kod_al"),
            )
            if called:
                return self._coerce_text(value)

            attr_name = self._get_cached_attr_name(
                editor,
                "_editor_state_attr_cache",
                ("text", "metin", "content", "icerik", "code"),
                require_string=True,
            )
            if attr_name:
                try:
                    value = getattr(editor, attr_name, "")
                    if isinstance(value, str):
                        return value
                except Exception:
                    pass

            try:
                editor_input_attr = self._get_cached_attr_name(
                    editor,
                    "_editor_state_editor_input_cache",
                    ("editor_input",),
                    require_string=False,
                )

                if editor_input_attr:
                    editor_input = getattr(editor, editor_input_attr, None)
                else:
                    editor_input = getattr(editor, "editor_input", None)

                if editor_input is not None and hasattr(editor_input, "text"):
                    return self._coerce_text(editor_input.text)
            except Exception:
                pass

        except Exception:
            pass

        return ""

    # =========================================================
    # EDITOR TEXT WRITE
    # =========================================================
    def _editor_text_yaz(self, text: str) -> None:
        """
        Editöre metin yazar.

        Öncelik sırası:
        1) set_text / metni_yaz / icerik_yaz / kod_yaz metodları
        2) editor_input.text
        3) doğrudan text / metin / content / icerik / code attribute'ları
        """
        temiz = self._coerce_text(text)

        try:
            editor = self._safe_getattr("editor", None)
            if editor is None:
                return

            called, _ = self._call_first_available(
                editor,
                ("set_text", "metni_yaz", "icerik_yaz", "kod_yaz"),
                temiz,
            )
            if called:
                return

            try:
                editor_input_attr = self._get_cached_attr_name(
                    editor,
                    "_editor_state_editor_input_cache",
                    ("editor_input",),
                    require_string=False,
                )

                if editor_input_attr:
                    editor_input = getattr(editor, editor_input_attr, None)
                else:
                    editor_input = getattr(editor, "editor_input", None)

                if editor_input is not None and hasattr(editor_input, "text"):
                    editor_input.text = temiz
                    return
            except Exception:
                pass

            attr_name = self._get_cached_attr_name(
                editor,
                "_editor_state_attr_cache",
                ("text", "metin", "content", "icerik", "code"),
                require_string=False,
            )
            if attr_name:
                try:
                    setattr(editor, attr_name, temiz)
                    return
                except Exception:
                    pass

            for attr_name in ("text", "metin", "content", "icerik", "code"):
                try:
                    if hasattr(editor, attr_name):
                        setattr(editor, attr_name, temiz)
                        return
                except Exception:
                    continue

        except Exception:
            pass

    # =========================================================
    # SELECTED ITEM HELPERS
    # =========================================================
    def _selected_item_identity(self) -> str:
        """
        Mevcut seçili item için kalıcı/tekrar bulunabilir kimlik değeri üretir.
        """
        try:
            selected_item = self._safe_getattr("selected_item", None)
            if selected_item is None:
                return ""

            attr_name = self._get_cached_attr_name(
                selected_item,
                "_editor_state_item_identity_attr_cache",
                ("identity", "full_path", "dotted_path", "path", "name"),
                require_string=False,
            )
            if attr_name:
                try:
                    value = getattr(selected_item, attr_name, None)
                    if value:
                        return str(value)
                except Exception:
                    pass

            for attr_name in (
                "identity",
                "full_path",
                "dotted_path",
                "path",
                "name",
            ):
                try:
                    value = getattr(selected_item, attr_name, None)
                    if value:
                        return str(value)
                except Exception:
                    continue
        except Exception:
            pass

        return ""

    def _find_item_by_identity_value(self, identity: str):
        """
        Kaydedilmiş kimlik değerine göre self.items içinde eşleşen item'i arar.
        """
        temiz = self._coerce_text(identity).strip()
        if not temiz:
            return None

        for item in list(self._safe_getattr("items", []) or []):
            try:
                attr_name = self._get_cached_attr_name(
                    item,
                    "_editor_state_item_identity_attr_cache",
                    ("identity", "full_path", "dotted_path", "path", "name"),
                    require_string=False,
                )

                if attr_name:
                    try:
                        value = getattr(item, attr_name, None)
                        if self._coerce_text(value).strip() == temiz:
                            return item
                        continue
                    except Exception:
                        pass

                for current_attr_name in (
                    "identity",
                    "full_path",
                    "dotted_path",
                    "path",
                    "name",
                ):
                    try:
                        value = getattr(item, current_attr_name, None)
                        if self._coerce_text(value).strip() == temiz:
                            return item
                    except Exception:
                        continue
            except Exception:
                continue

        return None

    # =========================================================
    # DOSYA SECICI HELPERS
    # =========================================================
    def _get_dosya_secici_method(
        self,
        dosya_secici,
        method_names: tuple[str, ...],
    ):
        """
        Dosya seçici için ilk uygun callable metodu bulur ve cache'ler.
        """
        if dosya_secici is None:
            return None

        self._ensure_editor_state_cache()

        cache_key = None

        try:
            object_id = id(dosya_secici)
            group_cache = self._editor_state_dosya_secici_method_cache
            cache_key = (object_id, tuple(method_names))

            if cache_key in group_cache:
                return group_cache[cache_key]
        except Exception:
            cache_key = None

        bulunan = None
        try:
            for method_name in method_names:
                method = getattr(dosya_secici, method_name, None)
                if callable(method):
                    bulunan = method
                    break
        except Exception:
            bulunan = None

        try:
            if cache_key is not None:
                self._editor_state_dosya_secici_method_cache[cache_key] = bulunan
        except Exception:
            pass

        return bulunan

    def _get_dosya_secici_attr(
        self,
        dosya_secici,
        attr_names: tuple[str, ...],
    ):
        """
        Dosya seçici üzerinde ilk uygun attribute adını bulur ve cache'ler.
        """
        if dosya_secici is None:
            return None

        self._ensure_editor_state_cache()

        cache_key = None

        try:
            object_id = id(dosya_secici)
            group_cache = self._editor_state_dosya_secici_attr_cache
            cache_key = (object_id, tuple(attr_names))

            if cache_key in group_cache:
                return group_cache[cache_key]
        except Exception:
            cache_key = None

        bulunan = None
        try:
            for attr_name in attr_names:
                if hasattr(dosya_secici, attr_name):
                    bulunan = attr_name
                    break
        except Exception:
            bulunan = None

        try:
            if cache_key is not None:
                self._editor_state_dosya_secici_attr_cache[cache_key] = bulunan
        except Exception:
            pass

        return bulunan

    def _selection_nesnesi_al(self):
        """
        Dosya seçiciden mevcut seçim nesnesini almaya çalışır.
        """
        try:
            dosya_secici = self._safe_getattr("dosya_secici", None)
            if dosya_secici is None:
                return None

            get_selection = self._get_dosya_secici_method(
                dosya_secici,
                ("get_selection", "selection", "secim", "get_secim"),
            )
            if callable(get_selection):
                return get_selection()
        except Exception:
            pass

        try:
            dosya_secici = self._safe_getattr("dosya_secici", None)
            if dosya_secici is None:
                return None

            attr_name = self._get_dosya_secici_attr(
                dosya_secici,
                (
                    "_selection",
                    "selection",
                    "_secim",
                    "secim",
                    "_current_selection",
                ),
            )
            if attr_name:
                return getattr(dosya_secici, attr_name, None)
        except Exception:
            pass

        return None

    def _selection_alani_oku(self, selection, alan_adlari: tuple[str, ...]) -> str:
        """
        Seçim nesnesinden verilen alan adlarından ilk dolu olanı okur.
        """
        if selection is None:
            return ""

        for alan in alan_adlari:
            try:
                deger = getattr(selection, alan, None)
                metin = self._coerce_text(deger).strip()
                if metin:
                    return metin
            except Exception:
                continue

        return ""

    # =========================================================
    # STATE COLLECTION
    # =========================================================
    def _collect_app_state(self) -> dict:
        """
        Root için RAM tabanlı geçici uygulama state sözlüğünü toplar.

        Toplanan alanlar:
        - current_file_path
        - selected_item_identity
        - editor_text
        - scroll_y
        - selection_identifier
        - selection_display_name
        - selection_source
        - selection_uri
        - selection_local_path
        - selection_mime_type
        """
        selection_identifier = ""
        selection_display_name = ""
        selection_source = ""
        selection_uri = ""
        selection_local_path = ""
        selection_mime_type = ""

        try:
            dosya_secici = self._safe_getattr("dosya_secici", None)
            if dosya_secici is not None:
                try:
                    get_path = self._get_dosya_secici_method(
                        dosya_secici,
                        ("get_path",),
                    )
                    if callable(get_path):
                        selection_identifier = self._coerce_text(
                            get_path()
                        ).strip()
                except Exception:
                    selection_identifier = ""

                try:
                    get_display_name = self._get_dosya_secici_method(
                        dosya_secici,
                        ("get_display_name",),
                    )
                    if callable(get_display_name):
                        selection_display_name = self._coerce_text(
                            get_display_name()
                        ).strip()
                except Exception:
                    selection_display_name = ""
        except Exception:
            pass

        try:
            selection = self._selection_nesnesi_al()

            selection_source = self._selection_alani_oku(
                selection,
                ("source", "kaynak", "picker_source"),
            )
            selection_uri = self._selection_alani_oku(
                selection,
                ("uri", "document_uri", "content_uri"),
            )
            selection_local_path = self._selection_alani_oku(
                selection,
                ("local_path", "path", "file_path"),
            )
            selection_mime_type = self._selection_alani_oku(
                selection,
                ("mime_type", "mime", "content_type"),
            )

            if not selection_display_name:
                selection_display_name = self._selection_alani_oku(
                    selection,
                    ("display_name", "name", "filename", "file_name"),
                )

            if not selection_identifier:
                selection_identifier = (
                    selection_uri
                    or selection_local_path
                    or self._selection_alani_oku(
                        selection,
                        ("identifier", "id", "selection_id"),
                    )
                )
        except Exception:
            pass

        state = {
            "current_file_path": self._coerce_text(
                self._safe_getattr("current_file_path", "")
            ),
            "selected_item_identity": self._selected_item_identity(),
            "editor_text": self._editor_text_al(),
            "scroll_y": None,
            "selection_identifier": selection_identifier,
            "selection_display_name": selection_display_name,
            "selection_source": selection_source,
            "selection_uri": selection_uri,
            "selection_local_path": selection_local_path,
            "selection_mime_type": selection_mime_type,
        }

        try:
            scroll = self._safe_getattr("scroll", None)
            if scroll is not None:
                state["scroll_y"] = float(scroll.scroll_y)
        except Exception:
            state["scroll_y"] = None

        return state
