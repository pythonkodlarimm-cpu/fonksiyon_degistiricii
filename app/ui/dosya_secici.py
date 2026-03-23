# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/dosya_secici.py

ROL:
- Dosya seçici UI organizatörü
- Dosya Seç aksiyonunu yönetir
- Platforma göre uygun picker'ı yöneticisi üzerinden çağırır
- Seçilen belgeyi üst katmana bildirir
- Geliştirici modunda test dosya seçimini destekler
- Aktif dile göre görünür metinleri üretir ve yeniler

MİMARİ:
- UI burada tutulur
- Picker, popup, model ve geliştirici mod erişimi DosyaSeciciYoneticisi üzerinden yürür
- Alt modüller doğrudan import edilmez
- Ağır modüller uygulama açılışında yüklenmez
- Kullanıcıya görünen metinler services -> sistem -> dil_servisi zincirinden alınır

DAVRANIŞ:
- Uygulama açılışında büyük Dosya Seç ikonu görünür
- Dosya Seç ile picker açılır
- Dosya seçildikten sonra otomatik tarama tek sefer tetiklenir
- Ham URI ekranda ana metin olarak gösterilmez
- Dosya adı ve kısa durum bilgisi öne çıkarılır
- DEV_MODE açıksa Test butonu da görünür
- Dil değiştiğinde apply_language çağrısıyla görünür metinler güncellenebilir

API UYUMLULUK:
- Android tarafında sistem picker yalnızca yöneticisi üzerinden çağrılır
- Dosya seçimi sonrası identifier ve display name güvenli şekilde normalize edilir
- API 35 uyumludur
- Çoklu otomatik tetikleme kaldırılmıştır, tek güvenli tetikleme korunur

