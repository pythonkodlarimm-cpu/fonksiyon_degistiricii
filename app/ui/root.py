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

SURUM: 7
TARIH: 2026-03-15
IMZA: FY.
"""

from __future__ import annotations

import traceback

from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.utils import platform

from app.core.degistirici import find_item_by_identity
from app.core.degistirici import update_function_in_code
from app.core.tarayici import scan_functions_from_file
from app.services.dosya_servisi import exists
from app.services.dosya_servisi import read_text
from app.services.dosya_servisi import safe_write_with_backup
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
        self.version_label = None
        self.app_version_text = self._resolve_app_version()

        try:
            self._build_ui()
            self._safe_set_status("Hazır.", "onaylandi.png")
        except Exception:
            hata = traceback.format_exc()
            print(hata)
            self.clear_widgets()
            self.add_widget(self._build_fallback_error_ui(hata))

    # =========================================================
    # VERSION
    # =========================================================
    def _resolve_app_version(self) -> str:
        """
        Uygulama sürümünü mümkünse Android APK içinden otomatik okur.
        Masaüstünde/fallback durumda geliştirici sürümü döner.
        """
        if platform == "android":
            try:
                from jnius import autoclass, cast  # type: ignore

                PythonActivity = autoclass("org.kivy.android.PythonActivity")
                current_activity = cast("android.app.Activity", PythonActivity.mActivity)
                package_manager = current_activity.getPackageManager()
                package_name = current_activity.getPackageName()
                package_info = package_manager.getPackageInfo(package_name, 0)
                version_name = str(getattr(package_info, "versionName", "") or "").strip()

                if version_name:
                    return version_name
            except Exception:
                pass

        try:
            from app import __version__ as app_version  # type: ignore

            temiz = str(app_version or "").strip()
            if temiz:
                return temiz
        except Exception:
            pass

        return "GELISTIRME"

    def _build_version_label(self) -> Label:
        lbl = Label(
            text=f"Sürüm: {self.app_version_text}",
            size_hint_y=None,
            height=dp(20),
            font_size="11sp",
            color=(0.72, 0.72, 0.76, 1),
            halign="right",
            valign="middle",
        )
        lbl.bind(size=lambda inst, size: setattr(inst, "text_size", size))
        return lbl

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

        alt_bar = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=dp(2),
        )

        self.status = DurumCubugu()
        self.status.size_hint_y = None
        alt_bar.add_widget(self.status)

        self.version_label = self._build_version_label()
        alt_bar.add_widget(self.version_label)

        toplam_yukseklik = 0
        try:
            toplam_yukseklik += int(self.status.height)
        except Exception:
            toplam_yukseklik += int(dp(40))

        try:
            toplam_yukseklik += int(self.version_label.height)
        except Exception:
            toplam_yukseklik += int(dp(20))

        toplam_yukseklik += int(dp(2))
        alt_bar.height = toplam_yukseklik

        self.add_widget(alt_bar)

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

    def _current_or_selector_path(self, file_path: str = "") -> str:
        temiz = str(file_path or "").strip()
        if temiz:
            return temiz

        try:
            if self.dosya_secici is not None:
                alternatif = str(self.dosya_secici.get_path() or "").strip()
                if alternatif:
                    return alternatif
        except Exception:
            pass

        return ""

    def _clear_state(self) -> None:
        self.current_file_path = ""
        self.items = []
        self.selected_item = None

        try:
            if self.dosya_secici is not None:
                self.dosya_secici.set_path("")
        except Exception:
            pass

        try:
            if self.function_list is not None:
                self.function_list.clear_all()
        except Exception:
            pass

        try:
            if self.editor is not None:
                self.editor.clear_all()
        except Exception:
            pass

    def _clear_view_only(self) -> None:
        self.items = []
        self.selected_item = None

        try:
            if self.function_list is not None:
                self.function_list.clear_all()
        except Exception:
            pass

        try:
            if self.editor is not None:
                self.editor.clear_all()
        except Exception:
            pass

    def _reset_selection_only(self) -> None:
        self.selected_item = None

        try:
            if self.function_list is not None:
                self.function_list.clear_selection()
                self.function_list.clear_new_preview()
        except Exception:
            pass

        try:
            if self.editor is not None:
                self.editor.clear_selection()
                self.editor.set_new_code_text("")
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
                    self.function_list.clear_all()
            except Exception:
                pass
            return

        self.items = scan_functions_from_file(self.current_file_path)

        try:
            if self.function_list is not None:
                self.function_list.set_items(self.items)
            else:
                pass
        except Exception:
            pass

    def _scan_or_refresh(self, file_path: str) -> None:
        temiz_yol = self._current_or_selector_path(file_path)

        if not temiz_yol:
            self._clear_state()
            self.set_status("Dosya seçilmedi.", "warning.png")
            return

        if not exists(temiz_yol):
            self._clear_state()
            self.set_status("Dosya bulunamadı.", "warning.png")
            return

        self.current_file_path = temiz_yol

        try:
            if self.dosya_secici is not None:
                self.dosya_secici.set_path(temiz_yol)
        except Exception:
            pass

        self._clear_view_only()
        self._reload_items_from_current_file()
        self._reset_selection_only()

        self.set_status(
            f"Tarama tamamlandı. {len(self.items)} fonksiyon bulundu.",
            "search.png",
        )

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
        try:
            self._scan_or_refresh(file_path)
        except ValueError as exc:
            self._clear_state()
            self.set_status(str(exc), "warning.png")
        except SyntaxError as exc:
            self._clear_state()
            self.set_status(f"SyntaxError: {exc}", "warning.png")
        except Exception:
            self._clear_state()
            self.set_status("Yenileme hatası oluştu.", "warning.png")
            print(traceback.format_exc())

    def scan_file(self, file_path: str) -> None:
        try:
            self._scan_or_refresh(file_path)
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
                self.editor.set_new_code_text("")
        except Exception:
            pass

        try:
            if self.function_list is not None:
                self.function_list.set_selected_preview(
                    str(getattr(item, "source", "") or "")
                )
                self.function_list.clear_new_preview()
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
                self.current_file_path = self._current_or_selector_path("")

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

            try:
                if self.editor is not None:
                    self.editor.set_new_code_text(str(new_code or ""))
            except Exception:
                pass

            old_source = read_text(self.current_file_path)
            if not isinstance(old_source, str):
                self.set_status("Kaynak dosya okunamadı.", "warning.png")
                return

            updated_source = update_function_in_code(old_source, item, new_code)
            backup_path = safe_write_with_backup(self.current_file_path, updated_source)

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