# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/root.py

ROL:
- Uygulamanın ana root widget'ı
- Dosya seçme, fonksiyon tarama, seçim, güncelleme ve geri yükleme akışını yönetir
- UI katmanını çekirdek servislerle bağlar

MİMARİ:
- Root çizim yapmaz
- Root sadece yerleşim + state + akış yönetir
- Görsel çizim alt bileşenlerin kendi içinde kalır

SURUM: 14
TARIH: 2026-03-16
IMZA: FY.
"""

from __future__ import annotations

import traceback
from pathlib import Path

from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.utils import platform

from app.core.degistirici import find_item_by_identity
from app.core.degistirici import update_function_in_code
from app.core.tarayici import scan_functions_from_file
from app.services.belge_geri_yukleme_servisi import (
    BelgeGeriYuklemeServisiHatasi,
    son_yedekten_geri_yukle,
)
from app.services.belge_oturumu_servisi import (
    BelgeOturumuServisiHatasi,
    calisma_dosyasi_yolu,
    calisma_kopyasi_var_mi,
    guncellenmis_icerigi_kaydet,
    oturum_baslat,
    oturum_display_name,
    oturum_identifier,
    son_yedek_yolu,
)
from app.services.dosya_servisi import read_text
from app.ui.dosya_secici import DosyaSecici
from app.ui.dosya_secici_paketi.models import DocumentSelection
from app.ui.durum_cubugu import DurumCubugu
from app.ui.editor_paneli import EditorPaneli
from app.ui.fonksiyon_listesi import FonksiyonListesi
from app.ui.kart import Kart
from app.ui.tum_dosya_erisim_paneli import TumDosyaErisimPaneli


class RootWidget(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(
            orientation="vertical",
            spacing=dp(8),
            padding=dp(8),
            **kwargs,
        )

        self.current_file_path = ""
        self.current_session = None
        self.items = []
        self.selected_item = None

        self.scroll = None
        self.main_column = None
        self.file_access_panel = None
        self.dosya_secici = None
        self.function_list = None
        self.editor = None
        self.status = None
        self.version_wrap = None
        self.version_label = None
        self.bottom_bar = None
        self.app_version_text = self._resolve_app_version()

        try:
            self._build_ui()
            self.set_status_info("Hazır.", "onaylandi.png")
        except Exception:
            hata = traceback.format_exc()
            print(hata)
            self.clear_widgets()
            self.add_widget(self._build_fallback_error_ui(hata))

    # =========================================================
    # DEBUG
    # =========================================================
    def _debug(self, message: str) -> None:
        try:
            print("[ROOT]", str(message))
        except Exception:
            pass

    # =========================================================
    # VERSION
    # =========================================================
    def _resolve_app_version(self) -> str:
        if platform == "android":
            try:
                from jnius import autoclass, cast  # type: ignore

                PythonActivity = autoclass("org.kivy.android.PythonActivity")
                current_activity = cast("android.app.Activity", PythonActivity.mActivity)
                package_info = current_activity.getPackageManager().getPackageInfo(
                    current_activity.getPackageName(),
                    0,
                )
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

    def _build_version_card(self) -> Kart:
        kart = Kart(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(28),
            padding=(dp(10), dp(4), dp(10), dp(4)),
            bg=(0.07, 0.09, 0.13, 1),
            border=(0.16, 0.19, 0.25, 1),
            radius=12,
        )

        spacer = Label(size_hint_x=1)
        kart.add_widget(spacer)

        self.version_label = Label(
            text=f"Sürüm: {self.app_version_text}",
            size_hint_x=None,
            width=dp(120),
            font_size="11sp",
            color=(0.72, 0.72, 0.76, 1),
            halign="right",
            valign="middle",
        )
        self.version_label.bind(size=lambda inst, size: setattr(inst, "text_size", size))
        kart.add_widget(self.version_label)

        return kart

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

        self.file_access_panel = TumDosyaErisimPaneli(
            on_status_changed=self._on_file_access_status_changed,
        )
        self.file_access_panel.size_hint_y = None
        self.main_column.add_widget(self.file_access_panel)

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
            on_restore=self.geri_yukle_secili_belge,
        )
        self.editor.size_hint_y = None
        self.editor.height = dp(820)
        self.main_column.add_widget(self.editor)

        self.scroll.add_widget(self.main_column)
        self.add_widget(self.scroll)

        self.bottom_bar = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=dp(4),
            padding=(0, dp(2), 0, 0),
        )

        self.status = DurumCubugu()
        self.status.size_hint_y = None
        self.bottom_bar.add_widget(self.status)

        self.version_wrap = self._build_version_card()
        self.bottom_bar.add_widget(self.version_wrap)

        self.bottom_bar.height = int(self.status.height) + int(self.version_wrap.height) + int(dp(4))
        self.add_widget(self.bottom_bar)

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
    # STATUS HELPERS
    # =========================================================
    def _safe_set_status(self, text: str, icon_name: str = "") -> None:
        try:
            if self.status is not None:
                self.status.set_status(text, icon_name=icon_name)
        except Exception:
            pass

    def set_status(self, text: str, icon_name: str = "") -> None:
        self._safe_set_status(text, icon_name)

    def set_status_info(self, text: str, icon_name: str = "") -> None:
        try:
            if self.status is not None:
                self.status.set_status(text, icon_name=icon_name)
        except Exception:
            pass

    def set_status_success(self, text: str) -> None:
        try:
            if self.status is not None:
                self.status.set_success(text)
        except Exception:
            pass

    def set_status_warning(self, text: str) -> None:
        try:
            if self.status is not None:
                self.status.set_warning(text)
        except Exception:
            pass

    def set_status_error(self, text: str) -> None:
        try:
            if self.status is not None:
                self.status.set_error(text)
        except Exception:
            pass

    def _on_file_access_status_changed(self, durum: bool) -> None:
        try:
            if durum:
                self.set_status_success("Tüm dosya erişimi açık.")
            else:
                self.set_status_warning("Tüm dosya erişimi kapalı.")
        except Exception:
            pass

    # =========================================================
    # HELPERS
    # =========================================================
    def _clear_state(self) -> None:
        self.current_file_path = ""
        self.current_session = None
        self.items = []
        self.selected_item = None

        try:
            self.dosya_secici.clear_selection()
        except Exception:
            pass

        try:
            self.function_list.clear_all()
        except Exception:
            pass

        try:
            self.editor.clear_all()
        except Exception:
            pass

    def _clear_view_only(self) -> None:
        self.items = []
        self.selected_item = None

        try:
            self.function_list.clear_all()
        except Exception:
            pass

        try:
            self.editor.clear_all()
        except Exception:
            pass

    def _reset_selection_only(self) -> None:
        self.selected_item = None

        try:
            self.function_list.clear_selection()
            self.function_list.clear_new_preview()
        except Exception:
            pass

        try:
            self.editor.clear_selection()
            self.editor.set_new_code_text("")
        except Exception:
            pass

    def _safe_backup_text(self) -> str:
        try:
            metin = str(son_yedek_yolu(self.current_session) or "").strip()
            if metin:
                return metin
        except Exception:
            pass
        return "yedek_bilinmiyor"

    def _reload_items_from_current_file(self) -> None:
        if not self.current_file_path:
            self.items = []
            try:
                self.function_list.clear_all()
            except Exception:
                pass
            return

        self.items = scan_functions_from_file(self.current_file_path)

        try:
            self.function_list.set_items(self.items)
        except Exception:
            pass

    def _selection_from_ui(self):
        try:
            secim = self.dosya_secici.get_selection()
            if secim is not None:
                return secim
        except Exception:
            pass

        try:
            ham = str(self.dosya_secici.get_path() or "").strip()
            if ham and Path(ham).exists() and Path(ham).is_file():
                return DocumentSelection(
                    source="filesystem",
                    uri="",
                    local_path=ham,
                    display_name=Path(ham).name,
                    mime_type="",
                )
        except Exception:
            pass

        return None

    # =========================================================
    # DOSYA AKIŞI
    # =========================================================
    def _scan_or_refresh(self, _ignored_file_path: str) -> None:
        selection = self._selection_from_ui()
        if selection is None:
            self._clear_state()
            self.set_status_warning("Dosya seçilmedi.")
            return

        try:
            session = oturum_baslat(selection)
        except BelgeOturumuServisiHatasi as exc:
            self._clear_state()
            self.set_status_error(f"Oturum başlatılamadı: {exc}")
            return

        working_path = str(calisma_dosyasi_yolu(session) or "").strip()
        source_identifier = str(oturum_identifier(session) or "").strip()
        display_name = str(oturum_display_name(session) or "").strip()

        if not working_path:
            self._clear_state()
            self.set_status_error("Çalışma dosyası oluşturulamadı.")
            return

        self.current_session = session
        self.current_file_path = working_path

        if not calisma_kopyasi_var_mi(session):
            self.set_status_error("Çalışma dosyası bulunamadı.")
            return

        try:
            self.dosya_secici.set_path(source_identifier or working_path)
        except Exception:
            pass

        self._clear_view_only()
        self._reload_items_from_current_file()
        self._reset_selection_only()

        if display_name:
            self.set_status_success(
                f"Tarama tamamlandı. {len(self.items)} fonksiyon bulundu. Belge: {display_name}"
            )
        else:
            self.set_status_success(
                f"Tarama tamamlandı. {len(self.items)} fonksiyon bulundu."
            )

    def refresh_file(self, file_path: str) -> None:
        try:
            self._scan_or_refresh(file_path)
        except Exception:
            self._clear_state()
            self.set_status_error("Yenileme hatası oluştu.")
            print(traceback.format_exc())

    def scan_file(self, file_path: str) -> None:
        try:
            self._scan_or_refresh(file_path)
        except Exception:
            self._clear_state()
            self.set_status_error("Tarama hatası oluştu.")
            print(traceback.format_exc())

    # =========================================================
    # SEÇİM
    # =========================================================
    def select_item(self, item) -> None:
        self.selected_item = item

        try:
            self.editor.set_item(item)
            self.editor.set_new_code_text("")
        except Exception:
            pass

        try:
            self.function_list.set_selected_preview(str(getattr(item, "source", "") or ""))
            self.function_list.clear_new_preview()
        except Exception:
            pass

        try:
            self.set_status_info(f"Seçildi: {item.path}", "visibility_on.png")
        except Exception:
            self.set_status_info("Fonksiyon seçildi.", "visibility_on.png")

    # =========================================================
    # HELPERS
    # =========================================================
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
    # GÜNCELLEME
    # =========================================================
    def update_selected_function(self, item, new_code: str) -> None:
        try:
            if self.current_session is None:
                self.set_status_warning("Önce dosya seç.")
                return

            if not self.current_file_path:
                self.current_file_path = str(calisma_dosyasi_yolu(self.current_session) or "").strip()

            if not self.current_file_path or not calisma_kopyasi_var_mi(self.current_session):
                self.set_status_error("Çalışma dosyası artık bulunamadı.")
                return

            if item is None:
                self.set_status_warning("Önce bir fonksiyon seç.")
                return

            if not str(new_code or "").strip():
                self.set_status_warning("Yeni fonksiyon kodu boş olamaz.")
                return

            try:
                self.function_list.set_new_preview(str(new_code or ""))
            except Exception:
                pass

            try:
                self.editor.set_new_code_text(str(new_code or ""))
            except Exception:
                pass

            old_source = read_text(self.current_file_path)
            updated_source = update_function_in_code(old_source, item, new_code)
            backup_path = guncellenmis_icerigi_kaydet(self.current_session, updated_source)

            self._reload_items_from_current_file()

            refreshed = self._find_refreshed_item(item)
            self.selected_item = refreshed

            try:
                self.function_list.set_items(self.items)
                self.function_list.selected_item = refreshed
                self.function_list.set_selected_preview(str(getattr(refreshed, "source", "") or ""))
                self.function_list.set_new_preview(str(new_code or ""))
            except Exception:
                pass

            try:
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
                    f"Güncellendi. Seçim yenilenemedi ama dosya yazıldı. Yedek: {backup_text}"
                )

        except BelgeOturumuServisiHatasi as exc:
            self.set_status_error(str(exc))
        except ValueError as exc:
            self.set_status_error(str(exc))
        except SyntaxError as exc:
            self.set_status_error(f"Sözdizimi hatası: {exc}")
        except Exception:
            self.set_status_error("Güncelleme hatası oluştu.")
            print(traceback.format_exc())

    # =========================================================
    # GERİ YÜKLEME
    # =========================================================
    def geri_yukle_secili_belge(self) -> None:
        try:
            if self.current_session is None:
                self.set_status_warning("Önce dosya seç.")
                return

            backup_path = str(getattr(self.current_session, "last_backup_path", "") or "").strip()
            if not backup_path:
                self.set_status_warning("Geri yüklenecek yedek bulunamadı.")
                return

            geri_yuklenen = son_yedekten_geri_yukle(self.current_session)

            try:
                self.current_file_path = str(calisma_dosyasi_yolu(self.current_session) or "").strip()
            except Exception:
                pass

            self._clear_view_only()
            self._reload_items_from_current_file()
            self._reset_selection_only()

            self.set_status_success(f"Geri yüklendi. Yedek: {geri_yuklenen}")

        except BelgeGeriYuklemeServisiHatasi as exc:
            self.set_status_error(str(exc))
        except Exception:
            self.set_status_error("Geri yükleme hatası oluştu.")
            print(traceback.format_exc())
