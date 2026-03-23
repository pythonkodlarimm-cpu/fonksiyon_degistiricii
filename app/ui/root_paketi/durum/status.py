# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/root_paketi/durum/status.py

ROL:
- Root katmanında durum metni ve geçici bildirim akışını yönetmek
- Status bar ve toast/overlay bildirimlerini güvenli biçimde tetiklemek
- Dosya erişim durumu değişimlerini kullanıcıya yansıtmak
- Hata durumunda detaylı, kopyalanabilir hata bilgisini status bar'a iletmek
- Aktif dile göre görünür durum metinlerini üretmek

MİMARİ:
- SADECE SistemYoneticisi kullanılır
- UI davranışını korur
- Hata durumlarında sessiz fallback uygular
- Status widget ve toast layer yoksa akışı bozmaz
- Root paketinin alt durum modülüdür
- Kullanıcıya görünen metinler sistem metin servisinden alınabilir

API UYUMLULUK:
- API 35 uyumlu
- Android ve masaüstü ortamlarında güvenli çalışır
- Doğrudan Android bridge çağrısı yapmaz

SURUM: 5
TARIH: 2026-03-23
IMZA: FY.
"""

from __future__ import annotations


class RootStatusMixin:
    def _sistem(self):
        return self._get_sistem_yoneticisi()

    def _m(self, anahtar: str, default: str = "") -> str:
        try:
            services = getattr(self, "services", None)
            if services is not None and hasattr(services, "metin"):
                return str(services.metin(anahtar, default) or default or anahtar)
        except Exception:
            pass
        return str(default or anahtar)

    def _safe_set_status(self, text: str, icon_name: str = "") -> None:
        try:
            if self.status is not None:
                self.status.set_status(
                    str(text or ""),
                    icon_name=str(icon_name or ""),
                )
        except Exception:
            pass

    def set_status(self, text: str, icon_name: str = "") -> None:
        self._safe_set_status(text, icon_name)

    def set_status_info(self, text: str, icon_name: str = "") -> None:
        self._safe_set_status(text, icon_name)

    def set_status_success(self, text: str) -> None:
        try:
            if self.status is not None:
                self.status.set_success(str(text or ""))
        except Exception:
            pass

    def set_status_warning(self, text: str) -> None:
        try:
            if self.status is not None:
                self.status.set_warning(str(text or ""))
        except Exception:
            pass

    def set_status_error(
        self,
        text: str,
        detailed_text: str = "",
        popup_title: str = "Hata Detayı",
    ) -> None:
        try:
            if self.status is not None:
                self.status.set_error(
                    str(text or ""),
                    detailed_text=str(detailed_text or ""),
                    popup_title=str(popup_title or "Hata Detayı"),
                )
        except Exception:
            pass

    def show_toast(
        self,
        text: str,
        icon_name: str = "",
        duration: float = 2.4,
    ) -> None:
        if self.toast_layer is None:
            return

        try:
            self._sistem().bildirim_goster(
                text=str(text or ""),
                icon_name=str(icon_name or ""),
                duration=float(duration or 2.4),
            )
        except Exception:
            pass

    def hide_toast(self) -> None:
        if self.toast_layer is None:
            return

        try:
            self._sistem().bildirimi_aninda_gizle()
        except Exception:
            pass

    def _on_file_access_status_changed(self, durum: bool) -> None:
        try:
            if durum:
                self.set_status_success(
                    self._m("all_files_access_on", "Tüm dosya erişimi açık.")
                )
            else:
                self.set_status_warning(
                    self._m("all_files_access_off", "Tüm dosya erişimi kapalı.")
                )
        except Exception:
            pass
