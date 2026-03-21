# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/fonksiyon_listesi_paketi/satir/satir.py

ROL:
- Fonksiyon listesindeki tek satırı çizmek
- Satır seçim / basma görsel durumunu yönetmek
- Tıklanınca üst katmana seçilen item'ı iletmek
- Hata durumunda detaylı bilgi üretmek
- Oluşum ve görünürlük için debug desteği sağlamak

MİMARİ:
- Sadece satır bileşenidir
- Panel doğrudan bu sınıfı değil, satır yöneticisini kullanmalıdır
- Hata popup açmaz, üst katmana detaylı hata metni gönderir

API UYUMLULUK:
- Doğrudan Android API çağrısı yapmaz
- Kivy tabanlıdır
- API 35 ile güvenle kullanılabilir

SURUM: 2
TARIH: 2026-03-20
IMZA: FY.
"""

from __future__ import annotations

import traceback

from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

from app.ui.tema import CARD_BG, RADIUS_MD, TEXT_MUTED, TEXT_PRIMARY


class FonksiyonSatiri(ButtonBehavior, BoxLayout):
    def __init__(self, item, on_press_row, on_error=None, is_selected=False, **kwargs):
        super().__init__(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(78),
            padding=(dp(12), dp(10)),
            spacing=dp(10),
            opacity=1,
            **kwargs,
        )

        self.item = item
        self.on_press_row = on_press_row
        self.on_error = on_error
        self.is_selected = bool(is_selected)

        with self.canvas.before:
            self._bg_color = Color(
                *(self._selected_bg() if self.is_selected else self._normal_bg())
            )
            self._bg_rect = RoundedRectangle(radius=[dp(RADIUS_MD)])

        self.bind(pos=self._update_canvas, size=self._update_canvas)
        self._update_canvas()

        self._build_ui()
        self._debug_row_created()

    # =========================================================
    # DEBUG
    # =========================================================
    def _debug(self, message: str) -> None:
        try:
            print("[FONKSIYON_SATIRI]", str(message))
        except Exception:
            pass

    def _debug_row_created(self) -> None:
        try:
            self._debug(
                "OLUSTU | "
                f"name={getattr(self.item, 'name', '')} "
                f"path={getattr(self.item, 'path', '')} "
                f"height={self.height} "
                f"size_hint_y={self.size_hint_y} "
                f"opacity={self.opacity}"
            )
        except Exception:
            pass

    # =========================================================
    # INTERNAL
    # =========================================================
    def _normal_bg(self):
        return CARD_BG

    def _selected_bg(self):
        return (0.20, 0.34, 0.52, 1)

    def _pressed_bg(self):
        if self.is_selected:
            return (0.24, 0.40, 0.60, 1)
        return (0.24, 0.28, 0.36, 1)

    def _update_canvas(self, *_args):
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size

    def _bind_label_size(self, label: Label):
        label.bind(size=lambda inst, size: setattr(inst, "text_size", size))
        return label

    def _safe_text(self, value, default="-") -> str:
        metin = str(value or "").strip()
        return metin if metin else default

    def _short_text(self, value: str, limit: int) -> str:
        metin = self._safe_text(value, "-")
        if len(metin) <= limit:
            return metin
        if limit <= 3:
            return metin[:limit]
        return metin[: limit - 3] + "..."

    def _display_name(self) -> str:
        qualified_name = str(getattr(self.item, "qualified_name", "") or "").strip()
        if qualified_name:
            return qualified_name
        return str(getattr(self.item, "name", "") or "-")

    def _kind_text(self) -> str:
        kind = str(getattr(self.item, "kind", "") or "").strip()
        if not kind:
            return "-"
        if kind == "function":
            return "func"
        return kind

    def _line_text(self) -> str:
        start = int(getattr(self.item, "lineno", 0) or 0)
        end = int(getattr(self.item, "end_lineno", 0) or 0)
        if start > 0 and end > 0:
            return f"{start}-{end}"
        if start > 0:
            return str(start)
        return "-"

    def _signature_text(self) -> str:
        signature = str(getattr(self.item, "signature", "") or "").strip()
        if signature:
            return self._short_text(signature, 22)

        name = str(getattr(self.item, "name", "") or "").strip()
        if name:
            return self._short_text(f"def {name}(...)", 22).strip()

        return "-"

    def _format_exception_details_local(self, exc: Exception, title: str) -> str:
        exc_type = type(exc).__name__
        dosya = "bilinmiyor"
        fonksiyon = "bilinmiyor"
        satir = "bilinmiyor"
        kaynak_satir = ""

        try:
            tb_list = traceback.extract_tb(exc.__traceback__)
            if tb_list:
                son = tb_list[-1]
                dosya = str(getattr(son, "filename", "bilinmiyor") or "bilinmiyor")
                fonksiyon = str(getattr(son, "name", "bilinmiyor") or "bilinmiyor")
                satir = str(getattr(son, "lineno", "bilinmiyor") or "bilinmiyor")
                kaynak_satir = str(getattr(son, "line", "") or "").strip()
        except Exception:
            pass

        parcalar = [
            f"BASLIK:\n{title}",
            f"HATA TÜRÜ:\n{exc_type}",
            f"DOSYA:\n{dosya}",
            f"FONKSİYON:\n{fonksiyon}",
            f"SATIR:\n{satir}",
        ]

        if kaynak_satir:
            parcalar.append(f"KAYNAK SATIR:\n{kaynak_satir}")

        parcalar.append(f"DETAY:\n{str(exc or '').strip() or 'Ayrıntı alınamadı.'}")

        try:
            tb_text = traceback.format_exc().strip()
            if tb_text and tb_text != "NoneType: None":
                parcalar.append(f"TRACEBACK:\n{tb_text}")
        except Exception:
            pass

        return "\n\n".join(parcalar)

    # =========================================================
    # UI
    # =========================================================
    def _build_ui(self):
        ad = self._bind_label_size(
            Label(
                text=self._short_text(self._display_name(), 22),
                size_hint_x=0.46,
                size_hint_y=1,
                color=TEXT_PRIMARY,
                font_size="14sp",
                halign="left",
                valign="middle",
                shorten=True,
                shorten_from="right",
                max_lines=2,
            )
        )
        self.add_widget(ad)

        tur = self._bind_label_size(
            Label(
                text=self._kind_text(),
                size_hint_x=0.14,
                size_hint_y=1,
                color=(0.84, 0.88, 0.96, 1),
                font_size="13sp",
                halign="center",
                valign="middle",
                shorten=True,
                shorten_from="right",
                max_lines=1,
            )
        )
        self.add_widget(tur)

        satir = self._bind_label_size(
            Label(
                text=self._line_text(),
                size_hint_x=0.16,
                size_hint_y=1,
                color=(0.88, 0.92, 1, 1),
                font_size="13sp",
                halign="center",
                valign="middle",
                max_lines=1,
            )
        )
        self.add_widget(satir)

        imza = self._bind_label_size(
            Label(
                text=self._signature_text(),
                size_hint_x=0.24,
                size_hint_y=1,
                color=TEXT_MUTED,
                font_size="12sp",
                halign="left",
                valign="middle",
                shorten=True,
                shorten_from="right",
                max_lines=2,
            )
        )
        self.add_widget(imza)

    # =========================================================
    # PUBLIC
    # =========================================================
    def set_selected_state(self, is_selected: bool) -> None:
        self.is_selected = bool(is_selected)
        try:
            self._bg_color.rgba = (
                self._selected_bg() if self.is_selected else self._normal_bg()
            )
        except Exception:
            pass

    # =========================================================
    # EVENTS
    # =========================================================
    def on_press(self):
        try:
            self._bg_color.rgba = self._pressed_bg()
        except Exception:
            pass
        return super().on_press()

    def on_release(self):
        try:
            self._bg_color.rgba = (
                self._selected_bg() if self.is_selected else self._normal_bg()
            )
        except Exception:
            pass

        try:
            if self.on_press_row:
                self.on_press_row(self.item)
        except Exception as exc:
            try:
                if self.on_error is not None:
                    self.on_error(
                        exc,
                        title="Fonksiyon Satırı Seçim Hatası",
                        detailed_text=self._format_exception_details_local(
                            exc,
                            title="Fonksiyon Satırı Seçim Hatası",
                        ),
                    )
            except Exception:
                pass

        return super().on_release()