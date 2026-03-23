# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/fonksiyon_listesi_paketi/panel/panel.py

ROL:
- Taranan fonksiyonları listeler
- Arama / filtreleme yapar
- Seçilen fonksiyonu üst katmana bildirir
- Göz ikonu ile listeyi geniş / dar görünüm arasında değiştirir
- Seçilen kod ve yeni kod için kısa önizleme gösterir
- Hata durumlarında detaylı ve kopyalanabilir hata metni üretir
- İlk render sonrası görünüm tazelemesini güvenli biçimde zorlar
- Büyük listelerde render yükünü tek kareye yıkmadan parça parça işler
- Seçim sırasında tüm listeyi yeniden çizmek yerine satır bazlı güncelleme yapar
- Android / APK ortamında restore sonrası render yarış durumlarını azaltır
- Aktif dile göre görünür metinleri yenileyebilir

MİMARİ:
- Kendi görselini kendi çizer
- Root sadece veri ve callback verir
- Liste görünürlüğü burada yönetilmez, ilgili akış yöneticilerine devredilir
- Alt paket yöneticileri üzerinden satır, arama, önizleme, yardımcı,
  UI kurulumu, render akışı, görünüm akışı ve hata akışı kullanılır
- Panel dosyası orkestrasyon katmanı olarak sade tutulur
- Render akışı widget hazırlığı ve seçim tutarlılığı için güvenli kontroller içerir
- Kullanıcıya görünen metinler services -> sistem -> dil_servisi zincirinden alınır

API UYUMLULUK:
- Bu dosya doğrudan Android API çağrısı yapmaz
- Kivy tabanlı liste ve arama akışı platform bağımsızdır
- Büyük liste / dar liste davranışı güvenli şekilde yönetilir
- API 35 ile güvenle kullanılabilir

