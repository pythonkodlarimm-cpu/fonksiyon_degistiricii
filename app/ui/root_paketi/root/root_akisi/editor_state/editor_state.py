# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/root_paketi/root/root_akisi/editor_state/editor_state.py

ROL:
- Root katmanında editör state okuma/yazma yardımcılarını toplar
- Editör içeriğini uyumlu şekilde alır ve yazar
- Seçili item için tekrar bulunabilir kimlik üretir
- Dosya seçiciden mevcut seçim bilgilerini toplar
- Root için RAM tabanlı geçici uygulama state sözlüğü üretir

MİMARİ:
- Bu modül mixin mantığıyla çalışır
- RootWidget içinde kullanılan editör state yardımcı metodlarını sağlar
- UI çizimi yapmaz
- Dil servisi yönetmez
- Disk yazımı yapmaz
- Tarama veya geri yükleme yürütmez

NOT:
- Amaç tek bir büyük “her şeyi yapan” yapı kurmak değil,
  editör-state odaklı yardımcıları tek yerde tutmaktır
- Dış davranış korunmuştur
- Fail-soft yaklaşım korunmuştur

SURUM: 5
TARIH: 2026-03-27
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

    _EDITOR_OKUMA_METODLARI = (
        "get_text",
        "metni_al",
        "icerik_al",
        "kod_al",
    )

    _EDITOR_YAZMA_METODLARI = (
        "set_text",
        "metni_yaz",
        "icerik_yaz",
        "kod_yaz",
    )

    _EDITOR_METIN_ALANLARI = (
        "text",
        "metin",
        "content",
        "icerik",
        "code",
    )

    _ITEM_KIMLIK_ALANLARI = (
        "identity",
        "full_path",
        "dotted_path",
        "path",
        "name",
    )

    _DOSYA_SECICI_SECIM_METODLARI = (
        "get_selection",
        "selection",
        "secim",
        "get_secim",
    )

    _DOSYA_SECICI_SECIM_ALANLARI = (
        "_selection",
        "selection",
        "_secim",
        "secim",
        "_current_selection",
    )

    def _safe_getattr(self, nesne_adi: str, varsayilan=None):
        """
        Root üzerinde güvenli getattr çağrısı yapar.
        """
        try:
            return getattr(self, nesne_adi, varsayilan)
        except Exception:
            return varsayilan

    def _metne_cevir(self, deger) -> str:
        """
        Gelen değeri güvenli şekilde metne çevirir.
        """
        try:
            return str(deger or "")
        except Exception:
            return ""

    def _ilk_cagrilabilir_metod(self, nesne, metod_adlari: tuple[str, ...]):
        """
        Verilen nesnede bulunan ilk callable metodu döndürür.
        """
        if nesne is None:
            return None

        for metod_adi in metod_adlari:
            try:
                metod = getattr(nesne, metod_adi, None)
                if callable(metod):
                    return metod
            except Exception:
                continue

        return None

    def _ilk_mevcut_attr_adi(
        self,
        nesne,
        attr_adlari: tuple[str, ...],
        *,
        yalnizca_string: bool = False,
    ):
        """
        Verilen nesnede ilk uygun attribute adını döndürür.
        """
        if nesne is None:
            return None

        for attr_adi in attr_adlari:
            try:
                if not hasattr(nesne, attr_adi):
                    continue

                if yalnizca_string:
                    deger = getattr(nesne, attr_adi, None)
                    if not isinstance(deger, str):
                        continue

                return attr_adi
            except Exception:
                continue

        return None

    def _editor_nesnesi_al(self):
        """
        Root üzerinden editör nesnesini döndürür.
        """
        return self._safe_getattr("editor", None)

    def _editor_input_al(self):
        """
        Editör içindeki editor_input benzeri alanı döndürür.
        """
        editor = self._editor_nesnesi_al()
        if editor is None:
            return None

        try:
            return getattr(editor, "editor_input", None)
        except Exception:
            return None

    def _editor_text_al(self) -> str:
        """
        Editördeki mevcut metni uyumlu biçimde okur.

        Öncelik sırası:
        1) get_text / metni_al / icerik_al / kod_al
        2) text / metin / content / icerik / code
        3) editor_input.text
        """
        editor = self._editor_nesnesi_al()
        if editor is None:
            return ""

        metod = self._ilk_cagrilabilir_metod(editor, self._EDITOR_OKUMA_METODLARI)
        if callable(metod):
            try:
                return self._metne_cevir(metod())
            except Exception:
                pass

        attr_adi = self._ilk_mevcut_attr_adi(
            editor,
            self._EDITOR_METIN_ALANLARI,
            yalnizca_string=True,
        )
        if attr_adi:
            try:
                return getattr(editor, attr_adi, "")
            except Exception:
                pass

        editor_input = self._editor_input_al()
        if editor_input is not None:
            try:
                return self._metne_cevir(getattr(editor_input, "text", ""))
            except Exception:
                pass

        return ""

    def _editor_text_yaz(self, text: str) -> None:
        """
        Editöre metin yazar.

        Öncelik sırası:
        1) set_text / metni_yaz / icerik_yaz / kod_yaz
        2) editor_input.text
        3) text / metin / content / icerik / code
        """
        editor = self._editor_nesnesi_al()
        if editor is None:
            return

        temiz_metin = self._metne_cevir(text)

        metod = self._ilk_cagrilabilir_metod(editor, self._EDITOR_YAZMA_METODLARI)
        if callable(metod):
            try:
                metod(temiz_metin)
                return
            except Exception:
                pass

        editor_input = self._editor_input_al()
        if editor_input is not None:
            try:
                if hasattr(editor_input, "text"):
                    editor_input.text = temiz_metin
                    return
            except Exception:
                pass

        attr_adi = self._ilk_mevcut_attr_adi(
            editor,
            self._EDITOR_METIN_ALANLARI,
            yalnizca_string=False,
        )
        if attr_adi:
            try:
                setattr(editor, attr_adi, temiz_metin)
                return
            except Exception:
                pass

        for attr_adi in self._EDITOR_METIN_ALANLARI:
            try:
                if hasattr(editor, attr_adi):
                    setattr(editor, attr_adi, temiz_metin)
                    return
            except Exception:
                continue

    def _selected_item_identity(self) -> str:
        """
        Mevcut seçili item için tekrar bulunabilir kimlik değeri üretir.
        """
        selected_item = self._safe_getattr("selected_item", None)
        if selected_item is None:
            return ""

        for attr_adi in self._ITEM_KIMLIK_ALANLARI:
            try:
                deger = getattr(selected_item, attr_adi, None)
                if deger:
                    return str(deger)
            except Exception:
                continue

        return ""

    def _find_item_by_identity_value(self, identity: str):
        """
        Kaydedilmiş kimlik değerine göre self.items içinde eşleşen item'i arar.
        """
        aranan = self._metne_cevir(identity).strip()
        if not aranan:
            return None

        tum_itemler = self._safe_getattr("items", []) or []

        for item in list(tum_itemler):
            try:
                for attr_adi in self._ITEM_KIMLIK_ALANLARI:
                    try:
                        deger = getattr(item, attr_adi, None)
                        if self._metne_cevir(deger).strip() == aranan:
                            return item
                    except Exception:
                        continue
            except Exception:
                continue

        return None

    def _dosya_secici_al(self):
        """
        Root üzerinden dosya seçici nesnesini döndürür.
        """
        return self._safe_getattr("dosya_secici", None)

    def _selection_nesnesi_al(self):
        """
        Dosya seçiciden mevcut seçim nesnesini almaya çalışır.
        """
        dosya_secici = self._dosya_secici_al()
        if dosya_secici is None:
            return None

        metod = self._ilk_cagrilabilir_metod(
            dosya_secici,
            self._DOSYA_SECICI_SECIM_METODLARI,
        )
        if callable(metod):
            try:
                return metod()
            except Exception:
                pass

        attr_adi = self._ilk_mevcut_attr_adi(
            dosya_secici,
            self._DOSYA_SECICI_SECIM_ALANLARI,
            yalnizca_string=False,
        )
        if attr_adi:
            try:
                return getattr(dosya_secici, attr_adi, None)
            except Exception:
                pass

        return None

    def _selection_alani_oku(self, selection, alan_adlari: tuple[str, ...]) -> str:
        """
        Seçim nesnesinden verilen alan adlarından ilk dolu olanı okur.
        """
        if selection is None:
            return ""

        for alan_adi in alan_adlari:
            try:
                deger = getattr(selection, alan_adi, None)
                metin = self._metne_cevir(deger).strip()
                if metin:
                    return metin
            except Exception:
                continue

        return ""

    def _dosya_secici_metod_sonucu(self, metod_adi: str) -> str:
        """
        Dosya seçicide verilen metod varsa çağırır ve sonucunu metne çevirir.
        """
        dosya_secici = self._dosya_secici_al()
        if dosya_secici is None:
            return ""

        try:
            metod = getattr(dosya_secici, metod_adi, None)
            if callable(metod):
                return self._metne_cevir(metod()).strip()
        except Exception:
            pass

        return ""

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
        selection_identifier = self._dosya_secici_metod_sonucu("get_path")
        selection_display_name = self._dosya_secici_metod_sonucu("get_display_name")
        selection_source = ""
        selection_uri = ""
        selection_local_path = ""
        selection_mime_type = ""

        selection = self._selection_nesnesi_al()
        if selection is not None:
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

        state = {
            "current_file_path": self._metne_cevir(
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

        scroll = self._safe_getattr("scroll", None)
        if scroll is not None:
            try:
                state["scroll_y"] = float(scroll.scroll_y)
            except Exception:
                state["scroll_y"] = None

        return state
