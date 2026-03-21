# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/root_paketi/akisi_geri_yukleme/geri_yukleme_akisi.py

ROL:
- Seçili belgeyi son yedeğinden geri yüklemek
- Geri yükleme sonrası UI ve çalışma kopyasını senkronize etmek
- Hata durumunda detaylı, kopyalanabilir hata bilgisini iletmek

MİMARİ:
- SADECE BelgeYoneticisi kullanılır
- Eski dict/fallback yapı kaldırıldı
- UI katmanı servis detaylarından izole tutulur
- Root paketinin alt geri yükleme akışı modülüdür

API UYUMLULUK:
- Android SAF + content URI uyumlu
- API 34+ / API 35 güvenli

SURUM: 4
TARIH: 2026-03-20
IMZA: FY.
"""

from __future__ import annotations

import traceback


class RootGeriYuklemeAkisiMixin:
    def _belge(self):
        return self._get_belge_yoneticisi()

    def geri_yukle_secili_belge(self) -> None:
        try:
            if self.current_session is None:
                self.set_status_warning("Önce dosya seç.")
                return

            backup_path = str(
                self._belge().son_yedek_yolu(self.current_session) or ""
            ).strip()

            if not backup_path:
                self.set_status_warning("Geri yüklenecek uygun yedek bulunamadı.")
                return

            geri_yuklenen = self._belge().son_yedekten_geri_yukle(
                self.current_session
            )

            try:
                self.current_file_path = str(
                    self._belge().calisma_dosyasi_yolu(self.current_session) or ""
                ).strip()
            except Exception:
                pass

            self._clear_view_only()
            self._reload_items_from_current_file()
            self._reset_selection_only()

            belge_adi = self._current_document_name()

            if belge_adi:
                self.set_status_success(
                    f"Geri yüklendi. Belge: {belge_adi} | Yedek: {geri_yuklenen}"
                )
            else:
                self.set_status_success(
                    f"Geri yüklendi. Yedek: {geri_yuklenen}"
                )

        except Exception as exc:
            self.set_status_error(
                str(exc),
                detailed_text=self._format_exception_details(
                    exc,
                    title="Geri Yükleme Hatası",
                ),
                popup_title="Geri Yükleme Hatası",
            )
            print(traceback.format_exc())