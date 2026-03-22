# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/editor_paketi/panel/editor_paneli.py

ROL:
- Editör panelinin ana UI organizatörü
- Mevcut kod, yeni kod ve aksiyon alanlarını bir araya getirir
- Aksiyon, bildirim, popup, doğrulama ve yardımcı akışları ilgili yöneticiler üzerinden yürütür
- Büyük kod içeriklerinde UI donmasını azaltmak için içerik yüklemeyi sade ve güvenli şekilde erteler
- Üst katmanların editör iç yapısını bilmeden metin okuyup yazabilmesi için public text API sağlar

MİMARİ:
- Alt modüllere doğrudan erişmez
- Sadece ilgili alt paket yöneticileri ile konuşur
- UI burada, iş akışı yöneticiler ve alt modüllerdedir
- Davranış korunur, bağımlılık yapısı sadeleştirilmiştir
- set_item akışı tek bir ertelenmiş yükleme ile stabil tutulur
- Root ve diğer üst katmanlar editör iç widget yapısını bilmeden public API üzerinden içerik okuyup yazabilir

API UYUMLULUK:
- Platform bağımsızdır
- Android API 35 ile uyumludur
- Doğrudan Android bridge çağrısı içermez

SURUM: 28
TARIH: 2026-03-22
IMZA: FY.
"""

from __future__ import annotations

from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout

from app.ui.icon_toolbar import IconToolbar
from app.ui.iconlu_baslik import IconluBaslik
from app.ui.tema import TEXT_MUTED, TEXT_PRIMARY


class EditorPaneli(BoxLayout):
    def __init__(self, on_update=None, on_restore=None, **kwargs):
        super().__init__(orientation="vertical", spacing=dp(10), **kwargs)

        self.on_update = on_update
        self.on_restore = on_restore
        self.current_item = None
        self._new_code_buffer = ""
        self._current_popup = None
        self._editor_popup = None

        self.path_label = None
        self.error_box = None
        self.current_code_area = None
        self.inline_notice = None
        self.new_code_area = None
        self.action_toolbar = None

        self._pending_set_item_event = None
        self._set_item_serial = 0

        self._build_ui()
        self._set_status_info("Hazır.", 0)

    # =========================================================
    # YONETICILER
    # =========================================================
    def _aksiyon(self):
        from app.ui.editor_paketi.aksiyon import AksiyonYoneticisi
        return AksiyonYoneticisi()

    def _bilesenler(self):
        from app.ui.editor_paketi.bilesenler import BilesenlerYoneticisi
        return BilesenlerYoneticisi()

    def _bildirim(self):
        from app.ui.editor_paketi.bildirim import BildirimYoneticisi
        return BildirimYoneticisi()

    def _dogrulama(self):
        from app.ui.editor_paketi.dogrulama import DogrulamaYoneticisi
        return DogrulamaYoneticisi()

    def _popup(self):
        from app.ui.editor_paketi.popup import PopupYoneticisi
        return PopupYoneticisi()

    def _yardimci(self):
        from app.ui.editor_paketi.yardimci import YardimciYoneticisi
        return YardimciYoneticisi()

    # =========================================================
    # UI
    # =========================================================
    def _build_ui(self) -> None:
        self.path_label = IconluBaslik(
            text="Seçili fonksiyon: -",
            icon_name="edit.png",
            height_dp=38,
            font_size="16sp",
            color=TEXT_PRIMARY,
        )
        self.path_label.size_hint_y = None
        self.path_label.height = dp(38)
        self.add_widget(self.path_label)

        self.error_box = self._bilesenler().bilgi_kutusu_olustur()
        self.add_widget(self.error_box)

        self.add_widget(
            self._build_title_row(
                title="Mevcut Kod",
                icon_name="visibility_on.png",
                action_icon="visibility_on.png",
                action_text="Aç",
                callback=self._open_current_code_popup,
            )
        )

        self.current_code_area = self._bilesenler().sade_kod_alani_olustur(
            readonly=True,
            size_hint_y=0.34,
        )
        self.add_widget(self.current_code_area)

        self.add_widget(
            self._build_title_row(
                title="Yeni Fonksiyon Kodu",
                icon_name="edit.png",
                action_icon="edit.png",
                action_text="Düzenle",
                callback=self._open_new_code_editor_popup,
            )
        )

        self.inline_notice = self._bildirim().bildirim_olustur()
        self.add_widget(self.inline_notice)

        self.new_code_area = self._bilesenler().sade_kod_alani_olustur(
            readonly=False,
            hint_text="Tam fonksiyon kodunu buraya yaz veya yapıştır.",
            size_hint_y=0.66,
        )
        self.add_widget(self.new_code_area)

        self._build_action_toolbar()

    def _build_title_row(
        self,
        title: str,
        icon_name: str,
        action_icon: str,
        action_text: str,
        callback,
    ):
        wrap = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(78),
            spacing=dp(4),
        )

        row = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(38),
            spacing=dp(8),
        )
        row.add_widget(
            IconluBaslik(
                text=title,
                icon_name=icon_name,
                height_dp=34,
                font_size="15sp",
                color=(0.80, 0.89, 1, 1),
                size_hint_x=1,
            )
        )
        wrap.add_widget(row)

        toolbar = IconToolbar(spacing_dp=12, padding_dp=0)
        toolbar.size_hint_y = None
        toolbar.height = dp(36)
        toolbar.add_tool(
            icon_name=action_icon,
            text=action_text,
            on_release=callback,
            icon_size_dp=34,
            text_size="11sp",
            color=TEXT_MUTED,
            icon_bg=None,
        )
        wrap.add_widget(toolbar)
        return wrap

    def _build_action_toolbar(self) -> None:
        self.action_toolbar = IconToolbar(spacing_dp=22, padding_dp=6)
        self.action_toolbar.size_hint_y = None
        self.action_toolbar.height = dp(84)

        self.action_toolbar.add_tool(
            icon_name="clear.png",
            text="Temizle",
            on_release=self._clear_new_code,
            icon_size_dp=42,
            text_size="12sp",
            color=TEXT_MUTED,
            icon_bg=None,
        )

        self.action_toolbar.add_tool(
            icon_name="upload.png",
            text="Güncelle",
            on_release=self._handle_update,
            icon_size_dp=42,
            text_size="12sp",
            color=TEXT_MUTED,
            icon_bg=None,
        )

        self.action_toolbar.add_tool(
            icon_name="code_check.png",
            text="Kontrol Et",
            on_release=self._check_new_code,
            icon_size_dp=42,
            text_size="11sp",
            color=TEXT_MUTED,
            icon_bg=None,
        )

        self.action_toolbar.add_tool(
            icon_name="file_copy.png",
            text="Kopyala",
            on_release=self._copy_current_to_new,
            icon_size_dp=42,
            text_size="12sp",
            color=TEXT_MUTED,
            icon_bg=None,
        )

        self.action_toolbar.add_tool(
            icon_name="geri_yukle.png",
            text="Geri Yükle",
            on_release=self._handle_restore,
            icon_size_dp=42,
            text_size="11sp",
            color=TEXT_MUTED,
            icon_bg=None,
        )

        self.add_widget(self.action_toolbar)

    # =========================================================
    # PUBLIC TEMIZLEME
    # =========================================================
    def clear_selection(self) -> None:
        self.set_item(None)

    def clear_all(self) -> None:
        self._cancel_pending_set_item()
        self._yardimci().close_popups(self)
        self.current_item = None
        self._new_code_buffer = ""
        self.path_label.set_text("Seçili fonksiyon: -")
        self.current_code_area.text = ""
        self.new_code_area.text = ""
        self.inline_notice.hide_immediately()
        self._set_status_info("Hazır.", 0)

    def set_new_code_text(self, text: str) -> None:
        self._set_new_code(text)

    # =========================================================
    # PUBLIC TEXT API
    # =========================================================
    def get_text(self) -> str:
        """
        Yeni kod alanındaki metni döner.
        Üst katmanlar editör iç yapısını bilmeden bu public API üzerinden
        içerik okuyabilir.
        """
        try:
            return str(self.new_code_area.text or "")
        except Exception:
            return ""

    def set_text(self, text: str) -> None:
        """
        Yeni kod alanına metin yazar.
        Üst katmanlar editör iç yapısını bilmeden bu public API üzerinden
        içerik geri yükleyebilir.
        """
        try:
            self._set_new_code(text)
        except Exception:
            try:
                self.new_code_area.text = str(text or "")
            except Exception:
                pass

    def get_current_text(self) -> str:
        """
        Mevcut kod alanındaki salt okunur metni döner.
        Tanılama, karşılaştırma ve gerektiğinde üst katman kullanımı için
        yardımcı public API sunar.
        """
        try:
            return str(self.current_code_area.text or "")
        except Exception:
            return ""

    # =========================================================
    # STATUS
    # =========================================================
    def _set_status_info(self, message="", line_no=0):
        self._yardimci().set_status_info(self, message, line_no)

    def _set_status_warning(self, message="", line_no=0):
        self._yardimci().set_status_warning(self, message, line_no)

    def _set_status_error(self, message="", line_no=0):
        self._yardimci().set_status_error(self, message, line_no)

    def _set_status_success(self, message="", line_no=0):
        self._yardimci().set_status_success(self, message, line_no)

    # =========================================================
    # INTERNAL
    # =========================================================
    def _cancel_pending_set_item(self) -> None:
        try:
            if self._pending_set_item_event is not None:
                self._pending_set_item_event.cancel()
        except Exception:
            pass
        self._pending_set_item_event = None

    # =========================================================
    # KOD
    # =========================================================
    def _set_new_code(self, text) -> None:
        metin = self._dogrulama().normalize_code_text(
            text,
            trim_outer_blank_lines=True,
        )
        self._new_code_buffer = metin
        self.new_code_area.text = metin
        self.new_code_area.scroll_to_top()

    def set_item(self, item) -> None:
        self._cancel_pending_set_item()
        self._set_item_serial += 1
        aktif_serial = int(self._set_item_serial)

        onceki_path = str(getattr(self.current_item, "path", "") or "")
        yeni_path = str(getattr(item, "path", "") or "")

        self.current_item = item
        self.inline_notice.hide_immediately()
        self._set_status_info("Hazır.", 0)

        if item is None:
            self._yardimci().close_popups(self)
            self.path_label.set_text("Seçili fonksiyon: -")
            self.current_code_area.text = ""
            self.new_code_area.text = ""
            self._new_code_buffer = ""
            return

        self.path_label.set_text(f"Seçili fonksiyon: {getattr(item, 'path', '-')}")

        if onceki_path != yeni_path:
            self._new_code_buffer = ""

        source_raw = str(getattr(item, "source", "") or "")
        new_buffer_raw = str(self._new_code_buffer or "")

        def _apply(_dt):
            if aktif_serial != int(self._set_item_serial):
                return

            try:
                current_text = self._dogrulama().normalize_code_text(
                    source_raw,
                    trim_outer_blank_lines=True,
                )
            except Exception:
                current_text = source_raw

            try:
                if new_buffer_raw.strip():
                    new_text = self._dogrulama().normalize_code_text(
                        new_buffer_raw,
                        trim_outer_blank_lines=True,
                    )
                else:
                    new_text = ""
            except Exception:
                new_text = new_buffer_raw

            try:
                self.current_code_area.text = current_text
            except Exception:
                self.current_code_area.text = ""

            try:
                self.new_code_area.text = new_text
            except Exception:
                self.new_code_area.text = ""

            try:
                self.current_code_area.scroll_to_top()
            except Exception:
                try:
                    self.current_code_area.scroll_y = 1
                except Exception:
                    pass

            try:
                self.new_code_area.scroll_to_top()
            except Exception:
                try:
                    self.new_code_area.scroll_y = 1
                except Exception:
                    pass

            self._pending_set_item_event = None

        self._pending_set_item_event = Clock.schedule_once(_apply, 0)

    # =========================================================
    # AKSIYONLAR
    # =========================================================
    def _copy_current_to_new(self, *_args):
        return self._aksiyon().copy_current_to_new(self, *_args)

    def _clear_new_code(self, *_args):
        return self._aksiyon().clear_new_code(self, *_args)

    def _check_new_code(self, *_args):
        return self._aksiyon().check_new_code(self, *_args)

    def _handle_update(self, *_args):
        return self._aksiyon().handle_update(self, *_args)

    def _handle_restore(self, *_args):
        return self._aksiyon().handle_restore(self, *_args)

    # =========================================================
    # POPUP
    # =========================================================
    def _open_current_code_popup(self, *_args):
        return self._popup().open_current_code_popup(self, *_args)

    def _open_new_code_editor_popup(self, *_args):
        return self._popup().open_new_code_editor_popup(self, *_args)
