# -*- coding: utf-8 -*-
from __future__ import annotations

import traceback


class RootGeriYuklemeAkisiMixin:
    def geri_yukle_secili_belge(self) -> None:
        belge_geri = self._get_belge_geri_yukleme()
        belge_oturumu = self._get_belge_oturumu()

        try:
            if self.current_session is None:
                self.set_status_warning("Önce dosya seç.")
                return

            backup_path = str(
                belge_oturumu["son_yedek_yolu"](self.current_session) or ""
            ).strip()

            if not backup_path:
                self.set_status_warning("Geri yüklenecek uygun yedek bulunamadı.")
                return

            geri_yuklenen = belge_geri["son_yedekten_geri_yukle"](self.current_session)

            try:
                self.current_file_path = str(
                    belge_oturumu["calisma_dosyasi_yolu"](self.current_session) or ""
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
                self.set_status_success(f"Geri yüklendi. Yedek: {geri_yuklenen}")

        except belge_geri["BelgeGeriYuklemeServisiHatasi"] as exc:
            self.set_status_error(str(exc))
        except Exception:
            self.set_status_error("Geri yükleme hatası oluştu.")
            print(traceback.format_exc())