SURUM: 37
TARIH: 2026-03-23
IMZA: FY.
"""

from __future__ import annotations

from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

from app.ui.dosya_secici_paketi import DosyaSeciciYoneticisi
from app.ui.icon_toolbar import IconToolbar
from app.ui.iconlu_baslik import IconluBaslik
from app.ui.kart import Kart
from app.ui.tema import TEXT_MUTED, TEXT_PRIMARY


class DosyaSecici(Kart):
    def __init__(self, on_scan, on_refresh=None, **kwargs):
        super().__init__(
            orientation="vertical",
            size_hint_y=None,
            height=dp(210),
            spacing=dp(12),
            padding=(dp(14), dp(12), dp(14), dp(14)),
            bg=(0.08, 0.11, 0.16, 1),
            border=(0.18, 0.21, 0.27, 1),
            radius=16,
            **kwargs,
        )

        self.on_scan = on_scan
        self.on_refresh = on_refresh

        self._yonetici = DosyaSeciciYoneticisi()
        self._aktif_picker = None

        self._selection = None
        self._last_identifier = ""
        self._last_display_name = ""
        self._scan_schedule_event = None
        self._scan_request_serial = 0

        self.header = None
        self.file_name_label = None
        self.file_detail_label = None
        self.status_hint_label = None
        self.toolbar = None
        self.select_tool = None
        self.test_tool = None

        self._build_ui()
        self.apply_language()

    # =========================================================
    # DEBUG
    # =========================================================
    def _debug(self, message: str) -> None:
        try:
            print("[DOSYA_SECICI]", str(message))
        except Exception:
            pass

    # =========================================================
    # DIL
    # =========================================================
    def _services(self):
        try:
            parent = self.parent
            while parent is not None:
                services = getattr(parent, "services", None)
                if services is not None:
                    return services
                parent = getattr(parent, "parent", None)
        except Exception:
            pass
        return None

    def _m(self, anahtar: str, default: str = "") -> str:
        try:
            services = self._services()
            if services is not None:
                return str(services.metin(anahtar, default) or default or anahtar)
        except Exception:
            pass
        return str(default or anahtar)

    def apply_language(self) -> None:
        try:
            if self.header is not None:
                if hasattr(self.header, "set_text") and callable(self.header.set_text):
                    self.header.set_text("Belge / Kod Dosyası")
                else:
                    self.header.text = "Belge / Kod Dosyası"
        except Exception:
            pass

        try:
            if self.select_tool is not None:
                if hasattr(self.select_tool, "set_text") and callable(self.select_tool.set_text):
                    self.select_tool.set_text(self._m("select_file", "Dosya Seç"))
                elif hasattr(self.select_tool, "text"):
                    self.select_tool.text = self._m("select_file", "Dosya Seç")
        except Exception:
            pass

        try:
            if self.test_tool is not None:
                if hasattr(self.test_tool, "set_text") and callable(self.test_tool.set_text):
                    self.test_tool.set_text(self._m("test", "Test"))
                elif hasattr(self.test_tool, "text"):
                    self.test_tool.text = self._m("test", "Test")
        except Exception:
            pass

        self._refresh_summary()

    # =========================================================
    # UI
    # =========================================================
    def _build_ui(self) -> None:
        self.header = IconluBaslik(
            text="Belge / Kod Dosyası",
            icon_name="schema.png",
            height_dp=30,
            font_size="15sp",
            color=TEXT_PRIMARY,
        )
        self.header.size_hint_y = None
        self.header.height = dp(30)
        self.add_widget(self.header)

        summary_wrap = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(62),
            spacing=dp(4),
        )

        self.file_name_label = Label(
            text="Dosya seçilmedi",
            color=TEXT_PRIMARY,
            font_size="17sp",
            bold=True,
            halign="center",
            valign="middle",
            size_hint_y=None,
            height=dp(26),
            shorten=True,
            shorten_from="right",
        )
        self.file_name_label.bind(
            size=lambda inst, size: setattr(inst, "text_size", (size[0], None))
        )
        summary_wrap.add_widget(self.file_name_label)

        self.file_detail_label = Label(
            text="Seçilen belge bilgisi burada görünür.",
            color=TEXT_MUTED,
            font_size="11sp",
            halign="center",
            valign="middle",
            size_hint_y=None,
            height=dp(16),
            shorten=True,
            shorten_from="right",
        )
        self.file_detail_label.bind(
            size=lambda inst, size: setattr(inst, "text_size", (size[0], None))
        )
        summary_wrap.add_widget(self.file_detail_label)

        self.status_hint_label = Label(
            text="Belge seçmeniz bekleniyor.",
            color=(0.76, 0.82, 0.92, 1),
            font_size="11sp",
            halign="center",
            valign="middle",
            size_hint_y=None,
            height=dp(16),
            shorten=True,
            shorten_from="right",
        )
        self.status_hint_label.bind(
            size=lambda inst, size: setattr(inst, "text_size", (size[0], None))
        )
        summary_wrap.add_widget(self.status_hint_label)

        self.add_widget(summary_wrap)

        toolbar_wrap = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(86),
        )
        toolbar_wrap.add_widget(Label(size_hint_x=1))

        self.toolbar = IconToolbar(
            spacing_dp=10,
            padding_dp=0,
        )
        self.toolbar.size_hint = (None, None)

        dev_mode = False
        try:
            dev_mode = bool(self._yonetici.dev_mode_aktif_mi())
        except Exception as exc:
            self._debug(f"DEV_MODE kontrol hatası: {exc}")

        self.toolbar.size = (dp(290) if dev_mode else dp(170), dp(86))

        self.select_tool = self.toolbar.add_tool(
            icon_name="dosya_sec.png",
            text="Dosya Seç",
            on_release=self._handle_select_pressed,
            icon_size_dp=68,
            text_size="14sp",
            color=TEXT_PRIMARY,
            icon_bg=None,
        )

        try:
            self.select_tool.size_hint_x = None
            self.select_tool.width = dp(170)
        except Exception:
            pass

        if dev_mode:
            self.test_tool = self.toolbar.add_tool(
                icon_name="dosya_sec.png",
                text="Test",
                on_release=self._handle_test_pressed,
                icon_size_dp=48,
                text_size="13sp",
                color=TEXT_PRIMARY,
                icon_bg=None,
            )

            try:
                self.test_tool.size_hint_x = None
                self.test_tool.width = dp(110)
            except Exception:
                pass

        toolbar_wrap.add_widget(self.toolbar)
        toolbar_wrap.add_widget(Label(size_hint_x=1))

        self.add_widget(toolbar_wrap)

    # =========================================================
    # POPUP
    # =========================================================
    def _show_info_popup(self, title: str, message: str) -> None:
        try:
            self._yonetici.bilgi_goster(
                owner=self,
                title=str(title or ""),
                message=str(message or ""),
            )
        except Exception as exc:
            self._debug(f"Bilgi popup açılamadı: {exc}")

    def _show_scan_error_popup(self, message: str) -> None:
        self._show_info_popup(
            "Tarama Hatası",
            str(message or "Tarama sırasında hata oluştu."),
        )

    # =========================================================
    # STATE HELPERS
    # =========================================================
    def _selection_identifier(self, selection) -> str:
        if selection is None:
            return ""

        try:
            return str(selection.preferred_identifier() or "").strip()
        except Exception:
            return ""

    def _selection_display_text(self, selection) -> str:
        if selection is None:
            return ""

        try:
            return str(selection.preferred_display_name() or "").strip()
        except Exception:
            return ""

    def _short_identifier(self, value: str, limit: int = 52) -> str:
        metin = str(value or "").strip()
        if len(metin) <= limit:
            return metin

        if limit < 10:
            return metin[:limit]

        sol = max(8, limit // 2 - 2)
        sag = max(8, limit - sol - 3)
        return f"{metin[:sol]}...{metin[-sag:]}"

    def _has_selection(self) -> bool:
        if self._selection is not None and self._selection_identifier(self._selection):
            return True
        return bool(str(self._last_identifier or "").strip())

    def _refresh_summary(self) -> None:
        if not self._has_selection():
            self.file_name_label.text = self._m("file_not_selected", "Dosya seçilmedi")
            self.file_detail_label.text = self._m(
                "file_info_placeholder",
                "Seçilen belge bilgisi burada görünür.",
            )
            self.status_hint_label.text = self._m(
                "file_waiting",
                "Belge seçmeniz bekleniyor.",
            )
            self.status_hint_label.color = (0.76, 0.82, 0.92, 1)
            return

        display_name = str(self._last_display_name or "").strip()
        identifier = str(self._last_identifier or "").strip()

        self.file_name_label.text = (
            display_name if display_name else self._m("file_not_selected", "Dosya seçilmedi")
        )
        self.file_detail_label.text = (
            self._short_identifier(identifier)
            if identifier
            else self._m("file_info_placeholder", "Seçilen belge bilgisi burada görünür.")
        )
        self.status_hint_label.text = self._m(
            "file_selected_auto_scan",
            "Belge seçildi • Tarama otomatik başlatılır.",
        )
        self.status_hint_label.color = (0.72, 0.94, 0.78, 1)

    def _cancel_pending_scan_trigger(self) -> None:
        try:
            if self._scan_schedule_event is not None:
                self._scan_schedule_event.cancel()
        except Exception:
            pass
        self._scan_schedule_event = None

    # =========================================================
    # PUBLIC API
    # =========================================================
    def get_path(self) -> str:
        if self._selection is not None:
            identifier = self._selection_identifier(self._selection)
            if identifier:
                return identifier
        return str(self._last_identifier or "").strip()

    def get_selection(self):
        return self._selection

    def get_display_name(self) -> str:
        return str(self._last_display_name or "").strip()

    def set_path(self, value: str) -> None:
        temiz = str(value or "").strip()
        self._last_identifier = temiz
        self._refresh_summary()
        self._debug(f"Identifier set edildi: {temiz}")

    def set_selection(self, selection) -> None:
        self._selection = selection

        identifier = self._selection_identifier(selection)
        display_text = self._selection_display_text(selection)

        self._last_identifier = identifier
        self._last_display_name = display_text

        self._refresh_summary()

        self._debug(
            "Selection set edildi | "
            f"source={getattr(selection, 'source', '')} "
            f"identifier={identifier} "
            f"display={display_text}"
        )

    def clear_selection(self) -> None:
        self._cancel_pending_scan_trigger()
        self._selection = None
        self._last_identifier = ""
        self._last_display_name = ""
        self._refresh_summary()

    # =========================================================
    # ACTIONS
    # =========================================================
    def _handle_select_pressed(self, *_args):
        self._open_selector()

    def _handle_test_pressed(self, *_args):
        self._open_test_selector()

    def _open_selector(self, *_args):
        self._debug("Dosya seçici açılıyor")

        try:
            self._aktif_picker = self._yonetici.picker_ac(
                owner=self,
                on_selected=self._after_picker_selected,
            )
        except Exception as exc:
            self._debug(f"Seçici açma hatası: {exc}")
            self._show_info_popup(
                "Dosya Seçici",
                f"Seçici açılamadı: {exc}",
            )

    def _open_test_selector(self, *_args):
        self._debug("Test dosya seçici açılıyor")

        try:
            self._aktif_picker = self._yonetici.test_popup_ac(
                on_select=self._after_test_path_selected,
                start_dir=str(self._yonetici.varsayilan_baslangic_klasoru() or ""),
            )
        except Exception as exc:
            self._debug(f"Test seçici açma hatası: {exc}")
            self._show_info_popup(
                "Test Dosya Seçici",
                f"Test seçici açılamadı: {exc}",
            )

    # =========================================================
    # AUTO TRIGGER
    # =========================================================
    def _trigger_scan_attempt(self, reason: str, request_serial: int) -> None:
        self._scan_schedule_event = None

        if int(request_serial or 0) != int(self._scan_request_serial or 0):
            self._debug(
                f"Otomatik tetikleme iptal edildi ({reason}) | eski istek: {request_serial}"
            )
            return

        final_identifier = self.get_path()
        self._debug(f"Otomatik tetikleme ({reason}): {final_identifier}")

        if not final_identifier and self._selection is None:
            self._debug("Tetikleme atlandı: selection ve path boş")
            return

        try:
            if self.on_scan:
                self.on_scan(final_identifier)
        except Exception as exc:
            self._debug(f"Otomatik tetikleme hatası ({reason}): {exc}")
            self._show_scan_error_popup(str(exc))

    def _auto_trigger_scan_sequence(self) -> None:
        self._cancel_pending_scan_trigger()
        self._scan_request_serial += 1
        aktif_istek = int(self._scan_request_serial)

        self._debug(f"Tek tarama tetikleme planlandı | istek={aktif_istek}")

        self._scan_schedule_event = Clock.schedule_once(
            lambda *_: self._trigger_scan_attempt("tek_tetikleme", aktif_istek),
            0.06,
        )

    # =========================================================
    # PICKER CALLBACK
    # =========================================================
    def _after_picker_selected(self, selection) -> None:
        identifier = self._selection_identifier(selection)
        self._debug(f"Seçim sonucu geldi: {identifier}")

        if not identifier:
            self._show_info_popup(
                "Dosya Seçici",
                "Seçilen dosya kimliği alınamadı.",
            )
            return

        try:
            if hasattr(selection, "is_valid") and callable(getattr(selection, "is_valid")):
                if not selection.is_valid():
                    self._show_info_popup(
                        "Dosya Seçici",
                        "Seçilen belge geçerli değil.",
                    )
                    return
        except Exception:
            pass

        self.set_selection(selection)
        self._auto_trigger_scan_sequence()

    def _after_test_path_selected(self, path: str) -> None:
        self._debug(f"Test seçim yolu geldi: {path}")

        try:
            selection = self._yonetici.test_selection_olustur(path)
        except Exception as exc:
            self._debug(f"Test selection oluşturma hatası: {exc}")
            selection = None

        if selection is None:
            self._show_info_popup(
                "Test Dosya Seçici",
                "Seçilen test dosyası geçerli değil.",
            )
            return

        self.set_selection(selection)
        self._auto_trigger_scan_sequence()
