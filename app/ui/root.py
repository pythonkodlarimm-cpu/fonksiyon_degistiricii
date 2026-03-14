# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/root.py

ROL:
- Uygulamanın ana root widget'ı
- Dosya seçme, fonksiyon tarama, seçim ve güncelleme akışını yönetir
- UI katmanını çekirdek servislerle bağlar

MİMARİ:
- Root çizim yapmaz
- Root sadece yerleşim + state + akış yönetir
- Görsel çizim alt bileşenlerin kendi içinde kalır

SURUM: 2
TARIH: 2026-03-14
IMZA: FY.
"""

from __future__ import annotations

import traceback

from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView

from app.core.degistirici import (
    find_item_by_identity,
    update_function_in_code,
)
from app.core.tarayici import scan_functions_from_file
from app.services.dosya_servisi import (
    backup_file,
    exists,
    read_text,
    write_text,
)
from app.ui.dosya_secici import DosyaSecici
from app.ui.durum_cubugu import DurumCubugu
from app.ui.editor_paneli import EditorPaneli
from app.ui.fonksiyon_listesi import FonksiyonListesi


class RootWidget(BoxLayout):
    """
    Uygulamanın ana kök arayüzü.

    Sorumluluklar:
    - dosya state yönetimi
    - fonksiyon listesini yenileme
    - seçim ve güncelleme akışını yürütme
    - alt bileşenler arası bağlantıyı kurma
    """

    def __init__(self, **kwargs):
        super().__init__(
            orientation="vertical",
            spacing=dp(8),
            padding=dp(8),
            **kwargs,
        )

        self.current_file_path = ""
        self.items = []
        self.selected_item = None

        self.scroll = None
        self.main_column = None
        self.dosya_secici = None
        self.function_list = None
        self.editor = None
        self.status = None

        try:
            self._build_ui()
            self._safe_set_status("Hazır.", "onaylandi.png")
        except Exception:
            hata = traceback.format_exc()
            print(hata)
            self.clear_widgets()
            self.add_widget(self._build_fallback_error_ui(hata))

    # =========================================================
    # UI
    # =========================================================
    def _build_ui(self) -> None:
        self.scroll = ScrollView(
            size_hint=(1, 1),
            do_scroll_x=False,
            do_scroll_y=True,
            bar_width=dp(8),
            scroll_type=["bars", "content"],
        )

        self.main_column = BoxLayout(
            orientation="vertical",
            spacing=dp(10),
            size_hint_y=None,
            padding=(0, 0, 0, dp(8)),
        )
        self.main_column.bind(minimum_height=self.main_column.setter("height"))

        self.dosya_secici = DosyaSecici(
            on_scan=self.scan_file,
            on_refresh=self.refresh_file,
        )
        self.dosya_secici.size_hint_y = None
        self.main_column.add_widget(self.dosya_secici)

        self.function_list = FonksiyonListesi(
            on_select=self.select_item,
        )
        self.function_list.size_hint_y = None
        self.main_column.add_widget(self.function_list)

        self.editor = EditorPaneli(
            on_update=self.update_selected_function,
        )
        self.editor.size_hint_y = None
        self.editor.height = dp(760)
        self.main_column.add_widget(self.editor)

        self.scroll.add_widget(self.main_column)
        self.add_widget(self.scroll)

        self.status = DurumCubugu()
        self.status.size_hint_y = None
        self.add_widget(self.status)

    def _build_fallback_error_ui(self, hata_metni: str) -> BoxLayout:
        root = BoxLayout(
            orientation="vertical",
            spacing=dp(10),
            padding=dp(12),
        )

        baslik = Label(
            text="RootWidget başlatılamadı",
            size_hint_y=None,
            height=dp(42),
            bold=True,
            halign="center",
            valign="middle",
            color=(1, 0.9, 0.9, 1),
        )
        baslik.bind(size=lambda inst, size: setattr(inst, "text_size", size))
        root.add_widget(baslik)

        mesaj = Label(
            text=hata_metni,
            halign="left",
            valign="top",
            color=(1, 0.85, 0.85, 1),
        )
        mesaj.bind(size=lambda inst, size: setattr(inst, "text_size", (size[0], None)))
        root.add_widget(mesaj)

        return root

    # =========================================================
    # HELPERS
    # =========================================================
    def _safe_set_status(self, text: str, icon_name: str = "") -> None:
        try:
            if self.status is not None:
                self.status.set_status(text, icon_name=icon_name)
        except Exception:
            pass

    def set_status(self, text: str, icon_name: str = "") -> None:
        self._safe_set_status(text, icon_name=icon_name)

    def _clear_state(self) -> None:
        self.current_file_path = ""
        self.items = []
        self.selected_item = None

        try:
            if self.function_list is not None:
                self.function_list.set_items([])
        except Exception:
            pass

        try:
            if self.function_list is not None:
                self.function_list.set_selected_preview("")
        except Exception:
            pass

        try:
            if self.function_list is not None:
                self.function_list.set_new_preview("")
        except Exception:
            pass

        try:
            if self.editor is not None:
                self.editor.set_item(None)
        except Exception:
            pass

    def _reset_selection_only(self) -> None:
        self.selected_item = None

        try:
            if self.function_list is not None:
                self.function_list.selected_item = None
                self.function_list.set_selected_preview("")
                self.function_list.set_new_preview("")
        except Exception:
            pass

        try:
            if self.editor is not None:
                self.editor.set_item(None)
        except Exception:
            pass

    def _safe_backup_text(self, backup_path) -> str:
        metin = str(backup_path or "").strip()
        return metin if metin else "yedek_bilinmiyor"

    def _reload_items_from_current_file(self) -> None:
        if not self.current_file_path:
            self.items = []
            try:
                if self.function_list is not None:
                    self.function_list.set_items([])
            except Exception:
                pass
            return

        self.items = scan_functions_from_file(self.current_file_path)

        try:
            if self.function_list is not None:
                self.function_list.set_items(self.items)
        except Exception:
            pass

    def _find_refreshed_item(self, old_item):
        if old_item is None:
            return None

        refreshed = find_item_by_identity(
            self.items,
            path=str(getattr(old_item, "path", "") or ""),
            name=str(getattr(old_item, "name", "") or ""),
            lineno=int(getattr(old_item, "lineno", 0) or 0),
            kind=str(getattr(old_item, "kind", "") or ""),
        )
        if refreshed is not None:
            return refreshed

        old_path = str(getattr(old_item, "path", "") or "")
        old_end_lineno = int(getattr(old_item, "end_lineno", 0) or 0)
        old_signature = str(getattr(old_item, "signature", "") or "").strip()

        for current in self.items:
            if (
                str(getattr(current, "path", "") or "") == old_path
                and int(getattr(current, "end_lineno", 0) or 0) == old_end_lineno
            ):
                return current

        for current in self.items:
            if (
                str(getattr(current, "path", "") or "") == old_path
                and str(getattr(current, "signature", "") or "").strip() == old_signature
            ):
                return current

        return None

    # =========================================================
    # DOSYA AKIŞI
    # =========================================================
    def refresh_file(self, file_path: str) -> None:
        self.scan_file(file_path)

    def scan_file(self, file_path: str) -> None:
        try:
            temiz_yol = str(file_path or "").strip()

            if not temiz_yol:
                self._clear_state()
                self.set_status("Dosya seçilmedi.", "warning.png")
                return

            if not exists(temiz_yol):
                self._clear_state()
                self.set_status("Dosya bulunamadı.", "warning.png")
                return

            self.current_file_path = temiz_yol
            self._reload_items_from_current_file()
            self._reset_selection_only()

            self.set_status(
                f"Tarama tamamlandı. {len(self.items)} fonksiyon bulundu.",
                "search.png",
            )

        except ValueError as exc:
            self._clear_state()
            self.set_status(str(exc), "warning.png")
        except SyntaxError as exc:
            self._clear_state()
            self.set_status(f"SyntaxError: {exc}", "warning.png")
        except Exception:
            self._clear_state()
            self.set_status("Tarama hatası oluştu.", "warning.png")
            print(traceback.format_exc())

    # =========================================================
    # SEÇİM
    # =========================================================
    def select_item(self, item) -> None:
        self.selected_item = item

        try:
            if self.editor is not None:
                self.editor.set_item(item)
        except Exception:
            pass

        try:
            if self.function_list is not None:
                self.function_list.set_selected_preview(
                    str(getattr(item, "source", "") or "")
                )
        except Exception:
            pass

        try:
            self.set_status(f"Seçildi: {item.path}", "visibility_on.png")
        except Exception:
            self.set_status("Fonksiyon seçildi.", "visibility_on.png")

    # =========================================================
    # GÜNCELLEME
    # =========================================================
    def update_selected_function(self, item, new_code: str) -> None:
        try:
            if not self.current_file_path:
                self.set_status("Önce dosya seç.", "warning.png")
                return

            if not exists(self.current_file_path):
                self.set_status("Seçili dosya artık bulunamadı.", "warning.png")
                return

            if item is None:
                self.set_status("Önce bir fonksiyon seç.", "warning.png")
                return

            if not str(new_code or "").strip():
                self.set_status("Yeni fonksiyon kodu boş olamaz.", "warning.png")
                return

            try:
                if self.function_list is not None:
                    self.function_list.set_new_preview(str(new_code or ""))
            except Exception:
                pass

            old_source = read_text(self.current_file_path)
            if not isinstance(old_source, str):
                self.set_status("Kaynak dosya okunamadı.", "warning.png")
                return

            backup_path = backup_file(self.current_file_path)
            updated_source = update_function_in_code(old_source, item, new_code)
            write_text(self.current_file_path, updated_source)

            self._reload_items_from_current_file()

            refreshed = self._find_refreshed_item(item)
            self.selected_item = refreshed

            try:
                if self.editor is not None:
                    self.editor.set_item(refreshed)
            except Exception:
                pass

            try:
                if self.function_list is not None:
                    self.function_list.selected_item = refreshed
                    self.function_list.set_items(self.items)
                    self.function_list.set_selected_preview(
                        str(getattr(refreshed, "source", "") or "")
                    )
                    self.function_list.set_new_preview(str(new_code or ""))
            except Exception:
                pass

            backup_text = self._safe_backup_text(backup_path)

            if refreshed is not None:
                self.set_status(
                    f"Güncellendi: {refreshed.path} | Yedek: {backup_text}",
                    "onaylandi.png",
                )
            else:
                self.set_status(
                    f"Güncellendi. Seçim yenilenemedi ama dosya yazıldı. Yedek: {backup_text}",
                    "onaylandi.png",
                )

        except ValueError as exc:
            self.set_status(str(exc), "warning.png")
        except SyntaxError as exc:
            self.set_status(f"Sözdizimi hatası: {exc}", "warning.png")
        except Exception:
            self.set_status("Güncelleme hatası oluştu.", "warning.png")
            print(traceback.format_exc())