SURUM: 7
TARIH: 2026-03-23
IMZA: FY.
"""

from __future__ import annotations

from typing import Iterable

from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout

from app.services.yoneticisi import ServicesYoneticisi
from app.ui.fonksiyon_listesi_paketi.arama import AramaYoneticisi
from app.ui.fonksiyon_listesi_paketi.gorunum_akisi import GorunumAkisiYoneticisi
from app.ui.fonksiyon_listesi_paketi.hata_akisi import HataAkisiYoneticisi
from app.ui.fonksiyon_listesi_paketi.onizleme import OnizlemeYoneticisi
from app.ui.fonksiyon_listesi_paketi.render_akisi import RenderAkisiYoneticisi
from app.ui.fonksiyon_listesi_paketi.satir import SatirYoneticisi
from app.ui.fonksiyon_listesi_paketi.ui_kurulumu import UiKurulumuYoneticisi
from app.ui.fonksiyon_listesi_paketi.yardimci import YardimciYoneticisi
from app.ui.tema import TEXT_MUTED


class FonksiyonListesi(BoxLayout):
    def __init__(
        self,
        on_select,
        on_error=None,
        services: ServicesYoneticisi | None = None,
        **kwargs,
    ):
        super().__init__(
            orientation="vertical",
            spacing=dp(8),
            size_hint_y=None,
            height=dp(760),
            **kwargs,
        )

        self.on_select = on_select
        self.on_error = on_error
        self.services = services

        self._satir_yoneticisi = SatirYoneticisi()
        self._arama_yoneticisi = AramaYoneticisi()
        self._onizleme_yoneticisi = OnizlemeYoneticisi()
        self._yardimci_yoneticisi = YardimciYoneticisi()
        self._ui_kurulumu_yoneticisi = UiKurulumuYoneticisi()
        self._render_akisi_yoneticisi = RenderAkisiYoneticisi()
        self._gorunum_akisi_yoneticisi = GorunumAkisiYoneticisi()
        self._hata_akisi_yoneticisi = HataAkisiYoneticisi()

        self.all_items = []
        self.filtered_items = []
        self.selected_item = None
        self.is_list_expanded = True

        self._selected_preview_text = ""
        self._new_preview_text = ""

        self._expanded_list_height = dp(360)
        self._compact_list_height = dp(212)

        self.header = None
        self.count_label = None
        self.header_toolbar = None
        self.toggle_button = None
        self.search_wrap = None
        self.search_input = None
        self.list_wrap = None
        self.list_info_label = None
        self.table_header = None
        self.scroll = None
        self.container = None
        self.selected_preview_card = None
        self.new_preview_card = None

        self._render_event = None
        self._render_serial = 0
        self._pending_render_items = []
        self._pending_keep_scroll = False

        self._row_widgets = {}

        self._build_ui()

    # =========================================================
    # DIL
    # =========================================================
    def _get_services(self) -> ServicesYoneticisi:
        if self.services is not None:
            return self.services

        try:
            parent = self.parent
            while parent is not None:
                services = getattr(parent, "services", None)
                if services is not None:
                    self.services = services
                    return services
                parent = getattr(parent, "parent", None)
        except Exception:
            pass

        self.services = ServicesYoneticisi()
        return self.services

    def _m(self, anahtar: str, default: str = "") -> str:
        try:
            return str(
                self._get_services().metin(anahtar, default) or default or anahtar
            )
        except Exception:
            return str(default or anahtar)

    def refresh_language(self) -> None:
        try:
            if self.header is not None:
                if hasattr(self.header, "set_text") and callable(self.header.set_text):
                    self.header.set_text(
                        self._m("function_list_title", "Fonksiyon Listesi")
                    )
                elif hasattr(self.header, "text"):
                    self.header.text = self._m(
                        "function_list_title",
                        "Fonksiyon Listesi",
                    )
        except Exception:
            pass

        try:
            if self.search_input is not None and hasattr(self.search_input, "hint_text"):
                self.search_input.hint_text = self._m(
                    "search_functions",
                    "Fonksiyon ara...",
                )
        except Exception:
            pass

        try:
            self._refresh_count_label()
        except Exception:
            pass

        try:
            self._selected_preview_card_text_guncelle()
        except Exception:
            pass

        try:
            self._new_preview_card_text_guncelle()
        except Exception:
            pass

        try:
            self._render_items(self.filtered_items, keep_scroll=True)
        except Exception:
            pass

    # =========================================================
    # SHARED HELPERS
    # =========================================================
    def _text_muted_color(self):
        return TEXT_MUTED

    def _ui_hazir_mi(self) -> bool:
        try:
            return bool(
                self.container is not None
                and self.scroll is not None
            )
        except Exception:
            return False

    def _item_gecerli_mi(self, item) -> bool:
        if item is None:
            return False

        try:
            path_value = str(getattr(item, "path", "") or "").strip()
            name_value = str(getattr(item, "name", "") or "").strip()
            source_value = str(getattr(item, "source", "") or "").strip()
            return bool(path_value or name_value or source_value)
        except Exception:
            return False

    def _refresh_count_label(self) -> None:
        try:
            if self.count_label is None:
                return

            toplam = len(self.all_items or [])
            filtreli = len(self.filtered_items or [])

            if toplam <= 0:
                text_value = self._m("function_count_empty", "Fonksiyon yok")
            elif filtreli == toplam:
                text_value = self._m(
                    "function_count_all",
                    f"Toplam {toplam} fonksiyon",
                )
                if "{count}" in text_value:
                    text_value = text_value.replace("{count}", str(toplam))
            else:
                text_value = self._m(
                    "function_count_filtered",
                    f"{filtreli} / {toplam} fonksiyon",
                )
                text_value = (
                    text_value.replace("{filtered}", str(filtreli))
                    .replace("{total}", str(toplam))
                )

            self.count_label.text = str(text_value)
        except Exception:
            pass

    # =========================================================
    # ERROR
    # =========================================================
    def _debug(self, message: str) -> None:
        self._hata_akisi_yoneticisi.debug(self, message)

    def _format_exception_details(
        self,
        exc: Exception,
        title: str = "",
    ) -> str:
        return self._hata_akisi_yoneticisi.format_exception_details(
            self,
            exc,
            title or self._m("function_list_error", "Fonksiyon Listesi Hatası"),
        )

    def _report_error(
        self,
        exc: Exception,
        title: str = "",
        detailed_text: str = "",
    ) -> None:
        self._hata_akisi_yoneticisi.report_error(
            owner=self,
            exc=exc,
            title=title or self._m("function_list_error", "Fonksiyon Listesi Hatası"),
            detailed_text=detailed_text,
        )

    # =========================================================
    # UI
    # =========================================================
    def _build_ui(self) -> None:
        try:
            self._ui_kurulumu_yoneticisi.build_ui(self)
            self.refresh_language()
        except Exception as exc:
            self._report_error(
                exc,
                title=self._m(
                    "function_list_ui_setup_error",
                    "Fonksiyon Listesi UI Kurulum Hatası",
                ),
            )

    # =========================================================
    # INTERNAL RENDER SCHEDULING
    # =========================================================
    def _cancel_pending_render(self) -> None:
        try:
            if self._render_event is not None:
                self._render_event.cancel()
        except Exception:
            pass
        self._render_event = None

    def _schedule_render(self, items, keep_scroll: bool = False) -> None:
        self._cancel_pending_render()
        self._render_serial += 1
        self._pending_render_items = list(items or [])
        self._pending_keep_scroll = bool(keep_scroll)
        aktif_serial = int(self._render_serial)

        self._debug(
            f"Render planlandı | serial={aktif_serial} | item_sayisi={len(self._pending_render_items)}"
        )

        self._render_event = Clock.schedule_once(
            lambda *_: self._run_scheduled_render(aktif_serial),
            0,
        )

    def _run_scheduled_render(self, render_serial: int) -> None:
        self._render_event = None

        if int(render_serial or 0) != int(self._render_serial or 0):
            self._debug(
                f"Eski render isteği atlandı | serial={render_serial} | guncel={self._render_serial}"
            )
            return

        if not self._ui_hazir_mi():
            self._debug("Render ertelendi: liste widgetları henüz hazır değil.")
            self._render_event = Clock.schedule_once(
                lambda *_: self._run_scheduled_render(render_serial),
                0.05,
            )
            return

        try:
            self._render_akisi_yoneticisi.render_items(
                self,
                items=list(self._pending_render_items or []),
                keep_scroll=bool(self._pending_keep_scroll),
            )
            self._rebuild_row_widget_index()
            self._refresh_count_label()
        except Exception as exc:
            self._report_error(
                exc,
                title=self._m(
                    "function_list_render_error",
                    "Fonksiyon Listesi Render Hatası",
                ),
            )

    def _rebuild_row_widget_index(self) -> None:
        self._row_widgets = {}

        try:
            if self.container is None:
                return

            for child in list(getattr(self.container, "children", []) or []):
                try:
                    item = getattr(child, "item", None)
                    if item is None:
                        continue
                    self._row_widgets[self._item_key(item)] = child
                except Exception:
                    continue
        except Exception:
            self._row_widgets = {}

    def _refresh_row_selection_state(self, onceki_item, yeni_item) -> None:
        try:
            onceki_key = self._item_key(onceki_item)
            yeni_key = self._item_key(yeni_item)

            onceki_row = self._row_widgets.get(onceki_key)
            yeni_row = self._row_widgets.get(yeni_key)

            if onceki_row is not None and hasattr(onceki_row, "set_selected_state"):
                try:
                    onceki_row.set_selected_state(False)
                except Exception:
                    pass

            if yeni_row is not None and hasattr(yeni_row, "set_selected_state"):
                try:
                    yeni_row.set_selected_state(True)
                except Exception:
                    pass
        except Exception:
            pass

    # =========================================================
    # PUBLIC API
    # =========================================================
    def clear_items(self) -> None:
        try:
            if self.container is None:
                return

            self.container.clear_widgets()
            self.container.height = dp(1)

            try:
                self.container.do_layout()
            except Exception:
                pass

            self._row_widgets = {}
            self._refresh_count_label()
        except Exception as exc:
            self._report_error(
                exc,
                title=self._m(
                    "function_list_clear_error",
                    "Fonksiyon Listesi Temizleme Hatası",
                ),
            )

    def clear_selection(self) -> None:
        self.selected_item = None
        self.set_selected_preview("")

    def clear_new_preview(self) -> None:
        self.set_new_preview("")

    def clear_all(self) -> None:
        try:
            self._cancel_pending_render()

            self.selected_item = None
            self.all_items = []
            self.filtered_items = []
            self._pending_render_items = []
            self._pending_keep_scroll = False
            self._row_widgets = {}

            try:
                if self.search_input is not None:
                    self.search_input.text = ""
            except Exception:
                pass

            self.clear_items()
            self.set_selected_preview("")
            self.set_new_preview("")
            self._refresh_count_label()
        except Exception as exc:
            self._report_error(
                exc,
                title=self._m(
                    "function_list_reset_error",
                    "Fonksiyon Listesi Sıfırlama Hatası",
                ),
            )

    def set_items(self, items: Iterable) -> None:
        try:
            yeni_items = list(items or [])
            onceki_secim = self.selected_item

            print("FonksiyonListesi.set_items CALISTI =", len(yeni_items))

            self.all_items = yeni_items
            self.filtered_items = self._arama_yoneticisi.apply_filter(
                self.all_items,
                self.search_input.text if self.search_input else "",
            )

            if not self.all_items:
                self.selected_item = None
            else:
                try:
                    self.selected_item = self._yardimci_yoneticisi.restore_selected_item(
                        self.all_items,
                        onceki_secim,
                    )
                except Exception:
                    self.selected_item = None

            self._schedule_render(self.filtered_items, keep_scroll=False)
            self._refresh_count_label()
        except Exception as exc:
            self._report_error(
                exc,
                title=self._m(
                    "function_list_update_error",
                    "Fonksiyon Listesi Güncelleme Hatası",
                ),
            )

    def set_selected_preview(self, text: str) -> None:
        self._selected_preview_text = str(text or "")
        self._selected_preview_card_text_guncelle()

    def set_new_preview(self, text: str) -> None:
        self._new_preview_text = str(text or "")
        self._new_preview_card_text_guncelle()

    # =========================================================
    # PREVIEW
    # =========================================================
    def _selected_preview_card_text_guncelle(self) -> None:
        try:
            if self.selected_preview_card is not None:
                self.selected_preview_card._preview_label.text = (
                    self._onizleme_yoneticisi.preview_from_text(
                        self._selected_preview_text,
                        max_lines=5,
                    )
                )
        except Exception as exc:
            self._report_error(
                exc,
                title=self._m(
                    "selected_preview_update_error",
                    "Seçilen Önizleme Güncelleme Hatası",
                ),
            )

    def _new_preview_card_text_guncelle(self) -> None:
        try:
            if self.new_preview_card is not None:
                self.new_preview_card._preview_label.text = (
                    self._onizleme_yoneticisi.preview_from_text(
                        self._new_preview_text,
                        max_lines=5,
                    )
                )
        except Exception as exc:
            self._report_error(
                exc,
                title=self._m(
                    "new_preview_update_error",
                    "Yeni Önizleme Güncelleme Hatası",
                ),
            )

    # =========================================================
    # SELECTION
    # =========================================================
    def _item_key(self, item) -> tuple:
        try:
            return self._yardimci_yoneticisi.item_key(item)
        except Exception:
            if item is None:
                return ("", "", "", 0, 0)

            return (
                str(getattr(item, "path", "") or ""),
                str(getattr(item, "name", "") or ""),
                str(getattr(item, "kind", "") or ""),
                int(getattr(item, "lineno", 0) or 0),
                int(getattr(item, "end_lineno", 0) or 0),
            )

    # =========================================================
    # SEARCH
    # =========================================================
    def _apply_filter(self, value: str):
        try:
            return self._arama_yoneticisi.apply_filter(self.all_items, value)
        except Exception:
            return list(self.all_items)

    # =========================================================
    # RENDER
    # =========================================================
    def _make_empty_label(self):
        return self._render_akisi_yoneticisi.make_empty_label(self)

    def _refresh_trigger(self, *_args):
        return self._render_akisi_yoneticisi.refresh_trigger(self, *_args)

    def _render_items(self, items, keep_scroll: bool = False) -> None:
        try:
            self._schedule_render(items, keep_scroll=keep_scroll)
        except Exception as exc:
            self._report_error(
                exc,
                title=self._m(
                    "function_list_render_error",
                    "Fonksiyon Listesi Render Hatası",
                ),
            )

    def _scroll_top(self, *_args):
        self._render_akisi_yoneticisi.scroll_top(self, *_args)

    def _selected_itemi_gorunur_tut(self, *_args):
        self._render_akisi_yoneticisi.selected_itemi_gorunur_tut(self, *_args)

    # =========================================================
    # VISIBILITY
    # =========================================================
    def _set_toggle_icon(self, icon_name: str) -> None:
        try:
            self._gorunum_akisi_yoneticisi.set_toggle_icon(self, icon_name)
        except Exception as exc:
            self._report_error(
                exc,
                title=self._m(
                    "list_icon_update_error",
                    "Liste İkon Güncelleme Hatası",
                ),
            )

    def _update_toggle_icon(self) -> None:
        self._gorunum_akisi_yoneticisi.update_toggle_icon(self)

    def _toggle_list_visibility(self, *_args):
        try:
            self._gorunum_akisi_yoneticisi.toggle_list_visibility(self, *_args)
        except Exception as exc:
            self._report_error(
                exc,
                title=self._m(
                    "list_visibility_error",
                    "Liste Görünürlük Hatası",
                ),
            )

    def _sync_list_visibility(self) -> None:
        try:
            self._gorunum_akisi_yoneticisi.sync_list_visibility(self)
        except Exception as exc:
            self._report_error(
                exc,
                title=self._m(
                    "list_sync_error",
                    "Liste Görünüm Senkron Hatası",
                ),
            )

    # =========================================================
    # EVENTS
    # =========================================================
    def _select(self, item) -> None:
        if not self._item_gecerli_mi(item):
            return

        try:
            onceki_item = self.selected_item
            self.selected_item = item

            self._refresh_row_selection_state(onceki_item, item)

            try:
                self.set_selected_preview(str(getattr(item, "source", "") or ""))
            except Exception:
                pass

            try:
                self.set_new_preview("")
            except Exception:
                pass

            try:
                if self.on_select:
                    self.on_select(item)
            except Exception:
                pass
        except Exception as exc:
            self._report_error(
                exc,
                title=self._m(
                    "function_select_error",
                    "Fonksiyon Seçim Hatası",
                ),
            )

    def _on_search_text(self, _instance, value: str) -> None:
        try:
            self.filtered_items = self._apply_filter(value)

            if self.selected_item is not None:
                hedef = None
                secim_key = self._item_key(self.selected_item)
                for item in self.filtered_items:
                    try:
                        if self._item_key(item) == secim_key:
                            hedef = item
                            break
                    except Exception:
                        continue
                self.selected_item = hedef

            self._render_items(self.filtered_items, keep_scroll=True)
            self._refresh_count_label()
        except Exception as exc:
            self._report_error(
                exc,
                title=self._m(
                    "function_search_error",
                    "Fonksiyon Arama Hatası",
                ),
      )
